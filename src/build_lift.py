"""MUDWATER SPIRE - the two interior lifts (the showpiece).
Both rise through the hollow core of the Floor 2 helix stair, either side of the glass vault, so riders climb
through the thousand portraits. Octagonal glass-and-brass shafts, carved landing portals with sunburst fans and
floor dials, a machine head on top (sheave, bull gear, pinion, flywheel, flyball governor), counterweights,
cables, and an ornate octagonal birdcage cab (tufted bench, operator's lever, crown gears, stained-glass cupola).

Static (world space):   sp_liftA_shaft.glb  sp_liftB_shaft.glb   + sp_lift_col.glb (shafts, collars, both lifts)
Moving parts (local):   sp_liftA_cab.glb / sp_liftB_cab.glb  (origin = cab floor centre, door faces +z)
                        sp_lift_cab_col.glb      cab floor + walls (door side open)
                        sp_lift_cgate.glb        one cab gate leaf (scissor lattice; hinge at x=0, leaf runs to -x; scale x to fold)
                        sp_lift_lgate.glb        one landing gate leaf (same idea, taller)
                        sp_lift_cgate_col.glb / sp_lift_lgate_col.glb   gate colliders (toggle when open)
                        sp_lift_sheave.glb       sheave + bull gear + flywheel (spins about local x)
                        sp_lift_pinion.glb       pinion + motor shaft (spins about local x, opposite way, faster)
                        sp_lift_gov.glb          flyball governor (spins about local y)
                        sp_lift_cabgear.glb      crown gear on the cab roof (spins about local x)
                        sp_lift_cable.glb        four steel ropes, 1 m long hanging down from y=0 (scale y)
                        sp_lift_cw.glb           counterweight (origin = top hitch)
                        sp_lift_needle.glb       dial needle (pivot at origin, points +y; rotate z)
                        sp_lift_lever.glb        operator's lever (pivot at origin; rotate x)
                        sp_lift_call.glb / sp_lift_callglow.glb   call button plate / its lit halo
out/lift_layout.json carries every position the MML needs (stops, gate hinges, dial needles, cables, counterweight rule)."""
import math, json, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from glb import *
from kit import *

OUT = '/home/claude/spire/out/glb/'
TMP = '/home/claude/spire/out/sprite_png/'
os.makedirs(TMP, exist_ok=True)
LY = json.load(open('/home/claude/spire/out/layout.json'))
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
INTERB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
rng = random.Random(77)

SA = LY['shaft_apo']; CA = LY['cab_apo']; BASE = LY['shaft_base']; TOP = LY['shaft_top']
DW = LY['door_w']; DH = LY['door_h']
FP = [tuple(p) for p in LY['shaft_fp']]
FLOORS = LY['floors_through']                                     # floors the shafts pass through (F1 is the base)
NAMES = {'lounge': 'THE LOUNGE', 'hall': 'HALL OF FAKES', 'gallery': 'THE GALLERY', 'cards': 'MUD ROYALE', 'rooms': 'GROUP MUD', 'roof': 'THE ROOF DECK'}
DIAL = {'lounge': '1', 'hall': '2', 'gallery': 'G', 'cards': '3', 'rooms': '4', 'roof': 'R'}
SHEAVE_R = 1.3; SHEAVE_Y = TOP + 1.6; SHEAVE_Z = -SHEAVE_R - 0.01     # cab ropes drop at z 0, counterweight ropes at z -2.61
HITCH = 4.35                                                          # cab floor -> rope hitch on the crown
CW_Z = SHEAVE_Z - SHEAVE_R

M_ = dict(MATS)
M_['steel'] = dict(color=(0.62, 0.62, 0.64, 1), metal=1.0, rough=0.3)
M_['glassL'] = dict(color=(0.6, 0.82, 0.76, 0.13), rough=0.04, alpha='BLEND', double=True)
M_['stained'] = dict(tex=TEX + 'mudglow.jpg', emis_tex=TEX + 'mudglow.jpg', emis=(1.0, 0.85, 0.55), emis_strength=1.6, rough=0.3)
M_['jewel'] = dict(color=(1.0, 0.55, 0.15, 1), emis=(1.0, 0.5, 0.1), emis_strength=3.0, rough=0.2)
M_['halo'] = dict(color=(1.0, 0.75, 0.3, 0.55), emis=(1.0, 0.7, 0.25), emis_strength=2.5, alpha='BLEND', unlit=True, double=True)
M_['redlamp'] = dict(color=(1.0, 0.25, 0.1, 1), emis=(1.0, 0.2, 0.05), emis_strength=3.0)

# ------------------------------------------------------------------------------------------------ small helpers
def lora(size):
    f = ImageFont.truetype(LORA, size)
    try: f.set_variation_by_name('Bold')
    except Exception: pass
    return f

def face_frame(corners, i, y=0.0, base=None):
    """matrix at the middle of octagon face i: local x along the face, local z outward, y up"""
    p0 = np.array(corners[i]); p1 = np.array(corners[(i + 1) % len(corners)])
    mid = (p0 + p1) / 2; n = mid / np.linalg.norm(mid); t = (p1 - p0) / np.linalg.norm(p1 - p0)
    if (-t[1]) * n[0] + t[0] * n[1] < 0: t = -t
    m = np.eye(4); m[:3, 0] = (t[0], 0, t[1]); m[:3, 1] = (0, 1, 0); m[:3, 2] = (n[0], 0, n[1]); m[:3, 3] = (mid[0], y, mid[1])
    return (m if base is None else base @ m), float(np.linalg.norm(p1 - p0))

def octprism(m, mat, apo, y0, y1, mm=None, uvs=1.0):
    R = apo / math.cos(math.radians(22.5))
    lathe(m, mat, [(0.0, y0), (R, y0), (R, y1), (0.0, y1)], 8, m=mm, a0=22.5, a1=382.5, smooth=False, uvs_u=uvs)

def seg_box(m, mat, p0, p1, w, h=None, uvs=1.0):
    p0 = np.asarray(p0, float)[:3]; p1 = np.asarray(p1, float)[:3]; d = p1 - p0
    box(m, mat, w, h or w, np.linalg.norm(d), m=M(T(*((p0 + p1) / 2)), look_basis(d)), uvs=uvs)

def lantern(m, mm, s=1.0):
    """caged jar lantern hanging from a little brass hook at the local origin"""
    tube(m, 'brass', [(0, 0, 0), (0, -0.06 * s, 0)], 0.012 * s, 5, m=mm)
    lathe(m, 'brass', [(0.0, -0.06 * s), (0.11 * s, -0.12 * s), (0.12 * s, -0.14 * s), (0.0, -0.14 * s)], 8, m=mm)
    lathe(m, 'glow', [(0.0, -0.14 * s), (0.08 * s, -0.16 * s), (0.1 * s, -0.3 * s), (0.08 * s, -0.42 * s), (0.0, -0.44 * s)], 10, m=mm)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        tube(m, 'brass', [(0.11 * s * math.sin(a), -0.14 * s, 0.11 * s * math.cos(a)), (0.115 * s * math.sin(a), -0.3 * s, 0.115 * s * math.cos(a)),
                          (0.09 * s * math.sin(a), -0.44 * s, 0.09 * s * math.cos(a))], 0.008 * s, 4, m=mm)
    lathe(m, 'brass', [(0.0, -0.44 * s), (0.1 * s, -0.45 * s), (0.04 * s, -0.5 * s), (0.0, -0.52 * s)], 8, m=mm)

