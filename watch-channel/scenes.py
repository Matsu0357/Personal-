"""背景シーン。各関数は (svg 文字列, キャラ位置 (x, y, scale)) を返す。

画面は 1080x1920。上 340px はヘッダー、下 1360px 以降は字幕なので、絵の主役はその間に置く。
"""
import random

from props import (FONT, SERIF, airship, biplane, cloud, earth, eiffel, gavel, lunar_module, race_car,
                   small_watch, watch)

W, H = 1080, 1920
DEFAULT_POS = (300, 960, 1.0)
CORNER_POS = (210, 1090, 0.72)


def _vgrad(gid, top, bottom):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{bottom}"/></linearGradient><rect width="{W}" height="{H}" fill="url(#{gid})"/>')


def _stars(n, seed, y_max):
    rnd = random.Random(seed)
    return "".join(
        f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, y_max):.0f}" '
        f'r="{rnd.choice([1.5, 2, 2.5, 3.5])}" fill="#FFF" opacity="{rnd.uniform(0.4, 1):.2f}"/>'
        for _ in range(n))


def _text(x, y, s, size, color="#3B2A1A", weight=900, stroke=None, family=FONT, anchor="middle"):
    st = f' stroke="{stroke}" stroke-width="{size * 0.12:.0f}" paint-order="stroke"' if stroke else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{st}>{s}</text>')


def _fit(s, width, max_size):
    """全角幅で文字を詰めたときに width に収まるフォントサイズ"""
    units = sum(0.6 if ord(c) < 0x2000 else 1.0 for c in s)
    return min(max_size, int(width / max(units, 1)))


# ---------- 宇宙・月 ----------

def moon(lm=False):
    p = [_vgrad("sky", "#070A20", "#1E2A5A"), _stars(110, 1, 1150), earth(830, 560, 110)]
    if lm:
        p.append(lunar_module(250, 1060, 0.9))
    p.append('<path d="M0 1190 Q270 1150 540 1180 T1080 1170 V1920 H0 Z" fill="#B9BCC6"/>')
    for cx, cy, rx in ((150, 1450, 70), (760, 1300, 50), (880, 1700, 90), (420, 1820, 60), (980, 1240, 30)):
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx * 0.3}" fill="#9EA2AD"/>')
    return "".join(p), ((640, 950, 1.0) if lm else DEFAULT_POS)


def space(timer=None):
    p = ['<radialGradient id="alert" cx="0.5" cy="0.5" r="0.75"><stop offset="0.55" stop-color="#FF2A2A" stop-opacity="0"/>'
         '<stop offset="1" stop-color="#FF2A2A" stop-opacity="0.45"/></radialGradient>',
         f'<rect width="{W}" height="{H}" fill="#05060F"/>', _stars(120, 3, 1920), earth(170, 640, 70),
         '<g transform="translate(700 760) rotate(-18)">'
         '<rect x="-70" y="-60" width="140" height="260" rx="8" fill="#D8DCE2"/>'
         '<path d="M-70 -10 H70 M-70 60 H70 M-70 130 H70" stroke="#AEB4BC" stroke-width="5"/>'
         '<rect x="15" y="20" width="50" height="90" fill="#2A2F3A"/>'
         '<circle cx="80" cy="50" r="30" fill="#FFF" opacity="0.6"/><circle cx="115" cy="30" r="22" fill="#FFF" opacity="0.45"/>'
         '<circle cx="140" cy="0" r="16" fill="#FFF" opacity="0.3"/>'
         '<path d="M-70 -60 L-20 -170 Q0 -185 20 -170 L70 -60 Z" fill="#E6E9ED"/>'
         '<path d="M-45 200 L-60 260 H60 L45 200 Z" fill="#7A808A"/></g>',
         f'<rect width="{W}" height="{H}" fill="url(#alert)"/>']
    if timer:
        p.append('<rect x="290" y="390" width="500" height="170" rx="20" fill="#120808" stroke="#FF4A3D" stroke-width="6"/>')
        p.append(_text(540, 515, timer, 130, "#FF4A3D", 700, family="monospace"))
    return "".join(p), (300, 1010, 0.9)


# ---------- 時計を主役に ----------

