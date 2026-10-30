#!/usr/bin/env python3
"""Figures for the geoscience complexity scoping of 30 October 2026. Offline.

Usage: python scripts/complexity_figures.py [--out build/complexity]

Inputs (tracked under docs/complexity_2026-10-30/, validated by scripts/complexity_tables.py):
  power_laws.json    sourced exponents with convention and test-against-alternatives verdict
  coupled_pdes.json  balance-equation and state-variable counts per coupled system
  readiness_profile.json  per-discipline readiness profile (statuses and cited row ids)
  ../archive_readiness_2026-10-30/  archive and benchmark volumes (via scripts/archive_readiness_figures.py)

Outputs: three PNG/SVG figures, power_law_pdf_exponents.csv (the rows behind figure 1) and
readiness_profile.csv (the cells behind figure 3).
Figure 1 draws only exponents that the source states in the density convention p(x) ~ x^-alpha;
a source that writes the exponent with its sign (x^-2.40 reported as -2.40) is drawn by magnitude.
No other convention is converted, and the figures never combine directions into one score.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("complexity_tables", ROOT / "scripts" / "complexity_tables.py")
ct = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ct)
_spec = importlib.util.spec_from_file_location("archive_readiness_figures", ROOT / "scripts" / "archive_readiness_figures.py")
arf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(arf)
sys.path.insert(0, str(ROOT / "scripts"))
import figure_style as fs   # noqa: E402  shared look of every report figure
plt = fs.plt

# Rows whose source states a density exponent, p(x) ~ x^-alpha (or dN/dx ~ x^-alpha), with a short plot label.
PDF_ROWS = {
    "pl-01": "Earthquake amplitude, California",
    "pl-02": "Seismic moment, southern California",
    "pl-03": "Seismic moment, global CMT",
    "pl-10": "Landslide area, 3 event inventories",
    "pl-11": "Landslide area, Umbria-Marche",
    "pl-12": "Landslide area, Taiwan and New Zealand",
    "pl-18": "River drainage area",
    "pl-21": "Wildfire area, USA and Australia",
    "pl-22": "Wildfire area, Angola",
    "pl-23": "Wildfire area, Canada boreal",
    "pl-24": "Wildfire area, US federal land",
    "pl-26": "Tropical cyclone power dissipation",
    "pl-25": "Solar flare intensity",
    "pl-29": "Word frequency, Moby Dick",
    "pl-30": "US city population",
    "pl-31": "Citations, 1981 papers",
    "pl-32": "Web site hits, AOL",
    "pl-33": "Net worth, richest Americans",
}
PDE_LABELS = {
    "pde-01": "Earthquake cycle, quasi-dynamic (SEAS BP1-QD)",
    "pde-02": "Earthquake cycle, fully dynamic (SEAS BP1-FD)",
    "pde-03": "Earthquake cycle, 3D (SEAS BP5)",
    "pde-04": "Earthquake cycle with fluid injection (SEAS BP6-QD)",
    "pde-05": "Biot poroelasticity, quasi-static",
    "pde-06": "Thermo-poro-elasticity",
    "pde-07": "Two-phase melt migration (simplified McKenzie)",
    "pde-09": "Volcanic conduit, steady homogeneous mixture",
    "pde-10": "Volcanic conduit with bubble growth",
    "pde-11": "Ice sheet: full Stokes plus heat",
    "pde-12": "Ice-shelf meltwater plume, three-equation melt",
    "pde-13": "Glacier-ocean composite (ice sheet + plume)",
    "pde-14": "Rain infiltration and slope stability (TRIGRS)",
    "pde-15": "Atmosphere primitive equations with moisture",
    "pde-16": "Ocean primitive equations",
    "pde-17": "Coupled atmosphere-ocean-sea ice",
    "pde-18": "Incompressible Navier-Stokes",
    "pde-19": "Maxwell's equations",
    "pde-20": "Ideal magnetohydrodynamics",
}
VERDICT_STYLE = {  # verdict: (colour, filled, legend label); slots 1-3 of the validated palette
    "tested, power law favored": (fs.THIRD, True, "Tested: power law favored"),
    "tested, mixed": (fs.FOCUS, True, "Tested: mixed result"),
    "tested, alternative favored or not distinguishable": (fs.SECOND, True, "Tested: alternative favored or equally good"),
    "not tested in this source": (fs.MUTED, False, "Not tested against alternatives"),
    "not stated": (fs.MUTED, False, "Not tested against alternatives"),
}


def pdf_exponent_rows(power):
    """Rows of figure 1: density exponents by magnitude, with the source's sign convention noted."""
    rows = []
    by_id = {r["id"]: r for r in power["rows"]}
    for rid, label in PDF_ROWS.items():
        r = by_id[rid]
        vals = [abs(v) for v in (r["value"], r["value_min"], r["value_max"]) if v is not None]
        rows.append({"id": rid, "label": label, "domain": r["domain"], "point": abs(r["value"]) if r["value"] is not None else None,
                     "low": min(vals), "high": max(vals), "sign_flipped": any(v is not None and v < 0 for v in
                                                                            (r["value"], r["value_min"], r["value_max"])),
                     "verdict": r["tested_vs_alternatives"], "symbol": r["symbol"], "source": r["source"],
                     "doi": r["doi"], "checked_in_text": r["checked_in_text"]})
    return rows


