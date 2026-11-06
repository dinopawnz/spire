"""THE MUDWATER SWAMP BLUES - original background music for the Spire (like the castle's "Pink Citadel Waltz").
A slow swing jazz blues in F, 92 bpm, three 12-bar choruses (~94 s), seamless loop:
  piano comping + a bluesy melody (the castle's recorded piano notes, piano_<midi>.mp3), a walking upright bass,
  brushes + ride cymbal + soft kick, a harp shimmer into the loop, crickets and the odd frog under it all.
Writes out/snd/swamp_jazz_00.mp3 / _01.mp3 (two halves played back to back, like the castle) and prints their lengths in ms."""
import os, subprocess, wave, numpy as np
SR = 44100; OUT = '/home/claude/spire/out/snd/'; SAMP = '/home/claude/castle_repo/'
rng = np.random.default_rng(1927)
BPM = 92; BEAT = 60.0 / BPM; BAR = 4 * BEAT; NBARS = 36
L = int(NBARS * BAR * SR); TAIL = int(4 * SR)
mix = np.zeros(L + TAIL)
f = lambda n: 440.0 * 2 ** ((n - 69) / 12)

def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
PIANO = {m: load(SAMP + 'piano_%d.mp3' % m) for m in range(48, 84)}
HARP = {int(p[5:-4]): load(SAMP + p) for p in os.listdir(SAMP) if p.startswith('harp_') and p.endswith('.mp3')}

def put(x, t, g=1.0):
    i = int(t * SR); n = min(len(x), len(mix) - i)
    if n > 0: mix[i:i + n] += x[:n] * g

def pnote(m, t, g=0.5, dur=None):
    while m < 48: m += 12
    while m > 83: m -= 12
    x = PIANO[m].copy()
    if dur:                                                          # damp the note (release) after dur seconds
        k = int(dur * SR)
        if k < len(x): x[k:] *= np.exp(-np.arange(len(x) - k) / (0.12 * SR))
    put(x, t, g)

def bass(m, t, g=0.5, dur=None):
    """(v29, owner: the synth bass sounded robotic) the walking bass is the castle's RECORDED piano, played an octave
    (or two) below its lowest sample by slowing it down: a warm, real left-hand stride bass"""
    dur = dur or BEAT * 0.95
    src = m; shift = 0
    while src < 48: src += 12; shift += 1
    x = PIANO[min(src, 83)]
    for _ in range(shift):                                             # each octave down: play the sample at half speed
        x = np.interp(np.arange(0, len(x), 0.5), np.arange(len(x)), x)
    k = int(dur * SR); x = x[: int((dur + 0.5) * SR)].copy()
    if k < len(x): x[k:] *= np.exp(-np.arange(len(x) - k) / (0.07 * SR))
    put(x, t, g * 1.6)

def bass_synth(m, t, g=0.55, dur=None):
    dur = dur or BEAT * 0.95; n = int((dur + 0.4) * SR); tt = np.arange(n) / SR; fr = f(m)
    x = sum((0.85 ** h) * np.sin(2 * np.pi * fr * (h + 1) * tt) / (h + 1) for h in range(6))
    env = np.minimum(1, tt / 0.006) * np.exp(-tt * 2.2) * np.where(tt < dur, 1, np.exp(-(tt - dur) * 25))
    x = x * env + 0.05 * rng.standard_normal(n) * np.exp(-tt * 120)        # the finger on the string
    put(x, t, g)

def ride(t, g=0.07):
    n = int(1.0 * SR); tt = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * fr * tt) for fr in (3150, 4370, 5120, 6890)) * 0.25 + 0.6 * rng.standard_normal(n)
    x = (x - np.convolve(x, np.ones(6) / 6, 'same')) * np.exp(-tt * 4.0) * np.minimum(1, tt / 0.002)
    put(x, t, g)

def brush(t, g=0.05, dur=BEAT * 1.6):
    n = int(dur * SR); tt = np.arange(n) / SR; nz = rng.standard_normal(n)
    nz = nz - np.convolve(nz, np.ones(20) / 20, 'same')
    put(nz * np.sin(np.pi * tt / dur) ** 2, t, g)

def chick(t, g=0.08):
    n = int(0.12 * SR); tt = np.arange(n) / SR; nz = rng.standard_normal(n)
    put((nz - np.convolve(nz, np.ones(4) / 4, 'same')) * np.exp(-tt * 60), t, g)

def kick(t, g=0.22):
    n = int(0.4 * SR); tt = np.arange(n) / SR; fr = 48 + 50 * np.exp(-tt * 30)
    put(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 9), t, g)

def cricket(t, g=0.012):
    n = int(0.35 * SR); tt = np.arange(n) / SR
    put(np.sin(2 * np.pi * 4600 * tt) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * tt))) * np.sin(np.pi * tt / 0.35), t, g)

def frog(t, g=0.05):
    n = int(0.5 * SR); tt = np.arange(n) / SR; fr = 170 + 30 * np.sin(2 * np.pi * 3 * tt)
    x = sum(np.sin(2 * np.pi * np.cumsum(fr) * h / SR) / h for h in (1, 2, 3, 4))
    am = (np.sin(2 * np.pi * 22 * tt) > -0.2).astype(float) * np.where((tt < 0.18) | (tt > 0.26), 1, 0) * np.exp(-tt * 3)
    put(x * am, t, g)

# ---- the form: F jazz blues, (chord, root for the bass, voicing) per half bar
V = {'F7': [57, 63, 67, 74], 'Bb7': [56, 62, 67, 72], 'Cm7': [58, 63, 67, 74], 'Bdim': [59, 62, 65, 68], 'D7': [54, 60, 64, 69],
     'Gm7': [58, 62, 65, 69], 'C7': [58, 64, 69, 74], 'Am7': [55, 60, 64, 67]}