def hero(watch_kind="chrono", **kw):
    p = ['<radialGradient id="spot" cx="0.5" cy="0.38" r="0.6"><stop offset="0" stop-color="#4A4A78"/>'
         '<stop offset="1" stop-color="#14142A"/></radialGradient>',
         f'<rect width="{W}" height="{H}" fill="url(#spot)"/>', _stars(40, 7, 1900), watch(watch_kind, 560, 810, 215, **kw)]
    return "".join(p), (220, 1080, 0.75)


def workshop(title=None, watch_kind="chrono"):
    p = [_vgrad("wall", "#5A3B22", "#7A5233")]
    for i in range(1, 9):
        p.append(f'<line x1="{i * 135}" y1="0" x2="{i * 135}" y2="1180" stroke="#4A2F1A" stroke-width="4" opacity="0.6"/>')
    p.append('<radialGradient id="lamp" cx="0.7" cy="0.55" r="0.5"><stop offset="0" stop-color="#FFE9B0" stop-opacity="0.55"/>'
             '<stop offset="1" stop-color="#FFE9B0" stop-opacity="0"/></radialGradient>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#lamp)"/>')
    if title:
        p.append(_text(540, 560, title, _fit(title, 960, 118), "#F2C14E", stroke="#3B2410"))
    p.append('<rect x="0" y="1180" width="1080" height="740" fill="#9A6A3C"/>')
    p.append('<rect x="0" y="1180" width="1080" height="24" fill="#B98552"/>')
    p.append('<path d="M760 1180 L800 1060 H880 L920 1180 Z" fill="#3A2A1A"/>')
    p.append(watch(watch_kind, 840, 960, 95))
    return "".join(p), (360, 900, 1.05)


def store():
    p = [_vgrad("wall", "#F3E9DA", "#E2D3BC"),
         '<rect x="0" y="380" width="1080" height="60" fill="#8B5A2B"/>',
         _text(540, 425, "WATCH SHOP", 40, "#F2E3C2", 800, family=SERIF),
         '<rect x="80" y="520" width="920" height="300" rx="14" fill="#6B4320"/>',
         '<rect x="100" y="540" width="880" height="260" rx="10" fill="#CFE6F2" opacity="0.6"/>']
    kinds = ["dress", "diver", "chrono", "pilot", "gold"]
    for i, k in enumerate(kinds):
        p.append(watch(k, 190 + i * 175, 670, 48))
    p += ['<rect x="0" y="1150" width="1080" height="770" fill="#B98552"/>',
          '<rect x="420" y="980" width="660" height="200" rx="10" fill="#6B4320"/>',
          '<rect x="440" y="1000" width="620" height="120" rx="8" fill="#CFE6F2" opacity="0.6"/>',
          watch("steel", 600, 1060, 40), watch("oyster", 760, 1060, 40), watch("tough", 920, 1060, 26)]
    return "".join(p), DEFAULT_POS


# ---------- 文字カード ----------

def card(big, sub=None, theme="paper"):
    bg, fg, sc = {"paper": ("#FFF4E0", "#3B2A1A", "#8B5A2B"), "dark": ("#14142A", "#F2C14E", "#E8E0C8"),
                  "red": ("#3A0D0D", "#FF6A5A", "#F2D6D0")}[theme]
    p = [f'<rect width="{W}" height="{H}" fill="{bg}"/>',
         f'<rect x="70" y="430" width="940" height="560" rx="40" fill="none" stroke="{sc}" stroke-width="6" stroke-dasharray="18 14"/>',
         _text(540, 760 if sub else 790, big, _fit(big, 860, 230), fg)]
    if sub:
        p.append(_text(540, 900, sub, _fit(sub, 860, 60), sc, 800))
    return "".join(p), CORNER_POS


def versus(l_big, l_sub, r_big, r_sub):
    p = [f'<rect width="{W}" height="{H}" fill="#FFF4E0"/>']
    for x, big, sub, col in ((60, l_big, l_sub, "#3A7BD5"), (560, r_big, r_sub, "#D83A2E")):
        p.append(f'<rect x="{x}" y="440" width="460" height="520" rx="30" fill="{col}"/>')
        p.append(_text(x + 230, 680, big, _fit(big, 400, 120), "#FFF"))
        p.append(_text(x + 230, 800, sub, _fit(sub, 400, 48), "#FFF", 700))
    p.append('<circle cx="540" cy="700" r="70" fill="#1B1B1F"/>')
    p.append(_text(540, 728, "VS", 72, "#F2C14E"))
    return "".join(p), (540, 1090, 0.62)


