"""THE ROOF = THE GRAND FINALE photo terrace (owner: "the most scenic part of the tower, no floating structures").
Called by build_html.py after outside.apply: roof.apply(D, L, FL).
Everything stands ON the deck (y = FL['roof']):
  - a raised dark-timber photo stage with steps, the Meshy photo arch on it (players face the crowd; behind them the steeple
    and the floating Mudwater pack + rings), the Mudwater logo hung from the arch
  - Meshy cypress planters round the terrace, benches, two Meshy stone fire pits with animated flames
  - tall Meshy lantern posts carrying strings of warm festival lights up to the steeple house eave
  - the Old Skipper by the stage
Colliders are invisible pads (D['pads']) so nothing is walk-through. The CELEBRATE fireworks live in spire_src.html."""
import math, random
import numpy as np
from glb import Mesh, write, tube, sphere, T, M, Ry
from kit import MATS, bevel_box, flat_deck
import outside
from outside import place, r3

OUTG = '/home/claude/spire/out/glb/'

def stage_glb(y, x0, x1, z0, z1, h):
    m = Mesh(); mats = dict(MATS)
    bevel_box(m, 'dark', x1 - x0, h, z1 - z0, 0.05, m=T((x0 + x1) / 2, y + h / 2, (z0 + z1) / 2), uvs=3.0)
    flat_deck(m, 'wetfloor', [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y + h + 0.01, under=None, uvs=3.0)
    for k in range(3):                                         # three broad steps down the front
        sh = h * (3 - k) / 3
        bevel_box(m, 'plank_ext', (x1 - x0) * 0.6, sh, 0.55, 0.02, m=T((x0 + x1) / 2, y + sh / 2, z1 + 0.275 + k * 0.55), uvs=2.0)
    for sx in (x0, x1):                                        # gilt trim along the stage edge
        bevel_box(m, 'gold', 0.1, 0.1, z1 - z0, 0.01, m=T(sx, y + h - 0.05, (z0 + z1) / 2))
    bevel_box(m, 'gold', x1 - x0, 0.1, 0.1, 0.01, m=T((x0 + x1) / 2, y + h - 0.05, z1))
    write(OUTG + 'sp_roof_stage.glb', m, mats)

def lights_glb(strands):
    """festival lights: each strand a thin dark wire sagging between two points with warm bulbs along it"""
    m = Mesh(); mats = dict(dark=MATS['dark'], bulb=dict(color=(1.0, 0.85, 0.5, 1), emis=(1.0, 0.76, 0.36), emis_strength=3.0))
    for (a, b) in strands:
        a, b = np.array(a), np.array(b); ln = np.linalg.norm(b - a); n = max(8, int(ln / 1.6))
        pts = [a + (b - a) * u - np.array([0, 0.06 * ln * math.sin(math.pi * u), 0]) for u in np.linspace(0, 1, n + 1)]
        tube(m, 'dark', pts, 0.015, 3)
        for p in pts[1:-1]: sphere(m, 'bulb', 0.11, 5, 3, m=T(p[0], p[1] - 0.1, p[2]))
    write(OUTG + 'sp_roof_lights.glb', m, mats)

def apply(D, L, FL):
    y = FL['roof']; add = D['sdeco'].append; pads = D.setdefault('pads', []); R = random.Random(51)
    have = lambda n: n in outside.META
    # ---- the deck we use: x +-30, z -28 .. 26 (between the steeple house and the front gables)
    # the stage
    x0, x1, z0, z1, h = -11.0, 11.0, -6.0, 3.0, 0.75
    stage_glb(y, x0, x1, z0, z1, h)
    D.setdefault('roofModels', []).append(['sp_roof_stage', 0, 0, 0])
    pads.append([0.0, y + h / 2, (z0 + z1) / 2, x1 - x0, h, z1 - z0, 0])
    for k in range(3):
        sh = h * (3 - k) / 3; pads.append([0.0, y + sh / 2, z1 + 0.275 + k * 0.55, (x1 - x0) * 0.6, sh, 0.55, 0])
    ys = y + h
    if have('photoarch'):
        add(place('photoarch', 0.0, ys, z0 + 2.2, 0, 8.0, 'h'))
        mn, mx = outside.META['photoarch']; s = 8.0 / (mx[1] - mn[1]); half = (mx[0] - mn[0]) * s / 2
        for sx in (-1, 1): pads.append([sx * (half - 0.45), ys + 4.0, z0 + 2.2, 0.8, 8.0, 0.8, 0])
    # the Mudwater logo (Coliseum GLB, an image-like plaque) high on the stage, under the arch
    D['deco'].append(['mw_logo', 0.0, r3(ys + 5.6), r3(z0 + 2.0), 0.0, 1.9])
    # ---- planters with little cypress trees all round the terrace edge
    if have('planter'):
        spots = [(x, -27.0) for x in (-26, -13, 13, 26)] + [(sx * 29.0, z) for sx in (-1, 1) for z in (-18, -6, 6, 18)] + [(x, 25.0) for x in (-24, -14, 14, 24)]
        for (x, z) in spots:
            add(place('planter', x, y, z, R.uniform(0, 360), 3.4, 'h')); pads.append([x, y + 0.6, z, 1.6, 1.2, 1.6, 0])
    # ---- benches facing the stage, two curved rows each side
    if have('bench'):
        for sx in (-1, 1):
            for (dx, z) in ((15.0, 9.0), (19.0, 4.0), (15.0, 15.0), (21.0, 11.0)):
                x = sx * dx; ry = math.degrees(math.atan2(-x, (z0 + z1) / 2 - z))
                add(place('bench', x, y, z, ry, 2.4, 'w'))
                pads.append([x, y + 0.45, z, 2.3, 0.9, 0.6, ry])
    # ---- fire pits (flames animated in spire_src.html from D['roofFires'])
    fires = []
    if have('firepit'):
        for sx in (-1, 1):
            x, z = sx * 22.0, 19.0
            add(place('firepit', x, y, z, R.uniform(0, 360), 2.6, 'l')); pads.append([x, y + 0.35, z, 2.2, 0.7, 2.2, 0])
            fires.append([x, y + 0.35, z])
    D['roofFires'] = fires
    # ---- tall lantern posts round the terrace, festival lights strung from them up to the steeple house eave
    strands = []
    posts = [(sx * 27.0, z) for sx in (-1, 1) for z in (-22.0, 0.0, 22.0)] + [(x, 27.0) for x in (-8.0, 8.0)]
    PH = 5.2
    for (x, z) in posts:
        if have('lanternpost'): add(place('lanternpost', x, y, z, 0, PH, 'h'))
        pads.append([x, y + PH / 2, z, 0.5, PH, 0.5, 0])
    eave = (y + 9.5 - 0.2, -(L['Z1'] - 11.0) + 0.3)              # the steeple house front eave (build_rect: hh 9.5, zb = -(Z1-11))
    for (x, z) in posts:
        strands.append(((x, y + PH - 0.4, z), (x * 0.45, eave[0], eave[1])))
    for (a, b) in ((posts[0], posts[1]), (posts[1], posts[2]), (posts[3], posts[4]), (posts[4], posts[5]), (posts[2], posts[6]), (posts[6], posts[7]), (posts[7], posts[5])):
        strands.append(((a[0], y + PH - 0.4, a[1]), (b[0], y + PH - 0.4, b[1])))
    lights_glb(strands)
    D['roofModels'].append(['sp_roof_lights', 0, 0, 0])
    # ---- the Old Skipper stands beside the stage, facing the crowd
    if 'where' in D and 'skipper' in D['where']: D['where']['skipper'] = [-13.5, y, 4.5, 20]
    backdrop(D, L, FL, zb=z0 - 3.2)
    artwall(D, L, FL)
    print('roof: stage, arch, %d planters, %d fires, %d light strands, %d pads' % (sum(1 for e in D['sdeco'] if e[0] == 'sp_m_planter'), len(fires), len(strands), len(pads)))

# ---- THE PHOTO BACKDROP (v33, owner: "we need a beautiful backdrop"): right behind the stage, a curtain of warm hanging lights in
# front of a deep green velvet drape, between two carved timber posts under a gilt beam, Spanish moss swagged along the beam and a
# Mudwater banner at each end. It stops below the steeple house roof, so the steeple and the floating Mudwater pack still crown it.
def backdrop(D, L, FL, zb=-9.2, half=12.4, top=8.6):
    y = FL['roof']; m = Mesh(); mats = dict(MATS)
    mats['velvet'] = dict(color=(0.035, 0.085, 0.055, 1), rough=0.82, emis=(0.004, 0.012, 0.008))
    mats['bulb'] = dict(color=(1.0, 0.86, 0.52, 1), emis=(1.0, 0.74, 0.34), emis_strength=3.2)
    mats['wire'] = dict(color=(0.08, 0.06, 0.04, 1), rough=0.7)
    B = '/home/claude/spire/tex/banner_mw.jpg'
    mats['ban'] = dict(tex=B, rough=0.9, emis_tex=B, emis=(0.12, 0.12, 0.1))
    # the velvet drape: soft vertical folds
    nx, ny = 160, 2; W = 2 * half - 0.4
    P, N, U, I = [], [], [], []
    for j in range(ny + 1):
        for i_ in range(nx + 1):
            u = i_ / nx; x = -W / 2 + W * u; t = x / 0.95 * 2 * math.pi
            P.append([x, y + top * j / ny, zb - 0.35 + 0.16 * math.sin(t)]); N.append([-0.6 * math.cos(t), 0, 1]); U.append([u * 8, j])
    for j in range(ny):
        for i_ in range(nx):
            a = j * (nx + 1) + i_; b = a + 1; c = a + nx + 1; d = c + 1
            I += [a, b, d, a, d, c]
    N = (np.array(N) / np.linalg.norm(N, axis=1)[:, None]).tolist()
    m.add('velvet', P, N, U, I)
    # posts, beam, gilt trim, carved brackets
    for sx in (-1, 1):
        bevel_box(m, 'dark', 0.62, top + 0.5, 0.62, 0.05, m=T(sx * half, y + (top + 0.5) / 2, zb), uvs=2.0)
        bevel_box(m, 'gold', 0.78, 0.14, 0.78, 0.02, m=T(sx * half, y + top + 0.57, zb))
        bevel_box(m, 'gold', 0.74, 0.12, 0.74, 0.02, m=T(sx * half, y + 0.06, zb))
        for k in range(3):                                         # stepped brackets under the beam
            bevel_box(m, 'dark', 0.5 + 0.35 * k, 0.22, 0.5, 0.03, m=T(sx * (half - 0.2 - 0.17 * k), y + top - 0.25 - 0.24 * k, zb), uvs=1.0)
    bevel_box(m, 'dark', 2 * half + 4.0, 0.55, 0.6, 0.05, m=T(0, y + top + 0.15, zb), uvs=3.0)
    for yy in (y + top - 0.13, y + top + 0.43):
        bevel_box(m, 'gold', 2 * half + 4.1, 0.06, 0.64, 0.01, m=T(0, yy, zb))
    # the light curtain: a strand every 0.45 m, bulbs every 0.42 m, the bottoms scalloped
    xs = np.arange(-half + 0.55, half - 0.5, 0.45)
    for k, x in enumerate(xs):
        bot = y + 1.0 + 0.55 * abs(math.sin(k * math.pi / 9.0))
        z = zb + 0.05 + 0.04 * math.sin(k * 1.7)
        tube(m, 'wire', [(x, y + top - 0.12, z), (x, bot, z)], 0.008, 3)
        for yy in np.arange(y + top - 0.45, bot - 0.01, -0.42):
            sphere(m, 'bulb', 0.055, 6, 4, m=T(x, yy, z + 0.02))
    # a Mudwater banner at each end, on iron arms off the beam
    w, h, tip = 2.5, 5.2, 0.9
    for sx in (-1, 1):
        cx = sx * (half + 1.75); ztop = y + top - 0.15
        Pb = np.array([[-w / 2, 0, 0], [w / 2, 0, 0], [w / 2, -h, 0], [0, -h - tip, 0], [-w / 2, -h, 0]])
        Ub = [[0, 0], [1, 0], [1, h / (h + tip)], [0.5, 1], [0, h / (h + tip)]]
        for nz in (1, -1):
            Ib = [0, 4, 1, 1, 4, 2, 2, 4, 3] if nz == 1 else [0, 1, 4, 1, 2, 4, 2, 3, 4]
            m.add('ban', np.c_[Pb[:, 0] + cx, Pb[:, 1] + ztop - 0.25, Pb[:, 2] + zb + 0.42 + nz * 0.015], [[0, 0, nz]] * 5, Ub, Ib)
        tube(m, 'iron', [(cx - w / 2 - 0.25, ztop - 0.2, zb + 0.42), (cx + w / 2 + 0.25, ztop - 0.2, zb + 0.42)], 0.05, 6)
        for ex in (-1, 1): sphere(m, 'gold', 0.1, 6, 4, m=T(cx + ex * (w / 2 + 0.3), ztop - 0.2, zb + 0.42))
    write(OUTG + 'sp_roof_backdrop.glb', m, mats)
    D.setdefault('roofModels', []).append(['sp_roof_backdrop', 0, 0, 0])
    D.setdefault('pads', []).append([0.0, y + top / 2, zb - 0.2, 2 * half + 0.6, top, 0.7, 0])     # can't walk into the drape
    # Spanish moss swagged along the front of the beam
    if 'vines' in outside.META:
        vm, vx = outside.META['vines']; asp = (vx[1] - vm[1]) / (vx[0] - vm[0]); vw = 3.4
        for k, x in enumerate(np.arange(-half - 1.2, half + 1.3, 3.1)):
            w_ = vw * (0.9 + 0.2 * (k % 2))
            D['sdeco'].append(place('vines', float(x), y + top - 0.1 - w_ * asp, zb + 0.36, 0, w_, 'w'))
    return zb

# ---- THE MUDWATER ART WALL (owner: "a massive art piece"; v33: moved off the photo spot - "our art is probably going to suck, put it
# somewhere on the side that we can mess up"): a 24 x 8 m canvas on the west side of the roof, towards the front (behind
# the photographers, out of every stage photo), facing the terrace. 30 x 10 paint squares of 0.8 m, two paint stands with 13 colours + an eraser, a signing lectern
# and a timber name board along the top. The painting itself is done in spire_src.html (THE ART WALL).
def artwall(D, L, FL):
    """built in a local frame (canvas centred on x, facing +z), then turned to stand on the west side of the roof facing the middle:
    seen from the photo stage it is only a thin edge, so it never spoils the pictures"""
    y = FL['roof']
    COLS, ROWS, C = 30, 10, 0.8
    W, H = COLS * C, ROWS * C
    CX, CZ, ANG = -45.6, 19.0, 90.0                             # world spot of the canvas face centre; ANG 90 = faces +x (the terrace)
    WM = M(T(CX, 0, CZ), Ry(ANG))
    Lm = lambda x, yy, z: M(WM, T(x, yy, z))
    def wp(x, z):                                                # local (x, z) -> world (x, z)
        v = WM @ np.array([x, 0, z, 1.0]); return float(v[0]), float(v[2])
    y0 = y + 0.6
    m = Mesh(); mats = dict(MATS)
    mats['canvas'] = dict(color=(0.93, 0.89, 0.8, 1), emis=(0.16, 0.15, 0.13), rough=0.95)
    from glb import quad
    quad(m, 'canvas', W, H, Lm(0, y0 + H / 2, 0))
    for sx in (-1, 1):                                           # two great timber posts standing on the deck, a beam on top and under
        bevel_box(m, 'dark', 0.5, H + 2.9, 0.5, 0.04, m=Lm(sx * (W / 2 + 0.25), y + (H + 2.9) / 2, -0.1), uvs=2.0)
    for yy in (y0 - 0.2, y0 + H + 0.2):
        bevel_box(m, 'dark', W + 1.0, 0.4, 0.45, 0.04, m=Lm(0, yy, -0.1), uvs=3.0)
        bevel_box(m, 'gold', W + 0.4, 0.08, 0.5, 0.01, m=Lm(0, yy + (0.2 if yy > y0 else -0.2), 0))
    bevel_box(m, 'dark', W, 0.6, 0.3, 0.03, m=Lm(0, y + 0.3, -0.1), uvs=3.0)                # the plinth under it
    hy = y0 + H + 1.15                                            # the name board along the top
    bevel_box(m, 'dark', W + 1.0, 1.5, 0.2, 0.03, m=Lm(0, hy, -0.12), uvs=3.0)
    bevel_box(m, 'gold', W + 1.0, 0.07, 0.26, 0.01, m=Lm(0, hy + 0.78, -0.1))
    bevel_box(m, 'dark', W + 0.6, 0.12, 0.6, 0.03, m=Lm(0, y + H + 2.95, -0.1), uvs=2.0)    # a little roof over it all
    stands = []
    for sx in (-1, 1):                                            # the paint stands: a waist-high timber table each
        tx, tz = sx * 6.0, 5.0
        bevel_box(m, 'dark', 2.9, 0.12, 0.9, 0.03, m=Lm(tx, y + 0.95, tz), uvs=1.5)
        for lx in (-1.3, 1.3):
            for lz in (-0.35, 0.35): bevel_box(m, 'dark', 0.1, 0.9, 0.1, 0.01, m=Lm(tx + lx, y + 0.45, tz + lz))
        bevel_box(m, 'gold', 2.9, 0.04, 0.04, 0.005, m=Lm(tx, y + 1.0, tz + 0.45))
        wx, wz = wp(tx, tz); stands.append([round(wx, 3), y + 1.01, round(wz, 3), ANG])
    write(OUTG + 'sp_artwall.glb', m, mats)
    D.setdefault('roofModels', []).append(['sp_artwall', 0, 0, 0])
    pads = D.setdefault('pads', [])
    px_, pz_ = wp(0, -0.25); pads.append([px_, y + 0.5 + H / 2, pz_, W + 1.0, H + 1.0, 0.4, ANG])
    for (sx_, sy_, sz_, _) in stands: pads.append([sx_, y + 0.5, sz_, 2.9, 1.0, 0.9, ANG])
    PAL = ['#f4efe2', '#1a1410', '#c8322a', '#f08a24', '#f6d23e', '#9ed03a', '#2e8a3c', '#1f9e8f', '#2d6fc4', '#7a46b8', '#e46aa8', '#7a4a26', '#d9a441', 'erase']
    lx_, lz_ = wp(0, 7.0); bx_, bz_ = wp(0, -0.01)
    D['artwall'] = dict(cols=COLS, rows=ROWS, cell=C, cx=CX, y0=y0, z=CZ, ry=ANG, palette=PAL, stands=stands,
                        sign=[round(lx_, 3), y, round(lz_, 3), ANG], board=[round(bx_, 3), hy, round(bz_, 3), W, ANG])
    if 'lectern' in outside.META:
        D['sdeco'].append(place('lectern', lx_, y, lz_, ANG, 1.35, 'h'))
        pads.append([lx_, y + 0.65, lz_, 1.1, 1.3, 0.9, ANG])
