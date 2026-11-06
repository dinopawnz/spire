"""MUDWATER SPIRE v3 - THE HALL OF FAKES, using the whole building.
A 4 m wide winding stair-ramp climbs TWICE round the inside of the building, hugging all four walls (front, west end, back, east end),
from a grand flight of steps (3.2 m up, so you can walk under the whole thing at floor level) to the gallery landing 14.4 m up.
The 200 portraits hang along the walls beside it. Inside the band: an open hall 60 x 51 m and 21 m tall, and in its middle the
FINALS HALL - a 26 x 20 m glass hall on an island in a glowing swamp moat (frosted until the host starts the finals).
Writes sp_f2_hall.glb, sp_f2_col.glb, sp_f2_vault.glb, sp_f2_vaultcol.glb, sp_vault_frost.glb, sp_vault_door.glb, out/f2_layout.json."""
import math, json, random, os
import numpy as np
from glb import *
from kit import *

OUT = '/home/claude/spire/out/glb/'
POUT = '/home/claude/spire/out/portraits/'
rng = random.Random(201)
LY = json.load(open('/home/claude/spire/out/layout.json'))
B = LY['band']; SW = LY['sw']; X1, Z1 = LY['X1'], LY['Z1']
Y0 = LY['FL']['hall']; YTOP = LY['FL']['gallery']; YCEIL = LY['FL']['cards'] - 0.45
YS = Y0 + 3.2                                  # where the winding stair starts (the grand steps lead up to it)
LAPS = 2
PW, PH = 1.1, 1.1 * 533 / 384                  # Black Flag portraits (finals)
PWH, PHH = 1.3, 1.3 * 533 / 384                # Founder portraits (on the walls)
ROW_Y = (1.45, 3.4)              # portrait centre heights above the ramp: a lower row at eye level and an upper row
N_HALL = None                    # = the number of wall slots (two rows round both laps)
IMGS = None
RX, RZ = 15.5, 12.0                            # the finals hall: x -15.5..15.5, z -12..12 (v24: roomier in the bigger building)
MOAT = 3.2                                     # the glowing moat round it
hall = Mesh(); col = Mesh(); vm = Mesh(); vc = Mesh()
xc, zc = (B['xo'] + B['xi']) / 2, (B['zo'] + B['zi']) / 2     # band centre lines (32.4, 27.6)

# ------------------------------------------------------------------ the route: straights between flat corner squares
SIDES = [  # name, start (x,z), end (x,z), wall normal direction for portraits (into the band), wall coordinate
    ('front', ( B['xi'],  zc), (-B['xi'],  zc), 'z',  B['zo']),
    ('west',  (-xc,  B['zi']), (-xc, -B['zi']), 'x', -B['xo']),
    ('back',  (-B['xi'], -zc), ( B['xi'], -zc), 'z', -B['zo']),
    ('east',  ( xc, -B['zi']), ( xc,  B['zi']), 'x',  B['xo'])]
LAP_LEN = sum(math.hypot(e[0] - s[0], e[1] - s[1]) for _, s, e, _, _ in SIDES)
RISE_LAP = (YTOP - YS) / LAPS
def runs():
    """every straight in order: (lap, side, start xz, end xz, y0, y1)"""
    out = []; s_acc = 0.0
    for lap in range(LAPS):
        for (name, a, b, ax, wc) in SIDES:
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            y0 = YS + (YTOP - YS) * s_acc / (LAP_LEN * LAPS); s_acc += ln
            y1 = YS + (YTOP - YS) * s_acc / (LAP_LEN * LAPS)
            out.append((lap, name, a, b, y0, y1, ax, wc))
    return out
CORNERS = {'front': (B['xi'], B['zi']), 'west': (-B['xo'], B['zi']), 'back': (-B['xo'], -B['zo']), 'east': (B['xi'], -B['zo'])}   # min corner of the square before each side
def corner_rect(name):
    """the square at the START of a side"""
    return {'front': (B['xi'], B['xo'], B['zi'], B['zo']), 'west': (-B['xo'], -B['xi'], B['zi'], B['zo']),
            'back': (-B['xo'], -B['xi'], -B['zo'], -B['zi']), 'east': (B['xi'], B['xo'], -B['zo'], -B['zi'])}[name]

