"""Reproduce the proposal's frozen OpenAlex DAS activity figure, offline.

The counts describe indexed articles/reviews mentioning DAS. They do not measure
multimodal research, AI use, dataset reuse, or community demand. A raw-data digest
failure or an incomplete year series is an error, never an implicit zero.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

YEARS = tuple(range(2020, 2026))
SNAPSHOT_DATE = "2026-10-21"
NUMERATOR_FILE = "das_article_review.json"
DENOMINATOR_FILE = "all_article_review.json"
BASENAME = "DAS_Publication_Activity_2026-10-23_v2"
SOURCE_QUERY = (
    "https://api.openalex.org/works?filter="
    "from_publication_date%3A2020-01-01%2Cto_publication_date%3A2025-12-31"
    "%2Ctype%3Aarticle%7Creview%2Ctitle_and_abstract.search%3A%22distributed"
    "+acoustic+sensing%22&group_by=publication_year&per_page=200"
)
CAPTION = (
    "Figure 2. DAS publication activity, 2020–2025 (OpenAlex, 2026; snapshot "
    "October 21). Left: articles/reviews mentioning distributed acoustic sensing "
    "in indexed titles/abstracts. Right: the same counts per 100,000 indexed "
    "articles/reviews worldwide. Search and index coverage affect both panels. "
    "These are research-activity counts, not measures of multimodal AI use, "
    "dataset reuse or expressed demand."
)


def _counts(payload: object, filename: str) -> dict[int, int]:
    """Validate an annual grouped OpenAlex response without imputing years."""
    if not isinstance(payload, dict) or not isinstance(payload.get("group_by"), list):
        raise ValueError(f"{filename}: expected a group_by list")
    counts: dict[int, int] = {}
    for group in payload["group_by"]:
        if not isinstance(group, dict):
            raise ValueError(f"{filename}: invalid annual group")
        key = group.get("key")
        if not isinstance(key, str) or key not in {str(y) for y in YEARS}:
            raise ValueError(f"{filename}: unexpected year {key!r}")
        year = int(key)
        if year in counts:
            raise ValueError(f"{filename}: duplicate year {year}")
        count = group.get("count")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"{filename}: invalid count for {year}")
        counts[year] = count
    if set(counts) != set(YEARS):
        missing = sorted(set(YEARS) - set(counts))
        raise ValueError(f"{filename}: missing years {missing}")
    return counts


def load_snapshot(snapshot_dir: str | Path) -> dict:
    """Check both file hashes and derive the plotted series from raw responses.

    ``manifest.json`` has a ``files`` mapping from each raw basename to its SHA256
    digest (or to a record containing ``sha256``). No path in the manifest is
    followed. The snapshot is deliberately not refreshed from the network.
    """
    snapshot_dir = Path(snapshot_dir)
    manifest = json.loads((snapshot_dir / "manifest.json").read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("manifest.json: expected files mapping")
    series = {}
    digests = {}
    for filename in (NUMERATOR_FILE, DENOMINATOR_FILE):
        expected = files.get(filename)
        if isinstance(expected, dict):
            expected = expected.get("sha256")
        if (not isinstance(expected, str) or len(expected) != 64
                or any(c not in "0123456789abcdefABCDEF" for c in expected)):
            raise ValueError(f"manifest.json: missing or invalid SHA256 for {filename}")
        raw = (snapshot_dir / filename).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected.lower():
            raise ValueError(f"SHA256 mismatch for {filename}")
        digests[filename] = digest
        series[filename] = _counts(json.loads(raw), filename)

    numerator = series[NUMERATOR_FILE]
    denominator = series[DENOMINATOR_FILE]
    rows = []
    for year in YEARS:
        n, d = numerator[year], denominator[year]
        if d <= 0:
            raise ValueError(f"{DENOMINATOR_FILE}: denominator must be positive for {year}")
        if n > d:
            raise ValueError(f"DAS count exceeds worldwide denominator for {year}")
        rows.append({
            "year": year,
            "das_articles_reviews": n,
            "all_indexed_articles_reviews_worldwide": d,
            "das_per_100000_worldwide": 100000 * n / d,
        })
    if numerator[YEARS[0]] <= 0:
        raise ValueError("2020 DAS count must be positive to calculate growth ratios")
    return {
        "snapshot_date": SNAPSHOT_DATE,
        "raw_sha256": digests,
        "rows": rows,
        "ratio_counts_2025_over_2020": numerator[2025] / numerator[2020],
        "ratio_normalized_2025_over_2020": (
            rows[-1]["das_per_100000_worldwide"]
            / rows[0]["das_per_100000_worldwide"]
        ),
    }


def build(output_dir: str | Path, snapshot_dir: str | Path) -> dict:
    """Render the redesigned figure using the same frozen, hash-checked data."""
    summary = load_snapshot(snapshot_dir)
    rows = summary["rows"]
    if (any(r["das_articles_reviews"] > 500 for r in rows)
            or any(r["das_per_100000_worldwide"] > 6.5 for r in rows)):
        raise ValueError("Series exceeds the figure axes; revise the plot explicitly")
    from reportlab.graphics import renderPDF, renderSVG
    from reportlab.graphics.shapes import Drawing, String, Rect, Line, PolyLine, Circle
    from reportlab.lib.colors import HexColor
    from .rendering import render_png

    ink = HexColor('#18242F')
    muted = HexColor('#52616D')
    grid = HexColor('#DDE4E9')
    blue = HexColor('#0072B2')
    teal = HexColor('#007E73')
    drawing = Drawing(468, 194.4)
    drawing.add(Rect(0, 0, 468, 194.4, fillColor=HexColor('#FFFFFF'), strokeColor=None))

    def text(x, y, value, size=8.5, bold=False, color=ink, anchor='start'):
        drawing.add(String(x, y, value, fontName='Helvetica-Bold' if bold else 'Helvetica',
                           fontSize=size, fillColor=color, textAnchor=anchor))

    text(0, 182, 'DAS publication activity, 2020-2025', 12.5, True)
    text(0, 168, 'Title/abstract matches for distributed acoustic sensing | OpenAlex snapshot: 21 Oct 2026',
         8.4, color=muted)
    text(0, 149, 'A   Annual DAS publications', 10, True)
    text(248, 149, 'B   Worldwide-normalized activity', 10, True)
    text(0, 136, 'Articles and reviews', 8.4, color=muted)
    text(248, 136, 'DAS per 100,000 indexed articles/reviews', 8.4, color=muted)

    y0, height = 44, 82
    for x0, color, metric, maximum, ticks, mode, ratio in [
        (32, blue, 'das_articles_reviews', 500, (0, 100, 200, 300, 400, 500), 'bar',
         summary['ratio_counts_2025_over_2020']),
        (278, teal, 'das_per_100000_worldwide', 6.5, (0, 2, 4, 6), 'line',
         summary['ratio_normalized_2025_over_2020']),
    ]:
        width = 182
        xs = [x0 + 10 + i * (width - 20) / 5 for i in range(6)]
        for tick in ticks:
            y = y0 + tick / maximum * height
            drawing.add(Line(x0, y, x0 + width, y, strokeColor=grid, strokeWidth=.45))
            text(x0 - 6, y - 2.8, str(tick), 8.2, color=muted, anchor='end')
        drawing.add(Line(x0, y0, x0 + width, y0, strokeColor=ink, strokeWidth=.65))
        points = []
        for row, x in zip(rows, xs):
            value = row[metric]
            y = y0 + value / maximum * height
            drawing.add(Line(x, y0, x, y0 - 3, strokeColor=ink, strokeWidth=.55))
            text(x, y0 - 14, str(row['year']), 8.5, color=muted, anchor='middle')
            if mode == 'bar':
                drawing.add(Rect(x - 7, y0, 14, y - y0, fillColor=color, strokeColor=None))
                label = str(value)
            else:
                points.append((x, y))
                label = f'{value:.2f}'
            text(x, y + 7, label, 8.7, bold=(row['year'] == 2025), color=ink, anchor='middle')
        if mode == 'line':
            drawing.add(PolyLine([v for pair in points for v in pair], strokeColor=color,
                                 strokeWidth=1.8, fillColor=None))
            for x, y in points:
                drawing.add(Circle(x, y, 2.4, fillColor=color, strokeColor=None))
        text(x0 + 13, 113, f'{ratio:.2f}x from 2020', 8.8, True, color)

    text(234, 9, 'Indexed publication activity; does not measure AI use, dataset reuse, or demand.',
         7.9, color=muted, anchor='middle')

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {ext: f'{BASENAME}.{ext}' for ext in ('svg', 'pdf', 'png')}
    outputs.update(csv=f'{BASENAME}_Data.csv', caption=f'{BASENAME}_Caption.txt',
                   provenance=f'{BASENAME}_Provenance.json')
    renderSVG.drawToFile(drawing, str(output_dir / outputs['svg']))
    renderPDF.drawToFile(drawing, str(output_dir / outputs['pdf']))
    render_png(output_dir / outputs['pdf'], output_dir / outputs['png'], dpi=300)
    with (output_dir / outputs['csv']).open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    caption = (
        'DAS publication activity, 2020-2025. (A) Annual OpenAlex article/review '
        'counts for a title/abstract search of distributed acoustic sensing. '
        '(B) The same counts per 100,000 indexed articles/reviews worldwide in '
        'each year. Values are from the frozen October 21, 2026 snapshot; the '
        '2025/2020 ratios are 3.59 for counts and 3.22 for normalized activity. '
        'Search and index coverage affect both panels. These are research-activity '
        'counts, not measures of multimodal AI use, dataset reuse or expressed demand.'
    )
    (output_dir / outputs['caption']).write_text(caption + '\n\nSource query: ' + SOURCE_QUERY + '\n',
                                                    encoding='utf-8')
    provenance = {
        **summary, 'artwork_date': '2026-10-23', 'artwork_version': '0.2.0',
        'source_files': [NUMERATOR_FILE, DENOMINATOR_FILE], 'source_query': SOURCE_QUERY,
        'interpretation': 'Indexed activity across all fields; not a geoscience-wide adoption statistic.',
        'uncertainty': 'Database/search coverage uncertainty remains unquantified. No sampling confidence intervals are invented.',
        'not_measured': ['actual AI use', 'number of modalities used', 'joint multimodal training',
                         'independent dataset reuse', 'expressed demand'],
        'design_changes': ['Absolute counts shown as bars; normalized values as a line.',
                           'Compact shared title, explicit units, direct numeric labels and zero baselines.',
                           'Original frozen data and normalization retained.'],
        'caption': caption, 'outputs': outputs,
    }
    (output_dir / outputs['provenance']).write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    return {'outputs': outputs, 'summary': summary}

