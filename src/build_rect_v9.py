"""MUDWATER SPIRE v2 - the rectangular swamp hall (85 x 60 m), four storeys + roof deck + steeple.
Building space: centre (0, 0, 0), water at y 0.1, the front (+z) faces the boardwalk.
  F1 lounge 3.0 | F2 Mud Match gallery 10.5 | F3 card floor 19.0 | F4 Group Mud rooms 26.5 | roof deck 34.0
Two stair towers at the short ends (x = +-34.4 .. 42.1, z = -9.5 .. 9.5), a bank of four lifts against the back wall.
Writes sp_shell.glb, sp_shell_col.glb, sp_boardwalk.glb, out/layout.json."""
import math, json, random
import numpy as np
from glb import *
from kit import *

OUT = '/home/claude/spire/out/glb/'
rng = random.Random(85)
X1, Z1 = 42.5, 30.0                         # outer wall lines (half sizes)
FL = dict(lounge=3.0, match=10.5, cards=19.0, rooms=26.5, roof=34.0)
KEYS = ['lounge', 'match', 'cards', 'rooms', 'roof']
YS = [FL[k] for k in KEYS]
PORCH = dict(x=50.0, zb=-37.0, zf=42.0)    # porch deck round the building (front plaza is deeper)
WALK = dict(w=8.0, z0=42.0, z1=108.0, y1=0.6)
# stair wells (east one; the west one is the mirror):  landing strip z -9.5..-6 is floor, the rest of the well is open
SW = dict(xi=34.4, xd=38.4, xo=42.1, zl=-9.5, z0=-6.0, z1=6.0, zm=9.5)
LIFTX = [-15.0, -5.0, 5.0, 15.0]; LIFTZ = -25.0
L = dict(FL=FL, keys=KEYS, X1=X1, Z1=Z1, porch_box=PORCH, walk=WALK, sw=SW,
         porch=FL['lounge'], f2=FL['match'], f3=FL['cards'], f4=FL['rooms'], roof=FL['roof'],
         walk_y=WALK['y1'], walk_len=WALK['z1'] - WALK['z0'], walk_w=WALK['w'], walk_z0=WALK['z0'],
         stop_names={'%.1f' % FL[k]: k for k in KEYS},
         lifts=[dict(id=i, name=n, x=x, z=LIFTZ, stops=YS) for i, n, x in zip('ABCD', ['The Grand Cage', 'The Gator Cage', 'The Heron Cage', 'The Lucky Cage'], LIFTX)],
         shaft_apo=2.3, cab_apo=2.05, shaft_base=FL['lounge'], shaft_top=FL['roof'] + 5.6, door_w=1.6, door_h=2.9,
         floors_through=YS[1:])
_c = octa(L['shaft_apo'])
L['shaft_fp'] = [[round(x, 4), round(z if z > -2.0 or abs(x) > 1.5 else -2.95, 4)] for (x, z) in _c]
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