def slab_quad(m, mat, P, under=True, th=0.25):
    P = np.array(P, float); U = np.c_[P[:, 0] / 3, P[:, 2] / 3]
    n = np.cross(P[1] - P[0], P[3] - P[0]); idx = [0, 1, 2, 0, 2, 3] if n[1] > 0 else [0, 2, 1, 0, 3, 2]
    m.add(mat, P, [[0, 1, 0]] * 4, U, idx, tint(rng, 0.08))
    if under: m.add('dark', P - np.array([0, th, 0]), [[0, -1, 0]] * 4, U, idx[::-1])

def straight(a, b, y0, y1):
    """one sloped run of the band: deck, soffit, inner fascia, inner rail with posts, colliders, moss beards"""
    a = np.array(a); b = np.array(b); d = (b - a) / np.linalg.norm(b - a); ln = np.linalg.norm(b - a)
    nrm_in = np.array([-d[1], d[0]])                      # left of travel...
    # the band's inner edge is toward the building centre: pick the normal that points to the centre
    mid = (a + b) / 2
    if np.dot(nrm_in, -mid) < 0: nrm_in = -nrm_in
    hw = 2.0
    n = max(1, int(ln / 3.0))
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        p0 = a + d * ln * t0; p1 = a + d * ln * t1; ya = y0 + (y1 - y0) * t0; yb = y0 + (y1 - y0) * t1
        P = [[*(p0 + nrm_in * hw)][0:1] + [ya] + [(p0 + nrm_in * hw)[1]], [(p0 - nrm_in * hw)[0], ya, (p0 - nrm_in * hw)[1]],
             [(p1 - nrm_in * hw)[0], yb, (p1 - nrm_in * hw)[1]], [(p1 + nrm_in * hw)[0], yb, (p1 + nrm_in * hw)[1]]]
        slab_quad(hall, 'plank', P)
    # collider: one sloped box
    ang = math.degrees(math.atan2(y1 - y0, ln))
    ry = math.degrees(math.atan2(d[0], d[1]))
    collider_box(col, 2 * hw, 0.3, ln + 0.2, M(T(mid[0], (y0 + y1) / 2 - 0.15, mid[1]), Ry(ry), Rx(-ang)))
    # inner fascia + rail + posts (posts carry a vine), moss hanging off the edge
    e0 = a + nrm_in * hw; e1 = b + nrm_in * hw
    bevel_box(hall, 'dark', 0.2, 0.45, math.hypot(ln, y1 - y0), 0.02, m=M(T((e0[0] + e1[0]) / 2, (y0 + y1) / 2 - 0.2, (e0[1] + e1[1]) / 2), Ry(ry), Rx(-ang)), uvs=3.0)
    rail = [(e0[0] + (e1[0] - e0[0]) * t, y0 + (y1 - y0) * t + 1.05, e0[1] + (e1[1] - e0[1]) * t) for t in np.linspace(0, 1, max(2, int(ln / 2.5)) + 1)]
    tube(hall, 'pale', rail, 0.055, 8)
    tube(hall, 'dark', [(p[0], p[1] - 0.6, p[2]) for p in rail], 0.03, 5)
    for i_, p in enumerate(rail):
        bevel_box(hall, 'dark', 0.12, 1.05, 0.12, 0.02, m=T(p[0], p[1] - 0.52, p[2]))
    collider_box(col, 0.25, 1.3, ln, M(T((e0[0] + e1[0]) / 2, (y0 + y1) / 2 + 0.65, (e0[1] + e1[1]) / 2), Ry(ry), Rx(-ang)))
    for t in np.arange(0.4, ln, 1.3):                      # moss beards hanging from the inner edge
        if rng.random() < 0.3: continue
        p = e0 + (e1 - e0) * t / ln; y = y0 + (y1 - y0) * t / ln - 0.42
        hh = rng.uniform(0.6, 2.6)
        tube(hall, 'moss', [(p[0], y, p[1]), (p[0] + rng.uniform(-0.12, 0.12), y - hh / 2, p[1] + rng.uniform(-0.12, 0.12)), (p[0], y - hh, p[1])], 0.07, 4, radii=[0.15, 0.08, 0.02])
    # support posts down to the floor (lap 1) at the inner edge, every ~8 m, wrapped in vines
    return e0, e1, nrm_in

def corner(name, y):
    x0, x1, z0, z1 = corner_rect(name)
    slab_quad(hall, 'plank', [[x0, y, z0], [x1, y, z0], [x1, y, z1], [x0, y, z1]])
    collider_box(col, x1 - x0, 0.3, z1 - z0, T((x0 + x1) / 2, y - 0.15, (z0 + z1) / 2))

