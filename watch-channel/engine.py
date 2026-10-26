"""エピソード定義（episodes/epNN_*.py）から縦動画を組み立てる共通エンジン。

エピソードモジュールに置くもの:
    SLUG     出力ファイル名（例 "ep02_rolex_oyster"）
    TITLE    画面上部に出すタイトル
    CAPTION  投稿用キャプション（ハッシュタグ込み）
    CUTS     [(シーン, 表情, 字幕, 読み上げ[省略可]), ...]
             シーンは scenes.py の関数名か、(関数名, {引数}) のタプル
    SE       {カット番号(1 始まり): [(se 関数名, 開始秒, 音量), ...]}（任意）
"""
import hashlib
import json
import os
import subprocess

import numpy as np

import scenes
import se
from craftsman import LENS_DEF, craftsman

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, "build")
VIDEOS = os.path.join(ROOT, "videos")
W, H = scenes.W, scenes.H
FONT = "Hiragino Sans, Noto Sans JP, IPAGothic, sans-serif"
SERIES = "1分でわかる時計史"

VOICE = "bb3bf6a073cb48c1a5b6c436053ce243"  # Fish Audio「男性ナレーター」
SPEED = 1.1
SE_GAIN = 0.45  # SE 全体の音量
BGM_GAIN = 0.09
TAIL = 0.3  # ナレーション後の間
MIN_SECONDS = 61  # Creator Rewards は 1 分超えの動画が対象

EXPR_SE = {"thinking": ("question", 0.45), "surprised": ("shock", 0.6),
           "happy": ("sparkle", 0.3), "sad": ("sad", 0.35)}


# ---------- 画 ----------

def header(title):
    size = scenes._fit(title, 960, 70)
    return (f'<rect x="60" y="190" width="380" height="64" rx="32" fill="#8B5A2B"/>'
            f'<text x="250" y="234" text-anchor="middle" font-family="{FONT}" font-size="36" font-weight="800" fill="#FFF">{SERIES}</text>'
            f'<text x="64" y="340" font-family="{FONT}" font-size="{size}" font-weight="900" fill="#FFF" '
            f'stroke="#1B1B1F" stroke-width="12" paint-order="stroke">{title}</text>')


def subtitle(text):
    lines = text.split("\n")
    lh, top = 86, 1360
    p = [f'<rect x="50" y="{top}" width="{W - 100}" height="{lh * len(lines) + 50}" rx="28" fill="#FFF" opacity="0.93"/>']
    for i, line in enumerate(lines):
        size = scenes._fit(line, 940, 64)
        p.append(f'<text x="{W / 2}" y="{top + 25 + lh * (i + 1) - 18}" text-anchor="middle" font-family="{FONT}" '
                 f'font-size="{size}" font-weight="900" fill="#1B1B1F">{line}</text>')
    return "".join(p)


def scene_svg(spec):
    name, kw = (spec, {}) if isinstance(spec, str) else spec
    return getattr(scenes, name)(**kw)


def cut_svg(title, spec, expr, text):
    bg, (x, y, s) = scene_svg(spec)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs>{LENS_DEF}</defs>{bg}{craftsman(x, y, s, expr)}{header(title)}{subtitle(text)}</svg>')


def render_pngs(pairs):
    js = """
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: %d, height: %d}});
  for (const [svg, png] of %s) { await p.goto('file://' + svg); await p.screenshot({path: png}); }
  await b.close();
})();""" % (W, H, json.dumps(pairs))
    subprocess.run(["node", "-e", js], check=True)


# ---------- 音 ----------

def tts(text):
    """ナレーションを生成してパスを返す。声・速度・テキストが同じならキャッシュを使う"""
    key = hashlib.sha1(f"{VOICE}|{SPEED}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(WORK, "tts", f"{key}.mp3")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        body = json.dumps({"text": text, "reference_id": VOICE, "format": "mp3", "latency": "normal",
                           "prosody": {"speed": SPEED, "volume": 0}})
        tmp = path + ".part"
        for attempt in range(4):
            r = subprocess.run(["curl", "-sS", "--fail", "-X", "POST", "https://api.fish.audio/v1/tts",
                                "-H", "Content-Type: application/json", "-H", "model: s1",
                                "--data-binary", body, "-o", tmp])
            if r.returncode == 0:
                break
            subprocess.run(["sleep", str(2 ** (attempt + 1))])
        else:
            raise RuntimeError(f"TTS failed: {text}")
        os.replace(tmp, path)
    return path


