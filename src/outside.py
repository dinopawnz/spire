"""THE OUTSIDE, to the owner's concept (reference/19_outside_concept.png). Called by build_html.py: outside.apply(D, L, FL, rg).
Everything is placed from the building's own numbers (L['X1'], L['Z1'], the boardwalk), so it follows when the building grows.
  - the boardwalk: carved Meshy railings both sides, Meshy lantern posts with glowing glass every few metres
  - the water: giant Meshy lily pads, glowing teal Meshy crystal clusters, Meshy bonsai islets round the building
  - the sky: Meshy floating rock islands (bobbing slowly), tall floating cliffs far out, a starry night
  - the front: two tall green banners on the facade, a gold baroque Meshy frame round the MUDWATER sign over the doors
  - lanterns hanging under every balcony, moss clumps under the lower ones
  - the floating Mudwater book over the roof in slowly turning gold rings and a gold glyph ring, a gold beam under it
  - strings of warm gold lights linking the floating cards
  - out: the cartoon acorn houses / mangroves / root stumps / red glow plants, the moonbeam slabs"""
import json, math, os, random
import numpy as np
from glb import Mesh, write, quad, tube, sphere, box, T, M, Ry, Rx, S
from kit import MATS

OUTG = '/home/claude/spire/out/glb/'
META = json.load(open(OUTG + 'meshy_meta.json'))
CARTOON = ('bog_acorn_house_lite', 'bog_giant_acorn_lite', 'bog_mangrove_tree_a_lite', 'bog_mangrove_tree_b_lite', 'bog_giant_tree_trunk_lite',
           'bog_giant_trunk_lite', 'bog_tree_trunk_a_lite', 'bog_tree_trunk_b_lite', 'bog_root_pathway_lite', 'mwm_spire', 'lantern_post')
r3 = lambda v: round(float(v), 3)

def place(name, x, y, z, ry, size, axis='l'):
    """[file, x, y, z, ry, s] for a Meshy model standing on (x, y, z), its footprint centred there, sized `size` m along axis"""
    mn, mx = META[name]
    ext = {'w': mx[0] - mn[0], 'h': mx[1] - mn[1], 'd': mx[2] - mn[2], 'l': max(mx[0] - mn[0], mx[2] - mn[2])}[axis]
    s = size / ext
    ccx, ccz = -(mn[0] + mx[0]) / 2 * s, -(mn[2] + mx[2]) / 2 * s
    c, sn = math.cos(math.radians(ry)), math.sin(math.radians(ry))
    return ['sp_m_' + name, r3(x + ccx * c + ccz * sn), r3(y - mn[1] * s), r3(z - ccx * sn + ccz * c), round(ry, 1), round(s, 4)]

def strands(gal):
    """a string of warm gold lights from every floating card to the next, one GLB per ring (rides in the ring's spin group)"""
    mats = dict(gold=MATS['gold'], bulb=dict(color=(1.0, 0.85, 0.5, 1), emis=(1.0, 0.75, 0.35), emis_strength=3.0))
    files = []
    for ri, ring in enumerate(gal):
        m = Mesh(); R = ring['r']; cs = ring['cards']
        for k in range(len(cs)):
            a0, d0 = cs[k][1], cs[k][2]; a1, d1 = cs[(k + 1) % len(cs)][1], cs[(k + 1) % len(cs)][2]
            if a1 < a0: a1 += 360
            p0 = np.array([R * math.sin(math.radians(a0)), d0 + 4.0, R * math.cos(math.radians(a0))])
            p1 = np.array([R * math.sin(math.radians(a1)), d1 + 4.0, R * math.cos(math.radians(a1))])
            pts = []
            for u in np.linspace(0, 1, 12):
                a = math.radians(a0 + (a1 - a0) * u)
                pts.append((R * math.sin(a), d0 + (d1 - d0) * u + 4.0 - 2.2 * math.sin(math.pi * u), R * math.cos(a)))
            tube(m, 'gold', pts, 0.035, 4)
            for p in pts[1:-1]: sphere(m, 'bulb', 0.16, 5, 3, m=T(p[0], p[1] - 0.12, p[2]))
        f = 'sp_strand_%d' % ri; write(OUTG + f + '.glb', m, mats); files.append(f)
    return files