def band():
    slots = []; rs = runs()
    seen_corner = set()
    # (v24, bigger building) exactly 200 portraits per row, shared out over the runs by length (largest remainder), so it stays 400
    lens = [math.hypot(r[3][0] - r[2][0], r[3][1] - r[2][1]) for r in rs]; tot = sum(lens)
    raw = [200 * l / tot for l in lens]; NPR = [int(v) for v in raw]
    for k in sorted(range(len(raw)), key=lambda k: raw[k] - NPR[k], reverse=True)[:200 - sum(NPR)]: NPR[k] += 1
    for ri, (lap, name, a, b, y0, y1, ax, wc) in enumerate(rs):
        corner(name, y0)
        e0, e1, nin = straight(a, b, y0, y1)
        # posts from below: from the floor to lap 1, from lap 1 to lap 2 (at the inner edge)
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        for t in np.arange(4.0, ln - 2, 8.0):
            p = np.array(e0) + (np.array(e1) - np.array(e0)) * t / ln; yy = y0 + (y1 - y0) * t / ln
            ybot = Y0 if lap == 0 else yy - RISE_LAP
            prof = [(0.2 + 0.03 * math.sin(u * 9 + t), (yy - 0.3 - ybot) * u) for u in np.linspace(0, 1, 5)]
            lathe(hall, 'bark', prof, 8, m=T(p[0] - nin[0] * 0.2, ybot, p[1] - nin[1] * 0.2), uv_v=3.0)
            vine = [(p[0] - nin[0] * 0.2 + 0.24 * math.cos(u * 9), ybot + (yy - 0.3 - ybot) * u, p[1] - nin[1] * 0.2 + 0.24 * math.sin(u * 9)) for u in np.linspace(0, 1, 18)]
            tube(hall, 'moss', vine, 0.05, 4)
            collider_box(col, 0.45, yy - ybot, 0.45, T(p[0] - nin[0] * 0.2, (yy + ybot) / 2, p[1] - nin[1] * 0.2))
        # portraits on the wall beside the run
        n = NPR[ri]
        for k in range(n):
            t = (k + 0.5) / n
            px = a[0] + (b[0] - a[0]) * t; pz = a[1] + (b[1] - a[1]) * t
            if ax == 'z': x, z, ry = px, wc - np.sign(wc) * 0.06, 180 if wc > 0 else 0
            else: x, z, ry = wc - np.sign(wc) * 0.06, pz, 270 if wc > 0 else 90
            for dy in ROW_Y:            # two rows of portraits (owner: at least 400 on the walls)
                py = y0 + (y1 - y0) * t + dy
                frame(hall, PWH, PHH, M(T(x, py, z), Ry(ry)))
                slots.append(dict(x=round(x - math.sin(math.radians(ry)) * -0.10, 3), y=round(py, 3), z=round(z - math.cos(math.radians(ry)) * -0.10, 3), ry=ry))   # 10 cm proud of the backing: no z-fighting from far away (v23)
            if k < n - 1:
                t2 = (k + 1) / n
                sx = a[0] + (b[0] - a[0]) * t2; sz = a[1] + (b[1] - a[1]) * t2; sy = y0 + (y1 - y0) * t2 + ROW_Y[-1] + 1.15
                if ax == 'z': sconce(hall, M(T(sx, sy, wc - np.sign(wc) * 0.02), Ry(ry)))
                else: sconce(hall, M(T(wc - np.sign(wc) * 0.02, sy, sz), Ry(ry)))
    corner('front', YTOP)          # the top landing (the gallery door on the east wall opens off it)
    # lantern points under the inner edge of every run (the game hangs jar lanterns there)
    global LANTERNS
    LANTERNS = []
    for (lap, name, a, b, y0, y1, ax, wc) in rs:
        a_ = np.array(a); b_ = np.array(b); ln = np.linalg.norm(b_ - a_); d = (b_ - a_) / ln
        nin = np.array([-d[1], d[0]]); mid = (a_ + b_) / 2
        if np.dot(nin, -mid) < 0: nin = -nin
        for t in np.arange(6.0, ln - 3, 12.0):
            p = a_ + d * t + nin * 1.7
            LANTERNS.append([round(p[0], 2), round(y0 + (y1 - y0) * t / ln - 0.4, 2), round(p[1], 2)])
    return slots

