"""シーンに置く小道具。時計はすべてロゴなしの汎用デザイン。"""
import math

FONT = "Hiragino Sans, Noto Sans JP, IPAGothic, sans-serif"
SERIF = "Times New Roman, DejaVu Serif, serif"
STEEL = "#C9CDD4"
GOLD = "#D4A24C"


def _hands(r, time, color, sec_color=None, width=1.0):
    h, m = time
    ha, ma = (h % 12) * 30 + m * 0.5, m * 6
    p = [f'<line x1="0" y1="{r * 0.08}" x2="0" y2="{-r * 0.45}" stroke="{color}" stroke-width="{r * 0.055 * width}" '
         f'stroke-linecap="round" transform="rotate({ha})"/>',
         f'<line x1="0" y1="{r * 0.1}" x2="0" y2="{-r * 0.7}" stroke="{color}" stroke-width="{r * 0.038 * width}" '
         f'stroke-linecap="round" transform="rotate({ma})"/>']
    if sec_color:
        p.append(f'<line x1="0" y1="{r * 0.15}" x2="0" y2="{-r * 0.78}" stroke="{sec_color}" stroke-width="{r * 0.012}" '
                 f'transform="rotate(200)"/>')
    p.append(f'<circle r="{r * 0.045}" fill="{color}"/>')
    return "".join(p)