def boardwalk():
    """the approach: 8 m wide, from the end of the pier (y 0.6) gently up to the porch front (y 3.0)"""
    w = WALK['w']; z0, z1 = WALK['z0'], WALK['z1']; ya, yb = FL['lounge'], WALK['y1']
    n = 22
    for i in range(n):
        za = z0 + (z1 - z0) * i / n; zb = z0 + (z1 - z0) * (i + 1) / n
        y0 = ya + (yb - ya) * i / n; y1 = ya + (yb - ya) * (i + 1) / n
        P = np.array([[-w / 2, y0, za], [w / 2, y0, za], [w / 2, y1, zb], [-w / 2, y1, zb]])
        U = np.c_[P[:, 0] / 3, P[:, 2] / 3]
        walkm.add('plank', P, [[0, 1, 0]] * 4, U, [0, 2, 1, 0, 3, 2], tint(rng, 0.06))
        walkm.add('dark', P - np.array([0, 0.12, 0]), [[0, -1, 0]] * 4, U, [0, 1, 2, 0, 2, 3])
        for s in (-1, 1):
            bevel_box(walkm, 'dark', 0.14, 0.4, zb - za, 0.02, m=M(T(s * (w / 2 + 0.07), (y0 + y1) / 2 - 0.2, (za + zb) / 2), Rx(-math.degrees(math.atan2(y1 - y0, zb - za)))), uvs=3.0)
    # collider: one long sloped slab + side rails
    ln = math.hypot(z1 - z0, ya - yb); ang = math.degrees(math.atan2(ya - yb, z1 - z0))
    collider_box(col, w + 0.4, 0.4, ln + 0.4, M(T(0, (ya + yb) / 2 - 0.2, (z0 + z1) / 2), Rx(ang)))
    for s in (-1, 1):
        collider_box(col, 0.3, 1.4, ln, M(T(s * (w / 2 + 0.15), (ya + yb) / 2 + 0.6, (z0 + z1) / 2), Rx(ang)))
    # posts + rope rails + pilings
    k = 0
    for z in np.arange(z0 + 1.5, z1, 3.0):
        t = (z - z0) / (z1 - z0); y = ya + (yb - ya) * t
        for s in (-1, 1):
            x = s * (w / 2 + 0.07)
            lathe(walkm, 'bark', [(0.16, -1.8), (0.15, 1.2), (0.0, 1.3)], 8, m=T(x, y, z), uv_v=2.0)
        k += 1
    for s in (-1, 1):
        pts = []
        for z in np.arange(z0 + 1.5, z1, 3.0):
            t = (z - z0) / (z1 - z0); y = ya + (yb - ya) * t
            pts.append((s * (w / 2 + 0.07), y + 0.95, z))
        for a, b in zip(pts[:-1], pts[1:]):
            sag = [(a[0], a[1] + (b[1] - a[1]) * u - 0.18 * math.sin(math.pi * u), a[2] + (b[2] - a[2]) * u) for u in np.linspace(0, 1, 6)]
            tube(walkm, 'rope', sag, 0.035, 5, twist=2)
    # wide steps down from the porch front edge onto the boardwalk are not needed (it meets the porch level)

# ------------------------------------------------------------------ the walls: timber bays with windows / doors
BAYX = 16; BAYZ = 12        # bays along the long (x) and short (z) sides
def side_bays(side):
    """returns list of (p0, p1, local_center_coord) per bay for a side: 'front' (+z), 'back', 'east' (+x), 'west'"""
    if side == 'front': pts = [(-X1 + 2 * X1 * i / BAYX, Z1) for i in range(BAYX + 1)]
    elif side == 'back': pts = [(X1 - 2 * X1 * i / BAYX, -Z1) for i in range(BAYX + 1)]
    elif side == 'east': pts = [(X1, Z1 - 2 * Z1 * i / BAYZ) for i in range(BAYZ + 1)]
    else: pts = [(-X1, -Z1 + 2 * Z1 * i / BAYZ) for i in range(BAYZ + 1)]
    return list(zip(pts[:-1], pts[1:]))

def bay_spec(side, k, p0, p1):
    """what goes in this bay on floor k: ('door', w, h) | ('win', w, h, y) | ('high', ...) | None"""
    cx = (p0[0] + p1[0]) / 2; cz = (p0[1] + p1[1]) / 2
    if side == 'back' and abs(cx) < 21: return None if k < 4 else ('win', 2.2, 2.4, 1.5)    # lift bank behind
    if k == 0:
        if side == 'front' and abs(cx) < 6: return ('door', 4.6, 4.6)            # the grand doors (two bays)
        if side in ('east', 'west') and abs(cz + 15) < 2.6: return ('door', 3.0, 3.6)
        return ('win', 2.2, 2.6, 1.6)
    if k == 1: return ('win', 2.6, 1.6, 6.3)        # gallery: high clerestory windows (portraits hang below)
    return ('win', 2.2, 2.4, 1.6)

