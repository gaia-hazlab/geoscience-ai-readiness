#!/usr/bin/env python3
"""Validate the sourced complexity tables of 30 October 2026. Offline, standard library only.

Usage: python scripts/complexity_tables.py [--dir docs/complexity_2026-10-30]

Each table is a JSON object {"retrieved", "method", "rows": [...]}. The checks enforce the
sourcing rules of docs/complexity_2026-10-30/README.md: every row carries units, a source, a
DOI or URL, an as-of date and a read-in-text flag; a missing value is written "not found",
never estimated; a sourced finding without a number starts its value_text with "qualitative:";
a row flagged as read in the text carries the quote it was read from.
The script never adds rows across tables or computes a combined score.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "complexity_2026-10-30"
TABLES = {  # file name: (id prefix, direction-specific required fields)
    "power_laws.json": ("pl-", ("domain", "relation", "symbol", "convention", "tested_vs_alternatives")),
    "dimensionality.json": ("dim-", ("dataset", "kind")),
    "coupled_pdes.json": ("pde-", ("balance_equations_vector", "balance_equations_scalar_3d", "ode_state_variables",
                                   "field_unknowns", "constitutive_closures", "count_derived_by")),
    "unobserved_drivers.json": ("uo-", ("category", "region", "outcome")),
    "ai_evidence.json": ("ai-", ("axis", "evidence_type", "task", "baseline", "metric")),
}
AXES = {"dimensionality", "closures", "tails", "unobserved"}
COMMON = ("id", "item", "quantity", "value", "value_min", "value_max", "value_text", "units", "source", "doi", "url",
          "as_of", "quote", "where_read", "checked_in_text", "notes")
WHERE_READ = {"full text", "abstract", "landing page", "search snippet", "not read"}
TESTED = {"tested, power law favored", "tested, alternative favored or not distinguishable", "tested, mixed",
          "not tested in this source", "not stated"}
DOI = re.compile(r"^10\.\d{4,9}/\S+$")
NUMBER = (int, float)
NOTE_NUMBER = re.compile(r"(?<![A-Za-z])\d")  # a free-standing number; names such as ERA5 pass


def row_errors(row, prefix, extra):
    """Return a list of human-readable problems with one row (empty when the row passes)."""
    rid = row.get("id", "?")
    errs = [f"{rid}: missing field {k!r}" for k in COMMON + extra if k not in row]
    if errs:
        return errs
    bad = lambda msg: errs.append(f"{rid}: {msg}")
    if not str(rid).startswith(prefix):
        bad(f"id must start with {prefix!r}")
    for k in ("value", "value_min", "value_max"):
        if row[k] is not None and (not isinstance(row[k], NUMBER) or isinstance(row[k], bool)):
            bad(f"{k} must be a number or null")
    found = any(row[k] is not None for k in ("value", "value_min", "value_max"))
    text = str(row["value_text"]).strip().lower()
    if not found and "not found" not in text and not text.startswith("qualitative:"):
        bad("no numeric value, so value_text must say 'not found' or start with 'qualitative:'")
    if found and "not found" == str(row["value_text"]).strip().lower():
        bad("value_text says 'not found' but a number is given")
    lo, hi, v = row["value_min"], row["value_max"], row["value"]
    if isinstance(lo, NUMBER) and isinstance(hi, NUMBER):
        if lo > hi:
            bad("value_min exceeds value_max")
        if isinstance(v, NUMBER) and not lo <= v <= hi:
            bad("value lies outside [value_min, value_max]")
    if found and not str(row["units"] or "").strip():
        bad("units required when a value is given")
    if not str(row["source"] or "").strip():
        bad("source required")
    if not (row["doi"] or row["url"]) and found:
        bad("a sourced value needs a DOI or URL")
    if row["doi"] is not None and not DOI.match(str(row["doi"])):
        bad(f"DOI not in 10.xxxx/... form: {row['doi']!r}")
    if found and not str(row["as_of"] or "").strip():
        bad("as_of required when a value is given")
    if not isinstance(row["checked_in_text"], bool):
        bad("checked_in_text must be true or false")
    if row["where_read"] not in WHERE_READ:
        bad(f"where_read must be one of {sorted(WHERE_READ)}")
    if row["checked_in_text"] is True:
        if not str(row["quote"] or "").strip():
            bad("checked_in_text is true but no quote is recorded")
        if row["where_read"] in ("search snippet", "not read"):
            bad("checked_in_text is true but where_read says the source was not fetched")
    if row["quote"] and len(str(row["quote"]).split()) > 40:
        bad("quote longer than 40 words; keep quotations short")
    if "tested_vs_alternatives" in extra and row["tested_vs_alternatives"] not in TESTED:
        bad(f"tested_vs_alternatives must be one of {sorted(TESTED)}")
    if "axis" in extra and (row["axis"] not in AXES or row["evidence_type"] not in ("success", "limitation")):
        bad(f"axis must be one of {sorted(AXES)} and evidence_type success or limitation")
    if "kind" in extra and row["kind"] not in ("nominal", "effective"):
        bad("kind must be 'nominal' or 'effective'")
    if "balance_equations_scalar_3d" in extra and found:
        vec, sca, ode = (row[k] for k in ("balance_equations_vector", "balance_equations_scalar_3d", "ode_state_variables"))
        if not all(isinstance(x, int) and x >= 0 for x in (vec, sca, ode)):
            bad("equation and state-variable counts must be non-negative integers")
        elif sca < vec:
            bad("scalar count cannot be smaller than vector count")
        elif v is not None and v != sca:
            bad("value must equal balance_equations_scalar_3d")
    return errs


def validate_table(payload, prefix, extra):
    errs = []
    if not str(payload.get("retrieved", "")).strip():
        errs.append("table: missing 'retrieved' date")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        return errs + ["table: 'rows' must be a non-empty list"]
    ids = [r.get("id") for r in rows]
    errs += [f"{i}: duplicate id" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for row in rows:
        errs += row_errors(row, prefix, extra)
    return errs


def load(directory=DOCS):
    """Return {file name: payload}; raises ValueError listing every problem found."""
    tables, errs = {}, []
    for name, (prefix, extra) in TABLES.items():
        path = Path(directory) / name
        if not path.is_file():
            errs.append(f"{name}: missing")
            continue
        payload = json.loads(path.read_text())
        errs += [f"{name}: {e}" for e in validate_table(payload, prefix, extra)]
        tables[name] = payload
    profile_path = Path(directory) / "readiness_profile.json"
    if not errs and profile_path.is_file():
        errs += [f"readiness_profile.json: {e}" for e in validate_profile(json.loads(profile_path.read_text()), tables)]
    if errs:
        raise ValueError("\n".join(errs))
    return tables


def validate_profile(profile, tables, pair_labels=None):
    """Check readiness_profile.json: known statuses and columns, and every cited row id exists.

    pair_labels: row labels of the archive-pair table (scripts/archive_readiness_figures.py PAIRS);
    when None, pair:<row> references are not checked.
    """
    errs = []
    statuses, keys = set(profile["statuses"]), [c["key"] for c in profile["columns"]]
    ids = {r["id"] for payload in tables.values() for r in payload["rows"]}
    for row in profile["rows"]:
        d = row.get("discipline", "?")
        for key in keys:
            cell = row.get(key)
            if not isinstance(cell, dict):
                errs.append(f"{d}/{key}: missing cell")
                continue
            if cell.get("status") not in statuses:
                errs.append(f"{d}/{key}: unknown status {cell.get('status')!r}")
            ev = cell.get("evidence", [])
            if cell.get("status") in ("measured", "partial", "not found") and not ev:
                errs.append(f"{d}/{key}: status {cell['status']!r} needs evidence")
            if cell.get("status") == "not assessed" and ev:
                errs.append(f"{d}/{key}: 'not assessed' cannot cite evidence")
            if NOTE_NUMBER.search(cell.get("note", "")):
                errs.append(f"{d}/{key}: notes carry no numbers; numbers come from the cited rows")
            for ref in ev:
                if ref.startswith("pair:"):
                    if pair_labels is not None and ref[5:] not in pair_labels:
                        errs.append(f"{d}/{key}: unknown archive pair {ref!r}")
                elif ref not in ids:
                    errs.append(f"{d}/{key}: unknown row id {ref!r}")
    return errs


def summary(tables):
    lines = []
    for name, payload in tables.items():
        rows = payload["rows"]
        valued = [r for r in rows if any(r[k] is not None for k in ("value", "value_min", "value_max"))]
        read = sum(r["checked_in_text"] for r in valued)
        qualitative = sum(str(r["value_text"]).strip().lower().startswith("qualitative:") for r in rows)
        lines.append(f"{name}: {len(rows)} rows, {len(valued)} with a value, {read} of those read in the source text, "
                     f"{qualitative} qualitative, {len(rows) - len(valued) - qualitative} not found")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", type=Path, default=DOCS)
    args = parser.parse_args()
    try:
        tables = load(args.dir)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(summary(tables))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
