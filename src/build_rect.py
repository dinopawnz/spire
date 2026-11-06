"""MUDWATER SPIRE v2 - the rectangular swamp hall (85 x 60 m), four storeys + roof deck + steeple.
Building space: centre (0, 0, 0), water at y 0.1, the front (+z) faces the boardwalk.
  F1 lounge 3.0 | F2 Mud Match gallery 10.5 | F3 card floor 19.0 | F4 Group Mud rooms 26.5 | roof deck 34.0
Two stair towers at the short ends (x = +-34.4 .. 42.1, z = -9.5 .. 9.5), a bank of four lifts against the back wall.
Writes sp_shell.glb, sp_shell_col.glb, sp_boardwalk.glb, out/layout.json."""
import math, json, random, os
import numpy as np
from glb import *
from kit import *

OUT = '/home/claude/spire/out/glb/'
rng = random.Random(85)
X1, Z1 = 60.0, 42.5                         # outer wall lines (half sizes). v24: twice the floor space (was 42.5 x 30)
FL = dict(lounge=3.0, hall=10.5, gallery=24.9, cards=32.0, rooms=40.0, roof=51.0)
KEYS = ['lounge', 'hall', 'cards', 'rooms', 'roof']        # full floors. 'gallery' is only the top of the Hall of Fakes stair + the east core
NS = len(KEYS) - 1                          # storeys between the levels
BAND = dict(xo=X1 - 8.1, xi=X1 - 12.1, zo=Z1 - 0.4, zi=Z1 - 4.4)   # the Hall of Fakes: a square winding stair hugging the walls, open hall inside it
YS = [FL[k] for k in KEYS]
PORCH = dict(x=X1 + 7.5, zb=-Z1 - 7.0, zf=Z1 + 12.0)    # porch deck round the building (front plaza is deeper)
WALK = dict(w=8.0, z0=Z1 + 12.0, z1=Z1 + 78.0, y1=0.6)
# stair wells (east one; the west one is the mirror):  landing strip z -9.5..-6 is floor, the rest of the well is open
SW = dict(xi=X1 - 8.1, xd=X1 - 4.1, xo=X1 - 0.4, zl=-9.5, z0=-6.0, z1=6.0, zm=9.5)
LIFTS = [('B', 'The Grand Cage', X1 - 4.25, -(Z1 - 11.0), False), ('D', 'The Lucky Cage', -(X1 - 4.25), -(Z1 - 11.0), False)]     # owner: 2 lifts, the back corners (the front ones blocked the ramp)
L = dict(FL=FL, keys=KEYS, X1=X1, Z1=Z1, porch_box=PORCH, walk=WALK, sw=SW,
         porch=FL['lounge'], f2=FL['hall'], gallery=FL['gallery'], f3=FL['cards'], f4=FL['rooms'], roof=FL['roof'], band=BAND,
         walk_y=WALK['y1'], walk_len=WALK['z1'] - WALK['z0'], walk_w=WALK['w'], walk_z0=WALK['z0'],
         stop_names=dict({'%.1f' % FL[k]: k for k in KEYS}, **{'%.1f' % FL['gallery']: 'gallery'}),
         lifts=[dict(id=i, name=n, x=x, z=z, stops=sorted(YS + ([FL['gallery']] if gal else []))) for (i, n, x, z, gal) in LIFTS],
         shaft_apo=3.2, cab_apo=2.9, shaft_base=FL['lounge'], shaft_top=FL['roof'] + 6.5, door_w=2.4, door_h=3.7,      # v24: cabs twice the floor area, wider doors
         floors_through=YS[1:] + [FL['gallery']])
_c = octa(L['shaft_apo'])
L['shaft_fp'] = [[round(x, 4), round(-(L['shaft_apo'] + 0.95) if (z < -L['shaft_apo'] * 0.9 and abs(x) < L['shaft_apo'] * 0.5) else z, 4)] for (x, z) in _c]   # the counterweight bay at the back
SHAFTS = [hole_poly(lf['x'], lf['z'], L['shaft_fp'], 1.04) for lf in L['lifts']]
def well_holes():
    out = []
    for s in (1, -1):
        xa, xb = sorted((s * SW['xi'], s * SW['xo']))
        out.append(('p', [(xa, SW['z0']), (xb, SW['z0']), (xb, SW['zm']), (xa, SW['zm'])]))
    return out
RECT = [(-X1, -Z1), (X1, -Z1), (X1, Z1), (-X1, Z1)]
shell = Mesh(); col = Mesh(); walkm = Mesh()

def box_between(m, mat, p0, p1, w, h, y, mm_extra=None, uvs=3.0):
    """a beam/board of width w (horizontal) x h (vertical) from xz p0 to p1, centred at height y"""
    mm, ln = place(p0, p1, y)
    bevel_box(m, mat, ln, h, w, 0.02, m=M(mm, T(ln / 2, 0, 0)), uvs=uvs)

def col_between(p0, p1, y0, h, th=0.4):
    mm, ln = place(p0, p1, y0)
    collider_box(col, ln, h, th, M(mm, T(ln / 2, h / 2, 0)))

# ------------------------------------------------------------------ porch, pilings, boardwalk
def porch():
    P = [(-PORCH['x'], PORCH['zb']), (PORCH['x'], PORCH['zb']), (PORCH['x'], PORCH['zf']), (-PORCH['x'], PORCH['zf'])]
    flat_deck(shell, 'plank', P, FL['lounge'], uvs=3.0)
    slab_collider(col, FL['lounge'], ('p', P), pad=0.0)
    # rim + railing (gap at the front for the boardwalk)
    for i in range(4):
        a, b = P[i], P[(i + 1) % 4]
        box_between(shell, 'dark', a, b, 0.14, 0.45, FL['lounge'] - 0.25)
        if i == 2:     # front edge runs from +x to -x
            for seg in (((PORCH['x'], PORCH['zf']), (WALK['w'] / 2 + 0.3, PORCH['zf'])), ((-WALK['w'] / 2 - 0.3, PORCH['zf']), (-PORCH['x'], PORCH['zf']))):
                railing(shell, list(seg), FL['lounge'], rng, closed=False, rope_mat='rope', balusters=False, post_every=3.0)
                col_between(seg[0], seg[1], FL['lounge'], 1.2, 0.3)
        else:
            railing(shell, [a, b], FL['lounge'], rng, closed=False, rope_mat='rope', balusters=False, post_every=3.0)
            col_between(a, b, FL['lounge'], 1.2, 0.3)
    # pilings: a ring under the porch edge and a sparse grid under the building
    for x in np.arange(-PORCH['x'] + 1, PORCH['x'], 4.5):
        for z in np.arange(PORCH['zb'] + 1, PORCH['zf'], 4.5):
            edge = min(x + PORCH['x'], PORCH['x'] - x, z - PORCH['zb'], PORCH['zf'] - z)
            if edge < 5 or rng.random() < 0.18:
                piling(shell, x + rng.uniform(-0.5, 0.5), z + rng.uniform(-0.5, 0.5), -1.5, FL['lounge'] - 0.3, rng, r=rng.uniform(0.3, 0.42), rope=rng.random() < 0.25)
    # big cypress-trunk columns under the building corners
    for (x, z) in RECT:
        prof = [(1.6 - 0.4 * t + 0.3 * math.exp(-t * 6), -1.5 + t * (FL['lounge'] + 1.4)) for t in np.linspace(0, 1, 10)]
        lathe(shell, 'bark', prof, 16, m=T(x, 0, z), uv_v=4.0, uvs_u=2)

MESHY_WALK = os.path.exists('/home/claude/spire/out/glb/sp_m_railing.glb')     # carved Meshy railings + lantern posts (placed by build_html)
def boardwalk():
    """the approach: 8 m wide, from the end of the pier (y 0.6) gently up to the porch front (y 3.0)"""
    w = WALK['w']; z0, z1 = WALK['z0'], WALK['z1']; ya, yb = FL['lounge'], WALK['y1']
    n = 22
    for i in range(n):
        za = z0 + (z1 - z0) * i / n; zb = z0 + (z1 - z0) * (i + 1) / n
        y0 = ya + (yb - ya) * i / n; y1 = ya + (yb - ya) * (i + 1) / n
        P = np.array([[-w / 2, y0, za], [w / 2, y0, za], [w / 2, y1, zb], [-w / 2, y1, zb]])
        U = np.c_[P[:, 0] / 3, P[:, 2] / 3]
        walkm.add('wetfloor', P, [[0, 1, 0]] * 4, np.c_[P[:, 2] / 3.2, P[:, 0] / 3.2], [0, 2, 1, 0, 3, 2])      # wet dark planks, boards across the walk
        walkm.add('dark', P - np.array([0, 0.12, 0]), [[0, -1, 0]] * 4, U, [0, 1, 2, 0, 2, 3])
        for s in (-1, 1):
            bevel_box(walkm, 'dark', 0.14, 0.4, zb - za, 0.02, m=M(T(s * (w / 2 + 0.07), (y0 + y1) / 2 - 0.2, (za + zb) / 2), Rx(-math.degrees(math.atan2(y1 - y0, zb - za)))), uvs=3.0)
    # (v23, owner: a gap under the bridge) solid plank skirts from the deck down into the water on both sides and across the far end,
    # with thick bark pilings every 6 m, so the boardwalk reads as built on the swamp, not floating over it
    for i in range(n):
        za = z0 + (z1 - z0) * i / n; zb = z0 + (z1 - z0) * (i + 1) / n
        y0 = ya + (yb - ya) * i / n; y1 = ya + (yb - ya) * (i + 1) / n
        for s in (-1, 1):
            x = s * (w / 2 + 0.03)
            P = np.array([[x, y0 - 0.1, za], [x, y1 - 0.1, zb], [x, -0.6, zb], [x, -0.6, za]])
            Uv = np.c_[P[:, 2] / 0.35, P[:, 1] / 3.0]                 # boards running up and down
            walkm.add('dark', P, [[s, 0, 0]] * 4, Uv, [0, 1, 2, 0, 2, 3] if s > 0 else [0, 2, 1, 0, 3, 2], col=tint(rng, 0.1, 0.7))
    x0_, x1_ = -w / 2 - 0.05, w / 2 + 0.05
    P = np.array([[x0_, yb - 0.1, z1 + 0.02], [x1_, yb - 0.1, z1 + 0.02], [x1_, -0.6, z1 + 0.02], [x0_, -0.6, z1 + 0.02]])
    walkm.add('dark', P, [[0, 0, 1]] * 4, np.c_[P[:, 0] / 0.35, P[:, 1] / 3.0], [0, 2, 1, 0, 3, 2], col=tint(rng, 0.1, 0.7))
    bevel_box(walkm, 'dark', w + 0.3, 0.22, 0.16, 0.02, m=T(0, yb - 0.2, z1 + 0.08), uvs=3.0)          # a fascia beam across the end
    for z in np.arange(z0 + 3.0, z1 + 0.1, 6.0):
        t = (z - z0) / (z1 - z0); y = ya + (yb - ya) * t
        for s in (-1, 1):
            lathe(walkm, 'bark', [(0.24, -1.2), (0.22, y - 0.15), (0.0, y - 0.1)], 10, m=T(s * (w / 2 + 0.2), 0, min(z, z1 - 0.2)), uv_v=2.0)
    # collider: one long sloped slab + side rails
    ln = math.hypot(z1 - z0, ya - yb); ang = math.degrees(math.atan2(ya - yb, z1 - z0))
    collider_box(col, w + 0.4, 0.4, ln + 0.4, M(T(0, (ya + yb) / 2 - 0.2, (z0 + z1) / 2), Rx(ang)))
    for s in (-1, 1):
        collider_box(col, 0.3, 1.4, ln, M(T(s * (w / 2 + 0.15), (ya + yb) / 2 + 0.6, (z0 + z1) / 2), Rx(ang)))
    # posts + rope rails + pilings
    k = 0
    for z in (np.arange(z0 + 1.5, z1, 3.0) if not MESHY_WALK else []):
        t = (z - z0) / (z1 - z0); y = ya + (yb - ya) * t
        for s in (-1, 1):
            x = s * (w / 2 + 0.07)
            lathe(walkm, 'bark', [(0.16, -1.8), (0.15, 1.2), (0.0, 1.3)], 8, m=T(x, y, z), uv_v=2.0)
        k += 1
    for s in ((-1, 1) if not MESHY_WALK else ()):
        pts = []
        for z in np.arange(z0 + 1.5, z1, 3.0):
            t = (z - z0) / (z1 - z0); y = ya + (yb - ya) * t
            pts.append((s * (w / 2 + 0.07), y + 0.95, z))
        for a, b in zip(pts[:-1], pts[1:]):
            sag = [(a[0], a[1] + (b[1] - a[1]) * u - 0.18 * math.sin(math.pi * u), a[2] + (b[2] - a[2]) * u) for u in np.linspace(0, 1, 6)]
            tube(walkm, 'rope', sag, 0.035, 5, twist=2)
    # wide steps down from the porch front edge onto the boardwalk are not needed (it meets the porch level)

