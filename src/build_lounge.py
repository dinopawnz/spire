"""MUDWATER SPIRE v2 - floor 1: THE LOUNGE (interior furnishings) for the rectangular hall.
Writes sp_f1_lounge.glb (everything static), sp_f1_col.glb, and the moving bits used by the bar mechanics:
sp_tap.glb (one tap handle), sp_pour.glb (beer stream), sp_foam.glb, sp_mug.glb, sp_fan.glb (ceiling fan blades),
sp_chandelier.glb, sp_jukebox_glow.glb, sp_guestbook.glb, sp_barrel.glb.
Lounge plan (tower space, front = +z): the bar runs along the back (z -16.5), shelves on the back wall,
the fireplace on the west face, the jukebox and the card tables on the east side, sofas round two big rugs."""
import math, random, json
import numpy as np
from glb import *
from kit import *

OUT = '/home/claude/spire/out/glb/'
MW = '/home/claude/dinopawnz/mudwater/'
rng = random.Random(11)
LY = json.load(open('/home/claude/spire/out/layout.json'))
Y = LY['FL']['lounge'] + 0.005
A1 = 27.0; dA = A1 - 24.0                     # the furniture code was written for the old tower: pieces are built in its coords, then moved
X1N, Z1N = LY['X1'], LY['Z1']; DX, DZ = X1N - 42.5, Z1N - 30.0       # v24: the room is bigger - the walls moved out by DX / DZ
KX, KZ = X1N / 42.5, Z1N / 30.0
GROUPS = [(22.0, 19.5 + DZ), (22.0, 8.0 + DZ), (-38.0, 28.0), (40.0, -20.0), (-40.0, -20.0)]           # sofa groups: by the fireplace (front-east) + new corners
X1, Z1 = LY['X1'] - 0.32, LY['Z1'] - 0.32
M_ = dict(MATS)
M_['rug'] = dict(tex=MW + 'mwcb_back.jpg', rough=1.0)
M_['beer'] = dict(color=(1.0, 0.62, 0.12, 0.82), emis=(0.45, 0.22, 0.02), alpha='BLEND', rough=0.1)
M_['foamw'] = dict(color=(1.0, 0.97, 0.9, 1), emis=(0.25, 0.24, 0.2), rough=0.9)
M_['bottle_g'] = dict(color=(0.2, 0.55, 0.25, 0.75), emis=(0.05, 0.2, 0.05), alpha='BLEND', rough=0.05)
M_['bottle_a'] = dict(color=(0.75, 0.38, 0.08, 0.8), emis=(0.3, 0.12, 0.0), alpha='BLEND', rough=0.05)
M_['bottle_c'] = dict(color=(0.85, 0.9, 0.95, 0.5), emis=(0.15, 0.15, 0.18), alpha='BLEND', rough=0.05)
M_['label'] = dict(color=(0.92, 0.84, 0.62, 1), rough=0.8)
M_['mirror'] = dict(color=(0.55, 0.5, 0.42, 1), metal=1.0, rough=0.08)
M_['felt'] = dict(color=(0.08, 0.28, 0.16, 1), rough=1.0)
M_['chalk'] = dict(color=(0.07, 0.08, 0.07, 1), rough=0.95)
M_['pond'] = dict(color=(0.03, 0.045, 0.035, 1), emis=(0.01, 0.03, 0.02), rough=0.03, metal=0.5)        # dark still swamp water
M_['shroom'] = dict(color=(0.5, 0.22, 0.06, 1), emis=(1.0, 0.36, 0.05), emis_strength=0.5, rough=0.6)     # warm amber, like the concept
M_['lglass'] = dict(color=(0.6, 0.26, 0.05, 1), emis=(1.0, 0.4, 0.06), emis_strength=0.62, rough=0.3)     # iron-lantern glass
M_['gills'] = dict(color=(0.7, 0.3, 0.06, 1), emis=(1.0, 0.42, 0.06), emis_strength=0.7, rough=0.7, double=True)   # glowing mushroom undersides
for _n, _r in (('dec_puddle1', 0.12), ('dec_puddle2', 0.12), ('dec_puddle3', 0.14)):     # puddle / mud decals: never pitch black
    M_[_n] = dict(tex=TEX + _n + '.png', emis_tex=TEX + _n + '.png', emis=(0.2, 0.15, 0.1), alpha='BLEND', rough=_r, metal=0.0)
M_['pool'] = dict(tex=TEX + 'pool.png', emis_tex=TEX + 'pool.png', emis=(1.0, 0.62, 0.26), alpha='BLEND', rough=0.2)      # lantern light on the wet floor
M_['dance'] = dict(tex=TEX + 'wood_planks.jpg', emis_tex=TEX + 'wood_planks.jpg', emis=(0.6, 0.33, 0.1), rough=0.25)
M_['puddle'] = dict(color=(0.035, 0.026, 0.016, 0.9), metal=0.6, rough=0.02, alpha='BLEND')
M_['banner'] = dict(tex=TEX + 'banner_mw.jpg', rough=0.9, double=True)
M_['ember'] = dict(color=(1, 0.4, 0.1, 1), emis=(1.0, 0.35, 0.05), emis_strength=2.0)
L1 = Mesh(); C1 = Mesh()
BAR_DX, BAR_DZ = -21.5, 27.5                   # old bar (x -12..6, counter z -19.5) -> x -33.5..-15.5, counter z 8

# ---- Meshy props: high-detail sculpted models replace the code-built furniture. Each call records [file, x, y, z, ry, scale] for
# build_html to place (sp_m_<name>.glb, made by meshy_props.py, which also writes meshy_meta.json = each model's bounding box).
import os
MESHY_PROPS = True
_META_P = OUT + 'meshy_meta.json'
META = json.load(open(_META_P)) if os.path.exists(_META_P) else {}
META_RY = json.load(open(OUT + 'meshy_ry.json')) if os.path.exists(OUT + 'meshy_ry.json') else {}   # per-model turn so its front faces +z
MPROPS = []; PROP_XF = None
def mp(name, mm, size):
    """place Meshy model `name` with the pose of matrix mm (floor point + yaw), scaled so its size[0] extent ('w' x, 'd' z, 'h' y,
    'l' longest of x/z) equals size[1] metres. False if the model isn't built (then the code-built piece is used)."""
    if not MESHY_PROPS or name not in META: return False
    mm_local = np.asarray(mm)
    mm = np.asarray(mm if PROP_XF is None else PROP_XF @ np.asarray(mm))
    ry = math.degrees(math.atan2(mm[0, 2], mm[2, 2])) + META_RY.get(name, 0)
    mn, mx = META[name]
    ext = {'w': mx[0] - mn[0], 'h': mx[1] - mn[1], 'd': mx[2] - mn[2], 'l': max(mx[0] - mn[0], mx[2] - mn[2])}[size[0]]
    sc = size[1] / ext
    ccx, ccz = -(mn[0] + mx[0]) / 2 * sc, -(mn[2] + mx[2]) / 2 * sc          # centre the model's footprint on the point
    c, sn = math.cos(math.radians(ry)), math.sin(math.radians(ry))
    MPROPS.append(['sp_m_' + name, round(float(mm[0, 3] + ccx * c + ccz * sn), 3), round(float(mm[1, 3] - mn[1] * sc), 3),
                   round(float(mm[2, 3] - ccx * sn + ccz * c), 3), round(ry, 1), round(sc, 4)])
    if name in SOLID:            # solid: an invisible box the size of the model (slightly inset), so nobody walks through it
        fx, fy, fz = SOLID[name]
        wx, hy, dz = (mx[0] - mn[0]) * sc * fx, (mx[1] - mn[1]) * sc * fy, (mx[2] - mn[2]) * sc * fz
        collider_box(C1, wx, hy, dz, M(mm_local, Ry(META_RY.get(name, 0)), T(0, hy / 2, 0)))
    return True
# which Meshy props get a box collider (fraction of the model's width, height, depth). The pond, grottos, booths, hearth and trees
# keep their own hand-placed colliders.
SOLID = {'sofa': (0.9, 0.75, 0.85), 'armchair': (0.85, 0.75, 0.85), 'cardtable': (0.8, 1.0, 0.8), 'coffeetable': (0.9, 1.0, 0.85),
         'stool': (0.6, 1.0, 0.6), 'barrel': (0.85, 1.0, 0.85), 'bench': (0.9, 0.8, 0.8)}

def barrel(m, mm, r=0.42, h=1.1, lying=False, mat='dark'):
    if not lying and np.asarray(mm)[1, 1] > 0.95 and mp('barrel', mm, ('h', h)): return
    prof = [(r * (1 + 0.12 * math.sin(math.pi * i / 10)), h * i / 10) for i in range(11)]
    lathe(m, mat, prof, 20, m=mm, cap_top=True, cap_bot=True, uvs_u=3)
    for y in (0.1, h - 0.1, h * 0.38, h * 0.62):
        rr = r * (1 + 0.12 * math.sin(math.pi * y / h)) + 0.012
        lathe(m, 'iron', [(rr, y - 0.03), (rr, y + 0.03)], 20, m=mm)

def chesterfield(m, mm, w=2.6, leather='leather'):
    """tufted leather sofa, front faces +z, origin at floor centre"""
    if mp('sofa', mm, ('w', w)): return
    d = 0.95
    bevel_box(m, leather, w - 0.3, 0.45, d - 0.15, 0.08, m=M(mm, T(0, 0.3, 0.05)), uvs=1.5)           # base
    for k in range(3):                                                                                  # seat cushions
        cw = (w - 0.55) / 3
        bevel_box(m, leather, cw - 0.02, 0.2, d - 0.35, 0.08, m=M(mm, T(-w / 2 + 0.27 + cw * (k + 0.5), 0.6, 0.13)), uvs=1.5)
    bevel_box(m, leather, w - 0.3, 0.6, 0.25, 0.1, m=M(mm, T(0, 0.85, -d / 2 + 0.17)), uvs=1.5)         # back
    for s in (-1, 1):                                                                                   # rolled arms
        bevel_box(m, leather, 0.25, 0.55, d, 0.1, m=M(mm, T(s * (w / 2 - 0.12), 0.55, 0)), uvs=1.5)
        lathe(m, leather, [(0.0, 0), (0.17, 0.0), (0.2, 0.08), (0.2, d - 0.08), (0.17, d), (0.0, d)], 12, m=M(mm, T(s * (w / 2 - 0.12), 0.83, -d / 2), Rx(90)), uvs_u=1.0)
    for i in range(int(w / 0.22)):                                                                      # tufting buttons
        for j in range(2):
            sphere(m, leather, 0.025, 6, 4, m=M(mm, T(-w / 2 + 0.35 + i * 0.22 + (j % 2) * 0.11, 0.78 + j * 0.2, -d / 2 + 0.3)))
    for sx in (-1, 1):
        for sz in (-1, 1): lathe(m, 'dark', [(0.05, 0), (0.06, 0.08), (0.04, 0.1)], 8, m=M(mm, T(sx * (w / 2 - 0.15), 0, sz * (d / 2 - 0.1))))
    gold_nails = [M(mm, T(sx * (w / 2 - 0.12), 0.32, -d / 2 + 0.05 + k * 0.1)) for sx in (-1, 1) for k in range(9)]
    for g in gold_nails: sphere(m, 'brass', 0.012, 5, 3, m=g)