def wall_lantern(m, mm, s=1.0):
    """bracket lantern on a wall facing +z local"""
    box(m, 'brass', 0.12 * s, 0.2 * s, 0.03 * s, m=M(mm, T(0, 0, 0.015 * s)))
    tube(m, 'brass', [(0, 0.04 * s, 0.03 * s), (0, 0.12 * s, 0.16 * s), (0, 0.1 * s, 0.26 * s)], 0.014 * s, 5, m=mm)
    lantern(m, M(mm, T(0, 0.1 * s, 0.26 * s)), s)

def spiral(m, mat, cx, cy, r0, r1, turns, mm, flip=1, rr=0.012, n=20):
    pts = []
    for k in range(n):
        t = k / (n - 1); a = flip * (t * turns * 2 * math.pi); r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a) * flip, cy + r * math.sin(a), 0))
    tube(m, mat, pts, rr, 5, m=mm)

def gear(m, mat, r, teeth, th, mm=None, rim=None, spokes=6, hub=None, tooth=None, spoke_mat=None):
    """spur gear in the local XY plane, axle along local z, centred at the origin"""
    td = tooth or max(0.03, r * 0.1); rr = r - td; rim = rim or max(0.05, r * 0.16); ri = rr - rim
    p = 2 * math.pi / teeth; O = []
    for k in range(teeth):
        a = k * p
        for (fa, rad) in ((0.0, rr), (0.18, rr), (0.33, r), (0.62, r), (0.77, rr)):
            O.append((rad, a + fa * p))
    O = [(rad * math.cos(a), rad * math.sin(a), a) for rad, a in O]
    n = len(O); I = [(ri * math.cos(a), ri * math.sin(a)) for (_, _, a) in O]
    for z, nz in ((th / 2, 1), (-th / 2, -1)):
        P = [(x, y, z) for (x, y, _) in O] + [(x, y, z) for (x, y) in I]
        idx = []
        for j in range(n):
            j1 = (j + 1) % n; idx += [j, j1, n + j1, j, n + j1, n + j]
        idx = np.array(idx).reshape(-1, 3); P_ = np.array(P)
        f = np.cross(P_[idx[0, 1]] - P_[idx[0, 0]], P_[idx[0, 2]] - P_[idx[0, 0]])
        if f[2] * nz < 0: idx = idx[:, ::-1]
        m.add(mat, P, [[0, 0, nz]] * len(P), [[x / r * 0.5 + 0.5, y / r * 0.5 + 0.5] for (x, y, _) in P], idx.reshape(-1), None, mm)
    for ring, sgn in ((O, 1), ([(x, y, 0) for (x, y) in I], -1)):
        for j in range(n):
            a = ring[j]; b = ring[(j + 1) % n]
            e = np.array([b[0] - a[0], b[1] - a[1], 0.0]); nn = np.array([e[1], -e[0], 0.0]); nn /= np.linalg.norm(nn) + 1e-12
            mid = np.array([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0])
            if np.dot(nn, mid) * sgn < 0: nn = -nn
            P = np.array([[a[0], a[1], -th / 2], [b[0], b[1], -th / 2], [b[0], b[1], th / 2], [a[0], a[1], th / 2]])
            idx = [0, 1, 2, 0, 2, 3] if np.dot(np.cross(P[1] - P[0], P[2] - P[0]), nn) > 0 else [0, 2, 1, 0, 3, 2]
            m.add(mat, P, [nn] * 4, [[0, 0], [1, 0], [1, 0.2], [0, 0.2]], idx, None, mm)
    hub = hub or r * 0.18
    for k in range(spokes):
        a = 2 * math.pi * k / spokes + p / 2
        bevel_box(m, spoke_mat or mat, rim * 0.7, (ri - hub) + 0.04, th * 0.6, 0.01, m=M(mm if mm is not None else np.eye(4), Rz(math.degrees(a) - 90), T(0, hub + (ri - hub) / 2, 0)))
    lathe(m, spoke_mat or mat, [(0.0, -th * 0.8), (hub, -th * 0.8), (hub * 1.15, 0), (hub, th * 0.8), (0.0, th * 0.8)], 12, m=M(mm if mm is not None else np.eye(4), Rx(90)))

# ------------------------------------------------------------------------------------------------ painted textures
def dial_tex(keys, name):
    W, H = 640, 360; img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    cx, cy, R = W // 2, H - 24, 300
    d.pieslice((cx - R, cy - R, cx + R, cy + R), 180, 360, fill=(150, 104, 36, 255))
    d.pieslice((cx - R + 16, cy - R + 16, cx + R - 16, cy + R - 16), 180, 360, fill=(208, 160, 70, 255))
    d.pieslice((cx - R + 30, cy - R + 30, cx + R - 30, cy + R - 30), 180, 360, fill=(244, 232, 200, 255))
    d.rectangle((cx - R, cy, cx + R, H), fill=(150, 104, 36, 255))
    angs = dial_angles(len(keys)); f = lora(64)
    for a in np.linspace(-80, 80, 33):
        r0 = R - 46 if abs(a) % 20 < 1 else R - 40
        x0 = cx + r0 * math.sin(math.radians(a)); y0 = cy - r0 * math.cos(math.radians(a))
        x1 = cx + (R - 32) * math.sin(math.radians(a)); y1 = cy - (R - 32) * math.cos(math.radians(a))
        d.line((x0, y0, x1, y1), fill=(90, 60, 24, 255), width=3)
    for k, a in zip(keys, angs):
        t = DIAL[k]; x = cx + (R - 100) * math.sin(math.radians(a)); y = cy - (R - 100) * math.cos(math.radians(a))
        d.ellipse((x - 44, y - 44, x + 44, y + 44), fill=(24, 96, 84, 255), outline=(150, 104, 36, 255), width=5)
        tw = d.textlength(t, font=f); d.text((x - tw / 2, y - 42), t, font=f, fill=(250, 232, 180, 255))
    d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(120, 82, 26, 255))
    p = TMP + 'lift_dial_%s.png' % name; img.save(p); return p, W / H

def dial_angles(n):
    return [0.0] if n == 1 else list(np.linspace(-62, 62, n))

def plaque_tex(title, sub, name):
    W, H = 1400, 330
    wood = Image.open(TEX + 'wood_dark.jpg').convert('RGB').resize((W, W)).crop((0, 0, W, H))
    d = ImageDraw.Draw(wood)
    d.rounded_rectangle((18, 18, W - 18, H - 18), 26, outline=(214, 160, 70), width=8)
    d.rounded_rectangle((36, 36, W - 36, H - 36), 18, outline=(150, 104, 36), width=3)
    f = lora(118); fs = ImageFont.truetype(INTERB, 46)
    tw = d.textlength(title, font=f)
    if tw > W - 140: f = lora(int(118 * (W - 140) / tw)); tw = d.textlength(title, font=f)
    d.text(((W - tw) / 2 + 4, 66 + 4), title, font=f, fill=(20, 10, 4))
    d.text(((W - tw) / 2, 66), title, font=f, fill=(244, 206, 120))
    sw = d.textlength(sub, font=fs); d.text(((W - sw) / 2, 228), sub, font=fs, fill=(150, 220, 200))
    for x in (90, W - 90): d.ellipse((x - 16, H / 2 - 16, x + 16, H / 2 + 16), fill=(214, 160, 70))
    p = TMP + 'lift_plaque_%s.jpg' % name; wood.save(p, quality=90); return p, W / H