def front_banner():
    """the same green Mudwater banner as inside the lounge (logo + gold card-back emblem, pointed bottom), big, on a gold rod"""
    m = Mesh(); w, h, tip = 6.6, 17.0, 2.4
    B = '/home/claude/spire/tex/banner_mw.jpg'
    mats = dict(gold=MATS['gold'], iron=MATS['iron'], ban=dict(tex=B, rough=0.9, emis_tex=B, emis=(0.1, 0.1, 0.08)))
    P = np.array([[-w / 2, 0, 0], [w / 2, 0, 0], [w / 2, -h, 0], [0, -h - tip, 0], [-w / 2, -h, 0]])
    U = [[0, 0], [1, 0], [1, h / (h + tip)], [0.5, 1], [0, h / (h + tip)]]
    for side, nz in ((0, 1), (1, -1)):
        I = [0, 4, 1, 1, 4, 2, 2, 4, 3] if side == 0 else [0, 1, 4, 1, 2, 4, 2, 3, 4]
        m.add('ban', np.c_[P[:, 0], P[:, 1] - 0.2, P[:, 2] + nz * 0.02], [[0, 0, nz]] * 5, U, I)
    tube(m, 'iron', [(-w / 2 - 0.5, 0, 0), (w / 2 + 0.5, 0, 0)], 0.1, 8)
    for sx in (-1, 1): sphere(m, 'gold', 0.2, 8, 6, m=T(sx * (w / 2 + 0.55), 0, 0))
    write(OUTG + 'sp_frontbanner.glb', m, mats)
    return h + tip

ISLANDS = False      # Meshy floating islands + far cliffs in the sky (owner turned off in v21)
BONSAI = False       # Meshy bonsai islets on the water (owner turned off in v21)

