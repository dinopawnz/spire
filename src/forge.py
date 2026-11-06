"""MUDWATER SPIRE - the Hall of Fakes forgery press.
Makes N forged copies of a Mudwater card, each with ONE small, findable defect (a few get two),
plus the genuine card, shuffled. Writes card images + an answer key.

    python3 forge.py 62 999 out_dir seed      -> 1000 portraits (999 fakes + 1 real)
    python3 forge.py 100 99 out_dir seed      -> 100 portraits for the finals
"""
import sys, json, random, colorsys
import numpy as np
from PIL import Image, ImageFilter

SRC = '/home/claude/dinopawnz/mudwater/mwc_%03d.jpg'
W, H = 720, 1000

def hsv_arrays(a):
    """a float 0..1 HxWx3 -> h,s,v arrays (vectorised)."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1); mn = a.min(-1); d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = np.where(m, (mx - r) / np.where(m, d, 1), 0)
    gc = np.where(m, (mx - g) / np.where(m, d, 1), 0)
    bc = np.where(m, (mx - b) / np.where(m, d, 1), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = (h / 6.0) % 1.0
    h = np.where(m, h, 0)
    s = np.where(mx > 0, d / np.where(mx > 0, mx, 1), 0)
    return h, s, mx

def from_hsv(h, s, v):
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p = v * (1 - s); q = v * (1 - s * f); t = v * (1 - s * (1 - f))
    r = np.choose(i, [v, q, p, p, t, v]); g = np.choose(i, [t, v, v, q, p, p]); b = np.choose(i, [p, p, t, v, v, q])
    return np.stack([r, g, b], -1)

def box_mask(shape, box):
    m = np.zeros(shape[:2], bool); x0, y0, x1, y1 = box; m[y0:y1, x0:x1] = True; return m

def feather(m, r=1.2):
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im).astype(float) / 255.0

class Card:
    def __init__(self, a): self.a = a.copy()     # float 0..1

    # recolour pixels inside box that pass a colour test: hue shift / sat / value
    def recolor(self, box, test, dh=0.0, ds=1.0, dv=1.0, set_s=None, soft=1.0):
        a = self.a; m = box_mask(a.shape, box) & test(a)
        if not m.any(): return False
        h, s, v = hsv_arrays(a)
        h2 = (h + dh) % 1.0; s2 = np.clip(s * ds if set_s is None else np.full_like(s, set_s) * np.where(s > 0.05, 1, 0), 0, 1); v2 = np.clip(v * dv, 0, 1)
        new = from_hsv(h2, s2, v2)
        k = feather(m, soft)[..., None]
        self.a = a * (1 - k) + new * k
        return True

    def fill_like(self, box, test, color):
        """paint pixels that pass test with a colour (used to erase smoke etc.)"""
        a = self.a; m = box_mask(a.shape, box) & test(a)
        k = feather(m, 0.9)[..., None]
        self.a = a * (1 - k) + np.array(color)[None, None, :] * k

    def copy_cell(self, src, dst, bg):
        """copy a glyph cell (x0,y0,x1,y1) over another cell, clearing the target to bg first"""
        a = self.a; sx0, sy0, sx1, sy1 = src; dx0, dy0, dx1, dy1 = dst
        patch = a[sy0:sy1, sx0:sx1].copy()
        a[dy0:dy1, dx0:dx1] = bg
        w = sx1 - sx0; cx = (dx0 + dx1) // 2; x0 = cx - w // 2
        a[sy0 - (sy0 - dy0):sy1 - (sy0 - dy0), x0:x0 + w] = patch

    def swap_cells(self, c1, c2, bg):
        a = self.a
        p1 = a[c1[1]:c1[3], c1[0]:c1[2]].copy(); p2 = a[c2[1]:c2[3], c2[0]:c2[2]].copy()
        a[c1[1]:c1[3], c1[0]:c1[2]] = bg; a[c2[1]:c2[3], c2[0]:c2[2]] = bg
        def put(p, c):
            w = p.shape[1]; cx = (c[0] + c[2]) // 2; x0 = cx - w // 2
            a[c[1]:c[1] + p.shape[0], x0:x0 + w] = p
        put(p1, c2); put(p2, c1)

def sample(a, x, y): return a[y, x].copy()

# ---------------------------------------------------------------- the card template (same on every Mudwater card)
TPL = {
    # stat circles (glyph boxes): top, left, right, bottom
    'stat': {'t': (68, 29, 84, 53), 'l': (39, 58, 53, 82), 'r': (99, 58, 114, 82), 'b': (68, 89, 84, 112)},
    'diam': [(297, 25, 319, 45), (323, 25, 344, 45), (350, 25, 370, 45), (376, 25, 396, 45), (401, 25, 421, 45)],
    'copy_digits': [(560, 949, 567, 969), (567, 949, 576, 969), (576, 949, 583, 969), (583, 949, 592, 969)],
    'skull': (668, 933, 716, 978),
    'bayc': (52, 950, 90, 968),
    'plate': (186, 912, 520, 975),
}

def template_defects(c, card):
    """defects that work on any card: (key, description, function)"""
    D = []
    a0 = c.a
    black = np.array([0.0, 0.0, 0.0])
    stat = TPL['stat']
    # stat digit swaps between circles (native font)
    for p, q in [('t', 'l'), ('t', 'r'), ('l', 'r'), ('l', 'b'), ('r', 'b'), ('t', 'b')]:
        vals = {'t': card['t'], 'l': card['l'], 'r': card['r'], 'b': card['b']}
        if vals[p] == vals[q]: continue
        D.append(('stat_%s%s' % (p, q), 'edge numbers %s and %s swapped' % (p, q), lambda c, p=p, q=q: c.swap_cells(stat[p], stat[q], black)))
    # a stat digit copied over another (changes one number)
    for p in 'tlrb':
        for q in 'tlrb':
            if p == q or card[p] == card[q]: continue
            D.append(('stat_%s=%s' % (p, q), 'edge number %s shows %s' % (p, card[q]), lambda c, p=p, q=q: c.copy_cell(stat[q], stat[p], black)))
    # a diamond missing (4 instead of 5) or one dimmed
    for i in range(5):
        D.append(('diam_gone%d' % i, 'diamond %d missing' % (i + 1), lambda c, i=i: c.a.__setitem__((slice(TPL['diam'][i][1], TPL['diam'][i][3]), slice(TPL['diam'][i][0], TPL['diam'][i][2])), black)))
        D.append(('diam_teal%d' % i, 'diamond %d is teal' % (i + 1), lambda c, i=i: c.recolor(TPL['diam'][i], lambda a: a.max(-1) > 0.3, dh=0.42, ds=1.1)))
    # copyright year digits: 2026 -> 2020 / 2022 / 2062 / 2006 / 2066
    cd = TPL['copy_digits']
    D.append(('year_2020', 'copyright says 2020', lambda c: c.copy_cell(cd[1], cd[3], black)))
    D.append(('year_2022', 'copyright says 2022', lambda c: c.copy_cell(cd[0], cd[3], black)))
    D.append(('year_2062', 'copyright says 2062', lambda c: c.swap_cells(cd[2], cd[3], black)))
    D.append(('year_2006', 'copyright says 2006', lambda c: (c.copy_cell(cd[1], cd[2], black), c.copy_cell(cd[3], cd[3], black))))
    D.append(('year_6026', 'copyright says 6026', lambda c: c.copy_cell(cd[3], cd[0], black)))
    D.append(('year_2626', 'copyright says 2626', lambda c: c.copy_cell(cd[3], cd[1], black)))
    # the little skull bottom right: gone / mirrored / gold
    sk = TPL['skull']
    D.append(('skull_gone', 'no skull bottom right', lambda c: c.a.__setitem__((slice(sk[1], sk[3]), slice(sk[0], sk[2])), black)))
    D.append(('skull_flip', 'skull mirrored', lambda c: c.a.__setitem__((slice(sk[1], sk[3]), slice(sk[0], sk[2])), c.a[sk[1]:sk[3], sk[0]:sk[2]][:, ::-1].copy())))
    D.append(('skull_gold', 'skull is gold', lambda c: c.recolor(sk, lambda a: a.min(-1) > 0.5, set_s=0.75, dh=0.0, dv=0.95) or c.recolor(sk, lambda a: a.min(-1) > 0.5, dh=0.12)))
    # BAYC mirrored / gone
    bb = TPL['bayc']
    D.append(('bayc_gone', 'no BAYC bottom left', lambda c: c.a.__setitem__((slice(bb[1], bb[3]), slice(bb[0], bb[2])), black)))
    D.append(('bayc_flip', 'BAYC is upside down', lambda c: c.a.__setitem__((slice(bb[1], bb[3]), slice(bb[0], bb[2])), c.a[bb[1]:bb[3], bb[0]:bb[2]][::-1].copy())))
    # name plate colour
    pl = TPL['plate']
    plate_test = lambda a: (a[..., 0] > 0.55) & (a[..., 1] > 0.5) & (a[..., 2] < 0.55) & (np.abs(a[..., 0] - a[..., 1]) < 0.15)
    D.append(('plate_green', 'name plate greener', lambda c: c.recolor(pl, plate_test, dh=0.12, ds=1.1)))
    D.append(('plate_pink', 'name plate rose', lambda c: c.recolor(pl, plate_test, dh=-0.16, ds=1.0)))
    D.append(('plate_grey', 'name plate silver', lambda c: c.recolor(pl, plate_test, ds=0.15, dv=1.05)))
    return D

def founder_defects(card):
    """art-specific defects for #62 The Founder"""
    D = []
    yellow = lambda a: (a[..., 0] > 0.6) & (a[..., 1] > 0.45) & (a[..., 2] < 0.45) & (a[..., 0] - a[..., 2] > 0.3)
    gold = lambda a: (a[..., 0] > 0.45) & (a[..., 1] > 0.35) & (a[..., 2] < 0.45) & (a[..., 0] - a[..., 2] > 0.2)
    ear_box = (163, 452, 202, 496)
    for nm, dh, ds, dv in [('silver', 0, 0.08, 1.05), ('red', -0.13, 1.0, 0.95), ('blue', 0.5, 0.9, 0.95), ('green', 0.2, 1.0, 0.9), ('purple', 0.68, 0.9, 0.9)]:
        D.append(('earring_' + nm, 'earring is ' + nm, lambda c, dh=dh, ds=ds, dv=dv: c.recolor(ear_box, yellow, dh=dh, ds=ds, dv=dv)))
    badge = (445, 105, 540, 205)
    for nm, dh, ds in [('silver', 0, 0.06), ('red', -0.12, 1.1), ('teal', 0.42, 1.0)]:
        D.append(('hatbadge_' + nm, 'hat badge anchor is ' + nm, lambda c, dh=dh, ds=ds: c.recolor(badge, gold, dh=dh, ds=ds)))
    band = (230, 225, 610, 335)
    for nm, dh, ds in [('silver', 0, 0.05), ('red', -0.12, 1.1), ('blue', 0.5, 0.9)]:
        D.append(('hatband_' + nm, 'hat stripe is ' + nm, lambda c, dh=dh, ds=ds: c.recolor(band, gold, dh=dh, ds=ds)))
    anchor = (596, 24, 690, 118)
    D.append(('emblem_silver', 'corner anchor emblem silver', lambda c: c.recolor(anchor, gold, ds=0.06)))
    D.append(('emblem_flip', 'corner anchor emblem upside down', lambda c: c.a.__setitem__((slice(28, 114), slice(600, 686)), c.a[28:114, 600:686][::-1].copy())))
    shirt = (40, 740, 600, 935)
    red = lambda a: (a[..., 0] > 0.55) & (a[..., 1] < 0.4) & (a[..., 2] < 0.4)
    for nm, dh in [('orange', 0.07), ('magenta', -0.09), ('purple', -0.2)]:
        D.append(('shirt_' + nm, 'shirt is ' + nm, lambda c, dh=dh: c.recolor(shirt, red, dh=dh)))
    cyan = lambda a: (a[..., 2] > 0.5) & (a[..., 0] < 0.35) & (a[..., 2] - a[..., 0] > 0.3)
    for nm, dh in [('green', -0.17), ('purple', 0.2)]:
        D.append(('leaves_' + nm, 'blue shirt leaves are ' + nm, lambda c, dh=dh: c.recolor(shirt, cyan, dh=dh)))
    orange_leaf = lambda a: (a[..., 0] > 0.6) & (a[..., 1] > 0.35) & (a[..., 1] < 0.7) & (a[..., 2] < 0.35) & (a[..., 1] - a[..., 2] > 0.15)
    D.append(('oleaves_green', 'orange shirt leaves are green', lambda c: c.recolor(shirt, orange_leaf, dh=0.2)))
    ember = (596, 655, 642, 708)
    D.append(('ember_blue', 'cigar ember burns blue', lambda c: c.recolor(ember, lambda a: (a[..., 0] > 0.55) & (a[..., 2] < 0.45), dh=0.52)))
    D.append(('ember_green', 'cigar ember burns green', lambda c: c.recolor(ember, lambda a: (a[..., 0] > 0.55) & (a[..., 2] < 0.45), dh=0.25)))
    TEAL = np.array([0.098, 0.384, 0.478])
    def bg_at(c): return c.a[600, 680].copy()
    smoke_test = lambda a: (a.max(-1) < 0.55) & ~((a[..., 2] - a[..., 0]) > 0.2)
    D.append(('no_smoke', 'no smoke from the cigar', lambda c: c.fill_like((592, 470, 648, 652), smoke_test, bg_at(c))))
    D.append(('no_drips', 'no ash drips under the cigar', lambda c: c.fill_like((605, 708, 640, 760), lambda a: a.max(-1) < 0.35, bg_at(c))))
    band_cig = (480, 640, 600, 705)
    D.append(('cigarband_red', 'cigar band is red', lambda c: c.recolor(band_cig, lambda a: (a.max(-1) > 0.45) & (a.max(-1) - a.min(-1) < 0.2), dh=0.0, set_s=0.6)))
    D.append(('parrot_gone', 'no parrot pin on the shirt', lambda c: c.a.__setitem__((slice(884, 915), slice(254, 292)), c.a[884:915, 214:252].copy())))
    D.append(('parrot_flip', 'parrot pin faces the other way', lambda c: c.a.__setitem__((slice(884, 915), slice(254, 292)), c.a[884:915, 254:292][:, ::-1].copy())))
    eyes = (330, 345, 535, 395)
    D.append(('eyes_yellow', 'eyes are yellow', lambda c: c.recolor(eyes, lambda a: a.min(-1) > 0.75, set_s=0.55, dh=0.0) or True))
    D.append(('eyes_red', 'eyes are bloodshot red', lambda c: c.recolor(eyes, lambda a: a.min(-1) > 0.75, set_s=0.5)))
    fur = lambda a: (a[..., 0] > 0.3) & (a[..., 0] < 0.72) & (a[..., 1] > 0.15) & (a[..., 1] < 0.45) & (a[..., 2] < 0.3) & (a[..., 0] - a[..., 2] > 0.2)
    D.append(('fur_red', 'fur is redder', lambda c: c.recolor((100, 280, 640, 930), fur, dh=-0.035, ds=1.25)))
    D.append(('fur_grey', 'fur is grey', lambda c: c.recolor((100, 280, 640, 930), fur, ds=0.25)))
    peak = (200, 250, 620, 350)
    D.append(('peak_navy', 'hat brim is navy blue', lambda c: c.recolor(peak, lambda a: (a.max(-1) > 0.1) & (a.max(-1) < 0.35) & (a.max(-1) - a.min(-1) < 0.07), dh=0.62, set_s=0.6, dv=1.5)))
    hat_white = (190, 100, 610, 270)
    D.append(('hat_cream', 'hat is cream, not white', lambda c: c.recolor(hat_white, lambda a: a.min(-1) > 0.7, set_s=0.22, dh=0.0) or True))
    bg = lambda a: (a[..., 2] > 0.3) & (a[..., 1] > 0.25) & (a[..., 0] < 0.2) & (a[..., 2] - a[..., 0] > 0.2)
    D.append(('bg_green', 'background is greener', lambda c: c.recolor((55, 55, 668, 905), bg, dh=-0.07)))
    D.append(('bg_navy', 'background is navy', lambda c: c.recolor((55, 55, 668, 905), bg, dh=0.06, dv=0.85)))
    D.append(('club_pill_gold', 'CLUB tag is gold', lambda c: c.recolor((505, 35, 600, 70), lambda a: a.min(-1) > 0.75, set_s=0.6, dh=0.0)))
    # name glyph swaps (native font): #26, #66, #22, Fuonder, Foundre
    N = {'6': (281, 928, 294, 954), '2': (294, 928, 304, 954), 'o': (372, 928, 383, 954), 'u': (384, 928, 394, 954), 'e2': (419, 928, 430, 954), 'r': (431, 928, 439, 954), 'n': (396, 928, 406, 954), 'd': (407, 928, 418, 954)}
    def plate_bg(c): return c.a[940, 460].copy()
    D.append(('name_26', 'card number #26', lambda c: c.swap_cells(N['6'], N['2'], plate_bg(c))))
    D.append(('name_66', 'card number #66', lambda c: c.copy_cell(N['6'], N['2'], plate_bg(c))))
    D.append(('name_22', 'card number #22', lambda c: c.copy_cell(N['2'], N['6'], plate_bg(c))))
    D.append(('name_fuonder', 'name says The Fuonder', lambda c: c.swap_cells(N['o'], N['u'], plate_bg(c))))
    D.append(('name_foudner', 'name says The Foudner', lambda c: c.swap_cells(N['n'], N['d'], plate_bg(c))))
    # CLUB -> CULB
    CL = {'L': (544, 43, 553, 61), 'U': (553, 43, 563, 61), 'B': (564, 43, 575, 61), 'C': (534, 43, 544, 61)}
    D.append(('club_culb', 'tag says CULB', lambda c: c.swap_cells(CL['L'], CL['U'], np.array([1.0, 1.0, 1.0]))))
    D.append(('club_cbul', 'tag says CBUL', lambda c: c.swap_cells(CL['L'], CL['B'], np.array([1.0, 1.0, 1.0]))))
    return D

