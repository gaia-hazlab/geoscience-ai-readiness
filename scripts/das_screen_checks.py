#!/usr/bin/env python3
"""Checks on the DAS semantic screen that need no human coder. None of them validates the labels.

Usage: python scripts/das_screen_checks.py [--first runs/das_topic_2026-10-29] [--retest runs/das_retest_2026-11-06/semantic]
                                           [--reharvest runs/das_topic_2026-11-06] [--out docs/das_screen_checks_2026-11-06]

Reads the gitignored run folders (abstracts stay there) and writes counts only, with no abstract text:
  checks.json  per-year keyword counts on the population the screen labeled, keyword-by-label cross-tabulation,
               bounds on the AI-as-method share when unknown works are counted both ways, test-retest agreement
               between two batches of the same model and prompt, and frame drift between two harvests.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YEARS = list(range(2020, 2026))
KEYWORD = re.compile(r"machine[- ]learning|deep[- ]learning|neural[- ]network", re.I)


def jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]


def abstract_text(index):
    """Rebuild an abstract from the OpenAlex inverted index."""
    if not index:
        return ""
    words = sorted((position, word) for word, positions in index.items() for position in positions)
    return " ".join(word for _, word in words)


def cohen_kappa(a, b):
    n = len(a)
    if not n:
        return None
    observed = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    expected = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if expected == 1 else (observed - expected) / (1 - expected)


def share_bounds(rows):
    """Bounds on the AI-as-method share among DAS-using works, counting every unknown work as no and then as yes.

    Unknown = in the frame, not labeled das_used no, and not both das_used yes with a known AI role.
    """
    known = [r for r in rows if r["das_used"] == "yes" and r["ai_role"] != "unclear"]
    excluded = sum(r["das_used"] == "no" for r in rows)
    unknown = len(rows) - excluded - len(known)
    k = sum(r["ai_role"] == "ai_as_method" for r in known)
    n = len(known) + unknown
    return {"works": len(rows), "das_used_no": excluded, "known": len(known), "unknown": unknown, "ai_as_method": k,
            "point_percent": 100 * k / len(known) if known else None,
            "lower_percent": 100 * k / n if n else None, "upper_percent": 100 * (k + unknown) / n if n else None}


def keyword_crosstab(works, screen):
    text = {w["id"]: f'{w.get("title") or ""} {abstract_text(w.get("abstract_inverted_index"))}' for w in works}
    out = []
    for year in YEARS:
        labeled = [r for r in screen if r["year"] == year and r["status"] == "labeled" and r["ai_role"] != "unclear"]
        group = [r for r in labeled if r["paper_id"] in text]
        tab = Counter()
        for r in group:
            tab[(bool(KEYWORD.search(text[r["paper_id"]])), r["ai_role"] == "ai_as_method")] += 1
        n = len(group)
        out.append({"year": year, "population": n, "screen_rows_without_text": len(labeled) - n, "keyword": tab[(True, True)] + tab[(True, False)], "screen_ai_as_method": tab[(True, True)] + tab[(False, True)],
                    "both": tab[(True, True)], "keyword_only": tab[(True, False)], "screen_only": tab[(False, True)], "neither": tab[(False, False)],
                    "keyword_percent": 100 * (tab[(True, True)] + tab[(True, False)]) / n if n else None,
                    "screen_percent": 100 * (tab[(True, True)] + tab[(False, True)]) / n if n else None})
    return out


def retest(first, second):
    a, b = {r["paper_id"]: r for r in first}, {r["paper_id"]: r for r in second}
    both = [p for p in a if p in b and a[p]["status"] == "labeled" and b[p]["status"] == "labeled"]
    result = {"papers_compared": len(both)}
    for field in ("ai_role", "das_used"):
        x, y = [a[p][field] for p in both], [b[p][field] for p in both]
        result[field] = {"agree": sum(i == j for i, j in zip(x, y)), "percent_agree": 100 * sum(i == j for i, j in zip(x, y)) / len(both) if both else None,
                         "cohen_kappa": cohen_kappa(x, y)}
    method = lambda r: r["ai_role"] == "ai_as_method"
    result["ai_as_method_flips"] = sum(method(a[p]) != method(b[p]) for p in both)
    result["by_year"] = []
    for year in YEARS:
        row = {"year": year}
        for name, rows in (("first", first), ("second", second)):
            row[name] = share_bounds([r for r in rows if r["year"] == year])
        result["by_year"].append(row)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--first", default=str(ROOT / "runs/das_topic_2026-10-29"))
    parser.add_argument("--retest", default=str(ROOT / "runs/das_retest_2026-11-06/semantic"))
    parser.add_argument("--reharvest", default=str(ROOT / "runs/das_topic_2026-11-06"))
    parser.add_argument("--out", default=str(ROOT / "docs/das_screen_checks_2026-11-06"))
    args = parser.parse_args(argv)
    first_dir, retest_dir, reharvest = Path(args.first), Path(args.retest), Path(args.reharvest)
    works = jsonl(first_dir / "works.jsonl")
    screen = jsonl(first_dir / "semantic/screen_semantic.jsonl")
    second = jsonl(retest_dir / "screen_semantic.jsonl")
    new_works = jsonl(reharvest / "works.jsonl")
    old_ids, new_ids = {w["id"] for w in works}, {w["id"] for w in new_works}
    removed = old_ids - new_ids
    first_manifest = json.loads((first_dir / "semantic/collect_manifest.json").read_text())
    second_manifest = json.loads((retest_dir / "collect_manifest.json").read_text())
    report = {
        "status": "No check here is a validation. Human coding of the 130-abstract sample remains undone.",
        "keyword_definition": KEYWORD.pattern,
        "first_batch": {k: first_manifest.get(k) for k in ("batch_id", "usd_total", "model", "prompt_sha256", "screen_semantic_sha256")},
        "second_batch": {k: second_manifest.get(k) for k in ("batch_id", "usd_total", "model", "prompt_sha256", "screen_semantic_sha256")},
        "keyword_crosstab": keyword_crosstab(works, screen),
        "bounds": [{"year": y, **share_bounds([r for r in screen if r["year"] == y])} for y in YEARS],
        "retest": retest(screen, second),
        "frame_drift": {"first_harvest": "2026-10-29", "second_harvest": "2026-11-06", "first_works": len(old_ids), "second_works": len(new_ids),
                        "added": len(new_ids - old_ids), "removed": len(removed),
                        "removed_by_year": dict(sorted(Counter(w["publication_year"] for w in works if w["id"] in removed).items())),
                        "second_by_year": dict(sorted(Counter(w["publication_year"] for w in new_works).items()))},
        "duplicate_doi_note": "OpenAlex lists W4281491833 and W4291158743 under one DOI (10.1029/2022gl098727). The harvester merges them, so 2022 has 193 works against an OpenAlex count of 194.",
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "checks.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({k: report[k] for k in ("frame_drift",)}, indent=1))
    print({k: v for k, v in report["retest"].items() if k != "by_year"})
    for row in report["bounds"]:
        print(row["year"], {k: (round(v, 1) if isinstance(v, float) else v) for k, v in row.items() if k != "year"})
    for row in report["keyword_crosstab"]:
        print({k: (round(v, 1) if isinstance(v, float) else v) for k, v in row.items()})
    for row in report["retest"]["by_year"]:
        print(row["year"], round(row["first"]["point_percent"], 1), round(row["second"]["point_percent"], 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
