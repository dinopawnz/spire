"""Mudwater Spire building kit: shared materials + timber parts (decks, walls with windows, rails, pilings, roofs, stairs)."""
import math, random
import numpy as np
from glb import *

TEX = '/home/claude/spire/tex/'
MR = '/home/claude/dinopawnz/mudwater/'
MATS = {
    'plank':   dict(tex=TEX + 'wood_planks.jpg', nrm=TEX + 'wood_planks_n.jpg', rough=0.82),
    'dark':    dict(tex=TEX + 'wood_dark.jpg', nrm=TEX + 'wood_dark_n.jpg', rough=0.75),
    'pale':    dict(tex=TEX + 'wood_pale.jpg', nrm=TEX + 'wood_pale_n.jpg', rough=0.9),
    'bartop':  dict(tex=TEX + 'bar_top.jpg', nrm=TEX + 'bar_top_n.jpg', rough=0.32),
    'bark':    dict(tex=TEX + 'bark.jpg', nrm=TEX + 'bark_n.jpg', rough=0.95),
    'rope':    dict(tex=TEX + 'rope.jpg', nrm=TEX + 'rope_n.jpg', rough=0.95),
    'iron':    dict(tex=TEX + 'iron.jpg', nrm=TEX + 'iron_n.jpg', metal=0.75, rough=0.5),
    'brass':   dict(tex=TEX + 'brass.jpg', metal=0.9, rough=0.35),
    'gold':    dict(tex=TEX + 'goldtrim.jpg', metal=1.0, rough=0.28, emis=(0.08, 0.055, 0.015)),
    'leather': dict(tex=TEX + 'leather.jpg', nrm=TEX + 'leather_n.jpg', rough=0.6),
    'leatherg': dict(tex=TEX + 'leather_green.jpg', nrm=TEX + 'leather_green_n.jpg', rough=0.6),
    'moss':    dict(tex=TEX + 'moss.jpg', nrm=TEX + 'moss_n.jpg', rough=1.0),
    'shingle': dict(tex=TEX + 'shingles.jpg', nrm=TEX + 'shingles_n.jpg', rough=0.9),
    'mud':     dict(tex=TEX + 'mudstone.jpg', nrm=TEX + 'mudstone_n.jpg', rough=0.95),
    'velvet':  dict(tex=TEX + 'velvet.jpg', rough=0.95),
    'velvett': dict(tex=TEX + 'velvet_teal.jpg', rough=0.95),
    'glass':   dict(color=(0.55, 0.75, 0.7, 0.22), metal=0.0, rough=0.05, alpha='BLEND', double=True),
    'window':  dict(color=(1.0, 0.72, 0.36, 1), emis=(1.0, 0.62, 0.22), rough=0.3),          # warm lit panes seen from outside
    'glow':    dict(color=(1.0, 0.8, 0.45, 1), emis=(1.0, 0.72, 0.3), emis_strength=2.0, rough=0.5),
    'mudglow': dict(tex=TEX + 'mudglow.jpg', emis_tex=TEX + 'mudglow.jpg', emis=(1.0, 0.8, 0.5), rough=0.4),
    'black':   dict(color=(0.03, 0.03, 0.03, 1), rough=0.6),
    'col':     dict(color=(1, 1, 1, 0.0), alpha='BLEND', rough=1.0),        # invisible collider
}

def octa(apothem, rot=22.5):
    """8 corners of an octagon with flat faces toward +-x/+-z"""
    R = apothem / math.cos(math.radians(22.5))
    return [(R * math.sin(math.radians(rot + 45 * i)), R * math.cos(math.radians(rot + 45 * i))) for i in range(8)]

def tint(rng, amt=0.12, base=1.0):
    v = base + rng.uniform(-amt, amt); return (v, v * rng.uniform(0.97, 1.0), v * rng.uniform(0.92, 1.0), 1.0)