def fig_power_laws(out, rows):
    geo = [r for r in rows if r["domain"] == "geoscience"]
    comp = [r for r in rows if r["domain"] != "geoscience"]
    order = geo + comp
    note = ("Sources: docs/complexity_2026-10-30/power_laws.json (rows listed in power_law_pdf_exponents.csv), retrieved "
            "2026-10-30. Only exponents stated in the density convention are drawn; b-values, survivor-function exponents, "
            "Hack's law and fractal dimensions use other conventions and stay in the table, not converted. Bars are ranges "
            "stated by the source. Landslide exponents written with a minus sign by their sources are drawn by magnitude. "
            "'Tested' means compared with lognormal, stretched exponential or truncated forms in that source.")
    gap = 0.8
    n = len(order)
    ys = [n - 1 - i + (gap if r["domain"] == "geoscience" else 0) for i, r in enumerate(order)]
    fig, ax = fs.figure(7.6, 0.25 * (n + gap) + 0.35, note, left=2.45, right=0.35)
    fs.header(fig, "Heavy tails are common; a pure power law rarely beats the alternatives",
              "Density exponent alpha in p(x) ~ x^-alpha, as stated by each source, coloured by its test against alternatives")
    for r, y in zip(order, ys):
        colour, filled, _ = VERDICT_STYLE[r["verdict"]]
        if r["high"] > r["low"]:
            ax.plot([r["low"], r["high"]], [y, y], color=colour, lw=3.2, solid_capstyle="round", alpha=0.45 if not filled else 0.9,
                    zorder=2)
        if r["point"] is not None or r["high"] == r["low"]:
            x = r["point"] if r["point"] is not None else r["low"]
            ax.plot(x, y, "o", ms=7.5, mfc=colour if filled else fs.SURFACE, mec=fs.SURFACE if filled else fs.INK2,
                    mew=1.6 if filled else 1.3, zorder=3)
    ax.set_yticks(ys, [r["label"] for r in order])
    ax.set_ylim(-0.7, max(ys) + 0.7)
    ax.set_xlim(1.0, 3.4)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    split = len(comp) - 0.5 + gap / 2
    ax.axhline(split, color=fs.AXIS, lw=0.6)
    for label, y in (("Geoscience", max(ys) + 0.55), ("Comparison", len(comp) - 1 + 0.55)):
        ax.annotate(label.upper(), (0, y), xycoords=("axes fraction", "data"), xytext=(-6, 0), textcoords="offset points",
                    ha="right", va="bottom", fontsize=6.8, color=fs.MUTED, fontweight="bold", annotation_clip=False)
    seen = []
    for v in VERDICT_STYLE.values():
        if v[2] not in [s[0] for s in seen]:
            seen.append((v[2], v[0], v[1]))
    fs.swatch_legend(ax, [(lab, col) for lab, col, _ in seen], marker="o", loc="upper right",
                     hollow=[lab for lab, _, filled in seen if not filled])
    fs.finish(fig, out, "fig1_power_law_exponents")


