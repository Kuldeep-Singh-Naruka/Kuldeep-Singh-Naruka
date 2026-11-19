#!/usr/bin/env python3
"""Generates the space-themed SVGs used in README.md (dark + light variants).

    python assets/generate.py

Pure Python, no dependencies. SVGs are self-contained (system fonts, CSS/SMIL
animation) so GitHub renders them through <img>/<picture>.
"""
import math, random, os
from xml.sax.saxutils import escape

OUT = os.path.dirname(os.path.abspath(__file__))
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', SFMono-Regular, Consolas, 'Liberation Mono', monospace"

THEMES = {
    'dark': dict(bg0='#0d1430', bg1='#05070d', ink='#ece8e1', ink2='#a8b0bc', ink3='#6f7885',
                 accent='#5ad1e6', star='#ffffff', line='#ffffff', line_op=0.13, chip='#ffffff', chip_op=0.07,
                 panel='#0a0f1e', milky=True),
    'light': dict(bg0='#faf6f1', bg1='#efe7de', ink='#1c2226', ink2='#4a5156', ink3='#7a7f84',
                  accent='#5b2f3b', star='#1c2226', line='#1c2226', line_op=0.16, chip='#1c2226', chip_op=0.06,
                  panel='#f5eee6', milky=False),
}
STAR_COLORS = ['#9bb0ff', '#cad7ff', '#f8f7ff', '#fff4ea', '#ffd2a1']


def stars(t, w, h, n, seed, twinkle=0.25, avoid=None):
    """avoid = (x0, y0, x1, y1): keep this box (the text) star-free."""
    r = random.Random(seed)
    out = []
    for i in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h)
        if avoid and avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]:
            continue
        size = r.choice([0.6, 0.7, 0.8, 1.0, 1.0, 1.3, 1.6]) + (1.2 if r.random() < 0.03 else 0)
        col = r.choice(STAR_COLORS) if t['milky'] else t['star']
        op = r.uniform(0.35, 0.95) if t['milky'] else r.uniform(0.18, 0.42)
        cls = ''
        if r.random() < twinkle:
            cls = f' class="tw" style="animation-delay:{r.uniform(0, 5):.2f}s"'
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size}" fill="{col}" opacity="{op:.2f}"{cls}/>')
    return '\n'.join(out)


STYLE = """<style>
.tw{animation:tw 4.5s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}
.met{animation:met 9s linear infinite;opacity:0}
@keyframes met{0%{transform:translate(0,0);opacity:0}1.5%{opacity:1}9%{transform:translate(-380px,190px);opacity:0}100%{transform:translate(-380px,190px);opacity:0}}
.pulse{animation:pulse 3s ease-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes pulse{0%{transform:scale(.3);opacity:.9}100%{transform:scale(2.6);opacity:0}}
@media (prefers-reduced-motion: reduce){.tw,.met,.pulse{animation:none}}
</style>"""


def defs(t):
    milky = ''
    return f"""<defs>
<radialGradient id="bg" cx="28%" cy="18%" r="95%"><stop offset="0" stop-color="{t['bg0']}"/><stop offset="1" stop-color="{t['bg1']}"/></radialGradient>
<radialGradient id="sun" cx="40%" cy="40%" r="65%"><stop offset="0" stop-color="#fffbe8"/><stop offset=".35" stop-color="#ffd27a"/><stop offset=".75" stop-color="#f59a3a"/><stop offset="1" stop-color="#c2410c"/></radialGradient>
<radialGradient id="corona"><stop offset=".55" stop-color="#ffb35c" stop-opacity="{.55 if t['milky'] else .35}"/><stop offset="1" stop-color="#ff8a3c" stop-opacity="0"/></radialGradient>
<radialGradient id="planet" cx="35%" cy="35%" r="75%"><stop offset="0" stop-color="#f3dfb8"/><stop offset=".6" stop-color="#c9a27a"/><stop offset="1" stop-color="#5a3e26"/></radialGradient>
<radialGradient id="blue" cx="35%" cy="35%" r="75%"><stop offset="0" stop-color="#9fc4ff"/><stop offset=".6" stop-color="#4a6be0"/><stop offset="1" stop-color="#162660"/></radialGradient>
<linearGradient id="meteor" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['star']}" stop-opacity="0"/><stop offset="1" stop-color="{t['star']}" stop-opacity=".95"/></linearGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
</defs>"""


