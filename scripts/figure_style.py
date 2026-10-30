"""Shared, print-friendly editorial style for the solid-earth opinion report.

Marks retain their data coordinates. Log-volume plots use points (length on a
log axis does not encode volume); linear comparisons use thin stems and points.
"""
import textwrap
import matplotlib.pyplot as plt
from matplotlib.container import BarContainer

OCEAN, OCHRE, MOSS, GOLD, PLUM = '#146B78', '#BB542F', '#547454', '#B78A29', '#886385'
INK, MUTED, GRID, STONE, PAPER = '#243C40', '#586663', '#DCE2DB', '#ABB3A8', '#FCFBF7'


def apply_style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 11,
        'figure.facecolor': PAPER, 'axes.facecolor': PAPER,
        'text.color': INK, 'axes.edgecolor': STONE,
        'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': INK,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.spines.left': False, 'axes.spines.bottom': False,
        'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': .55,
        'axes.axisbelow': True, 'axes.titlelocation': 'left',
        'axes.titlesize': 12, 'axes.titlecolor': INK, 'axes.titlepad': 13,
        'xtick.major.size': 0, 'ytick.major.size': 0,
        'xtick.minor.size': 0, 'ytick.minor.size': 0,
        'svg.fonttype': 'none', 'pdf.fonttype': 42,
        'savefig.facecolor': PAPER,
    })


def finish_figure(fig, out, name, note):
    """Unify exports, with a separate source band and full uncropped labels."""
    fig.set_figheight(fig.get_figheight() * 1.12)
    for ax in fig.axes:
        # Replace horizontal bars only; stacked vertical DAS counts stay intact.
        for container in list(ax.containers):
            if not isinstance(container, BarContainer) or container.orientation != 'horizontal':
                continue
            for bar in container.patches:
                x = bar.get_x() + bar.get_width()
                y = bar.get_y() + bar.get_height() / 2
                color = bar.get_facecolor()
                bar.set_visible(False)
                if ax.get_xscale() != 'log':
                    ax.plot([bar.get_x(), x], [y, y], color=color, lw=2, alpha=.45, zorder=2)
                ax.plot(x, y, 'o', color=color, ms=6, mec=PAPER, mew=.8, zorder=3)
        if ax.get_xscale() == 'log':
            ax.grid(axis='x', which='minor', visible=False)
        # One grid direction is sufficient to read either comparisons or trends.
        if ax.get_yticklabels() and any(t.get_text() and not t.get_text().replace('.', '').replace('−', '').isdigit()
                                       for t in ax.get_yticklabels()):
            ax.grid(axis='y', visible=False)
        else:
            ax.grid(axis='x', visible=False)
        for line in ax.lines:
            if line.get_marker() == 'o' and len(line.get_xdata()) > 1:
                line.set_markeredgecolor(PAPER)
                line.set_markeredgewidth(.8)
        for label in ax.texts:
            label.set_fontsize(max(10, label.get_fontsize()))
        legend = ax.get_legend()
        if legend:
            for label in legend.get_texts():
                label.set_fontsize(10)
    title = fig._suptitle
    if title:
        title.set_text(textwrap.fill(title.get_text(), width=int(fig.get_figwidth() * 9)))
        title.set_fontfamily('DejaVu Serif')
        title.set_fontsize(16)
        title.set_fontweight('normal')
        title.set_y(1.03)
    else:
        # Single-panel figures carry the headline on their axes.
        for ax in fig.axes:
            t = ax._left_title
            t.set_text(textwrap.fill(t.get_text(), width=int(fig.get_figwidth() * 8)))
            t.set_fontfamily('DejaVu Serif')
            t.set_fontsize(15)
    # Place sources below the plot, independently of variable label lengths.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    lower = min(ax.get_tightbbox(renderer).transformed(fig.transFigure.inverted()).y0 for ax in fig.axes)
    source = '\n'.join(textwrap.fill(p, int(fig.get_figwidth() * 16)) for p in note.split('\n'))
    fig.text(.01, lower - .07, source, fontsize=9, color=MUTED, va='top', linespacing=1.45)
    fig.add_artist(plt.Line2D([.01, .99], [lower - .045] * 2, transform=fig.transFigure, color=STONE, lw=.65))
    out.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'svg', 'pdf'):
        fig.savefig(out / f'{name}.{ext}', dpi=300, bbox_inches='tight', pad_inches=.18)
    plt.close(fig)
