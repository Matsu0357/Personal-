"""「オメガが月に行った話」縦動画を組み立てる。

    python3 build.py   ->  out/omega-moon.mp4

各カットの SVG/PNG、Fish Audio のナレーション、SE を混ぜた音声、ffmpeg で 1 パス書き出しした mp4 を out/ に置く。
"""
import hashlib
import json
import os
import random
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from craftsman import craftsman, LENS_DEF  # noqa: E402
import se  # noqa: E402

OUT = os.path.join(HERE, "out")
W, H = 1080, 1920
FONT = "Hiragino Sans, Noto Sans JP, IPAGothic, sans-serif"
VOICE = "bb3bf6a073cb48c1a5b6c436053ce243"  # Fish Audio「男性ナレーター」
SPEED = 1.1
SE_GAIN = 0.65  # SE 全体の音量
BGM_GAIN = 0.09
TITLE = "オメガが月に行った話"

# (場面, 表情, 字幕, 読み上げ用テキスト[省略時は字幕])
CUTS = [
    ("moon", "thinking", "人類が初めて\n月に立った日。", None),
    ("moon", "normal", "その腕にあった時計を\n知っていますか？", None),
    ("hero", "happy", "オメガ・\nスピードマスターです。", None),
    ("race", "normal", "1957年、\nスピードマスターは", "1957年、スピードマスターは"),
    ("race", "happy", "もともとカーレース用の\n時計として生まれました。", None),
    ("lab", "thinking", "1960年代、NASAは\n宇宙飛行士の時計を選ぶため、", "1960年代、ナサは、宇宙飛行士の時計を選ぶため、"),
    ("lab", "thinking", "複数のメーカーの時計を\n集めてテストします。", None),
    ("lab", "surprised", "90℃を超える高温、\n真空、強い衝撃…", "90度を超える高温。真空。強い衝撃。"),
    ("lab", "sad", "過酷なテストで\n次々と脱落する中、", None),
    ("hero", "happy", "最後まで耐え抜いたのは\nスピードマスターだけでした。", None),
    ("moon_lm", "happy", "1969年、\nアポロ11号。", "1969年、アポロ11号。"),
    ("moon_lm", "happy", "バズ・オルドリンの\n腕に巻かれ、月面へ。", None),
    ("moon_lm", "surprised", "実はアームストロングは、\n着陸船の時計の故障に備えて、", None),
    ("moon_lm", "normal", "自分の時計を\n船内に残していたんです。", None),
    ("apollo13", "sad", "1970年、事故で危機に陥った\nアポロ13号。", "1970年、事故で危機に陥った、アポロ13号。"),
    ("apollo13_timer", "surprised", "地球へ帰るための\nエンジン噴射、14秒。", "地球へ帰るための、エンジン噴射、14秒。"),
    ("apollo13_timer", "happy", "その時間を計ったのも、\nスピードマスターでした。", None),
    ("outro", "normal", "レース用に生まれた時計が、\n宇宙飛行士の命を支えた。", None),
    ("outro", "happy", "だから今も\n『ムーンウォッチ』と\n呼ばれています。", "だから今も、ムーンウォッチと呼ばれています。"),
    ("outro", "normal", "フォローして、\n次の時計の物語も見てね。", None),
]


# ---------- 部品 ----------

def stars(n, seed, y_max):
    rnd = random.Random(seed)
    return "".join(
        f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, y_max):.0f}" '
        f'r="{rnd.choice([1.5, 2, 2.5, 3.5])}" fill="#FFF" opacity="{rnd.uniform(0.4, 1):.2f}"/>'
        for _ in range(n))


def earth(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#3A7BD5"/>'
            f'<path d="M{cx - r * 0.6} {cy - r * 0.3} q{r * 0.3} {-r * 0.4} {r * 0.6} {-r * 0.1} '
            f'q{r * 0.2} {r * 0.3} {-r * 0.1} {r * 0.5} q{-r * 0.4} {r * 0.1} {-r * 0.5} {-r * 0.4}Z" fill="#4CAF6A"/>'
            f'<path d="M{cx + r * 0.2} {cy + r * 0.2} q{r * 0.4} {-r * 0.1} {r * 0.5} {r * 0.3} '
            f'q{-r * 0.2} {r * 0.4} {-r * 0.5} {r * 0.1}Z" fill="#4CAF6A"/>'
            f'<path d="M{cx - r * 0.8} {cy + r * 0.1} q{r * 0.5} {-r * 0.15} {r * 1.0} {0}" '
            f'stroke="#FFF" stroke-width="{r * 0.08}" fill="none" stroke-linecap="round" opacity="0.8"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#9FD0FF" stroke-width="{r * 0.06}" opacity="0.6"/>')