def graph(direction="down", label=""):
    pts = ([(150, 520), (300, 540), (450, 620), (600, 780), (750, 900), (900, 950)] if direction == "down"
           else [(150, 950), (300, 900), (450, 860), (600, 720), (750, 600), (900, 500)])
    col = "#D83A2E" if direction == "down" else "#2E9E5B"
    path = "M" + " L".join(f"{x} {y}" for x, y in pts)
    p = [f'<rect width="{W}" height="{H}" fill="#FFF4E0"/>',
         '<path d="M120 440 V1000 H960" stroke="#3B2A1A" stroke-width="8" fill="none" stroke-linecap="round"/>',
         f'<path d="{path}" stroke="{col}" stroke-width="18" fill="none" stroke-linecap="round" stroke-linejoin="round"/>']
    x, y = pts[-1]
    px, py = pts[-2]
    p.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{col}"/>')
    if label:
        p.append(_text(560 if direction == "down" else 400, 470 if direction == "down" else 1000 - 40, label,
                       _fit(label, 700, 72), col))
    return "".join(p), CORNER_POS


def newspaper(headline, sub=None):
    p = [_vgrad("desk", "#8B5A2B", "#6B4320"),
         '<g transform="rotate(-4 540 840)">',
         '<rect x="110" y="410" width="860" height="860" fill="#F4EEDD"/>',
         _text(540, 490, "THE DAILY NEWS", 58, "#222", 700, family=SERIF),
         '<path d="M150 515 H930 M150 525 H930" stroke="#222" stroke-width="3"/>',
         _text(540, 640, headline, _fit(headline, 760, 96), "#111")]
    if sub:
        p.append(_text(540, 720, sub, _fit(sub, 760, 44), "#333", 700))
    p.append('<rect x="150" y="770" width="380" height="300" fill="#CFC6B0"/>')
    p.append(watch("oyster", 340, 920, 80))
    for k in range(10):
        p.append(f'<rect x="570" y="{780 + k * 30}" width="{360 if k % 4 else 280}" height="12" fill="#B9B09A"/>')
    for k in range(5):
        p.append(f'<rect x="150" y="{1100 + k * 30}" width="{780 if k % 3 else 600}" height="12" fill="#B9B09A"/>')
    p.append('</g>')
    return "".join(p), CORNER_POS


# ---------- 場所 ----------

def race():
    p = [_vgrad("sky", "#7EC8F5", "#E8F6FF"),
         '<circle cx="860" cy="430" r="80" fill="#FFE27A"/>',
         '<path d="M0 900 Q250 780 520 880 T1080 850 V1000 H0Z" fill="#7CC07A"/>',
         '<rect x="0" y="960" width="1080" height="120" fill="#5E6A7A"/>']
    for i in range(12):
        p.append(f'<rect x="{i * 92 + 6}" y="975" width="80" height="22" rx="4" fill="{["#E8505B", "#F5C452", "#4FA3E0"][i % 3]}"/>')
        p.append(f'<rect x="{i * 92 + 6}" y="1015" width="80" height="22" rx="4" fill="{["#F5C452", "#4FA3E0", "#E8505B"][i % 3]}"/>')
    p.append('<rect x="0" y="1080" width="1080" height="840" fill="#8BC27F"/>')
    p.append('<path d="M0 1120 H1080 V1460 H0Z" fill="#4A4E57"/>')
    p.append('<path d="M0 1290 H1080" stroke="#FFF" stroke-width="10" stroke-dasharray="60 50"/>')
    p.append('<line x1="90" y1="1120" x2="90" y2="760" stroke="#555" stroke-width="10"/>')
    for r in range(4):
        for c in range(6):
            if (r + c) % 2 == 0:
                p.append(f'<rect x="{95 + c * 25}" y="{760 + r * 25}" width="25" height="25" fill="#111"/>')
    p.append('<rect x="95" y="760" width="150" height="100" fill="none" stroke="#111" stroke-width="3"/>')
    p.append(race_car(780, 1225, 0.95))
    return "".join(p), (330, 960, 0.95)


