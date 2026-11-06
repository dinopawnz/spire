"""MUDWATER SPIRE - the tower shell: stilts, porch, the five storeys, roofs, crow's nest, boardwalk.
The lifts are INSIDE the tower now (build_lift.py); this file only cuts the holes they pass through.
Tower space: tower centre at (0, 0, 0), water at y 0.1, the front faces +z (the boardwalk runs out to +z).
Writes: sp_shell.glb (looks), sp_shell_col.glb (invisible colliders), sp_boardwalk.glb, out/layout.json."""
import math, json, random
import numpy as np
from glb import *
from kit import *

OUT = '/home/claude/spire/out/glb/'
LOGO = '/home/claude/spire/tmp/ext/mw_logo_0.png'
# ---- the plan (keep in sync with spire.html LAYOUT)
L = dict(porch=3.0, A_porch=34.0, A1=27.0, f2=11.0, A2=24.0, f2top=52.0, gallery=43.0, f3=53.0, A3=28.0, A3d=31.0, f3top=61.0,
         f4=62.0, A4=25.0, A4d=28.0, f4top=71.0, peak=92.0, walk_len=75.0, walk_w=6.0, walk_y=0.6,
         # the two interior lifts: octagonal glass-and-brass shafts in the hollow core of the Floor 2 stair, either side of the vault.
         # doors face +z (towards the front). A = the Grand Cage (every floor), B = the Express (lounge -> card floor -> deck).
         stop_names={'3.0': 'lounge', '11.0': 'hall', '43.0': 'gallery', '53.0': 'cards', '62.0': 'deck'},
         lifts=[dict(id='A', name='The Grand Cage', x=11.6, z=0.0, stops=[3.0, 11.0, 43.0, 53.0, 62.0]),
                dict(id='B', name='The Express', x=-11.6, z=0.0, stops=[3.0, 53.0, 62.0])],
         shaft_apo=2.3, cab_apo=2.05, shaft_base=3.0, shaft_top=67.6, door_w=1.6, door_h=2.9)
# shaft footprint (local xz): the octagon plus the counterweight bay on the back (-z)
_c = octa(L['shaft_apo'])
L['shaft_fp'] = [[round(x, 4), round(z if z > -2.0 or abs(x) > 1.5 else -2.95, 4)] for (x, z) in _c]
def shaft_holes(s=1.04):
    return [hole_poly(lf['x'], lf['z'], L['shaft_fp'], s) for lf in L['lifts']]
rng = random.Random(62)
shell = Mesh(); col = Mesh()

def ring_faces(A):
    c = octa(A); return [(c[i], c[(i + 1) % 8]) for i in range(8)]

# face index 0 is the one whose outward normal is +z? octa(rot=22.5): corners at 22.5+45i from +z (x=sin, z=cos)
# face i spans corners i and i+1 -> centre angle 45+45i. Front (+z) face is the one centred at angle 0 = face 7.
FRONT = 7

def face_center_angle(i): return 45 + 45 * i     # degrees from +z towards +x

# ------------------------------------------------------------------ stilts + porch
def stilts():
    poly = octa(L['A_porch'])
    R = L['A_porch'] - 1.0
    for x in np.arange(-R, R + 1, 4.2):
        for z in np.arange(-R, R + 1, 4.2):
            if poly_x_range(poly, z) is None: continue
            x0, x1 = poly_x_range(poly, z)
            edge = min(x - x0, x1 - x, z + R + 1, R + 1 - z)
            if x0 + 0.6 < x < x1 - 0.6 and (edge < 9 or (round(x / 4.2) + round(z / 4.2)) % 2 == 0):   # full grid round the edge, sparser inside
                piling(shell, x + rng.uniform(-0.4, 0.4), z + rng.uniform(-0.4, 0.4), -1.5, L['porch'] - 0.5, rng, r=rng.uniform(0.28, 0.38), rope=rng.random() < 0.3)
    # giant cypress-trunk columns at the F1 corners (they carry the tower)
    for (x, z) in octa(L['A1']):
        prof = [(1.35 - 0.35 * t + 0.25 * math.exp(-t * 6), -1.5 + t * (L['porch'] + 1.6)) for t in np.linspace(0, 1, 10)]
        lathe(shell, 'bark', prof, 16, m=T(x, 0, z), uv_v=4.0, uvs_u=2)
    # cross bracing under the deck rim
    for a, b in ring_faces(L['A_porch'] - 0.5):
        mm, ln = place(a, b, 0.6)
        for k in range(3):
            x0 = ln * k / 3; x1 = ln * (k + 1) / 3
            for s in (1, -1):
                p0 = (mm @ np.array([x0, 0.3 if s > 0 else 2.2, 0, 1]))[:3]; p1 = (mm @ np.array([x1, 2.2 if s > 0 else 0.3, 0, 1]))[:3]
                d = p1 - p0; box(shell, 'dark', 0.12, 0.22, np.linalg.norm(d), m=M(T(*((p0 + p1) / 2)), look_basis(d)), uvs=2.0)