# ------------------------------------------------------------------------------------------------ the shaft (world space)
def shaft(lift, sm, col):
    cx, cz = lift['x'], lift['z']; B = T(cx, 0, cz)
    stops = lift['stops']; keys = [LY['stop_names'][str(s)] for s in stops]
    C = octa(SA)
    door_open = [(s, s + DH + 0.08) for s in stops]
    bands = sorted(set([BASE + 4 * k for k in range(int((TOP - BASE) / 4) + 1)] + [s + DH + 0.1 for s in stops] + [TOP]))
    # -- corner columns with brass collars, and the counterweight bay posts
    for k, (x, z) in enumerate(C):
        a = math.degrees(math.atan2(x, z))
        bevel_box(sm, 'iron', 0.18, TOP - BASE, 0.18, 0.03, m=M(B, T(x, (BASE + TOP) / 2, z), Ry(a)), uvs=2.0)
        for y in np.arange(BASE + 1.0, TOP, 2.0):
            lathe(sm, 'brass', [(0.12, y - 0.05), (0.15, y - 0.02), (0.15, y + 0.02), (0.12, y + 0.05)], 8, m=M(B, T(x, 0, z)))
        lathe(sm, 'brass', [(0.0, TOP), (0.16, TOP), (0.12, TOP + 0.18), (0.05, TOP + 0.32), (0.0, TOP + 0.36)], 8, m=M(B, T(x, 0, z)))
    bay = [(FP[3][0], FP[3][1]), (FP[4][0], FP[4][1])]               # the two outer back corners of the counterweight bay
    for (x, z) in bay:
        bevel_box(sm, 'iron', 0.14, TOP - BASE, 0.14, 0.02, m=M(B, T(x, (BASE + TOP) / 2, z)), uvs=2.0)
    # faces of the outer skin: the 7 octagon faces (not the back), plus the 3 faces of the bay
    faces = []
    for i in range(8):
        if i == 3: continue
        faces.append((C[i], C[(i + 1) % 8], i == 7))
    faces += [(C[3], bay[0], False), (bay[0], bay[1], False), (bay[1], C[4], False)]
    for (p0, p1, is_door) in faces:
        mm0, ln = place(p0, p1, 0)
        # vertical spans that get glass
        spans = [(BASE, TOP)]
        if is_door: spans = subtract(spans, door_open)
        for (y0, y1) in spans:
            cuts = [b for b in bands if y0 < b < y1]
            ys = [y0] + cuts + [y1]
            for a, b in zip(ys[:-1], ys[1:]):
                if b - a < 0.05: continue
                quad(sm, 'glassL', ln - 0.06, b - a, M(B, mm0, T(ln / 2, (a + b) / 2, 0)), double=True)
                if ln > 1.0: box(sm, 'brass', 0.035, b - a, 0.035, m=M(B, mm0, T(ln / 2, (a + b) / 2, 0)))
            collider_box(col, ln + 0.1, y1 - y0, 0.14, M(B, mm0, T(ln / 2, (y0 + y1) / 2, 0)))
        for y in bands:
            if is_door and any(lo + 0.01 < y < hi - 0.01 for lo, hi in door_open): continue
            bevel_box(sm, 'brass', ln + 0.04, 0.1, 0.09, 0.015, m=M(B, mm0, T(ln / 2, y, 0)))
        # decorative ironwork: scroll pairs on every band at the stops' heights and just under the top
        for y in [s + DH + 0.1 for s in stops] + [TOP]:
            if ln < 1.0: continue
            for f in (-1, 1):
                spiral(sm, 'iron', ln / 2 + f * 0.24, y - 0.24, 0.2, 0.03, 1.4, M(B, mm0, T(0, 0, 0.03)), flip=f, rr=0.014, n=18)
    # counterweight guide rails inside the bay + buffer springs at the bottom
    for sx in (-0.62, 0.62):
        bevel_box(sm, 'iron', 0.08, TOP - BASE, 0.16, 0.01, m=M(B, T(sx, (BASE + TOP) / 2, CW_Z)), uvs=2.0)
        pts = [(sx * 0.6 + 0.09 * math.cos(t), BASE + 0.15 + t / (2 * math.pi) * 0.09, CW_Z + 0.09 * math.sin(t)) for t in np.linspace(0, 2 * math.pi * 6, 90)]
        tube(sm, 'steel', [M(B) @ np.array([*p, 1]) for p in pts], 0.018, 5) if False else tube(sm, 'steel', [np.array(p) + np.array([cx, 0, cz]) for p in pts], 0.018, 5)
        cyl(sm, 'iron', 0.13, 0.15, 10, m=M(B, T(sx * 0.6, BASE, CW_Z)))
    # base: a polished mud-stone and brass plinth ring round the shaft on the lounge floor
    Rp = SA + 0.32
    for (p0, p1, is_door) in faces:
        mm0, ln = place(p0, p1, BASE)
        if is_door: continue
        bevel_box(sm, 'dark', ln + 0.06, 0.32, 0.1, 0.02, m=M(B, mm0, T(ln / 2, 0.16, 0.06)))
        box(sm, 'brass', ln + 0.08, 0.035, 0.12, m=M(B, mm0, T(ln / 2, 0.33, 0.06)))
    # skirting where the shaft passes through each upper floor (inc. non-stops)
    for y in FLOORS:
        for (p0, p1, is_door) in faces:
            if is_door and y in stops: continue
            mm0, ln = place(p0, p1, y)
            bevel_box(sm, 'dark', ln + 0.06, 0.26, 0.1, 0.02, m=M(B, mm0, T(ln / 2, 0.13, 0.06)))
            box(sm, 'brass', ln + 0.08, 0.03, 0.12, m=M(B, mm0, T(ln / 2, 0.27, 0.06)))
        # collar collider: closes the slack between the floor hole and the shaft
        hp = [(cx + x * 1.04, cz + z * 1.04) for (x, z) in FP]
        for k in range(len(hp)):
            a = np.array(hp[k]); b = np.array(hp[(k + 1) % len(hp)]); mid = (a + b) / 2; e = b - a; ln = np.linalg.norm(e)
            nrm = np.array([e[1], -e[0]]) / ln
            if np.dot(nrm, mid - np.array([cx, cz])) < 0: nrm = -nrm
            c = mid + nrm * 0.35; ang = math.degrees(math.atan2(e[0], e[1]))
            collider_box(col, 0.7, 0.3, ln + 0.6, M(T(c[0], y - 0.15, c[1]), Ry(ang)))
    # landing portals
    dial_p, dial_asp = dial_tex(keys, lift['id'])
    M_['dial_' + lift['id']] = dict(tex=dial_p, emis_tex=dial_p, emis=(0.35, 0.32, 0.26), alpha='BLEND', rough=0.4)
    out = []
    for s, key in zip(stops, keys):
        pp, pasp = plaque_tex(NAMES[key], lift['name'].upper(), lift['id'] + '_' + key)
        M_['plq_%s_%s' % (lift['id'], key)] = dict(tex=pp, emis_tex=pp, emis=(0.4, 0.36, 0.3), rough=0.6)
        F, _ = face_frame(C, 7, s, B)
        out.append(portal(sm, F, lift, key, dial_asp))
    # machine head
    machine_head(sm, B)
    return out