def grand_steps():
    """the grand flight up to the start of the winding stair: in the band under the east run, climbing toward the front corner"""
    x0, x1 = B['xi'], B['xo']; z1 = B['zi']; z0 = z1 - 6.4
    stair(hall, (x0 + x1) / 2, z0, Y0, 0, 20, rise=(YS - Y0) / 20, tread=6.4 / 20, w=x1 - x0 - 0.3, rng=rng, rails=False)
    ln = math.hypot(6.4, YS - Y0); ang = math.degrees(math.atan2(YS - Y0, 6.4))
    collider_box(col, x1 - x0, 0.3, ln + 0.3, M(T((x0 + x1) / 2, (Y0 + YS) / 2 - 0.12, (z0 + z1) / 2), Rx(-ang)))
    rail = [(x0, Y0 + 1.05 + (YS - Y0) * t, z0 + 6.4 * t) for t in np.linspace(0, 1, 6)]
    tube(hall, 'pale', rail, 0.06, 8)
    for p in rail: bevel_box(hall, 'dark', 0.14, 1.05, 0.14, 0.02, m=T(p[0], p[1] - 0.52, p[2]))
    collider_box(col, 0.25, 1.3 + (YS - Y0), 6.4, T(x0, (Y0 + YS) / 2 + 0.65, (z0 + z1) / 2))
    # the newel posts with lanterns at the foot
    for x in (x0 + 0.2, x1 - 0.2):
        bevel_box(hall, 'dark', 0.4, 1.6, 0.4, 0.04, m=T(x, Y0 + 0.8, z0 - 0.3))
        lathe(hall, 'glow', [(0.0, 0), (0.15, 0.05), (0.18, 0.3), (0.12, 0.45), (0.0, 0.48)], 10, m=T(x, Y0 + 1.6, z0 - 0.3))
    return [(x0 + x1) / 2, Y0, z0 - 1.5]

def end_walls():
    """the gallery walls at x = +-34.4 that close the band at both ends (portraits hang on them), with doorways at the floor for the
    lift lobbies and the stair door, and the east one at the top for the gallery landing"""
    for s in (1, -1):
        x = s * B['xo']
        # spans of the wall along z with openings: (z0, z1, y0, y1) holes
        lz = LY['lifts'][0]['z']                                   # the lift lobby door is just in front of the cage (doors face +z)
        holes = [(SW['zm'] + 1.3, SW['zm'] + 10.5, Y0, Y0 + 3.6), (lz + 3.6, lz + 10.6, Y0, Y0 + 3.6), (SW['zl'], SW['z0'], Y0, Y0 + 3.6)]
        if s > 0: holes.append((B['zi'] + 0.1, B['zo'] - 0.1, YTOP, YTOP + 3.2))
        segs = [(-B['zo'], SW['z0']), (SW['zm'], B['zo'])]          # the stair-well wall (shell) covers z -6..9.5
        for (za, zb) in segs:
            zs = sorted(set([za, zb] + [h[0] for h in holes if za < h[0] < zb] + [h[1] for h in holes if za < h[1] < zb]))
            for z0_, z1_ in zip(zs[:-1], zs[1:]):
                zm = (z0_ + z1_) / 2
                spans = [(Y0, YCEIL)]
                for (hz0, hz1, hy0, hy1) in holes:
                    if hz0 <= zm <= hz1:
                        ns = []
                        for lo, hi in spans:
                            if hi <= hy0 or lo >= hy1: ns.append((lo, hi))
                            else:
                                if lo < hy0: ns.append((lo, hy0))
                                if hi > hy1: ns.append((hy1, hi))
                        spans = ns
                for lo, hi in spans:
                    for (xx, mat) in ((x, 'dark'), (x + s * 0.3, 'plank')):
                        P = np.array([[xx, lo, z0_], [xx, lo, z1_], [xx, hi, z1_], [xx, hi, z0_]])
                        nn = [-s, 0, 0] if mat == 'dark' else [s, 0, 0]
                        idx = [0, 1, 2, 0, 2, 3] if (s > 0) == (mat == 'dark') else [0, 2, 1, 0, 3, 2]
                        hall.add(mat, P, [nn] * 4, [[z0_ / 3, lo / 3], [z1_ / 3, lo / 3], [z1_ / 3, hi / 3], [z0_ / 3, hi / 3]], idx, tint(rng, 0.12))
                    collider_box(col, 0.4, hi - lo, z1_ - z0_, T(x + s * 0.15, (lo + hi) / 2, zm))
        # the stair-door strip above the door (z -9.5..-6), up to the ceiling, so nobody steps off the stair into the well
        for (xx, mat) in ((x, 'dark'),):
            P = np.array([[xx, Y0 + 3.6, SW['zl']], [xx, Y0 + 3.6, SW['z0']], [xx, YCEIL, SW['z0']], [xx, YCEIL, SW['zl']]])
            hall.add(mat, P, [[-s, 0, 0]] * 4, [[0, 0], [1, 0], [1, 4], [0, 4]], [0, 1, 2, 0, 2, 3] if s > 0 else [0, 2, 1, 0, 3, 2])
        collider_box(col, 0.4, YCEIL - Y0 - 3.6, SW['z0'] - SW['zl'], T(x + s * 0.15, (Y0 + 3.6 + YCEIL) / 2, (SW['zl'] + SW['z0']) / 2))
        # carved door frames on the hall side
        for (hz0, hz1, hy0, hy1) in holes:
            zm = (hz0 + hz1) / 2; w = hz1 - hz0
            fm = M(T(x - s * 0.06, hy0, zm), Ry(-90 * s))
            for sx in (-1, 1): bevel_box(hall, 'dark', 0.3, hy1 - hy0 + 0.3, 0.3, 0.04, m=M(fm, T(sx * (w / 2 + 0.15), (hy1 - hy0 + 0.3) / 2, 0)))
            bevel_box(hall, 'dark', w + 0.9, 0.45, 0.35, 0.04, m=M(fm, T(0, hy1 - hy0 + 0.3, 0)))