# ------------------------------------------------------------------ the walls: timber bays with windows / doors
BAYX = 22; BAYZ = 16        # bays along the long (x) and short (z) sides
def side_bays(side):
    """returns list of (p0, p1, local_center_coord) per bay for a side: 'front' (+z), 'back', 'east' (+x), 'west'"""
    if side == 'front': pts = [(-X1 + 2 * X1 * i / BAYX, Z1) for i in range(BAYX + 1)]
    elif side == 'back': pts = [(X1 - 2 * X1 * i / BAYX, -Z1) for i in range(BAYX + 1)]
    elif side == 'east': pts = [(X1, Z1 - 2 * Z1 * i / BAYZ) for i in range(BAYZ + 1)]
    else: pts = [(-X1, -Z1 + 2 * Z1 * i / BAYZ) for i in range(BAYZ + 1)]
    return list(zip(pts[:-1], pts[1:]))

def bay_spec(side, k, p0, p1, bi):
    """what goes in bay bi on storey k: ('door', w, h) | ('win', w, h, y, kind) | ('brace',) | None
    (v23, owner: fewer but grander windows) - a big arched window on every other bay, plain timber between (vines + ivy outside,
    framed cards inside); the Hall of Fakes level only every third bay, high up above the portraits"""
    cx = (p0[0] + p1[0]) / 2; cz = (p0[1] + p1[1]) / 2
    if side in ('east', 'west') and abs(cz) < 10 and k < NS: return ('brace',) if bi % 2 else None   # stair towers behind
    kinds = ['win', 'win', 'win', 'boarded', 'win', 'win', 'win', 'win']
    kind = kinds[(bi * 7 + k * 3 + len(side)) % len(kinds)]
    if kind == 'crooked': kind = 'win'
    if k == 0:
        if side == 'front' and abs(cx) < 6: return ('door', 4.6, 4.6)
        if side in ('east', 'west') and abs(cz + Z1 * 0.5) < 2.6: return ('door', 3.0, 3.6)
        return ('win', 3.1, 5.6, 0.9, 'win') if bi % 2 == 1 else None          # tall glowing lounge windows
    if k == 1:
        if side in ('front', 'back') and bi % 3 == 1: return ('win', 3.0, 2.2, 19.0, kind)   # high, ABOVE the highest portraits
        return ('brace',) if bi % 3 == 2 and side in ('front', 'back') else None
    if bi % 2 == 1: return ('brace',) if bi % 4 == 3 else None
    if k == 3: return ('win', 3.0, 4.6, 3.6, kind)
    return ('win', 3.0, 4.4, 1.3, kind)

def rustic_wall(p0, p1, y0, h, holes, battens=True, plates=True, ext=False):
    """weathered vertical boards of uneven width and colour, a ragged bottom edge, two battens; holes = [(x, y, w, h)]"""
    mm, ln = place(p0, p1, y0)
    x = 0.0
    while x < ln - 0.02:
        bw = min(ln - x, rng.uniform(0.2, 0.42)); xc = x + bw / 2
        spans = [(rng.uniform(-0.12, 0.05), h)]
        for (hx, hy, hw, hh) in holes:
            if x + bw > hx - hw / 2 - 0.1 and x < hx + hw / 2 + 0.1:
                ns = []
                for a, b in spans:
                    lo, hi = hy - hh / 2 - 0.1, hy + hh / 2 + 0.1
                    if b <= lo or a >= hi: ns.append((a, b))
                    else:
                        if a < lo: ns.append((a, lo))
                        if b > hi: ns.append((hi, b))
                spans = ns
        c = tint(rng, 0.24, rng.choice([0.78, 0.9, 1.0, 1.05]))
        for a, b in spans:
            if b - a > 0.04:
                bm = M(mm, T(xc, (a + b) / 2, rng.uniform(-0.02, 0.02))); uo = (rng.random(), rng.random())
                box(shell, 'plank_ext' if ext else 'plank', bw - 0.015, b - a, 0.08, m=bm, col=c, uvs=3.0, uvoff=uo, faces='Z')      # outer face: deep brown
                box(shell, 'plank', bw - 0.015, b - a, 0.08, m=bm, col=c, uvs=3.0, uvoff=uo, faces='z')
        x += bw
    for yy in ((h * 0.33, h * 0.66) if battens else ()):
        segs = [(0.0, ln)]
        for (hx, hy, hw, hh) in holes:
            if hy - hh / 2 - 0.2 < yy < hy + hh / 2 + 0.2:
                segs = subtract(segs, [(hx - hw / 2 - 0.25, hx + hw / 2 + 0.25)])
        for a, b in segs:
            if b - a > 0.3: box(shell, 'dark', b - a, 0.16, 0.1, m=M(mm, T((a + b) / 2, yy, 0.09)), col=tint(rng, 0.1), uvs=3.0)
    if plates:
        box(shell, 'dark', ln, 0.3, 0.3, m=M(mm, T(ln / 2, h - 0.15, 0.05)), uvs=3.0)          # top plate
        box(shell, 'dark', ln, 0.25, 0.3, m=M(mm, T(ln / 2, 0.12, 0.05)), uvs=3.0)             # sill beam
    return mm, ln

def boarded(mm, w, h):
    quad(shell, 'black', w, h, M(mm, T(0, 0, -0.02)), double=True)
    for k in range(4):
        a = rng.uniform(-14, 14)
        box(shell, 'pale', w + 0.5, 0.2, 0.06, m=M(mm, T(rng.uniform(-0.1, 0.1), -h / 2 + (k + 0.6) * h / 4.2, 0.08), Rz(a)), col=tint(rng, 0.2), uvs=1.5)

