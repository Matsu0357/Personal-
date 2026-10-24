"""script.json → ナレーション音声（1行ずつ）→ timeline.json と audio.wav を作る。

使い方: python3 build_audio.py
必要: edge-tts, ffmpeg, numpy
"""
import json
import os
import subprocess
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 48000

GAP_LINE = 0.35    # 行と行のあいだ
GAP_SCENE = 0.9    # シーンとシーンのあいだ
RULE_CARD = 1.6    # 「ルールN」カードを見せる時間（ナレーション前）
LEAD_IN = 1.2      # 冒頭の無音
TAIL = 2.5         # 最後の余韻


def tts(text, voice, rate, out_mp3):
    if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 0:
        return
    cmd = ["edge-tts", "--voice", voice, f"--rate={rate}", "--text", text, "--write-media", out_mp3]
    proxy = os.environ.get("HTTPS_PROXY")
    if proxy:
        cmd[1:1] = ["--proxy", proxy]
    subprocess.run(cmd, check=True, capture_output=True)


def load_mono(path):
    raw = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def env(n, attack=0.005, release=0.05):
    e = np.ones(n, dtype=np.float32)
    a, r = int(attack * SR), int(release * SR)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def tone(freq, dur, vol=0.2, decay=8.0):
    t = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * freq * t) * np.exp(-decay * t) * vol).astype(np.float32)


def noise(dur, vol=0.2, lowpass=0.02, decay=20.0):
    n = np.random.default_rng(1).standard_normal(int(dur * SR)).astype(np.float32)
    # 簡単なローパス（指数移動平均）
    y = np.empty_like(n)
    acc = 0.0
    for i, v in enumerate(n):
        acc += lowpass * (v - acc)
        y[i] = acc
    t = np.arange(len(y)) / SR
    return (y / (np.abs(y).max() + 1e-9) * vol * np.exp(-decay * t)).astype(np.float32)


def add(*parts):
    out = np.zeros(max(len(p) for p in parts), dtype=np.float32)
    for p in parts:
        out[:len(p)] += p
    return out


SFX = {
    "atari": lambda: np.concatenate([tone(f, 0.12, 0.16, 6) for f in (988, 1319, 1568, 1976)]),
    "atari_slow": lambda: np.concatenate([tone(f, 0.2, 0.16, 4) for f in (988, 932, 880, 831)]),
    "can": lambda: add(noise(0.35, 0.5, 0.08, 14), tone(140, 0.35, 0.25, 12)),
    "coin": lambda: add(*(np.pad(tone(f, 0.25, 0.1, 18), (int(d * SR), 0))
                          for f, d in ((3200, 0), (4100, 0.07), (3600, 0.16), (4500, 0.24), (3900, 0.33)))),
    "beep": lambda: tone(1046, 0.18, 0.12, 3),
    "click": lambda: noise(0.06, 0.35, 0.5, 60),
    "thump": lambda: add(tone(55, 0.8, 0.5, 5), noise(0.4, 0.2, 0.03, 10)),
}


def main():
    os.makedirs(BUILD, exist_ok=True)
    script = json.load(open(os.path.join(HERE, "script.json"), encoding="utf-8"))
    voice, rate = script["voice"], script["rate"]

    t = LEAD_IN
    timeline = {"title": script["title"], "scenes": []}
    clips = []  # (start, samples)
    for si, sc in enumerate(script["scenes"]):
        scene = {k: v for k, v in sc.items() if k != "lines"}
        scene["start"] = t
        if sc.get("rule"):
            t += RULE_CARD
        scene["lines"] = []
        for li, text in enumerate(sc["lines"]):
            mp3 = os.path.join(BUILD, f"{si:02d}_{li:02d}.mp3")
            tts(text, voice, rate, mp3)
            samples = load_mono(mp3)
            dur = len(samples) / SR
            scene["lines"].append({"text": text, "start": round(t, 3), "end": round(t + dur, 3)})
            clips.append((t, samples))
            t += dur + GAP_LINE
        t += GAP_SCENE - GAP_LINE
        scene["end"] = round(t, 3)
        timeline["scenes"].append(scene)
        print(f"{sc['id']:8s} {scene['start']:6.1f} - {scene['end']:6.1f}")
    total = t + TAIL
    timeline["duration"] = round(total, 3)

    # 効果音のきっかけ（シーンIDと行番号で指定）
    cues = []
    def at(scene_id, line, sfx, offset=0.0):
        s = next(s for s in timeline["scenes"] if s["id"] == scene_id)
        base = s["start"] if line is None else s["lines"][line]["start"]
        cues.append((base + offset, sfx))
    at("hook", 0, "atari", 1.5)
    at("streak", 0, "atari", 1.2); at("streak", 0, "can", 2.2)
    at("streak", 1, "atari", 0.6); at("streak", 1, "can", 1.4)
    at("streak", 2, "atari_slow", 0.9); at("streak", 2, "can", 2.2)
    for sid in ("rule1", "rule2", "rule3", "rule4", "rule5"):
        at(sid, None, "beep", 0.1)
    at("rule2", 0, "coin", 0.5); at("rule2", 1, "coin", 0.2)
    at("rule3", 1, "beep", 0.4)
    for k in range(5):
        at("rule5", 1, "click", 0.3 + k * 0.6)
    at("reveal", 1, "thump", 0.0)
    at("twist", 5, "thump", 1.2)
    at("outro", None, "atari_slow", 0.2)
    timeline["cues"] = [{"t": round(c, 3), "sfx": s} for c, s in sorted(cues)]

    n = int(total * SR) + SR
    voice_track = np.zeros(n, dtype=np.float32)
    for start, s in clips:
        i = int(start * SR)
        voice_track[i:i + len(s)] += s
    sfx_track = np.zeros(n, dtype=np.float32)
    for c, name in cues:
        s = SFX[name]()
        i = int(c * SR)
        sfx_track[i:i + len(s)] += s[: n - i]

    # 環境音：低いハム（自販機のコンプレッサー）＋かすかなノイズ
    tt = np.arange(n) / SR
    hum = 0.018 * np.sin(2 * np.pi * 50 * tt) + 0.009 * np.sin(2 * np.pi * 100 * tt)
    hum *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * tt)
    rng = np.random.default_rng(7)
    hiss = rng.standard_normal(n).astype(np.float32) * 0.004
    amb = (hum + hiss) * env(n, 2.0, 3.0)

    mix = voice_track * 1.0 + sfx_track * 0.8 + amb
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(os.path.join(BUILD, "audio.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    json.dump(timeline, open(os.path.join(BUILD, "timeline.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"total {total:.1f}s")


if __name__ == "__main__":
    main()