def lab(readout="93°C"):
    p = [f'<rect width="{W}" height="{H}" fill="#DCE3EB"/>',
         '<rect x="0" y="1250" width="1080" height="670" fill="#AEB8C4"/>',
         '<path d="M0 1250 H1080" stroke="#8E99A6" stroke-width="6"/>',
         '<rect x="560" y="520" width="440" height="620" rx="24" fill="#8E99A6"/>',
         '<rect x="580" y="540" width="400" height="580" rx="16" fill="#C7CFD8"/>',
         '<radialGradient id="heat" cx="0.5" cy="0.6" r="0.7"><stop offset="0" stop-color="#FFD27A"/>'
         '<stop offset="1" stop-color="#FF6A3D"/></radialGradient>',
         '<rect x="620" y="600" width="320" height="300" rx="12" fill="url(#heat)" stroke="#5E6A7A" stroke-width="10"/>',
         small_watch(690, 760, 0.9), small_watch(780, 740, 0.9, "#FFF6D8"), small_watch(870, 770, 0.9, "#1B1B1F"),
         '<circle cx="780" cy="490" r="26" fill="#FF4A3D"/><circle cx="780" cy="490" r="40" fill="#FF4A3D" opacity="0.25"/>',
         '<rect x="630" y="960" width="300" height="110" rx="10" fill="#2A2F3A"/>',
         _text(780, 1035, readout, _fit(readout, 270, 64), "#FF6A3D", 700, family="monospace"),
         '<rect x="1010" y="600" width="30" height="380" rx="15" fill="#FFF" stroke="#5E6A7A" stroke-width="4"/>',
         '<rect x="1017" y="700" width="16" height="270" rx="8" fill="#FF4A3D"/>',
         '<circle cx="1025" cy="985" r="26" fill="#FF4A3D"/>']
    return "".join(p), (280, 960, 1.0)


def sea():
    p = [_vgrad("sky", "#9FD3F2", "#E6F4FB"),
         cloud(780, 520, 1.0), cloud(260, 640, 0.7, opacity=0.8),
         '<path d="M0 760 L120 740 L200 780 L260 770 L300 900 H0 Z" fill="#F4F1E8"/>',
         '<path d="M0 760 L120 740 L200 780 L260 770 L300 900" stroke="#C9C2AE" stroke-width="6" fill="none"/>',
         '<path d="M0 790 Q60 780 120 800 M40 830 Q120 820 200 840" stroke="#DCD5C2" stroke-width="5" fill="none"/>',
         '<rect x="0" y="880" width="1080" height="1040" fill="#2F7FB8"/>']
    for k in range(9):
        y = 930 + k * 55
        p.append(f'<path d="M0 {y} q45 -18 90 0 t90 0 t90 0 t90 0 t90 0 t90 0 t90 0 t90 0 t90 0 t90 0 t90 0 t90 0" '
                 f'stroke="#9FD3F2" stroke-width="5" fill="none" opacity="0.5"/>')
    p += ['<g transform="translate(760 1010)">',
          '<ellipse cx="0" cy="10" rx="90" ry="16" fill="#FFF" opacity="0.6"/>',
          '<circle cx="0" cy="-10" r="30" fill="#F2D2B6"/><path d="M-30 -14 A30 30 0 0 1 30 -14 Z" fill="#E8505B"/>',
          '<path d="M30 0 Q80 -70 120 -20" stroke="#F2D2B6" stroke-width="16" fill="none" stroke-linecap="round"/>',
          '<rect x="104" y="-40" width="26" height="14" rx="4" fill="#C9CDD4" transform="rotate(30 117 -33)"/></g>',
          '<path d="M140 1180 Q300 1240 460 1180 L440 1150 H160 Z" fill="#8B5A2B"/>']
    return "".join(p), (300, 920, 0.85)


def underwater():
    p = [_vgrad("water", "#2E8FC9", "#0A2A55")]
    for x in (200, 450, 700, 950):
        p.append(f'<path d="M{x} 0 L{x - 120} 1400 L{x + 20} 1400 Z" fill="#FFF" opacity="0.06"/>')
    rnd = random.Random(5)
    for _ in range(30):
        p.append(f'<circle cx="{rnd.uniform(350, 1000):.0f}" cy="{rnd.uniform(380, 1300):.0f}" r="{rnd.choice([6, 9, 12, 16])}" '
                 'fill="none" stroke="#CFEFFF" stroke-width="3" opacity="0.7"/>')
    for x in (620, 900, 980):
        p.append(f'<path d="M{x} 1340 q-30 -80 0 -160 q30 -80 0 -160" stroke="#2E9E5B" stroke-width="18" fill="none" stroke-linecap="round"/>')
    for x, y, c in ((760, 640, "#FFC83A"), (900, 820, "#FF7A59"), (680, 980, "#FFC83A")):
        p.append(f'<g transform="translate({x} {y})"><ellipse rx="44" ry="24" fill="{c}"/><path d="M40 0 L72 -22 V22Z" fill="{c}"/>'
                 '<circle cx="-22" cy="-6" r="5" fill="#111"/></g>')
    p.append('<path d="M0 1300 Q300 1250 600 1300 T1080 1290 V1920 H0Z" fill="#C9B27A"/>')
    return "".join(p), (300, 960, 1.0)


