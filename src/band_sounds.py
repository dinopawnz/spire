"""Sounds for the lounge stage band, synthesised (no sample library / sound API available):
piano notes (additive partials, hammer + soft decay), guitar chord strums and harp notes (Karplus-Strong plucked strings),
a drum kit (kick, snare, hi-hat, toms, crash). All in C major pentatonic so any mash of clicks sounds musical.
Writes out/snd/band_<inst>_<k>.mp3 (mono, 44.1 kHz)."""
import os, subprocess, numpy as np, wave
SR = 44100; OUT = '/home/claude/spire/out/snd/'; os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)
f = lambda n: 440.0 * 2 ** ((n - 69) / 12)            # MIDI note -> Hz

def save(name, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    fade = int(0.02 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    tmp = '/tmp/' + name + '.wav'
    with wave.open(tmp, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-ac', '1', '-b:a', '96k', OUT + name + '.mp3'], check=True)

def reverb(x, wet=0.18):
    out = x.copy()
    for d, g in ((0.031, 0.5), (0.047, 0.42), (0.071, 0.35), (0.113, 0.27), (0.163, 0.2), (0.239, 0.13)):
        k = int(d * SR); out[k:] += x[:-k] * g * wet * 3
    return out

def piano(n, dur=2.6):
    t = np.arange(int(dur * SR)) / SR; fr = f(n); x = np.zeros_like(t)
    for h in range(1, 9):
        B = 0.0004; fh = fr * h * np.sqrt(1 + B * h * h)
        x += (0.6 ** (h - 1)) * np.sin(2 * np.pi * fh * t + rng.uniform(0, 6)) * np.exp(-t * (1.2 + 0.7 * h))
    x *= np.minimum(1, t / 0.004)
    x += 0.15 * rng.standard_normal(len(t)) * np.exp(-t * 90)          # the hammer
    return reverb(x)

def pluck(fr, dur, bright=0.5, decay=0.996):
    N = int(SR / fr); buf = rng.uniform(-1, 1, N)
    for _ in range(int(bright * 3)): buf = 0.5 * (buf + np.roll(buf, 1))
    out = np.zeros(int(dur * SR))
    for i in range(len(out)):
        out[i] = buf[i % N]; buf[i % N] = decay * 0.5 * (buf[i % N] + buf[(i + 1) % N])
    return out

def strum(notes, dur=2.4):
    x = np.zeros(int(dur * SR))
    for k, n in enumerate(notes):
        s = pluck(f(n), dur, bright=1.0, decay=0.9975) * (0.9 - 0.05 * k); o = int(k * 0.022 * SR); x[o:] += s[:len(x) - o]
    return reverb(x, 0.22)

def harp(n, dur=2.8):
    x = pluck(f(n), dur, bright=0.3, decay=0.9988)
    x += 0.4 * pluck(f(n) * 2, dur, bright=0.2, decay=0.998)
    return reverb(x, 0.3)

def drum(kind):
    dur = {'kick': 0.6, 'snare': 0.45, 'hihat': 0.25, 'tom_hi': 0.6, 'tom_lo': 0.8, 'crash': 2.2}[kind]
    t = np.arange(int(dur * SR)) / SR; nz = rng.standard_normal(len(t))
    if kind == 'kick':
        fr = 50 + 110 * np.exp(-t * 30); x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 7) + 0.2 * nz * np.exp(-t * 200)
    elif kind == 'snare':
        x = 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 20) + 0.8 * np.convolve(nz, np.ones(3) / 3, 'same') * np.exp(-t * 14)
    elif kind == 'hihat':
        x = (nz - np.convolve(nz, np.ones(8) / 8, 'same')) * np.exp(-t * 40)
    elif kind in ('tom_hi', 'tom_lo'):
        f0 = 170 if kind == 'tom_hi' else 105
        fr = f0 * (1 + 0.5 * np.exp(-t * 18)); x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 6) + 0.12 * nz * np.exp(-t * 60)
    else:
        hp = nz - np.convolve(nz, np.ones(5) / 5, 'same')
        x = hp * np.exp(-t * 2.2) + 0.3 * np.sin(2 * np.pi * 410 * t) * np.sin(2 * np.pi * 593 * t) * np.exp(-t * 3)
    return reverb(x, 0.12)

if __name__ == '__main__':
    PENTA = [60, 62, 64, 67, 69, 72, 74, 76]                     # C D E G A C D E
    for k, n in enumerate(PENTA): save('band_piano_%d' % k, piano(n))
    CHORDS = [[43, 47, 50, 55, 59, 67], [48, 52, 55, 60, 64], [50, 57, 62, 66], [40, 47, 52, 55, 59, 64]]   # G C D Em
    for k, ch in enumerate(CHORDS): save('band_guitar_%d' % k, strum(ch))
    for k, n in enumerate([67, 69, 72, 74, 76, 79, 81, 84]): save('band_harp_%d' % k, harp(n))
    for kind in ('kick', 'snare', 'hihat', 'tom_hi', 'tom_lo', 'crash'): save('band_drum_' + kind, drum(kind))
    print('band sounds:', sorted(x for x in os.listdir(OUT) if x.startswith('band_')))
