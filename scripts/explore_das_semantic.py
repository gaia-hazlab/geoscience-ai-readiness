"""Exploratory draft plots from the DAS semantic screen. Offline; no API calls.

Usage: python scripts/explore_das_semantic.py [REPO_ROOT]

Reads the frozen screen data/semantic_screen/das_topic_2026-10-29/screen_semantic.jsonl (copied from
the gitignored run by ai_readiness.semantic_screen collect) and the frozen keyword series in
legacy/community_demand/, and writes explore_1..4 PNG/SVG into build/das_semantic/.
Every figure is labeled as an unvalidated draft until the human validation set is coded.
"""
import csv, json, math, sys, textwrap
from collections import Counter, defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
SCREEN = ROOT / "data/semantic_screen/das_topic_2026-10-29/screen_semantic.jsonl"
OUT = ROOT / "build/das_semantic"
OUT.mkdir(parents=True, exist_ok=True)
YEARS = list(range(2020, 2026))
from figure_style import (OCEAN as S1, OCHRE as S2, MOSS as S3, GOLD as S4,
                          PLUM as S5, INK, MUTED as INK2, GRID, STONE as NEUTRAL,
                          apply_style, finish_figure)
NOTE = "Unvalidated draft: Claude Opus 5.5 labels from title and abstract (batch msgbatch_01HdBu5onQdhwxu6adW2ZjqL, codebook v0.1), OpenAlex DAS topic frame 2020-2025."

apply_style()

rows = [json.loads(l) for l in open(SCREEN)]
lab = [r for r in rows if r["status"] == "labeled"]
das = [r for r in lab if r["das_used"] == "yes"]


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def finish(fig, name, note=NOTE):
    finish_figure(fig, OUT, name, note)


# 1. keyword co-occurrence share vs semantic AI-as-method share
kw = {}
with open(ROOT / "legacy/community_demand/annual_title_abstract_article_review_counts.csv") as f:
    for r in csv.DictReader(f):
        kw.setdefault(r["query_id"], {})[int(r["year"])] = int(r["count"])
kw_share = {y: kw["das_ml_article_review"][y] / kw["das_article_review"][y] for y in YEARS}
sem = {}
for y in YEARS:
    g = [r for r in lab if r["year"] == y and r["ai_role"] != "unclear"]
    k = sum(r["ai_role"] == "ai_as_method" for r in g)
    sem[y] = (k, len(g))
fig, ax = plt.subplots(figsize=(6.4, 3.8))
fig.subplots_adjust(left=0.10, right=0.78, top=0.88, bottom=0.22)
ax.plot(YEARS, [100 * kw_share[y] for y in YEARS], color=S2, lw=2, marker="o", ms=5, label="Keyword co-occurrence")
ys = [100 * sem[y][0] / sem[y][1] for y in YEARS]
lo = [100 * wilson(*sem[y])[0] for y in YEARS]; hi = [100 * wilson(*sem[y])[1] for y in YEARS]
ax.fill_between(YEARS, lo, hi, color=S1, alpha=0.15, lw=0)
ax.plot(YEARS, ys, color=S1, lw=2, marker="o", ms=5, label="Semantic screen")
ax.text(2025.12, ys[-1], "Semantic screen:\nAI as a method", color=INK, fontsize=8, va="center")
ax.text(2025.12, 100 * kw_share[2025], "Keyword: 'machine\nlearning' or 'deep\nlearning' present", color=INK, fontsize=8, va="center")
ax.set_xlim(2019.6, 2025.1); ax.set_ylim(0, 40); ax.set_xticks(YEARS)
ax.set_ylabel("Percent of DAS papers")
ax.set_title("Two lenses on AI in DAS papers")
ax.legend(frameon=False, loc="upper left", fontsize=8)
finish(fig, "explore_1_keyword_vs_semantic",
       NOTE + "\nBoth series cover the DAS topic frame. Keyword: frozen 2026-10-21 snapshot, share of all DAS works. Semantic: share of labeled abstracts with a non-unclear AI role, including the few that do not analyze DAS. Band: Wilson 95% (label sampling only, not classifier error).")

# 2. how the screen labeled each year
cats = [("ai_as_method", "AI as method", S1), ("ai_as_subject", "AI as subject", S2), ("none", "No AI", S3)]
fig, ax = plt.subplots(figsize=(7.0, 3.8))
fig.subplots_adjust(left=0.10, right=0.72, top=0.88, bottom=0.17)
bottom = [0] * len(YEARS)
for key, name, color in cats:
    vals = [sum(r["year"] == y and r["ai_role"] == key for r in lab) for y in YEARS]
    ax.bar(YEARS, vals, bottom=bottom, color=color, width=0.62, edgecolor="white", linewidth=1, label=name)
    bottom = [b + v for b, v in zip(bottom, vals)]
