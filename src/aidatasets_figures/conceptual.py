from pathlib import Path
import json
import numpy as np
from .vector_drawing import plt, FancyBboxPatch, Circle, Polygon, FancyArrowPatch, Rectangle

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9,
    'svg.fonttype': 'none', 'pdf.fonttype': 42,
    'axes.linewidth': .7, 'savefig.facecolor': 'white',
})
INK = '#17212B'
MUTED = '#4F5B66'
RULE = '#C9D2D9'
BLUE = '#0072B2'
TEAL = '#009E73'
ORANGE = '#D55E00'
PURPLE = '#8A5C8E'
TINTS = ['#EDF5FA', '#EAF6F1', '#FCF1E8', '#F5EFF7']


def text(ax, x, y, s, size=9.0, weight='normal', color=INK, ha='left', va='center', **kw):
    return ax.text(x, y, s, fontsize=size, weight=weight, color=color,
                   ha=ha, va=va, linespacing=1.20, **kw)


def rounded(ax, xy, w, h, fc='white', ec=RULE, lw=.8, radius=.12, **kw):
    patch = FancyBboxPatch(xy, w, h,
        boxstyle=f'round,pad=0,rounding_size={radius}',
        facecolor=fc, edgecolor=ec, linewidth=lw, **kw)
    ax.add_patch(patch)
    return patch


def arrow(ax, start, end, color=MUTED, lw=1, style='-|>', **kw):
    p = FancyArrowPatch(start, end, arrowstyle=style,
        mutation_scale=8, linewidth=lw, color=color, **kw)
    ax.add_patch(p)
    return p


def new_fig(height):
    fig = plt.figure(figsize=(6.5, height), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.3)
    ax.axis('off')
    return fig, ax


def export(fig, basename, caption, height, output_dir):
    OUT = Path(output_dir)
    for ext in ['svg', 'pdf']:
        fig.savefig(OUT/f'{basename}.{ext}')
    fig.savefig(OUT/f'{basename}.png', dpi=300)
    (OUT/f'{basename}_caption.txt').write_text(caption+'\n', encoding='utf-8')
    plt.close(fig)
    return {'basename': basename, 'width_inches': 6.5, 'height_inches': height,
            'png_pixels': [1950, round(height*300)],
            'formats': ['svg','pdf','png'], 'minimum_label_size_pt': 9.0,
            'kind': 'Original conceptual schematic; no measured results.'}


