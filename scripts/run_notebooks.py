#!/usr/bin/env python3
"""Execute the analysis notebooks in place, in order, from the repository root.

Usage: pixi run -e report notebooks        (or: python scripts/run_notebooks.py [names...])

Offline by default: notebooks read frozen, hash-checked snapshots. Set READINESS_LIVE=1 to let
notebook 02 re-query OpenAlex and DataCite (no keys) into runs/requery_<date>/.
"""
from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("[0-9][0-9]_*.ipynb"))


def main(argv=None):
    names = set(argv or sys.argv[1:])
    for path in NOTEBOOKS:
        if names and path.name not in names:
            continue
        notebook = nbformat.read(path, as_version=4)
        NotebookClient(notebook, timeout=900, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
        nbformat.write(notebook, path)
        print(f"executed {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
