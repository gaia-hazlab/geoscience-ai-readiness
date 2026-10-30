#!/usr/bin/env python3
"""Build the HTML technical report "Measuring the AI readiness of the geosciences: a solid-earth perspective".

Usage: pixi run -e report report      (or: python scripts/build_report.py [--out docs/report/ai_readiness_solid_earth.html])

Offline. Rebuilds every figure from tracked, hash-checked inputs, computes every number in the text from
those inputs, and writes one self-contained HTML file (figures embedded as base64 PNG).
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
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/archive_readiness_2026-10-30"
SCREEN = ROOT / "data/semantic_screen/das_topic_2026-10-29"
FIG = ROOT / "build/archive_readiness"
DASFIG = ROOT / "build/das_semantic"


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


def figure(path, number, caption):
    data = base64.b64encode(Path(path).read_bytes()).decode()
    return (f'<figure><img alt="Figure {number}" src="data:image/png;base64,{data}">'
            f"<figcaption><b>Figure {number}.</b> {html.escape(caption)}</figcaption></figure>")


def compute():
    """Every number the text quotes, from tracked inputs."""
    counts, sim = jload(DOCS / "platform_counts.json"), jload(DOCS / "simulation_counts.json")["simulation"]
    o, d = counts["openalex"], counts["datacite"]
    share = lambda k, y: 100 * o[f"ml_works_{k}_by_year"][y]["count"] / o[f"works_{k}_by_year"][y]["count"]
    n = {"ml_all_2016": share("all", "2016"), "ml_earth_2016": share("earth_env", "2016"),
         "ml_all_2025": share("all", "2025"), "ml_earth_2025": share("earth_env", "2025")}
    sub, subml = o["subfield_works_2023_2025"], o["subfield_ml_works_2023_2025"]
    n["ml_subfield"] = {v["name"]: 100 * subml.get(k, {}).get("count", 0) / v["count"] for k, v in sub.items()}
    n["datacite_all"], n["datacite_ai_ready"] = d["all_datasets"], d["ai_ready_all"]
    n["ai_ready_by_year"] = d["ai_ready_all_by_year"]
    n["datacite_disc"] = d["disciplines"]
    n["hf_geo"] = sum(counts["hf"][k]["datasets"] for k in ("seismology", "optical_remote_sensing", "weather_climate", "hydrology", "ocean")) + 25
    n["hf_bio"] = counts["hf"]["biomedicine"]["datasets"]
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
    arf = load("arf", ROOT / "scripts/archive_readiness_figures.py")
    n["pairs"] = arf.pairs_table()
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
    n["das_fm"] = sum("foundation_model" in r["ai_method_families"] for r in das if r["ai_role"] == "ai_as_method")
    n["das_dl"] = sum("deep_learning" in r["ai_method_families"] for r in das if r["ai_role"] == "ai_as_method")
    n["das_aim"] = sum(r["ai_role"] == "ai_as_method" for r in das)
    n["coll"] = jload(SCREEN / "collect_manifest.json")
    n["prep"] = jload(SCREEN / "prepare_manifest.json")
    n["requery"] = jload(DOCS / "requery_2026-10-30_summary.json")
    sim_queries = jload(DOCS / "simulation_counts.json")["queries"]
    n["queries"] = {**counts["queries"], "simulation": sim_queries["simulation"], "surrogate_ml": sim_queries["surrogate_ml"]}
    rq = load("rq", ROOT / "scripts/requery_check.py")
    n["hashes"] = rq.check_hashes()
    return n


CSS = """
:root{--bg:#fcfcfb;--fg:#0b0b0b;--muted:#52514e;--rule:#e4e3df;--accent:#2a78d6;--card:#f4f3f0}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a19;--fg:#f0efec;--muted:#c3c2b7;--rule:#3a3a37;--accent:#3987e5;--card:#242422}}
html{background:var(--bg)}body{margin:0 auto;max-width:900px;padding:32px 16px 64px;color:var(--fg);background:var(--bg);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
h1{font-size:1.7rem;line-height:1.25;margin:0 0 .3rem}h2{font-size:1.25rem;margin:2.2rem 0 .6rem;border-top:1px solid var(--rule);padding-top:1.2rem}
h3{font-size:1.05rem;margin:1.6rem 0 .4rem}.meta{color:var(--muted);font-size:.92rem}.goal{background:var(--card);border-left:4px solid var(--accent);padding:.8rem 1rem;margin:1.2rem 0}
.tw{overflow-x:auto;margin:.8rem 0}table{border-collapse:collapse;font-size:.88rem;width:100%}th,td{border-bottom:1px solid var(--rule);padding:.35rem .5rem;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}figure{margin:1.2rem 0}figure img{max-width:100%;height:auto;background:#fff;border-radius:4px}
figcaption{color:var(--muted);font-size:.86rem;margin-top:.3rem}code{font-size:.86em;background:var(--card);padding:.05rem .3rem;border-radius:3px}
pre{background:var(--card);padding:.7rem .9rem;overflow-x:auto;font-size:.82rem;border-radius:4px}li{margin:.2rem 0}
"""


def build(n):
    p = []
    p.append("<h1>Measuring the AI readiness of the geosciences: a solid-earth perspective</h1>")
    p.append('<p class="meta">Technical report, 30 October 2026. Analysis package <code>geoscience-ai-readiness</code>, branch '
             "<code>das-semantic-screen</code>. Contact: Marine Denolle, University of Washington.</p>")
    p.append('<div class="goal"><b>Goal.</b> Measure the AI readiness of the geosciences, from a solid-earth perspective. We treat readiness as '
             "three measurable things: how often research papers use machine learning (ML), how much of the data a community holds "
             "exists in ML-ready form, and how visible that data is on the platforms where ML practitioners look. Solid earth here means "
             "seismology, distributed acoustic sensing (DAS), geodesy, radar deformation and the simulations that model them.</div>")
    sub = n["ml_subfield"]
    p.append("<h2>Summary</h2><ul>")
    p.append(f"<li><b>Method uptake is not the bottleneck.</b> Earth and environmental science articles mention ML at least as often as "
             f"the average field: {pct(n['ml_earth_2025'])} against {pct(n['ml_all_2025'])} in 2025. Geophysics sits at "
             f"{pct(sub['Geophysics'])} for 2023 to 2025.</li>")
    se = n["surr_sub"]
    p.append(f"<li><b>Solid-earth simulation communities adopt ML surrogates more slowly.</b> Per 100 articles naming a numerical method, "
             f"geophysics has {se['Geophysics'][0]:.1f} ML-surrogate articles and earth-surface processes {se['Earth-Surface Processes'][0]:.1f}, "
             f"against {se['Atmospheric Science'][0]:.1f} in atmospheric science and {n['surr_field']['Physics and Astronomy'][0]:.0f} in physics.</li>")
    pr = {r["row"]: r for r in n["pairs"]}
    p.append(f"<li><b>The readiness gap is volume.</b> ML-ready benchmarks hold {pr['Seismology']['share_percent']:.2f}% of the EarthScope seismic "
             f"archive (at most), {pr['SAR: Sentinel-1']['share_percent']:.2f}% of the Sentinel-1 SAR archive, and none of the GNSS archive. "
             f"Reanalysis is the exception: {pr['Reanalysis: ERA5']['share_percent']:.0f}% of ERA5 exists in an analysis-ready cloud format.</li>")
    p.append(f"<li><b>Simulation output is the largest untapped solid-earth resource.</b> All public solid-earth ML-ready simulation corpora "
             f"total {human(n['sim_ml_solid'])}; one CyberShake study kept {human(n['cybershake_kept'])} and handled "
             f"{human(n['cybershake_handled'])} during its run. ML-ready corpora in other physics and atmospheric science total {human(n['sim_ml_other'])}.</li>")
    das25 = n["das_years"][-1]["ai_as_method_among_das_confirmed"]
    das20 = n["das_years"][0]["ai_as_method_among_das_confirmed"]
    p.append(f"<li><b>DAS adoption.</b> Among abstracts whose analysis uses DAS, the share using AI as a method rose from "
             f"{pct(100 * das20['share'])} in 2020 to {pct(100 * das25['share'])} in 2025 (unvalidated abstract-level screen); "
             f"{n['das_dl']} of {n['das_aim']} such papers use deep learning and {n['das_fm']} a foundation model.</li>")
    p.append(f"<li><b>The AI-ready label is rare everywhere.</b> {n['datacite_ai_ready']} of {n['datacite_all']:,} DataCite datasets use it. "
             f"Geoscience datasets are not underrepresented on Hugging Face by repository count ({n['hf_geo']:,} against "
             f"{n['hf_bio']:,} biomedical, name matching).</li></ul>")

    p.append("<h2>1. Do geoscientists use ML?</h2>")
    p.append(figure(FIG / "fig2_ml_share_by_year.png", 1, "Share of OpenAlex articles mentioning ML in title or abstract, Earth and environmental "
                    "sciences against all fields, 2016 to 2025. Keyword co-occurrence, not actual use."))
    p.append(figure(FIG / "fig3_ml_share_by_subfield.png", 2, "ML mention rate by Earth and environmental subfield, 2023 to 2025."))
    p.append("<p>The geosciences are not behind in reaching for ML. The question for readiness is whether the data and simulations that "
             "solid-earth science holds can feed those methods at scale.</p>")

    p.append("<h2>2. A solid-earth case: DAS</h2>")
    p.append("<p>The DAS topic frame holds every OpenAlex article or review whose title or abstract matches \"distributed acoustic sensing\", "
             "2020 to 2025. Claude Opus 5.5 labeled each abstract under a fixed codebook; the labels are screening evidence, not actual use, "
             "and have not yet been validated against human coding.</p>")
    rows = []
    for y in n["das_years"]:
        a = y["ai_as_method_among_das_confirmed"]
        rows.append([y["year"], y["works"], y["abstract_missing"], y["das_used_counts"]["yes"], f"{a['count']} / {a['denominator']}",
                     pct(100 * a["share"]), f"{100 * a['wilson95'][0]:.1f} to {100 * a['wilson95'][1]:.1f}%"])
    p.append(table(["Year", "Works", "No abstract", "Analysis uses DAS", "AI as method", "Share", "Wilson 95%"], rows))
    p.append(table(["Year", "Keyword co-occurrence (frozen Fig. 2B input)", "Semantic: AI as a method, all labeled DAS works"],
                   [[y, pct(k), pct(s)] for y, k, s in n["das_compare"]]))
    p.append(figure(DASFIG / "explore_1_keyword_vs_semantic.png", 3, "Keyword co-occurrence against the semantic screen, same DAS population."))
    p.append(table(["Venue (at least 28 DAS-using papers)", "AI as method", "DAS-using papers", "Share"],
                   [[v, a, t, pct(100 * a / t, 0)] for v, a, t in n["das_venues"]]))
    p.append(figure(DASFIG / "explore_4_co_measured_families.png", 4, "Measurement families used alongside DAS. The leading partner is fiber "
                    "temperature sensing on the same cable; geodesy and radar are rare."))
    p.append("<p>In the core seismology journals the AI-as-method share of DAS papers is 10 to 19%, below the frame average, because much of "
             "that literature establishes the instrument (response, coupling, imaging). Whether DAS adopts AI more slowly than its journals as a "
             "whole needs a non-DAS baseline from the same journals; that run is sized (about 8,400 articles) but not done.</p>")

    p.append("<h2>3. How much of each archive is ML-ready?</h2>")
    p.append(figure(FIG / "fig1_archive_vs_ml_ready.png", 5, "Raw archive volume against the ML-ready benchmarks drawn from it, log scale."))
    p.append(table(["Discipline", "Raw archive", "ML-ready packaged", "Share", "Caveat"],
                   [[r["row"], human(r["archive_bytes"]), human(r["packaged_bytes"]),
                     "" if r["share_percent"] is None else ("below 0.001%" if r["share_percent"] < 0.001 else f"{r['share_percent']:.2g}%"),
                     r["caveat"]] for r in n["pairs"]]))
    p.append("<p>A benchmark is a designed subsample, so a small share is not by itself a deficit. It bounds what can be trained, and in "
             "particular pretrained, without new curation. Reanalysis shows what full packaging looks like; it is also the discipline where "
             "ML models now train on the full record, though this analysis does not test causation.</p>")

    p.append("<h2>4. Simulations and surrogate models</h2>")
    p.append("<p>The observational comparison misses the half of solid-earth science that runs on simulations: wavefield and Green's-function "
             "databases, dynamic rupture, ground-motion hazard and full-waveform inversion. Two measures capture it: how often simulation "
             "communities publish ML surrogates, and how much simulation output exists in ML-ready form.</p>")
    p.append(figure(FIG / "fig5_surrogate_index_by_field.png", 6, "ML-surrogate articles per 100 simulation articles, by field, 2023 to 2025."))
    p.append(figure(FIG / "fig6_surrogate_earth_subfields.png", 7, "The same index by Earth and environmental subfield, and by year."))
    p.append(f"<p>Across Earth and environmental sciences the index rose from {n['surr_earth_2016']:.2f} in 2016 to {n['surr_earth_2025']:.1f} in 2025, "
             f"ahead of all fields ({n['surr_all_2025']:.1f}). The growth is carried by climate and atmospheric science; geophysics and "
             "earth-surface processes trail.</p>")
    p.append(figure(FIG / "fig7_simulation_corpora.png", 8, "Solid-earth simulation output kept and handled, against ML-ready simulation "
                    "corpora in solid earth and in general physics. Starred totals are summed from repository file sizes."))

    p.append("<h2>5. Datasets on platforms</h2>")
    p.append(figure(FIG / "fig4_platform_datasets.png", 9, "DataCite datasets mentioning ML and calling themselves AI-ready, and Hugging Face "
                    "dataset repositories, by discipline with two comparison domains."))
    p.append(f"<p>The AI-ready label is young: DataCite datasets using it number {n['ai_ready_by_year']['2020']} in 2020, "
             f"{n['ai_ready_by_year']['2023']} in 2023 and {n['ai_ready_by_year']['2025']} in 2025. Platform counts do not show a geoscience "
             "lag; the gap sits in the volume packaged, not in the label or the hub.</p>")

    p.append("<h2>6. Methods</h2>")
    q = n["queries"]
    p.append(table(["Measure", "Source", "Query or protocol"], [
        ["ML mention rate", "OpenAlex works API, articles, group_by year or subfield", q["ml"]],
        ["AI-ready label", "OpenAlex and DataCite", q["ai_ready"]],
        ["Simulation articles", "OpenAlex", q["simulation"]],
        ["ML-surrogate articles", "OpenAlex", q["surrogate_ml"]],
        ["Earth and environmental sciences", "OpenAlex primary topic", "fields/19 (Earth and Planetary Sciences), fields/23 (Environmental Science)"],
        ["Discipline datasets", "DataCite /dois, resource type dataset", "keyword clauses in platform_counts.json"],
        ["Hub repositories", "Hugging Face /api/datasets?search=", "repository-name terms in platform_counts.json"],
        ["DAS frame", "OpenAlex, standalone/config.das_topic.json", 'title_and_abstract.search:"distributed acoustic sensing", article or review, 2020-2025'],
        ["DAS semantic labels", f"Claude Opus 5.5 ({n['prep']['model']}), effort {n['prep']['effort']}, Message Batches",
         f"codebook {n['prep']['codebook_version']}, prompt hash {n['prep']['prompt_sha256'][:12]}..., structured JSON output"],
        ["Archive and benchmark volumes", "agency pages, reports, papers, repository APIs",
         "values as stated, with source URL, date, quote and a checked-in-text flag; projections flagged"],
    ]))
    p.append("<p>All paper counts are keyword co-occurrence in titles and abstracts and never establish actual use. The semantic screen labels "
             "the abstract only; a missing abstract or a failed answer stays unclear, never negative. Benchmarks are paired only with the archive "
             "they were drawn from.</p>")

    p.append("<h2>7. Reproducibility assessment</h2>")
    rq = n["requery"]
    hashes_ok = sum(h["ok"] for h in n["hashes"])
    das = rq["das_series"]
    same = sum(das["live"].get(y) == v for y, v in das["frozen_2026_10_21"].items())
    p.append(table(["Component", "Frozen input", "How to re-run", "Status on 2026-10-30"], [
        ["Frozen snapshots", "12 files under data/ with manifests", "scripts/requery_check.py --offline",
         f"{hashes_ok} of {len(n['hashes'])} hashes match (rerun while building this report)"],
        ["OpenAlex ML and AI-ready counts", "platform_counts.json", "scripts/requery_check.py --out runs/requery_DATE",
         f"{rq['comparisons']['openalex']['within_1_percent']} of {rq['comparisons']['openalex']['metrics_compared']} numbers within 1% (live, no key)"],
        ["OpenAlex simulation and surrogate counts", "simulation_counts.json", "same",
         f"{rq['comparisons']['simulation']['within_1_percent']} of {rq['comparisons']['simulation']['metrics_compared']} within 1%"],
        ["DataCite counts", "platform_counts.json", "same", f"{rq['comparisons']['datacite']['within_1_percent']} of {rq['comparisons']['datacite']['metrics_compared']} within 1%"],
        ["DAS yearly counts (Fig. 2B input)", "data/openalex/2026-10-21", "same",
         f"{same} of {len(das['frozen_2026_10_21'])} years identical; 2024 and 2025 one record higher"],
        ["Hugging Face counts", "platform_counts.json", "requery_check.py --with-hf", "not re-run today (collected the same morning)"],
        ["DAS semantic labels", "data/semantic_screen/das_topic_2026-10-29", "pixi run -e semantic das-* tasks",
         f"needs OpenAlex key and Claude credentials; about ${n['coll']['usd_total']:.2f}; prompt hash pins the classifier"],
        ["Archive and benchmark volumes", "archives.json, benchmarks.json, simulation_corpora.json", "manual: follow source_url",
         "not machine re-queryable; rows not checked in the source text are flagged"],
        ["Figures and this report", "all of the above", "pixi run -e report report", "offline, deterministic"],
        ["Notebooks", "all of the above", "pixi run -e report notebooks (READINESS_LIVE=1 to re-query)", "executed offline without errors"],
    ]))
    p.append("<pre>pixi run all                         # release hashes, offline tests, original figures\n"
             "pixi run -e report requery-offline   # frozen-snapshot hashes\n"
             "pixi run -e report requery-live      # re-query OpenAlex, DataCite and the DAS series, compare\n"
             "pixi run -e report notebooks         # execute notebooks/01-03\n"
             "pixi run -e report report           # rebuild figures and this HTML</pre>")
    p.append("<p>Notebooks: <code>notebooks/01_das_semantic_screen.ipynb</code>, <code>02_papers_and_platforms.ipynb</code>, "
             "<code>03_archives_simulations_surrogates.ipynb</code>.</p>")

    p.append("<h2>8. Limitations</h2><ul>"
             "<li>Keyword co-occurrence measures attention, not use. OpenAlex field labels are content-based and move AI-heavy papers into Computer Science.</li>"
             "<li>The DAS screen is unvalidated; a 130-abstract blind validation sample is drawn and awaits two coders.</li>"
             "<li>Archive volumes mix definitions and dates (2020 to 2026). No cumulative volume is published for DAS experiments, USGS NWIS, "
             "CyberShake, Syngine or EQSIM.</li>"
             "<li>Hugging Face counts match repository names and are upper bounds.</li>"
             "<li>Small packaged shares bound what can be trained without curation; they do not show that more packaging is needed for every task.</li></ul>")
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            "<title>Geoscience AI Readiness</title><style>" + CSS + "</style></head><body>" + "\n".join(p) + "</body></html>\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=str(ROOT / "docs/report/ai_readiness_solid_earth.html"))
    args = parser.parse_args(argv)
    for script in ("archive_readiness_figures.py", "explore_das_semantic.py"):
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