def walls():
    for k in range(NS):
        y0 = YS[k]; h = YS[k + 1] - y0
        for side in ('front', 'back', 'east', 'west'):
            for bi, (p0, p1) in enumerate(side_bays(side)):
                if side == 'front' and k == 0 and abs((p0[0] + p1[0]) / 2) < 6: continue    # the grand doorway is built below
                sp = bay_spec(side, k, p0, p1, bi)
                mm0, ln = place(p0, p1, y0)
                if k == 0: L.setdefault('lounge_bays', []).append([side, round((p0[0] + p1[0]) / 2, 3), round((p0[1] + p1[1]) / 2, 3), sp[0] if sp else ''])
                holes = []; door = None
                if sp and sp[0] == 'win': holes = [(ln / 2, sp[3] + sp[2] / 2, sp[1], sp[2])]
                if sp and sp[0] == 'door': door = (ln / 2, sp[1], sp[2]); holes = [(ln / 2, sp[2] / 2, sp[1], sp[2])]
                rustic_wall(p0, p1, y0, h, holes, battens=(k != 1), ext=True)      # no battens across the Hall of Fakes portraits; outer face deep brown
                if sp and sp[0] == 'win':
                    hx, hy, hw, hh = holes[0]; wm = M(mm0, T(hx, hy, 0))
                    if sp[4] == 'boarded': boarded(wm, hw, hh)
                    else:
                        window(shell, hw, hh, wm, rng, shutters=True, mull=(2, 4 if hh > 4 else 3))
                        if side != 'back':           # (v23) where the Meshy lodge windows go on the outside: [x, y centre, z, facing, w, h]
                            c_ = (wm @ np.array([0, 0, 0, 1]))[:3]; o_ = {'front': (0, 1, 0), 'east': (1, 0, 90), 'west': (-1, 0, 270)}[side]
                            L.setdefault('ext_windows', []).append([round(float(c_[0]), 3), round(float(c_[1]), 3), round(float(c_[2]), 3), o_[2], hw, hh])
                if sp and sp[0] == 'brace':           # an X of rough timbers across a blank bay, standing proud of the wall
                    for (a, b) in (((0.3, 0.4), (ln - 0.3, h - 0.5)), ((0.3, h - 0.5), (ln - 0.3, 0.4))):
                        pa = (mm0 @ np.array([a[0], a[1], 0.32, 1]))[:3]; pb = (mm0 @ np.array([b[0], b[1], 0.32, 1]))[:3]
                        d = pb - pa; bevel_box(shell, 'dark', 0.24, 0.3, np.linalg.norm(d), 0.03, m=M(T(*((pa + pb) / 2)), look_basis(d)), col=tint(rng, 0.15), uvs=2.5)
                if door:
                    dx, dw, dh = door
                    for sx in (-1, 1): bevel_box(shell, 'dark', 0.26, dh + 0.25, 0.5, 0.03, m=M(mm0, T(dx + sx * (dw / 2 + 0.13), (dh + 0.25) / 2, 0)), uvs=1.5)
                    bevel_box(shell, 'dark', dw + 0.9, 0.32, 0.5, 0.03, m=M(mm0, T(dx, dh + 0.16, 0)), uvs=1.5)
                    for a, b in ((0, dx - dw / 2), (dx + dw / 2, ln)):
                        if b - a > 0.05: collider_box(col, b - a, h, 0.45, M(mm0, T((a + b) / 2, h / 2, 0)))
                    collider_box(col, dw, h - dh, 0.45, M(mm0, T(dx, dh + (h - dh) / 2, 0)))
                else:
                    collider_box(col, ln, h, 0.45, M(mm0, T(ln / 2, h / 2, 0)))
    # the grand front doorway at x = 0
    y0 = YS[0]; h = YS[1] - y0; dw, dh = 9.0, 5.4; bx = 2 * X1 / BAYX
    for s in (-1, 1):
        a, b = dw / 2, bx
        p0, p1 = ((s * a, Z1), (s * b, Z1)) if s > 0 else ((s * b, Z1), (s * a, Z1))
        rustic_wall(p0, p1, y0, h, [])
        collider_box(col, b - a, h, 0.45, T(s * (a + b) / 2, y0 + h / 2, Z1))
        bevel_box(shell, 'dark', 0.6, dh + 0.6, 0.8, 0.04, m=T(s * (dw / 2 + 0.3), y0 + (dh + 0.6) / 2, Z1), uvs=2.0)
    rustic_wall((-dw / 2, Z1), (dw / 2, Z1), y0 + dh, h - dh, [])
    collider_box(col, dw, h - dh, 0.45, T(0, y0 + dh + (h - dh) / 2, Z1))
    bevel_box(shell, 'dark', dw + 1.8, 0.7, 0.9, 0.04, m=T(0, y0 + dh + 0.35, Z1 + 0.05), uvs=2.0)
    # exterior posts: rough cypress poles at every bay line, crooked a touch, porch to roof
    for side in ('front', 'back', 'east', 'west'):
        for (p0, p1) in side_bays(side):
            x, z = p0
            if side == 'front' and abs(x) < 6.0: continue          # never a pole in the grand doorway (owner: keep the entrance clear)
            out = np.array([np.sign(x) if abs(abs(x) - X1) < 1e-6 else 0, np.sign(z) if abs(abs(z) - Z1) < 1e-6 else 0]) * 0.45
            H = FL['roof'] - FL['lounge'] + 1.2
            prof = [(0.36 + 0.05 * math.sin(t * 11 + x * 0.7) + 0.08 * math.exp(-t * 8), t * H) for t in np.linspace(0, 1, 9)]
            lathe(shell, 'bark', prof, 8, m=M(T(x + out[0], FL['lounge'], z + out[1]), Rx(rng.uniform(-0.6, 0.6)), Rz(rng.uniform(-0.6, 0.6))), uv_v=9.0)

BAL_D = 2.4      # balcony depth
def belts():
    """wraparound balconies on every floor line (the owner's outside concept): a plank deck on angled brackets, a carved
    railing with balusters, a fascia beam, moss and vines trailing off the edge. The balcony above is each one's roof."""
    lines = [YS[k] for k in range(1, NS)] + [FL['gallery'] - 7.2, FL['gallery']]
    D = BAL_D
    for li, y in enumerate(sorted(lines)):
        o = 0.3
        R0 = [(-X1 - o, -Z1 - o), (X1 + o, -Z1 - o), (X1 + o, Z1 + o), (-X1 - o, Z1 + o)]
        for i in range(4): box_between(shell, 'dark', R0[i], R0[(i + 1) % 4], 0.5, 0.55, y - 0.1)        # belt beam on the wall
        Ri = [(-X1, -Z1), (X1, -Z1), (X1, Z1), (-X1, Z1)]
        Ro = [(-X1 - D, -Z1 - D), (X1 + D, -Z1 - D), (X1 + D, Z1 + D), (-X1 - D, Z1 + D)]
        skip_front = (y < 12.0)            # the portico roof covers the middle of the front at the first floor line
        for i in range(4):
            a0, a1, b0, b1 = Ri[i], Ri[(i + 1) % 4], Ro[i], Ro[(i + 1) % 4]
            front = (i == 2)
            spans = [(0.0, 1.0)]
            if front and skip_front:
                cut = (X1 - 11.0) / (2 * X1); spans = [(0.0, cut), (1.0 - cut, 1.0)]
            for (t0, t1) in spans:
                lerp = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
                # outer corners of a side reach the corner of the outer ring, so the four decks meet
                A0, A1 = lerp(a0, a1, t0), lerp(a0, a1, t1); B0, B1 = lerp(b0, b1, t0), lerp(b0, b1, t1)
                if t0 > 0: B0 = (A0[0] + (b0[0] - a0[0]), A0[1] + (b0[1] - a0[1])) if False else lerp(b0, b1, t0)
                P = np.array([[A0[0], y, A0[1]], [A1[0], y, A1[1]], [B1[0], y, B1[1]], [B0[0], y, B0[1]]])
                U = np.c_[P[:, 0] / 3.2, P[:, 2] / 3.2] if i % 2 == 0 else np.c_[P[:, 2] / 3.2, P[:, 0] / 3.2]
                idx = [0, 1, 2, 0, 2, 3]
                if np.cross(P[1] - P[0], P[3] - P[0])[1] < 0: idx = [0, 2, 1, 0, 3, 2]
                shell.add('plank', P + np.array([0, 0.02, 0]), [[0, 1, 0]] * 4, U, idx, col=tint(rng, 0.08, 0.85))
                shell.add('dark', P - np.array([0, 0.16, 0]), [[0, -1, 0]] * 4, U, idx[::-1])
                box_between(shell, 'dark', B0, B1, 0.22, 0.42, y - 0.08)                            # fascia
                # angled brackets under the deck
                d = np.array(B1) - np.array(B0); ln = np.linalg.norm(d)
                for t in np.arange(1.5, ln, 3.2):
                    q = np.array(B0) + d / ln * t; w_ = np.array(lerp(A0, A1, t / ln))
                    pa = np.array([w_[0], y - 1.6, w_[1]]); pb = np.array([q[0] - (q[0] - w_[0]) * 0.08, y - 0.15, q[1] - (q[1] - w_[1]) * 0.08])
                    dv = pb - pa; box(shell, 'dark', 0.16, 0.18, np.linalg.norm(dv), m=M(T(*((pa + pb) / 2)), look_basis(dv)), uvs=2.0)
                # carved railing on the outer edge (inset a touch), with an open end where a front span stops
                inset = 0.12
                r0 = (B0[0] + (A0[0] - B0[0]) / D * inset, B0[1] + (A0[1] - B0[1]) / D * inset)
                r1 = (B1[0] + (A1[0] - B1[0]) / D * inset, B1[1] + (A1[1] - B1[1]) / D * inset)
                pts = [r0, r1]
                if t0 > 0: pts = [lerp(a0, a1, t0), r0, r1]
                if t1 < 1: pts = [r0, r1, lerp(a0, a1, t1)]
                railing(shell, pts, y, rng, closed=False, h=1.05, post_every=2.6, balusters=True, bal_gap=0.36, cheap=True)
                # moss and vines trailing off the deck edge
                for t in np.arange(0.5, ln, 1.1):
                    if rng.random() < 0.45: continue
                    q = np.array(B0) + d / ln * t; hh = rng.uniform(0.6, 2.8)
                    tube(shell, 'moss', [(q[0], y - 0.25, q[1]), (q[0] + rng.uniform(-0.12, 0.12), y - 0.25 - hh / 2, q[1] + rng.uniform(-0.12, 0.12)), (q[0], y - 0.25 - hh, q[1])], 0.07, 4, radii=[0.12, 0.07, 0.015])
    L['balconies'] = dict(lines=sorted(lines), depth=D)

def pent(y_in, y_out, depth):
    for i in range(4):
        c_in = [(-X1, -Z1), (X1, -Z1), (X1, Z1), (-X1, Z1)]
        c_out = [(-X1 - depth, -Z1 - depth), (X1 + depth, -Z1 - depth), (X1 + depth, Z1 + depth), (-X1 - depth, Z1 + depth)]
        a0, a1 = c_in[i], c_in[(i + 1) % 4]; b0, b1 = c_out[i], c_out[(i + 1) % 4]
        P = np.array([[a0[0], y_in, a0[1]], [a1[0], y_in, a1[1]], [b1[0], y_out, b1[1]], [b0[0], y_out, b0[1]]])
        wd = P[1] - P[0]; wl = np.linalg.norm(wd); dd = P[3] - P[0]; dl = np.linalg.norm(dd)
        U = np.array([[0, 0], [wl / 4, 0], [np.dot(P[2] - P[0], wd / wl) / 4, dl / 4], [np.dot(P[3] - P[0], wd / wl) / 4, dl / 4]])
        nrm = np.cross(P[1] - P[0], P[3] - P[0]); nrm /= np.linalg.norm(nrm)
        idx = [0, 1, 2, 0, 2, 3]
        if nrm[1] < 0: nrm = -nrm; idx = [0, 2, 1, 0, 3, 2]
        shell.add('shingle', P + nrm * 0.16, [nrm] * 4, U, idx, col=tint(rng, 0.12, 0.9))
        shell.add('dark', P, [-nrm] * 4, U, idx[::-1])
        box_between(shell, 'dark', b0, b1, 0.14, 0.32, y_out)
        # rafter tails under the eave
        n = int(wl / 1.3)
        for kk in range(1, n):
            t = kk / n
            src = np.array(a0) + (np.array(a1) - np.array(a0)) * t; dst = np.array(b0) + (np.array(b1) - np.array(b0)) * t
            p0_ = np.array([src[0], y_in - 0.2, src[1]]); p1_ = np.array([dst[0], y_out - 0.15, dst[1]])
            dv = p1_ - p0_; box(shell, 'dark', 0.12, 0.18, np.linalg.norm(dv) + 0.25, m=M(T(*((p0_ + p1_) / 2)), look_basis(dv)), uvs=2.0)

