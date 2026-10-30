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
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "archive_readiness_2026-10-30"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"   # reference palette slots 1-3 (dataviz skill)
INK, INK2, GRID, NEUTRAL = "#0b0b0b", "#52514e", "#e4e3df", "#b9b8b2"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.axisbelow": True, "axes.titlelocation": "left", "axes.titlesize": 10})

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


def human(n):
    for unit, scale in (("PB", 1e15), ("TB", 1e12), ("GB", 1e9), ("MB", 1e6)):
        if n >= scale:
            return f"{n / scale:.3g} {unit}"
    return f"{n:.3g} B"


def finish(fig, out, name, note):
    width = int(fig.get_figwidth() * 17)
    fig.text(0.01, 0.01, "\n".join(textwrap.fill(p, width) for p in note.split("\n")), fontsize=6.5, color=INK2, va="bottom")
    for ext in ("png", "svg"):
        fig.savefig(out / f"{name}.{ext}", dpi=200)
    plt.close(fig)


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
    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    fig.subplots_adjust(left=0.24, right=0.97, top=0.90, bottom=0.17)
    labels = [r["row"] for r in rows][::-1]
    y = range(len(labels))
    for i, r in enumerate(rows[::-1]):
        if r["archive_bytes"]:
            ax.barh(i + 0.19, r["archive_bytes"], height=0.36, color=S1, label="Raw archive" if i == 0 else None)
            prefix = "more than " if r["archive_lower_bound"] else ""
            ax.text(r["archive_bytes"] * 1.25, i + 0.19, prefix + human(r["archive_bytes"]) + f" ({r['archive_as_of']})",
                    va="center", fontsize=7.5, color=INK)
        else:
            ax.text(2e9, i + 0.19, "archive volume not published", va="center", fontsize=7.5, color=INK2, style="italic")
        if r["packaged_bytes"]:
            ax.barh(i - 0.19, r["packaged_bytes"], height=0.36, color=S2, label="ML-ready packaged" if i == 0 else None)
            pct = r["share_percent"]
            share = "" if not pct else ("  (below 0.001% of archive)" if pct < 0.001 else f"  ({pct:.2g}% of archive)")
            ax.text(r["packaged_bytes"] * 1.25, i - 0.19, human(r["packaged_bytes"]) + share, va="center", fontsize=7.5, color=INK)
        else:
            ax.text(2e9, i - 0.19, "no ML-ready benchmark found", va="center", fontsize=7.5, color=INK2, style="italic")
    ax.set_xscale("log")
    ax.set_xlim(1e9, 1e20)
    ax.set_xticks([1e9, 1e12, 1e15, 1e18], ["1 GB", "1 TB", "1 PB", "1 EB"])
    ax.set_yticks(list(y), labels)
    ax.set_xlabel("Bytes (log scale)")
    ax.grid(axis="y", visible=False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=S1), plt.Rectangle((0, 0), 1, 1, color=S2)]
    ax.legend(handles, ["Raw archive", "ML-ready benchmarks drawn from it"], frameon=False, loc="lower right", fontsize=8)
    fig.suptitle("Only reanalysis has packaged a large share of its archive for ML", x=0.01, ha="left", fontsize=10, color=INK)
    finish(fig, out, "fig1_archive_vs_ml_ready", NOTE + " Caveats per row are in archive_pairs.csv. A benchmark is a designed "
           "subsample, so a small share is not by itself a deficit; it bounds what can be trained without new curation.")


def fig_ml_share_years(out, counts):
    o = counts["openalex"]
    years = sorted(o["works_all_by_year"])
    share = lambda k: [100 * o[f"ml_works_{k}_by_year"][y]["count"] / o[f"works_{k}_by_year"][y]["count"] for y in years]
    xs = [int(y) for y in years]
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    fig.subplots_adjust(left=0.10, right=0.74, top=0.88, bottom=0.22)
    a, e = share("all"), share("earth_env")
    ax.plot(xs, e, color=S1, lw=2, marker="o", ms=4.5, label="Earth and environmental sciences")
    ax.plot(xs, a, color=S2, lw=2, marker="o", ms=4.5, label="All fields")
    ax.text(xs[-1] + 0.15, e[-1], f"Earth and environmental\nsciences {e[-1]:.1f}%", va="center", fontsize=8, color=INK)
    ax.text(xs[-1] + 0.15, a[-1], f"All fields {a[-1]:.1f}%", va="center", fontsize=8, color=INK)
    ax.set_xticks(xs[::2]); ax.set_ylim(0, None); ax.set_ylabel("Articles mentioning ML (%)")
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    ax.set_title("Geoscience papers mention ML at least as often as the average field")
    finish(fig, out, "fig2_ml_share_by_year", "OpenAlex articles 2016-2025, retrieved 2026-10-30; keyword co-occurrence of 'machine learning', "
           "'deep learning' or 'neural network' in title or abstract, not actual use. Earth and environmental sciences = OpenAlex "
           "fields 19 and 23 by primary topic.")


