"""効果音と BGM を数式で合成する（素材ライセンス不要）。各関数は 48kHz モノラル float32、ピーク 1.0 で返す。"""
import numpy as np

SR = 48000


def _t(dur):
    return np.arange(int(SR * dur)) / SR


def _norm(x):
    return (x / (np.max(np.abs(x)) or 1)).astype(np.float32)


def _lowpass(x, alpha):
    """1 次ローパス。alpha は定数か、x と同じ長さの配列"""
    a = np.broadcast_to(alpha, x.shape)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def _tone(freq, dur, decay, partials=((1, 1.0),)):
    t = _t(dur)
    return sum(a * np.sin(2 * np.pi * freq * k * t) for k, a in partials) * np.exp(-t / decay)


def _place(parts, total):
    out = np.zeros(int(SR * total), dtype=np.float64)
    for start, x in parts:
        s = int(SR * start)
        out[s:s + len(x)] += x[:len(out) - s]
    return out


def whoosh(dur=0.45):
    rnd = np.random.default_rng(1)
    t = _t(dur)
    sweep = np.sin(np.pi * t / dur)
    y = _lowpass(rnd.standard_normal(len(t)), 0.02 + 0.35 * sweep)
    return _norm(y * sweep ** 2)


def sparkle():
    bell = ((1, 1.0), (2.0, 0.25), (3.0, 0.1))
    notes = [_tone(f, 0.6, 0.18, bell) for f in (1568, 2093, 2637, 3136)]
    return _norm(_place([(i * 0.06, n) for i, n in enumerate(notes)], 0.85))


def shock():
    t = _t(0.45)
    freq = 50 + 110 * np.exp(-t / 0.06)
    body = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t / 0.14)
    click = np.random.default_rng(2).standard_normal(len(t)) * np.exp(-t / 0.008) * 0.5
    return _norm(body + click)


def question():
    t = _t(0.32)
    freq = 520 + 420 * np.clip(t / 0.18, 0, 1) ** 0.7
    y = np.sin(2 * np.pi * np.cumsum(freq) / SR) + 0.2 * np.sin(4 * np.pi * np.cumsum(freq) / SR)
    return _norm(y * np.minimum(t / 0.01, 1) * np.exp(-np.maximum(t - 0.15, 0) / 0.06))


def sad():
    parts, start = [], 0.0
    for f, d in ((392, 0.22), (370, 0.22), (349, 0.22), (330, 0.6)):
        t = _t(d)
        vib = 1 + (0.012 * np.sin(2 * np.pi * 6 * t) if d > 0.5 else 0)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        y = np.sin(ph) + 0.35 * np.sin(3 * ph) + 0.15 * np.sin(5 * ph)
        parts.append((start, y * np.minimum(t / 0.02, 1) * np.minimum((d - t) / 0.05, 1)))
        start += d
    return _norm(_lowpass(_place(parts, start), 0.25))


def car_pass(dur=1.6):
    t = _t(dur)
    x = t / dur
    freq = 85 + 70 * np.exp(-((x - 0.45) / 0.18) ** 2) - 20 * (x > 0.45) * (x - 0.45)
    saw = 2 * ((np.cumsum(freq) / SR) % 1) - 1
    amp = np.exp(-((x - 0.45) / 0.25) ** 2)
    return _norm(_lowpass(saw, 0.12) * amp)


def alarm(beeps=4):
    parts = []
    for i in range(beeps):
        t = _t(0.2)
        sq = np.sign(np.sin(2 * np.pi * (880 if i % 2 == 0 else 660) * t))
        parts.append((i * 0.26, sq * np.minimum(t / 0.005, 1) * np.minimum((0.2 - t) / 0.01, 1)))
    return _norm(_lowpass(_place(parts, beeps * 0.26), 0.3))


def ticking(dur, interval=0.5):
    tick = _tone(2200, 0.03, 0.006) + _tone(3400, 0.03, 0.004) * 0.5
    n = int(dur / interval) + 1
    return _norm(_place([(i * interval, tick * (1.0 if i % 2 == 0 else 0.7)) for i in range(n)], dur))


def chime():
    bell = ((1, 1.0), (2.76, 0.3), (5.4, 0.1))
    return _norm(_place([(0, _tone(1047, 1.0, 0.3, bell)), (0.16, _tone(1568, 1.2, 0.4, bell))], 1.4))


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def bgm(dur, bpm=76):
    """穏やかなループ BGM（C - Am - F - G）。パッド + オルゴール風アルペジオ + ベース"""
    chords = [(48, 52, 55, 60), (45, 52, 57, 60), (41, 53, 57, 60), (43, 55, 59, 62)]
    beat = 60 / bpm
    bar = 4 * beat
    out = np.zeros(int(SR * dur) + SR * 4)
    bars = int(dur / bar) + 1
    for b in range(bars):
        notes = chords[b % len(chords)]
        s0 = int(SR * b * bar)
        t = _t(bar + 1.0)
        env = np.minimum(t / 0.6, 1) * np.clip((bar + 1.0 - t) / 1.0, 0, 1)
        pad = sum(np.sin(2 * np.pi * _midi(n + 12) * d * t) for n in notes[1:] for d in (0.9985, 1.0015))
        out[s0:s0 + len(t)] += 0.10 * pad * env
        out[s0:s0 + len(t)] += 0.35 * np.sin(2 * np.pi * _midi(notes[0]) * t) * np.exp(-t / 1.2)
        arp = [notes[1], notes[2], notes[3], notes[2] + 12, notes[3], notes[2], notes[1] + 12, notes[3]]
        for k, n in enumerate(arp):
            tone = _tone(_midi(n + 12), 0.6, 0.18, ((1, 1.0), (2.0, 0.2)))
            a = int(SR * (b * bar + k * beat / 2))
            out[a:a + len(tone)] += 0.12 * tone
    out = _lowpass(out[:int(SR * dur)], 0.35)
    t = _t(dur)
    out *= np.minimum(t / 1.5, 1) * np.clip((dur - t) / 2.0, 0, 1)
    return _norm(out)