def place(p0, p1, y=0.0):
    """matrix that maps local x along the segment p0->p1 (2D xz), origin at p0, at height y"""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    ang = math.degrees(math.atan2(-dz, dx))
    return M(T(p0[0], y, p0[1]), Ry(ang)), math.hypot(dx, dz)

def poly_x_range(poly, z):
    """x extent of a convex polygon (xz) at a given z"""
    xs = []
    n = len(poly)
    for i in range(n):
        (x0, z0), (x1, z1) = poly[i], poly[(i + 1) % n]
        if (z0 - z) * (z1 - z) <= 0 and z0 != z1:
            t = (z - z0) / (z1 - z0); xs.append(x0 + t * (x1 - x0))
    return (min(xs), max(xs)) if len(xs) >= 2 else None

def subtract(segs, cuts):
    """remove the intervals in cuts from the intervals in segs"""
    for c0, c1 in cuts:
        ns = []
        for a, b in segs:
            if c1 <= a or c0 >= b: ns.append((a, b)); continue
            if c0 > a: ns.append((a, c0))
            if c1 < b: ns.append((c1, b))
        segs = ns
    return segs

def hole_range(h, z0, z1):
    """x interval a hole covers anywhere in the band z0..z1. h = ('c', cx, cz, r) or ('p', convex_poly)"""
    if h[0] == 'c':
        _, cx, cz, r = h
        zz = min(max(cz, z0), z1)
        if abs(zz - cz) >= r: return None
        hx = math.sqrt(r * r - (zz - cz) ** 2); return (cx - hx, cx + hx)
    poly = h[1]; xs = []
    for z in np.linspace(z0, z1, 5):
        rg = poly_x_range(poly, z)
        if rg: xs += list(rg)
    zs = [p[1] for p in poly]
    for (x, zp) in poly:
        if z0 <= zp <= z1: xs.append(x)
    return (min(xs), max(xs)) if xs else None

def hole_poly(cx, cz, local, s=1.0):
    return ('p', [(cx + x * s, cz + z * s) for (x, z) in local])

def _circ_poly(h, n=40):
    _, cx, cz, r = h; return [(cx + r * math.sin(2 * math.pi * k / n), cz + r * math.cos(2 * math.pi * k / n)) for k in range(n)]

def _ranges_at(poly, holes, z):
    rg = poly_x_range(poly, z)
    if not rg: return []
    cuts = [r for r in (poly_x_range(hp, z) for hp in holes) if r]
    return subtract([rg], sorted(cuts))

def flat_deck(m, mat, poly, y, holes=(), uvs=3.0, under='dark', th=0.12, col=None):
    """one smooth plank-textured surface (the texture draws the boards): exact trapezoid strips, holes cut out exactly"""
    hp = [_circ_poly(h) if h[0] == 'c' else h[1] for h in holes]
    zs = sorted(set([p[1] for p in poly] + [q[1] for h in hp for q in h]))
    zmin, zmax = min(p[1] for p in poly), max(p[1] for p in poly)
    zs = [z for z in zs if zmin <= z <= zmax]
    for za, zb in zip(zs[:-1], zs[1:]):
        if zb - za < 1e-4: continue
        e = min(1e-4, (zb - za) / 4)
        A = _ranges_at(poly, hp, za + e); Bq = _ranges_at(poly, hp, zb - e)
        if len(A) != len(Bq): A = Bq = _ranges_at(poly, hp, (za + zb) / 2)
        for (a0, a1), (b0, b1) in zip(A, Bq):
            P = np.array([[a0, y, za], [a1, y, za], [b1, y, zb], [b0, y, zb]])
            U = np.c_[P[:, 0] / uvs, P[:, 2] / uvs]
            m.add(mat, P, [[0, 1, 0]] * 4, U, [0, 2, 1, 0, 3, 2], col)
            if under: m.add(under, P - np.array([0, th, 0]), [[0, -1, 0]] * 4, U, [0, 1, 2, 0, 2, 3])