def event_figure(output_dir):
    height = 3.3
    fig, ax = new_fig(height)
    text(ax, .18, 6.98, 'One Earth event. Multiple physical views.', 12.8, 'bold')
    text(ax, .18, 6.51, 'A common event link preserves what each record measures and how it was produced.', 9.0)
    colors = [BLUE, TEAL, ORANGE, PURPLE]
    xs = [.18, 3.40, 6.62, 9.84]
    titles = ['Observations', 'Simulations', 'Impacts', 'Agent tasks']
    details = ['Waveforms, DAS,\nGNSS and hydrology',
               'Rupture, wavefields,\nphysical settings',
               'Exposure, loss,\nmodeled consequences',
               'Scientific workflows\nand evaluation tasks']
    for x, c, tint, title, detail in zip(xs, colors, TINTS, titles, details):
        rounded(ax, (x, 3.71), 2.98, 2.30, fc=tint, ec='none')
        ax.plot([x+.12, x+2.86], [5.97, 5.97], color=c, lw=2.3)
        text(ax, x+.16, 5.63, title, 9.7, 'bold')
        text(ax, x+.16, 4.07, detail, 9.0)

    # Native observation traces, each with distinct sampling locations.
    x = xs[0]
    for i in range(3):
        tt = np.linspace(0, 1, 250)
        yy = np.sin(2*np.pi*(6+i*.7)*tt)*np.exp(-((tt-.55)/.22)**2)
        ax.plot(x+.22+2.45*tt, 5.14-i*.28+.12*yy, color=BLUE, lw=.9)
        ax.plot(x+.22+2.45*tt[::25], 5.14-i*.28+.12*yy[::25], '.', color=BLUE, ms=2)
    # Mesh and source-centered contours are symbolic, not model results.
    x = xs[1]
    nodes = [(x+.35,4.53),(x+1.05,4.44),(x+1.78,4.57),(x+2.61,4.48),
             (x+.57,4.98),(x+1.35,5.13),(x+2.16,5.02),(x+2.67,5.23)]
    for a,b in [(0,1),(1,2),(2,3),(4,5),(5,6),(6,7),(0,4),(1,4),(1,5),(2,5),(2,6),(3,6),(3,7)]:
        ax.plot([nodes[a][0], nodes[b][0]], [nodes[a][1], nodes[b][1]], color=TEAL, lw=.8)
    for nx,ny in nodes:
        ax.add_patch(Circle((nx,ny),.025,fc=TEAL,ec='none'))
    ax.plot(x+1.36,4.85,marker='*',ms=8,color=TEAL)
    # An exposure graph on geographic support, not an invented damage map.
    x = xs[2]
    for j in range(4):
        ax.plot([x+.26,x+2.69],[4.46+j*.23]*2,color='#E5CDBA',lw=.6)
    for j in range(6):
        ax.plot([x+.26+j*.48]*2,[4.46,5.15],color='#E5CDBA',lw=.6)
    pts = [(x+.55,4.63),(x+1.18,4.95),(x+1.68,4.61),(x+2.32,5.10)]
    for a,b in [(0,1),(1,2),(2,3),(1,3)]:
        ax.plot([pts[a][0],pts[b][0]], [pts[a][1],pts[b][1]], color=ORANGE,lw=1)
    for nx,ny in pts:
        ax.add_patch(Circle((nx,ny),.068,fc='white',ec=ORANGE,lw=1.1))
    # Task flow: question -> evidence -> answer/qualification.
    x = xs[3]
    for xx, yy, label in [(x+.49,4.94,'?'),(x+1.43,4.94,'D'),(x+2.37,4.94,'A')]:
        ax.add_patch(Circle((xx,yy),.24,fc='white',ec=PURPLE,lw=1.1))
        text(ax,xx,yy,label,9,'bold',ha='center')
    arrow(ax,(x+.76,4.94),(x+1.15,4.94),PURPLE,.9)
    arrow(ax,(x+1.70,4.94),(x+2.09,4.94),PURPLE,.9)

    # Four connections into a common corpus; native payloads remain explicit.
    for x,c in zip(xs,colors):
        arrow(ax,(x+1.49,3.71),(x+1.49,3.18),c,1.25)
    rounded(ax,(.18,2.21),12.64,.93,fc='#F2F5F7',ec='#AFBDC8',lw=.8)
    text(ax,6.50,2.83,'EVENT-LINKED CORPUS',9.7,'bold',ha='center')
    text(ax,6.50,2.47,'Event identity  |  Space-time support  |  Observed / derived / simulated',9.0,ha='center')

    blocks = [(.18,'Retain physical meaning','Units, response, native sampling'),
              (4.51,'Make evidence traceable','Uncertainty, provenance, transformations'),
              (8.84,'Test scientific use','Comparability, transfer, abstention')]
    for x,h,d in blocks:
        ax.plot([x,x+3.93],[1.80,1.80],color=RULE,lw=.8)
        text(ax,x,1.50,h,9.3,'bold')
        text(ax,x,.88,d.replace(', native', ',\nnative').replace(', transformations', ',\ntransformations').replace(', transfer', ',\ntransfer'),9.0)
    text(ax,.18,.30,'CONCEPTUAL DRAFT | Oct 20, 2026 | Symbols illustrate design; no measured results.',9.0,color=MUTED)

    caption = ('Figure 1. Event-linked Earth datasets preserve the physical meaning of distinct modalities. '
      'A common physical event connects observations, existing simulation archives, impact/exposure information and scientific-agent evaluation tasks. '
      'The enhancement records each view\'s native sampling, spatial and temporal support, measurement or model configuration, transformations, uncertainty, provenance and permitted uses. '
      'The project will test whether these explicit relationships improve scientific comparison, transfer and traceable inference. '
      'This is an illustrative design, not a measured result, a fixed universal schema or a commitment by an external partner.')
    return export(fig,'Figure_1_Event_Linked_Corpus_DRAFT_2026-10-20',caption,height,output_dir)


def variant_icon(ax,x,y,kind,color=BLUE):
    for row in range(3):
        for col in range(6):
            active = not (kind == 'coverage' and ((row,col) in [(0,1),(0,4),(1,2),(2,0),(2,5)]))
            ec = color if active else '#BCC8D0'
            fc = color if active else 'white'
            alpha = .70 if active else 1
            ax.add_patch(Rectangle((x+col*.115,y+row*.095),.085,.065,fc=fc,ec=ec,lw=.45,alpha=alpha))
    if kind == 'scale':
        for row in range(2):
            for col in range(3):
                ax.add_patch(Rectangle((x+col*.23-.01,y+row*.145-.01),.205,.12,fc='white',ec=color,lw=.75))
    elif kind == 'metadata':
        ax.plot([x+.09,x+.59],[y+.12,y+.12],color='white',lw=2)
        text(ax,x+.34,y+.14,'?',9,'bold',color=color,ha='center')


