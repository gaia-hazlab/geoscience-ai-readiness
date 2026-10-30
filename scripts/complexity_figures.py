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
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("complexity_tables", ROOT / "scripts" / "complexity_tables.py")
ct = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ct)
_spec = importlib.util.spec_from_file_location("archive_readiness_figures", ROOT / "scripts" / "archive_readiness_figures.py")
arf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(arf)

S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"   # reference palette slots 1-3 (dataviz skill), as in archive_readiness_figures.py
INK, INK2, GRID, NEUTRAL = "#0b0b0b", "#52514e", "#e4e3df", "#b9b8b2"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.axisbelow": True, "axes.titlelocation": "left", "axes.titlesize": 10})

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
VERDICT_STYLE = {  # verdict: (colour, filled, legend label)
    "tested, power law favored": (S3, True, "Tested: power law favored"),
    "tested, mixed": (S1, True, "Tested: mixed result"),
    "tested, alternative favored or not distinguishable": (S2, True, "Tested: alternative favored or equally good"),
    "not tested in this source": (NEUTRAL, False, "Not tested against alternatives"),
    "not stated": (NEUTRAL, False, "Not tested against alternatives"),
}


def finish(fig, out, name, note):
    width = int(fig.get_figwidth() * 17)
    fig.text(0.01, 0.01, "\n".join(textwrap.fill(p, width) for p in note.split("\n")), fontsize=6.5, color=INK2, va="bottom")
    for ext in ("png", "svg"):
        fig.savefig(out / f"{name}.{ext}", dpi=200)
    plt.close(fig)


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
    fig, ax = plt.subplots(figsize=(7.6, 6.0))
    fig.subplots_adjust(left=0.36, right=0.97, top=0.86, bottom=0.17)
    n = len(order)
    seen = set()
    for i, r in enumerate(order):
        y = n - 1 - i
        colour, filled, label = VERDICT_STYLE[r["verdict"]]
        if r["high"] > r["low"]:
            ax.plot([r["low"], r["high"]], [y, y], color=colour, lw=2.4, solid_capstyle="round")
        x = r["point"] if r["point"] is not None else (r["low"] + r["high"]) / 2
        if r["point"] is not None or r["high"] == r["low"]:
            ax.plot(x, y, "o", ms=6.5, mfc=colour if filled else "white", mec=colour if filled else INK2, mew=1.2,
                    label=None if label in seen else label)
        elif label not in seen:
            ax.plot([], [], "o", ms=6.5, mfc=colour if filled else "white", mec=colour if filled else INK2, label=label)
        seen.add(label)
    ax.axhline(len(comp) - 0.5, color=INK2, lw=0.8)
    ax.text(3.45, len(comp) - 0.35, "geoscience", ha="right", va="bottom", fontsize=7.5, color=INK2, style="italic")
    ax.text(3.45, len(comp) - 0.65, "comparison", ha="right", va="top", fontsize=7.5, color=INK2, style="italic")
    ax.set_yticks(range(n), [r["label"] for r in order][::-1])
    ax.set_xlim(1.0, 3.5)
    ax.set_xlabel("Density exponent alpha, p(x) ~ x^-alpha (as stated by each source)")
    ax.grid(axis="y", visible=False)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.32, 1.10), ncol=2, fontsize=7.5)
    fig.suptitle("Heavy tails are common; a pure power law rarely beats the alternatives", x=0.01, ha="left", fontsize=10, color=INK)
    finish(fig, out, "fig1_power_law_exponents",
           "Sources: docs/complexity_2026-10-30/power_laws.json (rows listed in power_law_pdf_exponents.csv), retrieved "
           "2026-10-30. Only exponents stated in the density convention are drawn; b-values, survivor-function exponents, "
           "Hack's law and fractal dimensions use other conventions and are left in the table, not converted. Bars are "
           "ranges stated by the source. Landslide exponents written with a minus sign by their sources are drawn by "
           "magnitude. 'Tested' means compared with lognormal, stretched exponential or truncated forms in that source.")