def fig_ml_share_subfield(out, counts):
    o = counts["openalex"]
    allw, mlw = o["subfield_works_2023_2025"], o["subfield_ml_works_2023_2025"]
    rows = sorted(((v["name"], v["count"], mlw.get(k, {}).get("count", 0)) for k, v in allw.items() if v["count"] >= 5000),
                  key=lambda r: r[2] / r[1])
    base_w = sum(o["works_all_by_year"][y]["count"] for y in ("2023", "2024", "2025"))
    base_m = sum(o["ml_works_all_by_year"][y]["count"] for y in ("2023", "2024", "2025"))
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    fig.subplots_adjust(left=0.40, right=0.95, top=0.90, bottom=0.17)
    vals = [100 * m / n for _, n, m in rows]
    ax.barh([r[0] for r in rows], vals, color=S1, height=0.62)
    for i, ((_, n, m), v) in enumerate(zip(rows, vals)):
        ax.text(v + 0.2, i, f"{v:.1f}%  ({m:,} of {n:,})", va="center", fontsize=7, color=INK)
    ax.axvline(100 * base_m / base_w, color=INK2, lw=1, ls="--")
    ax.text(100 * base_m / base_w + 0.2, len(rows) - 0.4, f"all fields {100 * base_m / base_w:.1f}%", fontsize=7.5, color=INK2)
    ax.set_xlim(0, max(vals) * 1.45); ax.set_xlabel("Articles mentioning ML, 2023-2025 (%)")
    ax.grid(axis="y", visible=False)
    fig.suptitle("ML mention rate by Earth and environmental subfield", x=0.01, ha="left", fontsize=10, color=INK)
    finish(fig, out, "fig3_ml_share_by_subfield", "OpenAlex articles 2023-2025 by primary-topic subfield within fields 19 and 23, subfields with "
           "at least 5,000 articles; keyword co-occurrence, not actual use. Remote sensing papers are mostly filed under other fields.")


def fig_platforms(out, counts):
    d, h = counts["datacite"]["disciplines"], counts["hf"]
    order = ["seismology", "geodesy_sar", "optical_remote_sensing", "weather_climate", "hydrology", "ocean", "biomedicine", "materials_chemistry"]
    names = {"seismology": "Seismology", "geodesy_sar": "Geodesy, SAR", "optical_remote_sensing": "Optical remote sensing",
             "weather_climate": "Weather, climate", "hydrology": "Hydrology", "ocean": "Ocean",
             "biomedicine": "Biomedicine (comparison)", "materials_chemistry": "Materials (comparison)"}
    hf_geo_sar = 25   # insar + gnss id matches only; "sar-" and "geodes" matches were unrelated repositories
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.4), sharey=True)
    fig.subplots_adjust(left=0.22, right=0.97, top=0.84, bottom=0.22, wspace=0.12)
    labels = [names[k] for k in order][::-1]
    shares = [100 * d[k]["mention_ml"] / d[k]["datasets"] for k in order][::-1]
    colors = [S3 if k in ("biomedicine", "materials_chemistry") else S1 for k in order][::-1]
    ax1.barh(labels, shares, color=colors, height=0.62)
    for i, k in enumerate(order[::-1]):
        ax1.text(shares[i] + 0.15, i, f"{shares[i]:.1f}%  AI-ready: {d[k]['mention_ai_ready']}", va="center", fontsize=7, color=INK)
    ax1.set_xlim(0, max(shares) * 1.7); ax1.set_xlabel("DataCite datasets mentioning ML (%)")
    ax1.set_title("A. Registered datasets (DataCite DOIs)")
    hf_n = [hf_geo_sar if k == "geodesy_sar" else h[k]["datasets"] for k in order][::-1]
    ax2.barh(labels, hf_n, color=colors, height=0.62)
    for i, v in enumerate(hf_n):
        ax2.text(v + 40, i, f"{v:,}", va="center", fontsize=7, color=INK)
    ax2.set_xlim(0, max(hf_n) * 1.2); ax2.set_xlabel("Hugging Face dataset repositories (name match)")
    ax2.set_title("B. AI-native hub (Hugging Face)")
    for ax in (ax1, ax2):
        ax.grid(axis="y", visible=False)
    fig.suptitle("Geoscience datasets on platforms, against two comparison domains", x=0.01, ha="left", fontsize=10, color=INK)
    finish(fig, out, "fig4_platform_datasets", "Retrieved 2026-10-30. A: DataCite dataset DOIs whose metadata match the discipline clause; share also "
           "matching 'machine learning', 'deep learning' or 'neural network'; 'AI-ready' counts metadata saying AI-ready or ML-ready. "
           "B: Hugging Face dataset ids containing discipline terms (upper bound; hydrology is mostly 'flood'; geodesy counts 'insar' and 'gnss' only). "
           "Queries in platform_counts.json.")