ROOT = {'F7': 41, 'Bb7': 34, 'Cm7': 36, 'Bdim': 35, 'D7': 38, 'Gm7': 31, 'C7': 36, 'Am7': 33}
FORM = [['F7'], ['Bb7'], ['F7'], ['Cm7', 'F7'], ['Bb7'], ['Bdim'], ['F7'], ['Am7', 'D7'], ['Gm7'], ['C7'], ['F7', 'D7'], ['Gm7', 'C7']]
chords = [FORM[b % 12] for b in range(NBARS)]
SW = 2 / 3                                                            # swing: the second eighth lands 2/3 through the beat
BLUES = [65, 68, 70, 71, 72, 75, 77]                                  # F Ab Bb B C Eb F

def swing(beat, off=0):                                               # time of beat (+ the swung "and" if off)
    return beat * BEAT + (SW * BEAT if off else 0)

# walking bass: root, chord tone, chord tone, chromatic approach into the next chord
for b in range(NBARS):
    halves = chords[b]
    nxt = chords[(b + 1) % NBARS][0]
    for beat in range(4):
        ch = halves[0] if (len(halves) == 1 or beat < 2) else halves[1]
        r = ROOT[ch]; t0 = b * BAR + beat * BEAT
        if beat == 0 or (len(halves) == 2 and beat == 2): m = r
        elif beat == 3:
            tgt = ROOT[nxt] if len(halves) == 1 or True else r
            m = tgt + (1 if rng.random() < 0.5 else -1)
        else: m = r + rng.choice([4, 7, 10, 12]) if 'm' not in ch else r + rng.choice([3, 7, 10])
        while m > 50: m -= 12
        while m < 28: m += 12
        bass(m, t0)

# piano comping: Charleston-ish stabs, voicing per chord, gentle and short
for b in range(NBARS):
    for i, ch in enumerate(chords[b]):
        hb = b * BAR + (i * 2 * BEAT if len(chords[b]) == 2 else 0)
        pattern = [(0, 0, 0.9), (1, 1, 0.5)] if len(chords[b]) == 2 else [[(0, 0, 0.9), (1, 1, 0.5), (3, 0, 0.6)], [(1, 0, 0.8), (2, 1, 0.5)], [(0, 1, 0.6), (2, 0, 0.9), (3, 1, 0.4)]][int(rng.integers(3))]
        for (bt, off, ln) in pattern:
            if len(chords[b]) == 2 and bt > 1: continue
            t0 = hb + swing(bt, off)
            for k, m in enumerate(V[ch]): pnote(m, t0 + k * 0.008, 0.16 if b < 12 else 0.12, dur=ln * BEAT)

# melody: chorus 2 (bars 12-23) a lazy blues line; chorus 3 (24-35) it answers itself an octave up, lighter
def phrase(b0, octave=0, g=0.4):
    t = b0 * BAR + swing(0, 1)
    motif = [rng.choice(BLUES[:5]) for _ in range(5)] + [65]
    for k, m in enumerate(motif):
        bt = k // 2 + (0 if k % 2 == 0 else 0); off = k % 2
        pnote(m + octave, b0 * BAR + swing(bt, off) + (0.0 if k < 5 else BEAT * 0.5), g, dur=BEAT * (0.9 if k < 5 else 2.6))
for b in range(12, 24, 2): phrase(b)
for b in range(24, 36, 4): phrase(b, 12, 0.28)

# drums: ride "ding ding-a ding ding-a", brushes on 2 and 4, foot hi-hat on 2 and 4, feathered kick
for b in range(NBARS):
    for beat in range(4):
        t0 = b * BAR + beat * BEAT
        ride(t0, 0.06 if beat % 2 == 0 else 0.075)
        if beat in (1, 3): ride(t0 + SW * BEAT, 0.04); chick(t0); brush(t0 - BEAT * 0.3)
        kick(t0, 0.12 if beat in (0, 2) else 0.06)

# harp shimmer over the last two bars, sliding back into the top of the loop
hk = sorted(HARP)
for k, m in enumerate(hk[-14:]):
    put(HARP[m], (NBARS - 2) * BAR + k * BEAT / 4, 0.18)

# the swamp: crickets all the way through, a frog now and then
t = 0.0
while t < NBARS * BAR:
    cricket(t, 0.01 + 0.006 * rng.random()); t += rng.uniform(0.6, 1.8)
for t in rng.uniform(0, NBARS * BAR - 1, 9): frog(float(t), 0.035)

# a small room reverb, then wrap the tail round so the loop is seamless
dry = mix.copy()
for d, g in ((0.029, 0.42), (0.043, 0.36), (0.067, 0.3), (0.101, 0.24), (0.149, 0.18), (0.211, 0.12), (0.293, 0.08)):
    k = int(d * SR); mix[k:] += dry[:-k] * g * 0.5
out = mix[:L].copy(); out[:TAIL] += mix[L:L + TAIL]
out = out / np.max(np.abs(out)) * 0.9
half = (NBARS // 2) * int(BAR * SR) if False else int((NBARS // 2) * BAR * SR)
parts = [out[:half], out[half:]]
lens = []
for i, p in enumerate(parts):
    tmp = '/tmp/swamp_jazz_%02d.wav' % i
    with wave.open(tmp, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((p * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-ac', '1', '-b:a', '112k', OUT + 'swamp_jazz_%02d.mp3' % i], check=True)
    lens.append(round(len(p) / SR * 1000))
print('MUSIC_PARTS', lens, 'total %.1f s' % (sum(lens) / 1000))