def frame(m, w, h, mm, depth=0.09, bw=0.13):
    prof = [(0.0, 0.0), (0.012, 0.035), (0.04, 0.05), (0.07, 0.09), (0.1, 0.075), (bw, 0.06), (bw + 0.005, 0.0)]
    corners = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    outs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for i in range(4):
        (x0, y0), (x1, y1) = corners[i], corners[(i + 1) % 4]; o0, o1 = outs[i], outs[(i + 1) % 4]
        P = []; N = []; U = []
        for j, (d, f) in enumerate(prof):
            for (x, y, o) in ((x0, y0, o0), (x1, y1, o1)):
                P.append([x + o[0] * d, y + o[1] * d, f])
            U += [[j / 6, 0], [j / 6, 1]]
        P = np.array(P)
        for j in range(len(prof)):
            j0, j1 = max(0, j - 1), min(len(prof) - 1, j + 1)
            dd = prof[j1][0] - prof[j0][0]; df = prof[j1][1] - prof[j0][1]
            side = np.array([y1 - y0, -(x1 - x0), 0.0]); side /= np.linalg.norm(side)
            n = side * (-df) + np.array([0, 0, 1.0]) * dd; n /= np.linalg.norm(n) + 1e-9
            N += [n, n]
        I = []
        for j in range(len(prof) - 1):
            a = 2 * j; I += [a, a + 1, a + 3, a, a + 3, a + 2]
        t = I[:3]; fn = np.cross(P[t[1]] - P[t[0]], P[t[2]] - P[t[0]])
        if np.dot(fn, N[t[0]]) < 0: I = list(np.array(I).reshape(-1, 3)[:, ::-1].reshape(-1))
        m.add('gold', P, N, U, I, None, mm)
    quad(m, 'black', w + 0.04, h + 0.04, M(mm, T(0, 0, -0.005)))

def sconce(m, mm):
    box(m, 'brass', 0.16, 0.24, 0.05, m=M(mm, T(0, 0, 0.025)))
    tube(m, 'brass', [(0, 0, 0.03), (0, -0.05, 0.2), (0, 0.06, 0.32)], 0.018, 6, m=mm)
    lathe(m, 'glow', [(0.0, 0.0), (0.07, 0.02), (0.09, 0.12), (0.06, 0.22), (0.0, 0.24)], 10, m=M(mm, T(0, 0.06, 0.32)))

