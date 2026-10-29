"""Offline figure reproduction: python -m aidatasets_figures --out build/figures."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from . import __version__
from .rendering import find_pdftoppm


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figure", choices=("all", "conceptual", "das"), default="all")
    parser.add_argument("--out", type=Path, default=Path("build/figures"))
    parser.add_argument("--snapshot", type=Path, default=Path(__file__).parent / "snapshots" / "2026-10-21",
                        help="Copy of the frozen 2026-10-21 snapshot, not a live API refresh")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    try:
        # Fail before partial output if PNG rendering cannot run.
        find_pdftoppm()
        receipt = {"version": __version__, "network_used": False, "figures": {}}
        if args.figure in ("all", "das"):
            from . import das_activity
            das_activity.load_snapshot(args.snapshot)
        if args.figure in ("all", "conceptual"):
            from . import conceptual
            receipt["figures"]["conceptual"] = conceptual.build(args.out)
        if args.figure in ("all", "das"):
            receipt["figures"]["das"] = das_activity.build(args.out, args.snapshot)
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "reproduction_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"Cannot reproduce figures: {error}\n")
    print(f"Figures saved in {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
