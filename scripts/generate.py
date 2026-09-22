"""Gera os SVGs animados do README do perfil (assets/header.svg).

As fontes (Space Grotesk e JetBrains Mono, OFL) são recortadas para os caracteres usados e
embutidas em base64, porque o GitHub não deixa um SVG em <img> baixar arquivos externos.
Toda animação usa só transform e opacity, e para com prefers-reduced-motion.

Uso: python3 scripts/generate.py <pasta-das-fontes-woff2>
"""

import base64
import io
import math
import random
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONTS = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

BG = "#0a0c10"
ASH_100 = "#eeece7"
ASH_300 = "#b3bac5"
ASH_400 = "#8d96a4"
EMBER_300 = "#ffb454"
EMBER_400 = "#ff8a3d"
EMBER_500 = "#ff6a2b"

GLYPHS = "{}()<>[];=/*+-_:.#$&|!?01fnletconstreturnasyncawait"
REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } .in, .fin { opacity: 1 !important; } }"


def font_face(family: str, file: str, weight: int, text: str) -> str:
    """Instance a variable font at one weight, keep only `text`, return an @font-face rule."""
    font = TTFont(FONTS / file)
    font = instancer.instantiateVariableFont(font, {"wght": weight})
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern", "liga"]
    sub = subset.Subsetter(options)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2');}}"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# --------------------------------------------------------------------------- header
