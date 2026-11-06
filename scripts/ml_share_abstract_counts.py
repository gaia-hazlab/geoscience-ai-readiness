#!/usr/bin/env python3
"""ML mention rate with a matching denominator: only OpenAlex articles that have an abstract.

Usage: python scripts/ml_share_abstract_counts.py --out runs/ml_share_abstract_<date> [--publish]

The original rate (platform_counts.json) divides title-or-abstract ML matches by all articles, including
articles with no abstract to search. The share of articles with an abstract differs between fields, so that
denominator does not match the numerator. This script requests numerator and denominator together in one run,
both filtered to has_abstract:true. Read-only, no key. --publish copies the counts to docs/archive_readiness_2026-10-30/.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("platform_readiness_counts", ROOT / "scripts/platform_readiness_counts.py")
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)


def collect(c):
    base = f"from_publication_date:{pc.YEARS[0]}-01-01,to_publication_date:{pc.YEARS[-1]}-12-31,type:article,has_abstract:true"
    recent = "from_publication_date:2023-01-01,to_publication_date:2025-12-31,type:article,has_abstract:true"
    fields = "|".join(pc.OPENALEX_FIELDS.values())
    earth = f"primary_topic.field.id:{fields}"
    ml = f"title_and_abstract.search:{pc.ML}"
    return {
        "works_all_by_year": pc.openalex(c, "abs_all", base, "publication_year"),
        "works_earth_env_by_year": pc.openalex(c, "abs_earth", f"{base},{earth}", "publication_year"),
        "ml_works_all_by_year": pc.openalex(c, "abs_ml_all", f"{base},{ml}", "publication_year"),
        "ml_works_earth_env_by_year": pc.openalex(c, "abs_ml_earth", f"{base},{earth},{ml}", "publication_year"),
        "subfield_works_2023_2025": pc.openalex(c, "abs_sub", f"{recent},{earth}", "primary_topic.subfield.id"),
        "subfield_ml_works_2023_2025": pc.openalex(c, "abs_sub_ml", f"{recent},{earth},{ml}", "primary_topic.subfield.id"),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args(argv)
    out = Path(args.out)
    c = pc.Collector(out)
    now = datetime.now(timezone.utc)
    result = {"retrieved_utc": now.isoformat(timespec="seconds"), "filter": "type:article,has_abstract:true", "ml_query": pc.ML,
              "openalex": collect(c)}
    (out / "counts.json").write_text(json.dumps(result, indent=1) + "\n")
    (out / "receipts.json").write_text(json.dumps(c.receipts, indent=1) + "\n")
    if args.publish:
        name = f"ml_share_abstract_{now:%Y-%m-%d}"
        docs = ROOT / "docs/archive_readiness_2026-10-30"
        (docs / f"{name}.json").write_text(json.dumps(result, indent=1) + "\n")
        (docs / f"{name}_receipts.json").write_text(json.dumps(c.receipts, indent=1) + "\n")
    print(f"{len(c.receipts)} requests; counts in {out / 'counts.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