def _markers(r, kind, ink, lume=False):
    p = []
    if kind == "bars":
        for i in range(12):
            w = 0.045 if i % 3 == 0 else 0.03
            p.append(f'<line x1="0" y1="{-r * 0.8}" x2="0" y2="{-r * 0.64}" stroke="{ink}" stroke-width="{r * w}" '
                     f'stroke-linecap="round" transform="rotate({i * 30})"/>')
    elif kind == "dots":
        for i in range(12):
            if i % 3 == 0:
                p.append(f'<rect x="{-r * 0.05}" y="{-r * 0.8}" width="{r * 0.1}" height="{r * 0.18}" rx="{r * 0.02}" '
                         f'fill="{"#F2F0D8" if lume else ink}" transform="rotate({i * 30})"/>')
            else:
                p.append(f'<circle cx="0" cy="{-r * 0.72}" r="{r * 0.06}" fill="{"#F2F0D8" if lume else ink}" '
                         f'transform="rotate({i * 30})"/>')
    elif kind in ("arabic", "pilot", "roman"):
        labels = {"arabic": ["12", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
                  "pilot": ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
                  "roman": ["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]}[kind]
        fam, size = (SERIF, 0.15) if kind == "roman" else (FONT, 0.2)
        for i, lab in enumerate(labels):
            a = math.radians(i * 30)
            x, y = math.sin(a) * r * 0.66, -math.cos(a) * r * 0.66
            p.append(f'<text x="{x:.1f}" y="{y + r * size * 0.36:.1f}" text-anchor="middle" font-family="{fam}" '
                     f'font-size="{r * size:.1f}" font-weight="700" fill="{ink}">{lab}</text>')
        if kind == "pilot":
            p.append(f'<path d="M{-r * 0.1} {-r * 0.84} L{r * 0.1} {-r * 0.84} L0 {-r * 0.62}Z" fill="{ink}"/>')
    return "".join(p)


def analog(cx, cy, r, *, case=STEEL, dial="#151517", ink="#FFF", markers="bars", time=(10, 10),
           strap="#24242A", bezel=None, tachy=False, dive=False, subdials=0, pushers=False,
           sec_color=None, lume=False, crown_left=False):
    p = []
    if strap:
        p.append(f'<rect x="{cx - r * 0.42}" y="{cy - r * 1.6}" width="{r * 0.84}" height="{r * 3.2}" rx="{r * 0.1}" fill="{strap}"/>')
    for sy in (-1, 1):
        for sx in (-1, 1):
            p.append(f'<rect x="{cx + sx * r * 0.62 - r * 0.11}" y="{cy + sy * r * 1.0 - r * 0.2}" '
                     f'width="{r * 0.22}" height="{r * 0.4}" rx="{r * 0.06}" fill="{case}"/>')
    side = -1 if crown_left else 1
    cx0 = cx + side * r * 0.98 - (r * 0.2 if side < 0 else 0)
    p.append(f'<rect x="{cx0}" y="{cy - r * 0.12}" width="{r * 0.2}" height="{r * 0.24}" rx="{r * 0.04}" fill="{case}"/>')
    if pushers:
        for sy in (-1, 1):
            p.append(f'<rect x="{cx + r * 0.82}" y="{cy + sy * r * 0.55 - r * 0.08}" width="{r * 0.22}" height="{r * 0.16}" '
                     f'rx="{r * 0.04}" fill="{case}" transform="rotate({sy * 32} {cx + r * 0.85} {cy + sy * r * 0.55})"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 1.06}" fill="{case}" stroke="#00000033" stroke-width="{r * 0.02}"/>')
    p.append(f'<g transform="translate({cx} {cy})">')
    inner = 1.0
    if bezel:
        p.append(f'<circle r="{r}" fill="{bezel}"/>')
        inner = 0.85
        if tachy:
            for i in range(60):
                long = i % 5 == 0
                p.append(f'<line x1="0" y1="{-r * 0.97}" x2="0" y2="{-r * (0.89 if long else 0.93)}" stroke="#FFF" '
                         f'stroke-width="{r * (0.018 if long else 0.008)}" transform="rotate({i * 6})"/>')
        if dive:
            for i in range(12):
                if i == 0:
                    p.append(f'<path d="M{-r * 0.06} {-r * 0.97} H{r * 0.06} L0 {-r * 0.88}Z" fill="#F2F0D8"/>')
                else:
                    p.append(f'<line x1="0" y1="{-r * 0.97}" x2="0" y2="{-r * 0.9}" stroke="#FFF" stroke-width="{r * 0.03}" '
                             f'transform="rotate({i * 30})"/>')
    p.append(f'<circle r="{r * inner}" fill="{dial}"/>')
    p.append(_markers(r, markers, ink, lume))
    if subdials:
        for dx, dy in ((0.42, 0), (0, 0.42), (-0.42, 0)):
            p.append(f'<circle cx="{dx * r}" cy="{dy * r}" r="{r * 0.19}" fill="#00000022" stroke="{ink}" '
                     f'stroke-opacity="0.5" stroke-width="{r * 0.012}"/>')
            p.append(f'<line x1="{dx * r}" y1="{dy * r}" x2="{dx * r}" y2="{dy * r - r * 0.15}" stroke="{ink}" '
                     f'stroke-width="{r * 0.015}"/>')
    p.append(_hands(r, time, ink if not lume else "#F2F0D8", sec_color, 1.3 if lume else 1.0))
    p.append(f'<path d="M{-r * 0.6} {-r * 0.55} A{r * 0.82} {r * 0.82} 0 0 1 {r * 0.1} {-r * 0.82}" '
             f'stroke="#FFF" stroke-width="{r * 0.03}" fill="none" opacity="0.15" stroke-linecap="round"/>')
    p.append('</g>')
    return "".join(p)


def square(cx, cy, w, h, *, case=STEEL, dial="#F4F1EA", ink="#222", screws=False, gadroons=False,
           strap="#3A2A1A", subdials=0, crown_left=False, time=(10, 10), roman=False):
    p = [f'<rect x="{cx - w * 0.32}" y="{cy - h * 1.15}" width="{w * 0.64}" height="{h * 2.3}" rx="{w * 0.06}" fill="{strap}"/>']
    cr = cx - w * 0.62 if crown_left else cx + w * 0.52
    p.append(f'<rect x="{cr}" y="{cy - h * 0.06}" width="{w * 0.1}" height="{h * 0.12}" rx="{w * 0.02}" fill="{case}"/>')
    p.append(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="{w * 0.12}" fill="{case}" '
             f'stroke="#00000033" stroke-width="{w * 0.01}"/>')
    if gadroons:
        for sy in (-1, 1):
            for k in range(3):
                y = cy + sy * (h * 0.44 - k * h * 0.035)
                p.append(f'<line x1="{cx - w * 0.38}" y1="{y}" x2="{cx + w * 0.38}" y2="{y}" stroke="#8E949C" stroke-width="{w * 0.012}"/>')
    inset = 0.14 if gadroons else 0.1
    dw, dh = w * (1 - inset * 2), h * (1 - (0.22 if gadroons else inset * 2))
    p.append(f'<rect x="{cx - dw / 2}" y="{cy - dh / 2}" width="{dw}" height="{dh}" rx="{w * 0.06}" fill="{dial}"/>')
    if screws:
        for sx in (-1, 1):
            for sy in (-1, 1):
                p.append(f'<circle cx="{cx + sx * w * 0.42}" cy="{cy + sy * h * 0.42}" r="{w * 0.035}" fill="#8E949C"/>')
        for x in (cx - w * 0.15, cx + w * 0.15):
            p.append(f'<circle cx="{x}" cy="{cy - h * 0.45}" r="{w * 0.03}" fill="#8E949C"/>')
            p.append(f'<circle cx="{x}" cy="{cy + h * 0.45}" r="{w * 0.03}" fill="#8E949C"/>')
    r = min(dw, dh) / 2
    p.append(f'<g transform="translate({cx} {cy})">')
    if subdials:
        for dx in (-0.42, 0.42):
            p.append(f'<circle cx="{dx * r}" cy="{r * 0.1}" r="{r * 0.24}" fill="#00000022" stroke="{ink}" stroke-width="{r * 0.02}"/>')
    if roman:
        p.append(_markers(r * 1.1, "roman", ink))
    else:
        for i in range(12):
            a = math.radians(i * 30)
            p.append(f'<line x1="{math.sin(a) * r * 0.75:.1f}" y1="{-math.cos(a) * r * 0.75:.1f}" '
                     f'x2="{math.sin(a) * r * 0.92:.1f}" y2="{-math.cos(a) * r * 0.92:.1f}" stroke="{ink}" '
                     f'stroke-width="{r * (0.06 if i % 3 == 0 else 0.035)}" stroke-linecap="round"/>')
    p.append(_hands(r, time, ink, None, 1.1))
    p.append('</g>')
    return "".join(p)


def octagon(cx, cy, r, dial="#2B4C7E"):
    """八角形ベゼル + 一体型ブレスレット + 格子文字盤"""
    p = [f'<path d="M{cx - r * 0.75} {cy - r * 2.0} H{cx + r * 0.75} L{cx + r * 0.85} {cy} L{cx + r * 0.75} {cy + r * 2.0} '
         f'H{cx - r * 0.75} L{cx - r * 0.85} {cy} Z" fill="#B9BEC6"/>']
    for k in range(-5, 6):
        if abs(k) >= 2:
            y = cy + k * r * 0.33
            p.append(f'<line x1="{cx - r * 0.75}" y1="{y}" x2="{cx + r * 0.75}" y2="{y}" stroke="#8E949C" stroke-width="{r * 0.02}"/>')
    p.append(f'<rect x="{cx - r * 1.12}" y="{cy - r * 1.05}" width="{r * 2.24}" height="{r * 2.1}" rx="{r * 0.4}" fill="{STEEL}"/>')
    pts = " ".join(f"{cx + math.cos(math.radians(22.5 + i * 45)) * r * 1.0:.1f},{cy + math.sin(math.radians(22.5 + i * 45)) * r * 1.0:.1f}"
                   for i in range(8))
    p.append(f'<polygon points="{pts}" fill="#DADDE2" stroke="#8E949C" stroke-width="{r * 0.02}"/>')
    for i in range(8):
        a = math.radians(i * 45)
        p.append(f'<circle cx="{cx + math.cos(a) * r * 0.86:.1f}" cy="{cy + math.sin(a) * r * 0.86:.1f}" r="{r * 0.055}" '
                 f'fill="#9AA0A8" stroke="#7A808A" stroke-width="{r * 0.01}"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.74}" fill="{dial}"/>')
    for k in range(-6, 7):
        p.append(f'<line x1="{cx + k * r * 0.11}" y1="{cy - r * 0.72}" x2="{cx + k * r * 0.11}" y2="{cy + r * 0.72}" '
                 f'stroke="#00000030" stroke-width="{r * 0.012}"/>')
        p.append(f'<line x1="{cx - r * 0.72}" y1="{cy + k * r * 0.11}" x2="{cx + r * 0.72}" y2="{cy + k * r * 0.11}" '
                 f'stroke="#00000030" stroke-width="{r * 0.012}"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.74}" fill="none" stroke="{STEEL}" stroke-width="{r * 0.03}"/>')
    p.append(f'<g transform="translate({cx} {cy})">{_markers(r * 0.85, "bars", "#FFF")}{_hands(r * 0.85, (10, 10), "#FFF")}</g>')
    return "".join(p)


def digital(cx, cy, w, h, *, style="lcd", text="10:58"):
    """style: led（赤い LED・金ケース）/ lcd（細身）/ tough（ゴツい樹脂）"""
    p = []
    if style == "led":
        p.append(f'<rect x="{cx - w * 0.3}" y="{cy - h * 1.3}" width="{w * 0.6}" height="{h * 2.6}" rx="{w * 0.05}" fill="{GOLD}"/>')
        p.append(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="{h * 0.35}" fill="{GOLD}" stroke="#A67C2A" stroke-width="{w * 0.015}"/>')
        p.append(f'<rect x="{cx - w * 0.38}" y="{cy - h * 0.32}" width="{w * 0.76}" height="{h * 0.64}" rx="{h * 0.12}" fill="#120606"/>')
        p.append(f'<text x="{cx}" y="{cy + h * 0.15}" text-anchor="middle" font-family="monospace" font-size="{h * 0.42}" '
                 f'font-weight="700" fill="#FF3B30">{text}</text>')
    elif style == "tough":
        p.append(f'<rect x="{cx - w * 0.32}" y="{cy - h * 1.35}" width="{w * 0.64}" height="{h * 2.7}" rx="{w * 0.08}" fill="#1B1B1F"/>')
        for sy in (-1, 1):
            for k in range(4):
                p.append(f'<rect x="{cx - w * 0.22}" y="{cy + sy * (h * 0.75 + k * h * 0.13) - h * 0.03}" width="{w * 0.44}" '
                         f'height="{h * 0.05}" fill="#2E2E36"/>')
        p.append(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="{w * 0.18}" fill="#26262C" stroke="#111" stroke-width="{w * 0.02}"/>')
        for sx in (-1, 1):
            for sy in (-1, 1):
                p.append(f'<rect x="{cx + sx * w * 0.52 - w * 0.05}" y="{cy + sy * h * 0.28 - h * 0.06}" width="{w * 0.1}" height="{h * 0.12}" rx="{w * 0.02}" fill="#111"/>')
        p.append(f'<rect x="{cx - w * 0.36}" y="{cy - h * 0.3}" width="{w * 0.72}" height="{h * 0.6}" rx="{w * 0.05}" fill="#9EB09A"/>')
        p.append(f'<text x="{cx}" y="{cy + h * 0.15}" text-anchor="middle" font-family="monospace" font-size="{h * 0.36}" '
                 f'font-weight="700" fill="#1E2A1E">{text}</text>')
        p.append(f'<rect x="{cx - w * 0.36}" y="{cy - h * 0.46}" width="{w * 0.72}" height="{h * 0.1}" rx="{h * 0.03}" fill="#C8432F"/>')
    else:
        p.append(f'<rect x="{cx - w * 0.3}" y="{cy - h * 1.3}" width="{w * 0.6}" height="{h * 2.6}" rx="{w * 0.05}" fill="#2A2A30"/>')
        p.append(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="{w * 0.08}" fill="#3A3A42"/>')
        p.append(f'<rect x="{cx - w * 0.38}" y="{cy - h * 0.3}" width="{w * 0.76}" height="{h * 0.6}" rx="{w * 0.04}" fill="#B9C4B0"/>')
        p.append(f'<text x="{cx}" y="{cy + h * 0.14}" text-anchor="middle" font-family="monospace" font-size="{h * 0.36}" '
                 f'font-weight="700" fill="#1E2A1E">{text}</text>')
    return "".join(p)


def pocket(cx, cy, r, case=GOLD):
    p = [f'<path d="M{cx} {cy - r * 1.25} q{r * 0.6} {r * 0.3} {r * 1.2} {r * 1.6} t{r * 0.4} {r * 1.4}" stroke="#B8862E" '
         f'stroke-width="{r * 0.04}" fill="none" stroke-dasharray="{r * 0.06} {r * 0.04}"/>',
         f'<circle cx="{cx}" cy="{cy - r * 1.22}" r="{r * 0.16}" fill="none" stroke="{case}" stroke-width="{r * 0.06}"/>',
         f'<rect x="{cx - r * 0.1}" y="{cy - r * 1.12}" width="{r * 0.2}" height="{r * 0.16}" rx="{r * 0.03}" fill="{case}"/>',
         analog(cx, cy, r, case=case, dial="#FBF7EC", ink="#2A2A2A", markers="roman", strap=None)]
    return "".join(p)


def plastic(cx, cy, r, color="#FF5A8A", strap="#3FB6E8"):
    return (f'<rect x="{cx - r * 0.45}" y="{cy - r * 1.7}" width="{r * 0.9}" height="{r * 3.4}" rx="{r * 0.2}" fill="{strap}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 1.08}" fill="{color}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.88}" fill="#FFF"/>'
            f'<g transform="translate({cx} {cy})">'
            + "".join(f'<circle cx="0" cy="{-r * 0.72}" r="{r * 0.07}" fill="{["#FFC83A", "#3FB6E8", "#7AD36B", "#FF5A8A"][i % 4]}" '
                      f'transform="rotate({i * 30})"/>' for i in range(12))
            + _hands(r, (10, 10), "#222", "#FF5A8A") + '</g>')


def movement(cx, cy, r):
    """裏から見たムーブメント。歯車と赤いルビー（石）"""
    p = [f'<circle cx="{cx}" cy="{cy}" r="{r * 1.06}" fill="{STEEL}"/>', f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#C8B68A"/>']
    for k in range(-8, 9):
        p.append(f'<path d="M{cx - r} {cy + k * r * 0.12} Q{cx} {cy + k * r * 0.12 - r * 0.06} {cx + r} {cy + k * r * 0.12}" '
                 f'stroke="#B8A578" stroke-width="{r * 0.02}" fill="none" opacity="0.6"/>')

    def gear(x, y, gr, teeth, color):
        t = "".join(f'<rect x="{-gr * 0.08}" y="{-gr * 1.12}" width="{gr * 0.16}" height="{gr * 0.2}" fill="{color}" '
                    f'transform="rotate({i * 360 / teeth})"/>' for i in range(teeth))
        return (f'<g transform="translate({x} {y})">{t}<circle r="{gr}" fill="{color}"/>'
                f'<circle r="{gr * 0.7}" fill="none" stroke="#00000025" stroke-width="{gr * 0.06}"/>'
                f'<circle r="{gr * 0.14}" fill="#C8102E"/></g>')
    p.append(gear(cx - r * 0.35, cy - r * 0.25, r * 0.32, 24, GOLD))
    p.append(gear(cx + r * 0.3, cy - r * 0.35, r * 0.22, 18, "#E2C27A"))
    p.append(gear(cx + r * 0.25, cy + r * 0.35, r * 0.3, 22, GOLD))
    p.append(f'<circle cx="{cx - r * 0.4}" cy="{cy + r * 0.45}" r="{r * 0.26}" fill="none" stroke="#8E949C" stroke-width="{r * 0.03}"/>')
    p.append(f'<path d="M{cx - r * 0.4} {cy + r * 0.45} m{-r * 0.15} 0 a{r * 0.15} {r * 0.15} 0 1 1 {r * 0.3} 0 '
             f'a{r * 0.1} {r * 0.1} 0 1 1 {-r * 0.2} 0" stroke="#5B6470" stroke-width="{r * 0.015}" fill="none"/>')
    for x, y in ((0.6, 0.1), (-0.65, -0.05), (0.05, 0.65), (-0.05, -0.68), (0.55, -0.6), (-0.2, 0.15)):
        p.append(f'<circle cx="{cx + x * r}" cy="{cy + y * r}" r="{r * 0.05}" fill="#C8102E" stroke="#F2C9C9" stroke-width="{r * 0.01}"/>')
    return "".join(p)


def watch(kind, cx, cy, r, **kw):
    """kind で時計を選ぶ。r はおおよその半径"""
    if kind == "chrono":
        return analog(cx, cy, r, bezel="#111", tachy=True, subdials=3, pushers=True, **kw)
    if kind == "diver":
        return analog(cx, cy, r, bezel=kw.pop("bezel", "#1B1B1F"), dive=True, markers="dots", lume=True,
                      strap="#B9BEC6", dial=kw.pop("dial", "#111"), **kw)
    if kind == "pilot":
        return analog(cx, cy, r, markers="pilot", strap="#5A3B22", **kw)
    if kind == "dress":
        return analog(cx, cy, r, case=GOLD, dial="#F6F1E6", ink="#2A2A2A", markers="roman", strap="#3A2A1A", **kw)
    if kind == "gold":
        return analog(cx, cy, r, case=GOLD, dial="#F3E7C9", ink="#3B2A1A", markers="bars", strap="#3A2A1A", **kw)
    if kind == "steel":
        return analog(cx, cy, r, dial="#F4F4F2", ink="#222", strap="#B9BEC6", **kw)
    if kind == "oyster":
        return analog(cx, cy, r, bezel="#D9DCE1", dial="#1B2A44", markers="bars", strap="#B9BEC6", **kw)
    if kind == "pocket":
        return pocket(cx, cy, r)
    if kind == "square":
        return square(cx, cy, r * 1.8, r * 1.8, dial="#1F4E8C", ink="#FFF", subdials=2, crown_left=True, strap="#1B1B1F")
    if kind == "santos":
        return square(cx, cy, r * 1.8, r * 1.8, screws=True, roman=True, strap="#3A2A1A")
    if kind == "reverso":
        return square(cx, cy, r * 1.4, r * 2.1, gadroons=True, roman=False, strap="#1B1B1F")
    if kind == "octagon":
        return octagon(cx, cy, r)
    if kind in ("led", "lcd", "tough"):
        return digital(cx, cy, r * 2.0, r * 1.5, style=kind, **kw)
    if kind == "plastic":
        return plastic(cx, cy, r, **kw)
    if kind == "movement":
        return movement(cx, cy, r)
    raise ValueError(kind)


# ---------- 時計以外 ----------

def earth(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#3A7BD5"/>'
            f'<path d="M{cx - r * 0.6} {cy - r * 0.3} q{r * 0.3} {-r * 0.4} {r * 0.6} {-r * 0.1} '
            f'q{r * 0.2} {r * 0.3} {-r * 0.1} {r * 0.5} q{-r * 0.4} {r * 0.1} {-r * 0.5} {-r * 0.4}Z" fill="#4CAF6A"/>'
            f'<path d="M{cx + r * 0.2} {cy + r * 0.2} q{r * 0.4} {-r * 0.1} {r * 0.5} {r * 0.3} '
            f'q{-r * 0.2} {r * 0.4} {-r * 0.5} {r * 0.1}Z" fill="#4CAF6A"/>'
            f'<path d="M{cx - r * 0.8} {cy + r * 0.1} q{r * 0.5} {-r * 0.15} {r * 1.0} {0}" '
            f'stroke="#FFF" stroke-width="{r * 0.08}" fill="none" stroke-linecap="round" opacity="0.8"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#9FD0FF" stroke-width="{r * 0.06}" opacity="0.6"/>')


def lunar_module(x, y, s):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            '<path d="M-90 40 L-150 150 M90 40 L150 150 M-50 40 L-80 150 M50 40 L80 150" stroke="#9AA0A8" stroke-width="8"/>'
            '<ellipse cx="-150" cy="152" rx="24" ry="7" fill="#9AA0A8"/><ellipse cx="150" cy="152" rx="24" ry="7" fill="#9AA0A8"/>'
            '<ellipse cx="-80" cy="152" rx="20" ry="6" fill="#9AA0A8"/><ellipse cx="80" cy="152" rx="20" ry="6" fill="#9AA0A8"/>'
            '<path d="M-100 -20 H100 L110 60 H-110 Z" fill="#D9A93A"/>'
            '<path d="M-60 -20 L-55 60 M0 -20 V60 M60 -20 L55 60" stroke="#B5862A" stroke-width="4"/>'
            '<path d="M-70 -20 L-60 -110 L20 -130 L75 -95 L80 -20 Z" fill="#C9CDD4"/>'
            '<path d="M-40 -95 L-10 -105 L-15 -70 Z M10 -105 L40 -95 L15 -70 Z" fill="#2A2F3A"/>'
            '<rect x="-5" y="-150" width="10" height="25" fill="#9AA0A8"/></g>')


def race_car(x, y, s, color="#D83A2E", number="7"):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-170 0 Q-170 -45 -110 -50 L60 -55 Q150 -55 180 -15 Q190 10 170 20 L-160 20 Q-175 15 -170 0Z" fill="{color}"/>'
            '<path d="M-150 -10 H160" stroke="#FFF" stroke-width="6" opacity="0.7"/>'
            '<ellipse cx="-10" cy="-55" rx="40" ry="16" fill="#222"/>'
            '<circle cx="-10" cy="-72" r="22" fill="#F4F4F4"/><rect x="-6" y="-80" width="24" height="10" rx="4" fill="#2A2F3A"/>'
            '<circle cx="70" cy="-18" r="24" fill="#FFF"/>'
            f'<text x="70" y="-6" text-anchor="middle" font-family="{FONT}" font-size="34" font-weight="900" fill="#222">{number}</text>'
            '<circle cx="-110" cy="25" r="38" fill="#1B1B1F"/><circle cx="-110" cy="25" r="15" fill="#CCC"/>'
            '<circle cx="110" cy="25" r="38" fill="#1B1B1F"/><circle cx="110" cy="25" r="15" fill="#CCC"/>'
            '<path d="M-200 -30 H-250 M-210 0 H-280 M-200 25 H-240" stroke="#FFF" stroke-width="6" stroke-linecap="round" opacity="0.8"/>'
            '</g>')


def small_watch(x, y, s, fill="#F2F2F2"):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            '<rect x="-14" y="-60" width="28" height="120" rx="6" fill="#3A2A1A"/>'
            f'<circle r="30" fill="#C9CDD4"/><circle r="24" fill="{fill}"/>'
            '<path d="M0 0 V-16 M0 0 L10 6" stroke="#222" stroke-width="3" stroke-linecap="round"/></g>')


def cloud(x, y, s, color="#FFF", opacity=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})" fill="{color}" opacity="{opacity}">'
            '<ellipse cx="0" cy="0" rx="90" ry="40"/><circle cx="-40" cy="-20" r="40"/><circle cx="25" cy="-35" r="50"/>'
            '<circle cx="70" cy="-5" r="35"/></g>')


def biplane(x, y, s, color="#E8B23A"):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<rect x="-120" y="-70" width="240" height="18" rx="9" fill="{color}"/>'
            f'<rect x="-120" y="10" width="240" height="18" rx="9" fill="{color}"/>'
            '<path d="M-70 -52 V10 M70 -52 V10" stroke="#5A3B22" stroke-width="6"/>'
            f'<path d="M-150 -10 Q-150 -40 -100 -40 H110 Q150 -35 160 -10 Q150 15 110 15 H-100 Q-150 15 -150 -10Z" fill="{color}" '
            'stroke="#B5862A" stroke-width="4"/>'
            '<path d="M160 -10 m0 -45 v90" stroke="#555" stroke-width="8" stroke-linecap="round"/>'
            '<path d="M-150 -10 L-200 -60 L-185 -10 Z" fill="#C8432F"/>'
            '<circle cx="-20" cy="-48" r="18" fill="#5A3B22"/><rect x="-30" y="-58" width="26" height="9" rx="4" fill="#9FD0FF"/>'
            '</g>')


def airship(x, y, s):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            '<ellipse cx="0" cy="0" rx="220" ry="62" fill="#F2E3C2" stroke="#B59A6A" stroke-width="5"/>'
            '<path d="M-150 -40 Q0 -70 150 -40 M-150 40 Q0 70 150 40 M-200 0 H200" stroke="#D6C29A" stroke-width="4" fill="none"/>'
            '<path d="M-215 0 L-270 -50 L-260 0 L-270 50 Z" fill="#C8432F"/>'
            '<path d="M-60 62 L-50 110 H50 L60 62" stroke="#5A3B22" stroke-width="3" fill="none"/>'
            '<rect x="-50" y="105" width="100" height="22" rx="6" fill="#8B5A2B"/>'
            '<circle cx="0" cy="98" r="10" fill="#1B1B1F"/></g>')


def eiffel(x, y, s, color="#3A2A4A"):
    return (f'<g transform="translate({x} {y}) scale({s})" fill="{color}">'
            '<path d="M-150 0 Q-60 -150 -30 -400 L-12 -700 L0 -760 L12 -700 L30 -400 Q60 -150 150 0 H90 Q40 -110 0 -110 Q-40 -110 -90 0Z"/>'
            '<rect x="-80" y="-260" width="160" height="22"/><rect x="-45" y="-480" width="90" height="16"/></g>')


def gavel(x, y, s):
    return (f'<g transform="translate({x} {y}) scale({s}) rotate(-30)">'
            '<rect x="-12" y="-20" width="24" height="200" rx="10" fill="#8B5A2B"/>'
            '<rect x="-80" y="-70" width="160" height="70" rx="18" fill="#6B4320"/>'
            '<rect x="-90" y="-70" width="20" height="70" rx="6" fill="#D4A24C"/><rect x="70" y="-70" width="20" height="70" rx="6" fill="#D4A24C"/></g>')