def balconies():
    """crooked little balconies on the upper storeys, hung off the wall on rough brackets"""
    spots = [('front', 3, 0), ('front', 12, 0), ('back', 2, 2), ('back', 13, 2), ('front', 5, 3), ('front', 10, 3), ('east', 2, 2), ('west', 9, 3)]
    for side, bi, k in spots:
        p0, p1 = side_bays(side)[bi]
        mm, ln = place(p0, p1, YS[k + 1] if k < NS - 1 else YS[k] + 1.0)
        y = (YS[k] + 0.0)
        mm = M(place(p0, p1, YS[k])[0], T(ln / 2, 0, 0), Rz(rng.uniform(-1.2, 1.2)))
        # platform (outward = +z local)
        deck_m = M(mm, T(0, 0.0, 1.0))
        bevel_box(shell, 'plank', 3.6, 0.14, 1.9, 0.02, m=M(deck_m, T(0, -0.07, 0)), col=tint(rng, 0.2), uvs=2.0)
        for sx in (-1.5, 1.5):
            pa = (mm @ np.array([sx, -1.4, 0.2, 1]))[:3]; pb = (mm @ np.array([sx, -0.1, 1.85, 1]))[:3]
            d = pb - pa; box(shell, 'dark', 0.16, 0.2, np.linalg.norm(d), m=M(T(*((pa + pb) / 2)), look_basis(d)), uvs=2.0)
        pts = [(mm @ np.array([x, 0, z, 1]))[:3] for (x, z) in ((-1.75, 0.1), (-1.75, 1.9), (1.75, 1.9), (1.75, 0.1))]
        railing(shell, [(p[0], p[2]) for p in pts], YS[k], rng, closed=False, h=1.0, post_every=1.0, balusters=False, rope_mat='rope')
        # a hanging lantern and a barrel
        lathe(shell, 'glow', [(0.0, 0), (0.12, 0.04), (0.14, 0.24), (0.1, 0.36), (0.0, 0.38)], 8, m=M(mm, T(1.3, 1.9, 1.2)))
        lathe(shell, 'dark', [(0.32, 0), (0.37, 0.4), (0.32, 0.8)], 10, m=M(mm, T(-1.1, 0.0, 1.1)), cap_top=True)

def shacks():
    """two crooked lean-to shacks on the side porches: a bait shop and a boat shed"""
    for s, z0, z1 in ((1, -Z1 + 1.0, -Z1 + 10.0), (-1, -Z1, -Z1 + 7.5)):
        x0, x1 = sorted((s * (X1 + 0.3), s * (X1 + 6.2)))
        y0 = FL['lounge']; hb, hf = 4.6, 3.4                # high side on the wall, low side out
        xin = s * (X1 + 0.3); xout = s * (X1 + 6.2)
        for (pa, pb, hh) in (((xout, z0), (xout, z1), hf), ((xin, z0), (xout, z0), None), ((xout, z1), (xin, z1), None)):
            mm, ln = place(pa, pb, y0)
            if hh:
                rustic_wall(pa, pb, y0, hh, [(ln / 2, 1.2, 1.2, 2.3), (ln * 0.2, 1.9, 1.0, 0.9)])
                collider_box(col, ln, hh, 0.4, M(mm, T(ln / 2, hh / 2, 0)))
            else:
                rustic_wall(pa, pb, y0, hf, [])
                tri = np.array([(mm @ np.array([0, hf, 0, 1]))[:3], (mm @ np.array([ln, hf, 0, 1]))[:3], (mm @ np.array([0 if (pa[0] == xin) else ln, hb, 0, 1]))[:3]])
                shell.add('plank', tri, [[0, 0, 1]] * 3, [[0, 0], [1, 0], [0, 1]], [0, 1, 2, 0, 2, 1], tint(rng, 0.2))
                collider_box(col, ln, hf, 0.4, M(mm, T(ln / 2, hf / 2, 0)))
        P = np.array([[xin, y0 + hb + 0.2, z0 - 0.6], [xin, y0 + hb + 0.2, z1 + 0.6], [xout + s * 0.8, y0 + hf - 0.1, z1 + 0.6], [xout + s * 0.8, y0 + hf - 0.1, z0 - 0.6]])
        nrm = np.cross(P[1] - P[0], P[3] - P[0]); nrm /= np.linalg.norm(nrm); idx = [0, 1, 2, 0, 2, 3]
        if nrm[1] < 0: nrm = -nrm; idx = [0, 2, 1, 0, 3, 2]
        U = np.array([[0, 0], [3, 0], [3, 2], [0, 2]])
        shell.add('shingle', P, [nrm] * 4, U, idx, col=tint(rng, 0.15, 0.85)); shell.add('dark', P - nrm * 0.1, [-nrm] * 4, U, idx[::-1])
        door_m = M(T(xout + s * 0.05, y0 + 1.15, (z0 + z1) / 2), Ry(90 * s))
        bevel_box(shell, 'dark', 1.25, 2.35, 0.08, 0.02, m=door_m)
        # crates and barrels outside
        for k in range(5):
            cx = xout + s * rng.uniform(0.8, 2.6); cz = rng.uniform(z0 + 0.5, z1 - 0.5)
            if k % 2: lathe(shell, 'dark', [(0.4, 0), (0.46, 0.5), (0.4, 1.0)], 10, m=T(cx, y0, cz), cap_top=True)
            else: bevel_box(shell, 'plank', 0.9, 0.9, 0.9, 0.04, m=M(T(cx, y0 + 0.45, cz), Ry(rng.uniform(0, 90))), col=tint(rng, 0.2))

# ------------------------------------------------------------------ floors: slabs, ceilings, colliders
def slabs():
    holes0 = well_holes() + SHAFTS
    flat_deck(shell, 'wetfloor', RECT, FL['lounge'] + 0.01, holes=[h for h in SHAFTS], under=None, uvs=3.2)      # wet muddy planks (owner's lounge concept)
    for k in range(1, NS + 1):
        y = YS[k]
        holes = holes0
        mat = 'dark' if KEYS[k] == 'hall' else ('bartop' if KEYS[k] == 'cards' else ('wetfloor' if KEYS[k] == 'roof' else 'plank'))     # roof: dark glossy terrace deck
        flat_deck(shell, mat, RECT, y, holes=holes, uvs=3.0, under='dark', th=0.45)
        slab_collider(col, y, ('p', RECT), holes=holes, pad=0.0)
        for i in range(1, BAYX):
            x = -X1 + 2 * X1 * i / BAYX
            if abs(x) > SW['xi'] - 0.3: continue
            bevel_box(shell, 'dark', 0.4, 0.55, 2 * Z1 - 0.5, 0.03, m=T(x, y - 0.45 - 0.27, 0), uvs=3.0)
        for s in (1, -1):
            bevel_box(shell, 'dark', 0.2, 0.45, SW['zm'] - SW['z0'], 0.02, m=T(s * SW['xi'], y - 0.22, (SW['zm'] + SW['z0']) / 2))
    # the gallery landing in the east core (x 34.4..42.1, z 9.5..29.6): the top of the Hall of Fakes stair opens onto it, the Grand Cage stops here
    G = [(BAND['xo'], SW['zm']), (X1, SW['zm']), (X1, Z1), (BAND['xo'], Z1)]
    gh = [h for h in SHAFTS if h[1][0][0] > 30 and h[1][0][1] > 5]
    y = FL['gallery']
    flat_deck(shell, 'plank', G, y, holes=gh, under='dark', th=0.4)
    slab_collider(col, y, ('p', G), holes=gh, pad=0.0)
    # the ramp carries on (owner: "the ramp should continue up to the next floor"): from the gallery landing a wide ramp climbs
    # through the east core (where the old front lift stood) onto the stair tower's half landing, and the stairs go on up to floor 3
    ym_hi = [ (c[0] + c[1]) / 2 for c in cycles() if c[0] < FL['cards'] - 0.1 and c[1] > FL['gallery'] + 0.1 ][0]     # the half landing above the gallery
    za, zb = SW['zm'] + 12.0, SW['zm']                    # foot of the ramp (on the gallery) -> top (at the half landing's edge)
    xa_, xb_ = BAND['xo'] + 0.05, X1 - 0.25
    P = np.array([[xa_, y, za], [xb_, y, za], [xb_, ym_hi, zb], [xa_, ym_hi, zb]])
    U = np.c_[P[:, 0] / 3.2, np.array([0, 0, 1, 1]) * np.linalg.norm(P[3] - P[0]) / 3.2]
    nrm = np.cross(P[1] - P[0], P[3] - P[0]); nrm /= np.linalg.norm(nrm); idx = [0, 1, 2, 0, 2, 3]
    if nrm[1] < 0: nrm = -nrm; idx = [0, 2, 1, 0, 3, 2]
    shell.add('plank', P + nrm * 0.02, [nrm] * 4, U, idx); shell.add('dark', P - nrm * 0.25, [-nrm] * 4, U, idx[::-1])
    ln = math.hypot(za - zb, ym_hi - y); ang = math.degrees(math.atan2(ym_hi - y, za - zb))
    collider_box(col, xb_ - xa_, 0.4, ln + 0.4, M(T((xa_ + xb_) / 2, (y + ym_hi) / 2 - 0.2, (za + zb) / 2), Rx(ang)))
    for k in range(9):                                     # cleats across the ramp so it reads as a boardwalk ramp
        t = (k + 0.5) / 9; zz = za + (zb - za) * t; yy = y + (ym_hi - y) * t
        box(shell, 'dark', xb_ - xa_ - 0.2, 0.05, 0.08, m=M(T((xa_ + xb_) / 2, yy + 0.05, zz), Rx(ang)))
    L['gallery_ramp'] = dict(y0=y, y1=ym_hi, z0=za, z1=zb)

