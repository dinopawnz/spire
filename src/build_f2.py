"""MUDWATER SPIRE - floor 2: THE HALL OF FAKES.
A Solomon-style helix stair climbs 6.5 turns round the inside of the gallery tower, its wall hung with 1000 gilt frames.
At the top, a gallery ring round the glass FINALS VAULT (100 frames on ten radial screens).
Writes sp_f2_hall.glb (wall, stair, frames, sconces), sp_f2_col.glb, sp_f2_vault.glb, sp_f2_vaultcol.glb, and
portrait models pf_0000..0999.glb / pv_000..099.glb + f2_layout.json (where every portrait hangs)."""
import math, json, random, os
import numpy as np
from glb import *
from kit import *

OUT = '/home/claude/spire/out/glb/'
POUT = '/home/claude/spire/out/portraits/'
os.makedirs(POUT, exist_ok=True)
rng = random.Random(1000)
LY = json.load(open('/home/claude/spire/out/layout.json'))
Y0 = LY['f2']; YTOP = LY['gallery']; TURNS = 6.5; RISE = (YTOP - Y0) / TURNS
R_WALL = 18.5; R_IN = 14.3; TH0 = 0.0                       # helix starts facing the front, climbs clockwise (seen from above)
PW, PH = 1.1, 1.1 * 533 / 384                                # vault portrait size (m)
PWH, PHH = 1.5, 1.5 * 533 / 384                              # hall portraits: 200 big ones, one row up the stair
N_HALL = 200; COLS_PER_TURN = 31.5; N_COLS = N_HALL
ROW_Y = (2.3,)                                               # portrait centre above the stair surface at the wall
IMGS = [821] + sorted(random.Random(62).sample([i for i in range(1000) if i != 821], N_HALL - 1))   # which of the 1000 forgeries hang (821 = the real one)
hall = Mesh(); col = Mesh()
SH = [hole_poly(lf['x'], lf['z'], LY['shaft_fp'], 1.04) for lf in LY['lifts']]        # the two lift shafts pass through the core

def ang_y(th):     # stair surface height at helix angle (degrees, from TH0)
    return Y0 + (th - TH0) / 360.0 * RISE
def polar(r, th, y): a = math.radians(th); return np.array([r * math.sin(a), y, r * math.cos(a)])

def frame(m, w, h, mm, depth=0.09, bw=0.13):
    """gilt picture frame swept round a w x h opening, facing +z, opening centred at the origin"""
    prof = [(0.0, 0.0), (0.012, 0.035), (0.04, 0.05), (0.07, 0.09), (0.1, 0.075), (bw, 0.06), (bw + 0.005, 0.0)]   # (outward, forward)
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
        # normals from the profile slope
        for j in range(len(prof)):
            j0, j1 = max(0, j - 1), min(len(prof) - 1, j + 1)
            dd = prof[j1][0] - prof[j0][0]; df = prof[j1][1] - prof[j0][1]
            side = np.array([y1 - y0, -(x1 - x0), 0.0]); side /= np.linalg.norm(side)        # outward in the frame plane
            n = side * (-df) + np.array([0, 0, 1.0]) * dd; n /= np.linalg.norm(n) + 1e-9
            N += [n, n]
        I = []
        for j in range(len(prof) - 1):
            a = 2 * j; I += [a, a + 1, a + 3, a, a + 3, a + 2]
        P_ = np.array(P); t = I[:3]; fn = np.cross(P_[t[1]] - P_[t[0]], P_[t[2]] - P_[t[0]])
        if np.dot(fn, N[t[0]]) < 0: I = list(np.array(I).reshape(-1, 3)[:, ::-1].reshape(-1))
        m.add('gold', P_, N, U, I, None, mm)
    # dark velvet mount behind the picture, and four corner rosettes
    quad(m, 'black', w + 0.04, h + 0.04, M(mm, T(0, 0, -0.005)))
    for (sx, sy) in outs:
        lathe(m, 'gold', [(0.0, 0.0), (0.05, 0.0), (0.045, 0.02), (0.0, 0.035)], 8, m=M(mm, T(sx * (w / 2 + 0.07), sy * (h / 2 + 0.07), 0.07), Rx(90)))