def portal(sm, F, lift, key, dial_asp):
    """carved timber + brass door surround on the +z face, with sunburst fan, floor dial, name plaque, lanterns"""
    for sx in (-1, 1):
        bevel_box(sm, 'dark', 0.26, 3.3, 0.24, 0.03, m=M(F, T(sx * 1.08, 1.65, 0.12)), uvs=2.0)
        bevel_box(sm, 'plank', 0.14, 2.6, 0.04, 0.01, m=M(F, T(sx * 1.08, 1.6, 0.25)), uvs=2.0)
        box(sm, 'brass', 0.36, 0.14, 0.32, m=M(F, T(sx * 1.08, 0.07, 0.12)))
        lathe(sm, 'brass', [(0.0, 0), (0.17, 0.0), (0.2, 0.06), (0.14, 0.14), (0.18, 0.22), (0.0, 0.22)], 8, m=M(F, T(sx * 1.08, 3.3, 0.12)), a0=45, a1=405)
        box(sm, 'dark', 0.3, 3.3, 0.2, m=M(F, T(sx * 1.18, 1.65, -0.02)))          # backing behind the pilaster
        wall_lantern(sm, M(F, T(sx * 1.38, 2.25, 0.04), Ry(sx * 50)), 1.1)
    bevel_box(sm, 'dark', 2.75, 0.32, 0.3, 0.04, m=M(F, T(0, 3.68, 0.13)), uvs=3.0)
    box(sm, 'gold', 2.8, 0.05, 0.32, m=M(F, T(0, 3.53, 0.13)))
    box(sm, 'gold', 2.8, 0.05, 0.32, m=M(F, T(0, 3.83, 0.13)))
    # sunburst fan (half disc) sitting on the entablature
    fc = M(F, T(0, 3.86, 0.08))
    half = [(1.02 * math.cos(math.radians(a)), 1.02 * math.sin(math.radians(a))) for a in np.linspace(0, 180, 25)]
    extrude(sm, 'dark', half, 0.08, m=fc)
    for a in np.linspace(9, 171, 13):
        mm = M(fc, Rz(a - 90), T(0, 0.67, 0.1))
        bevel_box(sm, 'brass', 0.035, 0.6, 0.025, 0.008, m=mm)
    tube(sm, 'brass', [(1.04 * math.cos(math.radians(a)), 1.04 * math.sin(math.radians(a)), 0.1) for a in np.linspace(0, 180, 31)], 0.045, 8, m=fc)
    tube(sm, 'brass', [(0.37 * math.cos(math.radians(a)), 0.37 * math.sin(math.radians(a)), 0.11) for a in np.linspace(0, 180, 17)], 0.025, 6, m=fc)
    lathe(sm, 'gold', [(0.0, 0.0), (0.09, 0.0), (0.06, 0.14), (0.0, 0.22)], 8, m=M(fc, T(0, 1.06, 0.1)))
    # floor dial in the heart of the fan (needle is separate)
    dh = 0.36; quad(sm, 'dial_' + lift['id'], dh * dial_asp, dh, M(fc, T(0, dh / 2 - 0.03, 0.14)))
    # the name plaque on top
    pw = 2.5; ph = pw / (1400 / 330)
    pm = M(F, T(0, 5.2, 0.12))
    quad(sm, 'plq_%s_%s' % (lift['id'], key), pw, ph, M(pm, T(0, 0, 0.055)))
    bevel_box(sm, 'dark', pw + 0.16, ph + 0.16, 0.1, 0.02, m=pm)
    for sx in (-1, 1):
        for sy in (-1, 1): sphere(sm, 'brass', 0.05, 8, 5, m=M(pm, T(sx * (pw / 2 + 0.05), sy * (ph / 2 + 0.05), 0.06)))
    # brass threshold plate in front of the doors
    box(sm, 'brass', 2.0, 0.025, 0.55, m=M(F, T(0, 0.012, 0.3)))
    # where the moving bits go (world)
    W = lambda p: [round(float(v), 3) for v in (F @ np.array([*p, 1]))[:3]]
    return dict(key=key, y=float(F[1, 3]), needle=W((0, 3.854, 0.24)), needle_scale=1.07, ry=0.0, gate_r=W((DW / 2, 0, 0.05)), gate_l=W((-DW / 2, 0, 0.05)),
                gate_col=W((0, 0, 0.05)), call=W((1.08, 1.25, 0.25)))

def machine_head(sm, B):
    y = TOP
    octprism(sm, 'iron', SA + 0.25, y, y + 0.15, m=None) if False else octprism(sm, 'iron', SA + 0.25, y, y + 0.15, B)
    lathe(sm, 'brass', [(SA / math.cos(math.radians(22.5)) + 0.3, y + 0.15), (SA / math.cos(math.radians(22.5)) + 0.3, y + 0.2)], 8, m=B, a0=22.5, a1=382.5)
    P = [(-1.75, -1.75), (1.75, -1.75), (1.75, 1.75), (-1.75, 1.75)]
    H = 2.95
    for (x, z) in P:
        bevel_box(sm, 'iron', 0.22, H, 0.22, 0.03, m=M(B, T(x, y + 0.15 + H / 2, z)))
        for yy in (y + 0.4, y + H - 0.1): box(sm, 'brass', 0.3, 0.06, 0.3, m=M(B, T(x, yy, z)))
    for k in range(4):
        a = np.array([*P[k]]); b = np.array([*P[(k + 1) % 4]])
        seg_box(sm, 'iron', M(B) @ np.array([a[0], y + 0.15 + H, a[1], 1]), M(B) @ np.array([b[0], y + 0.15 + H, b[1], 1]), 0.2)
        seg_box(sm, 'iron', (M(B) @ np.array([a[0], y + 0.3, a[1], 1]))[:3], (M(B) @ np.array([b[0], y + H - 0.1, b[1], 1]))[:3], 0.08)
    seg_box(sm, 'iron', (B @ np.array([-1.75, y + 0.15 + H, SHEAVE_Z, 1]))[:3], (B @ np.array([1.75, y + 0.15 + H, SHEAVE_Z, 1]))[:3], 0.18)
    # bearing blocks for the sheave axle and pinion axle
    for sx in (-1.05, 1.05):
        bevel_box(sm, 'iron', 0.2, SHEAVE_Y - y - 0.15, 0.36, 0.02, m=M(B, T(sx, (SHEAVE_Y + y + 0.15) / 2, SHEAVE_Z)))
        lathe(sm, 'brass', [(0.0, -0.12), (0.16, -0.12), (0.16, 0.12), (0.0, 0.12)], 12, m=M(B, T(sx, SHEAVE_Y, SHEAVE_Z), Rz(90)))
    pz, py = pinion_pos()
    bevel_box(sm, 'iron', 0.2, py - y - 0.15, 0.3, 0.02, m=M(B, T(0.4, (py + y + 0.15) / 2, pz)))
    # the motor: a riveted drum with brass bands and cooling fins, on the pinion axle
    mm = M(B, T(1.45, py, pz), Rz(90))
    lathe(sm, 'iron', [(0.0, -0.55), (0.42, -0.55), (0.48, -0.48), (0.48, 0.48), (0.42, 0.55), (0.0, 0.55)], 20, m=mm)
    for yy in (-0.4, -0.15, 0.1, 0.35): lathe(sm, 'brass', [(0.49, yy - 0.03), (0.51, yy), (0.49, yy + 0.03)], 20, m=mm)
    for k in range(12):
        a = 30 * k; box(sm, 'iron', 0.04, 0.8, 0.08, m=M(mm, Ry(a), T(0, 0, 0.5)))
    bevel_box(sm, 'iron', 1.1, py - y - 0.15 - 0.4, 0.8, 0.02, m=M(B, T(1.45, (py - 0.4 + y + 0.15) / 2, pz)))
    # pressure gauge + red warning lamp
    gm = M(B, T(1.45, py + 0.62, pz))
    lathe(sm, 'brass', [(0.0, 0), (0.06, 0), (0.06, 0.12), (0.0, 0.12)], 8, m=gm)
    lathe(sm, 'brass', [(0.0, -0.03), (0.16, -0.03), (0.16, 0.03), (0.0, 0.03)], 16, m=M(gm, T(0, 0.28, 0), Rx(90)))
    sphere(sm, 'redlamp', 0.1, 10, 6, m=M(B, T(0, y + 0.15 + H + 0.22, SHEAVE_Z)))
    lathe(sm, 'brass', [(0.0, 0), (0.12, 0), (0.12, 0.08), (0.0, 0.08)], 8, m=M(B, T(0, y + 0.15 + H + 0.1, SHEAVE_Z)))
    # holes in the platform for the ropes: little brass grommets
    for z in (0.0, CW_Z):
        lathe(sm, 'brass', [(0.18, y + 0.15), (0.24, y + 0.18), (0.18, y + 0.21)], 12, m=M(B, T(0, 0, z)))