def walls():
    hs = [YS[i + 1] - YS[i] for i in range(4)]
    for k in range(4):
        y0 = YS[k]; h = hs[k]
        for side in ('front', 'back', 'east', 'west'):
            for (p0, p1) in side_bays(side):
                sp = bay_spec(side, k, p0, p1)
                mm, ln = place(p0, p1, y0)
                win = door = None
                if sp and sp[0] == 'win': win = [(ln / 2, sp[3] + sp[2] / 2, sp[1], sp[2])]
                if side == 'front' and k == 0 and abs((p0[0] + p1[0]) / 2) < 6: continue    # the grand doorway is built below
                if sp and sp[0] == 'door': door = (ln / 2, sp[1], sp[2])
                wall(shell, p0, p1, y0, h, rng, windows=win, door=door, th=0.3)
                # colliders: full wall except the door opening
                if door:
                    dx, dw, dh = door
                    for a, b in ((0, dx - dw / 2), (dx + dw / 2, ln)):
                        if b - a > 0.05: collider_box(col, b - a, h, 0.45, M(mm, T((a + b) / 2, h / 2, 0)))
                    collider_box(col, dw, h - dh, 0.45, M(mm, T(dx, dh + (h - dh) / 2, 0)))
                else:
                    collider_box(col, ln, h, 0.45, M(mm, T(ln / 2, h / 2, 0)))
    # the grand front doorway at x = 0: a carved timber portal 9.4 m wide spanning the two centre bays
    y0 = YS[0]; h = hs[0]; dw, dh = 9.0, 5.4
    bx = 2 * X1 / BAYX
    for s in (-1, 1):
        # wall pieces either side of the opening inside the two centre bays
        a, b = dw / 2, bx
        wall(shell, (s * a, Z1), (s * b, Z1), y0, h, rng, th=0.3) if s > 0 else wall(shell, (s * b, Z1), (s * a, Z1), y0, h, rng, th=0.3)
        collider_box(col, b - a, h, 0.45, T(s * (a + b) / 2, y0 + h / 2, Z1))
        bevel_box(shell, 'dark', 0.6, dh + 0.6, 0.8, 0.04, m=T(s * (dw / 2 + 0.3), y0 + (dh + 0.6) / 2, Z1), uvs=2.0)
    wall(shell, (-dw / 2, Z1), (dw / 2, Z1), y0 + dh, h - dh, rng, th=0.3)
    collider_box(col, dw, h - dh, 0.45, T(0, y0 + dh + (h - dh) / 2, Z1))
    bevel_box(shell, 'dark', dw + 1.8, 0.7, 0.9, 0.04, m=T(0, y0 + dh + 0.35, Z1 + 0.05), uvs=2.0)
    quad(shell, 'gold', 3.0, 0.4, T(0, y0 + dh + 0.35, Z1 + 0.51))
    # exterior posts (rough cypress) at every bay line, porch to roof
    for side in ('front', 'back', 'east', 'west'):
        for (p0, p1) in side_bays(side):
            x, z = p0
            out = np.array([np.sign(x) if abs(abs(x) - X1) < 1e-6 else 0, np.sign(z) if abs(abs(z) - Z1) < 1e-6 else 0]) * 0.45
            prof = [(0.34 + 0.03 * math.sin(t * 9 + x), t * (FL['roof'] - FL['lounge'] + 1.2)) for t in np.linspace(0, 1, 6)]
            lathe(shell, 'bark', prof, 8, m=T(x + out[0], FL['lounge'], z + out[1]), uv_v=6.0)