def frame(t, w, h, body, label):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">
{STYLE}
{defs(t)}
<clipPath id="clip"><rect width="{w}" height="{h}" rx="18"/></clipPath>
<g clip-path="url(#clip)">
<rect width="{w}" height="{h}" fill="url(#bg)"/>
{body}
</g>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="18" fill="none" stroke="{t['line']}" stroke-opacity="{t['line_op']*0.8:.2f}"/>
</svg>"""


def milky_way(t, w, h):
    if not t['milky']:
        return ''
    return f'<ellipse cx="{w*0.45}" cy="{h*0.55}" rx="{w*0.55}" ry="{h*0.16}" fill="#6b5fa8" opacity=".16" filter="url(#blur)" transform="rotate(-14 {w*0.45} {h*0.55})"/>'


def meteor(t, x, y, delay=0):
    return (f'<g class="met" style="animation-delay:{delay}s"><line x1="{x}" y1="{y}" x2="{x+120}" y2="{y-60}" '
            f'stroke="url(#meteor)" stroke-width="2" stroke-linecap="round" transform="rotate(180 {x+60} {y-30})"/></g>')


# ─── Banner ─────────────────────────────────────────────────────────────────
def banner(theme):
    t = THEMES[theme]
    w, h = 1200, 340
    sx, sy, sr = 1150, 175, 150
    orbit = f'M {sx-470} {sy} a 470 125 0 1 0 940 0 a 470 125 0 1 0 -940 0'
    spots = ''.join(f'<ellipse cx="{sx+dx}" cy="{sy+dy}" rx="{rx}" ry="{ry}" fill="#8a2c08" opacity=".55"/>'
                    for dx, dy, rx, ry in [(-70, -40, 7, 4), (-95, 30, 5, 3), (-40, 70, 6, 3.5)])
    body = f"""
{milky_way(t, w, h)}
{stars(t, w, h, 210, 7, avoid=(50, 70, 760, 300))}
<circle cx="{sx}" cy="{sy}" r="{sr*1.75}" fill="url(#corona)"/>
<circle cx="{sx}" cy="{sy}" r="{sr}" fill="url(#sun)"/>
{spots}
<g fill="none" stroke="{t['line']}" stroke-opacity="{t['line_op']}">
  <path d="{orbit}" transform="rotate(-6 {sx} {sy})"/>
  <ellipse cx="{sx}" cy="{sy}" rx="330" ry="88" transform="rotate(-6 {sx} {sy})"/>
</g>
<g transform="rotate(-6 {sx} {sy})">
  <g>
    <ellipse rx="27" ry="7" fill="none" stroke="#d8c08b" stroke-width="3" opacity=".85"/>
    <circle r="13" fill="url(#planet)"/>
    <path d="M -27 0 A 27 7 0 0 0 27 0" fill="none" stroke="#d8c08b" stroke-width="3" opacity=".85"/>
    <animateMotion dur="70s" repeatCount="indefinite" path="{orbit}"/>
  </g>
  <g>
    <circle r="7" fill="url(#blue)"/>
    <animateMotion dur="38s" begin="-12s" repeatCount="indefinite" path="M {sx-330} {sy} a 330 88 0 1 0 660 0 a 330 88 0 1 0 -660 0"/>
  </g>