def sky():
    p = [_vgrad("sky", "#5FB4EC", "#D6EEFB"), cloud(820, 470, 1.1), cloud(160, 520, 0.8, opacity=0.9),
         cloud(950, 1100, 0.9, opacity=0.9), biplane(640, 720, 1.0),
         cloud(300, 1260, 2.2)]
    return "".join(p), (300, 960, 1.0)


def paris():
    p = [_vgrad("dusk", "#F7A86B", "#F7D9B5"), '<circle cx="300" cy="900" r="120" fill="#FFE6A8" opacity="0.8"/>',
         eiffel(820, 1250, 1.0), airship(430, 620, 0.85)]
    rnd = random.Random(9)
    x = 0
    while x < 1080:
        w, h = rnd.randint(110, 170), rnd.randint(150, 260)
        p.append(f'<rect x="{x}" y="{1250 - h}" width="{w}" height="{h}" fill="#7A5A7A"/>')
        p.append(f'<path d="M{x - 6} {1250 - h} L{x + w / 2} {1250 - h - 40} L{x + w + 6} {1250 - h}Z" fill="#5E4460"/>')
        for wy in range(1250 - h + 30, 1230, 60):
            for wx in range(x + 20, x + w - 25, 40):
                p.append(f'<rect x="{wx}" y="{wy}" width="16" height="26" fill="#FFE6A8" opacity="0.8"/>')
        x += w
    p.append('<rect x="0" y="1250" width="1080" height="670" fill="#B49A86"/>')
    return "".join(p), (300, 980, 0.95)


def mountains():
    p = [_vgrad("sky", "#A8D8F5", "#EEF7FC"),
         '<path d="M0 900 L220 560 L380 760 L560 470 L760 780 L900 600 L1080 820 V1100 H0Z" fill="#8FA7BF"/>',
         '<path d="M220 560 L270 640 L240 630 L200 660 L175 630Z M560 470 L620 560 L585 550 L550 580 L515 540Z '
         'M900 600 L945 670 L915 660 L880 690Z" fill="#FFF"/>',
         '<path d="M0 1000 Q300 900 600 980 T1080 960 V1920 H0Z" fill="#7CC07A"/>',
         '<g transform="translate(760 1010)">',
         '<rect x="-180" y="-120" width="360" height="200" fill="#F2E3C2"/>',
         '<path d="M-210 -110 L0 -260 L210 -110Z" fill="#8B5A2B"/>']
    for wx in range(-150, 160, 60):
        p.append(f'<rect x="{wx}" y="-80" width="36" height="44" fill="#9FD0FF" stroke="#8B5A2B" stroke-width="4"/>')
    p.append('<rect x="-30" y="0" width="60" height="80" fill="#6B4320"/></g>')
    for x in (60, 130, 950, 1020):
        p.append(f'<path d="M{x} 1080 l-45 0 l45 -160 l45 160Z" fill="#2E7D4F"/>')
    return "".join(p), (300, 980, 0.95)


def ginza():
    p = [_vgrad("sky", "#F5C27A", "#FBE7C6"),
         '<rect x="520" y="800" width="480" height="450" fill="#E9DCC6" stroke="#B59A6A" stroke-width="6"/>',
         '<rect x="680" y="560" width="160" height="250" fill="#E9DCC6" stroke="#B59A6A" stroke-width="6"/>',
         '<path d="M670 560 Q760 470 850 560Z" fill="#7A8C7A"/>',
         '<circle cx="760" cy="650" r="58" fill="#FFF" stroke="#3B2A1A" stroke-width="6"/>',
         '<path d="M760 650 V610 M760 650 L790 662" stroke="#3B2A1A" stroke-width="6" stroke-linecap="round"/>']
    for wx in range(550, 980, 70):
        for wy in (850, 960, 1070):
            p.append(f'<rect x="{wx}" y="{wy}" width="40" height="70" rx="20" fill="#7A6A5A"/>')
    p += ['<rect x="0" y="1000" width="420" height="250" fill="#C9B79A"/>',
          '<path d="M-10 1000 L210 930 L430 1000Z" fill="#6B5A4A"/>',
          '<rect x="0" y="1250" width="1080" height="670" fill="#A89880"/>']
    for x in (470, 1040):
        p.append(f'<path d="M{x} 1250 V1060" stroke="#3B2A1A" stroke-width="8"/><circle cx="{x}" cy="1050" r="18" fill="#FFE6A8"/>')
    return "".join(p), (300, 980, 0.95)