def porch():
    deck(shell, octa(L['A_porch']), L['porch'], rng, joists=False, flat=True)
    collider_box(col, 2 * L['A_porch'] * math.tan(math.radians(22.5)) * 2.414, 0.4, 2 * L['A_porch'], T(0, L['porch'] - 0.2, 0))
    # railing round the porch with a gap for the boardwalk (front centre)
    c = octa(L['A_porch'])
    for i in range(8):
        a, b = c[i], c[(i + 1) % 8]
        if i == FRONT:
            # front face: one gap for the boardwalk steps
            lo, hi = min(a[0], b[0]), max(a[0], b[0])
            xs = [(lo, -3.2), (3.2, hi)]
            zz = a[1]
            for x0, x1 in xs:
                if x1 - x0 > 0.3: railing(shell, [(x0, zz), (x1, zz)], L['porch'], rng, closed=False, rope_mat='rope')
        else:
            railing(shell, [a, b], L['porch'], rng, closed=False, rope_mat='rope')
            mm, ln = place(a, b, L['porch'])
            collider_box(col, ln, 1.2, 0.3, M(mm, T(ln / 2, 0.6, 0)))
    # front face collider rails (around the gaps)
    zz = c[FRONT][1]
    hw = L['A_porch'] * math.tan(math.radians(22.5))
    for x0, x1 in [(-hw, -3.2), (3.2, hw)]:
        collider_box(col, x1 - x0, 1.2, 0.3, T((x0 + x1) / 2, L['porch'] + 0.6, zz))

# ------------------------------------------------------------------ storeys
def storey(A, y0, h, win_per_face, win_w, win_h, win_y, door_faces=(), door_w=4.2, door_h=5.0, beam_tiers=()):
    faces = ring_faces(A)
    for i, (a, b) in enumerate(faces):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        wins = []
        door = None
        if i in door_faces:
            door = (ln / 2, door_w, door_h)
            slots = [ln * 0.15, ln * 0.85] if win_per_face else []
        else:
            slots = [ln * (k + 0.5) / win_per_face for k in range(win_per_face)]
        for x in slots: wins.append((x, win_y, win_w, win_h))
        mm, _ = wall(shell, a, b, y0, h, rng, windows=wins, door=door)
        for ty in beam_tiers: bevel_box(shell, 'dark', ln + 0.4, 0.34, 0.55, 0.03, m=M(mm, T(ln / 2, ty - y0, 0.06)), uvs=3.0)
        # collider: the wall as a box, split round the door
        if door:
            for (x0, x1) in [(0, ln / 2 - door_w / 2), (ln / 2 + door_w / 2, ln)]:
                collider_box(col, x1 - x0, h, 0.5, M(mm, T((x0 + x1) / 2, h / 2, 0)))
            collider_box(col, door_w, h - door_h, 0.5, M(mm, T(ln / 2, door_h + (h - door_h) / 2, 0)))
        else:
            collider_box(col, ln, h, 0.5, M(mm, T(ln / 2, h / 2, 0)))