rest = [sum(r["year"] == y for r in rows) - b for y, b in zip(YEARS, bottom)]
ax.bar(YEARS, rest, bottom=bottom, color=NEUTRAL, width=0.62, edgecolor="white", linewidth=1, label="No abstract or unclear")
for y, b, r in zip(YEARS, bottom, rest):
    ax.text(y, b + r + 4, str(b + r), ha="center", fontsize=8, color=INK)
ax.set_xticks(YEARS); ax.set_ylabel("Works in the DAS topic frame")
ax.set_title("Every DAS work, by the screen's AI label")
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8)
ax.grid(axis="x", visible=False)
finish(fig, "explore_2_ai_role_by_year")

# 3. AI method families among DAS papers using AI as a method (multi-label: lines, not stacks)
fams = [("deep_learning", "Deep learning", S1), ("classical_ml", "Classical ML", S2), ("generative_model", "Generative model", S3),
        ("uncertain", "ML, family not stated", S4), ("foundation_model", "Foundation model", S5)]
aim = [r for r in das if r["ai_role"] == "ai_as_method"]
fig, ax = plt.subplots(figsize=(6.4, 3.8))
fig.subplots_adjust(left=0.10, right=0.72, top=0.88, bottom=0.17)
ends = []
for key, name, color in fams:
    vals = [sum(r["year"] == y and key in r["ai_method_families"] for r in aim) for y in YEARS]
    ax.plot(YEARS, vals, color=color, lw=2, marker="o", ms=4.5, label=name)
    ends.append([vals[-1], f"{name} ({vals[-1]})"])
ends.sort()
for i in range(1, len(ends)):          # keep end labels at least 3.2 units apart
    ends[i][0] = max(ends[i][0], ends[i - 1][0] + 3.2)
for y, text in ends:
    ax.text(2025.12, y, text, color=INK, fontsize=8, va="center")
totals = [sum(r["year"] == y for r in aim) for y in YEARS]
ax.set_xlim(2019.6, 2025.1); ax.set_xticks(YEARS); ax.set_ylabel("DAS papers using AI as a method")
ax.set_title(f"Deep learning dominates the draft DAS screen (n = {sum(totals)} papers)")
ax.legend(frameon=False, loc="upper left", fontsize=8)
finish(fig, "explore_3_ai_method_families", NOTE + "\nOne paper can name several families; lines are not additive. Totals per year: "
       + ", ".join(f"{y}: {t}" for y, t in zip(YEARS, totals)) + ".")

# 4. what is measured alongside DAS
def other_group(note):
    n = (note or "").lower()
    if "temperature" in n or "dts" in n: return "Fiber temperature (DTS)"
    if "strain" in n or "brillouin" in n or "dss" in n: return "Fiber strain (Brillouin, DSS)"
    if any(w in n for w in ("pressure", "flow", "well", "production", "injection")): return "Well pressure, flow, injection"
    return "Other: logs, hydrophones, lab"
NAMES = {"geodetic_position_displacement": "Geodetic (GNSS, tilt)", "radar_backscatter_interferometry": "Radar, InSAR",
         "optical_reflectance": "Optical imagery", "thermal_radiance": "Thermal radiance", "atmospheric_in_situ": "Atmospheric in situ",
         "hydrologic_in_situ": "Hydrologic in situ", "oceanographic_in_situ": "Oceanographic in situ", "gravity_potential": "Gravity",
         "electromagnetic_electrical": "Electromagnetic", "geochemical_biological": "Geochemical, biological",
         "human_system_records": "Human-system records", "passive_microwave": "Passive microwave"}
co = Counter()
for r in das:
    for f in set(r["measurement_families"]) - {"seismic_elastic"}:
        co[other_group(r["other_family_note"]) if f == "other" else NAMES[f]] += 1
items = sorted(co.items(), key=lambda kv: kv[1])
items = [kv for kv in items if kv[1] >= 2]
fig, ax = plt.subplots(figsize=(6.6, 4.6))
fig.subplots_adjust(left=0.33, right=0.95, top=0.90, bottom=0.20)
ax.barh([k for k, _ in items], [v for _, v in items], color=S1, height=0.62)
for i, (_, v) in enumerate(items):
    ax.text(v + 0.8, i, str(v), va="center", fontsize=8, color=INK)
ax.set_xlabel("DAS-using papers that also use this measurement family")
ax.grid(axis="y", visible=False)
fig.suptitle(f"Measured alongside DAS, in {len(das):,} DAS-using papers", x=0.01, ha="left", fontsize=10, color=INK)
finish(fig, "explore_4_co_measured_families", NOTE + "\nFamilies from the protocol codebook; the 'other' family is split by a word rule on the model's note. Families seen once are left out.")
print(sorted(p.name for p in OUT.glob("explore_*.png")))
