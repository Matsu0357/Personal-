"""script.json → ナレーション（1行ずつ）→ build/timeline.json と BGM・効果音入りの build/audio.wav

使い方: python3 build_audio.py
必要: edge-tts, ffmpeg, numpy
行は文字列のほか {"text", "pitch", "rate", "gain"} でも書ける（心の声など）。
"""
import json
import os
import subprocess
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 48000

GAP_LINE = 0.55   # 行と行のあいだ（Day One Films 型はゆっくり）
GAP_SCENE = 1.2   # シーンとシーンのあいだ
CARD = 2.0        # 「DAY 1.」などのタイトルカード（ナレーション前）
LEAD_IN = 1.5
TAIL = 4.0


def tts(line, voice, rate, out_mp3):
    if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 0:
        return
    cmd = ["edge-tts", "--voice", voice, f"--rate={line.get('rate', rate)}",
           f"--pitch={line.get('pitch', '+0Hz')}", "--text", line["text"], "--write-media", out_mp3]
    if os.environ.get("HTTPS_PROXY"):
        cmd[1:1] = ["--proxy", os.environ["HTTPS_PROXY"]]
    subprocess.run(cmd, check=True, capture_output=True)


def load_mono(path):
    raw = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def lowpass(x, k):
    return np.convolve(x, np.ones(k, dtype=np.float32) / k, mode="same").astype(np.float32)


def note(freq, dur, vol):
    """ピアノ風の音：倍音を少し足して、指数的に減衰させる。"""
    t = np.arange(int(dur * SR)) / SR
    w = sum(np.sin(2 * np.pi * freq * h * t) / h ** 1.6 for h in (1, 2, 3, 4))
    e = np.exp(-2.2 * t) * np.minimum(1, t / 0.01)
    return (w * e * vol).astype(np.float32)


def pad(freqs, dur, vol):
    """やわらかいパッド：ゆっくり立ち上がって消える和音。"""
    t = np.arange(int(dur * SR)) / SR
    w = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs)
    e = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 1.5)
    return (w * e * vol / len(freqs)).astype(np.float32)


HZ = lambda m: 440.0 * 2 ** ((m - 69) / 12)  # MIDI → Hz
CHORDS_SAD = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]     # Am F C G
CHORDS_HOPE = [(48, 52, 55), (55, 59, 62), (57, 60, 64), (53, 57, 60)]    # C G Am F


def music(n, sections):
    """sections: [(start, end, chords, vol, arp)] → BGM の波形"""
    out = np.zeros(n, dtype=np.float32)
    bar = 4.0
    for start, end, chords, vol, arp in sections:
        t, k = start, 0
        while t < end:
            ch = chords[k % len(chords)]
            i = int(t * SR)
            p = pad([HZ(m - 12) for m in ch], bar + 1.5, vol * 0.5)
            out[i:i + len(p)] += p[: n - i]
            if arp:
                for j, m in enumerate((ch[0], ch[1], ch[2], ch[1] + 12, ch[2], ch[1], ch[0] + 12, ch[2])):
                    s = note(HZ(m + 12), 1.6, vol * 0.35)
                    ii = int((t + j * bar / 8) * SR)
                    if ii < n:
                        out[ii:ii + len(s)] += s[: n - ii]
            t += bar
            k += 1
    return out


def main():
    os.makedirs(BUILD, exist_ok=True)
    script = json.load(open(os.path.join(HERE, "script.json"), encoding="utf-8"))
    voice, rate = script["voice"], script["rate"]

    t = LEAD_IN
    timeline = {"title": script["title"], "scenes": []}
    clips = []
    for si, sc in enumerate(script["scenes"]):
        scene = {k: v for k, v in sc.items() if k != "lines"}
        scene["start"] = round(t, 3)
        if sc.get("card"):
            t += CARD
        scene["lines"] = []
        for li, raw in enumerate(sc["lines"]):
            line = raw if isinstance(raw, dict) else {"text": raw}
            mp3 = os.path.join(BUILD, f"{si:02d}_{li:02d}.mp3")
            tts(line, voice, rate, mp3)
            samples = load_mono(mp3) * line.get("gain", 1.0)
            dur = len(samples) / SR
            scene["lines"].append({"text": line["text"], "inner": "pitch" in line,
                                   "start": round(t, 3), "end": round(t + dur, 3)})
            clips.append((t, samples))
            t += dur + GAP_LINE
        t += GAP_SCENE - GAP_LINE
        scene["end"] = round(t, 3)
        timeline["scenes"].append(scene)
        print(f"{sc['id']:9s} {scene['start']:6.1f} - {scene['end']:6.1f}")
    total = t + TAIL
    timeline["duration"] = round(total, 3)
    sc = {s["id"]: s for s in timeline["scenes"]}
    n = int(total * SR) + SR

    voice_track = np.zeros(n, dtype=np.float32)
    for start, s in clips:
        i = int(start * SR)
        voice_track[i:i + len(s)] += s

    # BGM：前半は静か → 三日目〜スマホで消える → やり直しで戻る → 最後に明るく
    bgm = music(n, [
        (0, sc["day3"]["start"], CHORDS_SAD, 0.10, True),
        (sc["restart"]["start"], sc["day4"]["start"], CHORDS_SAD, 0.09, False),
        (sc["day4"]["start"], total, CHORDS_HOPE, 0.14, True),
    ])
    bgm = lowpass(bgm, 6)

    # 雨（三日目〜スマホ、四日目）
    rng = np.random.default_rng(3)
    rain = lowpass(rng.standard_normal(n).astype(np.float32), 12) * 0.05
    mask = np.zeros(n, dtype=np.float32)
    for a, b in ((sc["day3"]["start"], sc["phone"]["end"]), (sc["day4"]["start"], total)):
        i, j = int(a * SR), int(b * SR)
        ramp = int(1.5 * SR)
        m = np.ones(j - i, dtype=np.float32)
        m[:ramp] = np.linspace(0, 1, ramp)
        m[-ramp:] = np.linspace(1, 0, ramp)
        mask[i:j] = np.maximum(mask[i:j], m)
    rain *= mask

    # 効果音：目覚まし、スマホの振動
    sfx = np.zeros(n, dtype=np.float32)
    def put(at, s):
        i = int(at * SR)
        sfx[i:i + len(s)] += s[: n - i]
    beep = np.concatenate([note(2093, 0.12, 0.25), np.zeros(int(0.08 * SR), np.float32)] * 4)
    for d in ("day1", "day2", "day4"):
        put(sc[d]["start"] + 0.2, beep)
    tt = np.arange(int(0.5 * SR)) / SR
    buzz = (np.sign(np.sin(2 * np.pi * 150 * tt)) * 0.08 * np.minimum(1, (0.5 - tt) / 0.05)).astype(np.float32)
    put(sc["phone"]["lines"][1]["start"] - 0.6, lowpass(buzz, 20))

    mix = voice_track + bgm + rain + sfx
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