def armchair(m, mm, leather='leather'):
    if mp('armchair', mm, ('h', 1.2)): return
    w = 1.05; d = 0.95
    bevel_box(m, leather, w - 0.3, 0.42, d - 0.15, 0.08, m=M(mm, T(0, 0.3, 0.05)))
    bevel_box(m, leather, w - 0.32, 0.2, d - 0.35, 0.08, m=M(mm, T(0, 0.6, 0.13)))
    bevel_box(m, leather, w - 0.3, 0.75, 0.25, 0.1, m=M(mm, T(0, 0.9, -d / 2 + 0.17), Rx(-8)))
    for s in (-1, 1):
        bevel_box(m, leather, 0.24, 0.5, d, 0.09, m=M(mm, T(s * (w / 2 - 0.12), 0.55, 0)))
        lathe(m, leather, [(0.0, 0), (0.15, 0.0), (0.18, 0.08), (0.18, d - 0.08), (0.15, d), (0.0, d)], 10, m=M(mm, T(s * (w / 2 - 0.12), 0.8, -d / 2), Rx(90)))

def stool(m, mm):
    if mp('stool', mm, ('h', 0.9)): return
    lathe(m, 'leather', [(0.0, 0.78), (0.2, 0.78), (0.22, 0.84), (0.19, 0.9), (0.0, 0.92)], 14, m=mm)
    lathe(m, 'dark', [(0.18, 0.7), (0.2, 0.78)], 14, m=mm)
    for k in range(4):
        a = k * 90 + 45
        p0 = np.array([0.14 * math.sin(math.radians(a)), 0.72, 0.14 * math.cos(math.radians(a))]); p1 = np.array([0.24 * math.sin(math.radians(a)), 0, 0.24 * math.cos(math.radians(a))])
        tube(m, 'dark', [p0, p1], 0.025, 6, m=mm)
    lathe(m, 'brass', [(0.19, 0.3), (0.2, 0.32), (0.19, 0.34)], 14, m=mm)

def meshy_mug(src, dst, bb, height):
    """copy a Meshy model under a new root node that scales it to `height` m and stands its base on the origin, centred"""
    import struct as _st
    js, b = read_glb(src); mn, mx = bb; sc = height / (mx[1] - mn[1])
    t = [-(mn[0] + mx[0]) / 2 * sc, -mn[1] * sc, -(mn[2] + mx[2]) / 2 * sc]
    roots = js['scenes'][js.get('scene', 0)]['nodes']
    js['nodes'].append({'name': 'mug_root', 'scale': [sc, sc, sc], 'translation': t, 'children': roots})
    js['scenes'][js.get('scene', 0)]['nodes'] = [len(js['nodes']) - 1]
    j = json.dumps(js, separators=(',', ':')).encode(); j += b' ' * ((4 - len(j) % 4) % 4); b = bytes(b) + b'\0' * ((4 - len(b) % 4) % 4)
    with open(dst, 'wb') as f:
        f.write(_st.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(b))); f.write(_st.pack('<II', len(j), 0x4E4F534A)); f.write(j)
        f.write(_st.pack('<II', len(b), 0x004E4942)); f.write(b)
    return round(sc, 4)

def bottle(m, mm, kind):
    mat = {'g': 'bottle_g', 'a': 'bottle_a', 'c': 'bottle_c'}[kind]
    h = rng.uniform(0.28, 0.36); r = rng.uniform(0.04, 0.055)
    lathe(m, mat, [(0.0, 0), (r, 0.005), (r, h * 0.62), (r * 0.45, h * 0.8), (0.016, h * 0.86), (0.016, h), (0.0, h)], 10, m=mm)
    lathe(m, 'label', [(r + 0.002, h * 0.2), (r + 0.002, h * 0.42)], 10, m=mm, a0=-70, a1=70)
    lathe(m, 'dark', [(0.018, h), (0.018, h + 0.03), (0.0, h + 0.03)], 6, m=mm)

def mug(m, mm, full=True):
    lathe(m, 'bottle_c', [(0.0, 0.0), (0.065, 0.0), (0.07, 0.02), (0.07, 0.17), (0.072, 0.17), (0.0, 0.17)], 14, m=mm)
    tube(m, 'bottle_c', [(0.07, 0.04, 0), (0.11, 0.06, 0), (0.12, 0.1, 0), (0.11, 0.14, 0), (0.07, 0.15, 0)], 0.012, 6, m=mm)
    if full:
        lathe(m, 'beer', [(0.0, 0.015), (0.062, 0.015), (0.064, 0.14), (0.0, 0.14)], 14, m=mm)
        lathe(m, 'foamw', [(0.0, 0.14), (0.066, 0.14), (0.07, 0.16), (0.05, 0.19), (0.0, 0.2)], 14, m=mm)

# ---------------------------------------------------------------------------- the room
def floor_and_rugs():
    for (cx, cz), w in zip(GROUPS, (7.0, 5.0, 6.0, 6.0, 6.0)):
        h = w * 711 / 512
        quad(L1, 'rug', w, h, M(T(cx, Y + 0.078, cz), Rx(-90), Rz(90)))
        for s in (-1, 1):
            for k in range(int(w / 0.06)):
                x = -w / 2 + k * 0.06
                box(L1, 'pale', 0.012, 0.004, 0.12, m=M(T(cx, Y + 0.079, cz), Ry(90), T(x, 0, s * (h / 2 + 0.05))), faces='Y')
    # the foyer: a big glowing Mudwater medallion inside the grand doors, and a runner from the doors to the lifts
    floor_plaque(0.0, 19.5, 10.0)

def floor_plaque(cx, cz, w):
    """the MUDWATER logo inlaid in the floor: a long gold-framed plaque with pointed ends, as in the owner's lounge concept"""
    h = w * 0.27; e = h * 0.55
    hexo = lambda W, H, E: [(-W / 2, 0), (-W / 2 + E, -H / 2), (W / 2 - E, -H / 2), (W / 2, 0), (W / 2 - E, H / 2), (-W / 2 + E, H / 2)]
    base = M(T(cx, Y, cz), Rx(-90))
    extrude(L1, 'gold', hexo(w, h, e), 0.03, m=base)
    extrude(L1, 'dark', hexo(w - 0.36, h - 0.3, e - 0.12), 0.038, m=base, uvs=2.0)
    extrude(L1, 'gold', hexo(w - 0.62, h - 0.52, e - 0.2), 0.04, m=base)
    extrude(L1, 'dark', hexo(w - 0.74, h - 0.62, e - 0.24), 0.042, m=base, uvs=2.0)
    lw = w * 0.74
    quad(L1, 'logo_floor', lw, lw * 323 / 1334, M(T(cx, Y + 0.046, cz), Rx(-90)))
    for sx in (-1, 1):          # little gold leaf points at both ends
        extrude(L1, 'gold', [(0, -0.22), (0.5, 0), (0, 0.22), (-0.12, 0)], 0.044, m=M(base, T(sx * (w / 2 - e * 0.55), 0, 0), S(sx, 1, 1)))

def the_bar():
    global L1, C1
    RL, RC = L1, C1; L1 = Mesh(); C1 = Mesh()
    bz = -16.5 - dA; x0, x1 = -12.0, 6.0; Lb = x1 - x0; xc = (x0 + x1) / 2
    # counter: panelled front with raised panels, brass foot rail, thick glossy top with a rounded nose
    bevel_box(L1, 'dark', Lb, 1.05, 0.7, 0.03, m=T(xc, Y + 0.52, bz), uvs=3.0)
    for k in range(int(Lb / 1.2)):
        x = x0 + 0.6 + k * 1.2
        bevel_box(L1, 'plank', 0.95, 0.65, 0.06, 0.025, m=T(x, Y + 0.55, bz + 0.37), uvs=1.5)
        bevel_box(L1, 'dark', 0.12, 1.05, 0.1, 0.02, m=T(x + 0.6, Y + 0.52, bz + 0.38))
    bevel_box(L1, 'bartop', Lb + 0.4, 0.09, 1.05, 0.04, m=T(xc, Y + 1.1, bz + 0.05), uvs=4.0)
    lathe(L1, 'bartop', [(0.0, 0), (0.06, 0), (0.06, Lb + 0.4), (0.0, Lb + 0.4)], 10, m=M(T(x0 - 0.2, Y + 1.1, bz + 0.58), Rz(-90)))
    tube(L1, 'brass', [(x0 - 0.1, Y + 0.22, bz + 0.62), (x1 + 0.1, Y + 0.22, bz + 0.62)], 0.035, 10)
    for k in range(10): tube(L1, 'brass', [(x0 + 0.5 + k * 1.9, Y + 0.0, bz + 0.45), (x0 + 0.5 + k * 1.9, Y + 0.22, bz + 0.62)], 0.02, 6)
    collider_box(C1, Lb + 0.4, 1.15, 1.1, T(xc, Y + 0.58, bz + 0.05))
    # back counter + under-bar shelves
    bevel_box(L1, 'dark', Lb, 0.95, 0.6, 0.03, m=T(xc, Y + 0.48, bz - 1.7), uvs=3.0)
    bevel_box(L1, 'bartop', Lb + 0.1, 0.06, 0.7, 0.02, m=T(xc, Y + 0.98, bz - 1.7), uvs=4.0)
    collider_box(C1, Lb, 1.0, 0.7, T(xc, Y + 0.5, bz - 1.7))
    # the back bar: mirror, four shelves of glowing bottles between carved posts, kegs, the logo, a chalkboard
    wz = -22.6 - dA
    bevel_box(L1, 'dark', Lb + 1.0, 4.6, 0.3, 0.04, m=T(xc, Y + 3.3, wz), uvs=3.0)
    quad(L1, 'mirror', Lb - 4, 1.2, T(xc, Y + 1.9, wz + 0.17))
    for k in range(4):
        y = Y + 2.7 + k * 0.62
        bevel_box(L1, 'plank', Lb - 0.4, 0.05, 0.36, 0.015, m=T(xc, y, wz + 0.33), uvs=3.0)
        x = x0 + 0.5
        while x < x1 - 0.4:
            bottle(L1, T(x, y + 0.025, wz + 0.33 + rng.uniform(-0.06, 0.06)), rng.choice('gaac'))
            x += rng.uniform(0.13, 0.2)
    for k in range(7):
        x = x0 + k * Lb / 6
        bevel_box(L1, 'dark', 0.24, 5.2, 0.4, 0.04, m=T(x, Y + 2.6, wz + 0.25))
        lathe(L1, 'brass', [(0.0, 0), (0.08, 0), (0.06, 0.12), (0.0, 0.16)], 8, m=T(x, Y + 5.2, wz + 0.25))
    collider_box(C1, Lb + 1, 5.2, 0.8, T(xc, Y + 2.6, wz + 0.3))
    for (kx, ky) in [(x1 + 1.2, Y + 0.0), (x1 + 1.2, Y + 0.95), (x0 - 1.0, Y + 0.0)]:
        barrel(L1, M(T(kx, ky + 0.45, wz + 0.4), Rz(90), T(0, -0.55, 0)), r=0.42, h=1.1)
        cyl(L1, 'brass', 0.025, 0.18, 6, m=M(T(kx, ky + 0.45, wz + 0.4 + 0.5), Rx(90)))
    collider_box(C1, 1.2, 1.9, 1.0, T(x1 + 1.2, Y + 0.95, wz + 0.4))
    # chalkboard menu
    bevel_box(L1, 'dark', 2.4, 1.6, 0.08, 0.02, m=T(x1 + 1.6, Y + 3.9, wz + 0.3))
    quad(L1, 'chalk', 2.2, 1.4, T(x1 + 1.6, Y + 3.9, wz + 0.35))
    # the MUDWATER logo board across the top of the back bar
    quad(L1, 'logo', 7.5, 7.5 * 323 / 1334, T(xc, Y + 5.6, wz + 0.4))
    # beer engine: six brass taps on a brass rail, drip tray
    tx0 = -7.0
    box(L1, 'brass', 3.6, 0.08, 0.12, m=T(tx0 + 1.5, Y + 1.55, bz - 0.25))
    for k in range(6):
        x = tx0 + k * 0.6
        cyl(L1, 'brass', 0.035, 0.42, 8, m=T(x, Y + 1.15, bz - 0.25))
        cyl(L1, 'brass', 0.03, 0.22, 8, m=M(T(x, Y + 1.5, bz - 0.25), Rx(90)))
        lathe(L1, 'brass', [(0.025, 0), (0.035, 0.05), (0.02, 0.12)], 8, m=M(T(x, Y + 1.47, bz - 0.05), Rx(180)))
    bevel_box(L1, 'iron', 3.9, 0.04, 0.32, 0.01, m=T(tx0 + 1.5, Y + 1.17, bz - 0.05))
    # glasses hanging over the bar from a rack
    bevel_box(L1, 'dark', 6.0, 0.12, 0.5, 0.02, m=T(-1.0, Y + 3.2, bz - 0.4))
    for k in range(18):
        x = -3.8 + k * 0.32
        lathe(L1, 'bottle_c', [(0.0, 0.0), (0.04, 0.0), (0.035, 0.08), (0.008, 0.1), (0.008, 0.2), (0.03, 0.22), (0.0, 0.22)], 8, m=M(T(x, Y + 3.13, bz - 0.4), Rx(180)))
    for s in (-1, 1): tube(L1, 'iron', [(-1.0 + s * 2.8, Y + 3.25, bz - 0.4), (-1.0 + s * 2.8, Y + 7.6, bz - 0.4)], 0.02, 5)
    # stools
    for k in range(11):
        stool(L1, T(x0 + 0.9 + k * 1.6, Y, bz + 1.25))
    mv = T(BAR_DX, 0, BAR_DZ); RL.merge(L1, mv); RC.merge(C1, mv); L1, C1 = RL, RC
    # the back of the back-bar faces the room: a row of framed cards on it
    wz = -22.6 - dA + BAR_DZ
    for k, n in enumerate([5, 14, 27, 44, 63, 71, 88, 97]):
        hang_card(n, M(T(x0 + BAR_DX + 1.3 + k * 2.2, Y + 2.6, wz - 0.2), Ry(180)))
    return dict(taps=[[tx0 + k * 0.6 + BAR_DX, Y + 1.5, bz - 0.25 + BAR_DZ] for k in range(6)], bz=bz + BAR_DZ, x0=x0 + BAR_DX, x1=x1 + BAR_DX)