def chrono(cx, cy, r):
    """ロゴなしの汎用クロノグラフ"""
    p = [f'<rect x="{cx - r * 0.42}" y="{cy - r * 1.6}" width="{r * 0.84}" height="{r * 3.2}" rx="{r * 0.1}" fill="#24242A"/>']
    for sy in (-1, 1):
        for sx in (-1, 1):
            p.append(f'<rect x="{cx + sx * r * 0.62 - r * 0.11}" y="{cy + sy * r * 1.0 - r * 0.2}" '
                     f'width="{r * 0.22}" height="{r * 0.4}" rx="{r * 0.06}" fill="#B9BEC6"/>')
    p.append(f'<rect x="{cx + r * 0.98}" y="{cy - r * 0.12}" width="{r * 0.2}" height="{r * 0.24}" rx="{r * 0.04}" fill="#B9BEC6"/>')
    for sy in (-1, 1):
        p.append(f'<rect x="{cx + r * 0.82}" y="{cy + sy * r * 0.55 - r * 0.08}" width="{r * 0.22}" height="{r * 0.16}" '
                 f'rx="{r * 0.04}" fill="#B9BEC6" transform="rotate({sy * 32} {cx + r * 0.85} {cy + sy * r * 0.55})"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 1.06}" fill="#C9CDD4" stroke="#8E949C" stroke-width="{r * 0.02}"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#111"/>')
    p.append(f'<g transform="translate({cx} {cy})">')
    for i in range(60):
        long = i % 5 == 0
        p.append(f'<line x1="0" y1="{-r * 0.97}" x2="0" y2="{-r * (0.89 if long else 0.93)}" stroke="#FFF" '
                 f'stroke-width="{r * (0.018 if long else 0.008)}" transform="rotate({i * 6})"/>')
    p.append(f'<circle r="{r * 0.85}" fill="#151517"/>')
    for i in range(12):
        if i in (3, 6, 9):
            continue
        p.append(f'<line x1="0" y1="{-r * 0.8}" x2="0" y2="{-r * 0.64}" stroke="#F2F2F2" stroke-width="{r * 0.035}" '
                 f'stroke-linecap="round" transform="rotate({i * 30})"/>')
    for ang, (dx, dy) in ((60, (0.42, 0)), (200, (0, 0.42)), (300, (-0.42, 0))):
        x, y = dx * r, dy * r
        p.append(f'<circle cx="{x}" cy="{y}" r="{r * 0.19}" fill="#1E1E22" stroke="#8C8C94" stroke-width="{r * 0.012}"/>')
        p.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y - r * 0.15}" stroke="#FFF" stroke-width="{r * 0.015}" '
                 f'transform="rotate({ang} {x} {y})"/>')
    p.append(f'<line x1="0" y1="0" x2="0" y2="{-r * 0.45}" stroke="#FFF" stroke-width="{r * 0.05}" stroke-linecap="round" transform="rotate(-50)"/>')
    p.append(f'<line x1="0" y1="0" x2="0" y2="{-r * 0.7}" stroke="#FFF" stroke-width="{r * 0.035}" stroke-linecap="round" transform="rotate(55)"/>')
    p.append(f'<line x1="0" y1="{r * 0.15}" x2="0" y2="{-r * 0.78}" stroke="#FFF" stroke-width="{r * 0.012}" transform="rotate(10)"/>')
    p.append(f'<circle r="{r * 0.04}" fill="#FFF"/>')
    p.append(f'<path d="M{-r * 0.6} {-r * 0.55} A{r * 0.82} {r * 0.82} 0 0 1 {r * 0.1} {-r * 0.82}" '
             f'stroke="#FFF" stroke-width="{r * 0.03}" fill="none" opacity="0.12" stroke-linecap="round"/>')
    p.append('</g>')
    return "".join(p)


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