def sconce(m, mm):
    box(m, 'brass', 0.16, 0.24, 0.05, m=M(mm, T(0, 0, 0.025)))
    tube(m, 'brass', [(0, 0, 0.03), (0, -0.05, 0.2), (0, 0.06, 0.32)], 0.018, 6, m=mm)
    lathe(m, 'glow', [(0.0, 0.0), (0.07, 0.02), (0.09, 0.12), (0.06, 0.22), (0.0, 0.24)], 10, m=M(mm, T(0, 0.06, 0.32)))
    lathe(m, 'brass', [(0.1, 0.24), (0.02, 0.32)], 8, m=M(mm, T(0, 0.06, 0.32)))

# ------------------------------------------------------------------ the cylinder wall (inside face), with door openings
def cylinder_wall():
    doors = [(0, Y0, 3.4, 4.2)]                    # one door, at the front, out to the Floor 2 terrace
    seg = 160; y_bot = Y0; y_top = LY['f2top'] + 0.5
    for i in range(seg):
        a0 = 360 * i / seg; a1 = 360 * (i + 1) / seg; am = (a0 + a1) / 2
        spans = [(y_bot, y_top)]
        for (da, dy, dw, dh) in doors:
            half = math.degrees(dw / 2 / R_WALL)
            if abs((am - da + 180) % 360 - 180) < half:
                ns = []
                for lo, hi in spans:
                    if hi <= dy or lo >= dy + dh: ns.append((lo, hi))
                    else:
                        if lo < dy: ns.append((lo, dy))
                        if hi > dy + dh: ns.append((dy + dh, hi))
                spans = ns
        for lo, hi in spans:
            p = [polar(R_WALL, a0, lo), polar(R_WALL, a1, lo), polar(R_WALL, a1, hi), polar(R_WALL, a0, hi)]
            n0 = -polar(1, a0, 0); n1 = -polar(1, a1, 0)
            arc = 2 * math.pi * R_WALL / seg
            U = [[i * arc / 3, lo / 3], [(i + 1) * arc / 3, lo / 3], [(i + 1) * arc / 3, hi / 3], [i * arc / 3, hi / 3]]
            hall.add('dark', p, [n0, n1, n1, n0], U, [0, 2, 1, 0, 3, 2])
            # collider: the wall itself
            c = polar(R_WALL + 0.15, am, (lo + hi) / 2)
            collider_box(col, arc + 0.05, hi - lo, 0.3, M(T(*c), Ry(am)))
    # door tunnels through to the outer octagon (side faces at apothem 21)
    for (da, dy, dw, dh) in doors:
        for s in (-1, 1):
            a = math.radians(da); off = np.array([math.cos(a), 0, -math.sin(a)]) * s * dw / 2
            base = polar(R_WALL, da, dy) + off; end = polar(LY['A2'] - 0.1, da, dy) + off
            mid = (base + end) / 2; ln = np.linalg.norm(end - base)
            box(hall, 'plank', 0.3, dh, ln, m=M(T(mid[0], dy + dh / 2, mid[2]), Ry(da)))
            collider_box(col, 0.3, dh, ln, M(T(mid[0], dy + dh / 2, mid[2]), Ry(da)))
        mid = (polar(R_WALL, da, dy) + polar(LY['A2'], da, dy)) / 2
        box(hall, 'plank', dw, 0.12, LY['A2'] - R_WALL, m=M(T(mid[0], dy - 0.06, mid[2]), Ry(da)))
        box(hall, 'dark', dw + 0.6, 0.4, LY['A2'] - R_WALL, m=M(T(mid[0], dy + dh + 0.2, mid[2]), Ry(da)))
        collider_box(col, dw, 0.3, LY['A2'] - R_WALL + 0.4, M(T(mid[0], dy - 0.15, mid[2]), Ry(da)))
        # carved door frame on the hall side
        fm = M(T(*polar(R_WALL - 0.05, da, dy)), Ry(da + 180))
        for s in (-1, 1): bevel_box(hall, 'dark', 0.3, dh + 0.3, 0.3, 0.04, m=M(fm, T(s * (dw / 2 + 0.15), (dh + 0.3) / 2, 0)))
        bevel_box(hall, 'dark', dw + 0.9, 0.45, 0.35, 0.04, m=M(fm, T(0, dh + 0.3, 0)))
        quad(hall, 'gold', 1.0, 0.25, M(fm, T(0, dh + 0.3, 0.19)))