# ------------------------------------------------------------------ the finals hall on its island, the moat, the bridge
def finals_hall():
    H = 9.5
    sides = [((-RX, RZ), (RX, RZ)), ((RX, RZ), (RX, -RZ)), ((RX, -RZ), (-RX, -RZ)), ((-RX, -RZ), (-RX, RZ))]
    for i, (p0, p1) in enumerate(sides):
        mm, ln = place(p0, p1, Y0)
        n = int(round(ln / 2.0))
        for j in range(n):
            a = ln * j / n; b = ln * (j + 1) / n; c = (a + b) / 2
            gx = p0[0] + (p1[0] - p0[0]) * c / ln
            door = i == 0 and abs(gx) < 1.6
            if door:
                quad(vm, 'vglass', b - a, H - 3.2, M(mm, T(c, 3.2 + (H - 3.2) / 2, 0)), double=True)
                collider_box(vc, b - a, H - 3.2, 0.2, M(mm, T(c, 3.2 + (H - 3.2) / 2, 0)))
            else:
                quad(vm, 'vglass', b - a, H - 0.6, M(mm, T(c, 0.6 + (H - 0.6) / 2, 0)), double=True)
                bevel_box(vm, 'dark', b - a + 0.02, 0.6, 0.35, 0.03, m=M(mm, T(c, 0.3, 0)), uvs=2.0)
                collider_box(vc, b - a + 0.05, H, 0.25, M(mm, T(c, H / 2, 0)))
            cyl(vm, 'brass', 0.07, H, 6, m=M(mm, T(a, 0, 0)))
        for yy in (H, H / 2):
            bevel_box(vm, 'brass', ln + 0.3, 0.3, 0.4, 0.03, m=M(mm, T(ln / 2, yy, 0)), uvs=3.0)
    collider_box(vc, 2 * RX, 0.25, 2 * RZ, T(0, Y0 + H + 0.35, 0))       # an invisible lid: nobody jumps in off the stair
    flat_deck(vm, 'bartop', [(-RX, -RZ), (RX, -RZ), (RX, RZ), (-RX, RZ)], Y0 + 0.03, under=None)
    lathe(vm, 'mudglow', [(1.4, Y0 + 0.04), (1.8, Y0 + 0.04)], 48)
    # ten screens in two rows of five, wide aisles between them
    slots = []
    for zr in (-6.0, 6.0):
        for xr in (-12.4, -6.2, 0.0, 6.2, 12.4):
            z0, z1 = zr - 2.8, zr + 2.8
            bevel_box(vm, 'velvet', 0.3, 4.4, z1 - z0, 0.03, m=T(xr, Y0 + 2.2, zr), uvs=2.0)
            bevel_box(vm, 'dark', 0.5, 0.35, z1 - z0 + 0.2, 0.03, m=T(xr, Y0 + 0.17, zr))
            bevel_box(vm, 'brass', 0.5, 0.2, z1 - z0 + 0.2, 0.03, m=T(xr, Y0 + 4.5, zr))
            collider_box(vc, 0.5, 4.6, z1 - z0 + 0.2, T(xr, Y0 + 2.3, zr))
            for side in (1, -1):
                for k in range(5):
                    row = 0 if k < 3 else 1; c_ = k if k < 3 else k - 3
                    zz = z0 + 1.0 + c_ * 1.75 + (0.9 if row else 0); yy = Y0 + (1.3 if row == 0 else 3.25)
                    ry = 90 if side > 0 else 270; px = xr + side * 0.17
                    frame(vm, PW, PH, M(T(px, yy, zz), Ry(ry)), bw=0.09)
                    slots.append(dict(x=round(px + side * 0.10, 3), y=round(yy, 3), z=round(zz, 3), ry=ry))
    lathe(vm, 'dark', [(0.0, Y0), (1.1, Y0), (1.1, Y0 + 0.25), (0.8, Y0 + 0.4), (0.6, Y0 + 1.1), (0.85, Y0 + 1.25), (0.0, Y0 + 1.25)], 24)
    lathe(vm, 'gold', [(0.85, Y0 + 1.25), (0.9, Y0 + 1.32), (0.0, Y0 + 1.34)], 24)
    collider_box(vc, 1.8, 1.3, 1.8, T(0, Y0 + 0.65, 0))
    # the moat: a glowing swamp channel round the island, a mossy stone curb on both edges, a little bridge to the door
    ox, oz = RX + MOAT, RZ + MOAT
    for (x0, x1, z0, z1) in ((-ox, ox, RZ + 0.3, oz), (-ox, ox, -oz, -RZ - 0.3), (-ox, -RX - 0.3, -RZ - 0.3, RZ + 0.3), (RX + 0.3, ox, -RZ - 0.3, RZ + 0.3)):
        quad(hall, 'pond', x1 - x0, z1 - z0, M(T((x0 + x1) / 2, Y0 + 0.08, (z0 + z1) / 2), Rx(-90)), uv=(0, 0, (x1 - x0) / 4, (z1 - z0) / 4))
    for (hw, hd) in ((ox, oz), (RX + 0.3, RZ + 0.3)):
        for (p0, p1) in (((-hw, hd), (hw, hd)), ((hw, hd), (hw, -hd)), ((hw, -hd), (-hw, -hd)), ((-hw, -hd), (-hw, hd))):
            mm, ln = place(p0, p1, Y0)
            if p0[1] == hd and p1[1] == hd:          # leave a gap in both curbs for the bridge (front middle)
                for (a_, b_) in ((0, ln / 2 - 1.8), (ln / 2 + 1.8, ln)):
                    bevel_box(hall, 'mud', b_ - a_, 0.5, 0.6, 0.08, m=M(mm, T((a_ + b_) / 2, 0.25, 0)), uvs=1.5)
                    if hw == ox: collider_box(col, b_ - a_, 0.7, 0.6, M(mm, T((a_ + b_) / 2, 0.35, 0)))
                continue
            bevel_box(hall, 'mud', ln + 0.6, 0.5, 0.6, 0.08, m=M(mm, T(ln / 2, 0.25, 0)), uvs=1.5)
            if hw == ox: collider_box(col, ln + 0.6, 0.7, 0.6, M(mm, T(ln / 2, 0.35, 0)))
            for t in np.arange(0.5, ln, 2.2):
                lathe(hall, 'moss', [(0.32, 0.0), (0.22, 0.16), (0.0, 0.22)], 8, m=M(mm, T(t, 0.5, 0.0)))
    # the arched bridge across the moat to the door
    z0, z1 = RZ + 0.2, oz + 0.4; w = 3.4; n = 10
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        za, zb = z0 + (z1 - z0) * t0, z0 + (z1 - z0) * t1
        ya, yb = Y0 + 0.15 + 0.6 * math.sin(math.pi * t0), Y0 + 0.15 + 0.6 * math.sin(math.pi * t1)
        mm = M(T(0, (ya + yb) / 2, (za + zb) / 2), Rx(-math.degrees(math.atan2(yb - ya, zb - za))))
        bevel_box(hall, 'plank', w, 0.12, math.hypot(zb - za, yb - ya) + 0.02, 0.015, m=mm, col=tint(rng, 0.1), uvs=2.0)
        collider_box(col, w, 0.25, math.hypot(zb - za, yb - ya) + 0.05, M(mm, T(0, -0.08, 0)))
    for sx in (-1, 1):
        pts = [(sx * w / 2, Y0 + 1.1 + 0.6 * math.sin(math.pi * t), z0 + (z1 - z0) * t) for t in np.linspace(0, 1, 8)]
        tube(hall, 'pale', pts, 0.05, 6)
        for p in pts[::2]: box(hall, 'dark', 0.09, 1.0, 0.09, m=T(p[0], p[1] - 0.5, p[2]))
    return slots