def fireplace():
    global L1, C1, PROP_XF
    RL, RC = L1, C1; L1 = Mesh(); C1 = Mesh(); PROP_XF = M(T(22.0, 0, 3.0 + DZ), Ry(90))
    # big mud-stone hearth on the west face (x = -23.6)
    fx = -23.0 - dA; fz = 2.0
    meshy_fire = mp('fireplace', M(T(fx + 0.4, Y, fz), Ry(90)), ('w', 5.2))
    for k in (range(7) if not meshy_fire else []):
        w = 4.6 - k * 0.2 if k > 4 else 4.6
        bevel_box(L1, 'mud', 1.3, 1.0, w, 0.08, m=T(fx + 0.1, Y + 0.5 + k * 1.0, fz), uvs=2.0)
    if not meshy_fire:
        box(L1, 'black', 0.6, 1.5, 2.4, m=T(fx + 0.5, Y + 0.95, fz))
        bevel_box(L1, 'dark', 0.6, 0.25, 5.2, 0.04, m=T(fx + 0.75, Y + 2.25, fz), uvs=3.0)             # mantel
        bevel_box(L1, 'mud', 1.8, 0.25, 5.4, 0.05, m=T(fx + 0.8, Y + 0.12, fz), uvs=2.0)              # hearth stone
    for k in (range(5) if not meshy_fire else []): cyl(L1, 'bark', 0.09, 1.3, 8, m=M(T(fx + 0.55, Y + 0.32 + (k % 2) * 0.14, fz - 0.6 + k * 0.3), Rx(90), T(0, -0.65, 0)))
    for k in (range(9) if not meshy_fire else []): sphere(L1, 'ember', 0.07, 6, 4, m=T(fx + 0.55 + rng.uniform(-0.15, 0.15), Y + 0.28, fz + rng.uniform(-0.9, 0.9)))
    collider_box(C1, 1.6, 7, 4.8, T(fx + 0.1, Y + 3.5, fz))
    # mounted gator skull... a ship's wheel above the mantel and two armchairs facing the fire
    if not meshy_fire:
        mm = M(T(fx + 0.82, Y + 3.8, fz), Ry(90))
        lathe(L1, 'dark', [(0.85, -0.05), (0.95, -0.05), (0.95, 0.05), (0.85, 0.05)], 24, m=M(mm, Rx(90)))
        lathe(L1, 'brass', [(0.0, -0.08), (0.18, -0.08), (0.18, 0.08), (0.0, 0.08)], 12, m=M(mm, Rx(90)))
        for k in range(8):
            a = k * 45; d = np.array([math.sin(math.radians(a)), math.cos(math.radians(a)), 0])
            tube(L1, 'dark', [np.zeros(3) + d * 0.15, d * 1.25], 0.035, 6, m=mm)
            lathe(L1, 'dark', [(0.0, 0), (0.05, 0.02), (0.04, 0.2), (0.0, 0.25)], 6, m=M(mm, T(*(d * 1.2)), look_basis(d), Rx(-90)))
    for k, dz in enumerate((-2.2, 2.2)):
        armchair(L1, M(T(fx + 4.0, Y, fz + dz), Ry(-90 + (20 if dz < 0 else -20))), 'leatherg')
        collider_box(C1, 1.0, 0.9, 1.0, T(fx + 4.0, Y + 0.45, fz + dz))
    PROP_XF = None
    mv = M(T(22.0, 0, 3.0 + DZ), Ry(90)); RL.merge(L1, mv); RC.merge(C1, mv); L1, C1 = RL, RC          # on the front wall, facing into the room
    p = mv @ np.array([fx + 0.55, Y + 0.3, fz, 1])
    return dict(fire=[round(float(p[0]), 3), round(float(p[1]), 3), round(float(p[2]), 3)])

def lounge_seating():
    groups = GROUPS
    for gi, (cx, cz) in enumerate(groups):
        for k, (dx, dz, ry) in enumerate([(0, -2.3, 0), (0, 2.3, 180), (-2.9, 0, 90), (2.9, 0, -90)]):
            if gi == 1 and k >= 2: continue
            chesterfield(L1, M(T(cx + dx, Y, cz + dz), Ry(ry)), 2.8 if k < 2 else 2.2, 'leather' if (k + gi) % 2 == 0 else 'leatherg')
            collider_box(C1, 2.8 if k < 2 and ry in (0, 180) else 1.0, 0.9, 1.0 if ry in (0, 180) else 2.2, T(cx + dx, Y + 0.45, cz + dz))
        # coffee table: thick planks on iron legs, with a lantern, a deck of cards and mugs
        if not mp('coffeetable', T(cx, Y, cz), ('l', 2.2)):
            bevel_box(L1, 'bartop', 2.2, 0.12, 1.1, 0.03, m=T(cx, Y + 0.48, cz), uvs=2.0)
            for sx in (-1, 1):
                for sz in (-1, 1): bevel_box(L1, 'iron', 0.08, 0.42, 0.08, 0.01, m=T(cx + sx * 0.95, Y + 0.21, cz + sz * 0.45))
        collider_box(C1, 2.2, 0.55, 1.1, T(cx, Y + 0.28, cz))
        if 'coffeetable' not in META: mug(L1, T(cx + 0.5, Y + 0.54, cz + 0.2)); mug(L1, T(cx - 0.6, Y + 0.54, cz - 0.15), full=False)
        # barrel side tables with candles
        for s in (-1, 1):
            barrel(L1, T(cx + s * 2.0, Y, cz - 3.4 if gi == 0 else cz - 3.3), r=0.36, h=0.85)
            lathe(L1, 'label', [(0.0, 0), (0.04, 0), (0.04, 0.16), (0.0, 0.16)], 8, m=T(cx + s * 2.0, Y + 0.87, cz - 3.4))
            sphere(L1, 'glow', 0.025, 6, 4, m=T(cx + s * 2.0, Y + 1.06, cz - 3.4))

def card_tables():
    for (cx, cz) in [(12.0, -10.0), (19.0, -17.0), (-26.0, -15.0), (-16.0, -15.0), (-14.0, 22.0), (-24.0, 22.0),
                     (-36.0, 2.0), (-36.0, 14.0), (36.0, -4.0), (36.0, 8.0), (-12.0, 34.0), (8.0, 34.0), (24.0, -30.0), (-24.0, -30.0)]:     # v24: more tables in the new space
        meshy_table = mp('cardtable', M(T(cx, Y, cz), Ry(rng.uniform(0, 360))), ('l', 2.3))
        if not meshy_table:
            lathe(L1, 'bartop', [(1.05, Y + 0.76), (1.2, Y + 0.78), (1.2, Y + 0.84), (1.05, Y + 0.86)], 24, m=T(cx, 0, cz))
            lathe(L1, 'felt', [(0.0, Y + 0.81), (1.06, Y + 0.81), (1.06, Y + 0.83), (0.0, Y + 0.83)], 24, m=T(cx, 0, cz))
            lathe(L1, 'dark', [(0.25, Y), (0.12, Y + 0.1), (0.1, Y + 0.7), (0.3, Y + 0.78)], 12, m=T(cx, 0, cz))
        collider_box(C1, 2.2, 0.85, 2.2, T(cx, Y + 0.42, cz))
        for k in range(4):
            a = k * 90 + 45; x = cx + 1.65 * math.sin(math.radians(a)); z = cz + 1.65 * math.cos(math.radians(a))
            armchair(L1, M(T(x, Y, z), Ry(a + 180)), 'leather')
        for k in (range(6) if not meshy_table else []):   # poker chips + cards
            a = k * 60; x = cx + 0.6 * math.sin(math.radians(a)); z = cz + 0.6 * math.cos(math.radians(a))
            for j in range(rng.randint(2, 6)): cyl(L1, rng.choice(['gold', 'velvet', 'velvett']), 0.035, 0.008, 10, m=T(x, Y + 0.835 + j * 0.009, z))

def jukebox():
    jx, jz = 5.4, -27.6
    mm = M(T(jx, Y + 0.7, jz), Ry(0))
    bevel_box(L1, 'bartop', 1.4, 1.5, 0.8, 0.06, m=M(mm, T(0, 0.75, 0)))
    lathe(L1, 'bartop', [(0.0, -0.4), (0.7, -0.4), (0.7, 0.4), (0.0, 0.4)], 20, m=M(mm, T(0, 1.5, 0), Rx(90)), a0=-90, a1=90)
    quad(L1, 'mudglow', 1.1, 0.5, M(mm, T(0, 1.0, 0.41)))
    lathe(L1, 'mudglow', [(0.52, 0.41), (0.58, 0.41)], 20, m=M(mm, T(0, 1.5, 0), Rx(-90)), a0=-90, a1=90)
    for k in range(9): box(L1, 'brass', 1.0, 0.025, 0.03, m=M(mm, T(0, 0.15 + k * 0.06, 0.42)))
    quad(L1, 'label', 0.9, 0.22, M(mm, T(0, 1.36, 0.415)))
    collider_box(C1, 1.5, 2.2, 0.9, T(jx, Y + 1.8, jz))
    return dict(jukebox=[jx, Y + 1.7, jz + 0.45])

