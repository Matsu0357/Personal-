"""時計職人キャラを SVG で描く。表情差分シートを書き出す。

    python3 craftsman.py  ->  expressions.svg
"""

INK = "#1B1B1F"
BROWN = "#8B5A2B"
DARK_BROWN = "#6B4320"
FONT = "Hiragino Sans, Noto Sans JP, sans-serif"

LENS_DEF = """<radialGradient id="lens" cx="0.4" cy="0.35" r="0.7">
  <stop offset="0" stop-color="#EAF6FF"/><stop offset="1" stop-color="#9FCBEA"/>
</radialGradient>
<clipPath id="lensClip"><circle cx="42" cy="-4" r="33"/></clipPath>"""


def eye(cx, cy, rx, ry, pr, expr, outer):
    """outer: -1 なら外側が左（左目）、1 なら右（ルーペ側）"""
    if expr == "happy":
        return (f'<path d="M{cx - rx * 0.8} {cy + 8} Q{cx} {cy - ry * 0.9} {cx + rx * 0.8} {cy + 8}" '
                f'stroke="#FFF" stroke-width="9" fill="none" stroke-linecap="round"/>')
    if expr == "surprised":
        rx, ry = rx * 1.12, ry * 1.12
        px, py, pr = cx, cy, pr * 0.6
    elif expr == "thinking":
        px, py = cx + 8, cy - 14
    elif expr == "sad":
        px, py, pr = cx, cy + 16, pr * 0.85
    else:
        px, py = cx + 6, cy + 10
    s = (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#FFF"/>'
         f'<circle cx="{px}" cy="{py}" r="{pr}" fill="#111"/>'
         f'<circle cx="{px + pr * 0.35}" cy="{py - pr * 0.45}" r="{pr * 0.36}" fill="#FFF"/>')
    if expr == "sad":
        # 外側が下がったまぶた
        lo, hi = (cy - 4, cy - 18) if outer < 0 else (cy - 18, cy - 4)
        s += (f'<path d="M{cx - rx - 4} {lo} L{cx + rx + 4} {hi} L{cx + rx + 4} {cy - ry - 6} '
              f'L{cx - rx - 4} {cy - ry - 6} Z" fill="{INK}"/>')
    return s