def readiness_figure(output_dir):
    height = 3.3
    fig,ax = new_fig(height)
    text(ax,.18,6.98,'AI readiness is a testable research question.',12.8,'bold')
    text(ax,.18,6.51,'Which dataset properties predict reliable scientific use for a stated task and learning method?',9.0)
    # Open columns keep the experiment readable without a nested-box maze.
    columns = [(.18,3.46,BLUE,'01','Vary the corpus'),(4.37,3.76,TEAL,'02','Hold experiment fixed'),(8.88,3.94,ORANGE,'03','Measure consequences')]
    for x,w,c,n,h in columns:
        ax.add_patch(Circle((x+.23,5.77),.22,fc=c,ec='none'))
        text(ax,x+.23,5.77,n,9.0,'bold',color='white',ha='center')
        text(ax,x+.60,5.77,h,9.1,'bold')
        ax.plot([x,x+w],[5.38,5.38],color=c,lw=1.5)

    rows = [(4.84,'native','Native / minimally\nenhanced'),
            (4.12,'coverage','Coverage and\nrare conditions'),
            (3.40,'scale','Resolution and\ncompression'),
            (2.68,'metadata','Metadata and\nprovenance')]
    for y,kind,label in rows:
        variant_icon(ax,.26,y-.12,kind)
        text(ax,1.12,y,label,9.0)
    text(ax,.18,1.97,'Controlled changes;\nrights preserved.',9.0,color=MUTED)
    arrow(ax,(3.78,3.78),(4.24,3.78),MUTED,1.2)

    # Same model/training controls apply to the corpus variants.
    rounded(ax,(4.45,3.90),3.60,1.20,fc='#EFF7F4',ec='none')
    text(ax,6.25,4.80,'Reference learning + task',9.0,'bold',ha='center')
    text(ax,6.25,4.34,'Same architecture,\ntraining and task',9.0,ha='center')
    arrow(ax,(6.25,3.88),(6.25,3.48),TEAL,1.1)
    rounded(ax,(4.45,2.30),3.60,1.12,fc='white',ec=TEAL,lw=.9)
    text(ax,6.25,3.11,'HELD-OUT EVALUATION',9.0,'bold',ha='center')
    text(ax,6.25,2.65,'Events / regions / times\nPrespecified partitions',9.0,ha='center')
    text(ax,6.25,1.97,'Prevent leakage across splits.',9.0,color=MUTED,ha='center')
    arrow(ax,(8.24,3.78),(8.72,3.78),MUTED,1.2)

    # Outcomes are labels rather than fake measured bars or quantitative scores.
    outcomes = [(4.90,'Performance + transfer','Accuracy, transfer,\nreproducibility'),
                (3.75,'Uncertainty + failure','Missing support,\nfailure modes'),
                (2.60,'Appropriate abstention','Recognize inadequate\nevidence')]
    for y,h,d in outcomes:
        ax.add_patch(Circle((9.06,y),.08,fc=ORANGE,ec='none'))
        text(ax,9.29,y,h,9.0,'bold')
        text(ax,9.29,y-.53,d,9.0)

    rounded(ax,(.18,.71),12.64,.87,fc='#F2F5F7',ec='#AFBDC8',lw=.8)
    text(ax,6.50,1.26,'EVIDENCE-BASED, TASK-SPECIFIC READINESS PROFILES',9.2,'bold',ha='center')
    text(ax,6.50,.92,'Revise hypotheses and corpus design using independent evidence.',9.0,ha='center')
    text(ax,.18,.30,'CONCEPTUAL DRAFT | Oct 20, 2026 | Experimental design; no performance results implied.',9.0,color=MUTED)

    caption = ('Figure 2. A controlled experiment treats AI readiness as a relationship among a corpus, a learning method and a scientific task. '
      'Variants of the same permitted holdings isolate changes in coverage, scale, compression or metadata wherever feasible. '
      'Reference models and task definitions are held fixed, and evaluation partitions separate events, regions or time periods before final testing. '
      'The team will test whether candidate diagnostics predict downstream performance, transfer, uncertainty, failure and justified abstention. '
      'Independent evidence, including negative results, will support conditional readiness profiles and revisions to the corpus. '
      'All symbols depict the proposed experiment; no empirical outcomes or universal readiness thresholds are implied.')
    return export(fig,'Figure_2_Readiness_Research_Design_DRAFT_2026-10-20',caption,height,output_dir)



def build(output_dir):
    """Reproduce the two conceptual diagrams; no empirical results are inferred."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = [event_figure(output_dir), readiness_figure(output_dir)]
    (output_dir / 'conceptual_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest
