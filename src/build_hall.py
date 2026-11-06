"""MUDWATER SPIRE v2 - THE HALL OF FAKES tower (inside the rectangular hall).
Built round the tower centre, then moved to (TOWER x, z).
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
TW = LY['tower']; TX, TZ = TW['x'], TW['z']
Y0 = LY['FL']['hall']; YTOP = LY['FL']['gallery']; TURNS = 3.0; RISE = (YTOP - Y0) / TURNS
YCEIL = LY['FL']['cards'] - 0.45
R_WALL = 18.5; R_IN = 14.3; R_OUT = TW['ro']; TH0 = 180.0   # the stair starts at the back (facing the lifts) and arrives back there 3 turns up
PW, PH = 1.1, 1.1 * 533 / 384                                # vault portrait size (m)
PWH, PHH = 1.2, 1.2 * 533 / 384                              # hall portraits: 200, two rows up the stair
N_HALL = 200; N_COLS = N_HALL // 2; COLS_PER_TURN = N_COLS / 2.93
ROW_Y = (1.3, 3.1)                                           # portrait centres above the stair surface at the wall
BASE_DOORS = [180.0, 120.0]; TOP_DOORS = [180.0, 240.0]      # through the tower wall (degrees round the tower; 180 = towards the lifts)
IMGS = [821] + sorted(random.Random(62).sample([i for i in range(1000) if i != 821], N_HALL - 1))   # which of the 1000 forgeries hang (821 = the real one)
hall = Mesh(); col = Mesh()
SH = []

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
    doors = [(a, Y0, 3.0, 3.0) for a in BASE_DOORS] + [(a, YTOP, 3.0, 3.0) for a in TOP_DOORS]
    seg = 160; y_bot = Y0; y_top = YCEIL
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
            arc = 2 * math.pi * R_WALL / seg
            for (rr, sgn, mat) in ((R_WALL, -1, 'dark'), (R_OUT, 1, 'plank')):
                p = [polar(rr, a0, lo), polar(rr, a1, lo), polar(rr, a1, hi), polar(rr, a0, hi)]
                n0 = sgn * polar(1, a0, 0); n1 = sgn * polar(1, a1, 0)
                arc_r = 2 * math.pi * rr / seg
                U = [[i * arc_r / 3, lo / 3], [(i + 1) * arc_r / 3, lo / 3], [(i + 1) * arc_r / 3, hi / 3], [i * arc_r / 3, hi / 3]]
                idx = [0, 2, 1, 0, 3, 2] if sgn < 0 else [0, 1, 2, 0, 2, 3]
                hall.add(mat, p, [n0, n1, n1, n0], U, idx, tint(rng, 0.18) if mat == 'plank' else None)
            c = polar((R_WALL + R_OUT) / 2, am, (lo + hi) / 2)
            collider_box(col, 2 * math.pi * R_OUT / seg + 0.05, hi - lo, R_OUT - R_WALL + 0.1, M(T(*c), Ry(am)))
    # door jambs and lintels through the wall thickness, and carved frames on both faces
    for (da, dy, dw, dh) in doors:
        for s_ in (-1, 1):
            a = math.radians(da); off = np.array([math.cos(a), 0, -math.sin(a)]) * s_ * dw / 2
            base = polar(R_WALL, da, dy) + off; end = polar(R_OUT, da, dy) + off
            mid = (base + end) / 2; ln = np.linalg.norm(end - base)
            box(hall, 'dark', 0.3, dh, ln + 0.1, m=M(T(mid[0], dy + dh / 2, mid[2]), Ry(da)))
        mid = (polar(R_WALL, da, dy) + polar(R_OUT, da, dy)) / 2
        box(hall, 'dark', dw, 0.3, R_OUT - R_WALL + 0.1, m=M(T(mid[0], dy + dh + 0.15, mid[2]), Ry(da)))
        for rr, face in ((R_WALL - 0.05, da + 180), (R_OUT + 0.05, da)):
            fm = M(T(*polar(rr, da, dy)), Ry(face))
            for s_ in (-1, 1): bevel_box(hall, 'dark', 0.3, dh + 0.3, 0.3, 0.04, m=M(fm, T(s_ * (dw / 2 + 0.15), (dh + 0.3) / 2, 0)))
            bevel_box(hall, 'dark', dw + 0.9, 0.45, 0.35, 0.04, m=M(fm, T(0, dh + 0.3, 0)))
            quad(hall, 'gold', 1.0, 0.25, M(fm, T(0, dh + 0.3, 0.19)))
    # rough cypress posts round the outside, a belt at the gallery floor and moss
    for k in range(24):
        a = k * 15 + 7.5
        if any(abs((a - d + 180) % 360 - 180) < 6 for d in BASE_DOORS + TOP_DOORS): continue
        prof = [(0.3 + 0.04 * math.sin(t * 9 + k), (YCEIL - Y0) * t) for t in np.linspace(0, 1, 7)]
        lathe(hall, 'bark', prof, 8, m=T(*polar(R_OUT + 0.3, a, Y0)), uv_v=6.0)
    for yy in (Y0 + 4.6, YTOP - 0.2):
        lathe(hall, 'dark', [(R_OUT, yy - 0.25), (R_OUT + 0.35, yy - 0.25), (R_OUT + 0.35, yy + 0.25), (R_OUT, yy + 0.25)], 96)

# ------------------------------------------------------------------ floor, helix, rails, frames
def hall_floor():
    lathe(hall, 'mudglow', [(7.5, Y0 + 0.02), (8.2, Y0 + 0.02)], 64)
    lathe(hall, 'gold', [(8.2, Y0 + 0.022), (8.35, Y0 + 0.022)], 64)
    lathe(hall, 'gold', [(7.35, Y0 + 0.022), (7.5, Y0 + 0.022)], 64)

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
        yb = ang_y(th) + RISE / 60 + (ROW_Y[0] + ROW_Y[1]) / 2 - 0.15
        sconce(hall, M(T(*polar(R_WALL - 0.02, th, yb)), Ry(th + 180)))

# ------------------------------------------------------------------ the top: gallery ring + the glass finals vault
R_V = 11.0; YV = Y0; VH = 9.5; DOME = 3.2        # the FINALS ROOM: a tall glass rotunda filling the open middle of the spiral, on the hall floor
VSPOKES = 10; V_PER_SIDE = 5
R_BAL = 11.6                                       # the balcony ring at the top of the stair looks down onto the rotunda's dome

def gallery():
    """the balcony at the top of the stair: a ring from R_BAL to R_IN (railing on its inner edge), plus the band over the last turn"""
    deck(hall, [(R_IN * 1.02 * math.sin(math.radians(a)), R_IN * 1.02 * math.cos(math.radians(a))) for a in range(0, 360, 10)], YTOP, rng, mat='plank', joists=False, hole=(0, 0, R_BAL), flat=True)
    slab_collider(col, YTOP, ('c', R_IN), holes=[('c', 0, 0, R_BAL)], pad=0.3)
    lathe(hall, 'dark', [(R_BAL, YTOP - 0.45), (R_BAL, YTOP)], 64)
    b0, b1 = TH0 + 5, TH0 + 115
    band = [polar(R_WALL - 0.02, a, YTOP) for a in np.linspace(b0, b1, 31)] + [polar(R_IN, a, YTOP) for a in np.linspace(b1, b0, 31)]
    P = np.array(band); n = len(band) // 2
    I = []
    for j in range(n - 1): I += [j, j + 1, 2 * n - 2 - j, j, 2 * n - 2 - j, 2 * n - 1 - j]
    I = np.array(I).reshape(-1, 3)
    if np.cross(P[I[0, 1]] - P[I[0, 0]], P[I[0, 2]] - P[I[0, 0]])[1] < 0: I = I[:, ::-1]
    hall.add('plank', P, [[0, 1, 0]] * len(P), [[p[0] / 3, p[2] / 3] for p in P], I.reshape(-1))
    for a in np.arange(b0 + 2.5, b1, 5):
        collider_box(col, 2 * math.pi * 16.4 / 72 + 0.1, 0.3, R_WALL - R_IN, M(T(*polar((R_IN + R_WALL) / 2, a, YTOP - 0.15)), Ry(a)))
    for a0, a1 in [(b1 + 3, TH0 + 360 - 30)]:            # rail where the ring meets the open stair well
        pts = [(R_IN * math.sin(math.radians(a)), R_IN * math.cos(math.radians(a))) for a in np.linspace(a0, a1, 40)]
        railing(hall, pts, YTOP, rng, closed=False, post_every=2.5)
        for a in np.linspace(a0, a1, 40)[:-1]:
            collider_box(col, 2 * math.pi * R_IN / 144 * 1.2, 1.2, 0.25, M(T(*polar(R_IN, a + 1.25, YTOP + 0.6)), Ry(a)))
    pts = [(R_BAL * math.sin(math.radians(a)), R_BAL * math.cos(math.radians(a))) for a in np.linspace(0, 360, 73)]
    railing(hall, pts, YTOP, rng, closed=False, post_every=2.0, mat='dark', top='pale')
    for a in np.arange(0, 360, 5):
        collider_box(col, 2 * math.pi * R_BAL / 72 + 0.05, 1.2, 0.25, M(T(*polar(R_BAL, a + 2.5, YTOP + 0.6)), Ry(a + 2.5)))

def vault():
    v = Mesh(); vc = Mesh()
    lathe(v, 'mudglow', [(2.2, YV + 0.03), (2.6, YV + 0.03)], 48)
    lathe(v, 'gold', [(R_V - 0.4, YV + 0.031), (R_V - 0.25, YV + 0.031)], 96)
    H = VH; NP = 48
    for i in range(NP):
        a0 = 360 * i / NP; a1 = a0 + 360 / NP; am = (a0 + a1) / 2
        door = abs(((am - 180) + 180) % 360 - 180) < 360 / NP
        p = [polar(R_V, a0, YV + 0.6), polar(R_V, a1, YV + 0.6), polar(R_V, a1, YV + H), polar(R_V, a0, YV + H)]
        n0 = polar(1, am, 0)
        arc = 2 * math.pi * R_V / NP
        if not door:
            v.add('vglass', p, [n0] * 4, [[0, 0], [1, 0], [1, 1], [0, 1]], [0, 1, 2, 0, 2, 3])
            collider_box(vc, arc + 0.05, H, 0.2, M(T(*polar(R_V, am, YV + H / 2)), Ry(am)))
            box(v, 'dark', arc + 0.02, 0.6, 0.35, m=M(T(*polar(R_V, am, YV + 0.3)), Ry(am)))
        else:      # glass above the door
            p = [polar(R_V, a0, YV + 3.2), polar(R_V, a1, YV + 3.2), polar(R_V, a1, YV + H), polar(R_V, a0, YV + H)]
            v.add('vglass', p, [n0] * 4, [[0, 0], [1, 0], [1, 1], [0, 1]], [0, 1, 2, 0, 2, 3])
            collider_box(vc, arc + 0.05, H - 3.0, 0.2, M(T(*polar(R_V, am, YV + 3.0 + (H - 3.0) / 2)), Ry(am)))
        cyl(v, 'brass', 0.07, H, 6, m=T(*polar(R_V, a0, YV)))
    for yy in (YV + H, YV + H * 0.5):
        lathe(v, 'brass', [(R_V - 0.15, yy), (R_V + 0.25, yy), (R_V + 0.25, yy + 0.3), (R_V - 0.15, yy + 0.3)], 96)
    collider_box(vc, 2 * R_V, 0.2, 2 * R_V, T(0, YV + H + 0.4, 0))      # no dome, but an invisible lid so nobody can jump in off the stair
    # ten radial screens, spread wide (4 m to 9.6 m out) so the finalists have room to move
    slots = []
    for s in range(VSPOKES):
        a = 360 * s / VSPOKES + 18
        sm = M(T(0, YV, 0), Ry(a))
        r0, r1 = 4.0, 9.6
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
    lathe(v, 'dark', [(0.0, YV), (1.6, YV), (1.6, YV + 0.25), (1.2, YV + 0.4), (0.9, YV + 1.1), (1.25, YV + 1.25), (0.0, YV + 1.25)], 24)
    lathe(v, 'gold', [(1.25, YV + 1.25), (1.32, YV + 1.32), (0.0, YV + 1.34)], 24)
    collider_box(vc, 2.4, 1.3, 2.4, T(0, YV + 0.65, 0))
    # the great chandelier hangs from the tower's ceiling into the open core, over the dome
    CY = YCEIL - 4.5
    tube(v, 'iron', [(0, YCEIL, 0), (0, CY + 0.3, 0)], 0.07, 6)
    for (rr, nj, yy) in ((4.2, 20, CY), (2.8, 14, CY - 1.0), (1.4, 8, CY - 1.8)):
        lathe(v, 'brass', [(rr - 0.1, yy - 0.08), (rr + 0.1, yy - 0.08), (rr + 0.1, yy + 0.08), (rr - 0.1, yy + 0.08)], 48)
        for k in range(4):
            tube(v, 'iron', [polar(rr, 45 + 90 * k, yy), (0, CY + 0.3, 0)], 0.02, 4)
        for k in range(nj):
            p = polar(rr, 360 * k / nj, yy)
            tube(v, 'iron', [p, p - np.array([0, 0.35, 0])], 0.012, 4)
            lathe(v, 'glow', [(0.0, 0), (0.13, 0.03), (0.16, 0.22), (0.12, 0.36), (0.0, 0.4)], 10, m=T(*(p - np.array([0, 0.78, 0]))))
            lathe(v, 'brass', [(0.0, 0.36), (0.14, 0.4), (0.0, 0.46)], 8, m=T(*(p - np.array([0, 0.78, 0]))))
    sphere(v, 'glow', 0.3, 12, 8, m=T(0, CY - 2.6, 0))
    return v, vc, slots

def portrait_glbs(folder, prefix, ids, pw=PW, ph=PH):
    for i in ids:
        src = folder + 'p%04d.jpg' % i
        m = Mesh(); quad(m, 'pic', pw, ph, T(0, 0, 0))
        mats = {'pic': dict(tex=src, emis_tex=src, emis=(0.32, 0.32, 0.32), rough=0.55)}
        write(POUT + prefix % i, m, mats)

def frost_sleeve():
    m = Mesh(); RV = R_V + 0.12
    lathe(m, 'frost', [(RV, 0.6), (RV, VH + 0.3)], 64, uvs_u=10)
    lathe(m, 'frostrim', [(RV - 0.04, 0.6), (RV + 0.03, 0.6), (RV + 0.03, 0.66), (RV - 0.04, 0.66)], 64)
    lathe(m, 'frost', [(0.0, VH + 0.45), (RV, VH + 0.45)], 48)       # a frosted lid so the cards can't be studied from the stair above
    mats = dict(MATS)
    mats['frost'] = dict(tex=TEX + 'glass.png', color=(0.9, 0.95, 0.93, 0.93), emis=(0.12, 0.14, 0.13), rough=0.9, alpha='BLEND', double=True)
    mats['frostrim'] = dict(color=(0.85, 0.9, 0.88, 1), rough=0.6)
    print('frost', write(OUT + 'sp_vault_frost.glb', m, mats))

def vault_door():
    m = Mesh(); W_, H_ = 2.8, 3.0
    quad(m, 'vglass', W_, H_, T(0, H_ / 2, 0), double=True)
    for s_ in (-1, 1): box(m, 'brass', 0.08, H_, 0.1, m=T(s_ * W_ / 2, H_ / 2, 0))
    for yy in (0.04, H_ - 0.04, H_ / 2): box(m, 'brass', W_, 0.08, 0.1, m=T(0, yy, 0))
    mats = dict(MATS); mats['vglass'] = VGLASS
    print('door', write(OUT + 'sp_vault_door.glb', m, mats))

VGLASS = dict(color=(0.7, 0.85, 0.82, 0.07), metal=0.0, rough=0.02, alpha='BLEND', double=True)
if __name__ == '__main__':
    cylinder_wall(); hall_floor(); helix()
    lay = portraits_layout(); hang_frames(lay); gallery()
    v, vc, slots = vault()
    MV = T(TX, 0, TZ)
    def moved(m): out = Mesh(); out.merge(m, MV); return out
    print('hall', write(OUT + 'sp_f2_hall.glb', moved(hall), MATS), 'portraits', len(lay))
    print('col', write(OUT + 'sp_f2_col.glb', moved(col), MATS))
    VM = dict(MATS); VM['vglass'] = VGLASS
    print('vault', write(OUT + 'sp_f2_vault.glb', moved(v), VM), 'slots', len(slots))
    print('vcol', write(OUT + 'sp_f2_vaultcol.glb', moved(vc), MATS))
    frost_sleeve(); vault_door()
    off = lambda p: {'x': round(p['x'] + TX, 3), 'y': p['y'], 'z': round(p['z'] + TZ, 3), 'ry': p['ry']}
    dpos = polar(R_V, 180, YV)
    L2 = dict(rbal=R_BAL, ytop=YTOP, vh=VH, dome=DOME)
    json.dump({'hall': [off(p) for p in lay], 'vault': [off(s_) for s_ in slots[:100]], 'imgs': IMGS, 'tower': [TX, TZ], 'r_v': R_V, 'yv': YV,
               'door': [round(dpos[0] + TX, 3), YV, round(dpos[2] + TZ, 3), 180], 'extra': L2, 'plinth': [TX, YV + 1.34, TZ], 'turns': TURNS, 'rise': RISE, 'th0': TH0},
              open('/home/claude/spire/out/f2_layout.json', 'w'))
    if '--portraits' in __import__('sys').argv:
        portrait_glbs('/home/claude/spire/out/hall/', 'pf_%04d.glb', IMGS, PWH, PHH)
