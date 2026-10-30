"""Exploratory draft plots from the DAS semantic screen. Offline; no API calls.

Usage: python scripts/explore_das_semantic.py [REPO_ROOT]

Reads the frozen screen data/semantic_screen/das_topic_2026-10-29/screen_semantic.jsonl (copied from
the gitignored run by ai_readiness.semantic_screen collect) and the frozen keyword series in
legacy/community_demand/, and writes explore_1..4 PNG/SVG into build/das_semantic/.
Every figure is labeled as an unvalidated draft until the human validation set is coded.
"""
import csv, json, math, sys
from collections import Counter
from pathlib import Path
import matplotlib.ticker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figure_style as fs   # noqa: E402  shared look of every report figure

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
SCREEN = ROOT / "data/semantic_screen/das_topic_2026-10-29/screen_semantic.jsonl"
OUT = ROOT / "build/das_semantic"
OUT.mkdir(parents=True, exist_ok=True)
YEARS = list(range(2020, 2026))
# reference palette slots 4 and 5 (dataviz skill references/palette.md) for the five-family figure only
S1, S2, S3, S4, S5 = fs.FOCUS, fs.SECOND, fs.THIRD, "#eda100", "#e87ba4"
NOTE = "Unvalidated draft: Claude Opus 5.5 labels from title and abstract (batch msgbatch_01HdBu5onQdhwxu6adW2ZjqL, codebook v0.1), OpenAlex DAS topic frame 2020-2025."


rows = [json.loads(l) for l in open(SCREEN)]
lab = [r for r in rows if r["status"] == "labeled"]
das = [r for r in lab if r["das_used"] == "yes"]


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def finish(fig, name):
    fs.finish(fig, OUT, name)


def pct_axis(ax):
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))


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
note1 = (NOTE + "\nBoth series cover the DAS topic frame. Keyword: frozen 2026-10-21 snapshot, share of all DAS works. Semantic: "
         "share of labeled abstracts with a non-unclear AI role, including the few that do not analyze DAS. Band: Wilson 95% "
         "(label sampling only, not classifier error).")
fig, ax = fs.figure(7.2, 2.8, note1, left=0.6, right=2.1)
fs.header(fig, "Keyword counts understate AI use in DAS papers",
          "Share of distributed acoustic sensing (DAS) papers using AI, by year: keyword match against the semantic screen")
kys = [100 * kw_share[y] for y in YEARS]
ys = [100 * sem[y][0] / sem[y][1] for y in YEARS]
lo = [100 * wilson(*sem[y])[0] for y in YEARS]; hi = [100 * wilson(*sem[y])[1] for y in YEARS]
ax.fill_between(YEARS, lo, hi, color=fs.FOCUS, alpha=0.10, lw=0)
fs.series(ax, YEARS, kys, fs.CONTEXT, "Keyword co-occurrence")
fs.series(ax, YEARS, ys, fs.FOCUS, "Semantic screen")
fs.tip(ax, 2025, ys[-1], f"Semantic screen, AI as a method  {ys[-1]:.0f}%", dx=8)
fs.tip(ax, 2025, kys[-1], f"Keyword 'machine learning' or\n'deep learning' present  {kys[-1]:.0f}%", dx=8, color=fs.INK2)
ax.set_xlim(2019.7, 2025.3); ax.set_ylim(0, 35); ax.set_xticks(YEARS)
pct_axis(ax); ax.grid(axis="x", visible=False); ax.spines["left"].set_visible(False)
fs.swatch_legend(ax, [("Semantic screen (band: Wilson 95%)", fs.FOCUS), ("Keyword co-occurrence", fs.CONTEXT)],
                 loc="upper left", marker="line")
finish(fig, "explore_1_keyword_vs_semantic")

# 2. how the screen labeled each year
cats = [("ai_as_method", "AI as method", S1), ("ai_as_subject", "AI as subject", S2), ("none", "No AI", S3)]
fig, ax = fs.figure(7.2, 2.8, NOTE, left=0.6, right=2.0)
fs.header(fig, "Every DAS work, by the screen's AI label", "Works in the DAS topic frame per year, stacked by AI role")
bottom = [0] * len(YEARS)
for key, name, color in cats:
    vals = [sum(r["year"] == y and r["ai_role"] == key for r in lab) for y in YEARS]
    ax.bar(YEARS, vals, bottom=bottom, color=color, width=0.56, edgecolor=fs.SURFACE, linewidth=1.4, label=name, zorder=2.5)
    bottom = [b + v for b, v in zip(bottom, vals)]