def deck(m, poly, y, rng, mat='plank', plank_w=0.28, th=0.09, joists=True, hole=None, along='x', edge_mat='dark', holes=(), flat=False):
    """plank deck clipped to a convex polygon; optional circular hole (cx, cz, r) and extra holes [('c',cx,cz,r) | ('p',poly)].
    flat=True: one textured surface instead of individual planks (a fraction of the triangles)"""
    holes = list(holes) + ([('c',) + tuple(hole)] if hole else [])
    zs = [p[1] for p in poly]; z = min(zs) + plank_w / 2
    if flat:
        flat_deck(m, mat, poly, y, holes); z = max(zs) + 1
    while z < max(zs):
        rg = poly_x_range(poly, z)
        if rg:
            x0, x1 = rg
            cuts = [r for r in (hole_range(h, z - plank_w / 2, z + plank_w / 2) for h in holes) if r]
            segs = subtract([(x0, x1)], cuts)
            for a, b in segs:
                # break long runs into boards of 3-6 m
                xa = a
                while xa < b - 0.05:
                    L = min(b - xa, rng.uniform(3.0, 6.0))
                    bevel_box(m, mat, L - 0.01, th, plank_w - 0.012, 0.012, m=T(xa + L / 2, y - th / 2, z), col=tint(rng), uvs=3.0, uvoff=(rng.random(), rng.random()))
                    xa += L
        z += plank_w
    if joists:
        x = min(p[0] for p in poly) + 0.6
        sw = lambda h: ('c', h[2], h[1], h[3]) if h[0] == 'c' else ('p', [(q[1], q[0]) for q in h[1]])
        while x < max(p[0] for p in poly):
            # z extent at this x: swap axes
            pr = poly_x_range([(p[1], p[0]) for p in poly], x)
            if pr:
                cuts = [r for r in (hole_range(sw(h), x - 0.1, x + 0.1) for h in holes) if r]
                for a, b in subtract([(pr[0] + 0.1, pr[1] - 0.1)], cuts):
                    if b - a > 0.2: box(m, 'dark', 0.18, 0.3, b - a, m=T(x, y - th - 0.15, (a + b) / 2), uvs=2.0)
            x += 1.2
    # rim board round the edge
    n = len(poly)
    for i in range(n):
        mm, L = place(poly[i], poly[(i + 1) % n], y - 0.2)
        bevel_box(m, edge_mat, L, 0.42, 0.12, 0.02, m=M(mm, T(L / 2, 0, 0)), uvs=3.0)

def railing(m, pts, y, rng, h=1.1, post_every=2.0, closed=True, mat='dark', top='pale', balusters=True, rope_mat=None):
    n = len(pts); segs = n if closed else n - 1
    for i in range(segs):
        p0, p1 = pts[i], pts[(i + 1) % n]
        mm, L = place(p0, p1, y)
        k = max(1, int(round(L / post_every)))
        for j in range(k + 1):
            x = L * j / k
            bevel_box(m, mat, 0.14, h + 0.1, 0.14, 0.02, m=M(mm, T(x, (h + 0.1) / 2, 0)), col=tint(rng, 0.08), uvs=1.5)
            lathe(m, mat, [(0.1, 0), (0.1, 0.06), (0.06, 0.1), (0.07, 0.16), (0.0, 0.2)], 6, m=M(mm, T(x, h + 0.1, 0)))
        bevel_box(m, top, L, 0.09, 0.2, 0.02, m=M(mm, T(L / 2, h, 0)), uvs=3.0)
        bevel_box(m, mat, L, 0.07, 0.08, 0.015, m=M(mm, T(L / 2, 0.12, 0)), uvs=3.0)
        if balusters:
            nb = int(L / 0.24)
            for j in range(1, nb):
                x = L * j / nb
                if any(abs(x - L * q / k) < 0.12 for q in range(k + 1)): continue
                box(m, mat, 0.05, h - 0.14, 0.05, m=M(mm, T(x, (h - 0.14) / 2 + 0.12, 0)), col=tint(rng, 0.1), uvs=1.0, faces='xXzZ')
        if rope_mat:
            sag = [(mm @ np.array([L * t, 0.6 - 0.12 * math.sin(math.pi * t), 0.09, 1]))[:3] for t in np.linspace(0, 1, 8)]
            tube(m, rope_mat, sag, 0.025, 5, twist=3)