# ------------------------------------------------------------------ floor, helix, rails, frames
def hall_floor():
    deck(hall, [(R_WALL * 1.08 * math.sin(math.radians(a)), R_WALL * 1.08 * math.cos(math.radians(a))) for a in range(0, 360, 15)], Y0, rng, mat='bartop', joists=False, edge_mat='dark', holes=SH)
    slab_collider(col, Y0, ('c', R_WALL), holes=SH)
    # a glowing mudwater ring inlaid round the centre medallion
    lathe(hall, 'mudglow', [(7.5, Y0 + 0.01), (8.2, Y0 + 0.01)], 64)
    lathe(hall, 'gold', [(8.2, Y0 + 0.012), (8.35, Y0 + 0.012)], 64)
    lathe(hall, 'gold', [(7.35, Y0 + 0.012), (7.5, Y0 + 0.012)], 64)

def helix():
    steps_per_turn = 30; nsteps = int(TURNS * steps_per_turn)
    dth = 360.0 / steps_per_turn; srise = RISE / steps_per_turn
    for k in range(nsteps):
        th0 = TH0 + k * dth; th1 = th0 + dth; y = Y0 + (k + 1) * srise
        # tread: an annular sector, top + front riser + outer/inner edges; underside is the soffit
        sub = 6
        angs = np.linspace(th0, th1, sub + 1)
        top_out = [polar(R_WALL - 0.02, a, y) for a in angs]; top_in = [polar(R_IN, a, y) for a in angs]
        P = np.array(top_out + top_in); n = len(angs)
        U = np.array([[p[0] / 3, p[2] / 3] for p in P])
        I = []
        for j in range(sub): I += [j, j + 1, n + j + 1, j, n + j + 1, n + j]
        I = np.array(I).reshape(-1, 3)
        f = np.cross(P[I[0, 1]] - P[I[0, 0]], P[I[0, 2]] - P[I[0, 0]])
        if f[1] < 0: I = I[:, ::-1]
        hall.add('plank', P, [[0, 1, 0]] * len(P), U, I.reshape(-1), tint(rng, 0.1))
        # riser at the leading (low) edge
        r0 = polar(R_IN, th0, y - srise - 0.25); r1 = polar(R_WALL - 0.02, th0, y - srise - 0.25)
        r2 = polar(R_WALL - 0.02, th0, y); r3 = polar(R_IN, th0, y)
        Pr = np.array([r0, r1, r2, r3]); nr = -np.array([math.cos(math.radians(th0)), 0, -math.sin(math.radians(th0))])
        Ir = [0, 1, 2, 0, 2, 3]
        if np.dot(np.cross(Pr[1] - Pr[0], Pr[2] - Pr[0]), nr) < 0: Ir = [0, 2, 1, 0, 3, 2]
        hall.add('dark', Pr, [nr] * 4, [[0, 0], [1.3, 0], [1.3, 0.1], [0, 0.1]], Ir)
        # brass nosing
        tube(hall, 'brass', [polar(R_IN + 0.05, th0, y + 0.01), polar(R_WALL - 0.1, th0, y + 0.01)], 0.022, 5)
        # inner stringer face (the edge you see from the well)
        Ps = np.array([polar(R_IN, angs[j], yy) for j in range(n) for yy in (y - 0.55, y)])
        Is = []
        for j in range(sub): a = 2 * j; Is += [a, a + 2, a + 3, a, a + 3, a + 1]
        Is = np.array(Is).reshape(-1, 3)
        nn = [-polar(1, angs[j], 0) for j in range(n) for _ in (0, 1)]
        if np.dot(np.cross(Ps[Is[0, 1]] - Ps[Is[0, 0]], Ps[Is[0, 2]] - Ps[Is[0, 0]]), nn[0]) < 0: Is = Is[:, ::-1]
        hall.add('dark', Ps, nn, [[j / 3, yy] for j in range(n) for yy in (0, 0.2)], Is.reshape(-1))
    # soffit (underside) as one smooth helicoid strip, and the smooth walking ramp collider just under the treads
    seg = int(TURNS * 72)
    for surf, mat, dy in (('soffit', 'dark', -0.55), ('ramp', 'col', -0.02)):
        Ps = []; Us = []
        for i in range(seg + 1):
            th = TH0 + 360 * TURNS * i / seg; y = ang_y(th) + dy + (srise / 2 if surf == 'ramp' else 0)
            Ps += [polar(R_IN - (0.2 if surf == 'ramp' else 0), th, y), polar(R_WALL + (0.1 if surf == 'ramp' else 0), th, y)]; Us += [[i * 0.3, 0], [i * 0.3, 1.4]]
        Ps = np.array(Ps); Is = []
        for i in range(seg): a = 2 * i; Is += [a, a + 1, a + 3, a, a + 3, a + 2]
        Is = np.array(Is).reshape(-1, 3)
        f = np.cross(Ps[Is[0, 1]] - Ps[Is[0, 0]], Ps[Is[0, 2]] - Ps[Is[0, 0]])
        want = -1 if surf == 'soffit' else 1
        if f[1] * want < 0: Is = Is[:, ::-1]
        target = hall if surf == 'soffit' else col
        target.add(mat, Ps, [[0, want, 0]] * len(Ps), Us, Is.reshape(-1))
        if surf == 'ramp':   # ramp underside too, so it is solid from both sides
            col.add(mat, Ps - np.array([0, 0.25, 0]), [[0, -1, 0]] * len(Ps), Us, Is[:, ::-1].reshape(-1))
    # inner balustrade: turned posts every 4 steps, a brass-capped handrail following the helix, and a collider fence
    pts = []
    for i in range(seg + 1):
        th = TH0 + 360 * TURNS * i / seg; pts.append(polar(R_IN + 0.12, th, ang_y(th) + 1.05 + srise / 2))
    tube(hall, 'dark', pts, 0.07, 8)
    tube(hall, 'brass', [p + np.array([0, 0.075, 0]) for p in pts], 0.03, 6)
    lowpts = [p - np.array([0, 0.75, 0]) for p in pts]
    tube(hall, 'dark', lowpts, 0.035, 6)
    for k in range(0, nsteps, 1):
        th = TH0 + (k + 0.5) * dth; y = Y0 + (k + 1) * srise
        lathe(hall, 'dark', [(0.07, 0), (0.07, 0.08), (0.04, 0.14), (0.055, 0.5), (0.035, 0.8), (0.05, 0.92), (0.05, 1.0)], 8, m=T(*polar(R_IN + 0.12, th, y)))
        if k % 2 == 0:
            for t in (0.25, 0.75):
                thb = th0b = TH0 + (k + t) * dth
                box(hall, 'dark', 0.035, 0.75, 0.035, m=T(*polar(R_IN + 0.12, thb, y + 0.68)), faces='xXzZ')
    # collider fence on the inner edge (1.2 m tall), skipping the very top where the stair meets the landing
    for i in range(seg):
        th = TH0 + 360 * TURNS * (i + 0.5) / seg
        c = polar(R_IN + 0.12, th, ang_y(th) + 0.6 + srise / 2)
        arc = 2 * math.pi * (R_IN + 0.12) / 72
        collider_box(col, arc + 0.05, 1.3, 0.2, M(T(*c), Ry(th)))
    # outer skirting board against the wall
    sk = [polar(R_WALL - 0.04, TH0 + 360 * TURNS * i / seg, ang_y(TH0 + 360 * TURNS * i / seg) + srise / 2 + 0.12) for i in range(seg + 1)]
    tube(hall, 'dark', sk, 0.06, 4)