rest = [sum(r["year"] == y for r in rows) - b for y, b in zip(YEARS, bottom)]
ax.bar(YEARS, rest, bottom=bottom, color=fs.CONTEXT, width=0.56, edgecolor=fs.SURFACE, linewidth=1.4, label="No abstract or unclear", zorder=2.5)
for y, b, r in zip(YEARS, bottom, rest):
    ax.annotate(str(b + r), (y, b + r), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=7.5, color=fs.INK)
ax.set_xticks(YEARS); ax.grid(axis="x", visible=False); ax.spines["left"].set_visible(False)
fs.swatch_legend(ax, [(n, c) for _, n, c in cats] + [("No abstract or unclear", fs.CONTEXT)], loc="upper left", anchor=(1.01, 1.0))
finish(fig, "explore_2_ai_role_by_year")

# 3. AI method families among DAS papers using AI as a method (multi-label: lines, not stacks)
fams = [("deep_learning", "Deep learning", S1), ("classical_ml", "Classical ML", S2), ("generative_model", "Generative model", S3),
        ("uncertain", "ML, family not stated", S4), ("foundation_model", "Foundation model", S5)]
aim = [r for r in das if r["ai_role"] == "ai_as_method"]
totals = [sum(r["year"] == y for r in aim) for y in YEARS]
note3 = NOTE + "\nOne paper can name several families; lines are not additive. Totals per year: " + ", ".join(
    f"{y}: {t}" for y, t in zip(YEARS, totals)) + "."
fig, ax = fs.figure(7.2, 2.8, note3, left=0.6, right=2.0)
fs.header(fig, f"Deep learning carries DAS AI adoption (n = {sum(totals)} papers)",
          "DAS papers using AI as a method, by AI method family named in the abstract")
ends = []
for key, name, color in fams:
    vals = [sum(r["year"] == y and key in r["ai_method_families"] for r in aim) for y in YEARS]
    fs.series(ax, YEARS, vals, color, name)
    ends.append([vals[-1], vals[-1], f"{name}  {vals[-1]}"])
ends.sort()
for i in range(1, len(ends)):          # keep end labels at least 3.2 units apart
    ends[i][0] = max(ends[i][0], ends[i - 1][0] + 3.2)
for y_text, y_end, text in ends:
    ax.annotate(text, (2025, y_end), xytext=(2025.25, y_text), textcoords="data", va="center", fontsize=7.5, color=fs.INK,
                annotation_clip=False, arrowprops=dict(arrowstyle="-", color=fs.AXIS, lw=0.6) if abs(y_text - y_end) > 0.5 else None)
ax.set_xlim(2019.7, 2025.1); ax.set_xticks(YEARS); ax.grid(axis="x", visible=False); ax.spines["left"].set_visible(False)
fs.swatch_legend(ax, [(n, c) for _, n, c in fams], loc="upper left", marker="line")
finish(fig, "explore_3_ai_method_families")

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
note4 = NOTE + "\nFamilies from the protocol codebook; the 'other' family is split by a word rule on the model's note. Families seen once are left out."
items = items[::-1]
fig, ax = fs.figure(7.2, 0.27 * len(items), note4, left=2.25, right=0.4)
fs.header(fig, "What is measured alongside DAS", f"DAS-using papers that also use each measurement family, of {len(das):,} DAS-using papers")
fs.bar_axes(ax, [k for k, _ in items])
for i, (_, v) in enumerate(items):
    y = len(items) - 1 - i
    fs.hbar(ax, y, v, fs.FOCUS)
    fs.tip(ax, v, y, str(v))
ax.set_xlim(0, items[0][1] * 1.12)
finish(fig, "explore_4_co_measured_families")
print(sorted(p.name for p in OUT.glob("explore_*.png")))