</g>
{meteor(t, 560, 70)}
{meteor(t, 300, 40, 4.5)}
<text x="70" y="150" font-family="{SERIF}" font-size="68" fill="{t['ink']}" letter-spacing="1">Kuldeep Singh</text>
<text x="72" y="196" font-family="{SERIF}" font-size="27" fill="{t['ink2']}">Backend Engineer – GenAI &amp; Agentic AI</text>
<text x="72" y="242" font-family="{MONO}" font-size="13.5" fill="{t['ink3']}" letter-spacing="2">// JAIPUR, INDIA · 4+ YEARS · PYTHON · FASTAPI · LANGGRAPH · NODE.JS</text>
<circle cx="78" cy="281" r="4" fill="{t['accent']}"/>
<circle cx="78" cy="281" r="4" fill="{t['accent']}" class="pulse"/>
<text x="92" y="286" font-family="{MONO}" font-size="13" fill="{t['accent']}" letter-spacing="2">OPEN TO BACKEND · GENAI · AGENTIC AI ROLES</text>
"""
    return frame(t, w, h, body, 'Kuldeep Singh — Backend Engineer, GenAI & Agentic AI')


# ─── Spacecraft illustrations (drawn around 0,0) ────────────────────────────
def station(t):
    wings = []
    for x in (-150, -116, 116, 150):
        for d in (-1, 1):
            y0 = 10 if d == 1 else -96
            wings.append(f'<rect x="{x-13}" y="{y0}" width="26" height="86" fill="#b8742a" stroke="#5a3a12" stroke-width="1"/>')
            wings.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y0+86}" stroke="#5a3a12" stroke-width="1.2"/>')
            for k in range(1, 9):
                wings.append(f'<line x1="{x-13}" y1="{y0+k*9.6:.1f}" x2="{x+13}" y2="{y0+k*9.6:.1f}" stroke="#5a3a12" stroke-width=".6" opacity=".7"/>')
    white = '#eceae5'
    return f"""<g>
{''.join(wings)}
<rect x="-170" y="-5" width="340" height="10" fill="#9aa0aa" stroke="#5f656e"/>
{''.join(f'<line x1="{x}" y1="-5" x2="{x}" y2="5" stroke="#5f656e"/>' for x in range(-165, 170, 15))}
<rect x="-78" y="10" width="34" height="40" fill="#f4f4f2" stroke="#b9bcc0" opacity=".95"/>
<rect x="44" y="10" width="34" height="40" fill="#f4f4f2" stroke="#b9bcc0" opacity=".95"/>
<rect x="-11" y="-30" width="22" height="80" rx="10" fill="{white}" stroke="#b9bcc0"/>
<rect x="-42" y="34" width="84" height="16" rx="8" fill="{white}" stroke="#b9bcc0"/>
<rect x="-6" y="-46" width="12" height="20" fill="#d4a24c" stroke="#8a6420"/>
<path d="M -8 50 L 0 64 L 8 50 Z" fill="{white}" stroke="#b9bcc0"/>
</g>"""


def probe(t):
    cells = ''.join(f'<line x1="{x}" y1="-14" x2="{x}" y2="14" stroke="#9fb0d0" stroke-width=".7" opacity=".7"/>'
                    for x in list(range(-150, -50, 17)) + list(range(55, 155, 17)))
    sig = ''.join(f'<ellipse cx="0" cy="-70" rx="34" ry="9" fill="none" stroke="{t["accent"]}" stroke-width="1.5" class="pulse" style="animation-delay:{d}s"/>'
                  for d in (0, 1, 2))
    return f"""<g transform="rotate(-12)">
