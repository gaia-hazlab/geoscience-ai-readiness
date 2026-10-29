"""Portable, explicit PDF-to-PNG rendering with Poppler."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess


def find_pdftoppm() -> str:
    """Use PDFTOPPM or PATH; never depend on the author's machine layout."""
    configured = os.environ.get("PDFTOPPM")
    candidate = shutil.which(configured or "pdftoppm")
    if not candidate:
        raise RuntimeError(
            "PNG export needs Poppler's pdftoppm. Install poppler with your "
            "system package manager, or set PDFTOPPM to its executable path."
        )
    return candidate


def render_png(pdf: str | Path, png: str | Path, dpi: int = 300) -> Path:
    if isinstance(dpi, bool) or not isinstance(dpi, int) or dpi <= 0:
        raise ValueError("dpi must be a positive integer")
    pdf, png = Path(pdf), Path(png)
    if png.suffix.lower() != ".png":
        raise ValueError("PNG output must have a .png suffix")
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    png.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [find_pdftoppm(), "-png", "-singlefile", "-r", str(dpi),
         str(pdf), str(png.with_suffix(""))],
        check=True, capture_output=True,
    )
    if not png.is_file() or not png.stat().st_size:
        raise RuntimeError("Poppler did not create the requested PNG")
    return png
