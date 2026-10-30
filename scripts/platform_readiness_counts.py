#!/usr/bin/env python3
"""Count AI/ML-ready datasets and ML papers across geoscience disciplines and platforms.

Usage: python scripts/platform_readiness_counts.py --out runs/platform_counts_<date> [--skip openalex]

Read-only public API queries, no keys (OpenAlex keyless budget is small; the script stops a
source on HTTP 4xx/429 and records the failure instead of retrying). Every raw response is
saved under OUT/raw/ with its SHA256 in OUT/receipts.json; derived counts go to OUT/counts.json.

What each source measures, and what it does not:
- DataCite (/dois, resource-type dataset): registered dataset DOIs whose metadata match a query.
  Subject tags are sparse, so the "Earth (FOS)" subset undercounts Earth datasets; keyword
  queries match titles, descriptions and subjects, not file contents.
- Hugging Face Hub (/api/datasets?search=): dataset repositories whose id contains the term;
  downloads are the Hub's rolling 30-day count at retrieval time. Ids, not cards, are matched.
- OpenAlex (/works, group_by): works whose title or abstract match a phrase; keyword
  co-occurrence, not actual use (see the repository's evidence rules).
- OpenAlex simulation block: articles naming a numerical method (finite element, finite
  difference, spectral element, finite volume, numerical simulation) and articles naming an ML
  surrogate (physics-informed neural network, neural operator, DeepONet, or surrogate
  model/emulator together with an ML term), by field, subfield and year.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

UA = "GeoscienceAIReadiness/0.3 (research metadata counts; mailto:mdenolle@uw.edu)"
AI_READY = '("AI-ready" OR "AI ready" OR "ML-ready" OR "ML ready" OR "machine learning ready" OR "machine-learning-ready")'
ML = '("machine learning" OR "deep learning" OR "neural network")'
SIM = '("numerical simulation" OR "finite element" OR "finite difference" OR "spectral element" OR "finite volume")'
SURR_ML = ('("physics-informed neural network" OR "neural operator" OR DeepONet OR '
           '(("surrogate model" OR emulator) AND ("machine learning" OR "deep learning" OR "neural network")))')
EARTH_FOS = 'subjects.subject:"FOS: Earth and related environmental sciences"'
DISCIPLINES = {   # DataCite free-text clauses per discipline (title/description/subject match)
    "seismology": '(seismic OR seismology OR earthquake OR "distributed acoustic sensing")',
    "geodesy_sar": '(InSAR OR GNSS OR geodetic OR "synthetic aperture radar")',
    "optical_remote_sensing": '("remote sensing" OR Landsat OR "Sentinel-2" OR multispectral OR hyperspectral)',
    "weather_climate": '(weather OR climate OR reanalysis OR ERA5 OR CMIP6)',
    "hydrology": '(hydrology OR streamflow OR groundwater OR "soil moisture")',
    "ocean": '(oceanography OR "sea surface" OR Argo OR "ocean model")',
    # comparison domains outside the geosciences
    "biomedicine": '(clinical OR medical OR patient OR genomics)',
    "materials_chemistry": '(materials OR molecule OR "crystal structure")',
}
HF_TERMS = {
    "seismology": ["seismic", "seismo", "earthquake", "quake"],
    "geodesy_sar": ["insar", "gnss", "sar-", "geodes"],
    "optical_remote_sensing": ["satellite", "sentinel", "landsat", "remote-sensing", "remote_sensing", "remotesensing"],
    "weather_climate": ["weather", "climate", "era5", "cmip"],
    "hydrology": ["hydro", "streamflow", "flood"],
    "ocean": ["ocean", "marine"],
    "biomedicine": ["medical", "clinical", "radiology"],
    "materials_chemistry": ["molecul", "chemistry", "materials"],
}
OPENALEX_FIELDS = {"earth_planetary": "fields/19", "environmental": "fields/23"}
YEARS = list(range(2016, 2026))


class Collector:
    def __init__(self, out: Path):
        self.out = out
        (out / "raw").mkdir(parents=True, exist_ok=True)
        self.receipts = []

    def get(self, name: str, url: str, sleep: float = 0.4):
        time.sleep(sleep)
        try:
            with urlopen(Request(url, headers={"User-Agent": UA}), timeout=60) as response:
                body = response.read()
                link = response.headers.get("Link")
        except HTTPError as error:
            self.receipts.append({"name": name, "url": url, "status": error.code, "retrieved_utc": now()})
            raise
        except URLError as error:
            self.receipts.append({"name": name, "url": url, "status": f"network: {error.reason}", "retrieved_utc": now()})
            raise
        path = self.out / "raw" / (re.sub(r"[^A-Za-z0-9_.-]+", "_", name)[:120] + ".json")
        path.write_bytes(body)
        self.receipts.append({"name": name, "url": url, "status": 200, "file": str(path.relative_to(self.out)),
                              "sha256": hashlib.sha256(body).hexdigest(), "retrieved_utc": now()})
        return json.loads(body), link


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def datacite_total(c: Collector, name: str, query: str | None):
    params = {"resource-type-id": "dataset", "page[size]": 0}
    if query:
        params["query"] = query
    data, _ = c.get(f"datacite_{name}", "https://api.datacite.org/dois?" + urlencode(params))
    return data["meta"]["total"]


def datacite_years(c: Collector, name: str, query: str):
    """Per-year counts via one total query per publication year (facets are not returned at page size 0)."""
    out = {}
    for year in YEARS:
        out[year] = datacite_total(c, f"{name}_{year}", f"({query}) AND publicationYear:{year}")
    return out


def collect_datacite(c: Collector):
    res = {"all_datasets": datacite_total(c, "all", None),
           "earth_fos_datasets": datacite_total(c, "earth_fos", EARTH_FOS),
           "ai_ready_all": datacite_total(c, "ai_ready_all", AI_READY),
           "ai_ready_earth_fos": datacite_total(c, "ai_ready_earth_fos", f"{AI_READY} AND {EARTH_FOS}"),
           "ml_all": datacite_total(c, "ml_all", ML),
           "ml_earth_fos": datacite_total(c, "ml_earth_fos", f"{ML} AND {EARTH_FOS}"),
           "disciplines": {}}
    for key, clause in DISCIPLINES.items():
        res["disciplines"][key] = {"datasets": datacite_total(c, f"disc_{key}", clause),
                                   "mention_ml": datacite_total(c, f"disc_{key}_ml", f"{clause} AND {ML}"),
                                   "mention_ai_ready": datacite_total(c, f"disc_{key}_aiready", f"{clause} AND {AI_READY}")}
    res["ai_ready_all_by_year"] = datacite_years(c, "ai_ready_all", AI_READY)
    res["ai_ready_earth_fos_by_year"] = datacite_years(c, "ai_ready_earth", f"{AI_READY} AND {EARTH_FOS}")
    return res


def hf_search(c: Collector, term: str, max_pages: int = 40):
    ids, pages, truncated = {}, 0, False
    url = "https://huggingface.co/api/datasets?" + urlencode({"search": term, "limit": 1000})
    while url:
        data, link = c.get(f"hf_{term}_p{pages + 1}", url, sleep=0.6)
        for item in data:
            ids[item["id"]] = item.get("downloads") or 0
        pages += 1
        match = re.search(r'<([^>]+)>;\s*rel="next"', link or "")
        url = match.group(1) if match else None
        if url and pages >= max_pages:
            truncated, url = True, None
    return ids, truncated


def collect_hf(c: Collector):
    res = {}
    for key, terms in HF_TERMS.items():
        union, truncated = {}, False
        per_term = {}
        for term in terms:
            ids, cut = hf_search(c, term)
            per_term[term] = len(ids)
            union.update(ids)
            truncated |= cut
        top = sorted(union.items(), key=lambda kv: -kv[1])[:10]
        res[key] = {"datasets": len(union), "downloads_30d": sum(union.values()), "per_term": per_term,
                    "truncated": truncated, "top_by_downloads": top}
    return res


def openalex(c: Collector, name: str, filt: str, group_by: str):
    params = {"filter": filt, "group_by": group_by, "per_page": 200}
    data, _ = c.get(f"openalex_{name}", "https://api.openalex.org/works?" + urlencode(params), sleep=1.0)
    return {g["key"].rsplit("/", 1)[-1]: {"name": g.get("key_display_name"), "count": g["count"]} for g in data["group_by"]}


def collect_openalex(c: Collector):
    base = f"from_publication_date:{YEARS[0]}-01-01,to_publication_date:{YEARS[-1]}-12-31,type:article"
    fields = "|".join(OPENALEX_FIELDS.values())
    res = {}
    res["ai_ready_works_all_by_year"] = openalex(c, "aiready_all", f"{base},title_and_abstract.search:{AI_READY}", "publication_year")
    res["ai_ready_works_earth_env_by_year"] = openalex(c, "aiready_earth", f"{base},primary_topic.field.id:{fields},title_and_abstract.search:{AI_READY}", "publication_year")
    res["works_all_by_year"] = openalex(c, "all_by_year", base, "publication_year")
    res["works_earth_env_by_year"] = openalex(c, "earth_by_year", f"{base},primary_topic.field.id:{fields}", "publication_year")
    res["ml_works_all_by_year"] = openalex(c, "ml_all", f"{base},title_and_abstract.search:{ML}", "publication_year")
    res["ml_works_earth_env_by_year"] = openalex(c, "ml_earth", f"{base},primary_topic.field.id:{fields},title_and_abstract.search:{ML}", "publication_year")
    recent = "from_publication_date:2023-01-01,to_publication_date:2025-12-31,type:article"
    res["subfield_works_2023_2025"] = openalex(c, "subfield_all", f"{recent},primary_topic.field.id:{fields}", "primary_topic.subfield.id")
    res["subfield_ml_works_2023_2025"] = openalex(c, "subfield_ml", f"{recent},primary_topic.field.id:{fields},title_and_abstract.search:{ML}", "primary_topic.subfield.id")
    return res


def collect_simulation(c: Collector):
    """Simulation-method and ML-surrogate papers by field, subfield and year (OpenAlex keyword co-occurrence)."""
    recent = "from_publication_date:2023-01-01,to_publication_date:2025-12-31,type:article"
    base = f"from_publication_date:{YEARS[0]}-01-01,to_publication_date:{YEARS[-1]}-12-31,type:article"
    fields = "|".join(OPENALEX_FIELDS.values())
    res = {
        "field_works_2023_2025": openalex(c, "field_all", recent, "primary_topic.field.id"),
        "field_sim_2023_2025": openalex(c, "field_sim", f"{recent},title_and_abstract.search:{SIM}", "primary_topic.field.id"),
        "field_surr_ml_2023_2025": openalex(c, "field_surr", f"{recent},title_and_abstract.search:{SURR_ML}", "primary_topic.field.id"),
        "subfield_sim_2023_2025": openalex(c, "subfield_sim", f"{recent},primary_topic.field.id:{fields},title_and_abstract.search:{SIM}", "primary_topic.subfield.id"),
        "subfield_surr_ml_2023_2025": openalex(c, "subfield_surr", f"{recent},primary_topic.field.id:{fields},title_and_abstract.search:{SURR_ML}", "primary_topic.subfield.id"),
        "surr_ml_all_by_year": openalex(c, "surr_all_year", f"{base},title_and_abstract.search:{SURR_ML}", "publication_year"),
        "surr_ml_earth_env_by_year": openalex(c, "surr_earth_year", f"{base},primary_topic.field.id:{fields},title_and_abstract.search:{SURR_ML}", "publication_year"),
        "sim_all_by_year": openalex(c, "sim_all_year", f"{base},title_and_abstract.search:{SIM}", "publication_year"),
        "sim_earth_env_by_year": openalex(c, "sim_earth_year", f"{base},primary_topic.field.id:{fields},title_and_abstract.search:{SIM}", "publication_year"),
    }
    return res


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--skip", action="append", default=[], choices=["datacite", "hf", "openalex", "simulation"])
    args = parser.parse_args()
    out = Path(args.out)
    if (out / "counts.json").exists():
        raise SystemExit(f"{out}/counts.json exists; use a new dated folder.")
    c = Collector(out)
    counts = {"retrieved_utc": now(), "queries": {"ai_ready": AI_READY, "ml": ML, "earth_fos": EARTH_FOS,
              "disciplines_datacite": DISCIPLINES, "terms_hf": HF_TERMS, "openalex_fields": OPENALEX_FIELDS,
              "simulation": SIM, "surrogate_ml": SURR_ML}}
    for name, fn in (("datacite", collect_datacite), ("hf", collect_hf), ("openalex", collect_openalex),
                     ("simulation", collect_simulation)):
        if name in args.skip:
            continue
        try:
            counts[name] = fn(c)
            print(f"{name}: done", flush=True)
        except (HTTPError, URLError, KeyError, ValueError) as error:
            counts[name] = {"error": f"{type(error).__name__}: {error}"}
            print(f"{name}: stopped ({error})", flush=True)
    (out / "counts.json").write_text(json.dumps(counts, indent=2, default=str) + "\n")
    (out / "receipts.json").write_text(json.dumps(c.receipts, indent=1) + "\n")
    print(f"{len(c.receipts)} requests; counts in {out / 'counts.json'}")


if __name__ == "__main__":
    main()