def fig_pdes(out, pdes):
    rows = [r for r in pdes["rows"] if r["value"] is not None]
    geo = [r for r in rows if "(comparison)" not in r["item"]]
    comp = [r for r in rows if "(comparison)" in r["item"]]
    order = sorted(geo, key=lambda r: -(r["value"] + r["ode_state_variables"])) + sorted(comp, key=lambda r: -r["value"])
    note = ("Sources: docs/complexity_2026-10-30/coupled_pdes.json, retrieved 2026-10-30. Count rule (README): balance laws as "
            "written in one cited source (earthquake-cycle rows use rate-and-state friction), vector equations expanded to scalar "
            "components in the stated dimensionality (label at bar end); '1D steady' rows are ordinary differential equations in "
            "one coordinate. Constitutive closures (friction law, Darcy, equations of state, rheology) are listed in the table but "
            "not counted. Light blue: the glacier-ocean composite sums two sources. Counts measure model size, not difficulty.")
    gap = 0.8
    ys = [len(order) - 1 - i + (gap if r in geo else 0) for i, r in enumerate(order)]
    fig, ax = fs.figure(7.8, 0.25 * (len(order) + gap) + 0.2, note, left=2.95, right=0.35)
    fs.header(fig, "Minimal coupled models need 1 to 17 balance equations; physics comparisons need 4 to 8",
              "Scalar balance equations, plus ODE state variables on the fault or bubble, counted by one rule")
    for r, y in zip(order, ys):
        pde, ode = r["balance_equations_scalar_3d"], r["ode_state_variables"]
        colour = fs.CONTEXT if r in comp else (fs.FOCUS if r["checked_in_text"] else fs.FOCUS_LIGHT)
        if ode:
            fs.hbar(ax, y, pde + ode, fs.SECOND, height=0.56)
            fs.hbar(ax, y, pde, colour, height=0.56, radius_pt=0)
            ax.plot([pde, pde], [y - 0.28, y + 0.28], color=fs.SURFACE, lw=1.6, zorder=2.6, solid_capstyle="butt")
        else:
            fs.hbar(ax, y, pde, colour, height=0.56)
        count = f"{pde}" + (f" + {ode}" if ode else "")
        fs.tip(ax, pde + ode, y, count, weight="bold")
        fs.tip(ax, pde + ode, y, r["dims_tag"], color=fs.MUTED, size=7, dx=10 + fs.text_width_pt(count))
    ax.set_yticks(ys, [PDE_LABELS[r["id"]] for r in order])
    ax.set_ylim(-0.7, max(ys) + 0.7); ax.set_xlim(0, 21)
    ax.xaxis.set_major_locator(fs.MaxNLocator(nbins=6, integer=True))
    ax.tick_params(axis="y", length=0); ax.grid(axis="y", visible=False); ax.spines["bottom"].set_visible(False)
    ax.axhline(len(comp) - 0.5 + gap / 2, color=fs.AXIS, lw=0.6)
    ax.annotate("PHYSICS COMPARISONS", (0, len(comp) - 1 + 0.55), xycoords=("axes fraction", "data"), xytext=(-6, 0),
                textcoords="offset points", ha="right", va="bottom", fontsize=6.8, color=fs.MUTED, fontweight="bold")
    fs.swatch_legend(ax, [("Scalar balance equations", fs.FOCUS), ("ODE state variables", fs.SECOND),
                          ("Comparison systems", fs.CONTEXT)], loc="lower right")
    fs.finish(fig, out, "fig2_coupled_pde_counts")


STATUS_STYLE = {"measured": (fs.FOCUS, "white"), "partial": (fs.FOCUS_LIGHT, fs.INK), "not found": (fs.SECOND, "white"),
                "not assessed": (fs.EMPTY, fs.MUTED)}