def race_car(x, y, s):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            '<path d="M-170 0 Q-170 -45 -110 -50 L60 -55 Q150 -55 180 -15 Q190 10 170 20 L-160 20 Q-175 15 -170 0Z" fill="#D83A2E"/>'
            '<path d="M-150 -10 H160" stroke="#FFF" stroke-width="6" opacity="0.7"/>'
            '<ellipse cx="-10" cy="-55" rx="40" ry="16" fill="#222"/>'
            '<circle cx="-10" cy="-72" r="22" fill="#F4F4F4"/><rect x="-6" y="-80" width="24" height="10" rx="4" fill="#2A2F3A"/>'
            '<circle cx="70" cy="-18" r="24" fill="#FFF"/>'
            f'<text x="70" y="-6" text-anchor="middle" font-family="{FONT}" font-size="34" font-weight="900" fill="#222">7</text>'
            '<circle cx="-110" cy="25" r="38" fill="#1B1B1F"/><circle cx="-110" cy="25" r="15" fill="#CCC"/>'
            '<circle cx="110" cy="25" r="38" fill="#1B1B1F"/><circle cx="110" cy="25" r="15" fill="#CCC"/>'
            '<path d="M-200 -30 H-250 M-210 0 H-280 M-200 25 H-240" stroke="#FFF" stroke-width="6" stroke-linecap="round" opacity="0.8"/>'
            '</g>')


def small_watch(x, y, s, fill="#F2F2F2"):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            '<rect x="-14" y="-60" width="28" height="120" rx="6" fill="#3A2A1A"/>'
            f'<circle r="30" fill="#C9CDD4"/><circle r="24" fill="{fill}"/>'
            '<path d="M0 0 V-16 M0 0 L10 6" stroke="#222" stroke-width="3" stroke-linecap="round"/></g>')


# ---------- 背景 ----------

def bg_moon(lm=False):
    p = ['<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070A20"/>'
         '<stop offset="1" stop-color="#1E2A5A"/></linearGradient>',
         f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(110, 1, 1150), earth(830, 560, 110)]
    if lm:
        p.append(lunar_module(250, 1060, 0.9))
    p.append('<path d="M0 1190 Q270 1150 540 1180 T1080 1170 V1920 H0 Z" fill="#B9BCC6"/>')
    for cx, cy, rx in ((150, 1450, 70), (760, 1300, 50), (880, 1700, 90), (420, 1820, 60), (980, 1240, 30)):
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx * 0.3}" fill="#9EA2AD"/>')
    return "".join(p)


def bg_race():
    p = ['<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7EC8F5"/>'
         '<stop offset="1" stop-color="#E8F6FF"/></linearGradient>',
         f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
         '<circle cx="860" cy="430" r="80" fill="#FFE27A"/>',
         '<path d="M0 900 Q250 780 520 880 T1080 850 V1000 H0Z" fill="#7CC07A"/>',
         '<rect x="0" y="960" width="1080" height="120" fill="#5E6A7A"/>']
    for i in range(12):
        p.append(f'<rect x="{i * 92 + 6}" y="975" width="80" height="22" rx="4" fill="{["#E8505B", "#F5C452", "#4FA3E0"][i % 3]}"/>')
        p.append(f'<rect x="{i * 92 + 6}" y="1015" width="80" height="22" rx="4" fill="{["#F5C452", "#4FA3E0", "#E8505B"][i % 3]}"/>')
    p.append('<rect x="0" y="1080" width="1080" height="840" fill="#8BC27F"/>')
    p.append('<path d="M0 1120 H1080 V1460 H0Z" fill="#4A4E57"/>')
    p.append('<path d="M0 1290 H1080" stroke="#FFF" stroke-width="10" stroke-dasharray="60 50"/>')
    # チェッカーフラッグ
    p.append('<line x1="90" y1="1120" x2="90" y2="760" stroke="#555" stroke-width="10"/>')
    for r in range(4):
        for c in range(6):
            if (r + c) % 2 == 0:
                p.append(f'<rect x="{95 + c * 25}" y="{760 + r * 25}" width="25" height="25" fill="#111"/>')
    p.append('<rect x="95" y="760" width="150" height="100" fill="none" stroke="#111" stroke-width="3"/>')
    p.append(race_car(780, 1225, 0.95))
    return "".join(p)


def bg_lab():
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
         '<rect x="650" y="960" width="260" height="110" rx="10" fill="#2A2F3A"/>',
         f'<text x="780" y="1035" text-anchor="middle" font-family="monospace" font-size="64" font-weight="700" fill="#FF6A3D">93°C</text>',
         '<rect x="1010" y="600" width="30" height="380" rx="15" fill="#FFF" stroke="#5E6A7A" stroke-width="4"/>',
         '<rect x="1017" y="700" width="16" height="270" rx="8" fill="#FF4A3D"/>',
         '<circle cx="1025" cy="985" r="26" fill="#FF4A3D"/>']
    return "".join(p)


def bg_hero():
    return ('<radialGradient id="spot" cx="0.5" cy="0.38" r="0.6"><stop offset="0" stop-color="#4A4A78"/>'
            '<stop offset="1" stop-color="#14142A"/></radialGradient>'
            f'<rect width="{W}" height="{H}" fill="url(#spot)"/>' + stars(40, 7, 1900) + chrono(560, 760, 250))


