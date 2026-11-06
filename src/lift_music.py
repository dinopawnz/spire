"""placeholder elevator music: a soft swampy bossa loop (electric piano, walking bass, brushed shaker, a little vibraphone tune).
16 bars at 104 bpm, seamless loop. Replaced by an ElevenLabs Music track once the key is in."""
import numpy as np, wave, subprocess, os
SR = 44100; BPM = 104; BEAT = 60 / BPM; BARS = 16; N = int(SR * BEAT * 4 * BARS)
y = np.zeros(N + SR * 3); rng = np.random.default_rng(4)
def note(m): return 440 * 2 ** ((m - 69) / 12)
def add(t0, sig, vol):
    i = int(t0 * SR); y[i:i + len(sig)] += sig * vol
def epiano(f, d):
    t = np.arange(int(SR * d)) / SR; env = np.exp(-t * 2.2) * np.minimum(1, t * 200)
    return env * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4) + 0.12 * np.sin(2 * np.pi * 7 * f * t) * np.exp(-t * 12))
def vib(f, d):
    t = np.arange(int(SR * d)) / SR; trem = 1 + 0.25 * np.sin(2 * np.pi * 5.5 * t)
    return np.exp(-t * 1.6) * np.minimum(1, t * 300) * trem * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 6))
def bass(f, d):
    t = np.arange(int(SR * d)) / SR; return np.exp(-t * 3) * np.minimum(1, t * 120) * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t))
# F major-ish ii-V-I with a bayou flavour: Fmaj7 Dm7 Gm7 C7 | Bbmaj7 Bbm6 Am7 D7 | Gm7 C7 Fmaj7 D7 | Gm7 C7 Fmaj7 C7
CH = [[53, 57, 60, 64], [50, 53, 57, 60], [55, 58, 62, 65], [48, 52, 55, 58], [58, 62, 65, 69], [58, 61, 65, 67], [57, 60, 64, 67], [50, 54, 57, 60],
      [55, 58, 62, 65], [48, 52, 55, 58], [53, 57, 60, 64], [50, 54, 57, 60], [55, 58, 62, 65], [48, 52, 55, 58], [53, 57, 60, 64], [48, 52, 55, 58]]
MEL = [72, None, 69, 70, 72, None, 74, 72, 70, None, 67, 69, 70, None, 72, 70, 69, None, 65, 67, 69, None, 72, 74, 76, None, 74, 72, 69, None, None, None]
for b, ch in enumerate(CH):
    t0 = b * 4 * BEAT
    # bossa comp: chord stabs on 1, the and-of-2, 4
    for off in (0, 1.5, 3.0):
        for m in ch: add(t0 + off * BEAT, epiano(note(m + 12), 1.2), 0.09)
    root = ch[0] - 12
    for k, (off, iv) in enumerate([(0, 0), (1.5, 7), (2, 7), (3.5, 0)]): add(t0 + off * BEAT, bass(note(root + iv), 0.6), 0.32)
    for s in range(8):
        n = rng.normal(0, 1, int(SR * 0.08)); env = np.exp(-np.arange(len(n)) / SR * (60 if s % 2 else 35))
        add(t0 + s * 0.5 * BEAT, n * env, 0.035 if s % 2 else 0.05)
    for h in range(2):
        m = MEL[(b * 2 + h) % len(MEL)]
        if m: add(t0 + h * 2 * BEAT, vib(note(m), 1.9), 0.16)
# wrap the tail round so the loop is seamless
tail = y[N:N + SR * 3].copy(); y = y[:N]; y[:len(tail)] += tail
y = y / np.abs(y).max() * 0.8
p = '/home/claude/spire/out/snd/lift_music'
with wave.open(p + '.wav', 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((y * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p + '.wav', '-b:a', '112k', p + '.mp3']); os.remove(p + '.wav')
print('lift_music.mp3', round(N / SR, 1), 's', os.path.getsize(p + '.mp3') // 1024, 'KB')