# ------------------------------------------------------------------ the two stair towers (switchbacks, gentle ramps under the treads)
def flight(s, x_a, x_b, z_from, z_to, y_from, y_to):
    xa, xb = sorted((s * x_a, s * x_b)); w = xb - xa; xc = (xa + xb) / 2
    n = max(16, int(abs(y_to - y_from) / 0.17)); run = abs(z_to - z_from); dirn = 0 if z_to > z_from else 180
    stair(shell, xc, z_from, y_from, dirn, n, rise=(y_to - y_from) / n, tread=run / n, w=w - 0.3, rng=rng, rails=False)
    ln = math.hypot(run, y_to - y_from); ang = math.degrees(math.atan2(y_to - y_from, run)) * (1 if z_to > z_from else -1)
    collider_box(col, w, 0.3, ln + 0.3, M(T(xc, (y_from + y_to) / 2 - 0.12, (z_from + z_to) / 2), Rx(-ang)))
    bevel_box(shell, 'dark', w, 0.12, ln, 0.02, m=M(T(xc, (y_from + y_to) / 2 - 0.4, (z_from + z_to) / 2), Rx(-ang)), uvs=3.0)

def cycles():
    """every switchback (two flights) the stairs climb: [(y0, y1, landing_is_a_floor)] - tall storeys get two"""
    out = []
    for k in range(NS):
        y0, y1 = YS[k], YS[k + 1]; n = max(1, int(math.ceil((y1 - y0) / 8.6)))
        for c in range(n): out.append((y0 + (y1 - y0) * c / n, y0 + (y1 - y0) * (c + 1) / n, c == n - 1))
    return out

def stairs():
    for s in (1, -1):
        xa_, xb_ = sorted((s * SW['xi'], s * SW['xo']))
        for (y0, y1, top_is_floor) in cycles():
            ym = (y0 + y1) / 2
            flight(s, SW['xd'] + 0.1, SW['xo'], SW['z0'], SW['z1'], y0, ym)
            flight(s, SW['xi'], SW['xd'] - 0.1, SW['z1'], SW['z0'], ym, y1)
            P = [(xa_, SW['z1']), (xb_, SW['z1']), (xb_, SW['zm']), (xa_, SW['zm'])]
            flat_deck(shell, 'plank', P, ym, under='dark', th=0.3)
            collider_box(col, xb_ - xa_, 0.3, SW['zm'] - SW['z1'] + 0.2, T((xa_ + xb_) / 2, ym - 0.15, (SW['z1'] + SW['zm']) / 2))
            if not top_is_floor:     # a landing strip that is not a floor: its own little deck, walled in on the building side
                P = [(xa_, SW['zl']), (xb_, SW['zl']), (xb_, SW['z0']), (xa_, SW['z0'])]
                flat_deck(shell, 'plank', P, y1, under='dark', th=0.3)
                collider_box(col, xb_ - xa_, 0.3, SW['z0'] - SW['zl'] + 0.2, T((xa_ + xb_) / 2, y1 - 0.15, (SW['zl'] + SW['z0']) / 2))
                xw = s * SW['xi']
                in_hall = FL['hall'] - 0.5 < y1 < FL['cards']
                rustic_wall(*(((xw, SW['zl']), (xw, SW['z0'])) if s > 0 else ((xw, SW['z0']), (xw, SW['zl']))), y1, 3.6, [], battens=not in_hall, plates=not in_hall)
                collider_box(col, 0.45, 3.6, SW['z0'] - SW['zl'], T(xw, y1 + 1.8, (SW['zl'] + SW['z0']) / 2))
                # (v24, owner) and a wall on the lift side of the landing too (it was an open drop towards the lift lobby)
                zw = SW['zl'] - 0.12
                pa, pb = ((s * SW['xi'], zw), (s * SW['xo'], zw)) if s > 0 else ((s * SW['xo'], zw), (s * SW['xi'], zw))
                rustic_wall(pa, pb, y1 - 0.3, 3.9, [], battens=not in_hall, plates=not in_hall)
                collider_box(col, abs(SW['xo'] - SW['xi']), 3.9, 0.45, T(s * (SW['xo'] + SW['xi']) / 2, y1 - 0.3 + 1.95, zw))
            xd = s * SW['xd']
            pts = [(xd, y0 + (ym - y0) * t + 1.0, SW['z0'] + (SW['z1'] - SW['z0']) * t) for t in np.linspace(0, 1, 7)]
            tube(shell, 'pale', pts, 0.05, 8)
            for p in pts: box(shell, 'dark', 0.1, 1.0, 0.1, m=T(p[0], p[1] - 0.5, p[2]))
            tube(shell, 'pale', [(xd, ym + (y1 - ym) * t + 1.0, SW['z1'] + (SW['z0'] - SW['z1']) * t) for t in np.linspace(0, 1, 7)], 0.05, 8)
            # the rail between the two flights: a collider only as tall as the rail (owner: players can hop over it), one per flight
            for (ya, yb, za_, zb_) in ((y0, ym, SW['z0'], SW['z1']), (ym, y1, SW['z1'], SW['z0'])):
                ln_ = math.hypot(zb_ - za_, yb - ya); ang_ = math.degrees(math.atan2(yb - ya, zb_ - za_))
                collider_box(col, 0.2, 1.05, ln_, M(T(xd, (ya + yb) / 2 + 0.525, (za_ + zb_) / 2), Rx(-ang_)))
        # the back of the stair tower (z = zm, behind the half landings): a solid wall all the way up (owner: people walked off and fell)
        ramp_y = [(c[0] + c[1]) / 2 for c in cycles() if c[0] < FL['cards'] - 0.1 and c[1] > FL['gallery'] + 0.1][0]
        zb0 = SW['zm'] + 0.12
        p0, p1 = ((s * SW['xo'], zb0), (s * SW['xi'], zb0)) if s > 0 else ((s * SW['xi'], zb0), (s * SW['xo'], zb0))
        for k in range(NS):
            y0, h = YS[k], YS[k + 1] - YS[k]
            in_hall = KEYS[k] == 'hall'
            spans = [(y0, h)]
            if s > 0 and y0 < ramp_y < y0 + h:              # leave a doorway where the ramp from the Hall of Fakes reaches the landing
                spans = [(y0, ramp_y - y0), (ramp_y + 3.2, y0 + h - ramp_y - 3.2)]
            for (ya, hh) in spans:
                if hh < 0.2: continue
                rustic_wall(p0, p1, ya, hh, [], battens=not in_hall, plates=not in_hall)
                collider_box(col, abs(SW['xo'] - SW['xi']), hh, 0.45, T(s * (SW['xo'] + SW['xi']) / 2, ya + hh / 2, zb0))
        xa = s * SW['xi']
        for k in range(NS + 1):
            y0 = YS[k]; h = (YS[k + 1] - y0) if k < NS else 4.0
            p0, p1 = ((xa, SW['z0']), (xa, SW['zm'])) if s > 0 else ((xa, SW['zm']), (xa, SW['z0']))
            in_hall = KEYS[k] == 'hall' if k < len(KEYS) else False           # the Hall of Fakes portraits hang along this wall: no battens, no beams
            rustic_wall(p0, p1, y0, h, [], battens=not in_hall, plates=not in_hall)
            collider_box(col, 0.45, h, SW['zm'] - SW['z0'], T(xa, y0 + h / 2, (SW['z0'] + SW['zm']) / 2))
            # a lit STAIRS lamp over each stair door
            lathe(shell, 'glow', [(0.0, 0), (0.16, 0.05), (0.18, 0.3), (0.12, 0.45), (0.0, 0.48)], 10, m=T(xa - s * 0.35, y0 + 4.0, (SW['zl'] + SW['z0']) / 2 + 2.3))
        # roof stair-house
        y0 = YS[NS]; h = 4.0; xo = s * (X1 - 0.2)
        for (p0, p1) in (((xa, SW['zl']), (xo, SW['zl'])), ((xa, SW['zm']), (xo, SW['zm'])), ((xo, SW['zl']), (xo, SW['zm']))):
            rustic_wall(p0, p1, y0, h, [])
            mm, ln = place(p0, p1, y0); collider_box(col, ln, h, 0.45, M(mm, T(ln / 2, h / 2, 0)))
        xs = sorted((xa, xo))
        za, zb = SW['zl'] - 0.6, SW['zm'] + 0.6; xin, xout = xs[0] - 0.6, xs[1] + 0.6
        ridge = y0 + h + 2.4
        for zz0, zz1 in ((za, (za + zb) / 2), (zb, (za + zb) / 2)):
            P = np.array([[xin, y0 + h, zz0], [xout, y0 + h, zz0], [xout, ridge, zz1], [xin, ridge, zz1]])
            nrm = np.cross(P[1] - P[0], P[3] - P[0]); nrm /= np.linalg.norm(nrm)
            idx = [0, 1, 2, 0, 2, 3]
            if nrm[1] < 0: nrm = -nrm; idx = [0, 2, 1, 0, 3, 2]
            U = np.c_[P[:, 0] / 4, np.array([0, 0, 1, 1]) * np.linalg.norm(P[3] - P[0]) / 4]
            shell.add('shingle', P, [nrm] * 4, U, idx); shell.add('dark', P - nrm * 0.1, [-nrm] * 4, U, idx[::-1])
        for zz in (SW['zl'], SW['zm']):
            tri = np.array([[xs[0], y0 + h, zz], [xs[1], y0 + h, zz], [(xs[0] + xs[1]) / 2, ridge - 0.3, zz]])
            shell.add('dark', tri, [[0, 0, 1]] * 3, [[0, 0], [2, 0], [1, 1]], [0, 1, 2, 0, 2, 1])