def portraits_layout():
    """where each of the 1000 portraits hangs: returns list of dicts (index, x, y, z, ry, turn)"""
    out = []
    dth = 360.0 / COLS_PER_TURN
    for c in range(N_COLS):
        th = TH0 + 2.2 + c * dth + dth / 2
        yb = ang_y(th) + RISE / 30 / 2
        for r, ry in enumerate(ROW_Y):
            p = polar(R_WALL - 0.06, th, yb + ry)
            out.append(dict(i=len(out), x=round(p[0], 3), y=round(p[1], 3), z=round(p[2], 3), ry=round((th + 180) % 360, 2), th=th))
    return out

def hang_frames(lay):
    for p in lay:
        mm = M(T(p['x'], p['y'], p['z']), Ry(p['ry']))
        frame(hall, PWH, PHH, mm)
    # a sconce between every 3rd pair of columns, between the two rows
    dth = 360.0 / COLS_PER_TURN
    for c in range(0, N_COLS):
        th = TH0 + 2.2 + c * dth
        yb = ang_y(th) + RISE / 60 + ROW_Y[0] - 0.2
        sconce(hall, M(T(*polar(R_WALL - 0.02, th, yb)), Ry(th + 180)))

# ------------------------------------------------------------------ the top: gallery ring + the glass finals vault
R_V = 9.0; YV = YTOP
VSPOKES = 10; V_PER_SIDE = 5