def pinion_pos():
    a = math.radians(-18); d = 1.25
    return SHEAVE_Z + d * math.cos(a), SHEAVE_Y + d * math.sin(a)

# ------------------------------------------------------------------------------------------------ moving parts
def sheave():
    m = Mesh(); R = SHEAVE_R
    prof = [(R - 0.15, -0.25), (R, -0.25)]
    for k in range(4):
        z0 = -0.2 + k * 0.1
        prof += [(R, z0), (R - 0.05, z0 + 0.03), (R - 0.05, z0 + 0.05), (R, z0 + 0.08)]
    prof += [(R, 0.25), (R - 0.15, 0.25)]
    lathe(m, 'iron', prof, 40, m=Rz(-90))
    lathe(m, 'iron', [(R - 0.15, 0.25), (R - 0.15, -0.25)], 40, m=Rz(-90))
    for k in range(6):
        a = 60 * k + 15
        bevel_box(m, 'iron', 0.1, R - 0.3, 0.12, 0.02, m=M(Rx(a), T(0, (R - 0.3) / 2 + 0.15, 0)))
    lathe(m, 'brass', [(0.0, -0.3), (0.2, -0.3), (0.22, 0.0), (0.2, 0.3), (0.0, 0.3)], 16, m=Rz(-90))
    cyl(m, 'steel', 0.07, 2.3, 10, m=M(Rz(-90), T(0, -1.15, 0)))
    gear(m, 'brass', 1.0, 48, 0.12, mm=M(T(0.62, 0, 0), Ry(90)), spokes=8, spoke_mat='iron')
    # flywheel on the other side
    lathe(m, 'iron', [(0.82, -0.08), (0.95, -0.08), (0.97, 0.0), (0.95, 0.08), (0.82, 0.08)], 40, m=M(T(-0.7, 0, 0), Rz(-90)))
    for k in range(6):
        a = 60 * k
        pts = [(-0.7, (0.12 + t * 0.72) * math.cos(math.radians(a + 25 * t)), (0.12 + t * 0.72) * math.sin(math.radians(a + 25 * t))) for t in np.linspace(0, 1, 6)]
        tube(m, 'iron', pts, 0.03, 6)
    lathe(m, 'brass', [(0.0, -0.1), (0.14, -0.1), (0.14, 0.1), (0.0, 0.1)], 12, m=M(T(-0.7, 0, 0), Rz(-90)))
    return m

def pinion():
    m = Mesh()
    gear(m, 'brass', 0.33, 16, 0.12, mm=M(T(0.62, 0, 0), Ry(90)), spokes=0, hub=0.08)
    cyl(m, 'steel', 0.05, 1.3, 10, m=M(Rz(-90), T(0, 0.45, 0)))
    for k in range(4):
        a = 90 * k; box(m, 'brass', 0.02, 0.06, 0.12, m=M(T(0.95, 0, 0), Rx(a), T(0, 0.08, 0)))
    return m

def governor():
    m = Mesh()
    cyl(m, 'steel', 0.03, 1.1, 8)
    lathe(m, 'brass', [(0.0, 0.0), (0.12, 0.0), (0.12, 0.1), (0.0, 0.1)], 12)
    lathe(m, 'brass', [(0.0, 1.05), (0.06, 1.05), (0.08, 1.12), (0.0, 1.2)], 10)
    for s in (-1, 1):
        top = np.array([0, 1.0, 0]); ball = np.array([s * 0.36, 0.62, 0]); col = np.array([0, 0.45, 0])
        tube(m, 'brass', [top, ball], 0.018, 5); tube(m, 'brass', [col, (ball + col) / 2 + np.array([0, 0.02, 0]), ball * 0.6 + col * 0.4], 0.014, 5)
        sphere(m, 'brass', 0.11, 12, 8, m=T(*ball))
    lathe(m, 'brass', [(0.04, 0.42), (0.09, 0.44), (0.09, 0.48), (0.04, 0.5)], 10)
    return m

def cabgear():
    m = Mesh(); gear(m, 'brass', 0.3, 14, 0.07, mm=Ry(90), spokes=5, spoke_mat='iron'); cyl(m, 'steel', 0.03, 0.3, 8, m=M(Rz(-90), T(0, -0.15, 0))); return m

def cable():
    m = Mesh()
    for x in (-0.12, -0.04, 0.04, 0.12): tube(m, 'steel', [(x, 0, 0), (x, -1.0, 0)], 0.012, 5, uvs=0.2, twist=4)
    return m

def counterweight():
    m = Mesh(); w, d, h = 1.08, 0.36, 2.4
    for sx in (-1, 1): bevel_box(m, 'iron', 0.1, h, d + 0.04, 0.02, m=T(sx * (w / 2 - 0.05), -h / 2, 0))
    bevel_box(m, 'iron', w, 0.14, d + 0.06, 0.02, m=T(0, -0.07, 0)); bevel_box(m, 'iron', w, 0.14, d + 0.06, 0.02, m=T(0, -h + 0.07, 0))
    for k in range(13):
        bevel_box(m, 'iron' if k % 4 else 'brass', w - 0.22, 0.15, d, 0.02, m=T(0, -0.22 - k * 0.165, 0))
    for sx in (-0.12, -0.04, 0.04, 0.12): lathe(m, 'brass', [(0.0, 0), (0.03, 0), (0.03, 0.08), (0.0, 0.1)], 6, m=T(sx, 0, 0))
    for sx in (-1, 1):
        for y in (-0.25, -h + 0.25): box(m, 'brass', 0.08, 0.16, 0.2, m=T(sx * (w / 2 + 0.03), y, 0))
    return m

def needle():
    m = Mesh()
    extrude(m, 'gold', [(-0.012, -0.05), (0.012, -0.05), (0.008, 0.2), (0.03, 0.2), (0.0, 0.28), (-0.03, 0.2), (-0.008, 0.2)], 0.012, m=T(0, 0, -0.006))
    lathe(m, 'brass', [(0.0, -0.01), (0.035, -0.01), (0.035, 0.015), (0.0, 0.02)], 10, m=Rx(90))
    sphere(m, 'brass', 0.03, 8, 5, m=T(0, -0.06, 0))
    return m

def lever():
    m = Mesh()
    lathe(m, 'brass', [(0.0, -0.04), (0.06, -0.04), (0.06, 0.04), (0.0, 0.04)], 12, m=Rz(90))
    tube(m, 'brass', [(0, 0, 0), (0, 0.25, 0.02), (0, 0.42, 0.0)], 0.022, 8)
    lathe(m, 'dark', [(0.0, 0.4), (0.035, 0.41), (0.045, 0.48), (0.035, 0.55), (0.0, 0.57)], 10)
    return m

