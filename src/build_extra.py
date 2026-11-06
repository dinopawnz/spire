"""small extra models for the game: the finals-vault glass door (closed for everyone except finalists)."""
import math
from glb import *
from kit import *
m = Mesh(); W, H = 2.9, 3.9
for s in (-1, 1):
    quad(m, 'glass', W / 2 - 0.08, H - 0.2, T(s * W / 4, H / 2, 0), double=True)
    bevel_box(m, 'brass', 0.08, H, 0.1, 0.02, m=T(s * (W / 2 - 0.04), H / 2, 0))
    bevel_box(m, 'brass', 0.06, H - 0.1, 0.08, 0.015, m=T(s * 0.04, H / 2, 0))
    for y in (0.9, 2.0, 3.1): tube(m, 'brass', [(s * 0.15, y, 0.06), (s * 0.15, y + 0.5, 0.06)], 0.02, 6)
    lathe(m, 'gold', [(0.0, 0), (0.05, 0), (0.05, 0.02), (0.0, 0.03)], 10, m=M(T(s * 0.25, 1.15, 0.07), Rx(90)))
for y in (0.05, H - 0.05): bevel_box(m, 'brass', W, 0.1, 0.12, 0.02, m=T(0, y, 0))
bevel_box(m, 'dark', W + 0.3, 0.5, 0.3, 0.04, m=T(0, H + 0.25, 0))
quad(m, 'gold', 1.4, 0.18, T(0, H + 0.25, 0.16))
print(write('/home/claude/spire/out/glb/sp_vault_door.glb', m, MATS))

# the placer cube's logo block: the MUDWATER logo on a dark carved board
m = Mesh(); LOGO = '/home/claude/spire/tmp/ext/mw_logo_0.png'
w, h = 2.6, 2.6 * 323 / 1334
for s in (1, -1): quad(m, 'logo', w, h, M(Ry(0 if s > 0 else 180), T(0, h / 2 + 0.15, 0.07)))
bevel_box(m, 'dark', w + 0.3, h + 0.3, 0.12, 0.03, m=T(0, h / 2 + 0.15, 0))
mats = dict(MATS); mats['logo'] = dict(tex=LOGO, emis_tex=LOGO, emis=(0.5, 0.42, 0.3), alpha='MASK', cutoff=0.4, double=True)
print(write('/home/claude/spire/out/glb/sp_logo_block.glb', m, mats))

# game sound effects (synthesised)
import numpy as np, wave, subprocess, os
SR = 44100; rng = np.random.default_rng(9)
def save(name, x):
    x = np.clip(x / (np.abs(x).max() + 1e-9) * 0.9, -1, 1); p = '/home/claude/spire/out/snd/' + name
    with wave.open(p + '.wav', 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p + '.wav', '-b:a', '96k', p + '.mp3']); os.remove(p + '.wav')
def tone(f, d, decay=3.0, harm=((1, 1), (2, .4), (3, .2))):
    t = np.arange(int(SR * d)) / SR; return sum(a * np.sin(2 * np.pi * f * k * t) for k, a in harm) * np.exp(-t * decay)
def mix(parts, total):
    y = np.zeros(int(SR * total))
    for t0, s in parts: i = int(t0 * SR); y[i:i + len(s)] += s[:max(0, len(y) - i)]
    return y
# pour: gurgling stream
t = np.arange(int(SR * 2.4)) / SR; n = rng.normal(0, 1, len(t))
from numpy.fft import rfft, irfft
spec = rfft(n); fr = np.fft.rfftfreq(len(n), 1 / SR); spec *= np.exp(-((fr - 900) / 700) ** 2); n = irfft(spec, len(n))
gurg = 1 + 0.6 * np.sin(2 * np.pi * (6 + 3 * np.sin(2 * np.pi * 0.7 * t)) * t)
save('pour', n * gurg * np.minimum(1, t * 8) * np.minimum(1, (2.4 - t) * 4))
# wrong: a sour descending bwomp + a frog croak
t = np.arange(int(SR * 1.2)) / SR; f = 330 * np.exp(-t * 1.2)
bw = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 * np.exp(-t * 2.5)
cr = mix([(0.75, np.sin(2 * np.pi * 95 * np.arange(int(SR * .3)) / SR) * (rng.random(int(SR * .3)) > .5) * np.exp(-np.arange(int(SR * .3)) / SR * 8))], 1.2)
save('wrong', bw + cr * 0.8)
# found: a rising sparkle of bells
save('found', mix([(i * 0.11, tone(f, 1.6, 2.5)) for i, f in enumerate([523, 659, 784, 1047, 1319, 1568])], 2.4))
# finals: a drum roll into a big chord
t = np.arange(int(SR * 2.0)) / SR; roll = rng.normal(0, 1, len(t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * t) ** 2) * np.minimum(1, t / 1.5) * 0.5
save('finals', mix([(0, roll), (2.0, tone(262, 2.5, 1.2) + tone(330, 2.5, 1.2) + tone(392, 2.5, 1.2) + 0.6 * tone(131, 2.5, 1.0))], 4.5))
# winner: brassy fanfare
brass = lambda f, d: tone(f, d, 0.8, ((1, 1), (2, .7), (3, .5), (4, .3), (5, .2)))
save('winner', mix([(0, brass(392, .25)), (.25, brass(392, .25)), (.5, brass(392, .25)), (.75, brass(523, 1.6) + brass(659, 1.6) + brass(784, 1.6))], 3.0))
print('sounds ok', sorted(os.listdir('/home/claude/spire/out/snd')))

# frosted glass sleeve for the finals vault (hides the vault until the host starts the finals; the game sinks it away)
m = Mesh(); RV = 8.88; H0, H1 = 0.6, 7.5
lathe(m, 'frost', [(RV, H0), (RV, H1)], 64, uvs_u=8)
lathe(m, 'frostrim', [(RV - 0.04, H0), (RV + 0.02, H0), (RV + 0.02, H0 + 0.05), (RV - 0.04, H0 + 0.05)], 64)
mats = dict(MATS)
mats['frost'] = dict(tex=TEX + 'glass.png', color=(0.9, 0.95, 0.93, 0.9), emis=(0.12, 0.14, 0.13), rough=0.9, alpha='BLEND', double=True)
mats['frostrim'] = dict(color=(0.85, 0.9, 0.88, 1), rough=0.6)
print(write('/home/claude/spire/out/glb/sp_vault_frost.glb', m, mats))