def window(m, w, h, mm, rng, frame='pale', shutters=True, lit=True, mull=(2, 3)):
    """window set into a wall, centred at local origin, facing +z and -z (both sides)"""
    t = 0.12
    for sx in (-1, 1): box(m, frame, t, h + 2 * t, 0.36, m=M(mm, T(sx * (w / 2 + t / 2), 0, 0)), uvs=1.5)
    box(m, frame, w + 2 * t, t, 0.36, m=M(mm, T(0, h / 2 + t / 2, 0)), uvs=1.5)
    bevel_box(m, frame, w + 0.5, 0.1, 0.5, 0.02, m=M(mm, T(0, -h / 2 - 0.05, 0.05)), uvs=1.5)       # sill
    quad(m, 'window' if lit else 'glass', w, h, M(mm, T(0, 0, 0.02)), double=True)
    cx, cy = mull
    for i in range(1, cx): box(m, 'dark', 0.04, h, 0.06, m=M(mm, T(-w / 2 + w * i / cx, 0, 0.03)))
    for i in range(1, cy): box(m, 'dark', w, 0.04, 0.06, m=M(mm, T(0, -h / 2 + h * i / cy, 0.03)))
    if shutters:
        for sx in (-1, 1):
            ang = sx * rng.uniform(100, 165)
            hinge = M(mm, T(sx * (w / 2 + t), 0, 0.2), Ry(ang))
            sw = w / 2 + 0.05
            box(m, 'plank', sw, h, 0.05, m=M(hinge, T(sx * sw / 2, 0, 0)), col=(0.75, 0.82, 0.78, 1), uvs=1.5)
            for k in range(1, 4): box(m, 'dark', sw * 0.96, 0.04, 0.07, m=M(hinge, T(sx * sw / 2, -h / 2 + k * h / 4, 0)), faces='yYzZ')
            box(m, 'iron', sw * 0.8, 0.05, 0.07, m=M(hinge, T(sx * sw * 0.45, h * 0.3, 0.02)))
            box(m, 'iron', sw * 0.8, 0.05, 0.07, m=M(hinge, T(sx * sw * 0.45, -h * 0.3, 0.02)))

def wall(m, p0, p1, y0, h, rng, windows=None, door=None, th=0.3, mat='plank', frame='dark', inside_mat=None, vertical=True):
    """timber-frame wall from p0 to p1 (xz) at base y0. windows=[(x, y, w, h)] in local coords, door=(x, w, h).
    The outer face is +z local (left of the p0->p1 direction is outside when going clockwise)."""
    mm, L = place(p0, p1, y0)
    holes = list(windows or [])
    if door: holes.append((door[0], door[2] / 2, door[1], door[2]))
    # vertical boards, skipping holes
    bw = 0.3
    nb = int(L / bw)
    for j in range(nb):
        x0 = j * L / nb; x1 = (j + 1) * L / nb; xc = (x0 + x1) / 2
        spans = [(0, h)]
        for (hx, hy, hw, hh) in holes:
            if x1 > hx - hw / 2 - 0.12 and x0 < hx + hw / 2 + 0.12:
                ns = []
                for a, b in spans:
                    lo, hi = hy - hh / 2 - 0.12, hy + hh / 2 + 0.12
                    if b <= lo or a >= hi: ns.append((a, b))
                    else:
                        if a < lo: ns.append((a, lo))
                        if b > hi: ns.append((hi, b))
                spans = ns
        for a, b in spans:
            if b - a < 0.05: continue
            if vertical:
                box(m, mat, (x1 - x0), b - a, th, m=M(mm, T(xc, (a + b) / 2, 0)), col=tint(rng, 0.14), uvs=3.0, uvoff=(rng.random(), rng.random()), faces='zZ')
    # frame: corner posts, sill and plate beams, mid brace
    for x in (0, L): bevel_box(m, frame, 0.36, h, 0.44, 0.03, m=M(mm, T(x, h / 2, 0)), uvs=2.0)
    bevel_box(m, frame, L, 0.3, 0.42, 0.03, m=M(mm, T(L / 2, h - 0.15, 0)), uvs=3.0)
    bevel_box(m, frame, L, 0.3, 0.42, 0.03, m=M(mm, T(L / 2, 0.15, 0)), uvs=3.0)
    for (hx, hy, hw, hh) in (windows or []):
        window(m, hw, hh, M(mm, T(hx, hy, 0)), rng)
    if door:
        dx, dw, dh = door
        for sx in (-1, 1): bevel_box(m, frame, 0.24, dh + 0.2, 0.5, 0.03, m=M(mm, T(dx + sx * (dw / 2 + 0.12), (dh + 0.2) / 2, 0)), uvs=1.5)
        bevel_box(m, frame, dw + 0.8, 0.3, 0.5, 0.03, m=M(mm, T(dx, dh + 0.15, 0)), uvs=1.5)
    return mm, L

