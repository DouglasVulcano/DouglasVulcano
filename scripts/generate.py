"""Gera os SVGs animados do README do perfil (assets/header.svg e assets/terminal.svg).

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
OK = "#34d399"

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


# --------------------------------------------------------------------------- terminal
def terminal() -> None:
    W = 880
    steps = [
        ("whoami", [("douglas-vulcano · desenvolvedor full stack", ASH_300)]),
        (
            "cat stack.json",
            [
                ("{", ASH_400),
                ('  "backend":  ["Node.js", "NestJS", "REST", "PostgreSQL"],', EMBER_300),
                ('  "frontend": ["Next.js", "React", "TypeScript"],', EMBER_300),
                ('  "cloud":    ["Docker", "AWS", "CI/CD"],', EMBER_300),
                ('  "ai":       ["Claude Code", "Copilot", "Gemini"]', EMBER_300),
                ("}", ASH_400),
            ],
        ),
        ("ls ~/produtos", [("nexo/    zeroth/", OK)]),
        ("git log --oneline -1", [("feat: construindo o próximo produto", ASH_300)]),
    ]
    char_w, line_h, pad_x, top = 9.6, 25, 30, 78
    all_text = "".join(c for s in steps for c in s[0]) + "".join(t for s in steps for t, _ in s[1]) + "❯ douglas@vulcano: ~"
    css = [
        font_face("Mono", "jetbrains-mono-latin-wght-normal.woff2", 400, all_text),
        font_face("MonoB", "jetbrains-mono-latin-wght-normal.woff2", 600, "❯"),
        """
        text{font-family:'Mono',ui-monospace,monospace;font-size:16px;white-space:pre}
        .p{font-family:'MonoB','Mono',monospace}
        .cover{animation-fill-mode:both;animation-timing-function:steps(var(--n))}
        @keyframes type{from{transform:translateX(0)}to{transform:translateX(var(--w))}}
        .out{opacity:0;animation:out .35s ease-out forwards}
        @keyframes out{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
        .caret{opacity:0;animation:show 0s linear forwards, blink 1s steps(2) infinite}
        @keyframes show{to{opacity:1}}
        @keyframes blink{50%{fill-opacity:0}}
        .beam{animation:spin 7s linear infinite;transform-box:view-box}
        @keyframes spin{to{transform:rotate(360deg)}}
        """,
        REDUCED,
        "@media (prefers-reduced-motion: reduce){.cover{display:none}.out,.caret{opacity:1 !important}}",
    ]
    rows = []
    y = top
    t = 0.75
    type_ms, pause = 0.055, 0.45
    for cmd, out in steps:
        n = len(cmd)
        dur = n * type_ms
        width = n * char_w + 2
        rows.append(
            f'<g class="out" style="animation-delay:{t - 0.15:.2f}s">'
            f'<text x="{pad_x}" y="{y}" fill="{EMBER_400}" class="p">❯</text>'
            f'<text x="{pad_x + 22}" y="{y}" fill="{ASH_100}">{esc(cmd)}</text></g>'
        )
        rows.append(
            f'<rect class="cover" x="{pad_x + 20}" y="{y - 18}" width="{width + 12}" height="24" fill="#0d1015" '
            f'style="--n:{n};--w:{width + 12}px;animation-name:type;animation-duration:{dur:.2f}s;animation-delay:{t:.2f}s"/>'
        )
        t += dur + pause
        y += line_h
        for text, color in out:
            rows.append(
                f'<text class="out" x="{pad_x}" y="{y}" fill="{color}" style="animation-delay:{t:.2f}s">{esc(text)}</text>'
            )
            t += 0.07
            y += line_h
        t += pause
        y += 10
    rows.append(f'<text class="out" x="{pad_x}" y="{y}" fill="{EMBER_400}" style="animation-delay:{t:.2f}s">❯</text>')
    rows.append(
        f'<rect class="caret" x="{pad_x + 22}" y="{y - 15}" width="9" height="19" fill="{EMBER_400}" '
        f'style="animation-delay:{t:.2f}s,{t:.2f}s"/>'
    )
    H = y + 34

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="tt td">',
        '<title id="tt">Terminal de Douglas Vulcano</title>',
        '<desc id="td">Terminal digitando: whoami, a stack em JSON (Node.js, NestJS, Next.js, React, TypeScript, '
        "Docker, AWS e ferramentas de IA) e os produtos Nexo e Zeroth.</desc>",
        f"<style>{''.join(css)}</style>",
        "<defs>",
        f'<clipPath id="win"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
        '<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#ff6a2b" stop-opacity="0"/><stop offset=".85" stop-color="#ff6a2b"/>'
        '<stop offset="1" stop-color="#ffb454"/></linearGradient>',
        f'<mask id="ring"><rect width="{W}" height="{H}" rx="16" fill="#fff"/>'
        f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="14.5" fill="#000"/></mask>',
        "</defs>",
        '<g clip-path="url(#win)">',
        f'<rect width="{W}" height="{H}" fill="#0d1015"/>',
        f'<rect width="{W}" height="46" fill="#11151c"/>',
        f'<rect y="46" width="{W}" height="1" fill="#1f2530"/>',
        '<circle cx="26" cy="23" r="6.5" fill="#ff5f57"/><circle cx="48" cy="23" r="6.5" fill="#febc2e"/>'
        '<circle cx="70" cy="23" r="6.5" fill="#28c840"/>',
        f'<text x="94" y="28" fill="{ASH_400}" font-size="13">douglas@vulcano: ~</text>',
        *rows,
        "</g>",
        f'<rect width="{W}" height="{H}" rx="16" fill="none" stroke="#1f2530"/>',
        # A beam of light that travels along the border (rotated gradient, masked to the ring).
        f'<g mask="url(#ring)"><rect class="beam" x="{W / 2}" y="{H / 2 - 70}" width="{W}" height="140" '
        f'fill="url(#beam)" style="transform-origin:{W / 2}px {H / 2}px"/></g>',
        "</svg>",
    ]
    (OUT / "terminal.svg").write_text("\n".join(parts))


header()
terminal()
for f in sorted(OUT.glob("*.svg")):
    print(f.name, f"{f.stat().st_size / 1024:.1f} KB")