def gallery():
    # inner landing ring r 9.3 .. R_IN full circle, plus the outer band over the part of the last turn that has headroom
    deck(hall, [(R_IN * 1.02 * math.sin(math.radians(a)), R_IN * 1.02 * math.cos(math.radians(a))) for a in range(0, 360, 10)], YV, rng, mat='plank', joists=False, hole=(0, 0, R_V + 0.3), holes=SH)
    slab_collider(col, YV, ('c', R_IN), holes=[('c', 0, 0, R_V)] + SH, pad=0.3)
    band = [polar(R_WALL - 0.02, a, YV) for a in np.linspace(185, 335, 31)] + [polar(R_IN, a, YV) for a in np.linspace(335, 185, 31)]
    P = np.array(band); n = len(band) // 2
    I = []
    for j in range(n - 1): I += [j, j + 1, 2 * n - 2 - j, j, 2 * n - 2 - j, 2 * n - 1 - j]
    I = np.array(I).reshape(-1, 3)
    if np.cross(P[I[0, 1]] - P[I[0, 0]], P[I[0, 2]] - P[I[0, 0]])[1] < 0: I = I[:, ::-1]
    hall.add('plank', P, [[0, 1, 0]] * len(P), [[p[0] / 3, p[2] / 3] for p in P], I.reshape(-1))
    for a in np.arange(187.5, 335, 5):
        collider_box(col, 2 * math.pi * 16.4 / 72 + 0.1, 0.3, R_WALL - R_IN, M(T(*polar((R_IN + R_WALL) / 2, a, YV - 0.15)), Ry(a)))
    # railing on the open edge of the landing (where the band is missing) - from 335 round to 185 (through 0), skipping the stair arrival
    for a0, a1 in [(338, 360 + 150)]:
        pts = [(R_IN * math.sin(math.radians(a)), R_IN * math.cos(math.radians(a))) for a in np.linspace(a0, a1, 40)]
        railing(hall, pts, YV, rng, closed=False, post_every=2.5)
        for a in np.linspace(a0, a1, 40)[:-1]:
            collider_box(col, 2 * math.pi * R_IN / 144 * 1.2, 1.2, 0.25, M(T(*polar(R_IN, a + 1.25, YV + 0.6)), Ry(a)))

