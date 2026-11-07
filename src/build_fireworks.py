"""(v55, owner: "those are the absolute worst fireworks... add real fireworks. the coolest looking fireworks you can find... remove the
sound") REAL FIREWORK SHELLS for the CELEBRATE button. Each burst is ONE small glowing model (so a big show stays cheap), drawn as
hundreds of tapered light streaks (two crossed ribbons each, so they look right from every side) with a white-hot head fading into a
coloured tail. Every shell comes in 3 stages that the game swaps in turn:  _a the burst (sharp streaks)  ->  _b the streaks droop and
dim under gravity  ->  _c only glittering embers are left. The game grows _a out of a point, lets the shell sink, then swaps stages.
Types: PEONY (sphere of streaks), CHRYSANTHEMUM (long streaks with crackling tips), WILLOW (long golden trails that hang down), RING
(a tilted halo + inner sparkle), PALM (8 thick fronds with glitter), plus a ROCKET (a rising spark with a tail).
Writes out/glb/fw_*.glb and prints the list.   python3 build_fireworks.py"""
import math, io, sys
import numpy as np
from PIL import Image
sys.argv = sys.argv[:1]
from glb import Mesh, write
OUT = '/home/claude/spire/out/glb/'
rng = np.random.default_rng(2026)

COLS = {  # tail colour, head colour (rgb 0..1)
    'gold': ((1.0, 0.55, 0.12), (1.0, 0.95, 0.7)), 'red': ((1.0, 0.12, 0.08), (1.0, 0.75, 0.6)), 'blue': ((0.15, 0.35, 1.0), (0.75, 0.9, 1.0)),
    'green': ((0.15, 1.0, 0.35), (0.85, 1.0, 0.8)), 'purple': ((0.75, 0.2, 1.0), (1.0, 0.8, 1.0)), 'silver': ((0.7, 0.8, 1.0), (1.0, 1.0, 1.0)),
    'teal': ((0.1, 0.95, 0.85), (0.85, 1.0, 1.0)), 'pink': ((1.0, 0.3, 0.7), (1.0, 0.85, 0.95)),
}


def grad_png(tail, head, dim=1.0, dots=False):
    """a 256 x 8 strip: u=0 the faded tail -> u=1 the white-hot head (alpha fades the tail out)"""
    W = 256; u = np.linspace(0, 1, W)
    rgb = np.zeros((W, 3)); a = np.zeros(W)
    for i, t in enumerate(u):
        if t < 0.75: c = np.array(tail) * (0.25 + 0.75 * t / 0.75)
        else: k = (t - 0.75) / 0.25; c = np.array(tail) * (1 - k) + np.array(head) * k
        rgb[i] = c * dim; a[i] = (t ** 1.6) if not dots else 1.0
    img = np.zeros((8, W, 4)); img[..., :3] = rgb[None]; img[..., 3] = a[None]
    if dots: img[0] = img[-1] = 0
    im = Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8), 'RGBA'); b = io.BytesIO(); im.save(b, 'PNG'); return b.getvalue()


def mat(col, dim=1.0, dots=False):
    t, h = COLS[col]; png = grad_png(t, h, dim, dots)
    return dict(tex=png, emis_tex=png, emis=(1.0, 1.0, 1.0), emis_strength=7.0 * dim, color=(1, 1, 1, 1), rough=1.0, alpha='BLEND', double=True, unlit=True)