<line x1="-150" y1="0" x2="150" y2="0" stroke="#8a8f99" stroke-width="2"/>
<rect x="-150" y="-14" width="100" height="28" fill="#13234a" stroke="#9fb0d0" stroke-width="1"/>
<rect x="50" y="-14" width="100" height="28" fill="#13234a" stroke="#9fb0d0" stroke-width="1"/>
{cells}
<rect x="-26" y="-24" width="52" height="48" fill="#c9a03a" stroke="#7a5a14"/>
<path d="M -26 -24 l 8 -6 h 52 l -8 6 Z" fill="#e2bd5a" stroke="#7a5a14"/>
<path d="M -48 -44 Q 0 -10 48 -44 Q 0 -60 -48 -44 Z" fill="#f2f0ea" stroke="#b9bcc0"/>
<line x1="0" y1="-30" x2="0" y2="-62" stroke="#8a8f99" stroke-width="2"/>
<circle cx="0" cy="-64" r="3" fill="#8a8f99"/>
<line x1="0" y1="24" x2="0" y2="54" stroke="#8a8f99" stroke-width="1.5"/>
{sig}
</g>"""


def telescope(t):
    s = 17
    hexes = []
    for q in range(-2, 3):
        for rr in range(-2, 3):
            d = max(abs(q), abs(rr), abs(-q - rr))
            if d in (1, 2):
                x = s * 1.78 * (q + rr / 2)
                y = s * 1.78 * (rr * math.sqrt(3) / 2)
                pts = ' '.join(f'{x + s*math.cos(math.pi/3*k):.1f},{y + s*math.sin(math.pi/3*k):.1f}' for k in range(6))
                shade = '#f2c25a' if (q + rr) % 2 else '#e3ac3e'
                hexes.append(f'<polygon points="{pts}" fill="{shade}" stroke="#8a6420" stroke-width="1"/>')
    shield = ''.join(f'<polygon points="-120,{70+k*6} -60,{40+k*6} 60,{40+k*6} 120,{70+k*6} 60,{100+k*6} -60,{100+k*6}" '
                     f'fill="#a596cf" fill-opacity="{.95-k*.12:.2f}" stroke="#6e5ea0" stroke-width="1"/>' for k in range(4, -1, -1))
    return f"""<g>
{shield}
<rect x="-4" y="22" width="8" height="30" fill="#8a8f99"/>
<g transform="translate(0,-20)">
{''.join(hexes)}
<line x1="0" y1="-88" x2="0" y2="-5" stroke="#9aa0aa" stroke-width="2"/>
<line x1="-74" y1="40" x2="0" y2="-88" stroke="#9aa0aa" stroke-width="1.5" opacity=".8"/>
<line x1="74" y1="40" x2="0" y2="-88" stroke="#9aa0aa" stroke-width="1.5" opacity=".8"/>
<polygon points="0,-96 7,-92 7,-84 0,-80 -7,-84 -7,-92" fill="#f2c25a" stroke="#8a6420"/>
</g>
</g>"""


# ─── Mission cards ─────────────────────────────────────────────────────────
PROJECTS = [
    dict(slug='recallops', num='01', kind='MULTI-AGENT AI · GRAPH MEMORY', title='RecallOps',
         lines=['Five incident-response agents share one memory in FalkorDB.',
                'They recall which fixes worked, across 3 dependency hops,',
                'and learn from every "fix worked / didn\'t work".'],
         stats=['5 LangGraph agents', '0 lost writes · 50 threads', '35 tests'],
         stack=['Python', 'LangGraph', 'FalkorDB', 'Cypher', 'Groq', 'Streamlit'], art=station, ax=930),
    dict(slug='api-monitor', num='02', kind='AGENTIC AI · RAG', title='API Integration Monitor Agent',
         lines=['Watches third-party API docs for changes with a 5-node',
                'LangGraph state machine, flags breaking vs non-breaking',
                'changes and suggests code fixes, with RAG over ChromaDB.'],
         stats=['5-node state machine', 'RAG · ChromaDB', 'LangSmith traced'],
         stack=['Python', 'FastAPI', 'LangGraph', 'LangChain', 'PostgreSQL', 'ChromaDB'], art=probe, ax=950),
    dict(slug='hireflow', num='03', kind='LLM PIPELINE · EXPLAINABLE AI', title='HireFlow',
         lines=['AI candidate screening & interview intelligence. Maps every',
                'job requirement to quoted resume evidence instead of an',
                'opaque score, then writes interview questions from the gaps.'],
         stats=['Cited matches', 'Structured extraction', 'Auto interview Qs'],
         stack=['Python', 'FastAPI', 'Groq', 'LangChain', 'PostgreSQL', 'React'], art=telescope, ax=950),
]


def chip_row(t, x, y, items, mono=False, size=12.5):
    out, cx = [], x
    for it in items:
        wch = len(it) * (7.6 if mono else 7.5) * size / 12.5 + 22
        out.append(f'<rect x="{cx:.1f}" y="{y-16}" width="{wch:.1f}" height="24" rx="12" fill="{t["chip"]}" fill-opacity="{t["chip_op"]}" stroke="{t["line"]}" stroke-opacity="{t["line_op"]+0.05:.2f}"/>')
        out.append(f'<text x="{cx+11:.1f}" y="{y}" font-family="{MONO if mono else SANS}" font-size="{size}" fill="{t["ink2"]}">{escape(it)}</text>')
        cx += wch + 8
    return '\n'.join(out)


def card(p, theme):
    t = THEMES[theme]
    w, h = 1200, 300
    desc = '\n'.join(f'<text x="56" y="{140 + i*24}" font-family="{SANS}" font-size="16" fill="{t["ink2"]}">{escape(l)}</text>'
                     for i, l in enumerate(p['lines']))
    stats = '  ·  '.join(p['stats'])
    body = f"""
{milky_way(t, w, h)}
{stars(t, w, h, 120, sum(map(ord, p['slug'])), 0.2, avoid=(40, 28, 700, 290))}
<text x="56" y="56" font-family="{MONO}" font-size="12.5" fill="{t['accent']}" letter-spacing="2.4">MISSION {p['num']} · {p['kind']}</text>
<text x="56" y="103" font-family="{SERIF}" font-size="40" fill="{t['ink']}">{escape(p['title'])}</text>
{desc}
<text x="56" y="232" font-family="{MONO}" font-size="12.5" fill="{t['ink3']}" letter-spacing="1">{escape(stats)}</text>
{chip_row(t, 56, 272, p['stack'])}
<g transform="translate({p['ax']},150)">{p['art'](t)}</g>
<text x="{w-40}" y="{h-26}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{t['ink3']}">view repo →</text>
"""
    return frame(t, w, h, body, f"{p['title']} — {p['kind'].title()}")


# ─── Divider + footer ───────────────────────────────────────────────────────
def divider():
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="34" viewBox="0 0 1200 34" role="img" aria-label="">
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="#8a93a0" stop-opacity="0"/><stop offset=".5" stop-color="#8a93a0" stop-opacity=".55"/><stop offset="1" stop-color="#8a93a0" stop-opacity="0"/></linearGradient>
<radialGradient id="p" cx="35%" cy="35%" r="75%"><stop offset="0" stop-color="#ffd2a1"/><stop offset=".6" stop-color="#e9775c"/><stop offset="1" stop-color="#7a2c1a"/></radialGradient></defs>
<line x1="0" y1="17" x2="1200" y2="17" stroke="url(#l)" stroke-width="1"/>
<ellipse cx="600" cy="17" rx="22" ry="5" fill="none" stroke="#8a93a0" stroke-opacity=".7" stroke-width="1.4"/>
<circle cx="600" cy="17" r="8" fill="url(#p)"/>
<path d="M 578 17 A 22 5 0 0 0 622 17" fill="none" stroke="#8a93a0" stroke-opacity=".7" stroke-width="1.4"/>
</svg>"""