SURR_NOTE = ("OpenAlex articles 2023-2025, retrieved 2026-10-30. Index = articles naming an ML surrogate (physics-informed neural "
             "network, neural operator, DeepONet, or a surrogate model or emulator together with an ML term) per 100 articles naming a "
             "numerical method (finite element, finite difference, spectral element, finite volume, numerical simulation). Keyword "
             "co-occurrence by primary topic; an index, not the share of simulation papers that use surrogates.")


def surrogate_index(surr, sim, key):
    m, n = surr.get(key, {}).get("count", 0), sim[key]["count"]
    return 100 * m / n, m, n


def fig_surrogate_fields(out, sim_counts):
    s = sim_counts["simulation"]
    sim, surr = s["field_sim_2023_2025"], s["field_surr_ml_2023_2025"]
    keys = [k for k in sim if sim[k]["count"] >= 2000]
    rows = sorted(((sim[k]["name"], *surrogate_index(surr, sim, k)) for k in keys), key=lambda r: r[1])
    earth = {"Earth and Planetary Sciences", "Environmental Science"}
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    fig.subplots_adjust(left=0.34, right=0.95, top=0.88, bottom=0.25)
    ax.barh([r[0] for r in rows], [r[1] for r in rows], color=[S1 if r[0] in earth else NEUTRAL for r in rows], height=0.62)
    for i, (_, v, m, n) in enumerate(rows):
        ax.text(v + 0.4, i, f"{v:.1f}  ({m:,} of {n:,})", va="center", fontsize=7, color=INK)
    ax.set_xlim(0, max(r[1] for r in rows) * 1.35)
    ax.set_xlabel("ML-surrogate articles per 100 simulation articles")
    ax.grid(axis="y", visible=False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=S1), plt.Rectangle((0, 0), 1, 1, color=NEUTRAL)]
    ax.legend(handles, ["Earth and environmental fields", "Other fields"], frameon=False, loc="lower right", fontsize=8)
    fig.suptitle("Physics leads in ML surrogates; Earth sciences sit mid-table", x=0.01, ha="left", fontsize=10, color=INK)
    finish(fig, out, "fig5_surrogate_index_by_field", SURR_NOTE + " Fields with at least 2,000 simulation articles.")