def hang_card(n, mm, w=1.3):
    h = w * 1.8 / 1.3
    M_['card%d' % n] = dict(tex=MW + 'mwc_%03d.jpg' % n, emis_tex=MW + 'mwc_%03d.jpg' % n, emis=(0.25, 0.25, 0.25), rough=0.6)
    quad(L1, 'card%d' % n, w, h, M(mm, T(0, 0, 0.06)))
    bevel_box(L1, 'gold', w + 0.25, h + 0.25, 0.06, 0.02, m=mm)
    box(L1, 'brass', 0.5, 0.04, 0.16, m=M(mm, T(0, h / 2 + 0.3, 0.05)))
    sphere(L1, 'glow', 0.06, 8, 6, m=M(mm, T(0, h / 2 + 0.36, 0.12)))

FIRE_X = 24.0                                   # the fireplace on the front wall (world x)
def wall_cards():
    """framed Mudwater cards all round the lounge walls (the user loves these)"""
    cards = iter([4, 7, 10, 13, 15, 18, 20, 23, 8, 9, 19, 22, 34, 41, 49, 59, 61, 67, 76, 82, 85, 90, 100, 106, 118, 120, 21, 1, 3, 11, 16, 25, 30, 38, 46, 52, 57, 69, 73, 79, 94, 102, 110, 115, 2, 6, 12, 17, 24, 29, 33, 36, 40, 45])
    yc = Y + 3.0
    # (v23) on the plain wall sections between the big windows (from the building's bay plan)
    blank = [(sd, x, z) for (sd, x, z, kind) in LY.get('lounge_bays', []) if kind in ('', 'brace')]
    for (sd, x, z) in blank:
        if sd == 'front' and abs(x) > 8 and abs(x - FIRE_X) > 4.0: hang_card(next(cards), M(T(x, yc, Z1), Ry(180)))
        if sd == 'back' and abs(x) > 8 and abs(abs(x) - 13.5) > 3.6: hang_card(next(cards), M(T(x, yc, -Z1), Ry(0)))
    for z in [-14.0, 24.0, 36.0]:                                                           # the end walls, clear of the lifts and doors
        hang_card(next(cards), M(T(-X1, yc, z), Ry(90)))
        hang_card(next(cards), M(T(X1, yc, z), Ry(-90)))
    for z in [-2.0, 4.0]:                                                                   # the stair-tower walls face the room too (not over the stair door)
        hang_card(next(cards), M(T(-LY['sw']['xi'] + 0.25, yc, z), Ry(90)))
        hang_card(next(cards), M(T(LY['sw']['xi'] - 0.25, yc, z), Ry(-90)))

def ceiling_hardware():
    # ship's ropes swagged between the ceiling beams
    for k in range(8):
        x = (-28 + k * 8.0) * KX; z = rng.uniform(-12, 12) * KZ
        pts = [(x + 2.6 * math.cos(t), LY['FL']['hall'] - 1.1 - 0.9 * math.sin(t) ** 2, z + 2.6 * math.sin(t)) for t in np.linspace(0, math.pi, 12)]
        tube(L1, 'rope', pts, 0.05, 6, twist=2)

def columns():
    """big mossy cypress columns holding up the gallery floor, each with a jar lantern and a framed card"""
    spots = [(sx * 10.6, z) for sx in (-1, 1) for z in (-15.0, 0.0, 15.0)] + [(-27.0, -24.0), (27.0, -24.0), (30.0, 12.0)]
    H = LY['FL']['hall'] - 0.45 - Y
    for (x, z) in spots:
        prof = [(0.55 + 0.25 * math.exp(-t * 7) + 0.03 * math.sin(t * 13 + x), H * t) for t in np.linspace(0, 1, 9)]
        lathe(L1, 'bark', prof, 14, m=T(x, Y, z), uv_v=3.0, uvs_u=2)
        lathe(L1, 'moss', [(0.85, 0.0), (0.7, 0.5), (0.58, 1.1)], 14, m=T(x, Y, z))
        bevel_box(L1, 'dark', 1.6, 0.35, 1.6, 0.04, m=T(x, Y + H - 0.17, z))           # capital
        for a in (0, 90, 180, 270):
            mm = M(T(x, Y, z), Ry(a))
            tube(L1, 'iron', [(0, 3.4, 0.6), (0, 3.4, 0.95), (0, 3.2, 0.95)], 0.02, 5, m=mm)
            lathe(L1, 'glow', [(0.0, 0), (0.1, 0.03), (0.12, 0.2), (0.09, 0.3), (0.0, 0.32)], 10, m=M(mm, T(0, 2.85, 0.95)))
            lathe(L1, 'brass', [(0.0, 0.3), (0.11, 0.33), (0.0, 0.38)], 8, m=M(mm, T(0, 2.85, 0.95)))
        collider_box(C1, 1.3, H, 1.3, T(x, Y + H / 2, z))


BAR_C = (0.0, 1.0); BAR_RO, BAR_RI = 5.6, 4.5           # the round centre bar: counter ring between these radii
def round_bar():
    """THE CENTREPIECE: a round island bar under a shingled timber pavilion. Bartender inside, taps all round, stools all round."""
    cx, cz = BAR_C; Yt = Y + 1.1
    C = lambda: T(cx, 0, cz)
    # counter: panelled front ring, glossy top with a rounded nose, brass foot rail, inner work shelf
    lathe(L1, 'dark', [(BAR_RO - 0.05, Y), (BAR_RO - 0.05, Y + 1.05)], 64, m=C(), uvs_u=24)
    for k in range(32):
        a = k * 360 / 32 + 5.6
        p = (cx + (BAR_RO - 0.02) * math.sin(math.radians(a)), cz + (BAR_RO - 0.02) * math.cos(math.radians(a)))
        bevel_box(L1, 'plank', 0.85, 0.62, 0.05, 0.02, m=M(T(p[0], Y + 0.55, p[1]), Ry(a)), uvs=1.5)
        bevel_box(L1, 'dark', 0.1, 1.05, 0.1, 0.02, m=M(T(cx + (BAR_RO) * math.sin(math.radians(a + 5.6)), Y + 0.52, cz + BAR_RO * math.cos(math.radians(a + 5.6))), Ry(a)))
    lathe(L1, 'bartop', [(BAR_RI - 0.1, Yt - 0.05), (BAR_RO + 0.12, Yt - 0.05), (BAR_RO + 0.2, Yt), (BAR_RO + 0.12, Yt + 0.06), (BAR_RI - 0.1, Yt + 0.06)], 64, m=C(), uvs_u=20)
    lathe(L1, 'dark', [(BAR_RI - 0.05, Y), (BAR_RI - 0.05, Yt - 0.05)], 64, m=C(), uvs_u=20)
    lathe(L1, 'brass', [(BAR_RO + 0.38, Y + 0.2), (BAR_RO + 0.42, Y + 0.2), (BAR_RO + 0.42, Y + 0.25), (BAR_RO + 0.38, Y + 0.25)], 64, m=C())
    for k in range(16):
        a = math.radians(k * 22.5); r0, r1 = BAR_RO, BAR_RO + 0.4
        tube(L1, 'brass', [(cx + r0 * math.sin(a), Y, cz + r0 * math.cos(a)), (cx + r1 * math.sin(a), Y + 0.22, cz + r1 * math.cos(a))], 0.02, 5)
    for k in range(36):     # counter collider ring (the bartender's opening is at the back, toward the lifts)
        a = k * 10 + 5
        if abs(((a - 180) + 180) % 360 - 180) < 8: continue
        collider_box(C1, 2 * math.pi * BAR_RO / 36 + 0.1, 1.15, BAR_RO - BAR_RI + 0.2, M(T(cx + (BAR_RO + BAR_RI) / 2 * math.sin(math.radians(a)), Y + 0.58, cz + (BAR_RO + BAR_RI) / 2 * math.cos(math.radians(a))), Ry(a)))
    # stools all round
    for k in range(26):
        a = math.radians(k * 360 / 26 + 7)
        stool(L1, T(cx + (BAR_RO + 0.85) * math.sin(a), Y, cz + (BAR_RO + 0.85) * math.cos(a)))
    # the back-bar tower: a round column of glowing bottle shelves, kegs at its foot
    lathe(L1, 'dark', [(1.5, Y), (1.5, Y + 0.95), (1.25, Y + 1.0), (1.25, Y + 4.6), (1.55, Y + 4.7), (1.55, Y + 4.95), (0.0, Y + 4.95)], 32, m=C(), uvs_u=8)
    for kk in range(4):
        yy = Y + 1.3 + kk * 0.82
        lathe(L1, 'plank', [(1.25, yy), (1.62, yy), (1.62, yy + 0.05), (1.25, yy + 0.05)], 32, m=C())
        if 'bottles' in META:            # (v24, owner) Meshy rows of real-looking liquor bottles all round each shelf
            for j in range(8):
                a = j * 45 + kk * 11 + 22.5
                mp('bottles', M(T(cx + 1.47 * math.sin(math.radians(a)), yy + 0.05, cz + 1.47 * math.cos(math.radians(a))), Ry(a)), ('w', 1.08))
        else:
            n = 34
            for j in range(n):
                a = math.radians(j * 360 / n + kk * 4)
                bottle(L1, T(cx + 1.45 * math.sin(a), yy + 0.05, cz + 1.45 * math.cos(a)), rng.choice('gaac'))
    for k in range(5):
        a = math.radians(30 + k * 72)
        barrel(L1, M(T(cx + 2.3 * math.sin(a), Y + 0.45, cz + 2.3 * math.cos(a)), Ry(math.degrees(a)), Rz(90), T(0, -0.5, 0)), r=0.4, h=1.0)
    collider_box(C1, 2.8, 5.0, 2.8, T(cx, Y + 2.5, cz))
    # taps: eight brass beer engines round the inner edge, each facing out
    taps = []
    for k in range(8):
        a = k * 45 + 22.5
        p = (cx + (BAR_RI + 0.15) * math.sin(math.radians(a)), cz + (BAR_RI + 0.15) * math.cos(math.radians(a)))
        mm = M(T(p[0], Y, p[1]), Ry(a))
        cyl(L1, 'brass', 0.04, 0.45, 8, m=M(mm, T(0, 1.1, 0)))
        cyl(L1, 'brass', 0.03, 0.24, 8, m=M(mm, T(0, 1.5, 0), Rx(90)))
        bevel_box(L1, 'iron', 0.45, 0.04, 0.32, 0.01, m=M(mm, T(0, 1.13, 0.22)))
        taps.append([round(p[0], 3), round(Y + 1.5, 3), round(p[1], 3), round(a, 1)])
    # the pavilion: eight carved posts on the counter's outer edge, a shingled octagonal roof, a glass rack and lanterns
    PR = BAR_RO + 0.3; ph = 5.4
    for k in range(8):
        a = math.radians(k * 45)
        x, z = cx + PR * math.sin(a), cz + PR * math.cos(a)
        prof = [(0.22 + 0.06 * math.exp(-t * 7), ph * t) for t in np.linspace(0, 1, 7)]
        lathe(L1, 'bark', prof, 10, m=T(x, Y, z), uv_v=2.5)
        collider_box(C1, 0.5, ph, 0.5, T(x, Y + ph / 2, z))
    ring = [(cx + (PR + 0.2) * math.sin(math.radians(k * 45 + 22.5)) / math.cos(math.radians(22.5)), cz + (PR + 0.2) * math.cos(math.radians(k * 45 + 22.5)) / math.cos(math.radians(22.5))) for k in range(8)]
    for k in range(8):
        a, b = ring[k], ring[(k + 1) % 8]
        mm, ln = place(a, b, Y + ph)
        bevel_box(L1, 'dark', ln, 0.5, 0.3, 0.03, m=M(mm, T(ln / 2, 0.0, 0)), uvs=2.0)
        quad(L1, 'gold', ln * 0.7, 0.12, M(mm, T(ln / 2, 0.0, 0.16), Ry(180)))
        P = np.array([[a[0], Y + ph + 0.25, a[1]], [b[0], Y + ph + 0.25, b[1]], [cx, Y + ph + 1.45, cz]])
        nrm = np.cross(P[1] - P[0], P[2] - P[0]); nrm /= np.linalg.norm(nrm)
        idx = [0, 1, 2] if nrm[1] > 0 else [0, 2, 1]
        L1.add('shingle', P, [nrm if nrm[1] > 0 else -nrm] * 3, [[0, 0], [ln / 3, 0], [ln / 6, 2.4 / 3]], idx)
        L1.add('dark', P - np.array([0, 0.08, 0]), [-nrm if nrm[1] > 0 else nrm] * 3, [[0, 0], [1, 0], [0.5, 1]], idx[::-1])
    for k in range(4):        # a big glowing MUDWATER sign on all four faces of the pavilion (framed, gold trim, marquee bulbs)
        a = k * 90
        mm = M(T(cx + (PR + 0.62) * math.sin(math.radians(a)), Y + ph - 0.08, cz + (PR + 0.62) * math.cos(math.radians(a))), Ry(a))
        bar_sign(mm)
    lathe(L1, 'dark', [(3.2, Y + 3.15), (3.6, Y + 3.15), (3.6, Y + 3.3), (3.2, Y + 3.3)], 48, m=C())
    if 'glassrack' in META:              # (v24, owner) Meshy racks of hanging wine glasses all round under the canopy ring
        gm, gx_ = META['glassrack']; gw = 2.1; gh = (gx_[1] - gm[1]) * gw / (gx_[0] - gm[0])
        for k in range(9):
            a = k * 40 + 20
            mp('glassrack', M(T(cx + 3.4 * math.sin(math.radians(a)), Y + 3.15 - gh, cz + 3.4 * math.cos(math.radians(a))), Ry(a + 90)), ('w', gw))
    else:
        for k in range(40):
            a = math.radians(k * 9)
            lathe(L1, 'bottle_c', [(0.0, 0.0), (0.04, 0.0), (0.035, 0.08), (0.008, 0.1), (0.008, 0.2), (0.03, 0.22), (0.0, 0.22)], 8, m=M(T(cx + 3.4 * math.sin(a), Y + 3.13, cz + 3.4 * math.cos(a)), Rx(180)))
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        x, z = cx + (PR - 0.3) * math.sin(a), cz + (PR - 0.3) * math.cos(a)
        tube(L1, 'iron', [(x, Y + ph - 0.25, z), (x, Y + ph - 0.9, z)], 0.015, 4)
        lathe(L1, 'glow', [(0.0, 0), (0.13, 0.04), (0.16, 0.26), (0.11, 0.4), (0.0, 0.42)], 10, m=T(x, Y + ph - 1.35, z))
        lathe(L1, 'brass', [(0.0, 0.4), (0.15, 0.44), (0.0, 0.5)], 8, m=T(x, Y + ph - 1.35, z))
    return dict(taps=taps, bar=[cx, cz, BAR_RO + 0.05, BAR_RI + 0.25])