def belts():
    """a belt beam + a pent roof (shingle skirt) round the building at every floor line, and moss beards under it"""
    for k in range(1, 5):
        y = YS[k]
        o = 0.3
        R0 = [(-X1 - o, -Z1 - o), (X1 + o, -Z1 - o), (X1 + o, Z1 + o), (-X1 - o, Z1 + o)]
        for i in range(4):
            box_between(shell, 'dark', R0[i], R0[(i + 1) % 4], 0.5, 0.55, y - 0.1)
        if k < 4:
            pent(y + 0.9, y - 0.3, 2.6 if k < 3 else 2.0)
            for i in range(4):
                a, b = R0[i], R0[(i + 1) % 4]
                d = np.array(b) - np.array(a); ln = np.linalg.norm(d); d /= ln; nrm = np.array([d[1], -d[0]])
                for t in np.arange(1.0, ln, 2.3):
                    p = np.array(a) + d * t + nrm * rng.uniform(1.6, 2.4)
                    hh = rng.uniform(0.6, 1.6)
                    tube(shell, 'moss', [(p[0], y - 0.4, p[1]), (p[0] + rng.uniform(-0.1, 0.1), y - 0.4 - hh / 2, p[1]), (p[0], y - 0.4 - hh, p[1])], 0.07, 4, radii=[0.12, 0.07, 0.02])

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
        shell.add('shingle', P + nrm * 0.16, [nrm] * 4, U, idx)
        shell.add('dark', P, [-nrm] * 4, U, idx[::-1])
        box_between(shell, 'dark', b0, b1, 0.12, 0.3, y_out)

# ------------------------------------------------------------------ floors: slabs, ceilings, colliders
def slabs():
    holes = well_holes() + SHAFTS
    flat_deck(shell, 'plank', RECT, FL['lounge'] + 0.01, holes=[h for h in SHAFTS], under=None)
    for k in range(1, 5):
        y = YS[k]
        mat = 'bartop' if k in (1, 2) else 'plank'
        flat_deck(shell, mat, RECT, y, holes=holes, uvs=3.0, under='dark', th=0.45)
        slab_collider(col, y, ('p', RECT), holes=holes, pad=0.0)
        # ceiling beams under the slab (every 5.3 m along x), stopping at the stair wells
        for i in range(1, BAYX):
            x = -X1 + 2 * X1 * i / BAYX
            if abs(x) > SW['xi'] - 0.3: continue
            bevel_box(shell, 'dark', 0.4, 0.55, 2 * Z1 - 0.5, 0.03, m=T(x, y - 0.45 - 0.27, 0), uvs=3.0)
        # slab edge fascia inside the stair wells
        for s in (1, -1):
            xa = s * SW['xi']
            bevel_box(shell, 'dark', 0.2, 0.45, SW['zm'] - SW['z0'], 0.02, m=T(xa, y - 0.22, (SW['zm'] + SW['z0']) / 2))

# ------------------------------------------------------------------ the two stair towers (switchbacks, gentle ramps under the treads)
def flight(s, x_a, x_b, z_from, z_to, y_from, y_to):
    """one flight between x_a..x_b (east side coords, mirrored by s), climbing from z_from to z_to"""
    xa, xb = sorted((s * x_a, s * x_b)); w = xb - xa; xc = (xa + xb) / 2
    n = 30; run = abs(z_to - z_from); dirn = 0 if z_to > z_from else 180
    stair(shell, xc, z_from, y_from, dirn, n, rise=(y_to - y_from) / n, tread=run / n, w=w - 0.3, rng=rng, rails=False)
    ln = math.hypot(run, y_to - y_from); ang = math.degrees(math.atan2(y_to - y_from, run)) * (1 if z_to > z_from else -1)
    collider_box(col, w, 0.3, ln + 0.3, M(T(xc, (y_from + y_to) / 2 - 0.12, (z_from + z_to) / 2), Rx(-ang)))
    # soffit board under the flight
    bevel_box(shell, 'dark', w, 0.12, ln, 0.02, m=M(T(xc, (y_from + y_to) / 2 - 0.4, (z_from + z_to) / 2), Rx(-ang)), uvs=3.0)