def apply(D, L, FL, rg):
    X1, Z1 = L['X1'], L['Z1']; W = L['walk']; R = random.Random(19)
    add = D['sdeco'].append
    # ---- out with the cartoon pieces, the moonbeam slabs and the red glow plants out on the water
    # (owner, v21: the original water GLBs stay - nothing is removed from D['deco'])
    for k in range(10):                                   # low mist drifting over the water round the boardwalk and the porch
        a = R.uniform(-150, 150); rr = R.uniform(X1 + 10, X1 + 55)
        D['deco'].append(['mist', r3(rr * math.sin(math.radians(a))), 0.0, r3(Z1 * 0.3 + rr * math.cos(math.radians(a))), round(R.uniform(0, 360), 1), round(R.uniform(0.6, 1.0), 2)])
    # (moonbeams kept)
    # ---- the boardwalk: carved railings both sides, lantern posts at every other joint
    w = L['walk_w']; z0, z1 = L['walk_z0'], L['walk_z0'] + L['walk_len']; ya, yb = FL['lounge'], L['walk_y']
    wy = lambda z: ya + (yb - ya) * (z - z0) / (z1 - z0)
    seg = 3.0; zs = list(np.arange(z0 + 1.0, z1 - 0.5, seg))
    for i, zc in enumerate(zs):
        for sx in (-1, 1):
            add(place('railing', sx * (w / 2 + 0.1), wy(zc + seg / 2) - 0.02, zc + seg / 2, 90, seg, 'w'))
            if i % 2 == 0: add(place('lanternpost', sx * (w / 2 + 0.1), wy(zc), zc, 0, 2.9, 'h'))
    # ---- water: lily pads, glowing crystal clusters, bonsai islets
    def water_spot(rmin, rmax, avoid_walk=7.0):
        for _ in range(200):
            a = R.uniform(0, 2 * math.pi); rr = R.uniform(rmin, rmax)
            x, z = rr * math.sin(a), Z1 * 0.3 + rr * math.cos(a)
            if abs(x) < avoid_walk and z > Z1 - 2: continue                        # keep the boardwalk clear
            if abs(x) < X1 + 9 and abs(z) < Z1 + 12: continue                       # not under the porch
            return x, z
        return None
    for k in range(26):
        p = water_spot(X1 + 14, X1 + 70, 6.5)
        if p: add(place('lily', p[0], 0.06, p[1], R.uniform(0, 360), R.uniform(3.0, 6.0), 'l'))
    for k, zc in enumerate(np.arange(z0 + 6, z1 - 4, 9.0)):                        # crystals close to the boardwalk, both sides
        sx = 1 if k % 2 else -1
        add(place('crystals', sx * R.uniform(w / 2 + 3.0, w / 2 + 6.5), -0.3, zc + R.uniform(-2, 2), R.uniform(0, 360), R.uniform(2.2, 3.6), 'h'))
    for k in range(10):
        p = water_spot(X1 + 18, X1 + 85, 9.0)
        if p: add(place('crystals', p[0], -0.4, p[1], R.uniform(0, 360), R.uniform(2.5, 4.5), 'h'))
    for k in range(9 if BONSAI else 0):
        p = water_spot(X1 + 22, X1 + 80, 14.0)
        if p: add(place('bonsai', p[0], -0.8, p[1], R.uniform(0, 360), R.uniform(14.0, 22.0), 'l'))
    # ---- the sky: floating islands (bob slowly), tall floating cliffs far out
    isl = []
    for k in range(11):
        a = math.radians(-165 + k * 330 / 10 + R.uniform(-10, 10)); rr = R.uniform(X1 + 25, X1 + 75)
        x, z = rr * math.sin(a), Z1 * 0.3 + rr * math.cos(a)
        if abs(x) < 25 and z > 0: x += 40 * (1 if x >= 0 else -1)
        p = place('island', x, R.uniform(26, 70), z, R.uniform(0, 360), R.uniform(22, 36), 'h')
        isl.append(p + [round(R.uniform(1.5, 3.0), 2), int(R.uniform(9000, 16000))])
    for k in range(4):
        a = math.radians(-150 + k * 100 + R.uniform(-15, 15)); rr = R.uniform(X1 + 150, X1 + 200)
        p = place('cliff', rr * math.sin(a), R.uniform(8, 22), Z1 * 0.3 + rr * math.cos(a), R.uniform(0, 360), R.uniform(55, 80), 'h')
        isl.append(p + [round(R.uniform(2.0, 4.0), 2), int(R.uniform(14000, 22000))])
    D['fx']['islands'] = isl if ISLANDS else []
    # ---- the front: tall banners, gold frame round the MUDWATER sign
    bh = front_banner()
    top = max(L['balconies']['lines']) - 0.6; zf = Z1 + L['balconies']['depth'] + 0.35
    D['frontBanners'] = [[sx * 14.0, r3(top), r3(zf)] for sx in (-1, 1)]
    pc = L['portico']
    for sx in (-1, 1):                                     # the great double doors, swung wide open against the front wall
        add(place('doorleaf', sx * (4.5 + 1.45), FL['lounge'], Z1 + 0.42, 0, 5.4, 'h'))
    add(place('signframe', 0.0, pc['y'] - 2.6, pc['z'] + 0.05, 0, 11.0, 'w'))
    # ---- lanterns under every balcony edge, moss clumps under the lower balconies on the front
    Dd = L['balconies']['depth']
    for li, y in enumerate(L['balconies']['lines']):
        for side in range(4):
            ln = 2 * X1 if side % 2 == 0 else 2 * Z1
            for t in np.arange(3.5, ln - 2, 7.0):
                u = -ln / 2 + t; o = Dd - 0.35
                x, z = [(u, Z1 + o), (X1 + o, u), (u, -Z1 - o), (-X1 - o, u)][side]
                if side == 0 and y < 12 and abs(x) < 11: continue                  # the portico roof
                add(['sp_lantern_a', r3(x), r3(y - 0.2), r3(z), round(R.uniform(0, 60), 1), 1.6])
        if li < 3:
            for t in np.arange(5.0, 2 * X1 - 3, 9.5):
                x = -X1 + t
                if y < 12 and abs(x) < 11: continue
                add(place('mossclump', x, y - 1.5, Z1 + Dd - 0.1, R.choice([0, 180]), 1.8, 'w'))
    # (owner, v21: the original floating Mudwater pack, gold + teal rings and beam stay on top - no book)
    # (the floating cards stay exactly as they are - owner)
    print('outside: placed', len(D['sdeco']), 'spire models;', len(isl), 'sky islands/cliffs')