def trench():
    p = [_vgrad("sky", "#8A8F98", "#C8CBD0"),
         '<path d="M0 950 Q300 900 600 960 T1080 930 V1920 H0Z" fill="#6B5A45"/>',
         '<circle cx="820" cy="760" r="90" fill="#9A9EA6" opacity="0.6"/><circle cx="900" cy="700" r="60" fill="#A8ACB3" opacity="0.5"/>']
    for k in range(9):
        p.append(f'<ellipse cx="{k * 130 + 40}" cy="1170" rx="72" ry="34" fill="#A08A62" stroke="#7A6748" stroke-width="4"/>')
        p.append(f'<ellipse cx="{k * 130 + 105}" cy="1120" rx="72" ry="34" fill="#B09A70" stroke="#7A6748" stroke-width="4"/>')
    p.append('<path d="M0 1030 L1080 1010" stroke="#555" stroke-width="3"/>')
    for x in range(20, 1080, 60):
        p.append(f'<path d="M{x} 1020 l12 -12 m-12 0 l12 12" stroke="#555" stroke-width="3"/>')
    return "".join(p), (330, 940, 0.95)


def factory():
    p = [_vgrad("sky", "#5E6670", "#9AA1AB"),
         '<rect x="520" y="620" width="480" height="560" fill="#7A808A"/>',
         '<path d="M520 620 L600 540 L680 620 L760 540 L840 620 L920 540 L1000 620Z" fill="#6A707A"/>',
         '<rect x="880" y="380" width="60" height="240" fill="#6A707A"/>']
    for wx in range(560, 980, 100):
        p.append(f'<rect x="{wx}" y="720" width="60" height="80" fill="#3A3F48"/>')
    p += ['<rect x="610" y="880" width="300" height="120" rx="8" fill="#F4EEDD" transform="rotate(-6 760 940)"/>',
          _text(760, 965, "CLOSED", 70, "#C8432F", 900).replace("<text", '<text transform="rotate(-6 760 940)"'),
          '<rect x="0" y="1180" width="1080" height="740" fill="#4E545C"/>',
          '<ellipse cx="740" cy="1250" rx="160" ry="20" fill="#6E7680" opacity="0.6"/>']
    rnd = random.Random(4)
    for _ in range(70):
        x, y = rnd.uniform(0, 1080), rnd.uniform(360, 1300)
        p.append(f'<path d="M{x:.0f} {y:.0f} l-8 26" stroke="#CFD6DE" stroke-width="3" opacity="0.6"/>')
    return "".join(p), (300, 980, 0.95)


def auction(price):
    p = [f'<rect width="{W}" height="{H}" fill="#3A1414"/>']
    for x in range(0, 1080, 90):
        p.append(f'<path d="M{x} 0 Q{x + 45} 40 {x + 90} 0 V1250 Q{x + 45} 1220 {x} 1250Z" fill="#8E1F1F" opacity="0.85"/>')
    p += ['<rect x="140" y="420" width="800" height="230" rx="20" fill="#14142A" stroke="#D4A24C" stroke-width="8"/>',
          _text(540, 580, price, _fit(price, 720, 130), "#F2C14E"),
          '<rect x="0" y="1180" width="1080" height="740" fill="#5A3B22"/>',
          '<path d="M620 1180 L660 860 H960 L1000 1180Z" fill="#6B4320"/>',
          '<rect x="640" y="840" width="340" height="40" rx="8" fill="#8B5A2B"/>',
          gavel(820, 760, 0.8), watch("chrono", 820, 1020, 70)]
    return "".join(p), (300, 960, 1.0)