# ------------------------------------------------------------------ the roof: a shingle mansard skirt with dormers, chimneys, a water tower, the lift house + steeple
def roof():
    y = YS[NS]
    pent(y + 1.4, y - 2.2, 3.4)                     # the big mansard skirt
    # dormers sitting on the skirt along the front and back
    for side, zs in (('front', 1), ('back', -1)):
        for x in ((-46.0, 46.0) if zs > 0 else (-46.0, -31.0, 31.0, 46.0)):     # (v23) the front's middle dormers make way for the gables
            zc = zs * (Z1 + 1.4); yb = y - 0.9
            mm = M(T(x, yb, zc), Ry(0 if zs > 0 else 180))
            rustic_wall_local(mm, 2.8, 2.6)
            window(shell, 1.1, 1.3, M(mm, T(0, 1.3, 0.18)), rng, shutters=False, mull=(2, 2))
            for sx in (-1, 1):
                P = np.array([(mm @ np.array([0, 3.9, 0.3, 1]))[:3], (mm @ np.array([0, 3.9, -2.4, 1]))[:3], (mm @ np.array([sx * 1.8, 2.5, -2.4, 1]))[:3], (mm @ np.array([sx * 1.8, 2.5, 0.3, 1]))[:3]])
                nrm = np.cross(P[1] - P[0], P[3] - P[0]); nrm /= np.linalg.norm(nrm); idx = [0, 1, 2, 0, 2, 3]
                if nrm[1] < 0: nrm = -nrm; idx = [0, 2, 1, 0, 3, 2]
                shell.add('shingle', P, [nrm] * 4, [[0, 0], [1, 0], [1, 1], [0, 1]], idx, col=tint(rng, 0.1, 0.9))
                shell.add('dark', P - nrm * 0.08, [-nrm] * 4, [[0, 0], [1, 0], [1, 1], [0, 1]], idx[::-1])
            tri = np.array([(mm @ np.array([-1.4, 2.6, 0.12, 1]))[:3], (mm @ np.array([1.4, 2.6, 0.12, 1]))[:3], (mm @ np.array([0, 3.85, 0.12, 1]))[:3]])
            shell.add('dark', tri, [[0, 0, 1]] * 3, [[0, 0], [1, 0], [0.5, 1]], [0, 1, 2, 0, 2, 1])
    o = 0.2
    R0 = [(-X1 + o, -Z1 + o), (X1 - o, -Z1 + o), (X1 - o, Z1 - o), (-X1 + o, Z1 - o)]
    railing(shell, R0, y, rng, closed=True, rope_mat='rope', balusters=False, post_every=2.6)
    for i in range(4): col_between(R0[i], R0[(i + 1) % 4], y, 1.3, 0.3)
    # mud-stone chimneys and a water tower
    for (x, z) in ((-40.0, 31.0), (40.0, -17.0)):
        for kk in range(6):
            w_ = 1.9 - 0.06 * kk
            bevel_box(shell, 'mud', w_, 0.9, w_, 0.06, m=T(x + rng.uniform(-0.05, 0.05), y + 0.45 + kk * 0.9, z), uvs=1.5)
        bevel_box(shell, 'dark', 2.2, 0.3, 2.2, 0.04, m=T(x, y + 5.5, z))
        collider_box(col, 1.9, 5.6, 1.9, T(x, y + 2.8, z))
    wx, wz = 42.0, 25.0
    for (dx, dz) in ((-1.4, -1.4), (1.4, -1.4), (1.4, 1.4), (-1.4, 1.4)):
        cyl(shell, 'bark', 0.18, 6.0, 8, m=M(T(wx + dx, y, wz + dz), Rz(dx * 1.5), Rx(-dz * 1.5)))
        collider_box(col, 0.4, 6.0, 0.4, T(wx + dx, y + 3.0, wz + dz))
    bevel_box(shell, 'plank', 3.6, 0.2, 3.6, 0.03, m=T(wx, y + 6.0, wz))
    lathe(shell, 'plank', [(1.75, y + 6.1), (1.85, y + 7.0), (1.85, y + 9.0), (1.75, y + 9.8)], 20, m=T(wx, 0, wz), cap_top=True, uvs_u=4)
    for yy in (6.5, 8.2, 9.5): lathe(shell, 'iron', [(1.87, y + yy), (1.87, y + yy + 0.08)], 20, m=T(wx, 0, wz))
    lathe(shell, 'shingle', [(2.2, y + 9.8), (0.0, y + 11.4)], 16, m=T(wx, 0, wz))
    # the lift-head houses at the ends, over each cage's machinery
    SAp, DWp, DHp = L['shaft_apo'], L['door_w'], L['door_h']; HH = 11.0          # (v24) sized for the bigger lifts, tall enough for the machinery
    for (_, _, lx, lz, _) in LIFTS:
        xa_, xb_, za_, zb_ = lx - SAp - 0.8, lx + SAp + 0.8, lz - SAp - 1.7, lz + SAp + 2.2
        xa_, xb_ = max(xa_, -X1 + 0.3), min(xb_, X1 - 0.3)
        for wi, (p0, p1) in enumerate((((xa_, za_), (xb_, za_)), ((xb_, za_), (xb_, zb_)), ((xb_, zb_), (xa_, zb_)), ((xa_, zb_), (xa_, za_)))):
            mm, ln = place(p0, p1, y)
            front = (wi == 2)                      # (owner) the front faces the lift doors: a doorway out onto the roof deck
            dx = abs(p0[0] - lx)                   # where the lift's centre falls along this wall (it runs from p0)
            holes = [(dx, (DHp + 0.4) / 2, DWp + 1.0, DHp + 0.4)] if front else [(ln / 2, 6.5, 1.6, 2.0)]
            rustic_wall(p0, p1, y, HH, holes)
            if front:
                for (c0, c1) in ((0.0, dx - (DWp + 1.0) / 2), (dx + (DWp + 1.0) / 2, ln)):
                    if c1 - c0 > 0.05: collider_box(col, c1 - c0, HH, 0.45, M(mm, T((c0 + c1) / 2, HH / 2, 0)))
                collider_box(col, DWp + 1.0, HH - DHp - 0.4, 0.45, M(mm, T(dx, DHp + 0.4 + (HH - DHp - 0.4) / 2, 0)))
                bevel_box(shell, 'dark', DWp + 1.4, 0.35, 0.35, 0.03, m=M(mm, T(dx, DHp + 0.55, 0.12)), uvs=2.0)      # a lintel over the doorway
            else:
                window(shell, 1.6, 2.0, M(mm, T(ln / 2, 6.5, 0)), rng, shutters=False, mull=(2, 2))
                collider_box(col, ln, HH, 0.45, M(mm, T(ln / 2, HH / 2, 0)))
        P = np.array([[xa_ - 0.5, y + HH, za_ - 0.5], [xb_ + 0.5, y + HH, za_ - 0.5], [xb_ + 0.5, y + HH, zb_ + 0.5], [xa_ - 0.5, y + HH, zb_ + 0.5]])
        for i in range(4):
            tri = np.array([P[i], P[(i + 1) % 4], [lx, y + HH + 2.4, (za_ + zb_) / 2]])
            nrm = np.cross(tri[1] - tri[0], tri[2] - tri[0]); nrm /= np.linalg.norm(nrm)
            idx = [0, 1, 2] if nrm[1] > 0 else [0, 2, 1]
            shell.add('shingle', tri, [nrm if nrm[1] > 0 else -nrm] * 3, [[0, 0], [2, 0], [1, 1]], idx)
    # the steeple house (it used to hold the lift machinery)
    xa, xb, za, zb = -21.0, 21.0, -(Z1 - 0.4), -(Z1 - 11.0)
    hh = 9.5
    for (p0, p1) in (((xa, zb), (xb, zb)), ((xb, za), (xb, zb)), ((xa, za), (xa, zb))):
        mm, ln = place(p0, p1, y)
        nwin = max(1, int(ln / 5.2))
        wins = [(ln * (j + 0.5) / nwin, 4.8, 3.6, 5.4) for j in range(nwin)]
        rustic_wall(p0, p1, y, hh, wins)
        for (hx, hy, hw, hh_) in wins: window(shell, hw, hh_, M(mm, T(hx, hy, 0)), rng, shutters=False, mull=(3, 3))
        collider_box(col, ln, hh, 0.45, M(mm, T(ln / 2, hh / 2, 0)))
    flat_deck(shell, 'dark', [(xa, za), (xb, za), (xb, zb), (xa, zb)], y + hh, under='plank', th=0.3)
    collider_box(col, xb - xa, 0.4, zb - za, T(0, y + hh + 0.2, (za + zb) / 2))
    cx, cz = 0.0, (za + zb) / 2
    tiers = [(20.0, 9.0, y + hh, 7.0), (14.0, 7.0, y + hh + 7.0, 7.5), (9.0, 5.0, y + hh + 14.5, 8.5), (5.0, 3.4, y + hh + 23.0, 9.0)]
    for (w0, w1, ty, th_) in tiers:
        d0 = w0 * 0.55; d1 = w1 * 0.55
        c0 = [(cx - w0 / 2, cz - d0 / 2), (cx + w0 / 2, cz - d0 / 2), (cx + w0 / 2, cz + d0 / 2), (cx - w0 / 2, cz + d0 / 2)]
        c1 = [(cx - w1 / 2, cz - d1 / 2), (cx + w1 / 2, cz - d1 / 2), (cx + w1 / 2, cz + d1 / 2), (cx - w1 / 2, cz + d1 / 2)]
        for i in range(4):
            P = np.array([[c0[i][0], ty, c0[i][1]], [c0[(i + 1) % 4][0], ty, c0[(i + 1) % 4][1]], [c1[(i + 1) % 4][0], ty + th_, c1[(i + 1) % 4][1]], [c1[i][0], ty + th_, c1[i][1]]])
            nrm = np.cross(P[1] - P[0], P[3] - P[0]); nrm /= np.linalg.norm(nrm)
            idx = [0, 1, 2, 0, 2, 3]
            if np.dot(nrm, np.array([P[0][0] - cx, 0, P[0][2] - cz])) < 0: nrm = -nrm; idx = [0, 2, 1, 0, 3, 2]
            wl = np.linalg.norm(P[1] - P[0]); dl = np.linalg.norm(P[3] - P[0])
            U = np.array([[0, 0], [wl / 3, 0], [wl / 3, dl / 3], [0, dl / 3]])
            shell.add('shingle', P, [nrm] * 4, U, idx, col=tint(rng, 0.1, 0.85))
        for sz in (1, -1):
            window(shell, min(2.4, w1 * 0.4), th_ * 0.4, M(T(cx, ty + th_ * 0.45, cz + sz * (d0 + d1) / 4 + sz * 0.15), Ry(0 if sz > 0 else 180)), rng, shutters=False)
        for i in range(4): box_between(shell, 'dark', c0[i], c0[(i + 1) % 4], 0.3, 0.35, ty + 0.1)
        for i in range(4):     # moss along each tier's eave
            a, b = c0[i], c0[(i + 1) % 4]
            tube(shell, 'moss', [(a[0], ty + 0.3, a[1]), (b[0], ty + 0.3, b[1])], 0.16, 5)
    top = y + hh + 32.0
    lathe(shell, 'dark', [(0.0, top), (2.6, top), (2.8, top + 0.3), (2.8, top + 1.4), (2.5, top + 1.5), (0.0, top + 1.5)], 12, m=T(cx, 0, cz))
    for a in range(0, 360, 30):
        p = (cx + 2.7 * math.sin(math.radians(a)), cz + 2.7 * math.cos(math.radians(a)))
        cyl(shell, 'dark', 0.08, 1.2, 5, m=T(p[0], top + 1.5, p[1]))
    tube(shell, 'pale', [(cx + 2.7 * math.sin(math.radians(a)), top + 2.7, cz + 2.7 * math.cos(math.radians(a))) for a in range(0, 361, 15)], 0.07, 6)
    lathe(shell, 'shingle', [(3.0, top + 2.9), (0.0, top + 9.0)], 12, m=T(cx, 0, cz))
    cyl(shell, 'iron', 0.1, 9.0, 6, m=T(cx, top + 9.0, cz))
    sphere(shell, 'glow', 0.45, 12, 8, m=T(cx, top + 18.2, cz))
    L['steeple_top'] = top + 18.2; L['nest'] = [cx, top + 1.5, cz]