def chandeliers():
    """great wagon-wheel chandeliers on long chains, hung from the ceiling over the open hall"""
    for (x, z) in ((-26.0, -17.0), (26.0, -17.0), (-26.0, 17.0), (26.0, 17.0), (0.0, 0.0)):
        big = (x == 0)
        CY = YCEIL - (3.6 if big else 4.0)
        tube(hall, 'iron', [(x, YCEIL, z), (x, CY + 0.3, z)], 0.06, 6)
        for (rr, nj, dy) in (((4.0, 20, 0.0), (2.6, 12, -1.0)) if big else ((2.6, 14, 0.0), (1.5, 8, -0.8))):
            lathe(hall, 'brass', [(rr - 0.1, CY + dy - 0.08), (rr + 0.1, CY + dy - 0.08), (rr + 0.1, CY + dy + 0.08), (rr - 0.1, CY + dy + 0.08)], 40, m=T(x, 0, z))
            for k in range(4): tube(hall, 'iron', [(x + rr * math.sin(math.radians(45 + 90 * k)), CY + dy, z + rr * math.cos(math.radians(45 + 90 * k))), (x, CY + 0.3, z)], 0.02, 4)
            for k in range(nj):
                a = math.radians(360 * k / nj); p = (x + rr * math.sin(a), CY + dy, z + rr * math.cos(a))
                tube(hall, 'iron', [p, (p[0], p[1] - 0.3, p[2])], 0.012, 4)
                lathe(hall, 'glow', [(0.0, 0), (0.12, 0.03), (0.15, 0.2), (0.11, 0.34), (0.0, 0.38)], 10, m=T(p[0], p[1] - 0.72, p[2]))

