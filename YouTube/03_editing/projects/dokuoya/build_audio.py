"""script.json → ナレーション（1行ずつ）→ build/timeline.json と BGM・効果音入りの build/audio.wav（リスト型の解説動画用）

使い方: python3 build_audio.py                              （横長の本編）
        python3 build_audio.py script_short.json build_short  （縦型ショート）
必要: edge-tts, ffmpeg, numpy
行は文字列のほか {"text", "pitch", "rate", "gain"} でも書ける（心の声など）。
台本の "pace" で間の長さを上書きできる（ショートは詰める）。
シーンの "map" は、短縮した行が元のシーンの何行目の絵に当たるか（例 [0, 3]）。
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "script.json")
BUILD = os.path.join(HERE, sys.argv[2] if len(sys.argv) > 2 else "build")
SR = 48000

PACE = {
    "gap_line": 0.45,   # 行と行のあいだ
    "gap_scene": 1.2,   # シーンとシーンのあいだ
    "card": 2.2,        # 「サイン1」などのカード（ナレーション前）
    "lead_in": 1.5,
    "tail": 4.0,
}


def expand(lines, mapping):
    """短縮した行を、元のシーンの行番号に並べ直す。

    飛ばした行は次の行と同じ時刻に始まる扱いにするので、
    絵の側は元の行番号のまま動く。
    """
    out = []
    for k, line in enumerate(lines):
        while len(out) <= mapping[k]:
            out.append(dict(line))
    return out


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
    script = json.load(open(SCRIPT, encoding="utf-8"))
    voice, rate = script["voice"], script["rate"]
    pace = {**PACE, **script.get("pace", {})}
    GAP_LINE, GAP_SCENE, CARD, LEAD_IN, TAIL = (pace[k] for k in ("gap_line", "gap_scene", "card", "lead_in", "tail"))

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
        if sc.get("map"):
            scene["lines"] = expand(scene["lines"], sc["map"])
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

    # BGM：全体は静かな和音、「もし当てはまったら」から明るい和音へ
    bgm = music(n, [
        (0, sc["after"]["start"], CHORDS_SAD, 0.07, False),
        (sc["after"]["start"], total, CHORDS_HOPE, 0.09, True),
    ])
    bgm = lowpass(bgm, 6)

    # 効果音：サインのカードごとにやわらかいチャイム
    sfx = np.zeros(n, dtype=np.float32)
    def put(at, s):
        i = int(at * SR)
        sfx[i:i + len(s)] += s[: n - i]
    chime = note(HZ(76), 1.2, 0.12)
    chime[int(0.12 * SR):] += note(HZ(83), 1.2 - 0.12, 0.08)[: len(chime) - int(0.12 * SR)]
    for s_ in timeline["scenes"]:
        if s_.get("card") or s_.get("num"):
            put(s_["start"] + 0.15, chime)

    mix = voice_track + bgm + sfx
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