def header() -> None:
    W, H = 1280, 380
    rnd = random.Random(1584)
    words = ["Node.js", "NestJS", "Next.js", "React", "TypeScript"]
    title = "Douglas Vulcano"
    role = "Desenvolvedor Full Stack"
    prompt = "~/douglas $ whoami"

    # Volcano made of glyphs, anchored bottom-right.
    cx, base_y, cell_w, cell_h = 975, H - 18, 11, 17

    def surface(x: float) -> float:
        dx = (x - cx) / 290
        cone = math.exp(-(abs(dx) ** 1.2))
        crater = 0.07 * math.exp(-(((x - cx) / 26) ** 2))
        return base_y - (cone - crater) * 262

    crater_y = surface(cx)
    rock, lava = [], []
    channels = [(-5, -0.3), (5, 0.22), (-11, -0.58), (12, 0.46), (0, 0.03)]
    for gx in range(int((cx - 330) / cell_w), int((cx + 330) / cell_w) + 1):
        x = gx * cell_w
        top = surface(x)
        y = crater_y - ((crater_y - top) // cell_h) * cell_h  # keep rows on a shared grid
        while y < top:
            y += cell_h
        while y <= base_y:
            depth = (y - top) / 90
            hot = 0.0
            for off, slope in channels:
                lx = cx + off + slope * (y - crater_y) + 5 * math.sin(y / 17 + off)
                hot = max(hot, math.exp(-(((x - lx) / 6) ** 2)) * math.exp(-max(0, y - crater_y) / 230))
            ch = rnd.choice(GLYPHS)
            fade = min(1.0, max(0.0, 1 - abs(x - cx) / 330)) ** 0.45
            if hot > 0.14:
                k = min(1.0, hot * 1.3)
                g, b = round(72 + 124 * k), round(24 + 68 * k)
                lava.append((x, y, ch, f"rgb(255,{g},{b})", round((0.55 + 0.45 * k) * fade, 2)))
            else:
                edge = math.exp(-depth * 2.6)
                rim = (y - top) < cell_h
                v = round(96 + 60 * max(edge * 0.6, 1 if rim else 0))
                op = (0.42 + 0.5 * max(edge, 0.9 if rim else 0)) * fade
                if op > 0.06:
                    rock.append((x, y, ch, f"rgb({v},{v + 8},{v + 22})", round(op, 2)))
            y += cell_h

    used_mono = GLYPHS + prompt + "·*+.'°"
    css = [
        font_face("Grotesk", "space-grotesk-latin-wght-normal.woff2", 700, title),
        font_face("GroteskM", "space-grotesk-latin-wght-normal.woff2", 500, role + "com " + "".join(words)),
        font_face("Mono", "jetbrains-mono-latin-wght-normal.woff2", 600, used_mono),
        """
        .mono{font-family:'Mono',ui-monospace,monospace;font-weight:600}
        .rock text,.lava text{font-size:13px;text-anchor:middle;dominant-baseline:middle}
        .in{opacity:0;animation:in .9s cubic-bezier(.22,1,.36,1) forwards}
        @keyframes in{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
        .lava{animation:pulse 2.4s ease-in-out infinite}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:.72}}
        .spark{animation:rise var(--d) linear infinite;animation-delay:var(--t);opacity:0}
        @keyframes rise{0%{opacity:0;transform:translate(0,0)}10%{opacity:1}100%{opacity:0;transform:translate(var(--x),-150px)}}
        .word{opacity:0;animation:word 12.5s cubic-bezier(.22,1,.36,1) infinite}
        @keyframes word{0%{opacity:0;transform:translateY(18px)}3%,17%{opacity:1;transform:none}20%,100%{opacity:0;transform:translateY(-18px)}}
        .glow{animation:glow 5s ease-in-out infinite;transform-origin:975px 140px}
        @keyframes glow{0%,100%{opacity:.85;transform:scale(1)}50%{opacity:1;transform:scale(1.08)}}
        .caret{animation:blink 1s steps(2) infinite}
        @keyframes blink{50%{opacity:0}}
        """,
        REDUCED,
    ]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-labelledby="t d">',
        '<title id="t">Douglas Vulcano, Desenvolvedor Full Stack</title>',
        '<desc id="d">Banner animado: um vulcão desenhado com caracteres de código e a stack Node.js, NestJS, '
        "Next.js, React e TypeScript.</desc>",
        f"<style>{''.join(css)}</style>",
        "<defs>",
        '<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">'
        '<circle cx="1" cy="1" r="1" fill="#ffffff" fill-opacity=".045"/></pattern>',
        '<radialGradient id="g" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" '
        f'gradientTransform="translate({cx} {crater_y + 10}) scale(340 260)">'
        '<stop offset="0" stop-color="#ff6a2b" stop-opacity=".32"/>'
        '<stop offset=".5" stop-color="#ff6a2b" stop-opacity=".07"/>'
        '<stop offset="1" stop-color="#ff6a2b" stop-opacity="0"/></radialGradient>',
        f'<clipPath id="c"><rect width="{W}" height="{H}" rx="20"/></clipPath>',
        "</defs>",
        '<g clip-path="url(#c)">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
        f'<rect class="glow" width="{W}" height="{H}" fill="url(#g)"/>',
        '<g class="rock mono">',
    ]
    for x, y, ch, fill, op in rock:
        parts.append(f'<text x="{x}" y="{y:.0f}" fill="{fill}" fill-opacity="{op}">{esc(ch)}</text>')
    parts.append('</g><g class="lava mono">')
    for x, y, ch, fill, op in lava:
        parts.append(f'<text x="{x}" y="{y:.0f}" fill="{fill}" fill-opacity="{op}">{esc(ch)}</text>')
    parts.append("</g>")
    for i in range(26):
        sx = cx + rnd.uniform(-12, 12)
        d = rnd.uniform(2.4, 4.2)
        t = -rnd.uniform(0, d)
        dx = rnd.uniform(-70, 70)
        ch = rnd.choice("·*+.'°")
        size = rnd.choice([11, 13, 15])
        parts.append(
            f'<text class="spark mono" style="--d:{d:.2f}s;--t:{t:.2f}s;--x:{dx:.0f}px" x="{sx:.0f}" '
            f'y="{crater_y - 6:.0f}" font-size="{size}" fill="{EMBER_300}" text-anchor="middle">{esc(ch)}</text>'
        )

    X = 72
    parts += [
        f'<g class="in" style="animation-delay:.1s"><text class="mono" x="{X}" y="112" font-size="19" fill="{ASH_400}">'
        f'~/douglas <tspan fill="{EMBER_400}">$ whoami</tspan></text></g>',
        f'<g class="in" style="animation-delay:.25s"><text x="{X - 3}" y="190" font-family="Grotesk,Segoe UI,sans-serif" '
        f'font-weight="700" font-size="76" letter-spacing="-2" fill="{ASH_100}">{title}</text></g>',
        f'<g class="in" style="animation-delay:.45s"><text x="{X}" y="246" font-family="GroteskM,Segoe UI,sans-serif" '
        f'font-weight="500" font-size="32" fill="{ASH_100}">{role}</text></g>',
        f'<g class="in" style="animation-delay:.6s"><text x="{X}" y="294" font-family="GroteskM,Segoe UI,sans-serif" '
        f'font-weight="500" font-size="32" fill="{ASH_400}">com</text></g>',
    ]
    for i, w in enumerate(words):
        parts.append(
            f'<g class="word{' fin' if i == 0 else ''}" style="animation-delay:{0.6 + i * 2.5:.1f}s"><text x="{X + 78}" y="294" '
            f'font-family="GroteskM,Segoe UI,sans-serif" font-weight="500" font-size="32" fill="{EMBER_400}">{w}</text></g>'
        )
    parts.append("</g>")
    parts.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="19.5" fill="none" stroke="#1a1f28"/>')
    parts.append("</svg>")
    (OUT / "header.svg").write_text("\n".join(parts))


header()
for f in sorted(OUT.glob("*.svg")):
    print(f.name, f"{f.stat().st_size / 1024:.1f} KB")
