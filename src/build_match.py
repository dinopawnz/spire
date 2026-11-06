"""MUDWATER SPIRE v2 - floor 2: MUD MATCH, a museum gallery.
200 portraits of #62 The Founder (199 forgeries + the real one): eight free-standing display walls (11 a side) + the front and back walls.
In the middle, the FINALS ROOM: a glass box (frosted until the host starts the finals) holding 100 Black Flag portraits on five screens.
Writes sp_f2_hall.glb (display walls, frames, sconces, rugs), sp_f2_col.glb, sp_f2_vault.glb (glass room), sp_f2_vaultcol.glb,
sp_vault_frost.glb, sp_vault_door.glb, portraits pf_XXXX.glb / pv_XXX.glb + out/f2_layout.json."""
import math, json, random, os
import numpy as np
from glb import *
from kit import *

OUT = '/home/claude/spire/out/glb/'
POUT = '/home/claude/spire/out/portraits/'
os.makedirs(POUT, exist_ok=True)
rng = random.Random(200)
LY = json.load(open('/home/claude/spire/out/layout.json'))
Y = LY['FL']['match']; HCEIL = LY['FL']['cards'] - 0.45 - Y          # clear height under the beams' slab
PW, PH = 1.1, 1.1 * 533 / 384            # Black Flag portraits (finals room)
PWH, PHH = 1.5, 1.5 * 533 / 384          # Founder portraits (gallery)
N_HALL = 200
IMGS = [821] + sorted(random.Random(62).sample([i for i in range(1000) if i != 821], N_HALL - 1))
DWX = [-30.5, -25.0, -19.5, -14.0, 14.0, 19.5, 25.0, 30.5]     # display wall centre lines (they run along z)
DZ0, DZ1 = -15.0, 13.6; DWH = 5.2; DWT = 0.5
VX, VZ = 9.0, 8.0                        # finals room half sizes (x -9..9, z -8..8)
VDOOR_W, VDOOR_H = 2.6, 3.4
hall = Mesh(); col = Mesh(); vm = Mesh(); vc = Mesh()

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

def display_wall(x):
    """a free-standing panelled wall along z with a carved plinth and cornice; returns portrait slots on both faces"""
    zc = (DZ0 + DZ1) / 2; ln = DZ1 - DZ0
    bevel_box(hall, 'velvet', DWT, DWH, ln, 0.03, m=T(x, Y + DWH / 2, zc), uvs=2.5)
    bevel_box(hall, 'dark', DWT + 0.3, 0.5, ln + 0.3, 0.04, m=T(x, Y + 0.25, zc), uvs=3.0)
    bevel_box(hall, 'dark', DWT + 0.4, 0.35, ln + 0.4, 0.04, m=T(x, Y + DWH + 0.17, zc), uvs=3.0)
    quad(hall, 'gold', ln + 0.4, 0.08, M(T(x + (DWT + 0.42) / 2, Y + DWH + 0.17, zc), Ry(90)))
    quad(hall, 'gold', ln + 0.4, 0.08, M(T(x - (DWT + 0.42) / 2, Y + DWH + 0.17, zc), Ry(-90)))
    for zz in (DZ0, DZ1):
        bevel_box(hall, 'dark', DWT + 0.5, DWH + 0.7, 0.5, 0.04, m=T(x, Y + (DWH + 0.7) / 2, zz), uvs=2.0)
        lathe(hall, 'brass', [(0.0, 0.0), (0.18, 0.0), (0.12, 0.25), (0.0, 0.4)], 10, m=T(x, Y + DWH + 0.7, zz))
    collider_box(col, DWT + 0.5, DWH + 0.7, ln + 0.5, T(x, Y + (DWH + 0.7) / 2, zc))
    slots = []
    n = 11; dz = ln / n
    for side in (1, -1):
        for j in range(n):
            z = DZ0 + dz * (j + 0.5)
            ry = 90 if side > 0 else 270
            px = x + side * (DWT / 2 + 0.02)
            slots.append(dict(x=round(px + side * 0.03, 3), y=round(Y + 2.45, 3), z=round(z, 3), ry=ry))
            frame(hall, PWH, PHH, M(T(px, Y + 2.45, z), Ry(ry)))
            if j < n - 1: sconce(hall, M(T(px, Y + 3.3, z + dz / 2), Ry(ry)))
    return slots

def wall_slots(z, xs, ry):
    out = []
    for x in xs:
        frame(hall, PWH, PHH, M(T(x, Y + 2.45, z), Ry(ry)))
        out.append(dict(x=round(x, 3), y=round(Y + 2.45, 3), z=round(z + (0.03 if ry == 0 else -0.03), 3), ry=ry))
    for a, b in zip(xs[:-1], xs[1:]): sconce(hall, M(T((a + b) / 2, Y + 3.3, z), Ry(ry)))
    return out