def scissor_gate(w, h, cols=4):
    """one folding brass lattice leaf, hinge at x=0, leaf runs to x=-w; scale x to fold it"""
    m = Mesh()
    rows = max(3, int(round(h / 0.46)))
    for x in (0.0, -w):
        bevel_box(m, 'brass', 0.05, h, 0.05, 0.01, m=T(x - (0.025 if x == 0 else -0.025), h / 2, 0))
    for y in (0.04, h - 0.04): box(m, 'brass', w, 0.04, 0.035, m=T(-w / 2, y, 0))
    dx = w / cols; dy = (h - 0.08) / rows
    for i in range(cols):
        for j in range(rows):
            x0 = -i * dx; x1 = -(i + 1) * dx; y0 = 0.04 + j * dy; y1 = y0 + dy
            for (a, b, z) in (((x0, y0), (x1, y1), 0.012), ((x1, y0), (x0, y1), -0.012)):
                d = np.array([b[0] - a[0], b[1] - a[1], 0])
                box(m, 'brass', 0.03, 0.01, np.linalg.norm(d) + 0.02, m=M(T((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z), look_basis(d, up=(0, 0, 1))))
            sphere(m, 'gold', 0.016, 6, 3, m=T((x0 + x1) / 2, (y0 + y1) / 2, 0))
    lathe(m, 'gold', [(0.0, 0), (0.03, 0), (0.035, 0.03), (0.0, 0.06)], 8, m=M(T(-w + 0.04, h * 0.45, 0.04), Rx(90)))
    return m

def call_button():
    m = Mesh()
    bevel_box(m, 'brass', 0.16, 0.3, 0.03, 0.01, m=T(0, 0, 0.015))
    lathe(m, 'gold', [(0.055, 0.0), (0.065, 0.02), (0.05, 0.035)], 16, m=M(T(0, 0.04, 0.03), Rx(90)))
    sphere(m, 'jewel', 0.04, 12, 6, m=M(T(0, 0.04, 0.035), S(1, 1, 0.5)))
    for y in (-0.1,): lathe(m, 'gold', [(0.0, 0), (0.02, 0), (0.0, 0.015)], 8, m=M(T(0, y, 0.03), Rx(90)))
    return m

def call_glow():
    m = Mesh(); sphere(m, 'halo', 0.09, 12, 6, m=M(T(0, 0.04, 0.04), S(1, 1, 0.4))); return m

# ------------------------------------------------------------------------------------------------ the cab (local)
def cab(lift):
    m = Mesh(); C = octa(CA); keys = [LY['stop_names'][str(s)] for s in lift['stops']]
    # floor: dark slab, polished planks, compass rose of brass and a glowing mud ring
    octprism(m, 'dark', CA + 0.02, -0.28, -0.09)
    lathe(m, 'brass', [(CA / math.cos(math.radians(22.5)) + 0.04, -0.3), (CA / math.cos(math.radians(22.5)) + 0.04, -0.07)], 8, a0=22.5, a1=382.5, smooth=False)
    deck(m, octa(CA - 0.02), 0.0, rng, mat='bartop', joists=False, edge_mat='brass')
    for (r0, r1) in ((0.9, 0.95), (1.45, 1.5)): lathe(m, 'brass', [(r0, 0.004), (r1, 0.004)], 48)
    lathe(m, 'mudglow', [(0.95, 0.003), (1.05, 0.003)], 48)
    for k in range(16):
        L_ = 0.85 if k % 2 == 0 else 0.55
        mm = M(Ry(22.5 * k), T(0, 0.004, L_ / 2 + 0.1)); box(m, 'gold' if k % 4 == 0 else 'brass', 0.035 if k % 2 == 0 else 0.02, 0.006, L_, m=mm)
    lathe(m, 'gold', [(0.0, 0.006), (0.12, 0.006), (0.0, 0.03)], 16)
    box(m, 'brass', DW + 0.1, 0.02, 0.28, m=T(0, -0.005, CA + 0.11))                    # threshold lip towards the landing
    # undercarriage + the compensating chain loop
    for a in (0, 90): bevel_box(m, 'iron', 0.2, 0.25, 2 * CA - 0.2, 0.02, m=M(Ry(a), T(0, -0.42, 0)))
    pts = [(-0.9 + 1.8 * t, -0.35 - 0.75 * math.sin(math.pi * t), -0.6) for t in np.linspace(0, 1, 2)]
    path = [np.array([-0.9 * math.cos(math.pi * t), -0.4 - 0.75 * math.sin(math.pi * t), -0.6]) for t in np.linspace(0, 1, 120)]
    acc = 0; last = path[0]; links = [last]
    for p in path[1:]:
        acc += np.linalg.norm(p - last); last = p
        if acc >= 0.075: links.append(p); acc = 0
    for k in range(len(links) - 1):
        a, b = links[k], links[k + 1]; d = b - a; mm = M(T(*((a + b) / 2)), look_basis(d), Rz(90 * (k % 2)))
        loop = [(0.025 * math.cos(t), 0, 0.055 * math.sin(t) * 1.0 + (0.02 if math.sin(t) > 0 else -0.02)) for t in np.linspace(0, 2 * math.pi, 11)]
        tube(m, 'iron', loop, 0.009, 4, m=mm)
    # corner posts
    for (x, z) in C:
        lathe(m, 'brass', [(0.0, 0.0), (0.09, 0.0), (0.09, 0.06), (0.065, 0.12), (0.055, 0.98), (0.085, 1.03), (0.055, 1.09),
                           (0.05, 2.5), (0.08, 2.56), (0.055, 2.62), (0.07, 2.95), (0.0, 2.95)], 10, m=T(x * 0.985, 0, z * 0.985))
        for y in np.linspace(1.15, 2.4, 6): lathe(m, 'gold', [(0.052, y - 0.02), (0.064, y), (0.052, y + 0.02)], 10, m=T(x * 0.985, 0, z * 0.985))
    for i in range(8):
        F, ln = face_frame(C, i)
        inner = M(F, Ry(180))                                                    # facing into the cab
        door = i == 7
        # frieze band and gilt strip on every face
        bevel_box(m, 'dark', ln - 0.1, 0.34, 0.08, 0.02, m=M(F, T(0, 2.78, -0.02)))
        box(m, 'gold', ln - 0.1, 0.04, 0.1, m=M(F, T(0, 2.63, -0.02)))
        box(m, 'gold', ln - 0.1, 0.04, 0.1, m=M(F, T(0, 2.93, -0.02)))
        if door:
            continue
        # wainscot: dark panel with a raised inset and brass cap; brass handrail on posts
        bevel_box(m, 'dark', ln - 0.1, 1.0, 0.07, 0.02, m=M(F, T(0, 0.5, -0.03)))
        bevel_box(m, 'plank', ln - 0.42, 0.6, 0.03, 0.012, m=M(inner, T(0, 0.52, 0.08)), uvs=1.5)
        bevel_box(m, 'plank', ln - 0.42, 0.6, 0.03, 0.012, m=M(F, T(0, 0.52, 0.02)), uvs=1.5)
        box(m, 'brass', ln - 0.08, 0.035, 0.1, m=M(F, T(0, 1.02, -0.03)))
        tube(m, 'brass', [(F @ np.array([x, 0.95, -0.17, 1]))[:3] for x in (-ln / 2 + 0.12, ln / 2 - 0.12)], 0.022, 8)
        for x in (-ln / 2 + 0.25, ln / 2 - 0.25): tube(m, 'brass', [(F @ np.array([x, 0.95, -0.17, 1]))[:3], (F @ np.array([x, 0.88, -0.05, 1]))[:3]], 0.01, 5)
        # cage: brass bars, an arched rail and scroll spandrels
        nb = 4
        for k in range(1, nb + 1):
            x = -ln / 2 + ln * k / (nb + 1)
            cyl(m, 'brass', 0.014, 1.5, 6, m=M(F, T(x, 1.05, -0.02)), caps=False)
        arch = [(x, 2.32 + 0.2 * math.cos(math.pi * x / (ln - 0.1)), -0.02) for x in np.linspace(-ln / 2 + 0.05, ln / 2 - 0.05, 13)]
        tube(m, 'brass', arch, 0.02, 6, m=F)
        for f in (-1, 1): spiral(m, 'brass', f * (ln / 2 - 0.2), 2.42, 0.12, 0.02, 1.3, M(F, T(0, 0, -0.02)), flip=-f, rr=0.01, n=16)
        # a whisper of glass behind the bars so the cage reads as glazed
        quad(m, 'glassL', ln - 0.12, 1.55, M(F, T(0, 1.8, -0.045)), double=True)
    # ceiling, cornice, octagonal brass dome, stained-glass cupola, crest finials, rope hitch
    octprism(m, 'dark', CA + 0.08, 2.95, 3.05)
    octprism(m, 'brass', CA + 0.14, 3.05, 3.12)
    Rc = (CA + 0.05) / math.cos(math.radians(22.5))
    lathe(m, 'brass', [(Rc, 3.12), (Rc * 0.9, 3.3), (Rc * 0.7, 3.48), (Rc * 0.47, 3.6), (0.5, 3.68), (0.45, 3.72)], 8, a0=22.5, a1=382.5)
    lathe(m, 'stained', [(0.45, 3.72), (0.46, 3.85), (0.45, 4.0)], 8, a0=22.5, a1=382.5)
    for k in range(8):
        a = 22.5 + 45 * k; cyl(m, 'brass', 0.02, 0.3, 5, m=T(0.46 * math.sin(math.radians(a)), 3.72, 0.46 * math.cos(math.radians(a))))
    lathe(m, 'brass', [(0.55, 4.0), (0.3, 4.12), (0.12, 4.22), (0.1, 4.3), (0.0, 4.3)], 8, a0=22.5, a1=382.5)
    lathe(m, 'gold', [(0.0, 4.28), (0.08, 4.3), (0.08, HITCH - 0.02), (0.0, HITCH)], 8)
    tube(m, 'steel', [(0.1 * math.cos(t), HITCH + 0.06 + 0.06 * math.sin(t), 0) for t in np.linspace(0, math.pi, 9)], 0.02, 6)
    for (x, z) in C:
        lathe(m, 'gold', [(0.0, 0.0), (0.05, 0.0), (0.03, 0.1), (0.045, 0.16), (0.0, 0.32)], 8, m=T(x * 1.04, 3.12, z * 1.04))
    # ceiling inside: stained oculus + hanging lantern + two corner sconces
    lathe(m, 'stained', [(0.0, 2.94), (0.62, 2.94)], 24)
    lathe(m, 'gold', [(0.62, 2.935), (0.72, 2.935)], 24)
    for k in range(8): box(m, 'gold', 0.03, 0.01, 0.62, m=M(Ry(22.5 + 45 * k), T(0, 2.93, 0.31)))
    tube(m, 'iron', [(0, 2.93, 0), (0, 2.75, 0)], 0.012, 4)
    lantern(m, T(0, 2.75, 0), 0.85)
    for i in (2, 4):
        F, ln = face_frame(C, i)
        wall_lantern(m, M(F, Ry(180), T(ln / 2 - 0.05, 1.9, 0.05)), 0.9)
    # tufted green leather bench round the three back faces
    for i in (2, 3, 4):
        F, ln = face_frame(C, i); inner = M(F, Ry(180))
        L_ = ln - 0.1
        bevel_box(m, 'dark', L_, 0.38, 0.46, 0.02, m=M(inner, T(0, 0.19, 0.3)))
        bevel_box(m, 'leatherg', L_, 0.14, 0.5, 0.05, m=M(inner, T(0, 0.45, 0.31)), uvs=1.0)
        bevel_box(m, 'leatherg', L_, 0.42, 0.12, 0.05, m=M(inner, T(0, 0.8, 0.12), Rx(-8)), uvs=1.0)
        for k in range(int(L_ / 0.24)):
            for j in range(2): sphere(m, 'brass', 0.018, 6, 3, m=M(inner, T(-L_ / 2 + 0.17 + k * 0.24 + j * 0.12, 0.7 + j * 0.18, 0.19 - j * 0.025)))
        for k in range(int(L_ / 0.08)): sphere(m, 'brass', 0.01, 5, 3, m=M(inner, T(-L_ / 2 + 0.04 + k * 0.08, 0.39, 0.55)))
    # operator's pedestal on the front-right diagonal (the lever is separate)
    F, ln = face_frame(C, 0); P = M(F, Ry(180), T(0, 0, 0.42))
    lathe(m, 'brass', [(0.0, 0), (0.2, 0), (0.2, 0.05), (0.08, 0.12), (0.06, 0.85), (0.1, 0.9), (0.14, 1.0), (0.0, 1.0)], 12, m=P)
    bevel_box(m, 'dark', 0.36, 0.06, 0.3, 0.015, m=M(P, T(0, 1.02, 0), Rx(18)))
    quad(m, 'dial_' + lift['id'], 0.3, 0.3 / 1.78, M(P, T(0, 1.06, 0.0), Rx(-72)))
    for sx in (-1, 1): lathe(m, 'brass', [(0.0, 0), (0.04, 0), (0.04, 0.06), (0.0, 0.08)], 8, m=M(P, T(sx * 0.13, 1.02, 0.12)))
    lever_at = M(P, T(0.2, 0.92, 0.0))
    # the floor dial above the door, facing in (needle separate)
    F7, ln7 = face_frame(C, 7)
    quad(m, 'dial_' + lift['id'], 0.6, 0.6 / 1.78, M(F7, Ry(180), T(0, 2.78, 0.07)))
    quad(m, 'dial_' + lift['id'], 0.6, 0.6 / 1.78, M(F7, T(0, 2.78, 0.03)))
    W = lambda mm, p=(0, 0, 0): [round(float(v), 4) for v in (mm @ np.array([*p, 1]))[:3]]
    ry = lambda mm: round(math.degrees(math.atan2(mm[0, 2], mm[2, 2])), 2)
    info = dict(lever=W(lever_at), lever_ry=ry(M(F, Ry(180))), needle_in=W(M(F7, Ry(180), T(0, 2.634, 0.09))), needle_in_ry=180.0,
                needle_out=W(M(F7, T(0, 2.634, 0.05))), needle_scale=1.0,
                gear_l=[-1.3, 3.5, 0.0], gear_r=[1.3, 3.5, 0.0], gate_r=[DW / 2, 0.0, round(CA - 0.04, 3)], gate_l=[-DW / 2, 0.0, round(CA - 0.04, 3)],
                operator=W(M(F, Ry(180), T(-0.55, 0, 0.6))), operator_ry=ry(M(F, Ry(180))) + 180)
    # brackets for the two crown gears
    for sx in (-1, 1):
        bevel_box(m, 'iron', 0.06, 0.42, 0.18, 0.01, m=T(sx * 1.38, 3.3, 0))
        lathe(m, 'brass', [(0.0, -0.03), (0.05, -0.03), (0.05, 0.03), (0.0, 0.03)], 8, m=M(T(sx * 1.38, 3.5, 0), Rz(90)))
    return m, info

def cab_collider():
    c = Mesh(); C = octa(CA)
    slab_collider(c, 0.0, ('p', C), row=0.35, th=0.25, pad=0.0)
    box(c, 'col', DW + 0.1, 0.25, 0.3, m=T(0, -0.125, CA + 0.12))
    for i in range(8):
        if i == 7: continue
        F, ln = face_frame(C, i); box(c, 'col', ln + 0.12, 2.6, 0.12, m=M(F, T(0, 1.3, 0)))
    for i in (6, 0):                                                           # door jambs
        F, ln = face_frame(C, i); box(c, 'col', 0.12, 2.6, 0.12, m=M(F, T(ln / 2 if i == 6 else -ln / 2, 1.3, 0)))
    return c

def gate_col(w, h):
    c = Mesh(); box(c, 'col', w, h, 0.12, m=T(0, h / 2, 0)); return c

# ------------------------------------------------------------------------------------------------ sounds (synthesised, no assets needed)
def sounds():
    import wave, subprocess
    sr = 44100
    def save(name, x):
        x = np.clip(x / (np.abs(x).max() + 1e-9) * 0.9, -1, 1); p = '/home/claude/spire/out/snd/' + name
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with wave.open(p + '.wav', 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype(np.int16).tobytes())
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p + '.wav', '-b:a', '96k', p + '.mp3']); os.remove(p + '.wav')
    def bell(f, dur, t0, n):
        t = np.arange(int(sr * dur)) / sr; y = np.zeros(n)
        tone = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * d) for k, a, d in ((1, 1.0, 1.6), (2.0, 0.5, 2.6), (2.76, 0.35, 3.4), (5.4, 0.15, 6), (8.9, 0.06, 9)))
        i0 = int(t0 * sr); y[i0:i0 + len(t)] += tone[:max(0, n - i0)]; return y
    n = int(sr * 2.6); save('lift_chime', bell(1046.5, 2.2, 0.0, n) + 0.9 * bell(784.0, 2.2, 0.42, n))
    t = np.arange(int(sr * 0.9)) / sr; rngn = np.random.default_rng(3)
    clank = rngn.normal(0, 1, len(t)) * np.exp(-t * 40)
    for k, t0 in enumerate(np.linspace(0, 0.55, 9)):
        i0 = int(t0 * sr); seg = np.arange(len(t) - i0) / sr
        clank[i0:] += 0.6 * np.sin(2 * np.pi * (1900 + 160 * k) * seg) * np.exp(-seg * 55) + 0.3 * rngn.normal(0, 1, len(seg)) * np.exp(-seg * 90)
    save('lift_gate', clank)
    t = np.arange(int(sr * 4.0)) / sr
    hum = 0.5 * np.sin(2 * np.pi * 55 * t) + 0.25 * np.sin(2 * np.pi * 110 * t + 0.4) + 0.12 * np.sin(2 * np.pi * 165 * t)
    hum *= 1 + 0.08 * np.sin(2 * np.pi * 2 * t)
    for t0 in np.arange(0, 4.0, 0.25):
        i0 = int(t0 * sr); seg = np.arange(len(t) - i0) / sr
        hum[i0:] += 0.25 * np.sin(2 * np.pi * 2400 * seg) * np.exp(-seg * 120)
    save('lift_hum', hum)
    t = np.arange(int(sr * 0.5)) / sr
    save('lift_lever', np.sin(2 * np.pi * 140 * t) * np.exp(-t * 18) + 0.5 * rngn.normal(0, 1, len(t)) * np.exp(-t * 60))

