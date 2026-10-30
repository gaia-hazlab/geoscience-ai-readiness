#!/usr/bin/env python3
"""Auditable literature-study pilot. Standard library only; no LLM calls.

Metadata screening is candidate retrieval, never evidence of actual data use.
Network retrieval is opt-in. No account or API key is created by this program.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

VERSION = "0.3.0"
ENDPOINT = "https://api.openalex.org/works"
FAMILIES = {
    "seismic_elastic": r"\b(seismi\w*|earthquake waveform\w*|acoustic sensing|DAS)\b",
    "geodetic_position_displacement": r"\b(GNSS|GPS|geodetic|geodesy|displacement time series)\b",
    "radar_backscatter_interferometry": r"\b(InSAR|SAR|synthetic aperture radar|radar backscatter)\b",
    "optical_reflectance": r"\b(optical reflectance|multispectral|hyperspectral|Landsat|Sentinel[- ]?2)\b",
    "passive_microwave": r"\b(passive microwave|microwave brightness temperature)\b",
    "thermal_radiance": r"\b(thermal infrared|thermal radiance|land surface temperature)\b",
    "atmospheric_in_situ": r"\b(radiosonde\w*|weather station\w*|in[- ]situ atmospheric)\b",
    "hydrologic_in_situ": r"\b(streamflow|discharge gauge\w*|stream gauge\w*|well water level\w*)\b",
    "oceanographic_in_situ": r"\b(Argo|ocean buoy\w*|oceanographic mooring\w*|CTD)\b",
    "gravity_potential": r"\b(gravimetr\w*|gravity anomal\w*|GRACE)\b",
    "electromagnetic_electrical": r"\b(magnetotelluric\w*|electrical resistivity|electromagnetic sounding)\b",
    "geochemical_biological": r"\b(geochem\w*|isotop\w*|environmental DNA|eDNA|biodiversity)\b",
    "human_system_records": r"\b(crop yield\w*|trade flow\w*|census|infrastructure network\w*)\b",
    "other": r"(?!)",
}
AI_PATTERN = r"\b(machine learning|deep learning|neural network\w*|foundation model\w*|artificial intelligence|random forest\w*|support vector machine\w*|transformer\w*)\b"
FUSION = ["co_used_only", "joint_non_ml_inversion", "late_output_fusion", "joint_ml_inputs", "cross_modal_representation_learning", "cross_modal_transfer_test"]
FRAME_NOTES = {
    "journal": "Source-ID frame: articles in frozen journals, no topic or AI keyword in the denominator.",
    "topic": ("Topic frame: works whose title or abstract matches a phrase. The phrase may name a modality (DAS); "
              "AI/ML terms are refused. Counts measure indexed activity on the topic, not actual use or users."),
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary.replace(path)


def normalized_doi(value):
    if not value:
        return None
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I).lower().rstrip(".")


def paper_ids_digest(ids):
    return hashlib.sha256(json.dumps(sorted(ids), separators=(",", ":")).encode()).hexdigest()


def deduplicate(works):
    """Connect matching DOI OR OpenAlex IDs, including transitive duplicates."""
    groups, key_group, next_group = {}, {}, 0
    for work in works:
        keys = []
        if work.get("id"):
            keys.append("id:" + work["id"].rstrip("/"))
        if normalized_doi(work.get("doi")):
            keys.append("doi:" + normalized_doi(work["doi"]))
        if not keys:
            raise ValueError("A work lacks both a DOI and OpenAlex ID; cannot safely deduplicate.")
        matches = {key_group[key] for key in keys if key in key_group}
        group = min(matches) if matches else next_group
        if not matches:
            next_group += 1
        merged = [work]
        for existing in matches:
            merged.extend(groups.pop(existing))
        groups[group] = merged
        for item in merged:
            for key in ("id:" + item["id"].rstrip("/") if item.get("id") else None,
                        "doi:" + normalized_doi(item["doi"]) if item.get("doi") else None):
                if key:
                    key_group[key] = group
    result = []
    for items in groups.values():
        # Prefer the richest abstract, then stable identifier, without inventing text.
        chosen = max(items, key=lambda x: (len(x.get("abstract_inverted_index") or {}), x.get("id", ""))).copy()
        chosen["retrieval_query_ids"] = sorted({q for item in items for q in item.get("retrieval_query_ids", [])})
        chosen["dedup_openalex_ids"] = sorted({item["id"] for item in items if item.get("id")})
        result.append(chosen)
    return sorted(result, key=lambda row: row.get("id", row.get("doi", "")))


def reconstruct_abstract(index):
    if not index:
        return None
    words = {}
    for word, offsets in index.items():
        for offset in offsets:
            if offset in words and words[offset] != word:
                raise ValueError("Ambiguous abstract index positions.")
            words[offset] = word
    return " ".join(words.get(position, "[MISSING]") for position in range(max(words) + 1))


def evidence_matches(text, pattern, field):
    return [{"field": field, "start": match.start(), "end": match.end(), "matched_text": match.group(0)}
            for match in re.finditer(pattern, text, flags=re.I)]


def screen_work(work):
    title = work.get("display_name") or work.get("title") or ""
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    fields = {"title": title, "abstract": abstract or ""}
    candidates = {family: [e for field, text in fields.items() for e in evidence_matches(text, pattern, field)]
                  for family, pattern in FAMILIES.items()}
    candidates = {family: evidence for family, evidence in candidates.items() if evidence}
    ai = [e for field, text in fields.items() for e in evidence_matches(text, AI_PATTERN, field)]
    method_candidates = {
        "deep_learning": [e for field, text in fields.items() for e in evidence_matches(text, r"\b(deep learning|convolutional neural network\w*|CNNs?|transformer\w*|LSTMs?|recurrent neural network\w*)\b", field)],
        "foundation_model": [e for field, text in fields.items() for e in evidence_matches(text, r"\b(foundation model\w*|large language model\w*|LLMs?)\b", field)]
    }
    return {"paper_id": work.get("id"), "doi": normalized_doi(work.get("doi")),
            "year": work.get("publication_year"), "title": title, "abstract": abstract,
            "abstract_status": "available" if abstract else "missing",
            "screen_only": True, "screen_version": VERSION,
            "screen_interpretation": "Lexical candidate matches; neither actual modality use nor actual AI use.",
            "modality_candidates": candidates, "ai_candidate": bool(ai), "ai_evidence": ai,
            "method_candidates": method_candidates,
            "actual_modality_use": None, "actual_ai_use": None,
            "source_id": ((work.get("primary_location") or {}).get("source") or {}).get("id")}


def frame_kind(config):
    """'journal' (default; source-ID frame) or 'topic' (title/abstract phrase frame, e.g. DAS adoption)."""
    kind = config["frame"].get("kind", "journal")
    if kind not in ("journal", "topic"):
        raise ValueError("frame.kind must be 'journal' or 'topic'.")
    return kind


def topic_slug(phrase):
    return re.sub(r"[^a-z0-9]+", "_", phrase.lower()).strip("_")


def build_topic_queries(config, start, end, page_size):
    """One query per year for works whose title or abstract matches a quoted phrase.

    A topic frame is a query-conditioned corpus, not a journal census: its
    denominator is 'works matching the phrase', and the phrase itself may name a
    measurement modality (DAS). AI terms are still refused in the phrase so the
    AI-as-method share keeps an AI-free denominator.
    """
    frame = config["frame"]
    phrase = frame.get("topic_search")
    if not isinstance(phrase, str) or not phrase.strip():
        raise ValueError("A topic frame needs frame.topic_search, a quoted title/abstract phrase.")
    if re.search(AI_PATTERN, phrase, flags=re.I):
        raise ValueError("The topic phrase must not contain AI/ML terms; the AI share needs an AI-free denominator.")
    types = frame.get("types", ["article"])
    if not types or any(not re.fullmatch(r"[a-z-]+", t) for t in types):
        raise ValueError("frame.types must list OpenAlex work types such as article or review.")
    quoted = phrase if phrase.startswith('"') and phrase.endswith('"') else f'"{phrase}"'
    slug = topic_slug(phrase)
    queries = []
    for year in range(start, end + 1):
        filters = [f"from_publication_date:{year}-01-01", f"to_publication_date:{year}-12-31",
                   "type:" + "|".join(types), f"title_and_abstract.search:{quoted}"]
        if frame.get("language"):
            filters.append("language:" + frame["language"])
        queries.append({"query_id": f"topic_{slug}_{year}", "year": year, "source_id": None,
                        "source_label": f"topic:{phrase}", "parameters": {"filter": ",".join(filters),
                        "per_page": page_size, "sort": "publication_date:asc"}})
    return queries, []


def build_queries(config):
    start, end = config["years"]["start"], config["years"]["end"]
    if start > end or end >= 2026:
        raise ValueError("This frozen pilot requires complete publication years ending no later than 2025.")
    page_size = config.get("per_page", 100)
    if not 1 <= page_size <= 100:
        raise ValueError("per_page must be between 1 and 100 under current OpenAlex documentation.")
    if frame_kind(config) == "topic":
        return build_topic_queries(config, start, end, page_size)
    queries, unresolved = [], []
    for source in config["frame"]["sources"]:
        source_id = source.get("openalex_source_id")
        if not source_id:
            unresolved.append(source["label"])
            continue
        if not re.fullmatch(r"(?:https://openalex.org/)?S\d+", source_id):
            raise ValueError("A source ID must be a verified OpenAlex S-number or its canonical URL.")
        source_id = source_id.rsplit("/", 1)[-1]
        for year in range(start, end + 1):
            filters = [f"from_publication_date:{year}-01-01", f"to_publication_date:{year}-12-31",
                       "type:article", f"primary_location.source.id:{source_id}"]
            if config["frame"].get("language"):
                filters.append("language:" + config["frame"]["language"])
            queries.append({"query_id": f"{source_id}_{year}", "year": year, "source_id": source_id,
                            "source_label": source["label"], "parameters": {"filter": ",".join(filters),
                            "per_page": page_size, "sort": "publication_date:asc"}})
    return queries, unresolved


def query_url(parameters, cursor="*", api_key=None):
    params = dict(parameters, cursor=cursor)
    if api_key:
        params["api_key"] = api_key
    return ENDPOINT + "?" + urlencode(params)


def config_fingerprint(config):
    return hashlib.sha256(json.dumps({"endpoint": ENDPOINT, "config": config}, sort_keys=True).encode()).hexdigest()


def load_checkpoint(path, fingerprint):
    if Path(path).exists():
        checkpoint = read_json(path)
        if checkpoint["config_sha256"] != fingerprint:
            raise ValueError("Configuration changed. Use a new output folder to preserve query provenance.")
        return checkpoint
    return {"schema_version": 1, "config_sha256": fingerprint, "created_at": utc_now(), "queries": {}}


def fetch_json(url, attempts=5, opener=urlopen, sleeper=time.sleep):
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": "GeoscienceLiteratureStudy/0.1 (metadata-only pilot)"})
            with opener(request, timeout=60) as response:
                return json.loads(response.read())
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise RuntimeError(f"OpenAlex returned HTTP {error.code}; request URL/key omitted from error.") from None
            retry_after = error.headers.get("Retry-After", "") if error.headers else ""
            delay = float(retry_after) if retry_after.isdigit() else 2 ** attempt
            sleeper(min(60, max(1, delay)))
        except (URLError, TimeoutError):
            if attempt == attempts - 1:
                raise RuntimeError("Network request failed after retries; request URL/key omitted from error.") from None
            sleeper(min(60, 2 ** attempt))
    raise RuntimeError("Unreachable retry state")


def rebuild_corpus(out):
    works, receipts = [], []
    for page in sorted((out / "raw").glob("*.json")):
        envelope = read_json(page)
        for work in envelope["response"].get("results", []):
            work = work.copy()
            work["retrieval_query_ids"] = [envelope["query_id"]]
            works.append(work)
        receipts.append({"path": str(page.relative_to(out)), "sha256": hashlib.sha256(page.read_bytes()).hexdigest(),
                         "retrieved_at": envelope["retrieved_at"], "public_url": envelope["public_url"]})
    unique = deduplicate(works)
    write_jsonl(out / "works.jsonl", unique)
    return unique, receipts


def harvest(args):
    config = read_json(args.config)
    queries, unresolved = build_queries(config)
    kind = frame_kind(config)
    plan = {"mode": "dry_run" if not args.execute else "execute", "frame_kind": kind, "query_count": len(queries),
            "unresolved_source_labels": unresolved, "years": config["years"],
            "max_pages_this_run": args.max_pages,
            "parameters_contain_no_modality_or_AI_keywords": kind == "journal",
            "parameters_contain_no_AI_keywords": True,
            "frame_note": FRAME_NOTES[kind],
            "sample_public_urls": [query_url(q["parameters"]) for q in queries[:3]],
            "note": "No network request occurs unless --execute is given. Resolve and freeze every source ID first."}
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    if unresolved or not queries:
        raise ValueError("Cannot execute an unresolved/empty source frame; verify and fill all source IDs first.")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cp_path = out / "checkpoint.json"
    checkpoint = load_checkpoint(cp_path, config_fingerprint(config))
    atomic_json(out / "frozen_config.json", config)
    key = os.environ.get(config.get("api_key_env", "OPENALEX_API_KEY"))
    pages_this_run, stop_reason = 0, None
    try:
        for query in queries:
            state = checkpoint["queries"].setdefault(query["query_id"], {"pages": 0, "next_cursor": "*", "complete": False})
            while not state["complete"] and pages_this_run < args.max_pages:
                if state["pages"] > 0 and not key:
                    stop_reason = "Existing user-provided verified OpenAlex key needed to continue cursor pagination. No key was created."
                    break
                cursor = state["next_cursor"]
                response = fetch_json(query_url(query["parameters"], cursor, key))
                if not isinstance(response.get("results"), list) or "meta" not in response:
                    raise ValueError("Unexpected OpenAlex response; checkpoint not advanced.")
                envelope = {"query_id": query["query_id"], "retrieved_at": utc_now(),
                            "public_url": query_url(query["parameters"], cursor),
                            "response": response}
                page_path = out / "raw" / f"{query['query_id']}_page_{state['pages'] + 1:05d}.json"
                atomic_json(page_path, envelope)  # Repeating a page after a crash safely overwrites this page only.
                next_cursor = response["meta"].get("next_cursor")
                state.update(pages=state["pages"] + 1, next_cursor=next_cursor,
                             complete=not response["results"] or not next_cursor,
                             api_count=response["meta"].get("count"))
                checkpoint["updated_at"] = utc_now()
                atomic_json(cp_path, checkpoint)
                pages_this_run += 1
                time.sleep(max(0.1, config.get("minimum_request_interval_seconds", 1.0)))
            if stop_reason or pages_this_run >= args.max_pages:
                break
    finally:
        works, receipts = rebuild_corpus(out)
        complete = all(checkpoint["queries"].get(q["query_id"], {}).get("complete") for q in queries)
        atomic_json(out / "manifest.json", {"created_at": utc_now(), "tool_version": VERSION,
                    "frame_kind": kind, "frame_note": FRAME_NOTES[kind],
                    "topic_search": config["frame"].get("topic_search") if kind == "topic" else None,
                    "frame_complete": complete, "query_count": len(queries), "unique_works": len(works),
                    "works_jsonl_sha256": hashlib.sha256((out / "works.jsonl").read_bytes()).hexdigest(),
                    "paper_ids_sha256": paper_ids_digest([work["id"] for work in works]),
                    "pages_this_run": pages_this_run, "stop_reason": stop_reason or ("page limit" if not complete else None),
                    "config_sha256": config_fingerprint(config), "raw_pages": receipts,
                    "credentials_saved": False, "population_claim_allowed": complete,
                    "population": ("works matching the topic phrase in title or abstract at retrieval time; "
                                   "not a journal census and not all literature on the topic") if kind == "topic"
                                  else "articles in the frozen source frame"})
    print(json.dumps({"pages_this_run": pages_this_run, "unique_works": len(works), "frame_complete": complete,
                      "stop_reason": stop_reason or ("page limit" if not complete else None)}, indent=2))


def screen(args):
    source_digest = hashlib.sha256(Path(args.input).read_bytes()).hexdigest()
    rows = [dict(screen_work(work), source_works_jsonl_sha256=source_digest) for work in read_jsonl(args.input)]
    write_jsonl(args.out, rows)


def validate_sample_frame(rows, manifest):
    """A complete harvest manifest cannot bless a filtered/replaced screen file."""
    ids = [row.get("paper_id") for row in rows]
    if any(not isinstance(paper_id, str) or not paper_id for paper_id in ids):
        raise ValueError("Every screen record needs a paper ID matching the frozen frame.")
    if len(rows) != manifest.get("unique_works") or len(ids) != len(set(ids)):
        raise ValueError("Screen count/unique IDs do not match the complete manifest; do not sample a filtered subset.")
    if paper_ids_digest(ids) != manifest.get("paper_ids_sha256"):
        raise ValueError("Screen paper IDs differ from the frozen manifest.")
    expected_digest = manifest.get("works_jsonl_sha256")
    if not expected_digest or any(row.get("source_works_jsonl_sha256") != expected_digest for row in rows):
        raise ValueError("Screen provenance does not match the manifest's original works.jsonl hash.")


def sample_rows(rows, n_per_stratum, seed, by_source=True):
    if n_per_stratum < 2:
        raise ValueError("Use at least two per stratum to allow design-based variance estimation.")
    strata = {}
    for row in rows:
        middle = (row.get("source_id") or "unknown_source") if by_source else "topic"
        stratum = f"{row['year']}|{middle}|AI_screen_{int(row['ai_candidate'])}"
        strata.setdefault(stratum, []).append(row)
    selected, design = [], []
    for stratum, population in sorted(strata.items()):
        population = sorted(population, key=lambda row: row["paper_id"])
        n, N = min(n_per_stratum, len(population)), len(population)
        stable_seed = hashlib.sha256(f"{seed}|{stratum}".encode()).hexdigest()
        for row in random.Random(stable_seed).sample(population, n):
            item = row.copy()
            item.update(sampling_stratum=stratum, inclusion_probability=n / N)
            selected.append(item)
        design.append({"sampling_stratum": stratum, "year": population[0]["year"], "N": N, "n": n})
    return sorted(selected, key=lambda row: row["paper_id"]), design


def sample(args):
    manifest = read_json(args.manifest)
    if not manifest.get("frame_complete"):
        raise ValueError("Frame is incomplete. Finish harvesting before creating a probability sample.")
    rows = read_jsonl(args.input)
    validate_sample_frame(rows, manifest)
    if any(not row.get("screen_only") for row in rows):
        raise ValueError("Sampling expects the metadata screen output, including AI-screen negatives.")
    topic = manifest.get("frame_kind", "journal") == "topic"
    selected, strata = sample_rows(rows, args.n_per_stratum, args.seed, by_source=not topic)
    write_jsonl(args.out, selected)
    atomic_json(args.design, {"design": "stratified_simple_random_without_replacement", "seed": args.seed,
                "frame_kind": manifest.get("frame_kind", "journal"),
                "prototype_layout": ("year_x_AI_screen within one topic frame" if topic else
                                     "year_x_source_x_AI_screen; differs from the protocol's subject_x_year_band_x_AI_screen pilot"),
                "frame_complete": True, "frame_manifest_sha256": hashlib.sha256(Path(args.manifest).read_bytes()).hexdigest(),
                "scope": (manifest.get("population") or "Topic-phrase corpus at retrieval time; not a journal census.") if topic
                         else "Frozen source frame, complete publication years; not all geoscientific literature.",
                "sample_assignments": [{"paper_id": r["paper_id"], "year": r["year"],
                    "sampling_stratum": r["sampling_stratum"], "inclusion_probability": r["inclusion_probability"]}
                    for r in selected],
                "sample_ids_sha256": paper_ids_digest([r["paper_id"] for r in selected]),
                "strata": strata})


def annotation_template(row):
    return {"paper_id": row["paper_id"], "doi": row.get("doi"), "title": row["title"], "year": row["year"],
            "source_id": row.get("source_id"), "sampling_stratum": row.get("sampling_stratum"),
            "inclusion_probability": row.get("inclusion_probability"), "review_status": "not_reviewed",
            "reviewer_id": None, "review_date": None, "evidence_level": None,
            "full_text_status": "not_attempted", "eligibility": "uncertain", "eligibility_reason": None,
            "evidence": [], "data_sources": [], "actual_modality_families": None,
            "ai_actual_use": "uncertain", "ai_method_families": [], "ai_role": None,
            "deep_learning_actual_use": "uncertain", "foundation_model_actual_use": "uncertain",
            "foundation_model_pretraining": "uncertain", "foundation_model_roles": None,
            "training_regimes": None, "model_scale": [], "small_model_comparisons": [],
            "adoption_explanations": [],
            "fusion_labels": None, "dataset_dois_used": [], "readiness_barriers": [], "need_claims": [],
            "readiness_assessment": {"access": None, "machine_readability": None,
                "cross_experiment_interoperability": None, "training_scalability": None,
                "independent_evaluation": None, "community_reuse_evidence": None},
            "notes": "Do not copy screen labels into actual-use labels without reading and citing the methods/results."}


def template(args):
    write_jsonl(args.out, [annotation_template(row) for row in read_jsonl(args.input)])


def validate_review(row):
    if row.get("review_status") != "reviewed":
        return False
    if not row.get("reviewer_id") or row.get("evidence_level") != "full_text":
        raise ValueError("A reviewed row requires reviewer_id and full_text evidence_level.")
    if row.get("full_text_status") not in ("available_open", "available_licensed"):
        raise ValueError("A full-text reviewed row requires available_open or available_licensed full_text_status; unavailable/partial/parse-failed text is not a completed full-text review.")
    if row.get("eligibility") not in ("yes", "no", "uncertain"):
        raise ValueError("Invalid eligibility label.")
    if row.get("eligibility") == "yes":
        families = row.get("actual_modality_families")
        if families is not None and (not isinstance(families, list) or not set(families) <= set(FAMILIES)):
            raise ValueError("Unknown actual modality family.")
        if row.get("ai_actual_use") not in ("yes", "no", "uncertain"):
            raise ValueError("Invalid actual AI-use label.")
        fusion = row.get("fusion_labels")
        if fusion is not None and (not isinstance(fusion, list) or not set(fusion) <= set(FUSION)):
            raise ValueError("Unknown fusion label.")
        # Additional actual-use labels remain unknown for legacy annotations.
        for key in ["deep_learning_actual_use", "foundation_model_actual_use", "foundation_model_pretraining"]:
            if row.get(key, "uncertain") not in ("yes", "no", "uncertain"):
                raise ValueError("Invalid " + key + " label.")
            if row.get(key) == "yes" and row.get("ai_actual_use") != "yes":
                raise ValueError(key + " requires verified actual AI use.")
        if row.get("foundation_model_actual_use") == "yes" and row.get("deep_learning_actual_use") != "yes":
            raise ValueError("This codebook's neural foundation models require verified deep-learning use.")
        if row.get("foundation_model_pretraining") == "yes" and row.get("foundation_model_actual_use") != "yes":
            raise ValueError("Foundation-model pretraining requires verified foundation-model use.")
        # Each positive actual-use/fusion label must have its own locatable evidence record.
        required = set(families or []) | set(fusion or [])
        if row.get("ai_actual_use") == "yes":
            required.add("ai_actual_use")
        for key in ["deep_learning_actual_use", "foundation_model_actual_use", "foundation_model_pretraining"]:
            if row.get(key) == "yes":
                required.add(key)
        supported = set()
        for record in row.get("evidence", []):
            if not record.get("url") or not record.get("section_or_page") or not record.get("excerpt"):
                raise ValueError("Evidence requires URL, section/page, and a short excerpt.")
            if len(record["excerpt"].split()) > 25:
                raise ValueError("Evidence excerpts must not exceed 25 words each; respect total source quotation limits too.")
            supported.update(record.get("supports", []))
        if not required <= supported:
            raise ValueError("Positive actual-use/fusion labels lack evidence: " + ", ".join(sorted(required - supported)))
    return True


def metric(row, name):
    if row.get("eligibility") == "no":
        return (0, 0)
    if row.get("eligibility") != "yes":
        return None
    if name == "multimodal_actual_use":
        families = row.get("actual_modality_families")
        return None if families is None else (int(len(set(families)) >= 2), 1)
    if name == "ai_actual_use":
        ai = row.get("ai_actual_use")
        return None if ai not in ("yes", "no") else (int(ai == "yes"), 1)
    extended = {
        "deep_learning_actual_use": ("deep_learning_actual_use", None),
        "foundation_model_actual_use": ("foundation_model_actual_use", None),
        "foundation_model_pretraining": ("foundation_model_pretraining", None),
        "deep_learning_given_ai": ("deep_learning_actual_use", "ai_actual_use"),
        "foundation_model_given_ai": ("foundation_model_actual_use", "ai_actual_use"),
        "foundation_model_given_deep_learning": ("foundation_model_actual_use", "deep_learning_actual_use"),
    }
    if name in extended:
        target, condition = extended[name]
        if condition:
            value = row.get(condition, "uncertain")
            if value == "no":
                return (0, 0)
            if value != "yes":
                return None
        value = row.get(target, "uncertain")
        return None if value not in ("yes", "no") else (int(value == "yes"), 1)
    if name == "multimodal_given_ai":
        ai, families = row.get("ai_actual_use"), row.get("actual_modality_families")
        if ai == "no":
            return (0, 0)
        if ai != "yes" or families is None:
            return None
        return (int(len(set(families)) >= 2), 1)
    if name == "ai_given_multimodal":
        families, ai = row.get("actual_modality_families"), row.get("ai_actual_use")
        if families is None:
            return None
        if len(set(families)) < 2:
            return (0, 0)
        return None if ai not in ("yes", "no") else (int(ai == "yes"), 1)
    if name == "joint_ml_inputs_or_representation":
        families, labels = row.get("actual_modality_families"), row.get("fusion_labels")
        if families is None or labels is None or row.get("ai_actual_use") == "uncertain":
            return None
        positive = len(set(families)) >= 2 and row.get("ai_actual_use") == "yes" and bool(set(labels) & {"joint_ml_inputs", "cross_modal_representation_learning"})
        return (int(positive), 1)
    raise ValueError("Unknown metric")


def estimate_stratified(rows, strata, name):
    by_stratum = {}
    for row in rows:
        by_stratum.setdefault(row.get("sampling_stratum"), []).append(row)
    eligible_total, positive_total, terms = 0.0, 0.0, []
    for stratum in strata:
        sample = by_stratum.get(stratum["sampling_stratum"], [])
        N, n = stratum["N"], stratum["n"]
        if len(sample) != n or any(not math.isclose(row.get("inclusion_probability") or 0, n / N, rel_tol=1e-9) for row in sample):
            return {"available": False, "reason": "Missing sampled rows or inconsistent inclusion probabilities."}
        values = [metric(row, name) for row in sample]
        if any(value is None for value in values):
            return {"available": False, "reason": "Uncertain eligibility/actual-use labels; do not recode missing as negative."}
        mean_y = sum(value[0] for value in values) / n
        mean_x = sum(value[1] for value in values) / n
        positive_total += N * mean_y
        eligible_total += N * mean_x
        terms.append((N, n, values))
    if not eligible_total:
        return {"available": False, "reason": "No eligible denominator."}
    proportion = positive_total / eligible_total
    variance = 0.0
    for N, n, values in terms:
        if n == N:
            continue
        if n < 2:
            return {"available": False, "reason": "A non-census stratum needs at least two reviewed papers for variance."}
        residuals = [y - proportion * x for y, x in values]
        variance += N * N * (1 - n / N) * statistics.variance(residuals) / n
    se = math.sqrt(variance) / eligible_total
    boundary_non_census = proportion in (0, 1) and any(n < N for N, n, _ in terms)
    return {"available": True, "proportion": proportion, "eligible_population_total_estimate": eligible_total,
            "positive_population_total_estimate": positive_total, "standard_error": se,
            "ci95_normal_approximation": None if boundary_non_census else [max(0, proportion - 1.96 * se), min(1, proportion + 1.96 * se)],
            "ci_limitation": "A boundary estimate in a non-census sample does not justify a zero-width interval; use exact finite-population or sensitivity bounds." if boundary_non_census else None,
            "ci_method": "Stratified SRS ratio estimator, Taylor residual variance with finite-population correction; normal approximation. Sparse/boundary estimates need sensitivity analysis."}


def validate_annotation_design(rows, design):
    """Bind reviewed IDs to the saved draw, not just plausible stratum counts.

    Missing annotation rows remain missing; substituted IDs/assignments fail.
    Old designs without a saved draw support descriptive output only.
    """
    assignments = design.get("sample_assignments")
    if assignments is None:
        return False
    ids = [r.get("paper_id") for r in assignments]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError("Saved sample assignments contain missing or duplicate paper IDs.")
    if design.get("sample_ids_sha256") != paper_ids_digest(ids):
        raise ValueError("Saved sample-ID digest mismatch.")
    expected = {r["paper_id"]: r for r in assignments}
    strata = {r["sampling_stratum"]: r for r in design["strata"]}
    if len(strata) != len(design["strata"]):
        raise ValueError("Duplicate sampling strata in design.")
    counts = {k: 0 for k in strata}
    for r in assignments:
        group = r.get("sampling_stratum")
        if group not in strata:
            raise ValueError("Saved assignment has a stratum absent from design.")
        h = strata[group]
        if r.get("year") != h["year"] or not math.isclose(r.get("inclusion_probability") or 0, h["n"] / h["N"], rel_tol=1e-9):
            raise ValueError("Saved assignment year/probability contradicts design.")
        counts[group] += 1
    if any(counts[k] != h["n"] for k, h in strata.items()):
        raise ValueError("Saved sample assignments do not match stratum sample sizes.")
    for r in rows:
        if r["paper_id"] not in expected:
            raise ValueError("Annotation paper ID was not in the saved probability sample.")
        original = expected[r["paper_id"]]
        if r.get("year") != original["year"] or r.get("sampling_stratum") != original["sampling_stratum"]:
            raise ValueError("Annotation year/stratum differs from the saved draw.")
        if not math.isclose(r.get("inclusion_probability") or 0, original["inclusion_probability"], rel_tol=1e-9):
            raise ValueError("Annotation inclusion probability differs from the saved draw.")
    return True


def report(args):
    raw = read_jsonl(args.input)
    ids = [row["paper_id"] for row in raw]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate annotation paper IDs; adjudicate before reporting.")
    reviewed = [row for row in raw if validate_review(row)]
    design = read_json(args.design) if args.design else None
    if design and (design.get("design") != "stratified_simple_random_without_replacement" or not design.get("frame_complete")):
        raise ValueError("Population estimates require a complete, documented stratified SRS frame.")
    if design:
        allowed = {s["sampling_stratum"] for s in design["strata"]}
        if any(row.get("sampling_stratum") not in allowed for row in raw):
            raise ValueError("An annotation belongs to a stratum absent from the sampling design.")
    sample_binding_verified = validate_annotation_design(raw, design) if design else False
    metrics = ["multimodal_actual_use", "ai_actual_use", "deep_learning_actual_use",
               "foundation_model_actual_use", "foundation_model_pretraining", "multimodal_given_ai",
               "ai_given_multimodal", "joint_ml_inputs_or_representation", "deep_learning_given_ai",
               "foundation_model_given_ai", "foundation_model_given_deep_learning"]
    years = sorted({row["year"] for row in raw} | ({s["year"] for s in design["strata"]} if design else set()))
    output = {"created_at": utc_now(), "annotation_rows": len(raw), "human_reviewed_full_text_rows": len(reviewed),
              "not_reviewed_rows": len(raw) - len(reviewed), "scope": (design or {}).get("scope", "Reviewed accessible subset only; no population inference."),
              "full_text_status_counts": {status: sum((row.get("full_text_status") or "unspecified") == status for row in raw)
                  for status in sorted({row.get("full_text_status") or "unspecified" for row in raw})},
              "screen_labels_used_as_actual_use": False, "sample_binding_verified": sample_binding_verified,
              "years": []}
    for year in years:
        rows = [row for row in reviewed if row["year"] == year]
        annotation_count = sum(row["year"] == year for row in raw)
        expected_sample = sum(s["n"] for s in design["strata"] if s["year"] == year) if design else None
        annual = {"year": year, "annotation_rows": annotation_count, "expected_sampled_rows": expected_sample,
                  "missing_annotation_rows": max(0, expected_sample - annotation_count) if design else None,
                  "reviewed_rows": len(rows), "eligibility_uncertain": sum(row["eligibility"] == "uncertain" for row in rows), "metrics": {}}
        for name in metrics:
            known = [metric(row, name) for row in rows]
            known = [value for value in known if value is not None]
            denominator, numerator = sum(v[1] for v in known), sum(v[0] for v in known)
            result = {"reviewed_eligible_known_denominator": denominator, "reviewed_positive_count": numerator,
                      "reviewed_subset_proportion": numerator / denominator if denominator else None,
                      "unknown_or_inaccessible_labels": sum(metric(row, name) is None for row in rows),
                      "population_estimate": {"available": False, "reason": "No probability-sampling design supplied."}}
            if design and not sample_binding_verified:
                result["population_estimate"] = {"available": False,
                    "reason": "Legacy design lacks saved paper-ID assignments; descriptive output only."}
            if design and sample_binding_verified:
                strata = [s for s in design["strata"] if s["year"] == year]
                result["population_estimate"] = estimate_stratified(rows, strata, name) if strata else {"available": False, "reason": "No annual sampling strata."}
            annual["metrics"][name] = result
        output["years"].append(annual)
    atomic_json(args.out, output)
    print(json.dumps({"reviewed": len(reviewed), "not_reviewed": len(raw) - len(reviewed), "report": args.out}, indent=2))


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    p = sub.add_parser("harvest", help="Plan by default; --execute enables OpenAlex metadata requests.")
    p.add_argument("--config", default="config.example.json")
    p.add_argument("--out", default="runs/pilot")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="Explicit alias for the default planning behavior.")
    p.add_argument("--max-pages", type=int, default=1, help="Total requests/pages this invocation; repeat to resume.")
    p.set_defaults(function=harvest)
    p = sub.add_parser("screen", help="Conservative candidate screen; does not count actual use.")
    p.add_argument("--input", required=True); p.add_argument("--out", required=True); p.set_defaults(function=screen)
    p = sub.add_parser("sample", help="Stratified random sample including AI-screen negatives.")
    p.add_argument("--input", required=True); p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True); p.add_argument("--design", required=True)
    p.add_argument("--n-per-stratum", type=int, default=10); p.add_argument("--seed", default="2026-10-21-v1")
    p.set_defaults(function=sample)
    p = sub.add_parser("template", help="Create blank actual-use annotations for human review.")
    p.add_argument("--input", required=True); p.add_argument("--out", required=True); p.set_defaults(function=template)
    p = sub.add_parser("report", help="Report reviewed evidence only; optional design-based estimates.")
    p.add_argument("--input", required=True); p.add_argument("--out", required=True); p.add_argument("--design")
    p.set_defaults(function=report)
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    if getattr(args, "execute", False) and getattr(args, "dry_run", False):
        raise ValueError("Choose either --execute or --dry-run.")
    if getattr(args, "max_pages", 1) < 1:
        raise ValueError("max-pages must be positive.")
    args.function(args)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(2)
