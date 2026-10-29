"""Reproduce the two conceptual diagrams from an installed project."""
from aidatasets_figures.__main__ import main

if __name__ == "__main__":
    import sys
    raise SystemExit(main(["--figure", "conceptual", *sys.argv[1:]]))
