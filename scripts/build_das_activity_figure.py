"""Reproduce the frozen DAS publication-activity figure from an installed project."""
from aidatasets_figures.__main__ import main

if __name__ == "__main__":
    import sys
    raise SystemExit(main(["--figure", "das", *sys.argv[1:]]))
