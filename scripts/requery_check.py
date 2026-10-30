#!/usr/bin/env python3
"""Reproducibility check: re-query the live sources and compare with the frozen snapshots.

Usage:
  python scripts/requery_check.py --offline                      # verify frozen-file hashes only, no network
  python scripts/requery_check.py --out runs/requery_<date>      # live: DAS series + OpenAlex + simulation + DataCite
  python scripts/requery_check.py --out runs/requery_<date> --with-hf   # also Hugging Face (about 80 requests)

Live mode never uses keys. It re-runs the same query builders as scripts/platform_readiness_counts.py,
re-queries the DAS title/abstract counts per year that feed Fig. 2B, and writes:
  OUT/counts.json, OUT/receipts.json   the new live responses (same format as the frozen snapshot)
  OUT/comparison.json, OUT/comparison.md   every frozen number beside its new value and the relative change

Bibliographic and repository indexes change daily, so differences are expected. The check reports them;
it fails only when a query errors or a frozen file's hash no longer matches its manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
FROZEN_COUNTS = ROOT / "docs/archive_readiness_2026-10-30/platform_counts.json"
FROZEN_SIM = ROOT / "docs/archive_readiness_2026-10-30/simulation_counts.json"
DAS_SNAPSHOT = ROOT / "data/openalex/2026-10-21/das_article_review.json"
DAS_MANIFEST = ROOT / "data/openalex/2026-10-21/manifest.json"
SCREEN_MANIFEST = ROOT / "data/semantic_screen/das_topic_2026-10-29/MANIFEST.json"
DAS_FILTER = ('from_publication_date:2020-01-01,to_publication_date:2025-12-31,type:article|review,'
              'title_and_abstract.search:"distributed acoustic sensing"')


def load_collector():
    spec = importlib.util.spec_from_file_location("platform_readiness_counts", ROOT / "scripts/platform_readiness_counts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flatten(value, prefix=""):
    """Numeric leaves keyed by path; lists (top-download tables) are skipped."""
    out = {}
    if isinstance(value, dict):
        for key, item in value.items():
            out.update(flatten(item, f"{prefix}/{key}" if prefix else str(key)))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        out[prefix] = value
    return out


def compare(frozen, live):
    a, b = flatten(frozen), flatten(live)
    rows = []
    for key in sorted(set(a) | set(b)):
        old, new = a.get(key), b.get(key)
        change = None if old in (None, 0) or new is None else (new - old) / old
        rows.append({"metric": key, "frozen": old, "live": new, "relative_change": change})
    return rows


def summarize(rows):
    changes = [abs(r["relative_change"]) for r in rows if r["relative_change"] is not None]
    within = lambda t: sum(c <= t for c in changes)
    return {"metrics_compared": len(changes), "missing_in_live": sum(r["live"] is None for r in rows),
            "missing_in_frozen": sum(r["frozen"] is None for r in rows),
            "within_1_percent": within(0.01), "within_5_percent": within(0.05), "within_20_percent": within(0.20),
            "largest": sorted((r for r in rows if r["relative_change"] is not None), key=lambda r: -abs(r["relative_change"]))[:10]}


def check_hashes(manifests=None):
    """Frozen inputs must still match their manifests (offline). A missing file is a failed check, never an exception."""
    results = []
    for manifest_path in manifests or (DAS_MANIFEST, SCREEN_MANIFEST):
        manifest = json.loads(Path(manifest_path).read_text())
        for name, digest in manifest["files"].items():
            path = Path(manifest_path).parent / name
            label = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
            results.append({"file": label, "ok": path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == digest})
    return results


def das_series(collector, c):
    data, _ = c.get("openalex_das_by_year", "https://api.openalex.org/works?" + urlencode({"filter": DAS_FILTER, "group_by": "publication_year"}), sleep=1.0)
    live = {g["key"]: g["count"] for g in data["group_by"]}
    frozen = {str(g["key"]): g["count"] for g in json.loads(DAS_SNAPSHOT.read_text())["group_by"]}
    return {"frozen_2026_10_21": frozen, "live": live}


def markdown(report):
    lines = [f"# Re-query check, {report['run_utc']}", "", "## Frozen-file hashes", "",
             f"{sum(h['ok'] for h in report['hashes'])} of {len(report['hashes'])} frozen files match their manifests.", ""]
    if "das_series" in report:
        lines += ["## DAS title/abstract counts per year (Fig. 2B input)", "", "| Year | Frozen 2026-10-21 | Live |", "|---|---|---|"]
        d = report["das_series"]
        for year in sorted(set(d["frozen_2026_10_21"]) | set(d["live"])):
            lines.append(f"| {year} | {d['frozen_2026_10_21'].get(year, '')} | {d['live'].get(year, '')} |")
        lines.append("")
    for name, block in report.get("comparisons", {}).items():
        s = block["summary"]
        lines += [f"## {name}", "", f"{s['metrics_compared']} numbers compared; {s['within_1_percent']} within 1%, "
                  f"{s['within_5_percent']} within 5%, {s['within_20_percent']} within 20%.", "",
                  "| Largest changes | Frozen | Live | Change |", "|---|---|---|---|"]
        for r in s["largest"]:
            lines.append(f"| {r['metric']} | {r['frozen']} | {r['live']} | {100 * r['relative_change']:+.1f}% |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--with-hf", action="store_true")
    args = parser.parse_args(argv)
    hashes = check_hashes()
    report = {"run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "hashes": hashes}
    if args.offline:
        print(json.dumps({"frozen_files": len(hashes), "matching": sum(h["ok"] for h in hashes)}, indent=2))
        return 0 if all(h["ok"] for h in hashes) else 1
    if not args.out:
        parser.error("--out is required unless --offline")
    out = Path(args.out)
    if (out / "comparison.json").exists():
        parser.error(f"{out}/comparison.json exists; use a new dated folder.")
    collector = load_collector()
    c = collector.Collector(out)
    live = {}
    errors = []
    try:
        report["das_series"] = das_series(collector, c)
    except Exception as error:  # noqa: BLE001 - record and continue with the other sources
        errors.append(f"das_series: {error}")
    for name, fn in (("openalex", collector.collect_openalex), ("simulation", collector.collect_simulation),
                     ("datacite", collector.collect_datacite)) + ((("hf", collector.collect_hf),) if args.with_hf else ()):
        try:
            live[name] = fn(c)
            print(f"{name}: done", flush=True)
        except Exception as error:  # noqa: BLE001
            errors.append(f"{name}: {error}")
            print(f"{name}: failed ({error})", flush=True)
    frozen = json.loads(FROZEN_COUNTS.read_text())
    frozen["simulation"] = json.loads(FROZEN_SIM.read_text())["simulation"]
    report["comparisons"] = {}
    for name, value in live.items():
        rows = compare(frozen.get(name, {}), value)
        report["comparisons"][name] = {"summary": summarize(rows), "rows": rows}
    report["errors"] = errors
    out.mkdir(parents=True, exist_ok=True)
    (out / "counts.json").write_text(json.dumps(live, indent=2, default=str) + "\n")
    (out / "receipts.json").write_text(json.dumps(c.receipts, indent=1) + "\n")
    (out / "comparison.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
    (out / "comparison.md").write_text(markdown(report))
    print((out / "comparison.md").read_text())
    return 1 if errors or not all(h["ok"] for h in hashes) else 0


if __name__ == "__main__":
    sys.exit(main())