def terrace(A_in, A_out, y, gaps_front=()):
    """a walkable ring deck (roof terrace / balcony) between two octagons, with railing on the outer edge"""
    ci = octa(A_in); co = octa(A_out)
    for i in range(8):
        quad_poly = [ci[i], ci[(i + 1) % 8], co[(i + 1) % 8], co[i]]
        # deck boards running along the face
        mm, ln = place(co[i], co[(i + 1) % 8], y)
        depth = A_out - A_in
        nb = int(depth / 0.28)
        for k in range(nb):
            off = -(k + 0.5) * depth / nb      # inward
            # board length shrinks toward the inner octagon
            frac = (k + 0.5) / nb; lk = ln - 2 * frac * depth * math.tan(math.radians(22.5))
            box(shell, 'plank', lk - 0.02, 0.09, depth / nb - 0.015, m=M(mm, T(ln / 2, -0.045, off)), col=tint(rng), uvs=3.0, uvoff=(rng.random(), 0))
        collider_box(col, ln, 0.3, depth + 0.3, M(mm, T(ln / 2, -0.15, -depth / 2)))
        if i == FRONT and gaps_front:
            x0 = co[i][0]; x1 = co[(i + 1) % 8][0]; zz = co[i][1]
            cuts = sorted(gaps_front); pts = [x0]
            for gx, gw in cuts: pts += [gx - gw / 2, gx + gw / 2]
            pts.append(x1)
            for k in range(0, len(pts), 2):
                if pts[k + 1] - pts[k] > 0.3:
                    railing(shell, [(pts[k], zz), (pts[k + 1], zz)], y, rng, closed=False)
                    collider_box(col, pts[k + 1] - pts[k], 1.2, 0.3, T((pts[k] + pts[k + 1]) / 2, y + 0.6, zz))
        else:
            railing(shell, [co[i], co[(i + 1) % 8]], y, rng, closed=False)
            collider_box(col, ln, 1.2, 0.3, M(mm, T(ln / 2, 0.6, 0)))

def ceiling_beams(A, y, holes=()):
    """heavy exposed beams under a floor (seen from the storey below); beams stop short of the lift shafts"""
    hs = [(('p', [(q[1], q[0]) for q in h[1]])) for h in holes]
    for x in np.arange(-A + 1.5, A, 3.0):
        pr = poly_x_range([(p[1], p[0]) for p in octa(A)], x)
        if not pr: continue
        cuts = [r for r in (hole_range(h, x - 0.5, x + 0.5) for h in hs) if r]
        for a, b in subtract([(pr[0] + 0.2, pr[1] - 0.2)], [(c0 - 0.15, c1 + 0.15) for c0, c1 in cuts]):
            if b - a > 0.4: bevel_box(shell, 'dark', 0.45, 0.55, b - a, 0.04, m=T(x, y - 0.4, (a + b) / 2), uvs=3.0)
    for z in np.arange(-A + 4, A, 8.0):
        pr = poly_x_range(octa(A), z)
        if not pr: continue
        cuts = [r for r in (hole_range(h, z - 0.5, z + 0.5) for h in holes) if r]
        for a, b in subtract([(pr[0] + 0.2, pr[1] - 0.2)], [(c0 - 0.15, c1 + 0.15) for c0, c1 in cuts]):
            if b - a > 0.4: bevel_box(shell, 'dark', b - a, 0.4, 0.4, 0.04, m=T((a + b) / 2, y - 0.85, z), uvs=3.0)

def struts(A_from, y_from, A_to, y_to):
    """diagonal timber knee braces carrying a wider storey out over a narrower one"""
    cf = octa(A_from); ct = octa(A_to)
    for i in range(8):
        for t in (0.0, 0.33, 0.66):
            a = np.array([cf[i][0] + (cf[(i + 1) % 8][0] - cf[i][0]) * t, y_from, cf[i][1] + (cf[(i + 1) % 8][1] - cf[i][1]) * t])
            b = np.array([ct[i][0] + (ct[(i + 1) % 8][0] - ct[i][0]) * t, y_to, ct[i][1] + (ct[(i + 1) % 8][1] - ct[i][1]) * t])
            d = b - a; bevel_box(shell, 'dark', 0.45, 0.45, np.linalg.norm(d), 0.05, m=M(T(*((a + b) / 2)), look_basis(d)), uvs=3.0)
            box(shell, 'iron', 0.55, 0.08, 0.6, m=T(*a))