def gallery():
    slots = []
    for x in DWX: slots += display_wall(x)
    zf = LY['Z1'] - 0.32; zb = -LY['Z1'] + 0.32
    xs_f = [12.0 + 2.6 * i for i in range(8)]
    slots += wall_slots(zf, [-x for x in xs_f[::-1]], 180) + wall_slots(zf, xs_f, 180)
    xs_b = [22.6 + 2.6 * i for i in range(4)]
    slots += wall_slots(zb, [-x for x in xs_b[::-1]], 0) + wall_slots(zb, xs_b, 0)
    # velvet-backed panels behind the wall portraits so they read as a museum wall
    for z, ry in ((zf + 0.05, 180), (zb - 0.05, 0)):
        for sgn in (1, -1):
            xs = xs_f if ry == 180 else xs_b
            x0, x1 = min(xs) - 1.3, max(xs) + 1.3; xc = sgn * (x0 + x1) / 2
            quad(hall, 'velvet', x1 - x0, 4.0, M(T(xc, Y + 2.45, z), Ry(ry)))
    # rugs down the aisles
    for xa, xb in zip(DWX[:3], DWX[1:4]):
        for s in (1, -1):
            xc = s * (xa + xb) / 2
            quad(hall, 'velvett', 2.4, DZ1 - DZ0 - 1, M(T(xc, Y + 0.02, (DZ0 + DZ1) / 2), Rx(-90)))
    return slots

def finals_room():
    """glass box with brass mullions, a dark carved base and cornice, a door on the front (+z) side"""
    H = HCEIL
    sides = [((-VX, VZ), (VX, VZ)), ((VX, VZ), (VX, -VZ)), ((VX, -VZ), (-VX, -VZ)), ((-VX, -VZ), (-VX, VZ))]
    for i, (p0, p1) in enumerate(sides):
        mm, ln = place(p0, p1, Y)
        n = int(round(ln / 2.0))
        for j in range(n):
            a = ln * j / n; b = ln * (j + 1) / n; c = (a + b) / 2
            door = i == 0 and abs((p0[0] + (p1[0] - p0[0]) * c / ln)) < VDOOR_W / 2 + 0.1
            if door:
                quad(vm, 'vglass', b - a, H - VDOOR_H - 0.6, M(mm, T(c, VDOOR_H + 0.6 + (H - VDOOR_H - 0.6) / 2, 0)), double=True)
                collider_box(vc, b - a, H - VDOOR_H, 0.2, M(mm, T(c, VDOOR_H + (H - VDOOR_H) / 2, 0)))
            else:
                quad(vm, 'vglass', b - a, H - 0.6, M(mm, T(c, 0.6 + (H - 0.6) / 2, 0)), double=True)
                bevel_box(vm, 'dark', b - a + 0.02, 0.6, 0.35, 0.03, m=M(mm, T(c, 0.3, 0)), uvs=2.0)
                collider_box(vc, b - a + 0.05, H, 0.25, M(mm, T(c, H / 2, 0)))
            cyl(vm, 'brass', 0.06, H, 6, m=M(mm, T(a, 0, 0)))
        bevel_box(vm, 'brass', ln + 0.2, 0.3, 0.4, 0.03, m=M(mm, T(ln / 2, H - 0.15, 0)), uvs=3.0)
        bevel_box(vm, 'brass', ln + 0.2, 0.12, 0.4, 0.02, m=M(mm, T(ln / 2, 0.66, 0)), uvs=3.0)
    # door frame
    for s in (-1, 1): bevel_box(vm, 'brass', 0.16, VDOOR_H + 0.3, 0.4, 0.03, m=T(s * (VDOOR_W / 2 + 0.08), Y + (VDOOR_H + 0.3) / 2, VZ))
    bevel_box(vm, 'brass', VDOOR_W + 0.5, 0.3, 0.42, 0.03, m=T(0, Y + VDOOR_H + 0.15, VZ))
    # floor: polished wood with a gold border and a glowing mudwater compass
    flat_deck(vm, 'bartop', [(-VX, -VZ), (VX, -VZ), (VX, VZ), (-VX, VZ)], Y + 0.03, under=None)
    lathe(vm, 'mudglow', [(1.6, Y + 0.04), (2.0, Y + 0.04)], 48)
    # five screens of 20 Black Flags (2 rows x 5 a side)
    slots = []
    for x in (-6.0, -3.0, 0.0, 3.0, 6.0):
        z0, z1 = -5.2, 3.6; zc = (z0 + z1) / 2
        bevel_box(vm, 'velvet', 0.3, 4.4, z1 - z0, 0.03, m=T(x, Y + 2.2, zc), uvs=2.0)
        bevel_box(vm, 'dark', 0.5, 0.35, z1 - z0 + 0.2, 0.03, m=T(x, Y + 0.17, zc))
        bevel_box(vm, 'brass', 0.5, 0.2, z1 - z0 + 0.2, 0.03, m=T(x, Y + 4.5, zc))
        collider_box(vc, 0.5, 4.6, z1 - z0 + 0.2, T(x, Y + 2.3, zc))
        for side in (1, -1):
            for row, yy in enumerate((Y + 1.35, Y + 3.15)):
                for j in range(5):
                    z = z0 + (z1 - z0) * (j + 0.5) / 5
                    ry = 90 if side > 0 else 270; px = x + side * 0.17
                    slots.append(dict(x=round(px + side * 0.03, 3), y=round(yy, 3), z=round(z, 3), ry=ry))
                    frame(vm, PW, PH, M(T(px, yy, z), Ry(ry)), bw=0.09)
    return slots

