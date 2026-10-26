"""script.json → 英文を1行ずつ読み上げ → build/timeline.json と BGM入りの build/audio.wav

使い方: python3 build_audio.py
音声:
  - 環境変数 FISH_AUDIO_API_KEY があり、script.json の voice.fish_reference_id が入っていれば FishAudio
  - なければ試作用に edge-tts（本番では使わない）
必要: ffmpeg, numpy（edge-tts を使うときは edge-tts）
"""
import json
import os
import subprocess
import sys
import urllib.request
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 48000

PACE = {
    "intro": 2.6,     # タイトルとフックを見せる時間
    "gap_line": 0.55,  # 行と行のあいだ（声に出して追いかける余裕）
    "outro": 3.2,     # 単語まとめ・フォローのお願い
}


def tts_fish(text, ref_id, out_mp3):
    body = json.dumps({"text": text, "reference_id": ref_id, "format": "mp3", "normalize": True}).encode()
    req = urllib.request.Request(
        "https://api.fish.audio/v1/tts", data=body, method="POST",
        headers={"Authorization": "Bearer " + os.environ["FISH_AUDIO_API_KEY"],
                 "Content-Type": "application/json",
                 "model": os.environ.get("FISH_AUDIO_MODEL", "s1")})
    with urllib.request.urlopen(req) as r, open(out_mp3, "wb") as f:
        f.write(r.read())


def tts_edge(text, voice, rate, out_mp3):
    cmd = ["edge-tts", "--voice", voice, f"--rate={rate}", "--text", text, "--write-media", out_mp3]
    if os.environ.get("HTTPS_PROXY"):
        cmd[1:1] = ["--proxy", os.environ["HTTPS_PROXY"]]
    subprocess.run(cmd, check=True, capture_output=True)


def load_mono(path):
    raw = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).copy()
    # 前後の無音を詰める（行の切り替えとハイライトを合わせるため）
    loud = np.where(np.abs(x) > 0.01)[0]
    return x[max(0, loud[0] - int(0.03 * SR)): loud[-1] + int(0.08 * SR)] if len(loud) else x


HZ = lambda m: 440.0 * 2 ** ((m - 69) / 12)
CHORDS = [(48, 52, 55, 59), (45, 48, 52, 55), (41, 45, 48, 52), (43, 47, 50, 55)]  # Cmaj7 Am7 Fmaj7 G


def bgm(n):
    """やわらかいパッド＋ゆっくりした高音。声のじゃまにならない音量。"""
    out = np.zeros(n, dtype=np.float32)
    bar, t, k = 4.0, 0.0, 0
    while t < n / SR:
        ch = CHORDS[k % len(CHORDS)]
        dur = bar + 1.5
        tt = np.arange(int(dur * SR)) / SR
        env = np.minimum(1, tt / 1.2) * np.minimum(1, (dur - tt) / 1.2)
        w = sum(np.sin(2 * np.pi * HZ(m) * tt) + 0.25 * np.sin(2 * np.pi * HZ(m) * 2.003 * tt) for m in ch)
        seg = (w * env * 0.045 / len(ch)).astype(np.float32)
        for j, m in enumerate((ch[3] + 12, ch[1] + 12)):
            st = int(j * 2.0 * SR)
            e = np.exp(-1.8 * tt) * np.minimum(1, tt / 0.01)
            bell = (np.sin(2 * np.pi * HZ(m) * tt) * e * 0.03).astype(np.float32)
            seg[st:] += bell[: len(seg) - st]
        i = int(t * SR)
        out[i:i + len(seg)] += seg[: n - i]
        t += bar
        k += 1
    return np.convolve(out, np.ones(5, dtype=np.float32) / 5, mode="same").astype(np.float32)


def main():
    os.makedirs(BUILD, exist_ok=True)
    sc = json.load(open(os.path.join(HERE, "script.json"), encoding="utf-8"))
    v = sc["voice"]
    use_fish = bool(os.environ.get("FISH_AUDIO_API_KEY") and v.get("fish_reference_id"))
    engine = "fish" if use_fish else "edge"
    print("voice:", engine if use_fish else "edge-tts（試作用）")

    t = PACE["intro"]
    lines, clips = [], []
    for i, ln in enumerate(sc["lines"]):
        mp3 = os.path.join(BUILD, f"{engine}_{i:02d}.mp3")
        if not (os.path.exists(mp3) and os.path.getsize(mp3) > 0):
            if use_fish:
                tts_fish(ln["en"], v["fish_reference_id"], mp3)
            else:
                tts_edge(ln["en"], v["edge_voice"], v["edge_rate"], mp3)
        s = load_mono(mp3)
        dur = len(s) / SR
        lines.append({**ln, "start": round(t, 3), "end": round(t + dur, 3)})
        clips.append((t, s))
        t += dur + PACE["gap_line"]
    outro = t - PACE["gap_line"] + 0.6
    total = outro + PACE["outro"]

    n = int(total * SR) + SR
    voice = np.zeros(n, dtype=np.float32)
    for st, s in clips:
        i = int(st * SR)
        voice[i:i + len(s)] += s
    voice /= max(1e-6, np.abs(voice).max() / 0.9)
    mix = voice + bgm(n)
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    with wave.open(os.path.join(BUILD, "audio.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())

    timeline = {k: sc[k] for k in ("title_en", "title_ja", "hook", "level", "episode", "words")}
    timeline.update({"lines": lines, "outro": round(outro, 3), "duration": round(total, 3)})
    json.dump(timeline, open(os.path.join(BUILD, "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(lines)} lines, total {total:.1f}s")
    if total > 60:
        print("※ 60秒を超えています。YouTubeショートは3分まで投稿できますが、60秒以内が目安です", file=sys.stderr)


if __name__ == "__main__":
    main()
