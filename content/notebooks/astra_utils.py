"""Small presentation helpers; scientific models remain visible in each lesson."""
import html
import json
import numpy as np
import matplotlib.pyplot as plt

COLORS = ["#0f9d92", "#ed7953", "#7365c7", "#daa520", "#397ab9"]


class _Animation:
    """Jupyter rich display with a static text fallback and no constructor warnings."""
    def __init__(self, markup):
        self.data = markup

    def _repr_html_(self):
        return self.data

    def __repr__(self):
        return 'Interactive animation: run this cell in JupyterLite to play or scrub.'


def style():
    plt.rcParams.update({"figure.dpi": 100, "figure.figsize": (10, 4.5),
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.prop_cycle": plt.cycler(color=COLORS),
                         "axes.titleweight": "bold", "font.size": 10})


def animate_tracks(tracks, bounds, title="Motion explorer", labels=None, dt=1, units="step"):
    """A compact, self-contained, scrubbable Canvas animation. Initially paused.

    tracks: (frames, objects, 2); bounds: (xmin, xmax, ymin, ymax).
    No CDN, widget extension, video encoder, or remote data is needed.
    """
    tracks = np.asarray(tracks, dtype=float)
    if tracks.ndim != 3 or tracks.shape[2] != 2 or not np.isfinite(tracks).all():
        raise ValueError("tracks must be a finite (frames, objects, 2) array")
    if len(tracks) < 2 or bounds[1] <= bounds[0] or bounds[3] <= bounds[2]:
        raise ValueError("At least two frames and positive plot bounds are required")
    payload = json.dumps({"tracks": tracks.round(5).tolist(), "bounds": list(bounds), "colors": COLORS,
                          "labels": labels or [], "dt": dt, "units": units}).replace("<", "\\u003c")
    template = '''<!doctype html><html lang="en"><meta charset="utf-8"><style>
body{margin:0;padding:16px;background:#0d2233;color:#e9f4f4;font:14px system-ui}h3{margin:0 0 10px}
canvas{width:100%;height:auto;background:#112c3e;border-radius:12px}button,input{margin:10px 8px 4px 0}
button{padding:7px 18px;border:1px solid #73dfcb;border-radius:8px;background:#193d4d;color:white}input{width:50%}
</style><h3>__TITLE__</h3><canvas width="760" height="310" aria-label="__TITLE__ animation"></canvas>
<div><button id="play">Play</button><label>Frame <input id="frame" type="range" min="0" value="0"></label><output id="time"></output></div>
<p id="legend"></p><script>
const d=__DATA__,c=document.querySelector('canvas'),ctx=c.getContext('2d'),s=document.querySelector('#frame'),b=document.querySelector('#play');
s.max=d.tracks.length-1;let f=0,playing=false,last=0;
document.querySelector('#legend').textContent=d.labels.length?d.labels.join(' · '):'Each dot follows one simulated object. Scrub to inspect a moment.';
function draw(){ctx.clearRect(0,0,c.width,c.height);const [x0,x1,y0,y1]=d.bounds;
const X=x=>40+(x-x0)/(x1-x0)*680,Y=y=>275-(y-y0)/(y1-y0)*240;
ctx.strokeStyle='#345263';ctx.lineWidth=1;ctx.strokeRect(40,35,680,240);ctx.fillStyle='#afc9d5';ctx.font='12px system-ui';
ctx.fillText(x0,40,298);ctx.fillText(x1,690,298);ctx.fillText(y1,5,40);ctx.fillText(y0,5,276);
for(let i=0;i<d.tracks[0].length;i++){ctx.strokeStyle=d.colors[i%d.colors.length];ctx.globalAlpha=.45;ctx.beginPath();
for(let j=Math.max(0,f-28);j<=f;j++){const p=d.tracks[j][i];if(j===Math.max(0,f-28))ctx.moveTo(X(p[0]),Y(p[1]));else ctx.lineTo(X(p[0]),Y(p[1]));}ctx.stroke();ctx.globalAlpha=1;
const p=d.tracks[f][i];ctx.beginPath();ctx.arc(X(p[0]),Y(p[1]),4,0,Math.PI*2);ctx.fillStyle=d.colors[i%d.colors.length];ctx.fill();}
s.value=f;document.querySelector('#time').textContent=(f*d.dt).toFixed(2)+' '+d.units;}
b.onclick=()=>{playing=!playing;b.textContent=playing?'Pause':'Play';};s.oninput=()=>{f=+s.value;draw();};
function tick(t){if(playing&&t-last>65){f=(f+1)%d.tracks.length;draw();last=t;}requestAnimationFrame(tick);}draw();requestAnimationFrame(tick);
</script></html>'''
    doc = template.replace("__TITLE__", html.escape(title, quote=True)).replace("__DATA__", payload)
    return _Animation('<iframe title="' + html.escape(title, quote=True) + '" sandbox="allow-scripts" style="width:100%;height:470px;border:0;border-radius:14px" srcdoc="' + html.escape(doc, quote=True) + '"></iframe>')