# ------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    col = Mesh(); lay = dict(lifts=[], hitch=HITCH, sheave_y=SHEAVE_Y, sheave_z=SHEAVE_Z, sheave_r=SHEAVE_R, cw_z=CW_Z, cw_len=2.4)
    # rope length is fixed: (sheave - cab hitch) + (sheave - counterweight top) = ROPE.  With the cab at the bottom the weight hangs just under the head.
    ROPE = (SHEAVE_Y - (BASE + HITCH)) + (SHEAVE_Y - (TOP - 0.3))
    lay['rope'] = round(ROPE, 3)
    lay['cw_rule'] = 'cw_top_y = sheave_y - (rope - (sheave_y - (cab_y + hitch)))'
    pz, py = pinion_pos()
    DONE = set()
    for li, lift in enumerate(LY['lifts']):
        sm = Mesh()
        portals = shaft(lift, sm, col)
        cm, info = cab(lift)
        # shaft models are shared by lifts with the same stops (built at x = 0, z = 0, placed at each lift's x, z); one cab for all
        sk = 'sp_lift_shaft' + ('' if len(lift['stops']) == 5 else '_g')
        if not os.path.exists(OUT + sk + '.glb') or sk not in DONE:
            sm0 = Mesh(); shaft(dict(lift, x=0.0, z=0.0), sm0, Mesh()); DONE.add(sk)
            print('shaft', write(OUT + sk + '.glb', sm0, M_))
        lift['shaft_model'] = sk
        if li == 0: print('cab', write(OUT + 'sp_lift_cab.glb', cm, M_))
        keys = [LY['stop_names'][str(s)] for s in lift['stops']]
        x, z = lift['x'], lift['z']
        lay['lifts'].append(dict(id=lift['id'], name=lift['name'], x=x, z=z, stops=lift['stops'], keys=keys, shaft_model=lift['shaft_model'],
                                 dial_rz=[round(-a, 2) for a in dial_angles(len(keys))], portals=portals, cab=info,
                                 sheave=[x, round(SHEAVE_Y, 3), round(z + SHEAVE_Z, 3)], pinion=[x, round(py, 3), round(z + pz, 3)],
                                 governor=[x - 1.6, TOP + 0.15, z + 1.25], cab_rope_top=[x, round(SHEAVE_Y, 3), z], cw_rope_top=[x, round(SHEAVE_Y, 3), round(z + CW_Z, 3)],
                                 spin_ratio_pinion=round(-1.0 / 0.33, 3), sheave_rad_per_m=round(1 / SHEAVE_R, 4)))
    print('col', write(OUT + 'sp_lift_col.glb', col, M_))
    print('cabcol', write(OUT + 'sp_lift_cab_col.glb', cab_collider(), M_))
    for nm, mesh in [('sp_lift_cgate', scissor_gate(DW / 2, 2.5)), ('sp_lift_lgate', scissor_gate(DW / 2, DH)), ('sp_lift_sheave', sheave()),
                     ('sp_lift_pinion', pinion()), ('sp_lift_gov', governor()), ('sp_lift_cabgear', cabgear()), ('sp_lift_cable', cable()),
                     ('sp_lift_cw', counterweight()), ('sp_lift_needle', needle()), ('sp_lift_lever', lever()), ('sp_lift_call', call_button()),
                     ('sp_lift_callglow', call_glow()), ('sp_lift_cgate_col', gate_col(DW + 0.1, 2.5)), ('sp_lift_lgate_col', gate_col(DW + 0.2, DH))]:
        print(nm, write(OUT + nm + '.glb', mesh, M_))
    sounds()
    json.dump(lay, open('/home/claude/spire/out/lift_layout.json', 'w'), indent=1)