def garden():
    """the BAYOU GARDEN (west wing): a glowing pond behind a mossy stone curb, a little arched footbridge, benches round it"""
    cx, cz = -25.0, 4.0
    blob = [(cx + (7.5 + 1.1 * math.sin(3 * t) + 0.7 * math.cos(5 * t)) * math.cos(t), cz + (6.0 + 0.9 * math.sin(2 * t + 1)) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
    P = np.array([[x, Y + 0.12, z] for x, z in blob] + [[cx, Y + 0.12, cz]])
    n = len(blob); I = []
    for i in range(n): I += [n, i, (i + 1) % n]
    U = [[p[0] / 4, p[2] / 4] for p in P]
    f = np.cross(P[I[1]] - P[I[0]], P[I[2]] - P[I[0]])
    if f[1] < 0: I = list(np.array(I).reshape(-1, 3)[:, ::-1].reshape(-1))
    L1.add('pond', P, [[0, 1, 0]] * len(P), U, I)
    meshy_pond = mp('pond', T(cx, Y, cz), ('w', 17.0))
    for i in range(n):
        a, b = blob[i], blob[(i + 1) % n]
        d = np.array(b) - np.array(a); ln = np.linalg.norm(d)
        mm = M(T((a[0] + b[0]) / 2, Y + 0.22, (a[1] + b[1]) / 2), Ry(math.degrees(math.atan2(d[0], d[1])) + 90))
        if not meshy_pond:
            bevel_box(L1, 'mud', ln + 0.3, 0.45, 0.6, 0.08, m=mm, uvs=1.5)
            if i % 2 == 0: lathe(L1, 'moss', [(0.35, 0.0), (0.25, 0.18), (0.0, 0.25)], 8, m=T(a[0], Y + 0.42, a[1]))
        collider_box(C1, ln + 0.3, 0.8, 0.6, mm)
    # an arched footbridge across the middle (walkable)
    z0, z1 = cz - 7.4, cz + 7.4; w = 1.8; n = 16
    for k in (range(n) if not meshy_pond else []):
        t0, t1 = k / n, (k + 1) / n
        za, zb = z0 + (z1 - z0) * t0, z0 + (z1 - z0) * t1
        ya, yb = Y + 0.15 + 0.9 * math.sin(math.pi * t0), Y + 0.15 + 0.9 * math.sin(math.pi * t1)
        mm = M(T(cx, (ya + yb) / 2, (za + zb) / 2), Rx(-math.degrees(math.atan2(yb - ya, zb - za))))
        bevel_box(L1, 'plank', w, 0.1, math.hypot(zb - za, yb - ya) + 0.02, 0.015, m=mm, col=tint(rng, 0.1), uvs=2.0)
        collider_box(C1, w, 0.25, math.hypot(zb - za, yb - ya) + 0.05, M(mm, T(0, -0.08, 0)))
    for sx in ((-1, 1) if not meshy_pond else ()):
        pts = [(cx + sx * w / 2, Y + 1.1 + 0.9 * math.sin(math.pi * t), z0 + (z1 - z0) * t) for t in np.linspace(0, 1, 12)]
        tube(L1, 'pale', pts, 0.05, 6)
        for p in pts[::2]: box(L1, 'dark', 0.08, 1.0, 0.08, m=T(p[0], p[1] - 0.5, p[2]))
        collider_box(C1, 0.15, 2.2, z1 - z0, T(cx + sx * (w / 2 + 0.05), Y + 1.0, cz))
    # benches round the pond
    for (bx, bz, ry) in ((cx - 10.0, cz, 90), (cx + 9.6, cz - 3.0, -90), (cx - 4.0, cz - 9.0, 0), (cx + 3.0, cz + 8.6, 180)):
        mm = M(T(bx, Y, bz), Ry(ry))
        if mp('bench', mm, ('w', 2.4)): collider_box(C1, 2.4, 0.9, 0.6, M(mm, T(0, 0.45, 0))); continue
        bevel_box(L1, 'plank', 2.4, 0.1, 0.5, 0.02, m=M(mm, T(0, 0.48, 0)), col=tint(rng, 0.15))
        bevel_box(L1, 'plank', 2.4, 0.5, 0.08, 0.02, m=M(mm, T(0, 0.8, -0.24)), col=tint(rng, 0.15))
        for sx in (-1, 1): bevel_box(L1, 'iron', 0.08, 0.48, 0.45, 0.01, m=M(mm, T(sx * 1.05, 0.24, 0)))
        collider_box(C1, 2.4, 0.9, 0.6, M(mm, T(0, 0.45, 0)))
    return dict(pond=[cx, cz])

def bar_sign(mm, W=6.2, Hh=1.5):
    """one MUDWATER sign board, origin at the bottom centre, facing +z"""
    bevel_box(L1, 'dark', W, Hh, 0.14, 0.03, m=M(mm, T(0, Hh / 2, 0)), uvs=2.0)
    for (sx, sy, tx, ty) in [(W + 0.12, 0.1, 0, Hh), (W + 0.12, 0.1, 0, 0), (0.1, Hh, -W / 2, Hh / 2), (0.1, Hh, W / 2, Hh / 2)]:
        bevel_box(L1, 'gold', sx, sy, 0.18, 0.02, m=M(mm, T(tx, ty, 0.02)))
    lw = W * 0.86
    quad(L1, 'logo_hot', lw, lw * 323 / 1334, M(mm, T(0, Hh / 2, 0.085)))
    n = 20
    for i in range(n):
        x = -W / 2 + 0.22 + (W - 0.44) * i / (n - 1)
        for y in (0.13, Hh - 0.13): sphere(L1, 'glow', 0.045, 6, 4, m=M(mm, T(x, y, 0.1)))
    for sx in (-1, 1): lathe(L1, 'gold', [(0.0, 0.0), (0.07, 0.03), (0.04, 0.1), (0.0, 0.22)], 8, m=M(mm, T(sx * W / 2, Hh + 0.04, 0.02)))

def stage():
    """a raised stage in the back-east corner with a glowing dance floor in front of it"""
    x0, x1, z0, z1 = -7.3, 7.3, -29.4 - DZ, -18.0 - DZ; h = 0.7    # back centre, against the back wall
    bevel_box(L1, 'dark', x1 - x0, h, z1 - z0, 0.05, m=T((x0 + x1) / 2, Y + h / 2, (z0 + z1) / 2), uvs=3.0)
    flat_deck(L1, 'bartop', [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], Y + h + 0.005, under=None)
    collider_box(C1, x1 - x0, h, z1 - z0, T((x0 + x1) / 2, Y + h / 2, (z0 + z1) / 2))
    for k in range(4):          # steps down the front
        bevel_box(L1, 'plank', 6.0, h * (k + 1) / 4, 0.4, 0.02, m=T((x0 + x1) / 2, Y + h * (k + 1) / 8, z1 + 1.6 - k * 0.4))
    collider_box(C1, 6.0, 0.3, 1.8, M(T((x0 + x1) / 2, Y + h / 2 - 0.1, z1 + 0.9), Rx(math.degrees(math.atan2(h, 1.6)))))
    # proscenium: two bark posts, a carved header, red velvet swags, footlights
    for x in (x0 + 0.3, x1 - 0.3):
        lathe(L1, 'bark', [(0.32, 0), (0.28, 5.2), (0.0, 5.3)], 10, m=T(x, Y + h, z1 - 0.3), uv_v=2.5)
    bevel_box(L1, 'dark', x1 - x0, 0.7, 0.4, 0.04, m=T((x0 + x1) / 2, Y + h + 5.3, z1 - 0.3), uvs=3.0)
    for k in range(6):
        xa = x0 + (x1 - x0) * k / 6; xb = x0 + (x1 - x0) * (k + 1) / 6
        pts = [(xa + (xb - xa) * u, Y + h + 5.0 - 0.8 * math.sin(math.pi * u), z1 - 0.1) for u in np.linspace(0, 1, 8)]
        tube(L1, 'velvet', pts, 0.18, 6)
    for k in range(10): sphere(L1, 'glow', 0.09, 8, 5, m=T(x0 + 0.8 + k * (x1 - x0 - 1.6) / 9, Y + h + 0.08, z1 - 0.2))
    # the dance floor: glowing mud tiles and gold
    fx0, fx1, fz0, fz1 = -7.0, 7.0, -16.6 - DZ, -8.6 - DZ; n = 7
    for i in range(n):
        for j in range(5):
            xa = fx0 + (fx1 - fx0) * i / n; za = fz0 + (fz1 - fz0) * j / 5
            mat = 'dance' if (i + j) % 2 == 0 else 'bartop'
            quad(L1, mat, (fx1 - fx0) / n - 0.06, (fz1 - fz0) / 5 - 0.06, M(T(xa + (fx1 - fx0) / n / 2, Y + 0.09, za + (fz1 - fz0) / 10), Rx(-90)))
    return dict(stage=[(x0 + x1) / 2, Y + h, (z0 + z1) / 2])

def ceiling_lights():
    """warm string lights criss-crossing under the whole lounge ceiling"""
    yc = LY['FL']['hall'] - 0.62
    ends = []
    for k in range(9):
        x = (-33.0 + k * 8.25) * KX
        ends.append(((x, -27.5 * KZ), (-x * 0.6, 27.5 * KZ)))
    for k in range(6):
        z = (-24.0 + k * 9.6) * KZ
        ends.append(((-33.0 * KX, z), (33.0 * KX, -z * 0.5)))
    for (a, b) in ends:
        a = np.array(a); b = np.array(b); ln = np.linalg.norm(b - a); n = int(ln / 6)
        for s_ in range(n):
            p0 = a + (b - a) * s_ / n; p1 = a + (b - a) * (s_ + 1) / n
            pts = [(p0[0] + (p1[0] - p0[0]) * u, yc - 0.7 * math.sin(math.pi * u), p0[1] + (p1[1] - p0[1]) * u) for u in np.linspace(0, 1, 8)]
            tube(L1, 'dark', pts, 0.012, 3)
            for p in pts[1:-1]: sphere(L1, 'glow', 0.07, 5, 3, m=T(p[0], p[1] - 0.08, p[2]))

def swamp_moss():
    """swamp inside: moss beards hanging from every ceiling beam, vines winding up the columns"""
    yb = LY['FL']['hall'] - 1.0
    for i in []:          # (the thick moss cones were removed - the trusses carry thin trailing moss now)
        x = -42.5 + 85.0 * i / 16
        if abs(x) > 34.0: continue
        for z in np.arange(-28.5, 28.5, 1.6):
            if rng.random() < 0.45: continue
            if math.hypot(x - BAR_C[0], z - BAR_C[1]) < 7.5: continue          # keep the bar canopy clear
            hh = rng.uniform(0.6, 2.4); zz = z + rng.uniform(-0.5, 0.5)
            tube(L1, 'moss', [(x, yb, zz), (x + rng.uniform(-0.15, 0.15), yb - hh / 2, zz + rng.uniform(-0.15, 0.15)), (x, yb - hh, zz)], 0.08, 4, radii=[0.17, 0.09, 0.02])
    spots = []
    H = LY['FL']['hall'] - 0.45 - Y
    for (x, z) in spots:
        for ph in (0.0, math.pi):
            vine = [(x + 0.72 * math.cos(u * 11 + ph), Y + H * u, z + 0.72 * math.sin(u * 11 + ph)) for u in np.linspace(0.02, 0.97, 30)]
            tube(L1, 'moss', vine, 0.06, 4)
            for k in range(4):
                p = vine[5 + k * 6]; lathe(L1, 'moss', [(0.0, 0.0), (0.16, 0.05), (0.0, 0.12)], 6, m=T(p[0], p[1], p[2]))


TREES = [(-10.6, -15.0), (-10.6, 15.0), (10.6, -15.0), (10.6, 15.0), (-24.0, -21.0), (25.0, -2.0), (-30.0, 21.0),
         (-44.0, 14.0), (42.0, 30.0), (-30.0, 36.0), (44.0, -8.0), (32.0, -27.0), (-46.0, -30.0)]     # v24: more great trees in the new space
MESHY_TREES = True     # high-detail Meshy trunks (sp_mtree_1/2.glb, placed by build_html from f1_layout 'trees'); the code keeps the colliders + ceiling branches

def giant_trees():
    """great mossy swamp trees growing up through the lounge floor into the ceiling: flaring roots across the floor, moss, vines,
    glowing shelf mushrooms up the trunk, candles in the roots, branches spreading under the ceiling"""
    H = LY['FL']['hall'] - 0.45 - Y
    for ti, (x, z) in enumerate(TREES):
        r0 = 1.25 + 0.2 * (ti % 3)
        prof = [(r0 * (1.0 + 0.9 * math.exp(-t * 9)) * (1 + 0.06 * math.sin(t * 23 + ti)), H * t) for t in np.linspace(0, 1, 14)]
        if not MESHY_TREES: lathe(L1, 'bark', prof, 18, m=M(T(x, Y, z), Ry(ti * 37)), uv_v=4.0, uvs_u=3)
        collider_box(C1, r0 * 2.0, H, r0 * 2.0, T(x, Y + H / 2, z))
        if not MESHY_TREES:   # (the Meshy trunks bring their own roots, moss, vines and glowing mushrooms)
            # roots snaking out over the floor
            for k in range(7):
                a = math.radians(k * 360 / 7 + ti * 17); L_ = rng.uniform(3.0, 5.5)
                pts = []
                for u in np.linspace(0, 1, 9):
                    rr = r0 * 1.6 + L_ * u; wob = 0.4 * math.sin(u * 7 + k)
                    pts.append((x + rr * math.cos(a) + wob * math.sin(a), Y + 0.9 * (1 - u) ** 1.6 + 0.05, z + rr * math.sin(a) - wob * math.cos(a)))
                tube(L1, 'bark', pts, 0.35, 7, radii=list(np.linspace(0.42, 0.08, 9)))
                tube(L1, 'moss', [(p[0], p[1] + 0.25, p[2]) for p in pts[:5]], 0.14, 5, radii=list(np.linspace(0.18, 0.05, 5)))
            lathe(L1, 'moss', [(r0 * 2.3, Y + 0.02), (r0 * 1.9, Y + 0.25), (r0 * 1.5, Y + 0.6), (r0 * 1.3, Y + 1.1)], 18, m=T(x, 0, z))
            # moss sheets and vines climbing the trunk
            for ph in (0.0, 2.1, 4.2):
                vine = [(x + (r0 + 0.08) * math.cos(u * 8 + ph), Y + H * u, z + (r0 + 0.08) * math.sin(u * 8 + ph)) for u in np.linspace(0.05, 0.98, 32)]
                tube(L1, 'moss', vine, 0.07, 4)
            for k in range(10):
                a = rng.uniform(0, 2 * math.pi); yy = Y + rng.uniform(2.5, H - 0.4); hh = rng.uniform(0.8, 2.2)
                p = (x + (r0 + 0.12) * math.cos(a), z + (r0 + 0.12) * math.sin(a))
                tube(L1, 'moss', [(p[0], yy, p[1]), (p[0] + 0.1 * math.cos(a), yy - hh / 2, p[1] + 0.1 * math.sin(a)), (p[0], yy - hh, p[1])], 0.08, 4, radii=[0.16, 0.09, 0.02])
            # glowing shelf mushrooms in clusters up the trunk
            for c in range(3):
                a = rng.uniform(0, 2 * math.pi); yb = Y + 1.6 + c * 1.5 + rng.uniform(-0.3, 0.3)
                for k in range(rng.randint(2, 4)):
                    sz = rng.uniform(0.45, 0.85); yy = yb + k * 0.42; aa = a + rng.uniform(-0.3, 0.3)
                    px, pz = x + (r0 + sz * 0.6) * math.cos(aa), z + (r0 + sz * 0.6) * math.sin(aa)
                    mm = M(T(px, yy, pz), Ry(-math.degrees(aa) + 90))
                    lathe(L1, 'shroom', [(0.0, 0.12), (sz * 0.6, 0.1), (sz, 0.02), (sz * 0.95, -0.02), (0.0, 0.0)], 14, m=M(mm, S(1, 1, 0.75)))
                    lathe(L1, 'gills', [(0.0, -0.01), (sz * 0.9, -0.025)], 14, m=M(mm, S(1, 1, 0.75)))
        # branches spreading under the ceiling (code trees only; the Meshy trunks don't need them)
        for k in (range(5) if not MESHY_TREES else []):
            a = math.radians(k * 72 + ti * 23); L_ = rng.uniform(4, 7)
            pts = [(x + (r0 * 0.8 + L_ * u) * math.cos(a), Y + H - 1.6 + 1.3 * math.sin(u * 2.2), z + (r0 * 0.8 + L_ * u) * math.sin(a)) for u in np.linspace(0, 1, 8)]
            tube(L1, 'bark', pts, 0.3, 6, radii=list(np.linspace(0.45, 0.1, 8)))
            for p in pts[2::2]:
                hh = rng.uniform(0.6, 1.6)
                tube(L1, 'moss', [(p[0], p[1] - 0.2, p[2]), (p[0], p[1] - 0.2 - hh, p[2])], 0.08, 4, radii=[0.15, 0.02])
        # candles in the roots
        for k in range(rng.randint(4, 7)):
            a = rng.uniform(0, 2 * math.pi); rr = r0 * rng.uniform(1.8, 2.6)
            px, pz = x + rr * math.cos(a), z + rr * math.sin(a); hh = rng.uniform(0.15, 0.45)
            cyl(L1, 'label', 0.045, hh, 8, m=T(px, Y, pz))
            lathe(L1, 'glow', [(0.0, 0.0), (0.03, 0.03), (0.02, 0.09), (0.0, 0.12)], 6, m=T(px, Y + hh, pz))

# ---- where the lanterns hang (build_html places them from f1_layout.json), and the warm light pools they throw on the wet floor
RINGS = [[0, 24.0, 1.0], [0, -14.5, 1.0], [17, 18, 0.8], [27, 6, 0.75], [-20, -13, 0.8], [17, -10, 0.8], [-19, 22, 0.8], [31, -14, 0.75], [-33, 15, 0.75], [-30, -2, 0.75],
         [0, 36.0, 1.0], [-40, 6, 0.85], [40, 18, 0.85], [-38, -14, 0.8], [38, -24, 0.8], [-16, 36, 0.8], [26, 34, 0.75], [0, -27.0 - DZ * 0.2, 0.9]]
HOOK_Y = LY['FL']['hall'] - 0.5
def place_lanterns():
    lr = random.Random(5413); out = []
    def ok(x, z):
        if math.hypot(x - BAR_C[0], z - BAR_C[1]) < 8.0: return False
        if any(math.hypot(x - tx, z - tz) < 3.6 for tx, tz in TREES): return False
        if any(math.hypot(x - c[0], z - c[1]) < 3.6 * c[2] for c in RINGS): return False
        if z < -21.5 - DZ or (abs(x) < 9 and z < -16 - DZ): return False
        return all(math.hypot(x - s[1], z - s[3]) > 2.2 for s in out)
    garden = [(-30, 1), (-21, 6), (-25, 10), (-27, -3), (22, 19.5 + DZ), (22, 8 + DZ), (12, -10), (19, -17)]
    for (x, z) in garden:
        if ok(x, z): out.append(['sp_lantern_' + 'abc'[lr.randint(0, 2)], x, HOOK_Y, z, round(lr.uniform(0, 60), 1), 1.0])
    for _ in range(5000):
        if len(out) >= 100: break
        x, z = lr.uniform(-(X1N - 9), X1N - 9), lr.uniform(-(Z1N - 9), Z1N - 3)
        if ok(x, z): out.append(['sp_lantern_' + 'abc'[lr.randint(0, 2)], round(x, 2), HOOK_Y, round(z, 2), round(lr.uniform(0, 60), 1), 1.0])
    return out

def light_pools(lanterns):
    """soft, irregular pools of warm light under every lantern, ring, the bar, the fireplace and the booths (MML has no real lights)"""
    def pool(x, z, r, a, rot):
        quad(L1, 'pool', 2 * r, 2 * r, M(T(x, Y + 0.065, z), Ry(rot), Rx(-90)), col=(1, 1, 1, a))      # above the puddles, under the dance floor
    for f, x, y, z, ry, s in lanterns:
        k = 'abc'.index(f[-1]); pool(x, z, (1.5, 1.8, 2.1)[k], (0.32, 0.42, 0.55)[k], ry * 6)
    for x, z, s in RINGS: pool(x, z, 4.3 * s, 0.6, x * 7 + z)
    for k in range(6):          # the round bar glows all round
        a = k * 60 + 30; pool(BAR_C[0] + 7.4 * math.sin(math.radians(a)), BAR_C[1] + 7.4 * math.cos(math.radians(a)), 3.2, 0.42, a)
    pool(24.0, 25.6 + DZ, 3.6, 0.7, 20)                                  # the fireplace
    for x in BOOTH_X: pool(x, -22.2 - DZ, 2.8, 0.5, x)                   # the shop booths

def wet_floor():
    """photo-detailed muddy puddles and boot-printed mud splats (Meshy-made decals) scattered over the wet planks,
    and grass tufts poking up through the boards"""
    kinds = ['dec_puddle1', 'dec_puddle2', 'dec_puddle1', 'dec_puddle3']        # shallow glossy water (owner: like the concept's puddles)
    placed = []
    for k in range(110):
        for _ in range(40):
            x, z = rng.uniform(-(X1N - 9), X1N - 9), rng.uniform(-(Z1N - 3), Z1N - 3)
            if math.hypot(x - BAR_C[0], z - BAR_C[1]) < 7.5 or abs(x + 25) + abs(z - 4) < 13 or (abs(x) < 8 and z < -8 - DZ): continue
            if abs(x) < 6 and abs(z - 19.5) < 2.2: continue                      # keep the MUDWATER plaque clear
            if all(math.hypot(x - px, z - pz) > 2.6 for px, pz in placed): break
        placed.append((x, z))
        kd = kinds[k % 4]; sz = rng.uniform(2.0, 4.2)
        quad(L1, kd, sz, sz * rng.uniform(0.75, 1.0), M(T(x, Y + 0.022 + 0.005 * (k % 7), z), Ry(rng.uniform(0, 360)), Rx(-90)))   # 5 mm apart: no flicker
    for (tx, tz) in TREES + [(rng.uniform(-(X1N - 9), X1N - 9), rng.uniform(-(Z1N - 3), Z1N - 3)) for _ in range(50)]:
        for k in range(rng.randint(6, 14)):
            a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(2.6, 4.5) if (tx, tz) in TREES else rng.uniform(0, 1.2)
            px, pz = tx + rr * math.cos(a), tz + rr * math.sin(a)
            for b in range(4):
                h = rng.uniform(0.25, 0.6); ang = rng.uniform(0, 2 * math.pi)
                tube(L1, 'moss', [(px, Y, pz), (px + 0.08 * math.cos(ang), Y + h * 0.6, pz + 0.08 * math.sin(ang)), (px + 0.18 * math.cos(ang), Y + h, pz + 0.18 * math.sin(ang))], 0.015, 3, radii=[0.025, 0.012, 0.002])

def banners():
    """tall green Mudwater banners hung from the ceiling on iron rods"""
    yt = LY['FL']['hall'] - 0.7
    spots = [(-17.0, -6.0, 90), (17.0, -6.0, -90), (-17.0, 8.0, 90), (17.0, 8.0, -90), (-5.0, 18.0, 0), (5.0, 18.0, 0), (-30.0, -8.0, 90), (30.0, 5.0, -90),
             (-40.0, 22.0, 90), (40.0, -14.0, -90), (-40.0, -24.0, 90), (40.0, 24.0, -90), (-8.0, 38.0, 0), (8.0, 38.0, 0)]
    for (x, z, ry) in spots:
        mm = M(T(x, yt, z), Ry(ry))
        w, h = 1.6, 4.0
        P = np.array([[-w / 2, 0, 0], [w / 2, 0, 0], [w / 2, -h, 0], [0, -h - 0.6, 0], [-w / 2, -h, 0]])
        U = [[0, 0], [1, 0], [1, h / (h + 0.6)], [0.5, 1], [0, h / (h + 0.6)]]
        for side, nz in ((0, 1), (1, -1)):
            I = [0, 4, 1, 1, 4, 2, 2, 4, 3] if side == 0 else [0, 1, 4, 1, 2, 4, 2, 3, 4]
            L1.add('banner', np.c_[P[:, 0], P[:, 1], P[:, 2] + nz * 0.01], [[0, 0, nz]] * 5, U, I, None, mm)
        cyl(L1, 'iron', 0.04, w + 0.4, 8, m=M(mm, T(-(w + 0.4) / 2, 0.05, 0), Rz(-90)))
        for sx in (-1, 1):
            lathe(L1, 'gold', [(0.0, 0), (0.07, 0.04), (0.0, 0.1)], 8, m=M(mm, T(sx * (w / 2 + 0.2), 0.05, 0), Rz(90)))
            tube(L1, 'iron', [(x, yt + 0.05, z), (x, LY['FL']['hall'] - 0.45, z)], 0.01, 3)

def trusses():
    """squared timber trusses across the lounge ceiling, as in the owner's concept: a gently arched rib of hewn beams,
    a straight top beam tight under the ceiling, upright posts between them with iron straps, a little moss trailing down"""
    yc = LY['FL']['hall'] - 0.45; tr = random.Random(4)
    def beam(a, b, w, h):
        a = np.array(a, float); b = np.array(b, float); d = b - a
        bevel_box(L1, 'dark', w, h, np.linalg.norm(d) + 0.04, 0.03, m=M(T(*((a + b) / 2)), look_basis(d)), uvs=2.0)
    SPAN = LY['sw']['xi'] - 0.5                                   # wall to wall between the stair towers
    for z in np.linspace(-(Z1N - 5.5), Z1N - 5.5, 12):
        xs = np.linspace(-SPAN, SPAN, 25)
        arch = [(x, yc - 0.4 - 1.5 * (1 - (x / (SPAN + 0.5)) ** 2) ** 0.6, z) for x in xs]
        for a, b in zip(arch[:-1], arch[1:]): beam(a, b, 0.32, 0.46)
        beam((-SPAN, yc - 0.18, z), (SPAN, yc - 0.18, z), 0.3, 0.32)
        for k in range(1, 24, 2):
            x, yy, _ = arch[k]
            bevel_box(L1, 'dark', 0.24, yc - 0.34 - yy, 0.24, 0.025, m=T(x, (yc - 0.34 + yy) / 2, z), uvs=2.0)
            box(L1, 'iron', 0.36, 0.06, 0.36, m=T(x, yy + 0.05, z))
        for k in range(10):
            p = arch[tr.randint(2, 22)]; hh = tr.uniform(0.5, 1.4)
            tube(L1, 'moss', [(p[0], p[1] - 0.25, p[2]), (p[0] + 0.06, p[1] - 0.25 - hh / 2, p[2] + 0.04), (p[0], p[1] - 0.25 - hh, p[2])], 0.05, 4, radii=[0.08, 0.05, 0.01])

def waterfalls():
    """two indoor waterfalls in the back wall either side of the stage: a mossy rock face, the falling sheet (animated by the game), a pool"""
    out = []
    for sx in (-1, 1):
        x = sx * 13.5; z = -29.0 - DZ; w = 3.0 if 'grotto' in META else 4.2; top = LY['FL']['hall'] - 1.2
        meshy_g = mp('grotto', T(x, Y, z + 0.3), ('h', top - Y + 0.6))
        for k in (range(9) if not meshy_g else []):                    # rough stacked rocks framing the fall
            for side in (-1, 1):
                rw = rng.uniform(1.0, 1.7)
                bevel_box(L1, 'mud', rw, rng.uniform(0.7, 1.2), 1.4, 0.15, m=M(T(x + side * (w / 2 + rw / 2 - 0.2), Y + 0.5 + k * 0.78, z + rng.uniform(-0.2, 0.2)), Ry(rng.uniform(-10, 10))), uvs=1.5)
        if not meshy_g: bevel_box(L1, 'mud', w + 2.8, 1.0, 1.8, 0.2, m=T(x, top + 0.2, z + 0.1), uvs=1.5)            # the lip
        for k in (range(6) if not meshy_g else []): lathe(L1, 'moss', [(0.5, 0.0), (0.35, 0.3), (0.0, 0.42)], 8, m=T(x + rng.uniform(-w / 2 - 1, w / 2 + 1), top + 0.7, z + rng.uniform(-0.3, 0.6)))
        quad(L1, 'black', w, top - Y, M(T(x, (Y + top) / 2, z - 0.35)))                             # the dark rock behind the water
        # the pool
        if not (meshy_g and mp('pond', M(T(x, Y, z + 1.7), Ry(90 * sx)), ('l', 6.4))):      # a mossy rock basin (the pond rim, small)
            lathe(L1, 'mud', [(2.6, Y), (2.9, Y + 0.45), (2.6, Y + 0.6), (2.3, Y + 0.5)], 24, m=M(T(x, 0, z + 1.6), S(1.2, 1, 0.8)))
        lathe(L1, 'pond', [(0.0, Y + 0.38), (2.45, Y + 0.38)], 24, m=M(T(x, 0, z + 1.6), S(1.2, 1, 0.8)))
        collider_box(C1, 6.6, 0.7, 4.4, T(x, Y + 0.35, z + 1.6))
        collider_box(C1, w + 3.4, top - Y + 1, 1.6, T(x, (Y + top) / 2, z))
        out.append([x, Y + 0.38, z + 0.25, w, top + 0.25])
    return dict(falls=out)

BOOTH_X = (-40.0, -28.0, 28.0, 40.0)
def booths():
    """shop booths with striped awnings and lit counters along the front and back walls"""
    out = []
    for (x, z, ry, key) in ((BOOTH_X[0], -26.6 - DZ, 0, 'cardshop'), (BOOTH_X[1], -26.6 - DZ, 0, 'merch'), (BOOTH_X[2], -26.6 - DZ, 0, 'trophies'), (BOOTH_X[3], -26.6 - DZ, 0, 'photos')):
        mm = M(T(x, Y, z), Ry(ry)); w = 6.6
        if mp('booth', M(mm, T(0, 0, 1.0)), ('w', w)):
            collider_box(C1, w, 1.2, 1.1, M(mm, T(0, 0.6, 1.2))); out.append([x, Y + 4.3, z + 1.95, ry, key]); continue
        bevel_box(L1, 'dark', w, 1.1, 1.0, 0.04, m=M(mm, T(0, 0.55, 1.2)), uvs=2.0)
        bevel_box(L1, 'bartop', w + 0.2, 0.08, 1.2, 0.02, m=M(mm, T(0, 1.14, 1.2)))
        for sx in (-1, 1): bevel_box(L1, 'dark', 0.25, 3.6, 0.25, 0.03, m=M(mm, T(sx * w / 2, 1.8, 1.65)))
        for k in range(8):       # striped awning (green and gold), sloping out
            a = -w / 2 + w * k / 8
            P = np.array([[a, 3.6, 0.0], [a + w / 8, 3.6, 0.0], [a + w / 8, 3.0, 2.1], [a, 3.0, 2.1]])
            n_ = np.cross(P[1] - P[0], P[3] - P[0]); idx = [0, 1, 2, 0, 2, 3] if n_[1] > 0 else [0, 2, 1, 0, 3, 2]
            L1.add('velvett' if k % 2 else 'gold', P, [[0, 1, 0]] * 4, [[0, 0], [1, 0], [1, 1], [0, 1]], idx, None, mm)
        for k in range(5): lathe(L1, 'glow', [(0.0, 0), (0.1, 0.03), (0.12, 0.2), (0.0, 0.25)], 8, m=M(mm, T(-w / 2 + 0.7 + k * (w - 1.4) / 4, 2.6, 1.6)))
        quad(L1, 'window', w - 0.8, 1.6, M(mm, T(0, 2.0, 0.26)))
        collider_box(C1, w, 1.2, 1.1, M(mm, T(0, 0.6, 1.2)))
        out.append([x, Y + 4.3, z + 1.95, ry, key])
    return dict(booths=out)

def chandelier():
    m = Mesh()
    # wagon wheel with eight jar lights, hung from a chain; origin at the top hook
    lathe(m, 'dark', [(1.35, -0.06), (1.5, -0.06), (1.5, 0.06), (1.35, 0.06)], 32, m=M(T(0, -3.0, 0), Rx(0)))
    lathe(m, 'iron', [(1.5, -0.03), (1.53, -0.03), (1.53, 0.03), (1.5, 0.03)], 32, m=T(0, -3.0, 0))
    lathe(m, 'dark', [(0.0, -0.12), (0.22, -0.12), (0.22, 0.12), (0.0, 0.12)], 12, m=T(0, -3.0, 0))
    for k in range(12):
        a = k * 30; d = np.array([math.sin(math.radians(a)), 0, math.cos(math.radians(a))])
        tube(m, 'dark', [np.array([0, -3.0, 0]) + d * 0.2, np.array([0, -3.0, 0]) + d * 1.4], 0.04, 6)
    for k in range(8):
        a = k * 45 + 22.5; p = np.array([1.42 * math.sin(math.radians(a)), -3.0, 1.42 * math.cos(math.radians(a))])
        tube(m, 'iron', [p, p - np.array([0, 0.25, 0])], 0.01, 4)
        lathe(m, 'glow', [(0.0, 0), (0.09, 0.02), (0.11, 0.15), (0.08, 0.24), (0.0, 0.26)], 10, m=T(*(p - np.array([0, 0.52, 0]))))
        lathe(m, 'brass', [(0.0, 0.24), (0.1, 0.26), (0.0, 0.3)], 8, m=T(*(p - np.array([0, 0.52, 0]))))
    for k in range(4):
        a = k * 90 + 45; p = np.array([1.42 * math.sin(math.radians(a)), -3.0, 1.42 * math.cos(math.radians(a))])
        tube(m, 'iron', [p, np.array([0, -0.6, 0])], 0.012, 4)
    tube(m, 'iron', [(0, -0.6, 0), (0, 0, 0)], 0.03, 6)
    return m

def iron_lantern(m, mm, chain=1.0):
    """a black-iron hexagonal lantern with warm amber glass, hook at the origin, hanging \'chain\' metres below it"""
    tube(m, 'iron', [(0, 0, 0), (0, -chain, 0)], 0.014, 4, m=mm)
    y0 = -chain
    lathe(m, 'iron', [(0.0, y0 + 0.01), (0.04, y0), (0.04, y0 - 0.06), (0.0, y0 - 0.07)], 6, m=mm, smooth=False)
    lathe(m, 'iron', [(0.04, y0 - 0.06), (0.19, y0 - 0.2), (0.215, y0 - 0.23), (0.17, y0 - 0.245)], 6, m=mm, smooth=False)
    lathe(m, 'lglass', [(0.15, y0 - 0.245), (0.15, y0 - 0.565)], 6, m=mm, smooth=False)
    for k in range(6):
        a = math.radians(k * 60)
        p = (0.152 * math.cos(a), 0.152 * math.sin(a))
        tube(m, 'iron', [(p[0], y0 - 0.245, p[1]), (p[0], y0 - 0.565, p[1])], 0.013, 4, m=mm)
    lathe(m, 'iron', [(0.158, y0 - 0.395), (0.158, y0 - 0.415)], 6, m=mm, smooth=False)
    lathe(m, 'iron', [(0.17, y0 - 0.565), (0.19, y0 - 0.585), (0.16, y0 - 0.62), (0.06, y0 - 0.66), (0.0, y0 - 0.73)], 6, m=mm, smooth=False)

def lantern_single(chain):
    m = Mesh(); iron_lantern(m, T(0, 0, 0), chain); return m

def lantern_ring(R=3.0):
    """the concept's big round lantern ring: a timber hoop banded in iron, a smaller hoop under it, a ring of iron lanterns,
    a big lantern in the middle and moss trailing down. Origin = the ceiling hook."""
    m = Mesh(); rr = random.Random(7); yr = -2.0; R2 = R * 0.7; y2 = yr - 0.6
    lathe(m, 'dark', [(R - 0.15, yr - 0.13), (R + 0.15, yr - 0.13), (R + 0.15, yr + 0.13), (R - 0.15, yr + 0.13), (R - 0.15, yr - 0.13)], 48, uvs_u=12, smooth=False)
    for yy in (yr - 0.1, yr + 0.1):
        lathe(m, 'iron', [(R + 0.16, yy - 0.025), (R + 0.17, yy - 0.025), (R + 0.17, yy + 0.025), (R + 0.16, yy + 0.025)], 48)
    lathe(m, 'dark', [(R2 - 0.09, y2 - 0.08), (R2 + 0.09, y2 - 0.08), (R2 + 0.09, y2 + 0.08), (R2 - 0.09, y2 + 0.08), (R2 - 0.09, y2 - 0.08)], 40, uvs_u=8, smooth=False)
    for k in range(12):
        a = math.radians(k * 30 + 15)
        tube(m, 'iron', [(R * math.sin(a), yr - 0.1, R * math.cos(a)), (R2 * math.sin(a), y2, R2 * math.cos(a))], 0.025, 4)
    for k in range(4):
        a = math.radians(k * 90 + 45)
        tube(m, 'iron', [(0, 0, 0), (R * math.sin(a), yr + 0.13, R * math.cos(a))], 0.02, 4)
    for k in range(12):
        a = math.radians(k * 30)
        iron_lantern(m, T(R * math.sin(a), yr - 0.13, R * math.cos(a)), 0.22 + 0.12 * (k % 2))
    for k in range(6):
        a = math.radians(k * 60 + 30)
        iron_lantern(m, M(T(R2 * math.sin(a), y2 - 0.08, R2 * math.cos(a)), S(0.85)), 0.2)
    iron_lantern(m, M(T(0, -0.05, 0), S(1.7)), 1.55)
    for k in range(22):
        a = rr.uniform(0, 2 * math.pi); hh = rr.uniform(0.5, 1.5); x, z = R * math.sin(a), R * math.cos(a)
        tube(m, 'moss', [(x, yr - 0.1, z), (x + 0.06, yr - 0.1 - hh / 2, z), (x, yr - 0.1 - hh, z)], 0.05, 4, radii=[0.07, 0.045, 0.012])
    return m

def tap_handle():
    m = Mesh()   # pivot at the base of the handle; pulled forward by rotating about x
    lathe(m, 'brass', [(0.0, 0), (0.03, 0), (0.025, 0.05)], 8)
    lathe(m, 'dark', [(0.025, 0.05), (0.035, 0.12), (0.04, 0.26), (0.03, 0.32), (0.0, 0.34)], 10)
    lathe(m, 'gold', [(0.041, 0.18), (0.041, 0.22)], 10)
    return m

def pour():
    m = Mesh(); lathe(m, 'beer', [(0.012, 0), (0.014, -0.5)], 8); return m       # 0.5 m stream hanging down from y 0

def foam_head():
    m = Mesh(); lathe(m, 'foamw', [(0.0, 0.0), (0.07, 0.0), (0.072, 0.02), (0.05, 0.05), (0.0, 0.06)], 12); return m

def guestbook():
    m = Mesh()
    lathe(m, 'dark', [(0.32, 0), (0.12, 0.08), (0.08, 0.95), (0.14, 1.0)], 10)
    bevel_box(m, 'dark', 0.7, 0.06, 0.5, 0.015, m=M(T(0, 1.05, 0), Rx(-18)))
    bevel_box(m, 'label', 0.62, 0.04, 0.44, 0.01, m=M(T(0, 1.09, 0.01), Rx(-18)))
    box(m, 'velvet', 0.012, 0.05, 0.46, m=M(T(0, 1.1, 0.01), Rx(-18)))
    tube(m, 'gold', [(0.2, 1.14, 0.12), (0.32, 1.25, 0.05)], 0.008, 5)
    collider_box(m, 0.7, 1.1, 0.5, T(0, 0.55, 0))
    return m

if __name__ == '__main__':
    LOGO = '/home/claude/spire/tmp/ext/mw_logo_0.png'
    M_['logo'] = dict(tex=LOGO, emis_tex=LOGO, emis=(0.6, 0.5, 0.35), alpha='MASK', cutoff=0.4, double=True)
    M_['logo_hot'] = dict(tex=LOGO, emis_tex=LOGO, emis=(1.0, 0.78, 0.42), emis_strength=1.8, alpha='MASK', cutoff=0.4)   # the big bar signs
    M_['logo_floor'] = dict(tex=LOGO, emis_tex=LOGO, emis=(0.75, 0.55, 0.25), alpha='MASK', cutoff=0.4, rough=0.25, metal=0.4)
    floor_and_rugs(); bar = round_bar(); fire = fireplace(); lounge_seating(); card_tables(); jb = dict(jukebox=[0, 0, 0]); wall_cards()      # (v23) the old jukebox is gone - it did nothing; ceiling_hardware()
    gd = garden(); st = stage(); ceiling_lights(); swamp_moss(); giant_trees(); wet_floor(); banners(); trusses(); wf = waterfalls(); bt = booths()
    LANT = place_lanterns(); light_pools(LANT)
    print('lounge', write(OUT + 'sp_f1_lounge.glb', L1, M_))
    print('col', write(OUT + 'sp_f1_col.glb', C1, M_))
    for name, mesh in [('sp_lantern_ring', lantern_ring()), ('sp_lantern_a', lantern_single(0.6)), ('sp_lantern_b', lantern_single(1.4)), ('sp_lantern_c', lantern_single(2.4)),
                       ('sp_chandelier', chandelier()), ('sp_tap', tap_handle()), ('sp_pour', pour()), ('sp_foam', foam_head()), ('sp_guestbook', guestbook())]:
        print(name, write(OUT + name + '.glb', mesh, M_))
    if 'beermug' in META: print('mug (Meshy stein)', meshy_mug(OUT + 'sp_m_beermug.glb', OUT + 'sp_mug.glb', META['beermug'], 0.19))
    else: mm = Mesh(); mug(mm, T(0, 0, 0)); print('mug', write(OUT + 'sp_mug.glb', mm, M_))
    TREEM = [['sp_mtree_%d' % (1 + i % 2), x, round(Y + (0.946 if i % 2 == 0 else 0.951) * 4.0 - 0.08, 3), z, (i * 77) % 360, 4.0] for i, (x, z) in enumerate(TREES)] if MESHY_TREES else []
    json.dump(dict(bar, **fire, **jb, **gd, **st, **wf, **bt, lanterns=LANT, rings=RINGS, trees=TREEM, mprops=MPROPS), open('/home/claude/spire/out/f1_layout.json', 'w'))
