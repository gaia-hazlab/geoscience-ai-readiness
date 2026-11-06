#!/usr/bin/env python3
"""Build the HTML technical report "Measuring the AI readiness of the geosciences: a solid-earth perspective".

Usage: pixi run -e report report      (or: python scripts/build_report.py [--out docs/report/ai_readiness_solid_earth.html])

Offline. Rebuilds every figure from tracked, hash-checked inputs, computes every number in the text from
those inputs, and writes one self-contained HTML file (figures embedded as base64 PNG). figure() refuses to
place a plot without a method statement, so each plot follows text saying how it was made.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
import importlib.util
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/archive_readiness_2026-10-30"
SCREEN = ROOT / "data/semantic_screen/das_topic_2026-10-29"
FIG = ROOT / "build/archive_readiness"
DASFIG = ROOT / "build/das_semantic"
CXDOCS = ROOT / "docs/complexity_2026-10-30"
CXFIG = ROOT / "build/complexity"
CHECKS = ROOT / "docs/das_screen_checks_2026-11-06/checks.json"
REPORT_DATE = "6 November 2026"
CORE_JOURNALS = ("Seismological Research Letters", "Geophysical Journal International",
                 "Journal of Geophysical Research Solid Earth", "Geophysical Research Letters")
METHOD_FIELDS = (("question", "Question"), ("inputs", "Inputs"), ("selection", "Selection"), ("calculation", "Calculation"),
                 ("code", "Code and output"), ("checked", "Checked"), ("limits", "Does not show"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def jload(path):
    return json.loads(Path(path).read_text())


def human(b):
    if b is None:
        return "not published"
    for unit, scale in (("PB", 1e15), ("TB", 1e12), ("GB", 1e9), ("MB", 1e6)):
        if b >= scale:
            return f"{b / scale:.3g} {unit}"
    return f"{b:.3g} B"


def pct(x, digits=1):
    return f"{x:.{digits}f}%"


def table(header, rows, cls=""):
    head = "".join(f"<th>{html.escape(str(h))}</th>" for h in header)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def short_hash(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()[:12]


def method_block(number, method):
    """The text that precedes a plot. Every field is required; inputs are listed with their hashes."""
    missing = [key for key, _ in METHOD_FIELDS if not method.get(key)]
    if missing:
        raise ValueError(f"Figure {number} lacks method fields: {missing}")
    rows = []
    for key, label in METHOD_FIELDS:
        if key == "inputs":
            value = "; ".join(f"<code>{html.escape(p)}</code> (sha256 {short_hash(p)})" for p in method[key])
        else:
            value = html.escape(method[key])
        rows.append(f"<dt>{label}</dt><dd>{value}</dd>")
    return f'<div class="method"><b>How Figure {number} was made.</b><dl>' + "".join(rows) + "</dl></div>"


def figure(path, number, caption, method):
    data = base64.b64encode(Path(path).read_bytes()).decode()
    return (method_block(number, method) + f'<figure><img alt="Figure {number}" src="data:image/png;base64,{data}">'
            f"<figcaption><b>Figure {number}.</b> {html.escape(caption)}</figcaption></figure>")


def latest_requery():
    path = sorted(DOCS.glob("requery_*_summary.json"))[-1]
    return json.loads(path.read_text()), path.name[len("requery_"):-len("_summary.json")]


def compute():
    """Every number the text quotes, from tracked inputs."""
    counts, sim = jload(DOCS / "platform_counts.json"), jload(DOCS / "simulation_counts.json")["simulation"]
    o, d = counts["openalex"], counts["datacite"]
    share = lambda k, y: 100 * o[f"ml_works_{k}_by_year"][y]["count"] / o[f"works_{k}_by_year"][y]["count"]
    arf = load("arf", ROOT / "scripts/archive_readiness_figures.py")
    abstract_counts, abstract_path = arf.latest_ml_counts()
    oa = abstract_counts["openalex"]
    share_abs = lambda k, y: 100 * oa[f"ml_works_{k}_by_year"][y]["count"] / oa[f"works_{k}_by_year"][y]["count"]
    n = {"ml_abs_path": str(abstract_path.relative_to(ROOT)), "ml_abs_date": abstract_counts["retrieved_utc"][:10],
         }
    n["ml_compare"] = [(y, share("all", y), share("earth_env", y), share_abs("all", y), share_abs("earth_env", y),
                        100 * oa["works_all_by_year"][y]["count"] / o["works_all_by_year"][y]["count"],
                        100 * oa["works_earth_env_by_year"][y]["count"] / o["works_earth_env_by_year"][y]["count"])
                       for y in ("2016", "2020", "2025")]
    n["ml_all_2025"], n["ml_earth_2025"] = share_abs("all", "2025"), share_abs("earth_env", "2025")
    sub, subml = oa["subfield_works_2023_2025"], oa["subfield_ml_works_2023_2025"]
    n["ml_subfield"] = {v["name"]: 100 * subml.get(k, {}).get("count", 0) / v["count"] for k, v in sub.items()}
    n["datacite_all"], n["datacite_ai_ready"] = d["all_datasets"], d["ai_ready_all"]
    n["ai_ready_by_year"] = d["ai_ready_all_by_year"]
    n["datacite_disc"] = d["disciplines"]
    n["hf_geo"] = sum(counts["hf"][k]["datasets"] for k in ("seismology", "optical_remote_sensing", "weather_climate", "hydrology", "ocean")) + arf.hf_geodesy_count(counts["hf"])
    n["hf_bio"] = counts["hf"]["biomedicine"]["datasets"]
    n["hf_terms"] = {k: len(v) for k, v in counts["queries"]["terms_hf"].items()}
    fs, fm = sim["field_sim_2023_2025"], sim["field_surr_ml_2023_2025"]
    n["surr_field"] = {v["name"]: (100 * fm.get(k, {}).get("count", 0) / v["count"], fm.get(k, {}).get("count", 0), v["count"])
                       for k, v in fs.items() if v["count"] >= 2000}
    ss, sm = sim["subfield_sim_2023_2025"], sim["subfield_surr_ml_2023_2025"]
    n["surr_sub"] = {v["name"]: (100 * sm.get(k, {}).get("count", 0) / v["count"], sm.get(k, {}).get("count", 0), v["count"])
                     for k, v in ss.items() if v["count"] >= 500}
    yr = lambda k, y: 100 * sim[f"surr_ml_{k}_by_year"].get(y, {"count": 0})["count"] / sim[f"sim_{k}_by_year"][y]["count"]
    n["surr_earth_2016"], n["surr_earth_2025"] = yr("earth_env", "2016"), yr("earth_env", "2025")
    n["surr_all_2025"] = yr("all", "2025")
    sc = jload(DOCS / "simulation_corpora.json")["rows"]
    ml = [r for r in sc if r["side"] == "ML-ready simulation corpus"]
    n["sim_ml_solid"] = sum(r["bytes"] for r in ml if r["domain"] == "solid_earth")
    n["sim_ml_other"] = sum(r["bytes"] for r in ml if r["domain"] != "solid_earth")
    n["cybershake_kept"] = next(r["bytes"] for r in sc if r["name"] == "CyberShake Study 22.12, archived")
    n["cybershake_handled"] = next(r["bytes"] for r in sc if r["name"] == "CyberShake Study 22.12, managed during run")
    n["pairs"] = arf.pairs_table()
    n["copies"] = arf.copies_table()
    n["checks"] = jload(CHECKS)
    summ = jload(SCREEN / "summary.json")["years"]
    n["das_years"] = summ
    kw = defaultdict(dict)
    with open(ROOT / "legacy/community_demand/annual_title_abstract_article_review_counts.csv") as f:
        for r in csv.DictReader(f):
            kw[r["query_id"]][int(r["year"])] = int(r["count"])
    rows = [json.loads(l) for l in open(SCREEN / "screen_semantic.jsonl")]
    lab = [r for r in rows if r["status"] == "labeled" and r["ai_role"] != "unclear"]
    n["das_compare"] = []
    for y in range(2020, 2026):
        g = [r for r in lab if r["year"] == y]
        n["das_compare"].append((y, 100 * kw["das_ml_article_review"][y] / kw["das_article_review"][y],
                                 100 * sum(r["ai_role"] == "ai_as_method" for r in g) / len(g)))
    index = {w["paper_id"]: w for w in (json.loads(l) for l in open(SCREEN / "works_index.jsonl"))}
    das = [r for r in lab if r["das_used"] == "yes"]
    venues = defaultdict(lambda: [0, 0])
    for r in das:
        v = index[r["paper_id"]]["venue"] or "none"
        venues[v][1] += 1
        venues[v][0] += r["ai_role"] == "ai_as_method"
    n["das_venues"] = sorted(((v, a, t) for v, (a, t) in venues.items() if t >= 28), key=lambda x: -x[1] / x[2])
    core = [100 * venues[j][0] / venues[j][1] for j in CORE_JOURNALS]
    n["das_core"] = (min(core), max(core))
    n["das_fm"] = sum("foundation_model" in r["ai_method_families"] for r in das if r["ai_role"] == "ai_as_method")
    n["das_dl"] = sum("deep_learning" in r["ai_method_families"] for r in das if r["ai_role"] == "ai_as_method")
    n["das_aim"] = sum(r["ai_role"] == "ai_as_method" for r in das)
    n["coll"] = jload(SCREEN / "collect_manifest.json")
    n["prep"] = jload(SCREEN / "prepare_manifest.json")
    n["requery"], n["requery_date"] = latest_requery()
    sim_queries = jload(DOCS / "simulation_counts.json")["queries"]
    n["queries"] = {**counts["queries"], "simulation": sim_queries["simulation"], "surrogate_ml": sim_queries["surrogate_ml"]}
    rq = load("rq", ROOT / "scripts/requery_check.py")
    n["hashes"] = rq.check_hashes()
    n["cx"] = compute_complexity()
    return n


def compute_complexity():
    """Numbers for the complexity section, from the validated tables in docs/complexity_2026-10-30."""
    ct = load("ct", ROOT / "scripts/complexity_tables.py")
    tables = ct.load(CXDOCS)
    rows = {r["id"]: r for t in tables.values() for r in t["rows"]}
    valued = lambda r: any(r[k] is not None for k in ("value", "value_min", "value_max"))
    geo = [r for r in tables["power_laws.json"]["rows"] if r["domain"] == "geoscience" and valued(r)]
    tested = [r for r in geo if r["tested_vs_alternatives"].startswith("tested")]
    nontest = {"not tested in this source": [r for r in geo if r["tested_vs_alternatives"] == "not tested in this source"],
               "not stated": [r for r in geo if r["tested_vs_alternatives"] == "not stated"]}
    def test_class(row):
        text = (row.get("alternative_test") or "").lower()
        if "vuong" in text or "ks" in text or "cv_l" in text:
            return "maximum likelihood with goodness-of-fit or likelihood-ratio test"
        if "chi-square" in text:
            return "chi-square goodness of fit"
        if "rank-ordering" in text:
            return "rank-ordering statistics"
        return "other or described in the abstract only"
    classes = {}
    for row in tested:
        classes.setdefault(test_class(row), []).append(row)
    pdes = [r for r in tables["coupled_pdes.json"]["rows"] if r["value"] is not None]
    geo_pde = [r["value"] for r in pdes if "(comparison)" not in r["item"]]
    comp_pde = [r["value"] for r in pdes if "(comparison)" in r["item"]]
    ai = [r for r in tables["ai_evidence.json"]["rows"] if valued(r)]
    by_axis = {ax: (sum(r["axis"] == ax and r["evidence_type"] == "success" for r in ai),
                    sum(r["axis"] == ax and r["evidence_type"] == "limitation" for r in ai))
               for ax in ("dimensionality", "closures", "tails", "unobserved")}
    profile = json.loads((CXDOCS / "readiness_profile.json").read_text())
    cf = load("cf", ROOT / "scripts/complexity_figures.py")
    arf = load("arf2", ROOT / "scripts/archive_readiness_figures.py")
    return {"rows": rows, "summaries": ct.summary(tables).splitlines(), "pl_geo": len(geo), "pl_tested": len(tested),
            "pl_favored": sum(r["tested_vs_alternatives"] == "tested, power law favored" for r in tested),
            "pl_nontest": nontest, "pl_tested_rows": tested, "pl_classes": classes,
            "pde_geo": (min(geo_pde), max(geo_pde)), "pde_comp": (min(comp_pde), max(comp_pde)),
            "ai": ai, "ai_by_axis": by_axis, "profile": profile, "cells": cf.profile_cells(profile, tables, arf.pairs_table())}


def complexity_section(cx):
    """Section 6: four complexity axes, the AI evidence along each, and the readiness profile."""
    r = cx["rows"]
    rng = lambda row: f"{row['value_min']:g} to {row['value_max']:g}"
    p = ["<h2>6. Why the geosciences are hard, and why that suits AI</h2>"]
    p.append("<p>Complexity is measured along four axes, each with its own units, and the axes are never added into one score. "
             "Every value below comes from the sourced tables in <code>docs/complexity_2026-10-30/</code>, where each row carries a "
             "source, an as-of date, a quote and a flag saying whether the number was read in the source text.</p>")
    plural = lambda k, word: f"{k} {word}" + ("" if k == 1 else ("es" if word.endswith("s") else "s"))
    sl = lambda ax: plural(cx["ai_by_axis"][ax][0], "success") + ", " + plural(cx["ai_by_axis"][ax][1], "limitation")
    p.append(table(["Axis", "What the tables show", "Why it suits AI", "Work that remains", "AI evidence rows"], [
        ["Dimensionality",
         f"Native data are large: {r['dim-08']['value']:,} channels on one DAS array, {r['dim-14']['value']:,} seismic stations in one "
         f"study. Published effective dimensions of climate fields are {r['dim-26']['value']} to {r['dim-31']['value_max']}; image "
         f"benchmarks give {r['dim-40']['value_min']:g} to {r['dim-38']['value_max']:g} (MLE).",
         "Learning cost scales with intrinsic, not nominal, dimension; large data over modest structure is where learned "
         "representations outperform hand-built features.",
         "No published effective dimension for seismogram archives, DAS or ERA5; one DAS study finds near-uniform singular values.",
         sl("dimensionality")],
        ["Coupled physics",
         f"Minimal coupled models need {cx['pde_geo'][0]} to {cx['pde_geo'][1]} scalar balance equations; Navier-Stokes, Maxwell and "
         f"magnetohydrodynamics need {cx['pde_comp'][0]} to {cx['pde_comp'][1]}.",
         "The laws are few and known; the uncertainty sits in empirical closures (friction, permeability, rheology), which hybrid "
         "models can learn while keeping the balance laws.",
         f"Learned closures fail out of distribution (+{r['ai-12']['value']:g} K warming in two climate studies); no sourced learned "
         "friction or rheology closure was found.", sl("closures")],
        ["Heavy tails",
         f"{cx['pl_geo']} geoscience power-law rows report an exponent; {cx['pl_tested']} were tested against alternatives and "
         f"{cx['pl_favored']} favored a pure power law.",
         "Learned models can pool events across regions and catalogs, beyond what a single parametric fit uses.",
         f"AI forecasts degrade on record-breaking extremes; magnitude estimates saturate near M{r['ai-20']['value_min']:.1f} to "
         f"{r['ai-20']['value_max']:.1f}; tail-aware evaluation is missing.", sl("tails")],
        ["Unobserved drivers",
         f"EM-DAT lacks total damage for {r['uo-23']['value']}% of natural-hazard events (1990 to 2020); {r['uo-19']['value']}% of the "
         f"urban population lives in cities with more than 80% complete OpenStreetMap buildings; {rng(r['uo-10'])}% of California's "
         "moment rate is off modeled faults.",
         "Proxies can be learned: building footprints from imagery, dense catalogs that light up unmapped structures.",
         f"Building recall is {r['ai-26']['value']}% in Africa; regional pickers transfer poorly (AUC at most {r['ai-28']['value']}). "
         "Without outcome labels, supervised evaluation is not possible.", sl("unobserved")],
    ]))
    nt, ns = cx["pl_nontest"]["not tested in this source"], cx["pl_nontest"]["not stated"]
    p.append("<h3>What the tail count rests on</h3>")
    p.append(f"<p>Of {cx['pl_geo']} geoscience rows with an exponent, {cx['pl_tested']} were tested against alternatives, {len(nt)} were read in full "
             f"text with no test, and {len(ns)} were read only from an abstract or a search snippet, so a test may exist that was not seen. "
             "The 13 tested rows do not share one test, so a pooled rate of favorable verdicts is a count of published statements, "
             "not an estimate. A uniform refit of open catalogs with one test has not been done.</p>")
    p.append(table(["Test used", "Rows", "Row ids and verdicts"],
                   [[k, len(v), "; ".join(f"{r['id']}: {r['tested_vs_alternatives'].replace('tested, ', '')}" for r in v)] for k, v in sorted(cx["pl_classes"].items(), key=lambda kv: -len(kv[1]))]))
    p.append(table(["Status", "Rows", "Observables"],
                   [["Read in full text, no test", len(nt), "; ".join(r["item"] for r in nt)],
                    ["Abstract or snippet only, no test stated", len(ns), "; ".join(r["item"] for r in ns)]]))
    p.append(figure(CXFIG / "fig1_power_law_exponents.png", 10, "Density exponents of heavy-tailed geoscience observables and "
                    "non-geoscience comparisons, colored by whether the source tested the power law against alternatives. Only "
                    "exponents stated in the density convention are drawn.", {
                        "question": "Do geoscience density exponents differ from those of other heavy-tailed data, and was the power-law form tested?",
                        "inputs": ["docs/complexity_2026-10-30/power_laws.json"],
                        "selection": "Rows whose source states a density exponent, listed by id in PDF_ROWS. Other conventions (b-values, survivor exponents, Hack's law, fractal dimensions) are left out because they are not comparable.",
                        "calculation": "None on the exponents: values and ranges are drawn as stated. Exponents that a source writes with a minus sign are drawn by magnitude. Color comes from the verdict recorded for that source.",
                        "code": "scripts/complexity_figures.py, fig_power_laws; build/complexity/fig1_power_law_exponents and power_law_pdf_exponents.csv.",
                        "checked": "scripts/complexity_tables.py validated the table on each build. Values were read from the sources on 2026-10-30, mostly by subagents, and were not re-read on 2026-11-06.",
                        "limits": "A purposive sample of the literature, not a census. No exponent was refit, and the verdicts come from different tests.",
                    }))
    p.append(figure(CXFIG / "fig2_coupled_pde_counts.png", 11, "Scalar balance equations and per-point ODE state variables in "
                    "minimal coupled models, counted by one rule from one cited source per system.", {
                        "question": "How many coupled equations does a minimal model of each system need?",
                        "inputs": ["docs/complexity_2026-10-30/coupled_pdes.json"],
                        "selection": "One minimal model per system from one cited source; three physics systems for comparison.",
                        "calculation": "Each balance law counted once, vectors expanded to scalars in the stated dimensionality, per-point ODE states counted separately, closures listed but not counted.",
                        "code": "scripts/complexity_figures.py; build/complexity/fig2_coupled_pde_counts.",
                        "checked": "scripts/complexity_tables.py checks that vector and scalar counts agree. Sources were read on 2026-10-30 and not re-read on 2026-11-06.",
                        "limits": "Model size, not difficulty. Another source or dimensionality changes the count.",
                    }))
    p.append("<h3>AI evidence along the four axes</h3>")
    p.append("<p>Successes and limitations were both sought. Counts reflect what was collected, not how often AI succeeds.</p>")
    order = {"dimensionality": 0, "closures": 1, "tails": 2, "unobserved": 3}
    p.append(table(["Axis", "Type", "Task", "Result as stated", "Baseline", "Source"],
                   [[a["axis"], a["evidence_type"], a["task"], a["value_text"], a["baseline"] or "", a["source"]]
                    for a in sorted(cx["ai"], key=lambda a: (order[a["axis"]], a["evidence_type"] != "success", a["id"]))]))
    p.append("<h3>Readiness profile by discipline</h3>")
    p.append(figure(CXFIG / "fig3_readiness_profile.png", 12, "AI-readiness profile: each column is a separate measure with its own "
                    "evidence; cells are colored by status and never summed.", {
                        "question": "For each discipline and measure, what evidence do these tables hold?",
                        "inputs": ["docs/complexity_2026-10-30/readiness_profile.json", "docs/archive_readiness_2026-10-30/archives.json", "docs/archive_readiness_2026-10-30/benchmarks.json"],
                        "selection": "Eight disciplines and five measures, chosen by the authors of this report.",
                        "calculation": "Status rule: measured means a cited value read in the source text for this discipline; partial means proxy, secondary, small-sample or qualitative evidence; not found means searched and absent; not assessed means not searched. Share labels come from the archive pairs in section 3.",
                        "code": "scripts/complexity_figures.py, profile_cells and fig_profile; build/complexity/fig3_readiness_profile and readiness_profile.csv.",
                        "checked": "scripts/complexity_tables.py rejects unknown row ids, statuses without evidence and numbers typed into notes.",
                        "limits": "Status describes evidence, not readiness: measured does not mean ready. Cells are not summed, and not-assessed cells say nothing about the discipline.",
                    }))
    cols = [c["label"] for c in cx["profile"]["columns"]]
    grid = {}
    for c in cx["cells"]:
        grid.setdefault(c["discipline"], {})[c["column"]] = c["status"] + (f": {c['label']}" if c["label"] else "")
    p.append(table(["Discipline"] + cols, [[d] + [grid[d][c] for c in cols] for d in grid]))
    status_counts = Counter(c["status"] for c in cx["cells"])
    p.append(f"<p>Across {len(cx['cells'])} cells: {status_counts['measured']} measured, {status_counts['partial']} partial, {status_counts['not found']} not found and "
             f"{status_counts['not assessed']} not assessed. Seismology has no effective dimension for its archive, and weather and climate has "
             "only qualitative evidence on unobserved drivers. DAS and radar have sourced AI successes but no sourced limitation; "
             "geodesy was not assessed for AI results. Cells marked not assessed were not searched and say nothing about the discipline.</p>")
    return p


CSS = """
:root{--bg:#fcfcfb;--fg:#0b0b0b;--muted:#52514e;--rule:#e4e3df;--accent:#2a78d6;--card:#f4f3f0}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a19;--fg:#f0efec;--muted:#c3c2b7;--rule:#3a3a37;--accent:#3987e5;--card:#242422}}
html{background:var(--bg)}body{margin:0 auto;max-width:900px;padding:32px 16px 64px;color:var(--fg);background:var(--bg);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
h1{font-size:1.7rem;line-height:1.25;margin:0 0 .3rem}h2{font-size:1.25rem;margin:2.2rem 0 .6rem;border-top:1px solid var(--rule);padding-top:1.2rem}
h3{font-size:1.05rem;margin:1.6rem 0 .4rem}.meta{color:var(--muted);font-size:.92rem}.goal{background:var(--card);border-left:4px solid var(--accent);padding:.8rem 1rem;margin:1.2rem 0}
.tw{overflow-x:auto;margin:.8rem 0}table{border-collapse:collapse;font-size:.88rem;width:100%}th,td{border-bottom:1px solid var(--rule);padding:.35rem .5rem;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}.method{background:var(--card);border-left:4px solid var(--rule);padding:.6rem .9rem;margin:1.4rem 0 .4rem;font-size:.88rem}
.method dl{margin:.4rem 0 0;display:grid;grid-template-columns:8.5rem 1fr;gap:.25rem .7rem}.method dt{color:var(--muted);font-weight:600}.method dd{margin:0}
figure{margin:.6rem 0 1.4rem}figure img{max-width:100%;height:auto;background:#fff;border-radius:4px}
figcaption{color:var(--muted);font-size:.86rem;margin-top:.3rem}code{font-size:.86em;background:var(--card);padding:.05rem .3rem;border-radius:3px}
a{color:var(--accent)}pre{background:var(--card);padding:.7rem .9rem;overflow-x:auto;font-size:.82rem;border-radius:4px}li{margin:.2rem 0}
"""


def build(n):
    p = []
    rq, rq_date = n["requery"], n["requery_date"]
    comp = rq["comparisons"]
    within = lambda name: f"{comp[name]['within_1_percent']} of {comp[name]['metrics_compared']} numbers within 1%" if name in comp else "not re-run"
    live_check = f"Live re-query of {rq_date}: "
    rate_2025 = next((r for r in rq.get("ml_rates", []) if r["year"] == "2025"), None)
    rate_check = ((f"The 2025 rates in that run were {rate_2025['live_all_percent']:.2f}% and {rate_2025['live_earth_env_percent']:.2f}%, against {rate_2025['frozen_all_percent']:.2f}% and {rate_2025['frozen_earth_env_percent']:.2f}% here" if rate_2025 else "No rate comparison in that run"))
    checks = n["checks"]
    pr = {r["row"]: r for r in n["pairs"]}
    bounds = {b["year"]: b for b in checks["bounds"]}
    cross = {c["year"]: c for c in checks["keyword_crosstab"]}
    retest = checks["retest"]
    drift = checks["frame_drift"]
    validated = jload(SCREEN / "summary.json")["validated"]
    screen_inputs = ["data/semantic_screen/das_topic_2026-10-29/screen_semantic.jsonl"]
    das_status = ("Labels have not been checked against human coding: the 130-abstract sample is drawn and uncoded." if not validated else "Validated against human coding.")

    p.append("<h1>Measuring the AI readiness of the geosciences: a solid-earth perspective</h1>")
    p.append(f'<p class="meta">Technical report, rebuilt {REPORT_DATE}; it replaces the version of 30 October 2026 (changes in section 10). Analysis package '
             '<code>geoscience-ai-readiness</code>; source, data and notebooks at '
             '<a href="https://github.com/gaia-hazlab/geoscience-ai-readiness">github.com/gaia-hazlab/geoscience-ai-readiness</a>. '
             "Contact: Marine Denolle, University of Washington.</p>")
    p.append('<div class="goal"><b>How this report was produced.</b> Claude (Anthropic) wrote the analysis code, the tables and this text under the direction of Marine Denolle. '
             "Claude subagents read most of the published sources, and each table row records whether its number was seen in the source text. Claude Opus 5.5 produced the DAS labels. "
             "No person has checked those labels. Each figure below follows a statement of its question, inputs with file hashes, selection, calculation, code, checks and limits.</div>")
    p.append('<div class="goal"><b>Goal.</b> Measure the AI readiness of the geosciences from a solid-earth perspective. Readiness here depends on the use, because the use sets the intended population. '
             "Solid earth means seismology, distributed acoustic sensing (DAS), geodesy, radar deformation and the simulations that model them.</div>")
    p.append(table(["Use", "Intended population", "Quantity that fits", "Where reported"], [
        ["Data mining and pretraining on the whole record", "The archive", "How much of the archive a compute job can read as a whole", "Section 3, whole-record table"],
        ["Training on a curated benchmark", "The archive when the benchmark is meant to represent it; otherwise the task's events, sites and conditions", "Share of the archive packaged; counts of independent events and sites for a specific task", "Section 3, Figure 5 (bytes only)"],
        ["Community attention", "Published articles and registered datasets", "Keyword and metadata counts, which do not measure use", "Sections 1, 2, 4 and 5"],
    ]))
    sub = n["ml_subfield"]
    p.append("<h2>Summary</h2><ul>")
    p.append(f"<li><b>ML is mentioned at least as often here as elsewhere.</b> Among OpenAlex articles with an abstract, {pct(n['ml_earth_2025'])} in Earth and environmental sciences "
             f"mention ML, against {pct(n['ml_all_2025'])} in all fields (2025). Geophysics is at {pct(sub['Geophysics'])} for 2023 to 2025. These are keyword counts, not use.</li>")
    se = n["surr_sub"]
    p.append(f"<li><b>Solid-earth simulation papers mention ML surrogates less often.</b> Per 100 articles naming a numerical method, "
             f"geophysics has {se['Geophysics'][0]:.1f} ML-surrogate articles and earth-surface processes {se['Earth-Surface Processes'][0]:.1f}, "
             f"against {se['Atmospheric Science'][0]:.1f} in atmospheric science and {n['surr_field']['Physics and Astronomy'][0]:.0f} in physics (2023 to 2025).</li>")
    seis, asf, sent = pr["Seismology: EarthScope, NCEDC, SCEDC"], pr["SAR: all ASF holdings"], pr["Sentinel missions: all, Copernicus"]
    p.append(f"<li><b>Curated benchmarks are a small share of the archives they come from.</b> At most {seis['share_percent']:.2f}% of the US seismic archives, at most {asf['share_percent']:.2f}% of ASF SAR holdings and "
             f"{sent['share_percent']:.2f}% of the Sentinel archive. For data mining, where the archive is the intended population, this share matters only if the benchmark is the route to the data. "
             "No ML-ready benchmark was found for GNSS or the Ocean Observatories Initiative.</li>")
    p.append("<li><b>Whole-record access is a separate measure and changes the picture for mining.</b> ERA5 exists as whole-record cloud stores, and Ni et al. (2025) ran inference over 1.3 PB of US seismic archives in native format. "
             "ERA5 is therefore not a 20% case beside seismology at 0.2%: the two numbers measure different things. Marine Denolle is a co-author of Ni et al.</li>")
    p.append(f"<li><b>Little solid-earth simulation output is packaged.</b> The solid-earth ML-ready simulation corpora found total {human(n['sim_ml_solid'])}; one CyberShake study kept {human(n['cybershake_kept'])} and handled "
             f"{human(n['cybershake_handled'])} during its run. ML-ready corpora found in other physics and atmospheric science total {human(n['sim_ml_other'])}. The lists are purposive.</li>")
    p.append(f"<li><b>DAS.</b> On one set of abstracts, the keyword share went from {cross[2020]['keyword_percent']:.1f}% in 2020 to {cross[2025]['keyword_percent']:.1f}% in 2025. The unvalidated screen's share among DAS-using abstracts went from "
             f"{bounds[2020]['point_percent']:.1f}% to {bounds[2025]['point_percent']:.1f}%, with bounds of {bounds[2020]['lower_percent']:.0f} to {bounds[2020]['upper_percent']:.0f}% and {bounds[2025]['lower_percent']:.0f} to {bounds[2025]['upper_percent']:.0f}% "
             f"when unknown works are counted both ways. Two runs of the model agree (kappa {retest['ai_role']['cohen_kappa']:.2f}), which shows stability, not correctness.</li>")
    p.append(f"<li><b>The AI-ready label is rare everywhere.</b> {n['datacite_ai_ready']} of {n['datacite_all']:,} DataCite datasets use it. Hugging Face name counts cannot settle whether geoscience lags, "
             f"because the term lists differ in length ({n['hf_terms']['biomedicine']} biomedical terms against {sum(v for k, v in n['hf_terms'].items() if k not in ('biomedicine', 'materials_chemistry')) - 2} geoscience terms in use, after dropping 'sar-' and 'geodes').</li>")
    cx, r = n["cx"], n["cx"]["rows"]
    nt, ns = cx["pl_nontest"]["not tested in this source"], cx["pl_nontest"]["not stated"]
    p.append(f"<li><b>Complexity favors AI and also limits it.</b> Native data are large ({r['dim-08']['value']:,} DAS channels on one "
             f"array) while measured effective dimensions of climate fields are tens ({r['dim-26']['value']} to {r['dim-31']['value_max']}), "
             f"close to image benchmarks. Minimal coupled models need {cx['pde_geo'][0]} to {cx['pde_geo'][1]} balance equations, so the "
             f"unknowns sit in closures. Of {cx['pl_geo']} power-law rows, {cx['pl_favored']} of {cx['pl_tested']} tested fits favor a pure power law, {len(nt)} rows have no test and {len(ns)} are unknown. "
             f"Outcome labels are thin: EM-DAT lacks total damage for {r['uo-23']['value']}% of natural-hazard events.</li></ul>")

    # Section 1
    ml_method = lambda question, selection, code: {
        "question": question,
        "inputs": [n["ml_abs_path"]],
        "selection": selection,
        "calculation": "Articles whose title or abstract match \"machine learning\", \"deep learning\" or \"neural network\", divided by all articles in the same group. Numerator and denominator are both limited to has_abstract:true and come from one run.",
        "code": code,
        "checked": live_check + within("ml_share_abstract") + ". " + rate_check + ".",
        "limits": "Attention, not use. OpenAlex field labels are content based and move AI-heavy papers into Computer Science. Recent years are still being indexed.",
    }
    p.append("<h2>1. Do geoscientists use ML?</h2>")
    p.append("<p>The first version of this report divided title-or-abstract matches by all articles, including articles with no abstract to search. Earth and environmental articles have abstracts slightly less often, "
             "so that denominator did not match its numerator. The rates now use articles with an abstract. The difference between fields narrows but keeps its sign.</p>")
    p.append(table(["Year", "All fields, old", "Earth + env, old", "All fields, with abstract", "Earth + env, with abstract", "All fields with abstract", "Earth + env with abstract"],
                   [[y, pct(a, 2), pct(b, 2), pct(c, 2), pct(d, 2), pct(e), pct(f)] for y, a, b, c, d, e, f in n["ml_compare"]]))
    p.append(figure(FIG / "fig2_ml_share_by_year.png", 1, "Share of OpenAlex articles with an abstract that mention ML, Earth and environmental "
                    "sciences against all fields, 2016 to 2025. Keyword co-occurrence, not actual use.",
                    ml_method("Do Earth and environmental articles mention ML less often than articles in general?",
                              "Type article, 2016 to 2025, has_abstract:true. Earth and environmental sciences are OpenAlex fields 19 and 23 by primary topic.",
                              "scripts/ml_share_abstract_counts.py collects; scripts/archive_readiness_figures.py, fig_ml_share_years, draws build/archive_readiness/fig2_ml_share_by_year.")))
    p.append(figure(FIG / "fig3_ml_share_by_subfield.png", 2, "ML mention rate by Earth and environmental subfield, articles with an abstract, 2023 to 2025.",
                    ml_method("Which subfields mention ML most and least?",
                              "Type article, 2023 to 2025, has_abstract:true, fields 19 and 23, subfields with at least 5,000 such articles. The dashed line is all fields over the same years.",
                              "scripts/archive_readiness_figures.py, fig_ml_share_subfield; build/archive_readiness/fig3_ml_share_by_subfield.")))
    p.append("<p>Mentions alone do not show whether the data and simulations of solid-earth science can feed these methods. The following sections take that up.</p>")

    # Section 2
    p.append("<h2>2. A solid-earth case: DAS</h2>")
    p.append(f"<p>The frame holds every OpenAlex article or review whose title or abstract matches \"distributed acoustic sensing\", 2020 to 2025. Claude Opus 5.5 labeled each abstract under a fixed codebook. "
             f"{das_status} A label is screening evidence, not actual use. Nothing here should replace the keyword series in a figure until the human coding is done.</p>")
    p.append(f"<p>The frame moves. A harvest on {drift['second_harvest']} returned {drift['second_works']:,} works against {drift['first_works']:,} on {drift['first_harvest']}, with {drift['removed']} removed and {drift['added']} added. "
             f"OpenAlex also lists one 2022 paper under two records, which the harvester merges, so 2022 shows 193 works against an OpenAlex count of 194. All tables here use the frozen {drift['first_harvest']} frame.</p>")
    p.append("<p>The table gives the screen's share among abstracts known to use DAS with a known AI role, then bounds that count every unknown work, meaning a missing abstract or an unclear label, first as not AI and then as AI. Wilson intervals cover sampling of labels only, not classifier error.</p>")
    rows = []
    for y in n["das_years"]:
        a = y["ai_as_method_among_das_confirmed"]
        b = bounds[y["year"]]
        rows.append([y["year"], y["works"], y["abstract_missing"], b["das_used_no"], b["unknown"], f"{a['count']} / {a['denominator']}",
                     pct(100 * a["share"]), f"{100 * a['wilson95'][0]:.1f} to {100 * a['wilson95'][1]:.1f}%", f"{b['lower_percent']:.1f} to {b['upper_percent']:.1f}%"])
    p.append(table(["Year", "Works", "No abstract", "Labeled not DAS", "Unknown", "AI as method", "Share", "Wilson 95%", "Bounds"], rows))
    p.append(f"<p>Three checks need no coder, and none validates the labels. A second batch with the same model and prompt ({checks['second_batch']['batch_id']}, ${checks['second_batch']['usd_total']:.2f}) agreed on "
             f"{retest['ai_role']['percent_agree']:.1f}% of AI roles (kappa {retest['ai_role']['cohen_kappa']:.2f}) and {retest['das_used']['percent_agree']:.1f}% of DAS-use labels (kappa {retest['das_used']['cohen_kappa']:.2f}) across {retest['papers_compared']:,} abstracts. "
             "A model can repeat the same error, so this shows stability only. The keyword comparison below uses the same abstracts for both series.</p>")
    p.append(table(["Year", "Abstracts", "Keyword", "Screen", "Both", "Keyword only", "Screen only", "Neither", "Earlier keyword series, all works, two phrases"],
                   [[c["year"], c["population"], pct(c["keyword_percent"]), pct(c["screen_percent"]), c["both"], c["keyword_only"], c["screen_only"], c["neither"], pct(old)]
                    for c, (_, old, _) in zip(checks["keyword_crosstab"], n["das_compare"])]))
    p.append("<p>The earlier comparison set a two-phrase keyword share of all works against the screen's share of labeled abstracts, so it overstated the gap between them. On one denominator with three phrases the gap is smaller.</p>")
    p.append(figure(DASFIG / "explore_1_keyword_vs_semantic.png", 3, "Keyword share against the semantic screen on the same abstracts. Unvalidated.", {
        "question": "How far does a semantic label differ from a keyword search on the same abstracts?",
        "inputs": screen_inputs + ["docs/das_screen_checks_2026-11-06/checks.json"],
        "selection": "Abstracts with a label and a non-unclear AI role, including the few the model says do not analyze DAS.",
        "calculation": "Keyword: regular expression for the three ML phrases in title plus abstract, rebuilt from the OpenAlex inverted index. Screen: share labeled ai_as_method. One denominator per year. Band: Wilson 95% on the screen share.",
        "code": "scripts/das_screen_checks.py writes the counts; scripts/explore_das_semantic.py draws build/das_semantic/explore_1_keyword_vs_semantic.",
        "checked": f"Test-retest kappa {retest['ai_role']['cohen_kappa']:.2f} between two batches. {das_status}",
        "limits": "Not actual use, and not classifier accuracy. Abstracts can omit methods used in the paper.",
    }))
    p.append(table(["Venue (at least 28 DAS-using papers)", "AI as method", "DAS-using papers", "Share"],
                   [[v, a, t, pct(100 * a / t, 0)] for v, a, t in n["das_venues"]]))
    p.append(figure(DASFIG / "explore_4_co_measured_families.png", 4, "Measurement families used alongside DAS. The leading partner is fiber "
                    "temperature sensing on the same cable; geodesy and radar are rare. Unvalidated.", {
                        "question": "What do DAS papers measure alongside DAS?",
                        "inputs": screen_inputs,
                        "selection": "Abstracts labeled das_used yes. Families seen once are left out.",
                        "calculation": "Count of papers per measurement family other than seismic_elastic. The model's 'other' family is split by a word rule on its free-text note.",
                        "code": "scripts/explore_das_semantic.py; build/das_semantic/explore_4_co_measured_families.",
                        "checked": das_status,
                        "limits": "Not a multimodality rate. Whether fiber temperature counts as a separate family is undecided in the protocol, and co-use in a paper is not joint model input.",
                    }))
    p.append(f"<p>In SRL, GJI, JGR Solid Earth and GRL the AI-as-method share of DAS-using papers is {n['das_core'][0]:.0f} to {n['das_core'][1]:.0f}%, below the frame's 2025 share. "
             "Whether DAS adopts AI more slowly than the rest of those journals needs a non-DAS baseline from the same journals, which has not been run.</p>")

    # Section 3
    p.append("<h2>3. How much of each archive is ML-ready?</h2>")
    p.append("<p>For data mining and pretraining the total archive tends to be the intended population, so a share of the archive is the right kind of number. Two different things had been mixed under one share in the first version: curated benchmarks, and whole-record copies such as ARCO-ERA5. They are now separate. "
             "Each row label below names the denominator, and every benchmark in a row was drawn from it. Rows without a matching volume show no share.</p>")
    p.append(figure(FIG / "fig1_archive_vs_ml_ready.png", 5, "Source archive volume against the curated ML benchmarks drawn from it, log scale.", {
        "question": "How large are curated ML benchmarks relative to the archive they came from?",
        "inputs": ["docs/archive_readiness_2026-10-30/archives.json", "docs/archive_readiness_2026-10-30/benchmarks.json"],
        "selection": "Pairs listed in PAIRS. Benchmarks without a stated size are named but not summed. Whole-record copies are excluded and appear in the next table.",
        "calculation": "Sum of stated benchmark bytes divided by stated archive bytes. Where the archive volume is stated as a minimum, the share is marked at most.",
        "code": "scripts/archive_readiness_figures.py, pairs_table and fig_archive_vs_packaged; build/archive_readiness/fig1_archive_vs_ml_ready and archive_pairs.csv.",
        "checked": "Volumes cannot be re-queried by script. Rows added on 2026-11-06 were read through page summaries and carry checked_in_text false, so they need reading in the source before citation.",
        "limits": "Bytes are not samples, because formats differ. Benchmarks can overlap (CEED and SCEDC), so totals are not distinct data. Archive dates run from 2020 to 2026. Absence of a benchmark means none was found in one search on 2026-10-30.",
    }))
    p.append(table(["Row and denominator", "Source archive", "Curated benchmarks", "Share", "Caveat"],
                   [[r["row"], human(r["archive_bytes"]), human(r["packaged_bytes"]),
                     "" if r["share_percent"] is None else ("below 0.001%" if r["share_percent"] < 0.001 else ("at most " if r["share_is_upper_bound"] else "") + f"{r['share_percent']:.2g}%"),
                     r["caveat"]] for r in n["pairs"]]))
    p.append("<h3>Whole-record copies a compute job can read</h3>")
    p.append("<p>This table is the measure that fits data mining. Regridded stores can be larger than the raw archive, so the byte ratio is shown only to make that visible and is not a coverage fraction: "
             "the ARCO-ERA5 README itself puts ERA5 at about 5 PB, and ECMWF at about 10 PB. GNSS, OOI, DAS, hydrology, InSAR and Sentinel-1 were not searched for this table, so blank disciplines are not evidence of absence.</p>")
    p.append(table(["Discipline", "Copy", "Form", "Size", "As of", "Bytes against source archive", "Weakness"],
                   [[c["discipline"], c["name"], c["form"], c["stated"], c["as_of"], "" if c["byte_ratio_percent"] is None else f"{c['byte_ratio_percent']:.0f}%" + (" (computed sum)" if c["computed"] else ""), c.get("weak", "")] for c in n["copies"]]))
    p.append("<p>Seismology has the smallest curated share of the rows with a large archive and also the clearest case of whole-archive inference, in native miniSEED. Reading the archive for inference is not the same as training on it, and no comparable whole-archive training run was found. "
             "ERA5 is also the discipline where ML models now train on decades of the record. This report does not test whether the packaging caused that, and ERA5 differs in other ways, being a gridded, gap-free model product.</p>")

    # Section 4
    surr = lambda question, selection, code: {
        "question": question,
        "inputs": ["docs/archive_readiness_2026-10-30/simulation_counts.json"],
        "selection": selection,
        "calculation": "Articles naming an ML surrogate per 100 articles naming a numerical method, from title and abstract matches. Queries are in section 7. A surrogate article need not name a numerical method, so this is a ratio of two keyword groups and not a share.",
        "code": code,
        "checked": live_check + within("simulation") + ".",
        "limits": "Attention, not adoption or its rate. Keyword matches miss other surrogate wording, and field labels come from OpenAlex.",
    }
    p.append("<h2>4. Simulations and surrogate models</h2>")
    p.append("<p>Solid-earth science also runs on simulations: wavefield and Green's-function databases, dynamic rupture, ground-motion hazard and full-waveform inversion. "
             "Two measures apply: how often simulation communities publish ML surrogates, and how much simulation output exists in ML-ready form.</p>")
    p.append(figure(FIG / "fig5_surrogate_index_by_field.png", 6, "ML-surrogate articles per 100 simulation articles, by field, 2023 to 2025.",
                    surr("Which fields mention ML surrogates most, relative to their simulation literature?", "Articles 2023 to 2025; fields with at least 2,000 simulation articles.",
                         "scripts/platform_readiness_counts.py collects; scripts/archive_readiness_figures.py, fig_surrogate_fields; build/archive_readiness/fig5_surrogate_index_by_field.")))
    p.append(figure(FIG / "fig6_surrogate_earth_subfields.png", 7, "The same index by Earth and environmental subfield, and by year.",
                    surr("Within the Earth sciences, where do surrogate mentions concentrate, and how have they changed?", "Panel a: subfields of fields 19 and 23 with at least 500 simulation articles, 2023 to 2025. Panel b: all years 2016 to 2025.",
                         "scripts/archive_readiness_figures.py, fig_surrogate_earth; build/archive_readiness/fig6_surrogate_earth_subfields.")))
    p.append(f"<p>Across Earth and environmental sciences the index rose from {n['surr_earth_2016']:.2f} in 2016 to {n['surr_earth_2025']:.1f} in 2025, "
             f"above all fields ({n['surr_all_2025']:.1f}). Climate and atmospheric science carry the rise; geophysics and earth-surface processes are lower.</p>")
    p.append(figure(FIG / "fig7_simulation_corpora.png", 8, "Solid-earth simulation output kept and handled, against ML-ready simulation "
                    "corpora in solid earth and in general physics. Starred totals are summed from repository file sizes.", {
                        "question": "How does the simulation output solid-earth science keeps compare with what is packaged for ML?",
                        "inputs": ["docs/archive_readiness_2026-10-30/simulation_corpora.json"],
                        "selection": "Sixteen items found by web search on 2026-10-30: solid-earth archives and runs, and ML-ready corpora in any field. ClimSim alone is 41.2 TB and DrivAerNet++ 39 TB of the non-solid-earth total.",
                        "calculation": "Bytes as stated by the source. Items marked computed are sums of repository file sizes that no source states.",
                        "code": "scripts/archive_readiness_figures.py, fig_simulation_corpora; build/archive_readiness/fig7_simulation_corpora.",
                        "checked": "Not machine re-queryable and not re-read on 2026-11-06.",
                        "limits": "A purposive list, not a census. Handled during a run is not data kept. No cumulative CyberShake, Syngine or EQSIM volume was found.",
                    }))

    # Section 5
    p.append("<h2>5. Datasets on platforms</h2>")
    p.append(figure(FIG / "fig4_platform_datasets.png", 9, "DataCite datasets mentioning ML and calling themselves AI-ready, and Hugging Face "
                    "dataset repositories, by discipline with two comparison domains.", {
                        "question": "How visible are geoscience datasets where ML practitioners look?",
                        "inputs": ["docs/archive_readiness_2026-10-30/platform_counts.json"],
                        "selection": "Panel a: DataCite dataset DOIs matching one keyword clause per discipline. Panel b: Hugging Face dataset repositories whose id contains a discipline term. Geodesy keeps only 'insar' and 'gnss', because 'sar-' and 'geodes' matched unrelated repositories.",
                        "calculation": "Panel a: share of datasets also matching the ML query; n counts datasets saying AI-ready or ML-ready and is not the denominator. Panel b: unique repository ids per discipline, summed over its terms.",
                        "code": "scripts/platform_readiness_counts.py collects; scripts/archive_readiness_figures.py, fig_platforms; build/archive_readiness/fig4_platform_datasets.",
                        "checked": live_check + "DataCite " + within("datacite") + "; Hugging Face " + within("hf") + ".",
                        "limits": "Metadata and repository names, not contents. Term lists differ in length between disciplines, so panel b cannot show which domain leads. Hydrology is mostly the term 'flood'.",
                    }))
    p.append(f"<p>The AI-ready label is young: DataCite datasets using it number {n['ai_ready_by_year']['2020']} in 2020, "
             f"{n['ai_ready_by_year']['2023']} in 2023 and {n['ai_ready_by_year']['2025']} in 2025. These counts give no evidence of a geoscience lag on hubs, and they cannot rule one out: "
             f"the name-match totals ({n['hf_geo']:,} geoscience, {n['hf_bio']:,} biomedical) come from term lists of different lengths, and no hub total was retrieved as a denominator.</p>")

    p.extend(complexity_section(n["cx"]))

    # Section 7
    p.append("<h2>7. Methods</h2>")
    q = n["queries"]
    p.append(table(["Measure", "Source", "Query or protocol"], [
        ["ML mention rate", "OpenAlex works API, articles with has_abstract:true, group_by year or subfield", q["ml"]],
        ["AI-ready label", "OpenAlex and DataCite", q["ai_ready"]],
        ["Simulation articles", "OpenAlex", q["simulation"]],
        ["ML-surrogate articles", "OpenAlex", q["surrogate_ml"]],
        ["Earth and environmental sciences", "OpenAlex primary topic", "fields/19 (Earth and Planetary Sciences), fields/23 (Environmental Science)"],
        ["Discipline datasets", "DataCite /dois, resource type dataset", "keyword clauses in platform_counts.json"],
        ["Hub repositories", "Hugging Face /api/datasets?search=", "repository-name terms in platform_counts.json"],
        ["DAS frame", "OpenAlex, standalone/config.das_topic.json", 'title_and_abstract.search:"distributed acoustic sensing", article or review, 2020-2025'],
        ["DAS semantic labels", f"Claude Opus 5.5 ({n['prep']['model']}), effort {n['prep']['effort']}, Message Batches",
         f"codebook {n['prep']['codebook_version']}, prompt hash {n['prep']['prompt_sha256'][:12]}..., structured JSON output"],
        ["DAS share bounds", "scripts/das_screen_checks.py", "unknown = in frame, not labeled das_used no, and not das_used yes with a known AI role; lower counts unknowns as not AI, upper as AI"],
        ["DAS test-retest", "scripts/das_screen_checks.py", "same requests, model and prompt hash in two batches; percent agreement and Cohen's kappa"],
        ["Archive and benchmark volumes", "agency pages, reports, papers, repository APIs",
         "values as stated, with source URL, date, quote and a checked-in-text flag; projections flagged"],
        ["Whole-record copies", "analysis_ready_copies.json", "project pages read 2026-11-06; byte ratio is shown, not a coverage fraction"],
        ["Complexity and AI-evidence tables", "papers, textbooks, benchmark specifications, agency pages",
         "values as stated with units, DOI or URL, as-of date, quote and read-in-text flag; checked by scripts/complexity_tables.py"],
        ["Coupled-equation counts", "one cited source per system", "balance laws, vectors expanded to scalars in the stated dimensionality; closures listed, not counted"],
        ["Readiness profile", "readiness_profile.json", "status per discipline and measure, citing row ids; never summed"],
    ]))
    p.append("<p>All paper counts are keyword co-occurrence in titles and abstracts and never establish actual use. The semantic screen labels "
             "the abstract only; a missing abstract or a failed answer stays unclear, never negative. Benchmarks are paired only with an archive "
             "they were drawn from.</p>")

    # Section 8
    p.append("<h2>8. Reproducibility assessment</h2>")
    hashes_ok = sum(h["ok"] for h in n["hashes"])
    das = rq["das_series"]
    same = sum(das["live"].get(y) == v for y, v in das["frozen_2026_10_21"].items())
    changes = "; ".join(f"{y}: {v} to {das['live'].get(y)}" for y, v in sorted(das["frozen_2026_10_21"].items()) if das["live"].get(y) != v)
    p.append(table(["Component", "Frozen input", "How to re-run", f"Status, re-query of {rq_date}"], [
        ["Frozen snapshots", f"{len(n['hashes'])} files under data/ with manifests", "scripts/requery_check.py --offline",
         f"{hashes_ok} of {len(n['hashes'])} hashes match (rerun while building this report)"],
        ["OpenAlex ML and AI-ready counts", "platform_counts.json", "pixi run -e report requery-live", within("openalex") + " (live, no key)"],
        ["OpenAlex ML counts with abstracts", n["ml_abs_path"], "same", within("ml_share_abstract")],
        ["OpenAlex simulation and surrogate counts", "simulation_counts.json", "same", within("simulation")],
        ["DataCite counts", "platform_counts.json", "same", within("datacite")],
        ["Hugging Face counts", "platform_counts.json", "same", within("hf")],
        ["DAS yearly counts (Fig. 2B input)", "data/openalex/2026-10-21", "same", f"{same} of {len(das['frozen_2026_10_21'])} years identical; changed: {changes or 'none'}"],
        ["DAS frame", "harvest of 2026-10-29", "literature_study.py harvest, new folder", f"{drift['second_works']:,} works on {drift['second_harvest']} against {drift['first_works']:,}; {drift['removed']} removed, {drift['added']} added"],
        ["DAS semantic labels", "data/semantic_screen/das_topic_2026-10-29", "pixi run -e semantic das-* tasks",
         f"rerun on the same abstracts on 2026-11-06, ${checks['second_batch']['usd_total']:.2f}; kappa {retest['ai_role']['cohen_kappa']:.2f} for AI role; the frozen labels are unchanged"],
        ["Archive and benchmark volumes", "archives.json, benchmarks.json, analysis_ready_copies.json, simulation_corpora.json", "manual: follow source_url",
         "not machine re-queryable; rows not checked in the source text are flagged"],
        ["Complexity tables and profile", "docs/complexity_2026-10-30", "python scripts/complexity_tables.py",
         "; ".join(n["cx"]["summaries"][:1]) + " (and four more tables; all pass)"],
        ["Figures and this report", "all of the above", "pixi run -e report report", "offline; rebuilt on each run"],
        ["Notebooks", "all of the above", "pixi run -e report notebooks (READINESS_LIVE=1 to re-query)", "see the release validation receipt in provenance/"],
    ]))
    moved = "; ".join(f"{name}: {comp[name]['within_5_percent']} of {comp[name]['metrics_compared']} within 5%" for name in comp)
    errors = "; ".join(rq.get("errors", [])) or "none"
    p.append(f"<p>Indexes change daily, and OpenAlex counts moved noticeably between runs. Against the frozen files, {moved}. Errors in that run: {errors}. "
             "Absolute article counts for several years fell by a few percent as OpenAlex removed records, and one small subfield, Space and Planetary Science, nearly doubled within a day. It falls below the plotting threshold. "
             f"The ML rates, which are ratios, held. {rate_check}. Treat absolute OpenAlex counts as dated snapshots.</p>")
    p.append("<pre>pixi run all                         # release hashes, offline tests, original figures\n"
             "pixi run -e report requery-offline   # frozen-snapshot hashes\n"
             "pixi run -e report requery-live      # re-query all sources, compare, write the dated summary\n"
             "pixi run -e report notebooks         # execute notebooks/01-04\n"
             "pixi run -e report report            # rebuild figures and this HTML</pre>")
    p.append("<p>Notebooks: <code>notebooks/01_das_semantic_screen.ipynb</code>, <code>02_papers_and_platforms.ipynb</code>, "
             "<code>03_archives_simulations_surrogates.ipynb</code>, <code>04_complexity_and_readiness.ipynb</code>.</p>")

    # Section 9
    p.append("<h2>9. Limitations</h2><ul>"
             "<li>Keyword co-occurrence measures attention, not use.</li>"
             f"<li>The DAS labels are unvalidated. {das_status} Test-retest agreement does not replace it.</li>"
             "<li>Archive volumes mix definitions and dates (2020 to 2026). No cumulative volume was found for DAS experiments, USGS NWIS, CyberShake, Syngine or EQSIM, and no per-mission Sentinel volume was found. "
             "The CDSE and Sentinel Data Access report PDFs that may hold one exceeded the fetch limit and were not read.</li>"
             "<li>The 1.3 PB seismic denominator is data used in one study, from a paper Marine Denolle co-authored. It is a lower bound on holdings.</li>"
             "<li>Hugging Face counts match repository names and are upper bounds, with unequal term lists.</li>"
             "<li>The complexity and AI-evidence tables are purposive samples of the literature, not a census; successes and limitations "
             "were both sought, but their counts do not measure how often AI succeeds.</li>"
             "<li>Power-law verdicts come from different tests. A uniform refit of open catalogs has not been done.</li>"
             "<li>The task-conditioned readiness instrument in <code>instrument/</code> has not been applied to any holding here, so this report gives no task-level readiness judgment.</li>"
             "<li>Equation counts depend on the source and dimensionality chosen; they measure model size, not difficulty.</li></ul>")

    # Section 10
    p.append("<h2>10. Changes from the version of 30 October 2026</h2><ul>"
             "<li><b>Archive shares.</b> ARCO-ERA5 moved out of the benchmark share into a whole-record table. Seismology now pairs benchmarks from EarthScope, NCEDC and SCEDC with the 1.3 PB those archives supplied to Ni et al. (2025); it was EarthScope alone. "
             "\"Sentinel-1\" and \"Sentinel-2\" rows, whose denominators covered all ASF SAR and all Sentinel missions, are relabeled to say so, and benchmarks are matched to them. The claim that shares differ by six orders of magnitude is withdrawn.</li>"
             "<li><b>ML rate.</b> Numerator and denominator are limited to articles with an abstract.</li>"
             "<li><b>DAS.</b> The keyword comparison uses one denominator. Bounds, test-retest and frame drift are added. The summary no longer leads with the unvalidated share.</li>"
             "<li><b>Power laws.</b> The 11 rows described as never tested are split into 7 not tested and 4 unknown, and the tests behind the 13 tested rows are listed.</li>"
             "<li><b>Claims withdrawn.</b> \"The readiness gap is volume\", \"method uptake is not the bottleneck\", \"simulation output is the largest untapped resource\", \"adopt ML surrogates more slowly\" and \"platform counts do not show a geoscience lag\" each said more than their measure supports.</li>"
             "<li><b>Code.</b> The Hugging Face geodesy count is read from the data, not typed. Numbers typed into the text are now computed. The dated re-query summary is written by the re-query script. The contact address is removed from the API User-Agent. The pixi workspace version now matches the package.</li>"
             "<li><b>Figures.</b> Each figure now follows a method statement, and the build refuses a figure without one.</li></ul>")
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            "<title>Geoscience AI Readiness</title><style>" + CSS + "</style></head><body>" + "\n".join(p) + "</body></html>\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=str(ROOT / "docs/report/ai_readiness_solid_earth.html"))
    args = parser.parse_args(argv)
    for script in ("archive_readiness_figures.py", "explore_das_semantic.py", "complexity_figures.py"):
        subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True, cwd=ROOT, capture_output=True)
    n = compute()
    if not all(h["ok"] for h in n["hashes"]):
        raise SystemExit("A frozen snapshot no longer matches its manifest; refusing to build the report.")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(n), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB, sha256 {hashlib.sha256(out.read_bytes()).hexdigest()[:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
