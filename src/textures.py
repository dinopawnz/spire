"""Seamless procedural textures for the Spire (wood, bark, rope, iron, brass, leather, moss, shingles, mud stone...).
Every map tiles perfectly (all noise is made in the frequency domain). Each texture also gets a normal map."""
import numpy as np, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = '/home/claude/spire/tex'
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(1234)

def noise(n, sx, sy=None, seed=None):
    """seamless gaussian noise blurred anisotropically: sx/sy = blur radius in pixels along x / y"""
    sy = sx if sy is None else sy
    r = np.random.default_rng(seed) if seed is not None else RNG
    w = r.standard_normal((n, n))
    fy = np.fft.fftfreq(n)[:, None]; fx = np.fft.fftfreq(n)[None, :]
    g = np.exp(-2 * (np.pi ** 2) * ((fx * sx) ** 2 + (fy * sy) ** 2))
    o = np.real(np.fft.ifft2(np.fft.fft2(w) * g))
    o -= o.mean(); o /= (o.std() + 1e-9); return o

def fbm(n, base, oct=5, aniso=1.0, seed=0):
    o = np.zeros((n, n)); amp = 1; tot = 0
    for k in range(oct):
        s = base / (2 ** k)
        o += amp * noise(n, max(0.5, s * aniso), max(0.5, s), seed + k); tot += amp; amp *= 0.55
    return o / tot

def norm01(a): a = a - a.min(); return a / (a.max() + 1e-9)

def to_img(rgb): return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))

