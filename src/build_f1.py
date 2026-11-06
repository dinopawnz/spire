"""MUDWATER SPIRE - floor 1: THE SUNKEN LOUNGE (interior furnishings).
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
Y = LY['porch'] + 0.005
A1 = LY['A1']; dA = A1 - 24.0                  # the tower got wider: things on the walls move out by dA
GROUPS = [(-4.0, 7.5), (15.0, 12.0)]           # sofa groups, clear of the two lift doors at x = +-11.6
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
M_['ember'] = dict(color=(1, 0.4, 0.1, 1), emis=(1.0, 0.35, 0.05), emis_strength=2.0)
L1 = Mesh(); C1 = Mesh()

def barrel(m, mm, r=0.42, h=1.1, lying=False, mat='dark'):
    prof = [(r * (1 + 0.12 * math.sin(math.pi * i / 10)), h * i / 10) for i in range(11)]
    lathe(m, mat, prof, 20, m=mm, cap_top=True, cap_bot=True, uvs_u=3)
    for y in (0.1, h - 0.1, h * 0.38, h * 0.62):
        rr = r * (1 + 0.12 * math.sin(math.pi * y / h)) + 0.012
        lathe(m, 'iron', [(rr, y - 0.03), (rr, y + 0.03)], 20, m=mm)

def chesterfield(m, mm, w=2.6, leather='leather'):
    """tufted leather sofa, front faces +z, origin at floor centre"""
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
    w = 1.05; d = 0.95
    bevel_box(m, leather, w - 0.3, 0.42, d - 0.15, 0.08, m=M(mm, T(0, 0.3, 0.05)))
    bevel_box(m, leather, w - 0.32, 0.2, d - 0.35, 0.08, m=M(mm, T(0, 0.6, 0.13)))
    bevel_box(m, leather, w - 0.3, 0.75, 0.25, 0.1, m=M(mm, T(0, 0.9, -d / 2 + 0.17), Rx(-8)))
    for s in (-1, 1):
        bevel_box(m, leather, 0.24, 0.5, d, 0.09, m=M(mm, T(s * (w / 2 - 0.12), 0.55, 0)))
        lathe(m, leather, [(0.0, 0), (0.15, 0.0), (0.18, 0.08), (0.18, d - 0.08), (0.15, d), (0.0, d)], 10, m=M(mm, T(s * (w / 2 - 0.12), 0.8, -d / 2), Rx(90)))

def stool(m, mm):
    lathe(m, 'leather', [(0.0, 0.78), (0.2, 0.78), (0.22, 0.84), (0.19, 0.9), (0.0, 0.92)], 14, m=mm)
    lathe(m, 'dark', [(0.18, 0.7), (0.2, 0.78)], 14, m=mm)
    for k in range(4):
        a = k * 90 + 45
        p0 = np.array([0.14 * math.sin(math.radians(a)), 0.72, 0.14 * math.cos(math.radians(a))]); p1 = np.array([0.24 * math.sin(math.radians(a)), 0, 0.24 * math.cos(math.radians(a))])
        tube(m, 'dark', [p0, p1], 0.025, 6, m=mm)
    lathe(m, 'brass', [(0.19, 0.3), (0.2, 0.32), (0.19, 0.34)], 14, m=mm)

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
    deck(L1, octa(A1 - 0.25), Y + 0.03, rng, mat='dark', joists=False, edge_mat='dark', flat=True)
    for (cx, cz), w in zip(GROUPS, (7.0, 5.0)):
        h = w * 711 / 512
        quad(L1, 'rug', w, h, M(T(cx, Y + 0.045, cz), Rx(-90), Rz(90)))
        # fringe
        for s in (-1, 1):
            for k in range(int(w / 0.06)):
                x = -w / 2 + k * 0.06
                box(L1, 'pale', 0.012, 0.004, 0.12, m=M(T(cx, Y + 0.046, cz), Ry(90), T(x, 0, s * (h / 2 + 0.05))), faces='Y')

def the_bar():
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
    return dict(taps=[[tx0 + k * 0.6, Y + 1.5, bz - 0.25] for k in range(6)], bz=bz)

def fireplace():
    # big mud-stone hearth on the west face (x = -23.6)
    fx = -23.0 - dA; fz = 2.0
    for k in range(7):
        w = 4.6 - k * 0.2 if k > 4 else 4.6
        bevel_box(L1, 'mud', 1.3, 1.0, w, 0.08, m=T(fx + 0.1, Y + 0.5 + k * 1.0, fz), uvs=2.0)
    box(L1, 'black', 0.6, 1.5, 2.4, m=T(fx + 0.5, Y + 0.95, fz))
    bevel_box(L1, 'dark', 0.6, 0.25, 5.2, 0.04, m=T(fx + 0.75, Y + 2.25, fz), uvs=3.0)             # mantel
    bevel_box(L1, 'mud', 1.8, 0.25, 5.4, 0.05, m=T(fx + 0.8, Y + 0.12, fz), uvs=2.0)              # hearth stone
    for k in range(5): cyl(L1, 'bark', 0.09, 1.3, 8, m=M(T(fx + 0.55, Y + 0.32 + (k % 2) * 0.14, fz - 0.6 + k * 0.3), Rx(90), T(0, -0.65, 0)))
    for k in range(9): sphere(L1, 'ember', 0.07, 6, 4, m=T(fx + 0.55 + rng.uniform(-0.15, 0.15), Y + 0.28, fz + rng.uniform(-0.9, 0.9)))
    collider_box(C1, 1.6, 7, 4.8, T(fx + 0.1, Y + 3.5, fz))
    # mounted gator skull... a ship's wheel above the mantel and two armchairs facing the fire
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
    return dict(fire=[fx + 0.55, Y + 0.3, fz])

def lounge_seating():
    groups = GROUPS
    for gi, (cx, cz) in enumerate(groups):
        for k, (dx, dz, ry) in enumerate([(0, -2.3, 0), (0, 2.3, 180), (-2.9, 0, 90), (2.9, 0, -90)]):
            if gi == 1 and k >= 2: continue
            chesterfield(L1, M(T(cx + dx, Y, cz + dz), Ry(ry)), 2.8 if k < 2 else 2.2, 'leather' if (k + gi) % 2 == 0 else 'leatherg')
            collider_box(C1, 2.8 if k < 2 and ry in (0, 180) else 1.0, 0.9, 1.0 if ry in (0, 180) else 2.2, T(cx + dx, Y + 0.45, cz + dz))
        # coffee table: thick planks on iron legs, with a lantern, a deck of cards and mugs
        bevel_box(L1, 'bartop', 2.2, 0.12, 1.1, 0.03, m=T(cx, Y + 0.48, cz), uvs=2.0)
        for sx in (-1, 1):
            for sz in (-1, 1): bevel_box(L1, 'iron', 0.08, 0.42, 0.08, 0.01, m=T(cx + sx * 0.95, Y + 0.21, cz + sz * 0.45))
        collider_box(C1, 2.2, 0.55, 1.1, T(cx, Y + 0.28, cz))
        mug(L1, T(cx + 0.5, Y + 0.54, cz + 0.2)); mug(L1, T(cx - 0.6, Y + 0.54, cz - 0.15), full=False)
        # barrel side tables with candles
        for s in (-1, 1):
            barrel(L1, T(cx + s * 2.0, Y, cz - 3.4 if gi == 0 else cz - 3.3), r=0.36, h=0.85)
            lathe(L1, 'label', [(0.0, 0), (0.04, 0), (0.04, 0.16), (0.0, 0.16)], 8, m=T(cx + s * 2.0, Y + 0.87, cz - 3.4))
            sphere(L1, 'glow', 0.025, 6, 4, m=T(cx + s * 2.0, Y + 1.06, cz - 3.4))

def card_tables():
    for (cx, cz) in [(17.0, -8.0), (8.0, -11.5)]:
        lathe(L1, 'bartop', [(1.05, Y + 0.76), (1.2, Y + 0.78), (1.2, Y + 0.84), (1.05, Y + 0.86)], 24, m=T(cx, 0, cz))
        lathe(L1, 'felt', [(0.0, Y + 0.81), (1.06, Y + 0.81), (1.06, Y + 0.83), (0.0, Y + 0.83)], 24, m=T(cx, 0, cz))
        lathe(L1, 'dark', [(0.25, Y), (0.12, Y + 0.1), (0.1, Y + 0.7), (0.3, Y + 0.78)], 12, m=T(cx, 0, cz))
        collider_box(C1, 2.2, 0.85, 2.2, T(cx, Y + 0.42, cz))
        for k in range(4):
            a = k * 90 + 45; x = cx + 1.65 * math.sin(math.radians(a)); z = cz + 1.65 * math.cos(math.radians(a))
            armchair(L1, M(T(x, Y, z), Ry(a + 180)), 'leather')
        for k in range(6):   # poker chips + cards
            a = k * 60; x = cx + 0.6 * math.sin(math.radians(a)); z = cz + 0.6 * math.cos(math.radians(a))
            for j in range(rng.randint(2, 6)): cyl(L1, rng.choice(['gold', 'velvet', 'velvett']), 0.035, 0.008, 10, m=T(x, Y + 0.835 + j * 0.009, z))

def jukebox():
    jx, jz = A1 - 2.0, -3.0
    mm = M(T(jx, Y, jz), Ry(-90))
    bevel_box(L1, 'bartop', 1.4, 1.5, 0.8, 0.06, m=M(mm, T(0, 0.75, 0)))
    lathe(L1, 'bartop', [(0.0, -0.4), (0.7, -0.4), (0.7, 0.4), (0.0, 0.4)], 20, m=M(mm, T(0, 1.5, 0), Rx(90)), a0=-90, a1=90)
    quad(L1, 'mudglow', 1.1, 0.5, M(mm, T(0, 1.0, 0.41)))
    lathe(L1, 'mudglow', [(0.52, 0.41), (0.58, 0.41)], 20, m=M(mm, T(0, 1.5, 0), Rx(-90)), a0=-90, a1=90)
    for k in range(9): box(L1, 'brass', 1.0, 0.025, 0.03, m=M(mm, T(0, 0.15 + k * 0.06, 0.42)))
    quad(L1, 'label', 0.9, 0.22, M(mm, T(0, 1.36, 0.415)))
    collider_box(C1, 0.9, 2.2, 1.5, T(jx, Y + 1.1, jz))
    return dict(jukebox=[jx - 0.45, Y + 1.0, jz])

def wall_cards():
    """twenty real Mudwater cards in gilt frames round the walls"""
    cards = [8, 9, 19, 22, 34, 41, 49, 59, 61, 67, 76, 82, 85, 90, 100, 106, 118, 120, 21, 1]
    faces = octa(A1 - 0.25); spots = []
    for i in range(8):
        if i in (7, 3): continue                       # front (door) and back (the bar wall)
        a, b = faces[i], faces[(i + 1) % 8]
        mm, ln = place(a, b, Y)
        for t in (0.2, 0.8):
            spots.append(M(mm, T(ln * t, 4.9, -0.2), Ry(180)))
    for k, mm in enumerate(spots[:len(cards)]):
        n = cards[k]
        M_['card%d' % n] = dict(tex=MW + 'mwc_%03d.jpg' % n, emis_tex=MW + 'mwc_%03d.jpg' % n, emis=(0.25, 0.25, 0.25), rough=0.6)
        quad(L1, 'card%d' % n, 1.3, 1.8, M(mm, T(0, 0, 0.06)))
        bevel_box(L1, 'gold', 1.55, 2.05, 0.06, 0.02, m=mm)
        sconce_pos = M(mm, T(0, 1.25, 0.05))
        box(L1, 'brass', 0.5, 0.04, 0.16, m=sconce_pos)

def ceiling_hardware():
    # rope-hung wagon wheel chandeliers are separate (they sway); here: big ship's ropes and fishing nets on the beams
    for k in range(6):
        a = k * 60; r = 18
        x, z = r * math.sin(math.radians(a)), r * math.cos(math.radians(a))
        pts = [(x + 2.2 * math.cos(t), LY['f2'] - 0.9 - 0.9 * math.sin(t) ** 2, z + 2.2 * math.sin(t)) for t in np.linspace(0, math.pi, 12)]
        tube(L1, 'rope', pts, 0.05, 6, twist=2)

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
    M_['logo'] = dict(tex='/home/claude/spire/tmp/ext/mw_logo_0.png', emis_tex='/home/claude/spire/tmp/ext/mw_logo_0.png', emis=(0.6, 0.5, 0.35), alpha='MASK', cutoff=0.4, double=True)
    floor_and_rugs(); bar = the_bar(); fire = fireplace(); lounge_seating(); card_tables(); jb = jukebox(); wall_cards(); ceiling_hardware()
    print('lounge', write(OUT + 'sp_f1_lounge.glb', L1, M_))
    print('col', write(OUT + 'sp_f1_col.glb', C1, M_))
    for name, mesh in [('sp_chandelier', chandelier()), ('sp_tap', tap_handle()), ('sp_pour', pour()), ('sp_foam', foam_head()), ('sp_guestbook', guestbook())]:
        print(name, write(OUT + name + '.glb', mesh, M_))
    mm = Mesh(); mug(mm, T(0, 0, 0)); print('mug', write(OUT + 'sp_mug.glb', mm, M_))
    json.dump(dict(bar, **fire, **jb), open('/home/claude/spire/out/f1_layout.json', 'w'))