def polo():
    p = [_vgrad("sky", "#8FCBF0", "#E9F6FC"), '<circle cx="880" cy="460" r="70" fill="#FFE27A"/>',
         '<rect x="0" y="900" width="1080" height="1020" fill="#5DAA4F"/>']
    for k in range(6):
        p.append(f'<rect x="0" y="{900 + k * 70}" width="1080" height="35" fill="#67B558"/>')
    p.append('<path d="M0 900 H1080" stroke="#FFF" stroke-width="10"/>')
    for x in range(30, 1080, 120):
        p.append(f'<rect x="{x}" y="860" width="10" height="44" fill="#FFF"/>')
    p += ['<path d="M640 1220 L900 700" stroke="#8B5A2B" stroke-width="16" stroke-linecap="round"/>',
          '<rect x="570" y="1200" width="140" height="44" rx="14" fill="#6B4320" transform="rotate(-25 640 1222)"/>',
          '<circle cx="800" cy="1230" r="34" fill="#FFF" stroke="#DDD" stroke-width="4"/>',
          '<path d="M880 1240 h50 M890 1210 h40" stroke="#FFF" stroke-width="6" stroke-linecap="round" opacity="0.8"/>',
          watch("reverso", 860, 560, 70)]
    return "".join(p), (300, 960, 1.0)


def cinema(screen=""):
    p = [f'<rect width="{W}" height="{H}" fill="#14101A"/>',
         '<path d="M540 300 L120 420 V900 L540 1000 L960 900 V420Z" fill="#FFF" opacity="0.05"/>',
         '<rect x="110" y="410" width="860" height="500" rx="10" fill="#F4F1EA"/>']
    if screen:
        p.append(_text(540, 700, screen, _fit(screen, 760, 150), "#14101A"))
    for row, y in enumerate((1080, 1200)):
        for x in range(-40 + row * 40, 1120, 140):
            p.append(f'<path d="M{x} {y + 120} V{y + 20} Q{x} {y} {x + 20} {y} H{x + 100} Q{x + 120} {y} {x + 120} {y + 20} V{y + 120}Z" '
                     'fill="#5A1E2A"/>')
    return "".join(p), (540, 980, 0.85)


def park():
    p = [_vgrad("sky", "#8FD3F7", "#E6F6FD"), cloud(800, 480, 0.9),
         '<path d="M0 980 Q300 930 600 970 T1080 960 V1920 H0Z" fill="#7CC07A"/>']
    for x, y, r in ((120, 820, 110), (960, 840, 130)):
        p.append(f'<rect x="{x - 18}" y="{y}" width="36" height="200" fill="#8B5A2B"/><circle cx="{x}" cy="{y - 40}" r="{r}" fill="#3E9A55"/>')
    p += ['<rect x="560" y="1120" width="300" height="20" rx="6" fill="#8B5A2B"/>',
          '<rect x="580" y="1140" width="14" height="60" fill="#5A3B22"/><rect x="826" y="1140" width="14" height="60" fill="#5A3B22"/>',
          '<path d="M600 760 Q660 620 720 760 Q760 860 800 1000" stroke="#FFF" stroke-width="5" fill="none" stroke-dasharray="14 12" opacity="0.8"/>',
          '<circle cx="800" cy="1040" r="46" fill="#FF7A59"/><path d="M760 1030 Q800 1000 840 1030" stroke="#FFF" stroke-width="6" fill="none"/>']
    return "".join(p), (300, 980, 0.95)


def building():
    p = [_vgrad("sky", "#8FCBF0", "#E9F6FC"), cloud(260, 480, 0.8),
         '<rect x="560" y="380" width="440" height="880" fill="#C9CFD8"/>']
    for wy in range(420, 1220, 140):
        for wx in (600, 740, 880):
            p.append(f'<rect x="{wx}" y="{wy}" width="90" height="90" fill="#8FB8D8"/>')
    p += ['<rect x="740" y="700" width="90" height="90" fill="#2A2F3A"/>',
          '<path d="M785 800 V1080" stroke="#3B2A1A" stroke-width="5" stroke-dasharray="16 14" opacity="0.6"/>',
          watch("tough", 785, 1110, 28),
          '<path d="M740 1080 l-30 -20 M830 1080 l30 -20" stroke="#3B2A1A" stroke-width="5" stroke-linecap="round"/>',
          '<rect x="0" y="1250" width="1080" height="670" fill="#9AA0A8"/>']
    return "".join(p), (300, 980, 0.95)