def bg_apollo13(timer=False):
    p = ['<radialGradient id="alert" cx="0.5" cy="0.5" r="0.75"><stop offset="0.55" stop-color="#FF2A2A" stop-opacity="0"/>'
         '<stop offset="1" stop-color="#FF2A2A" stop-opacity="0.45"/></radialGradient>',
         f'<rect width="{W}" height="{H}" fill="#05060F"/>', stars(120, 3, 1920), earth(170, 640, 70),
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
        p.append('<text x="540" y="515" text-anchor="middle" font-family="monospace" font-size="130" font-weight="700" '
                 'fill="#FF4A3D">00:14</text>')
    return "".join(p)


def bg_outro():
    p = ['<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A3B22"/>'
         '<stop offset="1" stop-color="#7A5233"/></linearGradient>',
         f'<rect width="{W}" height="{H}" fill="url(#wall)"/>']
    for i in range(1, 9):
        p.append(f'<line x1="{i * 135}" y1="0" x2="{i * 135}" y2="1180" stroke="#4A2F1A" stroke-width="4" opacity="0.6"/>')
    p.append('<radialGradient id="lamp" cx="0.7" cy="0.55" r="0.5"><stop offset="0" stop-color="#FFE9B0" stop-opacity="0.55"/>'
             '<stop offset="1" stop-color="#FFE9B0" stop-opacity="0"/></radialGradient>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#lamp)"/>')
    p.append(f'<text x="540" y="560" text-anchor="middle" font-family="{FONT}" font-size="118" font-weight="900" '
             'fill="#F2C14E" stroke="#3B2410" stroke-width="14" paint-order="stroke">ムーンウォッチ</text>')
    p.append('<rect x="0" y="1180" width="1080" height="740" fill="#9A6A3C"/>')
    p.append('<rect x="0" y="1180" width="1080" height="24" fill="#B98552"/>')
    p.append('<path d="M760 1180 L800 1060 H880 L920 1180 Z" fill="#3A2A1A"/>')
    p.append(chrono(840, 960, 95))
    return "".join(p)


BACKGROUNDS = {
    "moon": (bg_moon, (300, 960, 1.0)),
    "moon_lm": (lambda: bg_moon(lm=True), (640, 950, 1.0)),
    "hero": (bg_hero, (220, 1080, 0.75)),
    "race": (bg_race, (330, 960, 0.95)),
    "lab": (bg_lab, (280, 960, 1.0)),
    "apollo13": (bg_apollo13, (300, 1010, 0.9)),
    "apollo13_timer": (lambda: bg_apollo13(timer=True), (300, 1010, 0.9)),
    "outro": (bg_outro, (360, 900, 1.05)),
}


# ---------- 1 カット ----------

def header():
    return (f'<rect x="60" y="190" width="380" height="64" rx="32" fill="#8B5A2B"/>'
            f'<text x="250" y="234" text-anchor="middle" font-family="{FONT}" font-size="36" font-weight="800" fill="#FFF">1分でわかる時計史</text>'
            f'<text x="64" y="340" font-family="{FONT}" font-size="70" font-weight="900" fill="#FFF" '
            f'stroke="#1B1B1F" stroke-width="12" paint-order="stroke">{TITLE}</text>')


def subtitle(text):
    lines = text.split("\n")
    lh, top = 86, 1360
    h = lh * len(lines) + 50
    p = [f'<rect x="50" y="{top}" width="{W - 100}" height="{h}" rx="28" fill="#FFF" opacity="0.93"/>']
    for i, line in enumerate(lines):
        p.append(f'<text x="{W / 2}" y="{top + 25 + lh * (i + 1) - 18}" text-anchor="middle" font-family="{FONT}" '
                 f'font-size="64" font-weight="900" fill="#1B1B1F">{line}</text>')
    return "".join(p)


def cut_svg(scene, expr, text):
    bg, (x, y, s) = BACKGROUNDS[scene]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs>{LENS_DEF}</defs>{bg()}{craftsman(x, y, s, expr)}{header()}{subtitle(text)}</svg>')


# ---------- ビルド ----------

def tts(text):
    """ナレーションを生成してパスを返す。声・速度・テキストが同じならキャッシュを使う"""
    key = hashlib.sha1(f"{VOICE}|{SPEED}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(OUT, "tts", f"{key}.mp3")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        body = json.dumps({"text": text, "reference_id": VOICE, "format": "mp3", "latency": "normal",
                           "prosody": {"speed": SPEED, "volume": 0}})
        subprocess.run(["curl", "-sS", "--fail", "-X", "POST", "https://api.fish.audio/v1/tts",
                        "-H", "Content-Type: application/json", "-H", "model: s1",
                        "--data-binary", body, "-o", path], check=True)
    return path


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def render_pngs(svgs):
    js = """
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: %d, height: %d}});
  for (const [svg, png] of %s) { await p.goto('file://' + svg); await p.screenshot({path: png}); }
  await b.close();
})();""" % (W, H, json.dumps(svgs))
    subprocess.run(["node", "-e", js], check=True)