def fig_pdes(out, pdes):
    rows = [r for r in pdes["rows"] if r["value"] is not None]
    geo = [r for r in rows if "(comparison)" not in r["item"]]
    comp = [r for r in rows if "(comparison)" in r["item"]]
    order = sorted(geo, key=lambda r: r["value"] + r["ode_state_variables"]) + sorted(comp, key=lambda r: r["value"])
    fig, ax = plt.subplots(figsize=(8.4, 0.30 * len(order) + 2.0))
    fig.subplots_adjust(left=0.40, right=0.97, top=0.91, bottom=0.17)
    for i, r in enumerate(order[::-1]):
        pde, ode = r["balance_equations_scalar_3d"], r["ode_state_variables"]
        hatch = None if r["checked_in_text"] else "////"
        ax.barh(i, pde, color=S1 if r in geo else NEUTRAL, height=0.62, hatch=hatch, edgecolor="white", lw=0)
        if ode:
            ax.barh(i, ode, left=pde, color=S2, height=0.62)
        count = f"{pde}" + (f" + {ode}" if ode else "")
        ax.text(pde + ode + 0.2, i, f"{count}   {r['dims_tag']}", va="center", fontsize=7.5, color=INK)
    ax.set_yticks(range(len(order)), [PDE_LABELS[r["id"]] for r in order][::-1], fontsize=8)
    if comp:
        ax.axhline(len(comp) - 0.5, color=INK2, lw=0.8)
    ax.set_xlim(0, 24)
    ax.set_xlabel("Scalar balance equations + ODE state variables on fault or bubble (orange)")
    ax.grid(axis="y", visible=False)
    fig.suptitle("Minimal coupled models need 1 to 17 balance equations; the physics comparisons need 4 to 8",
                 x=0.01, ha="left", fontsize=10, color=INK)
    finish(fig, out, "fig2_coupled_pde_counts",
           "Sources: docs/complexity_2026-10-30/coupled_pdes.json, retrieved 2026-10-30. Count rule (README): balance laws as "
           "written in one cited source (earthquake-cycle rows use rate-and-state friction), vector equations expanded to scalar components in the stated dimensionality "
           "(label at bar end); '1D steady' rows are ordinary differential equations in one coordinate. Constitutive closures "
           "(friction law, Darcy, equations of state, rheology) are listed in the table but not counted. Hatched: the "
           "glacier-ocean composite sums two sources and was not read as one model. Counts measure model size, not difficulty.")


STATUS_STYLE = {"measured": (S1, "white"), "partial": ("#a8c8ee", INK), "not found": (S2, "white"), "not assessed": (GRID, INK2)}


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
                label = ", ".join(shares)
            elif ev:
                sourced = [rows[i] for i in ev if any(rows[i][k] is not None for k in ("value", "value_min", "value_max"))]
                label = f"{len(sourced)} sourced row" + ("s" if len(sourced) != 1 else "")
            cells.append({"discipline": prow["discipline"], "column": col["label"], "status": cell["status"], "label": label,
                          "evidence": "; ".join(ev), "note": cell["note"]})
    return cells


def fig_profile(out, profile, cells):
    cols = [c["label"] for c in profile["columns"]]
    discs = [r["discipline"] for r in profile["rows"]]
    fig, ax = plt.subplots(figsize=(9.0, 0.48 * len(discs) + 2.3))
    fig.subplots_adjust(left=0.24, right=0.99, top=0.80, bottom=0.17)
    for c in cells:
        x, y = cols.index(c["column"]), len(discs) - 1 - discs.index(c["discipline"])
        face, ink = STATUS_STYLE[c["status"]]
        ax.add_patch(plt.Rectangle((x + 0.03, y + 0.06), 0.94, 0.88, color=face, lw=0))
        ax.text(x + 0.5, y + 0.5, c["label"] or c["status"], ha="center", va="center", fontsize=7.2, color=ink,
                style="italic" if not c["label"] else "normal")
    ax.set_xlim(0, len(cols)); ax.set_ylim(0, len(discs))
    ax.set_xticks([i + 0.5 for i in range(len(cols))], [textwrap.fill(c, 16) for c in cols], fontsize=8)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.5 for i in range(len(discs))], discs[::-1], fontsize=8)
    ax.tick_params(length=0)
    ax.grid(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=STATUS_STYLE[k][0]) for k in profile["statuses"]]
    ax.legend(handles, profile["statuses"], frameon=False, ncol=4, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.01))
    fig.suptitle("AI-readiness profile by discipline: each column is a separate measure, never summed", x=0.01, ha="left",
                 fontsize=10, color=INK)
    finish(fig, out, "fig3_readiness_profile",
           "Sources: docs/complexity_2026-10-30/readiness_profile.json and the tables it cites; the ML-ready share is from "
           "docs/archive_readiness_2026-10-30 (archive pairs), retrieved 2026-10-30. Status rule in readiness_profile.json: measured = "
           "a sourced value read in the source text for this discipline; partial = proxy, secondary, small-sample or qualitative "
           "evidence; not found = searched and absent; not assessed = not searched. Cell labels give the share or the count of "
           "sourced rows behind the cell; values are in readiness_profile.csv and the report.")


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