CARD_STATS = {62: dict(t=8, l=7, r=3, b=8), 100: dict(t=9, l=8, r=2, b=8)}

def build(card_no, n_fake, out, seed, size=(384, 533), art_defects=None):
    import os
    os.makedirs(out, exist_ok=True)
    src = np.asarray(Image.open(SRC % card_no).convert('RGB')).astype(float) / 255.0
    rng = random.Random(seed)
    base = Card(src)
    D = template_defects(base, CARD_STATS[card_no]) + (art_defects(CARD_STATS[card_no]) if art_defects else [])
    # every defect gets used about equally; ~15% of fakes carry a second, different defect
    picks = []
    pool = []
    while len(picks) < n_fake:
        if not pool: pool = list(range(len(D))); rng.shuffle(pool)
        first = pool.pop()
        combo = [first]
        if rng.random() < 0.15:
            second = rng.randrange(len(D))
            if D[second][0].split('_')[0] != D[first][0].split('_')[0]: combo.append(second)
        key = tuple(sorted(combo))
        picks.append(key)
    slots = list(range(n_fake + 1)); rng.shuffle(slots)
    real_slot = slots[-1]
    answer = {'card': card_no, 'real': real_slot, 'count': n_fake + 1, 'defects': {}}
    for i, combo in enumerate(picks + [None]):
        slot = slots[i]
        c = Card(src)
        if combo:
            for j in combo: D[j][2](c)
            answer['defects'][slot] = [D[j][1] for j in combo]
        img = Image.fromarray((np.clip(c.a, 0, 1) * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
        img.save(os.path.join(out, 'p%04d.jpg' % slot), quality=86)
    json.dump(answer, open(os.path.join(out, 'answer.json'), 'w'), indent=0)
    return D, answer

if __name__ == '__main__':
    card = int(sys.argv[1]); n = int(sys.argv[2]); out = sys.argv[3]; seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    D, ans = build(card, n, out, seed, art_defects=founder_defects if card == 62 else None)
    print(len(D), 'defect kinds; real portrait =', ans['real'])