def perp(d):
    a = np.array([0.0, 1.0, 0.0]) if abs(d[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = np.cross(d, a); e1 /= np.linalg.norm(e1); e2 = np.cross(d, e1); return e1, e2


def ribbon(m, mt, pts, w0, w1, u0=0.0, u1=1.0):
    """a tapered streak along pts (2+ points), two crossed ribbons; u runs u0 (tail) -> u1 (head)"""
    pts = np.asarray(pts, float); n = len(pts)
    for k in range(n - 1):
        p0, p1 = pts[k], pts[k + 1]; d = p1 - p0; L = np.linalg.norm(d)
        if L < 1e-6: continue
        d /= L; e1, e2 = perp(d)
        ta, tb = k / (n - 1), (k + 1) / (n - 1)
        wa, wb = w0 + (w1 - w0) * ta, w0 + (w1 - w0) * tb
        ua, ub = u0 + (u1 - u0) * ta, u0 + (u1 - u0) * tb
        for e, en in ((e1, e2), (e2, e1)):
            P = [p0 - e * wa / 2, p0 + e * wa / 2, p1 + e * wb / 2, p1 - e * wb / 2]
            m.add(mt, P, [en] * 4, [[ua, 0.1], [ua, 0.9], [ub, 0.9], [ub, 0.1]], [0, 1, 2, 0, 2, 3])


def sparkle(m, mt, p, s):
    """a little 4-point star of light (3 crossed quads), for embers / crackle"""
    for e1, e2 in (((1, 0, 0), (0, 1, 0)), ((0, 1, 0), (0, 0, 1)), ((1, 0, 0), (0, 0, 1))):
        e1, e2 = np.array(e1, float) * s, np.array(e2, float) * s; n = np.cross(e1, e2)
        P = [p - e1 - e2, p + e1 - e2, p + e1 + e2, p - e1 + e2]
        m.add(mt, P, [n] * 4, [[0.9, 0.1], [1.0, 0.1], [1.0, 0.9], [0.9, 0.9]], [0, 1, 2, 0, 2, 3])


def sphere_dirs(n, jitter=0.06):
    i = np.arange(n) + 0.5; th = np.arccos(1 - 2 * i / n); ph = np.pi * (1 + 5 ** 0.5) * i
    d = np.c_[np.sin(th) * np.cos(ph), np.cos(th), np.sin(th) * np.sin(ph)] + rng.normal(0, jitter, (n, 3))
    return d / np.linalg.norm(d, axis=1, keepdims=True)


def path(d, R, g, steps=6, t0=0.0, t1=1.0):
    """a spark's flight: out along d to radius R, sinking by g (metres at the end) - a gentle gravity curve"""
    return [d * R * t + np.array([0, -g * t * t, 0]) for t in np.linspace(t0, t1, steps)]


def shell(kind, col, col2=None):
    """(v55b, owner: "are those really the best fireworks we can get?") denser, brighter shells: 300-500 streaks with a white-hot star at
    every head, an inner 'pistil' burst in a second colour, colour-changing stars (stage _b turns the outer stars col2), and a dense
    crackling cloud of glitter at the end (_c)"""
    col2 = col2 or col
    out = []
    for st in 'abc':
        m = Mesh(); dim = {'a': 1.0, 'b': 0.75, 'c': 0.9}[st]
        mats = {'s': mat(col, dim, dots=(st == 'c')), 't': mat(col2, dim, dots=(st == 'c')), 'w': mat('silver', dim, dots=True), 'g': mat('gold', dim, dots=True)}
        R = 10.0
        if kind == 'peony':                                        # big round burst + inner pistil, colour change, crackle
            for i, d in enumerate(sphere_dirs(360)):
                if st == 'a': ribbon(m, 's', path(d, R, 0.5, 2, 0.5, 1.0), 0.05, 0.2); sparkle(m, 'w', d * R - [0, 0.5, 0], 0.16)
                elif st == 'b': ribbon(m, 't', path(d, R * 1.1, 2.4, 4, 0.55, 1.0), 0.04, 0.17); sparkle(m, 't', path(d, R * 1.1, 2.4, 2)[-1], 0.14)
                else:
                    tip = path(d, R * 1.14, 3.8, 2)[-1]; sparkle(m, 'w' if i % 2 else 'g', tip + rng.normal(0, 0.35, 3), 0.1 + 0.07 * rng.random())
            for d in sphere_dirs(120):
                if st == 'a': ribbon(m, 't', path(d, R * 0.45, 0.2, 2, 0.4, 1.0), 0.04, 0.15); sparkle(m, 'w', d * R * 0.45, 0.13)
                elif st == 'b': sparkle(m, 's', path(d, R * 0.5, 1.0, 2)[-1], 0.13)
        elif kind == 'chrys':                                      # long streaming tails + crackle at the tips
            for i, d in enumerate(sphere_dirs(320)):
                if st == 'a': ribbon(m, 's', path(d, R * 1.1, 0.8, 3, 0.08, 1.0), 0.03, 0.16); sparkle(m, 'w', path(d, R * 1.1, 0.8, 2)[-1], 0.14)
                elif st == 'b':
                    ribbon(m, 's', path(d, R * 1.18, 2.8, 5, 0.4, 1.0), 0.03, 0.11)
                    tip = path(d, R * 1.18, 2.8, 2)[-1]
                    for _ in range(2): sparkle(m, 't', tip + rng.normal(0, 0.5, 3), 0.11)
                else:
                    tip = path(d, R * 1.22, 4.2, 2)[-1]
                    for _ in range(3): sparkle(m, 'w', tip + rng.normal(0, 0.8, 3), 0.08 + 0.06 * rng.random())
        elif kind == 'willow':                                     # golden kamuro: thick glittering trails that hang right down
            for i, d in enumerate(sphere_dirs(240, 0.08)):
                if st == 'a': ribbon(m, 's', path(d, R * 0.95, 1.4, 5, 0.05, 1.0), 0.05, 0.18); sparkle(m, 'g', path(d, R * 0.95, 1.4, 2)[-1], 0.15)
                elif st == 'b':
                    ribbon(m, 's', path(d, R * 1.05, 7.5, 9, 0.0, 1.0), 0.05, 0.14)
                    for p in path(d, R * 1.05, 7.5, 6)[2:]: sparkle(m, 'g', p + rng.normal(0, 0.25, 3), 0.07)
                else:
                    ribbon(m, 's', path(d, R * 1.1, 12.0, 9, 0.35, 1.0), 0.04, 0.1)
                    for p in path(d, R * 1.1, 12.0, 5)[2:]: sparkle(m, 'g', p + rng.normal(0, 0.4, 3), 0.07)
        elif kind == 'ring':                                       # a double halo (tilted by the game) + a sparkling heart
            for (rr, n, mt) in ((1.0, 140, 's'), (0.62, 90, 't')):
                for i in range(n):
                    a = 2 * math.pi * i / n; d = np.array([math.cos(a), rng.normal(0, 0.015), math.sin(a)]); d /= np.linalg.norm(d)
                    if st == 'a': ribbon(m, mt, path(d, R * rr, 0.3, 2, 0.55, 1.0), 0.07, 0.24); sparkle(m, 'w', d * R * rr, 0.16)
                    elif st == 'b': ribbon(m, mt, path(d, R * rr * 1.06, 1.8, 3, 0.65, 1.0), 0.05, 0.18); sparkle(m, mt, path(d, R * rr * 1.06, 1.8, 2)[-1], 0.14)
                    else: sparkle(m, 'w' if i % 2 else 'g', path(d, R * rr * 1.08, 3.0, 2)[-1] + rng.normal(0, 0.2, 3), 0.12)
            for d in sphere_dirs(60):
                if st == 'a': sparkle(m, 'g', d * R * 0.2 * rng.random(), 0.16)
        elif kind == 'palm':                                       # 9 thick fronds bending over, glitter falling off them, a core
            for i in range(9):
                a = 2 * math.pi * i / 9; d = np.array([math.cos(a) * 0.8, 0.6, math.sin(a) * 0.8]); d /= np.linalg.norm(d)
                if st == 'a': ribbon(m, 's', path(d, R, 2.0, 7, 0.04, 1.0), 0.3, 0.6); sparkle(m, 'w', path(d, R, 2.0, 2)[-1], 0.35)
                elif st == 'b':
                    ribbon(m, 's', path(d, R * 1.05, 5.0, 9, 0.15, 1.0), 0.22, 0.42)
                    for p in path(d, R * 1.05, 5.0, 14)[3:]:
                        for _ in range(2): sparkle(m, 'g', p + rng.normal(0, 0.45, 3) - [0, rng.random() * 1.5, 0], 0.1)
                else:
                    for p in path(d, R * 1.1, 7.0, 14)[2:]:
                        for _ in range(2): sparkle(m, 'g', p + rng.normal(0, 0.7, 3) - [0, rng.random() * 3.0, 0], 0.09)
            for d in sphere_dirs(80):
                if st == 'a': ribbon(m, 't', path(d, R * 0.4, 0.2, 2, 0.3, 1.0), 0.04, 0.14)
                elif st == 'b': sparkle(m, 't', path(d, R * 0.45, 1.0, 2)[-1], 0.12)
        name = 'fw_%s_%s%s_%s.glb' % (kind, col, ('_' + col2) if col2 != col else '', st)
        write(OUT + name, m, mats); out.append(name)
    return out


def rocket():
    m = Mesh(); mats = {'s': mat('gold', 1.0)}
    ribbon(m, 's', [[0, -4.0, 0], [0, 0, 0]], 0.02, 0.14)               # the tail below the spark
    sparkle(m, 's', np.array([0.0, 0.0, 0.0]), 0.22)
    write(OUT + 'fw_rocket.glb', m, mats); return ['fw_rocket.glb']


if __name__ == '__main__':
    made = rocket()
    for (k, c, c2) in (('peony', 'red', 'gold'), ('peony', 'blue', 'silver'), ('peony', 'green', 'gold'), ('peony', 'purple', 'pink'), ('peony', 'teal', 'silver'),
                       ('chrys', 'gold', 'silver'), ('chrys', 'red', 'gold'), ('chrys', 'blue', 'teal'),
                       ('willow', 'gold', None), ('ring', 'pink', 'gold'), ('ring', 'teal', 'blue'), ('ring', 'gold', 'red'), ('palm', 'gold', 'silver'), ('palm', 'green', 'gold')):
        made += shell(k, c, c2)
    import os
    print(len(made), 'files,', sum(os.path.getsize(OUT + f) for f in made) // 1024, 'KB')
    print(sorted(set(f.rsplit('_', 1)[0] for f in made if f != 'fw_rocket.glb')))
