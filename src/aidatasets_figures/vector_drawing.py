"""Small scientific-figure drawing adapter backed by ReportLab, without installs."""
import math
from pathlib import Path
from .rendering import render_png
import numpy as np
from reportlab.graphics.shapes import Drawing, String, Rect, Ellipse, Line, PolyLine, Polygon as RLPolygon
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib.colors import toColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab

FONT_DIR = Path(reportlab.__file__).parent/'fonts'
pdfmetrics.registerFont(TTFont('Vera',str(FONT_DIR/'Vera.ttf')))
pdfmetrics.registerFont(TTFont('VeraBold',str(FONT_DIR/'VeraBd.ttf')))


def col(value):
    if value in [None,'none']:
        return None
    return toColor(value)


class Patch:
    def __init__(self,*args,**kwargs):
        self.args,self.kw = args,kwargs


class FancyBboxPatch(Patch): pass
class Circle(Patch): pass
class Rectangle(Patch): pass
class Polygon(Patch): pass
class FancyArrowPatch(Patch): pass


class Axes:
    def __init__(self,fig):
        self.fig=fig
        self.xlim=(0,13)
        self.ylim=(0,7.3)

    def set_xlim(self,a,b): self.xlim=(a,b)
    def set_ylim(self,a,b): self.ylim=(a,b)
    def axis(self,*args): pass
    def X(self,x): return (x-self.xlim[0])/(self.xlim[1]-self.xlim[0])*self.fig.w
    def Y(self,y): return (y-self.ylim[0])/(self.ylim[1]-self.ylim[0])*self.fig.h
    def W(self,w): return w/(self.xlim[1]-self.xlim[0])*self.fig.w
    def H(self,h): return h/(self.ylim[1]-self.ylim[0])*self.fig.h

    def text(self,x,y,s,fontsize=9,weight='normal',color='#17212B',ha='left',va='center',linespacing=1.35,**kw):
        lines=s.split('\n')
        leading=fontsize*linespacing
        y0=self.Y(y)+(len(lines)-1)*leading/2-fontsize*.34
        font='VeraBold' if weight=='bold' else 'Vera'
        for i,line in enumerate(lines):
            t=String(self.X(x),y0-leading*i,line,fontName=font,fontSize=fontsize,fillColor=col(color),textAnchor={'left':'start','center':'middle','right':'end'}[ha])
            self.fig.drawing.add(t)

    def plot(self,x,y,*args,color='#17212B',lw=1,linewidth=None,marker=None,ms=2,**kw):
        if np.isscalar(x): x=[x]
        if np.isscalar(y): y=[y]
        points=[(self.X(float(xx)),self.Y(float(yy))) for xx,yy in zip(x,y)]
        dot = marker is not None or (args and args[0]=='.')
        if len(points)>1 and not dot:
            self.fig.drawing.add(PolyLine([n for p in points for n in p],strokeColor=col(color),strokeWidth=lw,fillColor=None))
        if dot:
            for px,py in points:
                if marker=='*':
                    pp=[]
                    for j in range(10):
                        r=ms*.55 if j%2==0 else ms*.23
                        a=math.pi/2+j*math.pi/5
                        pp.extend((px+r*math.cos(a),py+r*math.sin(a)))
                    self.fig.drawing.add(RLPolygon(pp,fillColor=col(color),strokeColor=None))
                else:
                    self.fig.drawing.add(Ellipse(px,py,ms/2,ms/2,fillColor=col(color),strokeColor=None))

    def add_patch(self,p):
        k=p.kw
        fc=col(k.get('facecolor',k.get('fc','white')))
        ec=col(k.get('edgecolor',k.get('ec','#17212B')))
        lw=k.get('linewidth',k.get('lw',1))
        if isinstance(p,FancyArrowPatch):
            (x1,y1),(x2,y2)=p.args[:2]
            c=col(k.get('color','#4F5B66'))
            px1,py1,px2,py2=self.X(x1),self.Y(y1),self.X(x2),self.Y(y2)
            dx,dy=px2-px1,py2-py1
            norm=math.hypot(dx,dy)
            ux,uy=dx/norm,dy/norm
            al=k.get('mutation_scale',8)*.65
            base=(px2-ux*al,py2-uy*al)
            self.fig.drawing.add(Line(px1,py1,base[0],base[1],strokeColor=c,strokeWidth=lw))
            self.fig.drawing.add(RLPolygon([px2,py2,base[0]+uy*al*.38,base[1]-ux*al*.38,base[0]-uy*al*.38,base[1]+ux*al*.38],fillColor=c,strokeColor=None))
        elif isinstance(p,Circle):
            (x,y),r=p.args[:2]
            self.fig.drawing.add(Ellipse(self.X(x),self.Y(y),self.W(r),self.H(r),fillColor=fc,strokeColor=ec,strokeWidth=lw))
        elif isinstance(p,(FancyBboxPatch,Rectangle)):
            (x,y),w,h=p.args[:3]
            r=self.W(.12) if isinstance(p,FancyBboxPatch) else 0
            self.fig.drawing.add(Rect(self.X(x),self.Y(y),self.W(w),self.H(h),rx=r,ry=r,fillColor=fc,strokeColor=ec,strokeWidth=lw))
        elif isinstance(p,Polygon):
            self.fig.drawing.add(RLPolygon([n for x,y in p.args[0] for n in (self.X(x),self.Y(y))],fillColor=fc,strokeColor=ec,strokeWidth=lw))
        return p


class Figure:
    def __init__(self,figsize,**kwargs):
        self.w,self.h=figsize[0]*72,figsize[1]*72
        self.drawing=Drawing(self.w,self.h)

    def add_axes(self,*args): return Axes(self)

    def savefig(self,path,dpi=300):
        path=Path(path)
        if path.suffix=='.pdf':
            renderPDF.drawToFile(self.drawing,str(path))
        elif path.suffix=='.svg':
            renderSVG.drawToFile(self.drawing,str(path))
        elif path.suffix=='.png':
            pdf=path.with_suffix('.pdf')
            render_png(pdf, path, dpi=dpi)


class Plotting:
    rcParams={}
    figure=Figure
    @staticmethod
    def close(fig): pass


plt=Plotting()