def profile_cells(profile, tables, pairs):
    """One record per cell: status, cited evidence and the short label drawn in figure 3."""
    rows = {r["id"]: r for payload in tables.values() for r in payload["rows"]}
    pairs = {p["row"]: p for p in pairs}
    cells = []
    for prow in profile["rows"]:
        for col in profile["columns"]:
            cell = prow[col["key"]]
            ev = cell["evidence"]
            label = ""
            if col["key"] == "ml_ready" and ev:
                shares = []
                for ref in ev:
                    pr = pairs[ref[5:]]
                    tag = ref[5:].split(": ")[1] + " " if ": " in ref and len(ev) > 1 else ""
                    if pr["share_percent"] is not None:
                        pct = pr["share_percent"]
                        shares.append(tag + ("below 0.001%" if pct < 0.001 else f"{pct:.2g}%"))
                    elif pr["packaged_bytes"] is None:
                        shares.append("no benchmark")
                    else:
                        shares.append("no archive size")
                label = "\n".join(shares)
            elif ev:
                sourced = [rows[i] for i in ev if any(rows[i][k] is not None for k in ("value", "value_min", "value_max"))]
                label = f"{len(sourced)} sourced row" + ("s" if len(sourced) != 1 else "")
            cells.append({"discipline": prow["discipline"], "column": col["label"], "status": cell["status"], "label": label,
                          "evidence": "; ".join(ev), "note": cell["note"]})
    return cells


def fig_profile(out, profile, cells):
    cols = [c["label"] for c in profile["columns"]]
    discs = [r["discipline"] for r in profile["rows"]]
    note = ("Sources: docs/complexity_2026-10-30/readiness_profile.json and the tables it cites; the ML-ready share is from "
            "docs/archive_readiness_2026-10-30 (archive pairs), retrieved 2026-10-30. Measured = a sourced value read in the "
            "source text for this discipline; partial = proxy, secondary, small-sample or qualitative evidence; not found = "
            "searched and absent; not assessed = not searched. Labels give the share or the number of sourced rows behind a cell; "
            "values are in readiness_profile.csv and the report.")
    fig, ax = fs.figure(8.4, 0.46 * len(discs), note, left=2.25, right=0.2, xband=0.45, top=fs.TITLE_BAND + 0.5)
    fs.header(fig, "AI-readiness profile by discipline",
              "Five separate measures per discipline, each with its own evidence; cells are never summed into a score")
    from matplotlib.patches import FancyBboxPatch
    for c in cells:
        x, y = cols.index(c["column"]), len(discs) - 1 - discs.index(c["discipline"])
        face, ink = STATUS_STYLE[c["status"]]
        ax.add_patch(FancyBboxPatch((x + 0.04, y + 0.08), 0.92, 0.84, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc=face, ec="none", mutation_aspect=1 / 2.2))
        ax.text(x + 0.5, y + 0.5, "\n".join(textwrap.fill(line, 14) for line in (c["label"] or c["status"]).splitlines()), ha="center", va="center", fontsize=7.2, color=ink,
                fontweight="bold" if c["status"] == "measured" and c["label"].endswith("%") else "normal")
    ax.set_xlim(0, len(cols)); ax.set_ylim(0, len(discs))
    ax.set_xticks([i + 0.5 for i in range(len(cols))], [textwrap.fill(c, 15) for c in cols], fontsize=8, color=fs.INK2)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.5 for i in range(len(discs))], discs[::-1])
    ax.tick_params(length=0); ax.grid(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    fs.swatch_legend(ax, [(k, STATUS_STYLE[k][0]) for k in profile["statuses"]], loc="upper left", anchor=(0.0, -0.02), ncol=4)
    fs.finish(fig, out, "fig3_readiness_profile")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=ROOT / "build" / "complexity")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    tables = ct.load()
    rows = pdf_exponent_rows(tables["power_laws.json"])
    with open(args.out / "power_law_pdf_exponents.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    fig_power_laws(args.out, rows)
    fig_pdes(args.out, tables["coupled_pdes.json"])
    profile = json.loads((ct.DOCS / "readiness_profile.json").read_text())
    errs = ct.validate_profile(profile, tables, [p[0] for p in arf.PAIRS])
    if errs:
        raise SystemExit("\n".join(errs))
    cells = profile_cells(profile, tables, arf.pairs_table())
    with open(args.out / "readiness_profile.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(cells[0]))
        writer.writeheader()
        writer.writerows(cells)
    fig_profile(args.out, profile, cells)
    print(f"Wrote figures to {args.out}")


if __name__ == "__main__":
    main()