def frost_sleeve():
    """frosted panels just outside the glass, base at the floor: the game scales it to nothing to reveal the room"""
    m = Mesh(); H = HCEIL - 0.05; o = 0.12
    sides = [((-VX - o, VZ + o), (VX + o, VZ + o)), ((VX + o, VZ + o), (VX + o, -VZ - o)), ((VX + o, -VZ - o), (-VX - o, -VZ - o)), ((-VX - o, -VZ - o), (-VX - o, VZ + o))]
    for p0, p1 in sides:
        mm, ln = place(p0, p1, 0)
        quad(m, 'frost', ln, H, M(mm, T(ln / 2, H / 2, 0)), uv=(0, 0, ln / 2, H / 2), double=True)
        box(m, 'frostrim', ln, 0.06, 0.06, m=M(mm, T(ln / 2, 0.03, 0)))
    mats = dict(MATS)
    mats['frost'] = dict(tex=TEX + 'glass.png', color=(0.9, 0.95, 0.93, 0.92), emis=(0.12, 0.14, 0.13), rough=0.9, alpha='BLEND', double=True)
    mats['frostrim'] = dict(color=(0.85, 0.9, 0.88, 1), rough=0.6)
    print('frost', write(OUT + 'sp_vault_frost.glb', m, mats))

def vault_door():
    m = Mesh()
    quad(m, 'vglass', VDOOR_W, VDOOR_H, T(0, VDOOR_H / 2, 0), double=True)
    for s in (-1, 1): box(m, 'brass', 0.08, VDOOR_H, 0.1, m=T(s * VDOOR_W / 2, VDOOR_H / 2, 0))
    for yy in (0.04, VDOOR_H - 0.04, VDOOR_H / 2): box(m, 'brass', VDOOR_W, 0.08, 0.1, m=T(0, yy, 0))
    lathe(m, 'brass', [(0.0, 0.0), (0.22, 0.0), (0.22, 0.03), (0.0, 0.03)], 20, m=M(T(0, VDOOR_H / 2, 0.06), Rx(90)))
    mats = dict(MATS); mats['vglass'] = VGLASS
    print('door', write(OUT + 'sp_vault_door.glb', m, mats))

def portrait_glbs(folder, prefix, ids, pw, ph):
    for i in ids:
        src = folder + 'p%04d.jpg' % i
        m = Mesh(); quad(m, 'pic', pw, ph, T(0, 0, 0))
        write(POUT + prefix % i, m, {'pic': dict(tex=src, emis_tex=src, emis=(0.32, 0.32, 0.32), rough=0.55)})

VGLASS = dict(color=(0.7, 0.85, 0.82, 0.07), metal=0.0, rough=0.02, alpha='BLEND', double=True)
if __name__ == '__main__':
    lay = gallery(); vslots = finals_room()
    assert len(lay) == N_HALL, len(lay)
    print('hall', write(OUT + 'sp_f2_hall.glb', hall, MATS), 'portraits', len(lay))
    print('col', write(OUT + 'sp_f2_col.glb', col, MATS))
    VM = dict(MATS); VM['vglass'] = VGLASS
    print('vault', write(OUT + 'sp_f2_vault.glb', vm, VM), 'slots', len(vslots))
    print('vcol', write(OUT + 'sp_f2_vaultcol.glb', vc, MATS))
    frost_sleeve(); vault_door()
    json.dump({'hall': lay, 'vault': vslots, 'imgs': IMGS, 'room': [VX, VZ], 'door': [0.0, Y, VZ, 0], 'y': Y, 'h': HCEIL}, open('/home/claude/spire/out/f2_layout.json', 'w'))
    if '--portraits' in __import__('sys').argv:
        portrait_glbs('/home/claude/spire/out/hall/', 'pf_%04d.glb', IMGS, PWH, PHH)
        portrait_glbs('/home/claude/spire/out/vault/', 'pv_%03d.glb', range(100), PW, PH)