def craftsman(x, y, scale=1.0, expr="normal"):
    """(x, y) は頭の中心。expr: normal / surprised / thinking / happy / sad"""
    p = [f'<g transform="translate({x} {y}) scale({scale})">']
    p.append('<ellipse cx="0" cy="270" rx="95" ry="14" fill="#000" opacity="0.15"/>')
    for sx in (-1, 1):
        p.append(f'<path d="M{25 * sx} 190 L{32 * sx} 255" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>')
        p.append(f'<ellipse cx="{40 * sx}" cy="260" rx="20" ry="10" fill="{INK}"/>')
    if expr != "thinking":
        p.append(f'<path d="M-62 135 Q-95 165 -90 200" stroke="{INK}" stroke-width="15" fill="none" stroke-linecap="round"/>')
    p.append(f'<ellipse cx="0" cy="150" rx="70" ry="60" fill="{INK}"/>')
    # エプロン
    p.append(f'<path d="M-32 108 H32 L48 202 Q0 216 -48 202 Z" fill="{BROWN}"/>')
    p.append(f'<path d="M-32 108 Q0 80 32 108" stroke="{DARK_BROWN}" stroke-width="5" fill="none"/>')
    p.append(f'<rect x="-20" y="142" width="40" height="28" rx="4" fill="{DARK_BROWN}"/>')
    p.append('<path d="M-12 142 V130" stroke="#C0C0C8" stroke-width="3" stroke-linecap="round"/>')
    p.append('<path d="M-4 142 V126" stroke="#D4A24C" stroke-width="3" stroke-linecap="round"/>')
    # 頭
    p.append(f'<circle cx="0" cy="0" r="112" fill="{INK}"/>')
    p.append(eye(-38, 2, 27, 35, 12.5, expr, -1))
    # ルーペ
    p.append('<path d="M38 -40 Q80 -70 105 -40" stroke="#3E2A17" stroke-width="4" fill="none"/>')
    p.append('<circle cx="42" cy="-4" r="46" fill="#6B4A2B" stroke="#3E2A17" stroke-width="6"/>')
    p.append('<circle cx="42" cy="-4" r="33" fill="url(#lens)"/>')
    p.append(f'<g clip-path="url(#lensClip)">{eye(42, 0, 24, 29, 13, expr, 1)}</g>')
    p.append('<path d="M20 -22 Q28 -32 40 -34" stroke="#FFF" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.8"/>')
    # 右腕とドライバー
    if expr == "sad":
        p.append(f'<path d="M62 135 Q95 165 95 200" stroke="{INK}" stroke-width="15" fill="none" stroke-linecap="round"/>')
        p.append('<rect x="87" y="200" width="16" height="30" rx="5" fill="#C8432F"/>')
        p.append('<path d="M95 230 V258" stroke="#C0C0C8" stroke-width="4" stroke-linecap="round"/>')
    else:
        p.append(f'<path d="M62 135 Q115 125 140 100" stroke="{INK}" stroke-width="15" fill="none" stroke-linecap="round"/>')
        p.append('<rect x="134" y="70" width="16" height="30" rx="5" fill="#C8432F"/>')
        p.append('<path d="M142 70 V40" stroke="#C0C0C8" stroke-width="4" stroke-linecap="round"/>')
    # 表情ごとの演出
    if expr == "thinking":
        p.append(f'<path d="M-62 135 Q-115 120 -70 92" stroke="{INK}" stroke-width="15" fill="none" stroke-linecap="round"/>')
        p.append(f'<text x="-150" y="-95" font-family="{FONT}" font-size="80" font-weight="900" fill="{BROWN}">?</text>')
    elif expr == "surprised":
        for d in ('M-60 -125 L-75 -150', 'M0 -135 L0 -165', 'M60 -125 L75 -150'):
            p.append(f'<path d="{d}" stroke="#3B2A1A" stroke-width="7" stroke-linecap="round"/>')
    elif expr == "happy":
        for sx, sy, r in ((-130, -90, 22), (150, -60, 16), (120, -130, 12)):
            p.append(f'<path d="M{sx} {sy - r} Q{sx} {sy} {sx + r} {sy} Q{sx} {sy} {sx} {sy + r} '
                     f'Q{sx} {sy} {sx - r} {sy} Q{sx} {sy} {sx} {sy - r} Z" fill="#E8B23A"/>')
    elif expr == "sad":
        p.append('<path d="M-52 40 Q-60 58 -52 66 Q-44 58 -52 40 Z" fill="#7EC3F0"/>')
        for d in ('M-70 -150 V-125', 'M-40 -158 V-130', 'M-10 -150 V-125'):
            p.append(f'<path d="{d}" stroke="#7E9BB8" stroke-width="5" stroke-linecap="round"/>')
    p.append('</g>')
    return "\n".join(p)


def expressions_sheet():
    items = [("normal", "通常"), ("surprised", "驚き"), ("thinking", "考え中"),
             ("happy", "ドヤ・喜び"), ("sad", "しょんぼり")]
    w, h = 1600, 600
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           '<defs>', LENS_DEF,
           '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#FFF4E0"/><stop offset="1" stop-color="#FFD9A8"/></linearGradient>',
           '</defs>',
           f'<rect width="{w}" height="{h}" fill="url(#bg)"/>',
           f'<text x="{w / 2}" y="62" text-anchor="middle" font-family="{FONT}" font-size="38" '
           f'font-weight="800" fill="#3B2A1A">時計職人くん 表情差分</text>']
    for i, (expr, label) in enumerate(items):
        x = 170 + i * 315
        out.append(craftsman(x, 240, 0.75, expr))
        out.append(f'<text x="{x}" y="525" text-anchor="middle" font-family="{FONT}" font-size="30" '
                   f'font-weight="800" fill="#3B2A1A">{label}</text>')
    out.append('</svg>')
    return "\n".join(out)


if __name__ == "__main__":
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expressions.svg")
    with open(path, "w") as f:
        f.write(expressions_sheet())