def stairs():
    for s in (1, -1):
        for k in range(4):
            y0, y1 = YS[k], YS[k + 1]; ym = (y0 + y1) / 2
            flight(s, SW['xd'] + 0.1, SW['xo'], SW['z0'], SW['z1'], y0, ym)          # A: outer, climbs to the back... toward +z
            flight(s, SW['xi'], SW['xd'] - 0.1, SW['z1'], SW['z0'], ym, y1)          # B: inner, climbs back toward -z
            # mid landing (z 6..9.5)
            xa, xb = sorted((s * SW['xi'], s * SW['xo']))
            P = [(xa, SW['z1']), (xb, SW['z1']), (xb, SW['zm']), (xa, SW['zm'])]
            flat_deck(shell, 'plank', P, ym, under='dark', th=0.3)
            collider_box(col, xb - xa, 0.3, SW['zm'] - SW['z1'] + 0.2, T((xa + xb) / 2, ym - 0.15, (SW['z1'] + SW['zm']) / 2))
            # divider: a handrail wall between A and B (follows the slope)
            xd = s * SW['xd']
            pts = [(xd, y0 + (ym - y0) * t + 1.0, SW['z0'] + (SW['z1'] - SW['z0']) * t) for t in np.linspace(0, 1, 7)]
            tube(shell, 'pale', pts, 0.05, 8)
            for p in pts: box(shell, 'dark', 0.1, 1.0, 0.1, m=T(p[0], p[1] - 0.5, p[2]))
            ptsB = [(xd, ym + (y1 - ym) * t + 1.0, SW['z1'] + (SW['z0'] - SW['z1']) * t) for t in np.linspace(0, 1, 7)]
            tube(shell, 'pale', ptsB, 0.05, 8)
            # collider fence along the divider, tall enough to cover both flights
            collider_box(col, 0.2, (y1 - y0) + 1.2, SW['z1'] - SW['z0'], T(xd, (y0 + y1) / 2 + 0.6, (SW['z0'] + SW['z1']) / 2))
        # the well wall on the building side (x = 34.4) from z -6 to 9.5, every storey + the roof stair-house
        xa = s * SW['xi']
        for k in range(5):
            y0 = YS[k]; h = (YS[k + 1] - y0) if k < 4 else 4.0
            p0, p1 = ((xa, SW['z0']), (xa, SW['zm'])) if s > 0 else ((xa, SW['zm']), (xa, SW['z0']))
            wall(shell, p0, p1, y0, h, rng, th=0.3, mat='dark', frame='dark')
            collider_box(col, 0.45, h, SW['zm'] - SW['z0'], T(xa, y0 + h / 2, (SW['z0'] + SW['zm']) / 2))
            # the end walls of the well (z = -9.5 and z = 9.5) only matter on the roof (inside the building the outer walls close it)
        # roof stair-house: walls round the well above the roof + a pitched cap
        y0 = YS[4]; h = 4.0
        xo = s * (X1 - 0.2)
        for (p0, p1) in (((xa, SW['zl']), (xo, SW['zl'])), ((xa, SW['zm']), (xo, SW['zm'])), ((xo, SW['zl']), (xo, SW['zm']))):
            wall(shell, p0, p1, y0, h, rng, th=0.3)
            mm, ln = place(p0, p1, y0); collider_box(col, ln, h, 0.45, M(mm, T(ln / 2, h / 2, 0)))
        # the opening: the landing strip faces the roof deck through x = 34.4 (z -9.5..-6): wall above the door only
        xs = sorted((xa, xo))
        for zz, sgn in ((SW['zl'], -1), (SW['zm'], 1)):
            pass
        # pitched cap
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

