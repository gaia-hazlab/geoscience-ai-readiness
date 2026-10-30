"""Shared figure style for the readiness and complexity figures. Offline; matplotlib only.

One look for every figure in docs/report: the reference palette of the dataviz skill (light mode,
validated with its validate_palette.js: slots 1 to 3 pass all gates; slot 3 needs visible labels),
a system sans, a bold left-aligned title with a one-line subtitle, hairline value-axis grid, thin
bars with a square baseline and a rounded data end, 2 px lines with end dots only, and a muted
source note. Colour has one meaning across figures: FOCUS (blue) for the geoscience series a
figure is about, CONTEXT (grey) for comparisons and references, SECOND (orange) only for a
genuine second series.
"""
from __future__ import annotations

import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.path import Path as MPath
from matplotlib.ticker import MaxNLocator
from matplotlib.transforms import IdentityTransform

# Reference palette, light mode (dataviz skill references/palette.md)
FOCUS, SECOND, THIRD = "#2a78d6", "#eb6834", "#1baf7a"   # categorical slots 1-3, in this order
FOCUS_LIGHT = "#9ec5f4"                                    # blue ramp step 200: a lighter form of the focus series
CONTEXT = "#b9b8b2"                                        # comparisons, references, other fields
EMPTY = "#efeee9"                                          # a cell with nothing in it
SURFACE = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
FONT = ["Helvetica Neue", "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"]
DPI = 200

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": FONT, "font.size": 8.5, "svg.fonttype": "none",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.labelcolor": INK2, "axes.labelsize": 8.5,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.axisbelow": True,
    "axes.titlelocation": "left", "axes.titlesize": 9.5, "axes.titleweight": "bold", "axes.titlecolor": INK,
    "axes.titlepad": 10, "grid.color": GRID, "grid.linewidth": 0.6, "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelcolor": INK2, "ytick.labelcolor": INK2, "xtick.labelsize": 8, "ytick.labelsize": 8.5,
    "xtick.major.size": 0, "ytick.major.size": 0, "xtick.major.pad": 5, "ytick.major.pad": 6,
    "lines.linewidth": 1.8, "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
    "legend.frameon": False, "legend.fontsize": 8, "legend.handlelength": 1.0, "legend.handleheight": 0.9,
    "legend.borderaxespad": 0.2, "legend.columnspacing": 1.4,
})

NOTE_CHARS_PER_IN = 19          # wrap width of the 6.5 pt source note
TITLE_BAND, NOTE_LINE = 0.78, 0.118


def figure(width, plot_height, note, *, left=1.9, right=0.35, xband=0.55, ncols=1, wspace=0.35, sharey=False,
           top=None):
    """A figure with fixed bands in inches: title and subtitle on top, plot, x-axis, then the source note.

    Multi-panel figures get a taller top band so panel titles clear the subtitle.
    """
    top = top if top is not None else TITLE_BAND + (0.32 if ncols > 1 else 0)
    lines = sum(len(textwrap.wrap(p, int(width * NOTE_CHARS_PER_IN))) or 1 for p in note.split("\n"))
    note_h = 0.14 + lines * NOTE_LINE
    height = top + plot_height + xband + note_h
    fig, axes = plt.subplots(1, ncols, figsize=(width, height), sharey=sharey)
    fig.subplots_adjust(left=left / width, right=1 - right / width, top=1 - top / height,
                        bottom=(xband + note_h) / height, wspace=wspace)
    fig._readiness_note = note
    return fig, axes


def header(fig, title, subtitle=None):
    """Bold title and a one-line subtitle, left-aligned to the figure edge."""
    h = fig.get_figheight()
    fig.text(0.16 / fig.get_figwidth(), 1 - 0.20 / h, title, fontsize=11, fontweight="bold", color=INK, va="top")
    if subtitle:
        fig.text(0.16 / fig.get_figwidth(), 1 - 0.43 / h, subtitle, fontsize=8.5, color=INK2, va="top")


def finish(fig, out, name):
    """Source note in muted ink at the bottom, then PNG and SVG."""
    note = fig._readiness_note
    width = int(fig.get_figwidth() * NOTE_CHARS_PER_IN)
    wrapped = "\n".join(textwrap.fill(p, width) for p in note.split("\n"))
    fig.text(0.16 / fig.get_figwidth(), 0.12 / fig.get_figheight(), wrapped, fontsize=6.5, color=MUTED, va="bottom",
             linespacing=1.35)
    for ext in ("png", "svg"):
        fig.savefig(out / f"{name}.{ext}", dpi=DPI)
    plt.close(fig)