def piling(m, x, z, y0, y1, rng, r=0.32, rope=True):
    lean_x = rng.uniform(-2.5, 2.5); lean_z = rng.uniform(-2.5, 2.5)
    mm = M(T(x, y0, z), Rx(lean_z), Rz(lean_x))
    h = y1 - y0
    prof = [(r * (1.08 - 0.08 * t) * (1 + 0.04 * math.sin(t * 17 + x)), h * t) for t in np.linspace(0, 1, 9)]
    lathe(m, 'bark', prof[::2] + ([prof[-1]] if len(prof) % 2 == 0 else []), 8, m=mm, uvs_u=1.0, uv_v=3.0, cap_top=True)
    if rope:
        yy = rng.uniform(0.8, 1.6)
        pts = [(r * 1.05 * math.cos(a), yy + a * 0.02, r * 1.05 * math.sin(a)) for a in np.linspace(0, 6 * math.pi, 28)]
        tube(m, 'rope', pts, 0.03, 4, m=mm, twist=3)
    # moss at the water line
    lathe(m, 'moss', [(r * 1.12, 0.0), (r * 1.14, 0.35), (r * 1.03, 0.7)], 8, m=mm)

def skirt_roof(m, apo_in, apo_out, y_in, y_out, rng, overhang=0.6):
    """sloping shingle roof ring between two octagons (a pent roof round a storey)"""
    ci = octa(apo_in); co = octa(apo_out + overhang)
    for i in range(8):
        a0, a1 = ci[i], ci[(i + 1) % 8]; b0, b1 = co[i], co[(i + 1) % 8]
        P = np.array([[a0[0], y_in, a0[1]], [a1[0], y_in, a1[1]], [b1[0], y_out, b1[1]], [b0[0], y_out, b0[1]]])
        # rows of shingle courses: just tile the shingle texture; UV in metres
        wdir = (P[1] - P[0]); wl = np.linalg.norm(wdir)
        ddir = P[3] - P[0]; dl = np.linalg.norm(ddir)
        U = np.array([[0, 0], [wl / 4, 0], [np.dot(P[2] - P[0], wdir / wl) / 4, dl / 4], [np.dot(P[3] - P[0], wdir / wl) / 4, dl / 4]])
        nrm = np.cross(P[1] - P[0], P[3] - P[0]); nrm /= np.linalg.norm(nrm)
        if nrm[1] < 0: nrm = -nrm; idx = [0, 2, 1, 0, 3, 2]
        else: idx = [0, 1, 2, 0, 2, 3]
        th = 0.18
        m.add('shingle', P + nrm * th, [nrm] * 4, U, idx)
        m.add('dark', P, [-nrm] * 4, U, idx[::-1] if idx[0] == 0 else idx)
        # fascia board + rafter tails along the eave
        mm, L = place(b0, b1, y_out)
        bevel_box(m, 'dark', L, 0.3, 0.12, 0.02, m=M(mm, T(L / 2, 0.0, 0)), uvs=3.0)
        nr = int(L / 1.2)
        for k in range(1, nr):
            x = L * k / nr
            src = np.array([a0[0] + (a1[0] - a0[0]) * k / nr, y_in, a0[1] + (a1[1] - a0[1]) * k / nr])
            dst = (mm @ np.array([x, -0.1, 0, 1]))[:3]
            d = dst - src; ln = np.linalg.norm(d)
            bm = M(T(*((src + dst) / 2)), look_basis(d))
            box(m, 'dark', 0.12, 0.2, ln + 0.3, m=bm, uvs=2.0)
    # moss on the ridge
    for i in range(8):
        a0, a1 = ci[i], ci[(i + 1) % 8]
        tube(m, 'moss', [(a0[0], y_in + 0.15, a0[1]), (a1[0], y_in + 0.15, a1[1])], 0.18, 6)