def vault():
    v = Mesh(); vc = Mesh()
    # floor: polished bar-top wood with a gold compass rose
    deck(v, [(R_V * 1.02 * math.sin(math.radians(a)), R_V * 1.02 * math.cos(math.radians(a))) for a in range(0, 360, 10)], YV + 0.02, rng, mat='bartop', joists=False, edge_mat='brass')
    lathe(v, 'mudglow', [(2.0, YV + 0.03), (2.4, YV + 0.03)], 48)
    # glass wall with brass mullions, a carved base and a brass ring beam; a door at 180 (where the stair arrives)
    H = 7.5
    for i in range(40):
        a0 = 9 * i; a1 = a0 + 9; am = a0 + 4.5
        door = abs(((am - 180) + 180) % 360 - 180) < 9
        p = [polar(R_V, a0, YV + 0.6), polar(R_V, a1, YV + 0.6), polar(R_V, a1, YV + H), polar(R_V, a0, YV + H)]
        n0 = polar(1, am, 0)
        if not door:
            v.add('vglass', p, [n0] * 4, [[0, 0], [1, 0], [1, 1], [0, 1]], [0, 1, 2, 0, 2, 3])
            collider_box(vc, 2 * math.pi * R_V / 40 + 0.05, H, 0.2, M(T(*polar(R_V, am, YV + H / 2)), Ry(am)))
            box(v, 'dark', 2 * math.pi * R_V / 40 + 0.02, 0.6, 0.35, m=M(T(*polar(R_V, am, YV + 0.3)), Ry(am)))
        cyl(v, 'brass', 0.06, H, 6, m=T(*polar(R_V, a0, YV)))
    lathe(v, 'brass', [(R_V - 0.15, YV + H), (R_V + 0.25, YV + H), (R_V + 0.25, YV + H + 0.35), (R_V - 0.15, YV + H + 0.35)], 64)
    # glass dome
    dome = [(R_V * math.cos(t), YV + H + 0.35 + 3.2 * math.sin(t)) for t in np.linspace(0, math.pi / 2, 10)]
    lathe(v, 'glass', dome, 40)
    for i in range(16):
        a = 22.5 * i
        tube(v, 'brass', [polar(R_V * math.cos(t), a, YV + H + 0.35 + 3.2 * math.sin(t)) for t in np.linspace(0, math.pi / 2, 10)], 0.05, 5)
    collider_box(vc, 2 * R_V, 0.2, 2 * R_V, T(0, YV + H + 0.4, 0))
    slab_collider(vc, YV + 0.02, ('c', R_V), pad=0.0)
    # the ten radial screens that carry the 100 portraits
    slots = []
    for s in range(VSPOKES):
        a = 360 * s / VSPOKES + 18
        sm = M(T(0, YV, 0), Ry(a))
        r0, r1 = 2.6, 8.2
        bevel_box(v, 'dark', 0.36, 4.6, r1 - r0, 0.05, m=M(sm, T(0, 2.3, (r0 + r1) / 2)), uvs=3.0)
        bevel_box(v, 'gold', 0.42, 0.14, r1 - r0 + 0.1, 0.03, m=M(sm, T(0, 4.66, (r0 + r1) / 2)))
        collider_box(vc, 0.4, 4.6, r1 - r0, M(sm, T(0, 2.3, (r0 + r1) / 2)))
        for side in (-1, 1):
            for k in range(V_PER_SIDE):
                row = 0 if k < 3 else 1; col_ = k if k < 3 else k - 3
                zz = r0 + 1.0 + col_ * 1.75 + (0.9 if row else 0)
                yy = 1.3 if row == 0 else 3.25
                mm = M(sm, T(side * 0.2, yy, zz), Ry(90 * side))
                frame(v, PW, PH, mm)
                p = mm @ np.array([0, 0, 0.005, 1])
                slots.append(dict(i=len(slots), x=round(p[0], 3), y=round(p[1], 3), z=round(p[2], 3), ry=round((a + 90 * side) % 360, 2)))
    # central plinth where the true card is unveiled at the end
    lathe(v, 'dark', [(0.0, YV), (1.6, YV), (1.6, YV + 0.25), (1.2, YV + 0.4), (0.9, YV + 1.1), (1.25, YV + 1.25), (0.0, YV + 1.25)], 24)
    lathe(v, 'gold', [(1.25, YV + 1.25), (1.32, YV + 1.32), (0.0, YV + 1.34)], 24)
    collider_box(vc, 2.4, 1.3, 2.4, T(0, YV + 0.65, 0))
    # the vault's underside, seen by everyone looking up the core (and by riders in the lifts):
    # a beamed soffit with brass rings and a great hanging chandelier of glowing jars
    lathe(v, 'dark', [(0.0, YV - 0.45), (R_V + 0.2, YV - 0.45)], 48, uvs_u=8)
    lathe(v, 'dark', [(R_V + 0.2, YV - 0.45), (R_V + 0.2, YV + 0.02)], 48, uvs_u=8)
    for i in range(16):
        a = 22.5 * i
        bevel_box(v, 'dark', 0.35, 0.5, R_V - 1.2, 0.04, m=M(Ry(a), T(0, YV - 0.7, (R_V + 1.2) / 2)), uvs=3.0)
        lathe(v, 'brass', [(0.0, 0.0), (0.1, 0.0), (0.06, -0.14), (0.0, -0.2)], 8, m=T(*polar(R_V - 0.4, a, YV - 0.95)))
    for r in (3.0, 6.0, R_V - 0.1):
        tube(v, 'brass', [polar(r, a, YV - 0.97) for a in np.linspace(0, 360, 65)], 0.06, 6)
    lathe(v, 'brass', [(0.0, YV - 0.45), (1.3, YV - 0.45), (1.1, YV - 0.8), (0.6, YV - 1.2), (0.35, YV - 1.5), (0.0, YV - 1.6)], 24)
    CY = YV - 6.0
    tube(v, 'iron', [(0, YV - 1.6, 0), (0, CY + 0.3, 0)], 0.06, 6)
    for (rr, nj, yy) in ((3.2, 16, CY), (2.0, 10, CY - 1.0), (0.9, 6, CY - 1.8)):
        lathe(v, 'brass', [(rr - 0.1, yy - 0.08), (rr + 0.1, yy - 0.08), (rr + 0.1, yy + 0.08), (rr - 0.1, yy + 0.08)], 48)
        for k in range(4):
            tube(v, 'iron', [polar(rr, 45 + 90 * k, yy), (0, CY + 0.3, 0)], 0.02, 4)
        for k in range(nj):
            p = polar(rr, 360 * k / nj, yy)
            tube(v, 'iron', [p, p - np.array([0, 0.35, 0])], 0.012, 4)
            lathe(v, 'glow', [(0.0, 0), (0.13, 0.03), (0.16, 0.22), (0.12, 0.36), (0.0, 0.4)], 10, m=T(*(p - np.array([0, 0.78, 0]))))
            lathe(v, 'brass', [(0.0, 0.36), (0.14, 0.4), (0.0, 0.46)], 8, m=T(*(p - np.array([0, 0.78, 0]))))
    lathe(v, 'brass', [(0.0, CY - 1.8), (0.25, CY - 2.0), (0.1, CY - 2.5), (0.0, CY - 2.7)], 12)
    sphere(v, 'glow', 0.22, 12, 8, m=T(0, CY - 2.85, 0))
    # brass chandelier ring
    lathe(v, 'brass', [(3.0, YV + H - 0.6), (3.15, YV + H - 0.6), (3.15, YV + H - 0.45), (3.0, YV + H - 0.45)], 48)
    for i in range(12):
        a = 30 * i; p = polar(3.08, a, YV + H - 0.45)
        lathe(v, 'glow', [(0, 0), (0.08, 0.05), (0.1, 0.2), (0.06, 0.32), (0, 0.34)], 8, m=T(*p))
    return v, vc, slots