def main_roof():
    A = L['A4'] + 1.2; y0 = L['f4top']; c = octa(A); peak = L['peak']
    apex = np.array([0, peak, 0])
    for i in range(8):
        a = np.array([c[i][0], y0, c[i][1]]); b = np.array([c[(i + 1) % 8][0], y0, c[(i + 1) % 8][1]])
        P = np.array([a, b, apex]); n = np.cross(b - a, apex - a); n /= np.linalg.norm(n)
        w = np.linalg.norm(b - a); hgt = np.linalg.norm(apex - (a + b) / 2)
        U = np.array([[0, 0], [w / 4, 0], [w / 8, hgt / 4]])
        shell.add('shingle', P + n * 0.2, [n] * 3, U, [0, 1, 2])
        shell.add('dark', P, [-n] * 3, U, [0, 2, 1])
        # hip ridge caps
        tube(shell, 'moss', [a + np.array([0, 0.25, 0]), apex], 0.22, 6)
        # a dormer with a lit window on every other face
        if i % 2 == 1:
            mid = (a + b) / 2; inward = -np.array([mid[0], 0, mid[2]]); inward /= np.linalg.norm(inward)
            p = mid + inward * 3.2 + np.array([0, 3.2 * (peak - y0) / (A * math.cos(math.radians(22.5))), 0])
            ang = math.degrees(math.atan2(-inward[0], -inward[2]))
            dm = M(T(p[0], p[1] - 0.6, p[2]), Ry(ang))
            box(shell, 'plank', 3.4, 3.2, 3.0, m=M(dm, T(0, 1.2, -0.8)))
            window(shell, 1.6, 1.9, M(dm, T(0, 1.4, 0.72)), rng, shutters=False)
            for s in (-1, 1):
                rm = M(dm, T(s * 1.0, 3.1, -0.8), Rz(s * 38))
                box(shell, 'shingle', 2.6, 0.16, 3.6, m=rm, uvs=4.0)
    # crow's nest lantern room at the peak
    cn = peak - 4.5
    deck(shell, octa(4.2), cn, rng, joists=False)
    railing(shell, octa(4.2), cn, rng)
    lathe(shell, 'dark', [(0.0, cn - 1.6), (3.8, cn - 0.2), (3.9, cn)], 16)
    for (x, z) in octa(2.6): bevel_box(shell, 'dark', 0.25, 3.0, 0.25, 0.03, m=T(x, cn + 1.5, z))
    lathe(shell, 'glass', [(2.55, cn + 0.1), (2.55, cn + 2.9)], 16)
    lathe(shell, 'shingle', [(3.4, cn + 3.0), (0.2, cn + 5.6)], 16, cap_bot=True)
    lathe(shell, 'glow', [(0.0, cn + 0.4), (0.9, cn + 0.9), (1.05, cn + 1.6), (0.8, cn + 2.3), (0.0, cn + 2.6)], 16)   # the beacon jar
    # flagpole + skull flag
    cyl(shell, 'dark', 0.09, 9.0, 8, m=T(0, cn + 5.4, 0))
    sphere(shell, 'gold', 0.25, 10, 6, m=T(0, cn + 14.5, 0))

