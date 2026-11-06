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
    print('roof: stage, arch, %d planters, %d fires, %d light strands, %d pads' % (sum(1 for e in D['sdeco'] if e[0] == 'sp_m_planter'), len(fires), len(strands), len(pads)))