class RoundedBar(Patch):
    """Horizontal bar from x0 to x1 at row y: square at the baseline, rounded at the data end.

    The path is computed in display space at draw time, so it is right on linear and log axes and in
    every backend, and the corner radius stays a fixed size in points.
    """

    def __init__(self, ax, y, x0, x1, height, radius_pt=2.6, **kw):
        super().__init__(**kw)
        self._ax, self._y, self._x0, self._x1, self._h, self._r = ax, y, x0, x1, height, radius_pt
        self.set_transform(IdentityTransform())

    def get_path(self):
        t = self._ax.transData
        (xa, ya), (xb, yb) = t.transform([(self._x0, self._y - self._h / 2), (self._x1, self._y + self._h / 2)])
        lo, hi = min(ya, yb), max(ya, yb)
        sign = 1 if xb >= xa else -1
        r = min(self._r * self._ax.figure.dpi / 72, abs(xb - xa), (hi - lo) / 2)
        e = xb - sign * r
        verts = [(xa, lo), (e, lo), (xb, lo), (xb, lo + r), (xb, hi - r), (xb, hi), (e, hi), (xa, hi), (xa, lo)]
        codes = [MPath.MOVETO, MPath.LINETO, MPath.CURVE3, MPath.CURVE3, MPath.LINETO, MPath.CURVE3, MPath.CURVE3,
                 MPath.LINETO, MPath.CLOSEPOLY]
        return MPath(verts, codes)


def hbar(ax, y, x1, color, *, x0=0.0, height=0.58, **kw):
    """Draw one rounded horizontal bar; returns the patch."""
    kw.setdefault("zorder", 2.5)
    bar = RoundedBar(ax, y, x0, x1, height, facecolor=color, edgecolor="none", linewidth=0, **kw)
    ax.add_patch(bar)
    bar.set_clip_path(ax.patch)
    return bar


def bar_axes(ax, labels, *, log=False):
    """Category axis for horizontal bars: labels top to bottom, value grid only, baseline hairline."""
    n = len(labels)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_yticks(range(n), labels[::-1])
    ax.grid(axis="y", visible=False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    if log:
        ax.set_xscale("log")
    else:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=6, steps=[1, 2, 5, 10]))


def tip(ax, x, y, text, *, color=INK, size=7.5, dx=4, style="normal", weight="normal"):
    """Value label just beyond a bar end or point, offset in points (works on log axes)."""
    return ax.annotate(text, (x, y), xytext=(dx, 0), textcoords="offset points", va="center", ha="left", fontsize=size,
                       color=color, fontstyle=style, fontweight=weight, annotation_clip=False, zorder=4,
                       bbox=dict(boxstyle="square,pad=0.12", fc=SURFACE, ec="none"))


def text_width_pt(text, size=7.5):
    """Rough rendered width of a label in points, for placing a second label after it."""
    return 0.56 * size * len(text)


def series(ax, xs, ys, color, label=None, *, end_dot=True, z=3):
    """A 2 px line with a ringed end dot at the last point only."""
    ax.plot(xs, ys, color=color, lw=1.8, label=label, zorder=z)
    if end_dot:
        ax.plot(xs[-1:], ys[-1:], "o", ms=6.5, mfc=color, mec=SURFACE, mew=1.6, zorder=z + 1)


def reference(ax, x, label, *, y_text=None):
    """A solid muted hairline marking a reference value, labelled above the plot."""
    ax.axvline(x, color=MUTED, lw=0.9, zorder=1.5)
    ymax = ax.get_ylim()[1] if y_text is None else y_text
    ax.annotate(label, (x, ymax), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=7.5,
                color=INK2, annotation_clip=False)


def swatch_legend(ax, items, *, loc="lower right", ncol=1, anchor=None, marker="s", hollow=()):
    """Legend of square swatches (or other markers); hollow lists labels drawn as open markers."""
    if marker == "line":
        handles = [Line2D([], [], color=col, lw=2.2) for _, col in items]
    else:
        handles = [Line2D([], [], marker=marker, ls="", ms=7, mfc=SURFACE if lab in hollow else col,
                          mec=INK2 if lab in hollow else col, mew=1.1) for lab, col in items]
    kw = {"bbox_to_anchor": anchor} if anchor else {}
    return ax.legend(handles, [lab for lab, _ in items], loc=loc, ncol=ncol, handletextpad=0.5, **kw)


def human(n):
    for unit, scale in (("PB", 1e15), ("TB", 1e12), ("GB", 1e9), ("MB", 1e6)):
        if n >= scale:
            return f"{n / scale:.3g} {unit}"
    return f"{n:.3g} B"