def portrait_glbs(folder, prefix, ids, pw=PW, ph=PH):
    for i in ids:
        src = folder + 'p%04d.jpg' % i
        m = Mesh(); quad(m, 'pic', pw, ph, T(0, 0, 0))
        mats = {'pic': dict(tex=src, emis_tex=src, emis=(0.32, 0.32, 0.32), rough=0.55)}
        write(POUT + prefix % i, m, mats)

if __name__ == '__main__':
    cylinder_wall(); hall_floor(); helix()
    lay = portraits_layout(); hang_frames(lay); gallery()
    print('hall', write(OUT + 'sp_f2_hall.glb', hall, MATS), 'portraits', len(lay))
    print('col', write(OUT + 'sp_f2_col.glb', col, MATS))
    v, vc, slots = vault()
    VM = dict(MATS); VM['vglass'] = dict(color=(0.7, 0.85, 0.82, 0.07), metal=0.0, rough=0.02, alpha='BLEND', double=True)  # crystal clear once unfrosted
    print('vault', write(OUT + 'sp_f2_vault.glb', v, VM), 'slots', len(slots))
    print('vcol', write(OUT + 'sp_f2_vaultcol.glb', vc, MATS))
    json.dump({'hall': [{k: p[k] for k in ('x', 'y', 'z', 'ry')} for p in lay], 'vault': [{k: s[k] for k in ('x', 'y', 'z', 'ry')} for s in slots[:100]],
               'turns': TURNS, 'rise': RISE, 'r_wall': R_WALL, 'r_in': R_IN, 'y0': Y0, 'ytop': YTOP, 'th0': TH0, 'imgs': IMGS}, open('/home/claude/spire/out/f2_layout.json', 'w'))
    portrait_glbs('/home/claude/spire/out/hall/', 'pf_%04d.glb', IMGS, PWH, PHH)
    portrait_glbs('/home/claude/spire/out/vault/', 'pv_%03d.glb', range(100))
    print('portrait glbs done', len(os.listdir(POUT)))