def gable_spots():
    """(v23) three swamp-timber gables along the front roof edge (Meshy models placed by outside.py); here only where they stand + colliders.
    The owner turned down the castle look (turrets, iron spires) - these are rustic bayou-lodge gables."""
    y = YS[NS]; L['gables'] = []
    for (gx, gw) in ((0.0, 18.0), (-31.0, 12.0), (31.0, 12.0)):
        gd = gw * 0.75
        L['gables'].append([gx, y, Z1 - 0.3, gw])
        collider_box(col, gw * 0.9, gw * 0.45, gd * 0.8, T(gx, y + gw * 0.225, Z1 - 0.3 - gd * 0.45))
        # (v24, owner: "floating structures") the Meshy gable is only a roof - its eaves hang ~3 m over the deck with moss underneath.
        # Timber knee walls fill the space under the eaves so each gable is a little attic lodge standing ON the roof.
        try:
            gm, gM = json.load(open('out/glb/meshy_meta.json'))['gable']
        except Exception:
            continue
        s_ = gw / (gM[0] - gm[0]); d_ = (gM[2] - gm[2]) * s_
        cx_, cz_ = gx, (Z1 - 0.3) - d_ / 2 + 0.6                       # where outside.py centres the model's footprint
        hw_, hz_ = 0.70 * s_, 0.80 * s_                                 # tucked inside the eaves (model eave reach ~0.78 x, ~0.85 z)
        wh_ = (-0.24 - gm[1]) * s_ - 0.3                                # from the deck up into the underside of the roof (model base sits 0.3 below)
        xa_, xb_, za_, zb_ = cx_ - hw_, cx_ + hw_, cz_ - hz_, cz_ + hz_
        for wi, (p0, p1) in enumerate((((xa_, za_), (xb_, za_)), ((xb_, za_), (xb_, zb_)), ((xb_, zb_), (xa_, zb_)), ((xa_, zb_), (xa_, za_)))):
            mm, ln = place(p0, p1, y)
            ww_, wwh = min(2.2, ln * 0.22), min(1.6, wh_ * 0.45)
            rustic_wall(p0, p1, y, wh_, [(ln / 2, wh_ * 0.55, ww_, wwh)])
            window(shell, ww_, wwh, M(mm, T(ln / 2, wh_ * 0.55, 0)), rng, shutters=False, mull=(2, 1))
            bevel_box(shell, 'dark', ln + 0.3, 0.32, 0.32, 0.03, m=M(mm, T(ln / 2, wh_ - 0.2, 0.1)), uvs=2.0)     # a top plate where wall meets roof
            for u in (0.0, ln):
                bevel_box(shell, 'dark', 0.36, wh_, 0.36, 0.03, m=M(mm, T(u, wh_ / 2, 0.0)), uvs=2.0)             # corner posts

def gothic_front_unused():
    """(v23, owner's concept) a gothic roofline on the front: three steep gables with tall pointed glowing windows, carved bargeboards and
    iron spires; slender octagonal turrets with tall cone roofs between them and at the corners; moss trailing off every edge"""
    y = YS[NS]; zf = Z1 - 0.2
    def slope(P, mat='shingle'):
        P = np.array(P); nrm = np.cross(P[1] - P[0], P[3] - P[0]); nrm /= np.linalg.norm(nrm); idx = [0, 1, 2, 0, 2, 3]
        if nrm[1] < 0: nrm = -nrm; idx = [0, 2, 1, 0, 3, 2]
        wl = np.linalg.norm(P[1] - P[0]); dl = np.linalg.norm(P[3] - P[0])
        shell.add(mat, P, [nrm] * 4, [[0, 0], [wl / 3, 0], [wl / 3, dl / 3], [0, dl / 3]], idx, col=tint(rng, 0.1, 0.85))
        shell.add('dark', P - nrm * 0.1, [-nrm] * 4, [[0, 0], [1, 0], [1, 1], [0, 1]], idx[::-1])
    def spire(x, yb, z, h, r=0.12):
        lathe(shell, 'iron', [(r * 2.2, yb), (r * 1.4, yb + 0.25), (r * 1.6, yb + 0.5), (r, yb + 0.7), (r * 0.6, yb + h * 0.75), (0.0, yb + h)], 8, m=T(x, 0, z))
        sphere(shell, 'glow', r * 2.0, 8, 6, m=T(x, yb + h * 0.55, z))
    for (gx, gw, gd) in ((0.0, 15.0, 9.0), (-23.0, 10.0, 7.0), (23.0, 10.0, 7.0)):
        hw = 3.2; ha = gw * 0.85                                  # wall height, then a steep triangle
        mm = M(T(gx, y, zf), Ry(0))
        rustic_wall_local(mm, gw, hw)
        x = -gw / 2                                               # the triangle, boarded vertically
        while x < gw / 2 - 0.02:
            bw = min(gw / 2 - x, rng.uniform(0.22, 0.4)); xc = x + bw / 2
            top = hw + ha * (1 - abs(xc) / (gw / 2))
            if top - hw > 0.05: box(shell, 'plank', bw - 0.015, top - hw, 0.08, m=M(mm, T(xc, hw + (top - hw) / 2, 0)), col=tint(rng, 0.22), uvs=3.0, faces='zZ')
            x += bw
        ww = gw * 0.26; wh = (hw + ha) * 0.62                     # a tall pointed glowing window
        window(shell, ww, wh, M(mm, T(0, hw * 0.45 + wh / 2, 0.06)), rng, shutters=False, mull=(2, 4), arch=True)
        for sx in (-1, 1):
            window(shell, ww * 0.55, wh * 0.45, M(mm, T(sx * gw * 0.33, hw * 0.4 + wh * 0.22, 0.06)), rng, shutters=False, mull=(1, 3), arch=True)
        apex = (gx, y + hw + ha, zf); back = zf - gd
        for sx in (-1, 1):                                        # the two roof slopes, running back
            e0 = (gx + sx * (gw / 2 + 0.5), y + hw - 0.35, zf + 0.5)
            slope([[e0[0], e0[1], e0[2]], [apex[0], apex[1] + 0.3, zf + 0.5], [apex[0], apex[1] + 0.3, back], [e0[0], e0[1], back]])
            # carved bargeboard along the gable edge, moss trailing off it
            pts = [(gx + sx * (gw / 2 + 0.5) * (1 - t), y + hw - 0.35 + (ha + 0.65) * t, zf + 0.55) for t in np.linspace(0, 1, 7)]
            tube(shell, 'dark', pts, 0.16, 6)
            for t in np.linspace(0.1, 0.9, 6):
                q = (gx + sx * (gw / 2 + 0.5) * (1 - t), y + hw - 0.5 + (ha + 0.65) * t, zf + 0.6); hh = rng.uniform(0.6, 2.2)
                tube(shell, 'moss', [q, (q[0] + rng.uniform(-0.1, 0.1), q[1] - hh / 2, q[2] + 0.05), (q[0], q[1] - hh, q[2])], 0.06, 4, radii=[0.12, 0.07, 0.02])
            spire(gx + sx * (gw / 2 + 0.4), y + hw - 0.3, zf + 0.5, 3.4, 0.1)        # pinnacles at the eaves
        for sx in (-1, 1):                                        # side walls under the slopes (closing the gable)
            P = np.array([[gx + sx * gw / 2, y, zf], [gx + sx * gw / 2, y, back], [gx + sx * gw / 2, y + hw, back], [gx + sx * gw / 2, y + hw, zf]])
            shell.add('plank', P, [[sx, 0, 0]] * 4, np.c_[P[:, 2] / 0.35, P[:, 1] / 3.0], [0, 1, 2, 0, 2, 3] if sx < 0 else [0, 2, 1, 0, 3, 2])
        spire(gx, apex[1] + 0.2, zf + 0.5, gw * 0.42, 0.16)      # the iron spire on the apex
        collider_box(col, gw, hw + ha * 0.5, gd, T(gx, y + (hw + ha * 0.5) / 2, zf - gd / 2))
    for (tx, rr, th) in ((-12.5, 1.3, 9.0), (12.5, 1.3, 9.0), (-X1 + 1.6, 1.8, 11.0), (X1 - 1.6, 1.8, 11.0), (-31.5, 1.1, 7.5), (31.5, 1.1, 7.5)):
        tz = zf - rr - 0.2
        lathe(shell, 'plank', [(rr, y), (rr, y + th)], 8, m=M(T(tx, 0, tz), Ry(22.5)), uvs_u=3, smooth=False)
        for yy in (y + 0.2, y + th * 0.5, y + th - 0.2): lathe(shell, 'dark', [(rr + 0.08, yy - 0.12), (rr + 0.08, yy + 0.12)], 8, m=M(T(tx, 0, tz), Ry(22.5)), smooth=False)
        for a in range(0, 360, 90):
            window(shell, rr * 0.55, th * 0.3, M(T(tx + (rr + 0.02) * math.sin(math.radians(a)), y + th * 0.62, tz + (rr + 0.02) * math.cos(math.radians(a))), Ry(a)), rng, shutters=False, mull=(1, 2), arch=True)
        lathe(shell, 'shingle', [(rr + 0.45, y + th), (rr * 0.7, y + th + th * 0.35), (0.0, y + th + th * 0.95)], 8, m=M(T(tx, 0, tz), Ry(22.5)), smooth=False)
        spire(tx, y + th + th * 0.9, tz, 2.6, 0.08)
        tube(shell, 'moss', [(tx + (rr + 0.4) * math.sin(math.radians(a)), y + th - 0.1, tz + (rr + 0.4) * math.cos(math.radians(a))) for a in range(0, 361, 30)], 0.13, 5)
        collider_box(col, rr * 2, th, rr * 2, T(tx, y + th / 2, tz))