def stair(m, x0, z0, y0, run_dir, n, rise=0.18, tread=0.32, w=2.4, rng=None, mat='plank', stringer='dark', rails=True):
    """straight stair starting at (x0,y0,z0) climbing along run_dir (degrees, 0 = +z)"""
    mm = M(T(x0, y0, z0), Ry(run_dir))
    for i in range(n):
        bevel_box(m, mat, w, 0.07, tread + 0.04, 0.012, m=M(mm, T(0, rise * (i + 1) - 0.035, tread * i + tread / 2)), col=tint(rng) if rng else None, uvs=3.0)
    L = tread * n; H = rise * n; sl = math.hypot(L, H); a = math.degrees(math.atan2(H, L))
    for sx in (-1, 1):
        bevel_box(m, stringer, 0.12, 0.38, sl, 0.02, m=M(mm, T(sx * (w / 2 + 0.06), H / 2 - 0.08, L / 2), Rx(-a)), uvs=3.0)
        if rails:
            pts = [(mm @ np.array([sx * (w / 2 + 0.06), rise * k + 1.0, tread * k, 1]))[:3] for k in range(0, n + 1, max(1, n // 6))]
            if (n % max(1, n // 6)): pts.append((mm @ np.array([sx * (w / 2 + 0.06), H + 1.0, L, 1]))[:3])
            tube(m, 'pale', pts, 0.045, 8)
            for p in pts: box(m, stringer, 0.08, 1.0, 0.08, m=T(p[0], p[1] - 0.5, p[2]))
    return (mm @ np.array([0, H, L, 1]))[:3]

def collider_box(m, sx, sy, sz, mm): box(m, 'col', sx, sy, sz, m=mm)

def slab_collider(m, y, outer, holes=(), row=0.5, th=0.3, pad=0.25):
    """invisible walk-on floor (top at y) made of strips: outer = ('c', r) or ('p', convex poly); holes stay open"""
    if outer[0] == 'c': R = outer[1] + pad; zmin, zmax = -R, R
    else: zs = [p[1] for p in outer[1]]; zmin, zmax = min(zs), max(zs)
    z = zmin
    while z < zmax - 1e-6:
        z1 = min(z + row, zmax); zm = (z + z1) / 2
        if outer[0] == 'c':
            if abs(zm) >= R: z = z1; continue
            hx = math.sqrt(R * R - zm * zm); rg = (-hx, hx)
        else:
            rg = poly_x_range(outer[1], zm)
            if rg: rg = (rg[0] - pad, rg[1] + pad)
        if rg:
            cuts = [r for r in (hole_range(h, z, z1) for h in holes) if r]
            for a, b in subtract([rg], cuts):
                if b - a > 0.05: box(m, 'col', b - a, th, z1 - z + 0.02, m=T((a + b) / 2, y - th / 2, zm))
        z = z1