def decode(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(se.SR), "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32)


EXPR_SE = {"thinking": (se.question, 0.45), "surprised": (se.shock, 0.6),
           "happy": (se.sparkle, 0.3), "sad": (se.sad, 0.35)}
TAIL = 0.3  # ナレーション後の間


def cues(i, scene, expr, prev):
    """カット i（1 始まり）の頭から鳴らす SE: [(開始秒, 波形, 音量)]"""
    out = []
    changed = prev is None or prev[0].split("_")[0] != scene.split("_")[0]
    if changed and prev is not None:
        out.append((0.0, se.whoosh(), 0.3))
    if expr in EXPR_SE and (changed or prev[1] != expr):
        fn, gain = EXPR_SE[expr]
        out.append((0.05, fn(), gain))
    if i == 4:
        out.append((0.4, se.car_pass(), 0.4))
    if i == 15:
        out.append((0.0, se.alarm(), 0.18))
    if i == 20:
        out.append((0.1, se.chime(), 0.35))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    pairs, mp3s = [], []
    for i, (scene, expr, text, reading) in enumerate(CUTS, 1):
        svg = os.path.join(OUT, f"cut{i:02d}.svg")
        with open(svg, "w") as f:
            f.write(cut_svg(scene, expr, text))
        pairs.append([svg, svg[:-4] + ".png"])
        mp3s.append(tts(reading or text.replace("\n", "")))
    render_pngs(pairs)

    # タイムラインを組んでナレーションと SE を 1 本にミックス
    voice, fx, frames, t, prev = [], [], [], 0.0, None
    for i, (scene, expr, _, _) in enumerate(CUTS, 1):
        v = decode(mp3s[i - 1])
        c = cues(i, scene, expr, prev)
        lead = 0.3 if c else 0.08
        dur = round(lead + len(v) / se.SR + TAIL, 2)
        voice.append((t + lead, v, 1.0))
        fx += [(t + s, w, g) for s, w, g in c]
        if scene == "apollo13_timer" and (prev is None or prev[0] != scene):
            fx.append((t, se.ticking(dur), 0.22))
        frames.append((os.path.join(OUT, f"cut{i:02d}.png"), dur))
        t += dur
        prev = (scene, expr)
    total = int(se.SR * (t + 0.5))
    vtrack, fxtrack = np.zeros(total), np.zeros(total)
    for track, items in ((vtrack, voice), (fxtrack, fx)):
        for start, w, g in items:
            s0 = int(se.SR * start)
            n = min(len(w), total - s0)
            track[s0:s0 + n] += g * w[:n]
    # BGM はナレーション中だけ少し下げる
    win = int(se.SR * 0.4)
    c = np.concatenate([[0], np.cumsum(np.abs(vtrack))])
    env = (c[np.minimum(np.arange(total) + win // 2, total)] - c[np.maximum(np.arange(total) - win // 2, 0)]) / win
    duck = 1 - 0.45 * np.clip(env / 0.04, 0, 1)
    mix = vtrack + SE_GAIN * fxtrack + BGM_GAIN * duck * se.bgm(total / se.SR)
    mix *= 0.89 / np.max(np.abs(mix))
    wav = os.path.join(OUT, "mix.f32")
    mix.astype(np.float32).tofile(wav)

    lst = os.path.join(OUT, "frames.txt")
    with open(lst, "w") as f:
        for png, d in frames:
            f.write(f"file '{png}'\nduration {d}\n")
        f.write(f"file '{frames[-1][0]}'\n")
    final = os.path.join(OUT, "omega-moon.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error",
                    "-f", "concat", "-safe", "0", "-i", lst,
                    "-f", "f32le", "-ar", str(se.SR), "-ac", "1", "-i", wav,
                    "-map", "0:v", "-map", "1:a", "-vf", "fps=30,format=yuv420p",
                    "-c:v", "libx264", "-profile:v", "high", "-tune", "stillimage",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-t", f"{t:.2f}", "-movflags", "+faststart", final], check=True)
    print(final, f"{duration(final):.1f}s")


if __name__ == "__main__":
    main()