def normal_map(h, strength=2.0):
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * strength
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * strength
    n = np.dstack([-dx, dy, np.ones_like(h)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    return to_img(n * 0.5 + 0.5)

def colorize(t, stops):
    """t 0..1 -> gradient through [(pos,(r,g,b)),...]"""
    t = np.clip(t, 0, 1); out = np.zeros(t.shape + (3,))
    ps = [p for p, _ in stops]; cs = np.array([c for _, c in stops], float) / 255
    for ch in range(3): out[..., ch] = np.interp(t, ps, cs[:, ch])
    return out

def save(name, rgb, h=None, strength=2.0, q=88, png=False):
    im = to_img(rgb) if not isinstance(rgb, Image.Image) else rgb
    p = os.path.join(OUT, name + ('.png' if png else '.jpg'))
    im.save(p, quality=q) if not png else im.save(p)
    if h is not None: normal_map(h, strength).save(os.path.join(OUT, name + '_n.jpg'), quality=90)
    return p

def planks(n=1024, rows=6, palette=None, name='wood_planks', seed=1, wear=0.5):
    """weathered swamp planks: grain runs along x; `rows` boards across the tile, with staggered butt joints"""
    pal = palette or [(0, (38, 24, 14)), (0.35, (78, 52, 30)), (0.65, (112, 78, 46)), (1, (150, 112, 70))]
    grain = fbm(n, 6, 5, aniso=18, seed=seed)
    rings = np.sin(grain * 9 + fbm(n, 40, 3, aniso=8, seed=seed + 9) * 6)
    big = fbm(n, 90, 3, seed=seed + 20)
    y = np.arange(n)[:, None] * np.ones((1, n)); x = np.ones((n, 1)) * np.arange(n)[None, :]
    bh = n / rows; row = (y // bh).astype(int)
    r = np.random.default_rng(seed)
    tint = r.uniform(-0.18, 0.18, rows); joint = r.uniform(0, n, rows)
    t = 0.5 + 0.18 * grain + 0.12 * rings + 0.12 * big + tint[row]
    # board gaps + joints
    edge = np.minimum(y % bh, bh - (y % bh))
    gap = np.clip(edge / 3.0, 0, 1)
    jd = np.abs(((x - joint[row]) + n / 2) % n - n / 2)
    gap = np.minimum(gap, np.clip(jd / 2.0, 0, 1))
    # nail heads
    rgb = colorize(t, pal)
    rgb *= (0.35 + 0.65 * gap)[..., None]
    for k in range(rows):
        for jx in (joint[k] + 8, joint[k] - 8):
            for yy in (k * bh + bh * 0.25, k * bh + bh * 0.75):
                cx, cy = int(jx) % n, int(yy)
                rr = 3
                rgb[max(0, cy - rr):cy + rr, max(0, cx - rr):cx + rr] = [0.18, 0.16, 0.15]
    # weathering: grey sun-bleach and dark water stains
    stain = norm01(fbm(n, 60, 4, seed=seed + 40))
    rgb = rgb * (1 - wear * 0.35 * (stain > 0.62)[..., None] * stain[..., None])
    bleach = norm01(fbm(n, 80, 3, seed=seed + 50)) ** 3 * wear
    grey = rgb.mean(-1, keepdims=True) * np.array([1.0, 1.0, 1.02])
    rgb = rgb * (1 - bleach[..., None] * 0.6) + grey * bleach[..., None] * 0.6
    h = 0.4 * grain + 0.3 * rings - 3 * (1 - gap)
    return save(name, rgb, h, 1.5)

def bark(n=1024, name='bark', seed=3, pal=None):
    pal = pal or [(0, (28, 20, 14)), (0.4, (62, 46, 32)), (0.75, (92, 74, 54)), (1, (120, 104, 84))]
    v = fbm(n, 5, 5, aniso=0.18, seed=seed)          # vertical ridges (grain along v)
    ridges = 1 - np.abs(np.sin(v * 6))
    cracks = np.clip(1 - np.abs(fbm(n, 12, 3, aniso=0.25, seed=seed + 5)) * 3, 0, 1)
    t = 0.45 + 0.3 * ridges + 0.1 * fbm(n, 30, 3, seed=seed + 9) - 0.35 * cracks
    rgb = colorize(t, pal)
    moss = norm01(fbm(n, 50, 4, seed=seed + 30)) ** 4 * 1.4
    rgb = rgb * (1 - moss[..., None]) + np.array([0.22, 0.30, 0.10]) * moss[..., None]
    return save(name, rgb, ridges - cracks * 1.5, 3)

def rope(n=512, name='rope', seed=5):
    y = np.arange(n)[:, None]; x = np.arange(n)[None, :]
    strand = 0.5 + 0.5 * np.sin((x / n * 3 + y / n * 1) * 2 * np.pi * 3)
    fib = fbm(n, 2, 3, aniso=0.2, seed=seed)
    t = 0.3 + 0.55 * strand + 0.12 * fib
    rgb = colorize(t, [(0, (54, 40, 22)), (0.5, (140, 112, 70)), (1, (196, 168, 118))])
    return save(name, rgb, strand + 0.2 * fib, 4)

def iron(n=512, name='iron', seed=7):
    t = 0.5 + 0.25 * fbm(n, 30, 4, seed=seed)
    rgb = colorize(t, [(0, (22, 22, 24)), (0.6, (52, 50, 50)), (1, (82, 78, 74))])
    rust = norm01(fbm(n, 25, 5, seed=seed + 3)) ** 3
    rgb = rgb * (1 - rust[..., None]) + np.array([0.42, 0.2, 0.08]) * rust[..., None]
    return save(name, rgb, fbm(n, 6, 3, seed=seed + 8), 1)

def brass(n=512, name='brass', seed=9):
    t = 0.55 + 0.2 * fbm(n, 40, 4, seed=seed)
    rgb = colorize(t, [(0, (120, 82, 26)), (0.6, (206, 158, 66)), (1, (250, 214, 130))])
    pat = norm01(fbm(n, 30, 4, seed=seed + 4)) ** 4
    rgb = rgb * (1 - pat[..., None] * 0.7) + np.array([0.18, 0.36, 0.28]) * pat[..., None] * 0.7
    return save(name, rgb, fbm(n, 4, 2, seed=seed + 1), 0.5)

def leather(n=1024, name='leather', seed=11, base=(60, 46, 26)):
    cells = fbm(n, 4, 3, seed=seed)
    cr = np.clip(1 - np.abs(fbm(n, 10, 3, seed=seed + 2)) * 4, 0, 1)
    t = 0.5 + 0.2 * cells + 0.25 * fbm(n, 70, 3, seed=seed + 5) - 0.3 * cr
    b = np.array(base, float) / 255
    rgb = np.clip(b[None, None, :] * (0.6 + 0.8 * t[..., None]), 0, 1)
    return save(name, rgb, cells - cr, 2)

def moss(n=512, name='moss', seed=13):
    t = norm01(fbm(n, 6, 5, seed=seed))
    rgb = colorize(t, [(0, (16, 26, 8)), (0.5, (52, 74, 24)), (1, (112, 132, 46))])
    return save(name, rgb, t, 3)

def shingles(n=1024, name='shingles', seed=15, rows=10):
    """overlapping cedar shakes for the roofs"""
    y = np.arange(n)[:, None] * np.ones((1, n)); x = np.ones((n, 1)) * np.arange(n)[None, :]
    rh = n / rows; row = (y // rh).astype(int); fy = (y % rh) / rh
    r = np.random.default_rng(seed); widths = []
    rgb = np.zeros((n, n, 3)); h = np.zeros((n, n))
    grain = fbm(n, 3, 4, aniso=0.15, seed=seed)
    for k in range(rows):
        xs = [0]; off = r.uniform(0, 60)
        while xs[-1] < n: xs.append(xs[-1] + r.uniform(50, 110))
        sel = row == k
        xx = (x + off + k * 37) % n
        idx = np.searchsorted(xs, xx) - 1
        tint = r.uniform(-0.2, 0.2, len(xs))
        t = 0.5 + 0.2 * grain + tint[idx] - 0.35 * fy
        edge = np.minimum(xx - np.take(xs, idx), np.take(xs, idx + 1, mode='clip') - xx)
        g = np.clip(edge / 3, 0, 1)
        c = colorize(t, [(0, (30, 22, 16)), (0.5, (86, 62, 40)), (1, (132, 104, 74))]) * (0.35 + 0.65 * g)[..., None] * (1 - 0.5 * (fy > 0.92))[..., None]
        rgb[sel] = c[sel]; h[sel] = (1 - fy)[sel] + 0.2 * grain[sel] - (1 - g[sel])
    mossm = norm01(fbm(n, 40, 4, seed=seed + 7)) ** 3 * 0.9
    rgb = rgb * (1 - mossm[..., None]) + np.array([0.2, 0.28, 0.1]) * mossm[..., None]
    return save(name, rgb, h, 3)

def mudstone(n=1024, name='mudstone', seed=17):
    t = norm01(fbm(n, 30, 6, seed=seed))
    cr = np.clip(1 - np.abs(fbm(n, 14, 3, seed=seed + 1)) * 5, 0, 1)
    rgb = colorize(t, [(0, (34, 28, 20)), (0.5, (74, 60, 42)), (1, (112, 96, 70))]) * (1 - 0.5 * cr)[..., None]
    return save(name, rgb, t - cr, 3)

def velvet(n=512, name='velvet', base=(90, 18, 24), seed=19):
    t = 0.5 + 0.15 * fbm(n, 20, 3, seed=seed) + 0.05 * fbm(n, 1.2, 2, seed=seed + 1)
    rgb = np.clip(np.array(base)[None, None, :] / 255 * (0.6 + 0.8 * t[..., None]), 0, 1)
    return save(name, rgb, t, 0.6)

def glass_tile(n=256, name='glass', tint=(170, 210, 200)):
    im = Image.new('RGBA', (n, n), tint + (70,)); d = ImageDraw.Draw(im)
    for i in range(0, n, 4):
        d.line([(i, 0), (i - n, n)], fill=tint + (90 if (i // 4) % 9 == 0 else 60,))
    p = os.path.join(OUT, name + '.png'); im.save(p); return p

def gold_trim(n=512, name='goldtrim', seed=21):
    t = 0.6 + 0.25 * fbm(n, 20, 4, seed=seed)
    rgb = colorize(t, [(0, (140, 96, 30)), (0.6, (226, 176, 72)), (1, (255, 230, 150))])
    return save(name, rgb, fbm(n, 4, 2, seed=seed + 1), 0.3)

def water_glow(n=512, name='mudglow', seed=23):
    """the glowing mudwater ripple used as emissive inlay"""
    t = norm01(fbm(n, 18, 5, seed=seed))
    rip = 0.5 + 0.5 * np.sin(t * 22)
    rgb = colorize(rip * 0.7 + t * 0.3, [(0, (20, 12, 4)), (0.55, (150, 96, 20)), (1, (255, 206, 90))])
    return save(name, rgb, None)

def all_textures():
    out = {}
    out['planks'] = planks()
    out['planks_dark'] = planks(name='wood_dark', seed=2, rows=8, palette=[(0, (20, 12, 8)), (0.4, (48, 30, 18)), (0.7, (74, 48, 28)), (1, (104, 72, 44))], wear=0.25)
    out['planks_pale'] = planks(name='wood_pale', seed=4, rows=5, palette=[(0, (70, 56, 40)), (0.4, (122, 100, 72)), (0.7, (160, 136, 102)), (1, (196, 176, 140))], wear=0.7)
    out['bar_top'] = planks(name='bar_top', seed=6, rows=3, palette=[(0, (40, 18, 8)), (0.4, (96, 46, 18)), (0.7, (140, 74, 32)), (1, (186, 112, 52))], wear=0.05)
    out['bark'] = bark(); out['rope'] = rope(); out['iron'] = iron(); out['brass'] = brass()
    out['leather'] = leather(); out['leather_green'] = leather(name='leather_green', base=(44, 52, 30), seed=12)
    out['moss'] = moss(); out['shingles'] = shingles(); out['mudstone'] = mudstone(); out['velvet'] = velvet()
    out['velvet_teal'] = velvet(name='velvet_teal', base=(16, 70, 74), seed=20)
    out['glass'] = glass_tile(); out['goldtrim'] = gold_trim(); out['mudglow'] = water_glow()
    return out

if __name__ == '__main__':
    import time; t = time.time(); r = all_textures(); print(len(r), 'textures in', round(time.time() - t, 1), 's')