def fig_surrogate_earth(out, sim_counts):
    s = sim_counts["simulation"]
    sim, surr = s["subfield_sim_2023_2025"], s["subfield_surr_ml_2023_2025"]
    keys = [k for k in sim if sim[k]["count"] >= 500]
    short = {"Management, Monitoring, Policy and Law": "Environmental management, policy"}
    rows = sorted(((short.get(sim[k]["name"], sim[k]["name"]), *surrogate_index(surr, sim, k)) for k in keys), key=lambda r: r[1])
    solid = {"Geophysics", "Earth-Surface Processes", "Geology", "Geochemistry and Petrology"}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.2))
    fig.subplots_adjust(left=0.23, right=0.86, top=0.84, bottom=0.25, wspace=0.55)
    ax1.barh([r[0] for r in rows], [r[1] for r in rows], color=[S2 if r[0] in solid else S1 for r in rows], height=0.62)
    for i, (_, v, m, n) in enumerate(rows):
        ax1.text(v + 0.3, i, f"{v:.1f}  ({m} of {n:,})", va="center", fontsize=7, color=INK)
    ax1.set_xlim(0, max(r[1] for r in rows) * 1.6)
    ax1.set_xlabel("ML-surrogate per 100 simulation articles, 2023-2025")
    ax1.grid(axis="y", visible=False)
    ax1.set_title("A. By subfield (orange = solid earth)")
    years = sorted(s["sim_all_by_year"])
    xs = [int(y) for y in years]
    for key, label, color in (("earth_env", "Earth and environmental", S1), ("all", "All fields", INK2)):
        a, b = s[f"surr_ml_{key}_by_year"], s[f"sim_{key}_by_year"]
        ys = [100 * a.get(y, {"count": 0})["count"] / b[y]["count"] for y in years]
        ax2.plot(xs, ys, color=color, lw=2, marker="o", ms=4.5, label=label)
        ax2.text(xs[-1] + 0.2, ys[-1], f"{label}\n{ys[-1]:.1f}", va="center", fontsize=8, color=INK)
    ax2.set_xticks(xs[::3]); ax2.set_ylim(0, None)
    ax2.set_ylabel("ML-surrogate per 100 simulation articles")
    ax2.legend(frameon=False, loc="upper left", fontsize=8)
    ax2.set_title("B. By year, 2016-2025")
    fig.suptitle("Solid-earth simulation communities adopt ML surrogates more slowly", x=0.01, ha="left", fontsize=10, color=INK)
    finish(fig, out, "fig6_surrogate_earth_subfields", SURR_NOTE + " Panel A: subfields of OpenAlex fields 19 and 23 with at least 500 "
           "simulation articles. Panel B uses all years 2016-2025.")


def fig_simulation_corpora(out):
    data = json.loads((DOCS / "simulation_corpora.json").read_text())["rows"]
    groups = [("simulation generated", "Solid earth: generated during one CyberShake study", INK2),
              ("simulation archive", "Solid earth: kept in archives", S1),
              ("ML-ready simulation corpus", None, None)]
    order = []
    for side, _, _ in groups[:2]:
        order += sorted([r for r in data if r["side"] == side], key=lambda r: r["bytes"])
    ml = [r for r in data if r["side"] == "ML-ready simulation corpus"]
    order += sorted([r for r in ml if r["domain"] == "solid_earth"], key=lambda r: r["bytes"])
    order += sorted([r for r in ml if r["domain"] != "solid_earth"], key=lambda r: r["bytes"])
    color = lambda r: (INK2 if r["side"] == "simulation generated" else S1 if r["side"] == "simulation archive"
                       else S2 if r["domain"] == "solid_earth" else NEUTRAL)
    order = order[::-1]
    fig, ax = plt.subplots(figsize=(8.0, 6.0))
    fig.subplots_adjust(left=0.30, right=0.97, top=0.91, bottom=0.17)
    short = lambda n: n.replace("CyberShake Study ", "CyberShake ").replace(", managed during run", ", handled in run")
    labels = [short(r["name"]) + (" *" if r["computed"] else "") for r in order]
    ax.barh(labels, [r["bytes"] for r in order], color=[color(r) for r in order], height=0.62)
    for i, r in enumerate(order):
        ax.text(r["bytes"] * 1.3, i, human(r["bytes"]), va="center", fontsize=7.5, color=INK)
    ax.set_xscale("log"); ax.set_xlim(5e8, 1e18)
    ax.set_xticks([1e9, 1e12, 1e15], ["1 GB", "1 TB", "1 PB"])
    ax.grid(axis="y", visible=False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (INK2, S1, S2, NEUTRAL)]
    ax.legend(handles, ["Solid earth, handled in one run", "Solid earth, output kept",
                        "Solid earth, ML-ready", "Other physics, ML-ready"],
              frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.56), fontsize=7.5)
    fig.suptitle("One CyberShake study keeps more data than all solid-earth ML-ready simulation corpora combined",
                 x=0.01, ha="left", fontsize=10, color=INK)
    finish(fig, out, "fig7_simulation_corpora", "Sources: docs/archive_readiness_2026-10-30/simulation_corpora.json, retrieved 2026-10-30. "
           "* total summed from repository file sizes, not stated by the source. 'Handled during one run' is data the CyberShake "
           "workflow managed, not data kept. No cumulative CyberShake, Syngine or EQSIM archive volume is published.")


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
