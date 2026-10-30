#!/usr/bin/env python3
"""Figures for the domain-level AI-readiness assessment of 30 October 2026. Offline.

Usage: python scripts/archive_readiness_figures.py [--out build/archive_readiness]

Inputs (all tracked under docs/archive_readiness_2026-10-30/):
  archives.json         sourced raw-archive volumes
  benchmarks.json       sourced ML-ready benchmark volumes
  platform_counts.json  DataCite, Hugging Face and OpenAlex counts (scripts/platform_readiness_counts.py)

Outputs: four PNG/SVG figures and archive_pairs.csv (the paired volumes behind figure 1).
A benchmark is paired only with the archive it was drawn from; rows without a sourced archive
volume or without a matching benchmark are drawn without a ratio.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib.ticker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figure_style as fs   # noqa: E402  shared look of every report figure

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "archive_readiness_2026-10-30"

# (row label, archive name in archives.json or None, benchmark names in benchmarks.json, caveat)
PAIRS = [
    ("Reanalysis: ERA5", "ECMWF ERA5 (raw, on MARS)", ["ARCO-ERA5 0.25 deg"],
     "ARCO-ERA5 pressure and surface levels only; the model-level store adds 5.88 PB"),
    ("Seismology", "EarthScope seismic archive", ["STEAD", "INSTANCE", "ETHZ", "PNW-ML ComCat", "CEED", "SCEDC (SeisBench)", "CREW"],
     "benchmarks also draw on SCEDC, NCEDC, INGV and Swiss archives; EarthScope alone is the denominator, so the share is an upper bound"),
    ("SAR: Sentinel-1", "ASF DAAC SAR archive", ["Major TOM Core-S1RTC", "Sen1Floods11"],
     "ASF figure from 2023, secondary source; ASF also holds non-Sentinel SAR"),
    ("Optical: Sentinel-2", "Copernicus Data Space Ecosystem (Sentinel)", ["Major TOM Core-S2L2A", "SSL4EO-S12", "SEN12MS", "BigEarthNet v2.0"],
     "CDSE volume covers all Sentinel missions; Major TOM L1C (another ~23 TB) not added"),
    ("Climate projections: CMIP6", "CMIP6 on ESGF, distinct", ["ClimateBench"], "ClimateBench uses one model, NorESM2"),
    ("Geodesy: GNSS", "EarthScope geodetic archive (GAGE)", [], "archive figure from 2020; no released ML-ready GNSS benchmark found"),
    ("Ocean observatory: OOI", "OOI raw data", [], "no ML-ready benchmark derived from OOI found"),
    ("DAS", None, ["QuakeFlow DAS", "DeepSubDAS", "Stanford DAS earthquake detection", "DAS fin whale labeled"],
     "DAS has no central archive with a published volume"),
    ("Hydrology: gauges", None, ["CAMELS US", "Caravan v1.6", "LamaH-CE"], "USGS NWIS publishes site counts, not bytes"),
]
NOTE = ("Sources: docs/archive_readiness_2026-10-30 (archives.json, benchmarks.json), retrieved 2026-10-30. Volumes as stated by "
        "each source; benchmark totals sum the listed datasets with a stated size.")


human = fs.human


def pairs_table():
    archives = {a["archive"]: a for a in json.loads((DOCS / "archives.json").read_text())["archives"]}
    benches = {b["name"]: b for b in json.loads((DOCS / "benchmarks.json").read_text())["datasets"]}
    rows = []
    for label, arch, names, caveat in PAIRS:
        a = archives[arch] if arch else None
        sized = [benches[n] for n in names if benches[n]["bytes"]]
        packaged = sum(b["bytes"] for b in sized) if sized else None
        archive_bytes = a["bytes"] if a else None
        rows.append({"row": label, "archive": arch, "archive_bytes": archive_bytes, "archive_as_of": a["as_of"] if a else None,
                     "archive_lower_bound": bool(a and a["stated"].lstrip().startswith(">")),
                     "benchmarks": "; ".join(b["name"] for b in sized), "packaged_bytes": packaged,
                     "share_percent": 100 * packaged / archive_bytes if packaged and archive_bytes else None, "caveat": caveat})
    return rows


def fig_archive_vs_packaged(out, rows):
    note = NOTE + (" Caveats per row are in archive_pairs.csv. A benchmark is a designed subsample, so a small share is not by "
                   "itself a deficit; it bounds what can be trained without new curation.")
    fig, ax = fs.figure(7.6, 0.56 * len(rows), note, left=1.75, right=0.3)
    fs.header(fig, "Only reanalysis has packaged a large share of its archive for ML",
              "Raw archive volume against the ML-ready benchmarks drawn from it, bytes on a log scale")
    labels = [r["row"] for r in rows]
    fs.bar_axes(ax, labels, log=True)
    ax.set_xlim(1e9, 1e19)
    n = len(rows)
    for i, r in enumerate(rows):
        y = n - 1 - i
        if r["archive_bytes"]:
            fs.hbar(ax, y + 0.17, r["archive_bytes"], fs.CONTEXT, x0=1e9, height=0.3)
            prefix = "more than " if r["archive_lower_bound"] else ""
            fs.tip(ax, r["archive_bytes"], y + 0.17, f"{prefix}{fs.human(r['archive_bytes'])} ({r['archive_as_of']})", color=fs.INK2, size=7)
        else:
            fs.tip(ax, 1e9, y + 0.17, "archive volume not published", color=fs.MUTED, size=7, style="italic", dx=2)
        if r["packaged_bytes"]:
            fs.hbar(ax, y - 0.17, r["packaged_bytes"], fs.FOCUS, x0=1e9, height=0.3)
            pct = r["share_percent"]
            share = "" if not pct else ("   below 0.001% of archive" if pct < 0.001 else f"   {pct:.2g}% of archive")
            fs.tip(ax, r["packaged_bytes"], y - 0.17, fs.human(r["packaged_bytes"]) + share, size=7.5, weight="bold" if share else "normal")
        else:
            fs.tip(ax, 1e9, y - 0.17, "no ML-ready benchmark found", color=fs.MUTED, size=7, style="italic", dx=2)
    ax.set_xticks([1e9, 1e12, 1e15, 1e18], ["1 GB", "1 TB", "1 PB", "1 EB"])
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    fs.swatch_legend(ax, [("Raw archive", fs.CONTEXT), ("ML-ready benchmarks drawn from it", fs.FOCUS)], loc="lower right")
    fs.finish(fig, out, "fig1_archive_vs_ml_ready")


def fig_ml_share_years(out, counts):
    o = counts["openalex"]
    years = sorted(o["works_all_by_year"])
    share = lambda k: [100 * o[f"ml_works_{k}_by_year"][y]["count"] / o[f"works_{k}_by_year"][y]["count"] for y in years]
    xs = [int(y) for y in years]
    note = ("OpenAlex articles 2016-2025, retrieved 2026-10-30; keyword co-occurrence of 'machine learning', 'deep learning' or "
            "'neural network' in title or abstract, not actual use. Earth and environmental sciences = OpenAlex fields 19 and 23 "
            "by primary topic.")
    fig, ax = fs.figure(7.2, 2.9, note, left=0.65, right=2.0)
    fs.header(fig, "Geoscience papers mention ML at least as often as the average field",
              "Share of articles whose title or abstract mentions machine learning, by year")
    a, e = share("all"), share("earth_env")
    fs.series(ax, xs, a, fs.CONTEXT, "All fields")
    fs.series(ax, xs, e, fs.FOCUS, "Earth and environmental sciences")
    fs.tip(ax, xs[-1], e[-1], f"Earth and environmental sciences  {e[-1]:.1f}%", dx=8)
    fs.tip(ax, xs[-1], a[-1], f"All fields  {a[-1]:.1f}%", dx=8, color=fs.INK2)
    ax.set_xticks(xs[::3]); ax.set_xlim(xs[0] - 0.3, xs[-1] + 0.3); ax.set_ylim(0, None)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="x", visible=False); ax.spines["left"].set_visible(False)
    fs.swatch_legend(ax, [("Earth and environmental sciences", fs.FOCUS), ("All fields", fs.CONTEXT)],
                     loc="upper left", marker="line")
    fs.finish(fig, out, "fig2_ml_share_by_year")


def fig_ml_share_subfield(out, counts):
    o = counts["openalex"]
    allw, mlw = o["subfield_works_2023_2025"], o["subfield_ml_works_2023_2025"]
    rows = sorted(((v["name"], v["count"], mlw.get(k, {}).get("count", 0)) for k, v in allw.items() if v["count"] >= 5000),
                  key=lambda r: -r[2] / r[1])
    base_w = sum(o["works_all_by_year"][y]["count"] for y in ("2023", "2024", "2025"))
    base_m = sum(o["ml_works_all_by_year"][y]["count"] for y in ("2023", "2024", "2025"))
    note = ("OpenAlex articles 2023-2025 by primary-topic subfield within fields 19 and 23, subfields with at least 5,000 "
            "articles; keyword co-occurrence, not actual use. Remote sensing papers are mostly filed under other fields. "
            "Article counts per subfield are in platform_counts.json.")
    fig, ax = fs.figure(7.2, 0.27 * len(rows), note, left=2.75, right=0.4)
    fs.header(fig, "ML mention rate by Earth and environmental subfield",
              "Articles mentioning machine learning, 2023 to 2025, against the all-field rate")
    fs.bar_axes(ax, [r[0] for r in rows])
    vals = [100 * m / n for _, n, m in rows]
    for i, v in enumerate(vals):
        y = len(rows) - 1 - i
        fs.hbar(ax, y, v, fs.FOCUS, height=0.56)
        fs.tip(ax, v, y, f"{v:.1f}%")
    ax.set_xlim(0, max(vals) * 1.15)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    fs.reference(ax, 100 * base_m / base_w, f"All fields {100 * base_m / base_w:.1f}%")
    fs.finish(fig, out, "fig3_ml_share_by_subfield")


def fig_platforms(out, counts):
    d, h = counts["datacite"]["disciplines"], counts["hf"]
    order = ["seismology", "geodesy_sar", "optical_remote_sensing", "weather_climate", "hydrology", "ocean", "biomedicine", "materials_chemistry"]
    names = {"seismology": "Seismology", "geodesy_sar": "Geodesy, SAR", "optical_remote_sensing": "Optical remote sensing",
             "weather_climate": "Weather, climate", "hydrology": "Hydrology", "ocean": "Ocean",
             "biomedicine": "Biomedicine", "materials_chemistry": "Materials"}
    comparison = ("biomedicine", "materials_chemistry")
    hf_geo_sar = 25   # insar + gnss id matches only; "sar-" and "geodes" matches were unrelated repositories
    note = ("Retrieved 2026-10-30. A: DataCite dataset DOIs whose metadata match the discipline clause; share also matching "
            "'machine learning', 'deep learning' or 'neural network'; the count after the share is datasets saying AI-ready or "
            "ML-ready. B: Hugging Face dataset ids containing discipline terms (upper bound; hydrology is mostly 'flood'; geodesy "
            "counts 'insar' and 'gnss' only). Queries in platform_counts.json.")
    fig, (ax1, ax2) = fs.figure(8.6, 0.34 * len(order), note, left=1.55, right=0.35, ncols=2, wspace=0.28, sharey=True)
    fs.header(fig, "Geoscience datasets on platforms, against two comparison domains",
              "Blue: geoscience disciplines. Grey: biomedicine and materials, for comparison")
    labels = [names[k] for k in order]
    fs.bar_axes(ax1, labels)
    n = len(order)
    shares = [100 * d[k]["mention_ml"] / d[k]["datasets"] for k in order]
    hf_n = [hf_geo_sar if k == "geodesy_sar" else h[k]["datasets"] for k in order]
    for i, k in enumerate(order):
        y = n - 1 - i
        col = fs.CONTEXT if k in comparison else fs.FOCUS
        fs.hbar(ax1, y, shares[i], col)
        fs.tip(ax1, shares[i], y, f"{shares[i]:.1f}%")
        fs.tip(ax1, shares[i], y, f"{d[k]['mention_ai_ready']} AI-ready", color=fs.MUTED, size=6.8,
               dx=10 + fs.text_width_pt(f"{shares[i]:.1f}%"))
        fs.hbar(ax2, y, hf_n[i], col)
        fs.tip(ax2, hf_n[i], y, f"{hf_n[i]:,}")
    ax1.set_xlim(0, max(shares) * 1.55)
    ax1.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax2.set_xlim(0, max(hf_n) * 1.18)
    ax2.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}K" if v else "0"))
    ax2.spines["bottom"].set_visible(False); ax2.grid(axis="y", visible=False)
    ax1.set_title("A. DataCite datasets mentioning ML")
    ax2.set_title("B. Hugging Face dataset repositories")
    ax1.axhline(1.5, color=fs.AXIS, lw=0.6); ax2.axhline(1.5, color=fs.AXIS, lw=0.6)
    fs.finish(fig, out, "fig4_platform_datasets")


SURR_NOTE = ("OpenAlex articles, retrieved 2026-10-30. Index = articles naming an ML surrogate (physics-informed neural "
             "network, neural operator, DeepONet, or a surrogate model or emulator together with an ML term) per 100 articles naming a "
             "numerical method (finite element, finite difference, spectral element, finite volume, numerical simulation). Keyword "
             "co-occurrence by primary topic; an index, not the share of simulation papers that use surrogates. Counts behind each "
             "index are in simulation_counts.json.")


def surrogate_index(surr, sim, key):
    m, n = surr.get(key, {}).get("count", 0), sim[key]["count"]
    return 100 * m / n, m, n


def fig_surrogate_fields(out, sim_counts):
    s = sim_counts["simulation"]
    sim, surr = s["field_sim_2023_2025"], s["field_surr_ml_2023_2025"]
    keys = [k for k in sim if sim[k]["count"] >= 2000]
    rows = sorted(((sim[k]["name"], *surrogate_index(surr, sim, k)) for k in keys), key=lambda r: -r[1])
    earth = {"Earth and Planetary Sciences", "Environmental Science"}
    fig, ax = fs.figure(7.2, 0.3 * len(rows), SURR_NOTE + " Fields with at least 2,000 simulation articles, 2023 to 2025.",
                        left=2.1, right=0.4)
    fs.header(fig, "Physics leads in ML surrogates; Earth sciences sit mid-table",
              "ML-surrogate articles per 100 simulation articles, 2023 to 2025. Blue: Earth and environmental fields")
    fs.bar_axes(ax, [r[0] for r in rows])
    for i, (name, v, _, _) in enumerate(rows):
        y = len(rows) - 1 - i
        fs.hbar(ax, y, v, fs.FOCUS if name in earth else fs.CONTEXT)
        fs.tip(ax, v, y, f"{v:.1f}")
    ax.set_xlim(0, max(r[1] for r in rows) * 1.12)
    fs.finish(fig, out, "fig5_surrogate_index_by_field")


def fig_surrogate_earth(out, sim_counts):
    s = sim_counts["simulation"]
    sim, surr = s["subfield_sim_2023_2025"], s["subfield_surr_ml_2023_2025"]
    keys = [k for k in sim if sim[k]["count"] >= 500]
    short = {"Management, Monitoring, Policy and Law": "Environmental management, policy"}
    rows = sorted(((short.get(sim[k]["name"], sim[k]["name"]), *surrogate_index(surr, sim, k)) for k in keys), key=lambda r: -r[1])
    solid = {"Geophysics", "Earth-Surface Processes", "Geology", "Geochemistry and Petrology"}
    fig, (ax1, ax2) = fs.figure(9.2, 2.6, SURR_NOTE + " Panel A: subfields of OpenAlex fields 19 and 23 with at least 500 "
                                "simulation articles, 2023 to 2025. Panel B: all years 2016 to 2025.",
                                left=2.15, right=1.75, ncols=2, wspace=0.55)
    fs.header(fig, "Solid-earth simulation communities adopt ML surrogates more slowly",
              "ML-surrogate articles per 100 simulation articles")
    fs.bar_axes(ax1, [r[0] for r in rows])
    for i, (name, v, _, _) in enumerate(rows):
        y = len(rows) - 1 - i
        fs.hbar(ax1, y, v, fs.FOCUS if name in solid else fs.CONTEXT)
        fs.tip(ax1, v, y, f"{v:.1f}")
    ax1.set_xlim(0, max(r[1] for r in rows) * 1.18)
    ax1.set_title("A. By subfield, 2023 to 2025 (blue: solid earth)")
    years = sorted(s["sim_all_by_year"])
    xs = [int(y) for y in years]
    for key, label, color in (("all", "All fields", fs.CONTEXT), ("earth_env", "Earth and environmental", fs.FOCUS)):
        a, b = s[f"surr_ml_{key}_by_year"], s[f"sim_{key}_by_year"]
        ys = [100 * a.get(y, {"count": 0})["count"] / b[y]["count"] for y in years]
        fs.series(ax2, xs, ys, color, label)
        fs.tip(ax2, xs[-1], ys[-1], f"{label}  {ys[-1]:.1f}", dx=8, color=fs.INK if key == "earth_env" else fs.INK2)
    ax2.set_xticks(xs[::3]); ax2.set_xlim(xs[0] - 0.3, xs[-1] + 0.3); ax2.set_ylim(0, None)
    ax2.grid(axis="x", visible=False); ax2.spines["left"].set_visible(False)
    ax2.set_title("B. By year, Earth and environmental against all fields")
    fs.swatch_legend(ax2, [("Earth and environmental", fs.FOCUS), ("All fields", fs.CONTEXT)], loc="upper left", marker="line")
    fs.finish(fig, out, "fig6_surrogate_earth_subfields")


def fig_simulation_corpora(out):
    data = json.loads((DOCS / "simulation_corpora.json").read_text())["rows"]
    group_of = lambda r: (0 if r["side"] == "simulation generated" else 1 if r["side"] == "simulation archive"
                          else 2 if r["domain"] == "solid_earth" else 3)
    groups = [("Solid earth, handled during one run", fs.FOCUS_LIGHT), ("Solid earth, output kept", fs.FOCUS),
              ("Solid earth, ML-ready corpora", fs.SECOND), ("Other physics, ML-ready corpora", fs.CONTEXT)]
    short = lambda n: n.replace("CyberShake Study ", "CyberShake ").replace(", managed during run", ", handled in run")
    rows = []
    for g in range(4):
        rows += sorted([r for r in data if group_of(r) == g], key=lambda r: -r["bytes"])
    note = ("Sources: docs/archive_readiness_2026-10-30/simulation_corpora.json, retrieved 2026-10-30. * total summed from "
            "repository file sizes, not stated by the source. 'Handled during one run' is data the CyberShake workflow managed, "
            "not data kept. No cumulative CyberShake, Syngine or EQSIM archive volume is published.")
    gap = 0.7
    ypos, y = [], 0.0
    for i, r in enumerate(rows):
        if i and group_of(r) != group_of(rows[i - 1]):
            y += gap
        ypos.append(y); y += 1
    fig, ax = fs.figure(7.6, 0.27 * y, note, left=2.25, right=0.3)
    fs.header(fig, "One CyberShake study keeps more data than all solid-earth ML-ready simulation corpora",
              "Bytes on a log scale, by what the data are")
    top = ypos[-1]
    for r, yy in zip(rows, ypos):
        fs.hbar(ax, top - yy, r["bytes"], groups[group_of(r)][1], x0=1e8, height=0.6)
        fs.tip(ax, r["bytes"], top - yy, fs.human(r["bytes"]))
    ax.set_xscale("log"); ax.set_xlim(1e8, 1e17)
    ax.set_ylim(-0.7, top + 0.7)
    ax.set_yticks([top - yy for yy in ypos], [short(r["name"]) + (" *" if r["computed"] else "") for r in rows])
    ax.set_xticks([1e9, 1e12, 1e15], ["1 GB", "1 TB", "1 PB"])
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.grid(axis="y", visible=False); ax.spines["bottom"].set_visible(False)
    fs.swatch_legend(ax, groups, loc="lower right")
    fs.finish(fig, out, "fig7_simulation_corpora")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=str(ROOT / "build" / "archive_readiness"))
    args = parser.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    rows = pairs_table()
    with (out / "archive_pairs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    counts = json.loads((DOCS / "platform_counts.json").read_text())
    fig_archive_vs_packaged(out, rows)
    fig_ml_share_years(out, counts)
    fig_ml_share_subfield(out, counts)
    fig_platforms(out, counts)
    sim_counts = json.loads((DOCS / "simulation_counts.json").read_text())
    fig_surrogate_fields(out, sim_counts)
    fig_surrogate_earth(out, sim_counts)
    fig_simulation_corpora(out)
    for r in rows:
        archive = human(r["archive_bytes"]) if r["archive_bytes"] else "-"
        packaged = human(r["packaged_bytes"]) if r["packaged_bytes"] else "-"
        share = "" if r["share_percent"] is None else f"{r['share_percent']:.3g}%"
        print(f"{r['row']:28s} archive {archive:>10}  packaged {packaged:>10}  share {share}")
    print(f"figures in {out}")


if __name__ == "__main__":
    main()