def rustic_wall_local(mm, w, h):
    x = -w / 2
    while x < w / 2 - 0.02:
        bw = min(w / 2 - x, rng.uniform(0.2, 0.4))
        box(shell, 'plank', bw - 0.015, h, 0.08, m=M(mm, T(x + bw / 2, h / 2, 0)), col=tint(rng, 0.22), uvs=3.0, faces='zZ')
        x += bw

def portico():
    """the grand entrance: four cypress columns, a gabled shingle roof and the MUDWATER board, over the front doors"""
    y0 = FL['lounge']; z0, z1 = Z1, Z1 + 9.0; w = 16.0; hcol = 7.2
    for x in (-w / 2, w / 2):                    # only the two outer columns - the middle of the porch stays open for the doors
        prof = [(0.55 + 0.2 * math.exp(-t * 6), hcol * t) for t in np.linspace(0, 1, 8)]
        lathe(shell, 'bark', prof, 12, m=T(x, y0, z1 - 0.6), uv_v=3.0)
        lathe(shell, 'moss', [(0.75, 0), (0.6, 0.6)], 12, m=T(x, y0, z1 - 0.6))
        collider_box(col, 1.1, hcol, 1.1, T(x, y0 + hcol / 2, z1 - 0.6))
    # beam + gable roof
    bevel_box(shell, 'dark', w + 1.6, 0.7, 0.8, 0.04, m=T(0, y0 + hcol + 0.35, z1 - 0.6), uvs=3.0)
    for s in (-1, 1): bevel_box(shell, 'dark', 0.6, 0.7, z1 - z0, 0.04, m=T(s * (w / 2 + 0.5), y0 + hcol + 0.35, (z0 + z1) / 2), uvs=3.0)
    ridge = y0 + hcol + 5.2; eave = y0 + hcol + 0.7
    for s in (-1, 1):
        P = np.array([[0, ridge, z0], [0, ridge, z1 + 0.6], [s * (w / 2 + 1.4), eave, z1 + 0.6], [s * (w / 2 + 1.4), eave, z0]])
        nrm = np.cross(P[1] - P[0], P[3] - P[0]); nrm /= np.linalg.norm(nrm)
        idx = [0, 1, 2, 0, 2, 3]
        if nrm[1] < 0: nrm = -nrm; idx = [0, 2, 1, 0, 3, 2]
        U = np.array([[0, 0], [(z1 - z0) / 3, 0], [(z1 - z0) / 3, 3], [0, 3]])
        shell.add('shingle', P, [nrm] * 4, U, idx); shell.add('dark', P - nrm * 0.12, [-nrm] * 4, U, idx[::-1])
    tri = np.array([[-w / 2 - 1.4, eave, z1 + 0.6], [w / 2 + 1.4, eave, z1 + 0.6], [0, ridge, z1 + 0.6]])
    shell.add('dark', tri, [[0, 0, 1]] * 3, [[0, 0], [4, 0], [2, 1.5]], [0, 1, 2])
    shell.add('dark', tri + np.array([0, 0, -0.1]), [[0, 0, -1]] * 3, [[0, 0], [4, 0], [2, 1.5]], [0, 2, 1])
    tube(shell, 'moss', [(0, ridge + 0.1, z0), (0, ridge + 0.1, z1 + 0.6)], 0.22, 6)
    # gilt sunburst in the gable
    for k in range(9):
        a = math.radians(-80 + k * 20)
        tube(shell, 'gold', [(0, eave + 0.4, z1 + 0.68), (3.2 * math.sin(a), eave + 0.4 + 3.2 * math.cos(a) * 0.95, z1 + 0.68)], 0.06, 5)
    lathe(shell, 'gold', [(0.0, 0.0), (0.7, 0.0), (0.7, 0.05), (0.0, 0.05)], 20, m=M(T(0, eave + 0.4, z1 + 0.66), Rx(90)))
    L['portico'] = dict(z=z1 + 0.75, y=eave - 1.6, w=w)

def lift_lobby_trim():
    """carved timber surround framing the lift bank on every floor"""
    for k in range(NS + 1):
        y = YS[k]
        bevel_box(shell, 'dark', 42.0, 0.6, 0.6, 0.04, m=T(0, y + 3.8, -22.4), uvs=3.0)
        for x in (-20.6, -10, 0, 10, 20.6):
            bevel_box(shell, 'dark', 0.6, 3.8, 0.6, 0.04, m=T(x, y + 1.9, -22.4), uvs=2.0)
        quad(shell, 'gold', 6.0, 0.35, T(0, y + 3.8, -22.08))

NEON = dict(MATS)
NEON['neon_t'] = dict(color=(0.3, 1.0, 0.85, 1), emis=(0.3, 1.0, 0.85), emis_strength=2.5, unlit=True)
NEON['neon_g'] = dict(color=(1.0, 0.75, 0.25, 1), emis=(1.0, 0.72, 0.2), emis_strength=2.5, unlit=True)
NEON['bulb'] = dict(color=(1.0, 0.85, 0.5, 1), emis=(1.0, 0.8, 0.4), emis_strength=3.0, unlit=True)
neonm = Mesh()
def neon():
    """glowing teal tubes under every eave, gold on the steeple, string lights on the lower eaves, glowing mud round the porch"""
    def ring_rect(o, y, mat, r=0.06):
        R0 = [(-X1 - o, -Z1 - o), (X1 + o, -Z1 - o), (X1 + o, Z1 + o), (-X1 - o, Z1 + o)]
        for i in range(4):
            a, b = R0[i], R0[(i + 1) % 4]
            tube(neonm, mat, [(a[0], y, a[1]), (b[0], y, b[1])], r, 6)
        return R0
    # warm string lights sagging under every eave (the swamp's own festival lights - no neon)
    lines = [(YS[k], 2.4) for k in range(1, NS)] + [(FL['gallery'] - 7.2, 2.4), (FL['gallery'], 2.4), (YS[NS] - 1.85, 3.4)]
    for (y, depth) in lines:
        R0 = [(-X1 - depth + 0.3, -Z1 - depth + 0.3), (X1 + depth - 0.3, -Z1 - depth + 0.3), (X1 + depth - 0.3, Z1 + depth - 0.3), (-X1 - depth + 0.3, Z1 + depth - 0.3)]
        for i in range(4):
            a, b = np.array(R0[i]), np.array(R0[(i + 1) % 4]); ln = np.linalg.norm(b - a); n = int(ln / 5.3)
            for k in range(n):
                p0 = a + (b - a) * k / n; p1 = a + (b - a) * (k + 1) / n
                pts = [(p0[0] + (p1[0] - p0[0]) * u, y - 0.75 - 0.55 * math.sin(math.pi * u), p0[1] + (p1[1] - p0[1]) * u) for u in np.linspace(0, 1, 7)]
                tube(neonm, 'dark', pts, 0.012, 3)
                for p in pts[1:-1]: sphere(neonm, 'bulb', 0.1, 5, 3, m=T(p[0], p[1] - 0.1, p[2]))
    # bulbs down the steeple's tier edges
    y = YS[NS]; hh = 9.5; cx, cz = 0.0, (-(Z1 - 0.4) - (Z1 - 11.0)) / 2
    tiers = [(20.0, 9.0, y + hh, 7.0), (14.0, 7.0, y + hh + 7.0, 7.5), (9.0, 5.0, y + hh + 14.5, 8.5), (5.0, 3.4, y + hh + 23.0, 9.0)]
    for (w0, w1, ty, th_) in tiers:
        d0 = w0 * 0.55; d1 = w1 * 0.55
        c0 = [(cx - w0 / 2, cz - d0 / 2), (cx + w0 / 2, cz - d0 / 2), (cx + w0 / 2, cz + d0 / 2), (cx - w0 / 2, cz + d0 / 2)]
        c1 = [(cx - w1 / 2, cz - d1 / 2), (cx + w1 / 2, cz - d1 / 2), (cx + w1 / 2, cz + d1 / 2), (cx - w1 / 2, cz + d1 / 2)]
        for i in range(4):
            for u in np.linspace(0, 1, 9)[1:-1]:
                p = np.array(c0[i]) + (np.array(c0[(i + 1) % 4]) - np.array(c0[i])) * u
                sphere(neonm, 'bulb', 0.12, 5, 3, m=T(p[0], ty + 0.1, p[1]))
            for u in np.linspace(0, 1, 7):
                p = np.array(c0[i]) + (np.array(c1[i]) - np.array(c0[i])) * u
                sphere(neonm, 'bulb', 0.11, 5, 3, m=T(p[0], ty + th_ * u, p[1]))
    # glowing mud channel round the porch, inside the rail, and down both edges of the boardwalk
    P = PORCH; o = 0.6
    for (a, b) in (((-P['x'] + o, P['zb'] + o), (P['x'] - o, P['zb'] + o)), ((P['x'] - o, P['zb'] + o), (P['x'] - o, P['zf'] - o)), ((-P['x'] + o, P['zb'] + o), (-P['x'] + o, P['zf'] - o)),
                   ((-P['x'] + o, P['zf'] - o), (-WALK['w'] / 2 - 0.5, P['zf'] - o)), ((WALK['w'] / 2 + 0.5, P['zf'] - o), (P['x'] - o, P['zf'] - o))):
        mm, ln = place(a, b, FL['lounge'] + 0.015)
        pass      # (glowing mud strip removed - the concept has a plain wet boardwalk)
    for sx in (-1, 1):
        x = sx * (WALK['w'] / 2 - 0.35)
        P2 = np.array([[x - 0.15, FL['lounge'] + 0.02, WALK['z0']], [x + 0.15, FL['lounge'] + 0.02, WALK['z0']], [x + 0.15, WALK['y1'] + 0.02, WALK['z1']], [x - 0.15, WALK['y1'] + 0.02, WALK['z1']]])
        pass

if __name__ == '__main__':
    porch(); boardwalk(); walls(); belts(); balconies(); shacks(); slabs(); stairs(); roof(); gable_spots(); portico()
    print('shell', write(OUT + 'sp_shell.glb', shell, MATS))
    print('col', write(OUT + 'sp_shell_col.glb', col, MATS))
    print('walk', write(OUT + 'sp_boardwalk.glb', walkm, MATS))
    neon(); print('neon', write(OUT + 'sp_neon.glb', neonm, NEON))
    json.dump(L, open('/home/claude/spire/out/layout.json', 'w'))