def exoskeleton():
    """giant cypress trunks climbing the eight corners of the Hall tower, iron-banded, from the F2 terrace up to the card floor,
    each carrying a big glowing lantern at every tier, plus moss beards hanging from the pent-roof eaves"""
    Rc = L['A2'] / math.cos(math.radians(22.5)) + 0.7
    y0, y1 = L['f2'], L['f3'] - 0.4
    for i in range(8):
        a = math.radians(22.5 + 45 * i); x, z = Rc * math.sin(a), Rc * math.cos(a)
        prof = [(1.25 + 0.6 * math.exp(-t * 9) - 0.35 * t + 0.06 * math.sin(t * 23 + i), y0 + (y1 - y0) * t) for t in np.linspace(0, 1, 14)]
        lathe(shell, 'bark', prof, 12, m=T(x, 0, z), uv_v=6.0, uvs_u=2)
        for yy in (y0 + 2.0, 27.4, 43.8, y1 - 1.0):
            t = (yy - y0) / (y1 - y0); rr = 1.25 + 0.6 * math.exp(-t * 9) - 0.35 * t + 0.08
            lathe(shell, 'iron', [(rr, yy - 0.18), (rr + 0.05, yy), (rr, yy + 0.18)], 12, m=T(x, 0, z))
        # knots and a few snapped branch stubs
        for k in range(3):
            yy = y0 + 6 + k * 11 + i % 3; ang = rng.uniform(0, 360)
            d = np.array([math.sin(math.radians(ang)), rng.uniform(0.1, 0.5), math.cos(math.radians(ang))])
            p0 = np.array([x, yy, z]); p1 = p0 + d * rng.uniform(1.6, 2.6)
            tube(shell, 'bark', [p0, (p0 + p1) / 2 + np.array([0, 0.2, 0]), p1], 0.3, 8, radii=[0.45, 0.3, 0.14])
        # lanterns on iron brackets facing outwards, one per tier
        out = np.array([math.sin(a), 0, math.cos(a)])
        for yy in (19.2, 27.4, 35.6, 43.8):
            p0 = np.array([x, yy + 1.5, z]) + out * 0.9; p1 = p0 + out * 1.3 + np.array([0, 0.5, 0])
            tube(shell, 'iron', [p0, (p0 + p1) / 2 + np.array([0, 0.35, 0]), p1], 0.05, 6)
            tube(shell, 'iron', [p1, p1 - np.array([0, 0.4, 0])], 0.02, 4)
            q = p1 - np.array([0, 0.4, 0])
            lathe(shell, 'iron', [(0.0, 0.0), (0.42, -0.1), (0.46, -0.16), (0.0, -0.16)], 8, m=T(*q))
            lathe(shell, 'glow', [(0.0, -0.16), (0.28, -0.22), (0.34, -0.6), (0.26, -0.95), (0.0, -1.0)], 10, m=T(*q))
            for kk in range(4):
                b = math.radians(45 + 90 * kk); c = np.array([0.36 * math.sin(b), 0, 0.36 * math.cos(b)])
                tube(shell, 'iron', [q + c + np.array([0, -0.16, 0]), q + c * 1.05 + np.array([0, -0.6, 0]), q + c * 0.75 + np.array([0, -1.0, 0])], 0.025, 4)
            lathe(shell, 'iron', [(0.0, -1.0), (0.3, -1.02), (0.08, -1.2), (0.0, -1.28)], 8, m=T(*q))

def moss_beards(A_out, y, every=1.4):
    co = octa(A_out)
    for i in range(8):
        p0, p1 = np.array(co[i]), np.array(co[(i + 1) % 8]); ln = np.linalg.norm(p1 - p0)
        for k in range(int(ln / every)):
            t = (k + rng.random()) / int(ln / every); p = p0 + (p1 - p0) * t
            h = rng.uniform(0.8, 2.6); top = np.array([p[0], y, p[1]])
            sway = np.array([rng.uniform(-0.2, 0.2), 0, rng.uniform(-0.2, 0.2)])
            tube(shell, 'moss', [top, top + sway * 0.5 - np.array([0, h * 0.5, 0]), top + sway - np.array([0, h, 0])], 0.08, 4, radii=[0.14, 0.09, 0.02])

def logo_sign():
    """the big MUDWATER plaque on the front of the tower, above the lounge roof"""
    z = L['A2'] + 0.45; y = 19.5
    w, h = 16.0, 16.0 * 323 / 1334
    quad(shell, 'logo', w, h, T(0, y, z + 0.08))
    bevel_box(shell, 'dark', w + 1.2, h + 1.2, 0.35, 0.08, m=T(0, y, z - 0.12))
    # gold rope trim round the plaque
    pts = [(-w / 2 - 0.4, y - h / 2 - 0.4, z + 0.12), (w / 2 + 0.4, y - h / 2 - 0.4, z + 0.12), (w / 2 + 0.4, y + h / 2 + 0.4, z + 0.12), (-w / 2 - 0.4, y + h / 2 + 0.4, z + 0.12), (-w / 2 - 0.4, y - h / 2 - 0.4, z + 0.12)]
    tube(shell, 'gold', pts, 0.09, 8, twist=4)
    # brackets
    for s in (-1, 1):
        bevel_box(shell, 'iron', 0.3, 0.3, 1.6, 0.03, m=T(s * w / 2.6, y + h / 2 + 0.6, z - 0.4))
        tube(shell, 'iron', [(s * w / 2.6, y + h / 2 + 0.6, z + 0.3), (s * w / 2.6, y + h / 2 + 2.5, z - 0.1)], 0.05, 6)