def footer(theme):
    t = THEMES[theme]
    w, h = 1200, 220
    cx, cy = 980, 110
    dark = theme == 'dark'
    disk_hot, disk_warm = ('#fff1d6', '#ff8c3a') if dark else ('#c86a2a', '#9a4618')
    body = f"""
{milky_way(t, w, h)}
{stars(t, w, h, 100, 99, 0.2, avoid=(40, 50, 720, 185))}
<defs>
 <radialGradient id="disk" cx="50%" cy="50%" r="50%"><stop offset=".45" stop-color="{disk_hot}" stop-opacity="0"/><stop offset=".55" stop-color="{disk_hot}"/><stop offset=".75" stop-color="{disk_warm}" stop-opacity=".85"/><stop offset="1" stop-color="{disk_warm}" stop-opacity="0"/></radialGradient>
 <radialGradient id="halo"><stop offset=".6" stop-color="{disk_warm}" stop-opacity=".0"/><stop offset=".72" stop-color="{disk_warm}" stop-opacity=".55"/><stop offset="1" stop-color="{disk_warm}" stop-opacity="0"/></radialGradient>
</defs>
<ellipse cx="{cx}" cy="{cy}" rx="150" ry="30" fill="url(#disk)"/>
<circle cx="{cx}" cy="{cy}" r="62" fill="url(#halo)"/>
<circle cx="{cx}" cy="{cy}" r="40" fill="#000" stroke="{disk_hot}" stroke-width="2"/>
<path d="M {cx-150} {cy} A 150 30 0 0 0 {cx+150} {cy}" fill="none" stroke="{disk_hot}" stroke-width="5" stroke-opacity=".9"/>
<path d="M {cx-118} {cy+6} A 118 22 0 0 0 {cx+118} {cy+6}" fill="none" stroke="{disk_warm}" stroke-width="3" stroke-opacity=".8"/>
<text x="56" y="92" font-family="{SERIF}" font-size="40" fill="{t['ink']}">Let's build something.</text>
<text x="58" y="132" font-family="{SANS}" font-size="16" fill="{t['ink2']}">Backend-heavy projects, agentic AI, and systems that don't break at 3 AM.</text>
<text x="58" y="170" font-family="{MONO}" font-size="12.5" fill="{t['ink3']}" letter-spacing="2">EVERYTHING GETS PULLED IN EVENTUALLY ↘</text>
"""
    return frame(t, w, h, body, "Let's build something")


def write(name, svg):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(svg)


if __name__ == '__main__':
    for th in THEMES:
        write(f'banner-{th}.svg', banner(th))
        write(f'footer-{th}.svg', footer(th))
        for p in PROJECTS:
            write(f'mission-{p["slug"]}-{th}.svg', card(p, th))
    write('divider.svg', divider())
    print('ok')