def palace():
    p = [_vgrad("wall", "#F2D6D0", "#E8C0B8")]
    for x in range(60, 1080, 240):
        p.append(f'<rect x="{x}" y="380" width="30" height="860" fill="#E8C877" opacity="0.7"/>')
    p += ['<path d="M540 380 V460" stroke="#B5862A" stroke-width="6"/>',
          '<path d="M400 520 Q540 600 680 520 L640 470 H440Z" fill="#E8C877"/>']
    for x in range(420, 680, 40):
        p.append(f'<circle cx="{x}" cy="{560 + (x % 80) / 4}" r="9" fill="#FFF6D8"/>')
    p += ['<rect x="560" y="660" width="380" height="460" rx="12" fill="#D4A24C"/>',
          '<rect x="590" y="690" width="320" height="400" fill="#7A3A4A"/>',
          '<path d="M690 760 L710 720 L730 760 L750 715 L770 760 L790 720 L810 760Z" fill="#E8C877"/>',
          '<circle cx="750" cy="880" r="70" fill="#F2D6D0"/><path d="M680 1090 Q750 960 820 1090Z" fill="#F2D6D0"/>',
          '<rect x="0" y="1250" width="1080" height="670" fill="#A02838"/>',
          '<path d="M0 1250 H1080" stroke="#E8C877" stroke-width="10"/>']
    return "".join(p), (300, 980, 0.95)


def night_desk(sketch="octagon"):
    p = [_vgrad("room", "#1C2340", "#2E3760"),
         '<rect x="620" y="420" width="360" height="420" rx="10" fill="#0E1430" stroke="#5A3B22" stroke-width="14"/>',
         '<path d="M800 420 V840 M620 630 H980" stroke="#5A3B22" stroke-width="10"/>',
         '<circle cx="890" cy="510" r="44" fill="#FFF6D0"/><circle cx="908" cy="498" r="40" fill="#0E1430"/>',
         "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#FFF" opacity="0.8"/>'
                 for x, y in ((660, 470), (720, 560), (680, 700), (760, 780), (850, 690), (940, 760), (930, 600))),
         '<radialGradient id="glow" cx="0.3" cy="0.62" r="0.4"><stop offset="0" stop-color="#FFE9B0" stop-opacity="0.6"/>'
         '<stop offset="1" stop-color="#FFE9B0" stop-opacity="0"/></radialGradient>',
         f'<rect width="{W}" height="{H}" fill="url(#glow)"/>',
         '<rect x="0" y="1150" width="1080" height="770" fill="#6B4320"/>',
         '<rect x="560" y="1080" width="380" height="100" fill="#F4EEDD" transform="skewX(-20)"/>']
    if sketch == "octagon":
        p.append('<polygon points="760,1095 800,1095 822,1118 822,1150 800,1170 760,1170 738,1150 738,1118" '
                 'fill="none" stroke="#3B2A1A" stroke-width="5" transform="skewX(-20) translate(380 0)"/>')
    p.append('<path d="M140 1150 L180 900 L320 860" stroke="#3B2A1A" stroke-width="10" fill="none"/>'
             '<path d="M300 820 L400 860 L360 920 Z" fill="#3B2A1A"/>')
    return "".join(p), (360, 900, 1.0)


def wall():
    p = [_vgrad("sky", "#9FB6CC", "#DCE6EF"),
         '<rect x="0" y="700" width="1080" height="560" fill="#B5B8BC"/>']
    for x in range(0, 1080, 180):
        p.append(f'<path d="M{x} 700 V1260" stroke="#8E9298" stroke-width="6"/>')
    p += ['<path d="M80 900 q60 -80 140 0 t140 0" stroke="#E8505B" stroke-width="22" fill="none" stroke-linecap="round"/>',
          '<path d="M780 820 l40 120 l40 -120 l40 120" stroke="#3FB6E8" stroke-width="18" fill="none" stroke-linejoin="round"/>',
          '<circle cx="980" cy="1120" r="50" fill="none" stroke="#F5C452" stroke-width="16"/>',
          '<path d="M520 700 L560 820 L510 900 L580 1000 L540 1260 H700 L720 700Z" fill="#E6EEF5"/>',
          '<rect x="0" y="1250" width="1080" height="670" fill="#8E9298"/>']
    return "".join(p), (300, 980, 0.95)