# ------------------------------------------------------------------ the roof: deck rail, lift house + the steeple
def roof():
    y = YS[4]
    o = 0.2
    R0 = [(-X1 + o, -Z1 + o), (X1 - o, -Z1 + o), (X1 - o, Z1 - o), (-X1 + o, Z1 - o)]
    railing(shell, R0, y, rng, closed=True, rope_mat=None, balusters=True, post_every=2.6)
    for i in range(4): col_between(R0[i], R0[(i + 1) % 4], y, 1.3, 0.3)
    # the lift house (glass + timber) over the four machine heads, the base of the steeple
    xa, xb, za, zb = -21.0, 21.0, -29.6, -19.0
    hh = 9.5
    for (p0, p1) in (((xa, zb), (xb, zb)), ((xb, za), (xb, zb)), ((xa, za), (xa, zb))):
        mm, ln = place(p0, p1, y)
        nwin = max(1, int(ln / 5.2))
        wins = [(ln * (j + 0.5) / nwin, 4.8, 3.6, 5.4) for j in range(nwin)]
        wall(shell, p0, p1, y, hh, rng, windows=wins, th=0.3)
        collider_box(col, ln, hh, 0.45, M(mm, T(ln / 2, hh / 2, 0)))
    flat_deck(shell, 'dark', [(xa, za), (xb, za), (xb, zb), (xa, zb)], y + hh, under='plank', th=0.3)
    collider_box(col, xb - xa, 0.4, zb - za, T(0, y + hh + 0.2, (za + zb) / 2))
    # the steeple: four tapering tiers of shingle + a crow's nest + the flag mast
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
            shell.add('shingle', P, [nrm] * 4, U, idx)
        # a lit dormer window on the front and back of each tier
        for sz in (1, -1):
            window(shell, min(2.4, w1 * 0.4), th_ * 0.4, M(T(cx, ty + th_ * 0.45, cz + sz * (d0 + d1) / 4 + sz * 0.15), Ry(0 if sz > 0 else 180)), rng, shutters=False)
        # eave band
        for i in range(4): box_between(shell, 'dark', c0[i], c0[(i + 1) % 4], 0.3, 0.35, ty + 0.1)
    top = y + hh + 32.0
    # crow's nest + spike
    lathe(shell, 'dark', [(0.0, top), (2.6, top), (2.8, top + 0.3), (2.8, top + 1.4), (2.5, top + 1.5), (0.0, top + 1.5)], 12, m=T(cx, 0, cz))
    for a in range(0, 360, 30):
        p = (cx + 2.7 * math.sin(math.radians(a)), cz + 2.7 * math.cos(math.radians(a)))
        cyl(shell, 'dark', 0.08, 1.2, 5, m=T(p[0], top + 1.5, p[1]))
    tube(shell, 'pale', [(cx + 2.7 * math.sin(math.radians(a)), top + 2.7, cz + 2.7 * math.cos(math.radians(a))) for a in range(0, 361, 15)], 0.07, 6)
    lathe(shell, 'shingle', [(3.0, top + 2.9), (0.0, top + 9.0)], 12, m=T(cx, 0, cz))
    cyl(shell, 'iron', 0.1, 9.0, 6, m=T(cx, top + 9.0, cz))
    sphere(shell, 'glow', 0.45, 12, 8, m=T(cx, top + 18.2, cz))
    L['steeple_top'] = top + 18.2; L['nest'] = [cx, top + 1.5, cz]

def portico():
    """the grand entrance: four cypress columns, a gabled shingle roof and the MUDWATER board, over the front doors"""
    y0 = FL['lounge']; z0, z1 = Z1, Z1 + 9.0; w = 16.0; hcol = 7.2
    for x in (-w / 2, -w / 6, w / 6, w / 2):
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
    for k in range(5):
        y = YS[k]
        bevel_box(shell, 'dark', 42.0, 0.6, 0.6, 0.04, m=T(0, y + 3.8, -22.4), uvs=3.0)
        for x in (-20.6, -10, 0, 10, 20.6):
            bevel_box(shell, 'dark', 0.6, 3.8, 0.6, 0.04, m=T(x, y + 1.9, -22.4), uvs=2.0)
        quad(shell, 'gold', 6.0, 0.35, T(0, y + 3.8, -22.08))

if __name__ == '__main__':
    porch(); boardwalk(); walls(); belts(); slabs(); stairs(); roof(); portico(); lift_lobby_trim()
    print('shell', write(OUT + 'sp_shell.glb', shell, MATS))
    print('col', write(OUT + 'sp_shell_col.glb', col, MATS))
    print('walk', write(OUT + 'sp_boardwalk.glb', walkm, MATS))
    json.dump(L, open('/home/claude/spire/out/layout.json', 'w'))