def decode(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(se.SR), "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32)


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def _name(spec):
    return spec if isinstance(spec, str) else spec[0]


def cues(i, n, spec, expr, prev, extra):
    """カット i（1 始まり）の頭から鳴らす SE: [(開始秒, 波形, 音量)]"""
    out = []
    changed = prev is None or _name(prev[0]) != _name(spec)
    if changed and prev is not None:
        out.append((0.0, se.whoosh(), 0.3))
    if expr in EXPR_SE and (changed or prev[1] != expr):
        name, gain = EXPR_SE[expr]
        out.append((0.05, getattr(se, name)(), gain))
    for name, start, gain in extra.get(i, []):
        if name != "ticking":
            out.append((start, getattr(se, name)(), gain))
    if i == n:
        out.append((0.1, se.chime(), 0.35))
    return out


# ---------- ビルド ----------

def build(ep, render=True):
    work = os.path.join(WORK, ep.SLUG)
    os.makedirs(work, exist_ok=True)
    os.makedirs(VIDEOS, exist_ok=True)
    extra = getattr(ep, "SE", {})
    cuts = [(c[0], c[1], c[2], c[3] if len(c) > 3 else None) for c in ep.CUTS]
    for _, _, text, _ in cuts:
        for line in text.split("\n"):
            if len(line) > 16:
                print(f"  [warn] {ep.SLUG}: 字幕が長い「{line}」")

    pairs, mp3s = [], []
    for i, (spec, expr, text, reading) in enumerate(cuts, 1):
        svg = os.path.join(work, f"cut{i:02d}.svg")
        with open(svg, "w") as f:
            f.write(cut_svg(ep.TITLE, spec, expr, text))
        pairs.append([svg, svg[:-4] + ".png"])
        mp3s.append(tts(reading or text.replace("\n", "")))
    if render:
        render_pngs(pairs)

    voice, fx, frames, t, prev = [], [], [], 0.0, None
    for i, (spec, expr, _, _) in enumerate(cuts, 1):
        v = decode(mp3s[i - 1])
        c = cues(i, len(cuts), spec, expr, prev, extra)
        lead = 0.3 if c else 0.08
        dur = round(lead + len(v) / se.SR + TAIL, 2)
        voice.append((t + lead, v, 1.0))
        fx += [(t + s, w, g) for s, w, g in c]
        for name, start, gain in extra.get(i, []):
            if name == "ticking":
                fx.append((t + start, se.ticking(dur - start), gain))
        frames.append((pairs[i - 1][1], dur))
        t += dur
        prev = (spec, expr)

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
    idx = np.arange(total)
    env = (c[np.minimum(idx + win // 2, total)] - c[np.maximum(idx - win // 2, 0)]) / win
    duck = 1 - 0.45 * np.clip(env / 0.04, 0, 1)
    bgm = np.resize(se.bgm(total / se.SR), total)  # 丸めで 1 サンプルずれることがあるので長さを合わせる
    mix = vtrack + SE_GAIN * fxtrack + BGM_GAIN * duck * bgm
    mix *= 0.89 / np.max(np.abs(mix))
    raw = os.path.join(work, "mix.f32")
    mix.astype(np.float32).tofile(raw)

    lst = os.path.join(work, "frames.txt")
    with open(lst, "w") as f:
        for png, d in frames:
            f.write(f"file '{png}'\nduration {d}\n")
        f.write(f"file '{frames[-1][0]}'\n")
    final = os.path.join(VIDEOS, f"{ep.SLUG}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error",
                    "-f", "concat", "-safe", "0", "-i", lst,
                    "-f", "f32le", "-ar", str(se.SR), "-ac", "1", "-i", raw,
                    "-map", "0:v", "-map", "1:a", "-vf", "fps=30,format=yuv420p",
                    "-c:v", "libx264", "-profile:v", "high", "-tune", "stillimage",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-t", f"{t:.2f}", "-movflags", "+faststart", final], check=True)
    with open(os.path.join(VIDEOS, f"{ep.SLUG}.txt"), "w") as f:
        f.write(ep.CAPTION.strip() + "\n")
    d = duration(final)
    flag = "" if d >= MIN_SECONDS else f"  [warn] {MIN_SECONDS}秒未満"
    print(f"{ep.SLUG}: {d:.1f}s{flag}")
    return d