def boardwalk():
    bw = Mesh()
    z0 = L['A_porch'] + 5.0; z1 = L['A_porch'] + L['walk_len']; y = L['walk_y']; hw = L['walk_w'] / 2
    # steps up from the boardwalk to the porch (y 0.6 -> 3.0)
    n = 13; rise = (L['porch'] - y) / n; tread = 0.38
    for i in range(n):
        zz = z0 - tread * (i + 0.5)
        box(bw, 'plank', 2 * hw, 0.1, tread - 0.02, m=T(0, y + rise * (i + 1) - 0.05, zz), col=tint(rng), uvs=3.0)
        box(bw, 'dark', 2 * hw, rise, 0.06, m=T(0, y + rise * i + rise / 2, zz + tread / 2 - 0.03), uvs=3.0)
    # the stair collider: a smooth ramp
    ln = n * tread; hh = L['porch'] - y
    collider_box(col, 2 * hw, 0.3, math.hypot(ln, hh), M(T(0, y + hh / 2 - 0.12, z0 - ln / 2), Rx(math.degrees(math.atan2(hh, ln)))))
    zbase = z0 - ln     # where the steps meet the porch edge
    # gap between the steps and the porch edge
    box(bw, 'plank', 2 * hw, 0.1, max(0.1, zbase - L['A_porch']) + 0.3, m=T(0, L['porch'] - 0.05, (zbase + L['A_porch']) / 2))
    # the walk itself
    z = z0
    while z < z1:
        box(bw, 'plank', 2 * hw - 0.02, 0.1, 0.27, m=T(rng.uniform(-0.03, 0.03), y - 0.05, z + 0.14), col=tint(rng, 0.16), uvs=3.0, uvoff=(rng.random(), 0))
        z += 0.3
    collider_box(col, 2 * hw, 0.3, z1 - z0, T(0, y - 0.15, (z0 + z1) / 2))
    for zz in np.arange(z0 + 2, z1, 4.0):
        for s in (-1, 1):
            piling(bw, s * (hw + 0.1), zz, -1.5, y + 1.0, rng, r=0.2, rope=rng.random() < 0.35)
    for s in (-1, 1):
        bevel_box(bw, 'dark', 0.18, 0.35, z1 - z0, 0.03, m=T(s * hw, y - 0.25, (z0 + z1) / 2), uvs=3.0)
        pts = []
        for zz in np.arange(z0 + 2, z1 - 1, 4.0):
            for t in np.linspace(0, 1, 7)[:-1]:
                pts.append((s * (hw + 0.1), y + 1.0 - 0.28 * math.sin(math.pi * t), zz + 4 * t))
        tube(bw, 'rope', pts, 0.035, 6, twist=2)
        collider_box(col, 0.3, 1.2, z1 - z0, T(s * (hw + 0.1), y + 0.6, (z0 + z1) / 2))
    # the welcome arch at the origin end: two big trunks, a carved beam, the logo
    za = z1 - 3
    for s in (-1, 1):
        prof = [(0.75 - 0.25 * t + 0.25 * math.exp(-t * 5), -1.2 + 10.5 * t) for t in np.linspace(0, 1, 10)]
        lathe(bw, 'bark', prof, 14, m=T(s * (hw + 1.0), 0, za), uv_v=4.0)
    bevel_box(bw, 'dark', 2 * hw + 4.5, 1.1, 0.9, 0.08, m=T(0, 9.0, za))
    quad(bw, 'logo', 8.0, 8.0 * 323 / 1334, T(0, 7.4, za + 0.5))
    quad(bw, 'logo', 8.0, 8.0 * 323 / 1334, M(T(0, 7.4, za - 0.5), Ry(180)))
    bevel_box(bw, 'dark', 8.6, 2.5, 0.6, 0.05, m=T(0, 7.4, za))
    for s in (-1, 1): tube(bw, 'iron', [(s * 3.5, 8.6, za), (s * 3.5, 8.95, za)], 0.04, 4)
    return bw