def frost_sleeve():
    m = Mesh(); H = 9.5; o = 0.12
    for (p0, p1) in (((-RX - o, RZ + o), (RX + o, RZ + o)), ((RX + o, RZ + o), (RX + o, -RZ - o)), ((RX + o, -RZ - o), (-RX - o, -RZ - o)), ((-RX - o, -RZ - o), (-RX - o, RZ + o))):
        mm, ln = place(p0, p1, 0)
        quad(m, 'frost', ln, H - 0.6, M(mm, T(ln / 2, 0.6 + (H - 0.6) / 2, 0)), uv=(0, 0, ln / 2, H / 2), double=True)
    quad(m, 'frost', 2 * RX + 0.3, 2 * RZ + 0.3, M(T(0, H + 0.45, 0), Rx(-90)), uv=(0, 0, 6, 5), double=True)
    mats = dict(MATS)
    mats['frost'] = dict(tex=TEX + 'glass.png', color=(0.9, 0.95, 0.93, 0.93), emis=(0.12, 0.14, 0.13), rough=0.9, alpha='BLEND', double=True)
    print('frost', write(OUT + 'sp_vault_frost.glb', m, mats))

def vault_door():
    m = Mesh(); W_, H_ = 3.0, 3.0
    quad(m, 'vglass', W_, H_, T(0, H_ / 2, 0), double=True)
    for s_ in (-1, 1): box(m, 'brass', 0.08, H_, 0.1, m=T(s_ * W_ / 2, H_ / 2, 0))
    for yy in (0.04, H_ - 0.04, H_ / 2): box(m, 'brass', W_, 0.08, 0.1, m=T(0, yy, 0))
    mats = dict(MATS); mats['vglass'] = VGLASS
    print('door', write(OUT + 'sp_vault_door.glb', m, mats))

VGLASS = dict(color=(0.7, 0.85, 0.82, 0.07), metal=0.0, rough=0.02, alpha='BLEND', double=True)
MM = dict(MATS)
MM['pond'] = dict(tex=TEX + 'mudglow.jpg', emis_tex=TEX + 'mudglow.jpg', emis=(0.35, 0.55, 0.45), color=(0.55, 0.85, 0.75, 1), rough=0.05, metal=0.2)
if __name__ == '__main__':
    slots = band(); foot = grand_steps(); end_walls(); vslots = finals_hall(); chandeliers()
    N_HALL = len(slots)
    IMGS = [821] + sorted(random.Random(62).sample([i for i in range(1000) if i != 821], N_HALL - 1))     # the real #62 (821) + fakes
    print('hall', write(OUT + 'sp_f2_hall.glb', hall, MM), 'portraits', len(slots), 'lap', round(LAP_LEN, 1), 'rise/lap', round(RISE_LAP, 2))
    print('col', write(OUT + 'sp_f2_col.glb', col, MATS))
    VM = dict(MATS); VM['vglass'] = VGLASS
    print('vault', write(OUT + 'sp_f2_vault.glb', vm, VM), 'slots', len(vslots))
    print('vcol', write(OUT + 'sp_f2_vaultcol.glb', vc, MATS))
    frost_sleeve(); vault_door()
    json.dump({'hall': slots, 'vault': vslots, 'imgs': IMGS, 'room': [RX, RZ], 'moat': MOAT, 'yv': Y0, 'door': [0.0, Y0, RZ, 0], 'plinth': [0.0, Y0 + 1.34, 0.0],
               'foot': foot, 'top': [xc, YTOP, zc], 'lanterns': LANTERNS, 'runs': [[a[0], a[1], y0, b[0], b[1], y1, ax, wc] for (lap, name, a, b, y0, y1, ax, wc) in runs()], 'band': [B['xi'], B['xo'], B['zi'], B['zo']]}, open('/home/claude/spire/out/f2_layout.json', 'w'))
    if '--portraits' in __import__('sys').argv:
        for i in IMGS:
            src = '/home/claude/spire/out/hall/p%04d.jpg' % i
            m = Mesh(); quad(m, 'pic', PWH, PHH, T(0, 0, 0))
            write(POUT + 'pf_%04d.glb' % i, m, {'pic': dict(tex=src, emis_tex=src, emis=(0.32, 0.32, 0.32), rough=0.55)})