if __name__ == '__main__':
    MATS['logo'] = dict(tex=LOGO, emis_tex=LOGO, emis=(0.55, 0.45, 0.3), alpha='MASK', cutoff=0.4, double=True, rough=0.4)
    H = shaft_holes()
    stilts(); porch()
    # F1: the lounge (door on the front)
    storey(L['A1'], L['porch'], L['f2'] - L['porch'], 3, 2.6, 3.8, 3.4, door_faces=(FRONT,), door_w=4.6, door_h=5.2)
    ceiling_beams(L['A1'], L['f2'], H)
    skirt_roof(shell, L['A1'] + 0.3, L['A1'] + 3.8, L['f2'] - 0.1, L['f2'] - 1.7, rng)
    terrace(L['A2'] + 0.25, L['A1'], L['f2'])
    # the ring of floor between the Hall's round wall and the octagon (the Hall floor itself is in build_f2)
    deck(shell, octa(L['A2'] + 0.25), L['f2'], rng, joists=False, holes=[('c', 0, 0, 19.6)], flat=True)
    slab_collider(col, L['f2'], ('p', octa(L['A2'])), holes=[('c', 0, 0, 19.0)])
    # F2: the tall gallery tower, in five tiers with belt beams and pent roofs on two of them
    tiers = [L['f2'], 19.2, 27.4, 35.6, 43.8, L['f2top']]
    for k in range(5):
        y0 = tiers[k]; h = tiers[k + 1] - y0
        doors = (FRONT,) if k == 0 else ()
        storey(L['A2'], y0, h, 3, 2.2, 3.6, h * 0.55, door_faces=doors, door_w=3.2, door_h=4.0)
        if k in (1, 3):
            skirt_roof(shell, L['A2'] + 0.3, L['A2'] + 2.6, tiers[k + 1] + 0.2, tiers[k + 1] - 1.0, rng)
    struts(L['A2'] + 0.3, L['f3'] - 9.0, L['A3d'] - 0.4, L['f3'] - 0.5)
    # F3: the card floor (wider, cantilevered), balcony ring; the lift shafts pass through
    deck(shell, octa(L['A3d']), L['f3'], rng, joists=False, holes=H, flat=True)
    slab_collider(col, L['f3'], ('p', octa(L['A3'])), holes=H)
    storey(L['A3'], L['f3'], L['f3top'] - L['f3'], 3, 2.4, 3.4, 3.6, door_faces=(FRONT,), door_w=4.0, door_h=4.6)
    ceiling_beams(L['A3'], L['f3top'] + 1.0, H)
    terrace(L['A3'], L['A3d'], L['f3'])
    skirt_roof(shell, L['A3'] + 0.3, L['A3d'] + 0.8, L['f3top'] + 0.4, L['f3top'] - 0.9, rng)
    # F4: the escape floor
    deck(shell, octa(L['A4d']), L['f4'], rng, joists=False, holes=H, flat=True)
    slab_collider(col, L['f4'], ('p', octa(L['A4'])), holes=H)
    storey(L['A4'], L['f4'], L['f4top'] - L['f4'], 2, 2.0, 3.0, 4.2, door_faces=(FRONT,), door_w=3.4, door_h=4.2)
    terrace(L['A4'], L['A4d'], L['f4'])
    main_roof(); logo_sign(); exoskeleton()
    moss_beards(L['A1'] + 3.8 + 0.6, L['f2'] - 1.75); moss_beards(L['A2'] + 2.6 + 0.6, 27.4 - 1.0); moss_beards(L['A2'] + 2.6 + 0.6, 43.8 - 1.0)
    moss_beards(L['A3d'] + 0.8 + 0.6, L['f3top'] - 0.95)
    print('shell', write(OUT + 'sp_shell.glb', shell, MATS))
    bw = boardwalk()
    print('walk', write(OUT + 'sp_boardwalk.glb', bw, MATS))
    print('col', write(OUT + 'sp_shell_col.glb', col, MATS))
    json.dump(L, open('/home/claude/spire/out/layout.json', 'w'))
