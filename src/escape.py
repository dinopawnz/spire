"""MUDWATER ESCAPE (game 3, floor 4 'rooms', y 40). Called by build_html.py: escape.apply(D, L, FL).

The owner's rules: all the teams begin in a different room; to progress they solve clues/puzzles to get to the next room, which may or may
not be on another floor. Built inside floor 4 (no taller tower needed): the floor is ~10 m high, so it gets a second level at +5.3 m.

  6 teams, one lane each: 3 lanes on the west half, 3 on the east half (z bands -36..-12, -12..12, 12..36).
  In every lane (u = metres in from the outer wall, v = metres along the lane from its middle):
    R1 lower, outer (u 0..18)  - LANTERN CODE: 4 hidden coloured lanterns show digits, a painting gives the colour order, door keypad
    R2 lower, inner (u 18..36) - LILY PADS: stand on 4 pads at once (fewer if the team is smaller)
       -> a stair (in an enclosed well carved out of R1's corner) climbs to the upper level
    R3 upper, outer            - CARD MEMORY: 12 face-down Mudwater cards on the wall, find the 6 pairs
    R4 upper, inner            - FROG CHOIR: 4 frogs croak a pattern, the team copies it (3 rounds: 4, 5, 6 croaks)
    -> the last door opens into the VICTORY HALL (upper level, the middle strip |x| < 8). First team out wins.
  Doors: D0 start door (outer wall, from the side aisle where the lifts + stairs arrive), D1 R1->R2, D2 R2->stair, D3 R3->R4, D4 R4->hall.
  The middle strip downstairs is the hosts' / spectators' corridor (glass into every R2), with a stair up to the Victory Hall (glass into
  every R4). Progress boards in both.
Writes sp_escape.glb (everything static), sp_escape_col.glb (invisible colliders), sp_esc_door.glb, esc/k_NNN.jpg (memory cards) and
D['escape'] for the game code (spire_src.html block "MUDWATER ESCAPE")."""
import math, os, random
import numpy as np
from PIL import Image
from glb import Mesh, write, box, bevel_box, cyl, sphere, T, M, Rx, Ry
from kit import MATS
import outside as _o

OUT = '/home/claude/spire/out/'
OUTG = OUT + 'glb/'
MW = '/home/claude/mudwater_repo/'

XO, XM, XC = 44.0, 26.0, 8.0          # |x| of the outer, middle and centre walls
ZB = 36.0                             # the complex runs z -36..36 (front/back aisles beyond)
HALF = 12.0                           # half a lane
UP = 5.3                              # the upper level's floor is this far above floor 4
WT, DW, DH = 0.3, 2.4, 3.2            # wall thickness, door opening
SLIDE = 2.5                           # doors slide this far along the wall (into it) to open
TEAMS = [  # key, colour, rgb, side (-1 west / +1 east), lane centre z
    ('red', '#e5533d', (0.90, 0.25, 0.18), -1, -24.0), ('gold', '#f2b632', (0.95, 0.70, 0.15), -1, 0.0),
    ('green', '#56d364', (0.30, 0.80, 0.35), -1, 24.0), ('blue', '#3d8bfd', (0.22, 0.48, 0.97), 1, -24.0),
    ('purple', '#b06cf0', (0.66, 0.40, 0.94), 1, 0.0), ('orange', '#ff8c2e', (1.0, 0.52, 0.16), 1, 24.0)]
LANTERN_COLS = ['#ff4a3a', '#ffd23a', '#4ae06a', '#4aa8ff']     # the four lantern colours (red, yellow, green, blue)
FROG_COLS = ['#ff5a4a', '#ffd84a', '#5ae07a', '#5aaeff']
WATER = dict(color=(0.02, 0.045, 0.035, 1), metal=0.0, rough=0.55, emis=(0.004, 0.014, 0.011))


def r3(v): return round(float(v), 3)


def apply(D, L, FL):
    Y0 = FL['rooms']; YU = Y0 + UP; YT = Y0 + 10.0
    vis, col = Mesh(), Mesh()
    mats = {k: MATS[k] for k in ('plank', 'dark', 'iron', 'gold', 'glass', 'glow', 'moss', 'rope', 'bartop', 'wetfloor')}
    mats['col'] = MATS['col']; mats['water'] = WATER
    for ti, t in enumerate(TEAMS):
        mats['esc%d' % ti] = dict(color=t[2] + (1,), emis=tuple(v * 0.55 for v in t[2]), rough=0.6)
    colm = {'col': MATS['col']}

    def blk(mat, cx, cy, cz, sx, sy, sz, solid=True, uvs=2.4):
        if sx <= 0.01 or sy <= 0.01 or sz <= 0.01: return
        box(vis, mat, sx, sy, sz, m=T(cx, cy, cz), uvs=uvs)
        if solid: box(col, 'col', sx, sy, sz, m=T(cx, cy, cz))

    def wall_x(x, z0, z1, y0, y1, holes=(), mat='plank'):
        """a wall at constant x from z0 to z1, y0 to y1, with door holes [(zc, w, h)] (from y0)"""
        cuts = sorted(holes); z = z0
        for (zc, w, h) in cuts:
            blk(mat, x, (y0 + y1) / 2, (z + zc - w / 2) / 2, WT, y1 - y0, zc - w / 2 - z)
            blk(mat, x, (y0 + h + y1) / 2, zc, WT, y1 - y0 - h, w)
            frame_x(x, zc, y0, w, h)
            z = zc + w / 2
        blk(mat, x, (y0 + y1) / 2, (z + z1) / 2, WT, y1 - y0, z1 - z)

    def wall_z(z, x0, x1, y0, y1, mat='plank'):
        blk(mat, (x0 + x1) / 2, (y0 + y1) / 2, z, x1 - x0, y1 - y0, WT)

    def frame_x(x, zc, y0, w, h):           # a dark timber door frame on both faces
        for dx in (-WT / 2 - 0.04, WT / 2 + 0.04):
            for s in (-1, 1): box(vis, 'dark', 0.08, h + 0.2, 0.22, m=T(x + dx, y0 + (h + 0.2) / 2, zc + s * (w / 2 + 0.11)), uvs=1.2)
            box(vis, 'dark', 0.08, 0.24, w + 0.44, m=T(x + dx, y0 + h + 0.1, zc), uvs=1.2)

    def slab(x0, x1, z0, z1, top, th=0.25):
        blk('plank', (x0 + x1) / 2, top - th / 2, (z0 + z1) / 2, x1 - x0, th, z1 - z0, uvs=3.0)

    def ramp(xc, w, zlow, zhigh, ylow, yhigh):
        """a stair from (zlow, ylow) up to (zhigh, yhigh); a smooth ramp collider under visible treads, side boards"""
        run = abs(zhigh - zlow); rise = yhigh - ylow; ln = math.hypot(run, rise); ang = math.degrees(math.atan2(rise, run))
        sgn = 1 if zhigh < zlow else -1                       # climbing toward -z (Rx +) or +z (Rx -)
        zc, yc = (zlow + zhigh) / 2, (ylow + yhigh) / 2
        Mr = M(T(xc, yc, zc), Rx(sgn * ang))
        box(col, 'col', w, 0.3, ln + 0.4, m=M(Mr, T(0, -0.15, 0)))
        box(vis, 'dark', w, 0.3, ln, m=M(Mr, T(0, -0.25, 0)), uvs=2.0)
        n = int(round(rise / 0.22))
        for k in range(n):
            z = zlow + (zhigh - zlow) * (k + 0.5) / n; y = ylow + rise * (k + 1) / n
            box(vis, 'plank', w - 0.1, 0.06, run / n + 0.04, m=T(xc, y - 0.03, z), uvs=1.5)
            box(vis, 'dark', w - 0.1, rise / n, 0.04, m=T(xc, y - rise / n / 2, z + sgn * run / n / 2), uvs=1.5)
        for sx in (-1, 1):
            box(vis, 'dark', 0.12, 0.9, ln, m=M(Mr, T(sx * (w / 2 - 0.06), 0.25, 0)), uvs=2.0)

    def rail(x0, z0, x1, z1, y):
        ln = math.hypot(x1 - x0, z1 - z0); ry = math.degrees(math.atan2(x1 - x0, z1 - z0))
        Mr = M(T((x0 + x1) / 2, y, (z0 + z1) / 2), Ry(ry))
        box(vis, 'dark', 0.1, 0.1, ln, m=M(Mr, T(0, 1.05, 0)), uvs=1.5)
        box(vis, 'dark', 0.06, 0.06, ln, m=M(Mr, T(0, 0.55, 0)), uvs=1.5)
        box(col, 'col', 0.2, 1.3, ln, m=M(Mr, T(0, 0.65, 0)))
        for k in range(int(ln / 1.6) + 2):
            f = min(1.0, k * 1.6 / ln); box(vis, 'dark', 0.12, 1.1, 0.12, m=T(x0 + (x1 - x0) * f, y + 0.55, z0 + (z1 - z0) * f), uvs=1.0)

    def glass_x(x, z0, z1, y0, y1):
        blk('glass', x, (y0 + y1) / 2, (z0 + z1) / 2, 0.05, y1 - y0, z1 - z0)
        for z in np.linspace(z0, z1, max(2, int((z1 - z0) / 3.2) + 1)):
            box(vis, 'dark', 0.2, y1 - y0, 0.16, m=T(x, (y0 + y1) / 2, z), uvs=1.2)

    sdeco = D.setdefault('sdeco', [])
    def deco(name, x, y, z, ry, size, axis='l'):
        if name in _o.META: sdeco.append(_o.place(name, x, y, z, ry, size, axis))

    teams = []
    rng = random.Random(3)
    for ti, (key, hx, rgb, s, zc) in enumerate(TEAMS):
        X = lambda u: s * (XO - u)                    # u = metres in from the outer wall
        ryi, ryo = -90 * s, 90 * s                    # facing the middle / facing the outer wall
        Zl, Zh = zc - HALF, zc + HALF
        # ---- walls
        wall_x(X(0), Zl, Zh, Y0, YT, [(zc, DW, DH)])                                   # outer wall, start door D0
        wall_x(X(18), Zl, Zh, Y0, YU - 0.25, [(zc - 7, DW, DH), (zc + 10, DW, DH)])    # middle wall downstairs: D1, D2
        wall_x(X(18), Zl, Zh, YU, YT, [(zc - 7, DW, DH)])                              # middle wall upstairs: D3
        blk('dark', X(18), YU - 0.125, zc, WT, 0.25, 2 * HALF)
        # centre wall (glass): downstairs one big window into R2; upstairs two windows either side of the last door D4
        cx = X(36)
        blk('plank', cx, Y0 + 0.45, zc, WT, 0.9, 2 * HALF)
        blk('plank', cx, (Y0 + 4.5 + YU) / 2, zc, WT, YU - Y0 - 4.5, 2 * HALF)
        for zz in (Zl + 0.6, Zh - 0.6): blk('plank', cx, (Y0 + 0.9 + Y0 + 4.5) / 2, zz, WT, 3.6, 1.2)
        glass_x(cx, Zl + 1.2, Zh - 1.2, Y0 + 0.9, Y0 + 4.5)
        blk('plank', cx, YU + 0.45, zc, WT, 0.9, 2 * HALF)
        blk('plank', cx, (YU + 4.2 + YT) / 2, zc, WT, YT - YU - 4.2, 2 * HALF)
        for (a, b) in ((Zl, Zl + 1.2), (zc - 4.2, zc - DW / 2), (zc + DW / 2, zc + 4.2), (Zh - 1.2, Zh)):
            blk('plank', cx, (YU + 0.9 + YU + 4.2) / 2, (a + b) / 2, WT, 3.3, b - a)
        blk('plank', cx, YU + DH + (4.2 - DH) / 2 + 0.0, zc, WT, 4.2 - DH, DW)        # over the door, under the header
        frame_x(cx, zc, YU, DW, DH)
        glass_x(cx, Zl + 1.2, zc - 4.2, YU + 0.9, YU + 4.2); glass_x(cx, zc + 4.2, Zh - 1.2, YU + 0.9, YU + 4.2)
        # lane walls (shared with the next lane) + the two ends of the complex
        for zw in ([Zl] + ([Zh] if zc > 0 else [])):
            wall_z(zw, min(X(0), X(36)), max(X(0), X(36)), Y0, YT)
        # ---- upper floor (with the stairwell hole in R3's corner) + the stair
        ua, ub = 14.5, 18.0                           # the stairwell strip, inside R1
        slab(min(X(0), X(ua)), max(X(0), X(ua)), Zl, Zh, YU)
        slab(min(X(ua), X(ub)), max(X(ua), X(ub)), Zl, zc - 2.0, YU)
        slab(min(X(ub), X(36)), max(X(ub), X(36)), Zl, Zh, YU)
        blk('plank', X(ua), (Y0 + YU) / 2, (zc - 3 + Zh) / 2, WT, YU - Y0, Zh - (zc - 3))   # the well's walls (R1 can't get in)
        blk('plank', X((ua + ub) / 2), (Y0 + YU) / 2, zc - 3, ub - ua, YU - Y0, WT)
        ramp(X((ua + ub) / 2), ub - ua - 0.35, zc + 8.0, zc - 2.0, Y0, YU)
        rail(X(ua), zc - 2.0, X(ua), Zh - 0.2, YU)
        # ---- team colour: a glowing bar over every door (both faces) + a banner beside the start door outside
        for (u, y, zz) in ((0, Y0, zc), (18, Y0, zc - 7), (18, Y0, zc + 10), (18, YU, zc - 7), (36, YU, zc)):
            for dx in (-0.2, 0.2): box(vis, 'esc%d' % ti, 0.05, 0.14, DW + 0.4, m=T(X(u) + dx, y + DH + 0.36, zz))
        for sz in (-1, 1):
            box(vis, 'esc%d' % ti, 0.06, 4.6, 1.3, m=T(X(-0.2), Y0 + 2.6, zc + sz * 2.9))
            box(vis, 'gold', 0.08, 0.1, 1.42, m=T(X(-0.22), Y0 + 4.95, zc + sz * 2.9))
        # ---- R1 (lantern code): shelves, a table, barrels, crates; the lanterns hide in/under/behind them
        deco('bottles', X(0.75), Y0 + 1.6, zc - 10.2, ryi, 1.9, 'w')                  # high shelf of bottles (lantern A on top)
        bevel_box(vis, 'dark', 0.5, 0.1, 2.2, 0.02, m=T(X(0.55), Y0 + 1.55, zc - 10.2), uvs=1.0)
        for sz in (-1, 1): box(vis, 'dark', 0.4, 1.55, 0.1, m=T(X(0.55), Y0 + 0.78, zc - 10.2 + sz * 1.0), uvs=1.0)
        deco('coffeetable', X(8.5), Y0, zc + 8.5, 15, 2.2)                            # lantern B under it
        deco('barrel', X(12.4), Y0, zc - 10.4, 0, 1.0, 'h'); deco('barrel', X(13.4), Y0, zc - 9.5, 40, 1.0, 'h'); deco('barrel', X(12.0), Y0, zc - 8.9, 80, 0.9, 'h')
        deco('bench', X(1.0), Y0, zc + 4.0, ryi, 1.9)
        for (u, v) in ((3, -6), (6, 3), (10.5, -3)): sdeco.append(['sp_lantern_%s' % 'abc'[rng.randrange(3)], r3(X(u)), r3(YU - 0.3), r3(zc + v), rng.uniform(0, 360), 1.0])
        # ---- R2 (lily pads): dark water floor, reeds round the edge
        box(vis, 'water', 17.4, 0.02, 2 * HALF - 0.6, m=T(X(27), Y0 + 0.012, zc))
        for k in range(10):
            u = 19 + rng.uniform(0, 16.4); v = rng.choice([-1, 1]) * rng.uniform(9.6, 11.3)
            deco('cattails', X(u), Y0, zc + v, rng.uniform(0, 360), 0.9)
        for (u, v) in ((22, 0), (31, 0), (27, -9)): sdeco.append(['sp_lantern_%s' % 'abc'[rng.randrange(3)], r3(X(u)), r3(YU - 0.3), r3(zc + v), rng.uniform(0, 360), 1.0])
        # ---- R3 (card memory): a big dark board for the cards on the outer wall, a card table
        bevel_box(vis, 'dark', 0.12, 4.3, 9.6, 0.05, m=T(X(0.2), YU + 2.05, zc), uvs=2.0)
        bevel_box(vis, 'gold', 0.14, 0.1, 9.8, 0.02, m=T(X(0.21), YU + 4.25, zc))
        bevel_box(vis, 'gold', 0.14, 0.1, 9.8, 0.02, m=T(X(0.21), YU - 0.15 + 0.2, zc))
        deco('cardtable', X(8.5), YU, zc + 6.5, 0, 2.0)
        for (u, v) in ((4, -8), (9, 0), (12, -8), (6, 8)): sdeco.append(['sp_lantern_%s' % 'abc'[rng.randrange(3)], r3(X(u)), r3(YT - 0.3), r3(zc + v), rng.uniform(0, 360), 1.0])
        # ---- R4 (frog choir): 4 tree stumps in a row, moss, a round counter
        frogs = []
        for k, v in enumerate((-6.0, -2.0, 2.0, 6.0)):
            fx = X(30.5)
            cyl(vis, 'dark', 0.62, 0.6, 14, m=T(fx, YU, zc + v)); cyl(vis, 'moss', 0.64, 0.05, 14, m=T(fx, YU + 0.58, zc + v))
            box(col, 'col', 1.1, 0.6, 1.1, m=T(fx, YU + 0.3, zc + v))
            frogs.append([r3(fx), r3(YU + 0.62), r3(zc + v), ryo])
        for (u, v) in ((25, -10.5), (33, 10.5), (34.5, -10.5)): deco('mossclump', X(u), YU, zc + v, rng.uniform(0, 360), 1.4)
        for (u, v) in ((23, 0), (31, -8), (31, 8)): sdeco.append(['sp_lantern_%s' % 'abc'[rng.randrange(3)], r3(X(u)), r3(YT - 0.3), r3(zc + v), rng.uniform(0, 360), 1.0])
        # ---- the clue painting frame (R1) and the keypad back plate (R1, beside D1)
        bevel_box(vis, 'dark', 0.1, 1.3, 2.6, 0.03, m=T(X(0.2), Y0 + 2.1, zc + 6.5), uvs=1.0)
        bevel_box(vis, 'gold', 0.12, 1.42, 2.72, 0.02, m=T(X(0.18), Y0 + 2.1, zc + 6.5))
        bevel_box(vis, 'iron', 0.08, 2.1, 1.35, 0.03, m=T(X(17.8), Y0 + 1.75, zc - 4.0), uvs=0.6)
        bevel_box(vis, 'dark', 0.06, 0.5, 1.5, 0.02, m=T(X(17.82), Y0 + 2.95, zc - 4.0), uvs=0.6)
        # ---- data for the game
        lant = [[X(0.75), Y0 + 2.35, zc - 10.6], [X(8.5), Y0 + 0.22, zc + 8.5], [X(13.7), Y0 + 0.25, zc - 11.0], [X(1.1), Y0 + 3.6, zc + 10.9]]
        keys = []
        for k in range(10):                                         # 1 2 3 / 4 5 6 / 7 8 9 / _ 0 _
            c, r = (1, 3) if k == 0 else ((k - 1) % 3, (k - 1) // 3)
            keys.append([r3(X(17.72)), r3(Y0 + 2.42 - r * 0.42), r3(zc - 4.0 + (c - 1) * 0.42 * (-s))])
        cards = []
        for r in range(2):
            for c in range(6):
                cards.append([r3(X(0.36)), r3(YU + 1.1 + r * 1.85), r3(zc + (c - 2.5) * 1.45 * (-s)), ryi])
        # (fps) the static bits of the puzzles live in this model, not as separate objects: keypad buttons, lantern caps, rug border
        for (kx, ky, kz) in keys: box(vis, 'dark', 0.05, 0.34, 0.34, m=T(kx + 0.03 * s, ky, kz))
        for (lx, ly, lz) in lant:
            cyl(vis, 'iron', 0.13, 0.04, 10, m=T(lx, ly, lz)); cyl(vis, 'iron', 0.09, 0.05, 10, m=T(lx, ly + 0.34, lz))
        rw_, rd_ = 12.5, 21.5
        for (dx, dz, w_, d_) in ((0, rd_ / 2 - 0.35, rw_ - 0.4, 0.12), (0, -rd_ / 2 + 0.35, rw_ - 0.4, 0.12), (rw_ / 2 - 0.35, 0, 0.12, rd_ - 0.4), (-rw_ / 2 + 0.35, 0, 0.12, rd_ - 0.4)):
            box(vis, 'esc%d' % ti, w_, 0.01, d_, m=T(X(7.25) + dx, Y0 + 0.085, zc + dz))
        teams.append(dict(
            k=key, c=hx, side=s, zc=zc, word='e_' + key,
            rug=[r3(X(7.25)), r3(Y0), zc, 12.5, 21.5],
            doors=[[r3(X(0)), Y0, zc], [r3(X(18)), Y0, zc - 7], [r3(X(18)), Y0, zc + 10], [r3(X(18)), YU, zc - 7], [r3(X(36)), YU, zc]],
            lanterns=[[r3(a), r3(b), r3(c)] for a, b, c in lant],
            clue=[r3(X(0.28)), r3(Y0 + 2.1), r3(zc + 6.5), ryi],
            keys=keys, disp=[r3(X(17.76)), r3(Y0 + 2.95), r3(zc - 4.0), ryo],
            pads=[[r3(X(u)), r3(Y0), r3(zc + v)] for (u, v) in ((22.5, -5.5), (31.5, -5.5), (22.5, 5.0), (31.5, 5.0))],
            cards=cards, frogs=frogs, rounds=[r3(X(26.5)), r3(YU + 0.1), r3(zc + 9.0), ryo],
            hint=[[r3(X(9)), r3(Y0 + 3.6), zc, ryi], [r3(X(27)), r3(Y0 + 3.6), zc, ryi], [r3(X(9)), r3(YU + 3.6), zc, ryi], [r3(X(27)), r3(YU + 3.6), zc, ryi]]))
    # ---- the middle: corridor downstairs (open at both ends), Victory Hall upstairs, the stair between them
    slab(-XC, -3.0, -ZB, ZB, YU); slab(3.0, XC, -ZB, ZB, YU); slab(-3.0, 3.0, -ZB, 23.5, YU); slab(-3.0, 3.0, 34.0, ZB, YU)
    ramp(0.0, 5.6, 33.5, 23.5, Y0, YU)
    rail(-3.0, 23.5, -3.0, 34.0, YU); rail(3.0, 23.5, 3.0, 34.0, YU); rail(-3.0, 34.0, 3.0, 34.0, YU)
    for zz in (-ZB, ZB):
        wall_z(zz, -XC, XC, YU, YT)
        blk('dark', 0.0, YU - 0.35, zz, 2 * XC, 0.7, WT + 0.1)
    # the progress boards (corridor + Victory Hall): a dark board with a gold rim; the lamps/clock are drawn by the game
    boards = [[0.0, Y0 + 2.6, -ZB + 0.6, 0.0], [0.0, YU + 2.6, -ZB + 0.6, 0.0]]
    for (bx, by, bz, _) in boards:
        bevel_box(vis, 'dark', 9.4, 4.0, 0.16, 0.05, m=T(bx, by, bz - 0.1), uvs=2.0)
        bevel_box(vis, 'gold', 9.6, 0.1, 0.2, 0.02, m=T(bx, by + 2.02, bz - 0.1)); bevel_box(vis, 'gold', 9.6, 0.1, 0.2, 0.02, m=T(bx, by - 2.02, bz - 0.1))
        for k in range(6):
            box(vis, 'esc%d' % k, 1.1, 0.16, 0.04, m=T(bx + (k - 2.5) * 1.45, by + 1.25, bz))
    # Victory Hall dressing: a gold-rimmed dais in the middle, lantern rings of light
    cyl(vis, 'dark', 3.2, 0.18, 32, m=T(0, YU, 0)); cyl(vis, 'gold', 3.3, 0.04, 32, m=T(0, YU + 0.15, 0))
    box(col, 'col', 6.0, 0.18, 6.0, m=T(0, YU + 0.09, 0))
    for z in (-24, -12, 0, 12): sdeco.append(['sp_lantern_%s' % 'abc'[rng.randrange(3)], 0.0, r3(YT - 0.3), float(z), rng.uniform(0, 360), 1.2])
    for z in (-24, -8, 8): sdeco.append(['sp_lantern_%s' % 'abc'[rng.randrange(3)], 0.0, r3(YU - 0.35), float(z), rng.uniform(0, 360), 1.0])
    write(OUTG + 'sp_escape.glb', vis, mats)
    from shrink_glb import shrink
    shrink(OUTG + 'sp_escape.glb', OUTG + 'sp_escape.glb', 512)
    write(OUTG + 'sp_escape_col.glb', col, colm)
    door_glb()
    cardset = card_images()
    D['escape'] = dict(y0=Y0, yu=YU, teams=teams, boards=boards, vh=[0.0, r3(YU + 0.2), 0.0], slide=SLIDE, dw=DW, dh=DH,
                       lcols=LANTERN_COLS, fcols=FROG_COLS, cards=cardset,
                       frogm=[_o.place(n, 0, 0, 0, 0, 0.62, 'l') for n in ('frogbull', 'frogtree')],
                       signs=[[r3(s * (XO + 1.2)), r3(Y0 + 2.4), z, 90 * s] for s in (-1, 1) for z in (-12.0, 12.0)])
    print('escape: 6 teams x 4 rooms, victory hall at y %.1f, %d memory cards' % (YU, len(cardset)))


def door_glb():
    """one timber door leaf: planks, iron bands and studs, a ring pull. Thin along x (the walls it sits in run along z); origin at the
    bottom centre"""
    m = Mesh(); w, h, t = DW - 0.06, DH - 0.04, 0.12
    for k in range(6):
        bevel_box(m, 'dark', t, h, w / 6 - 0.01, 0.01, m=T(0, h / 2, -w / 2 + w / 12 + k * w / 6), uvs=1.2)
    for y in (0.45, h / 2, h - 0.45):
        box(m, 'iron', t + 0.04, 0.12, w, m=T(0, y, 0), uvs=0.5)
        for k in range(7):
            for sx in (-1, 1): sphere(m, 'iron', 0.03, 6, 4, m=T(sx * (t / 2 + 0.02), y, -w / 2 + 0.15 + k * (w - 0.3) / 6))
    for sx in (-1, 1): sphere(m, 'gold', 0.07, 8, 6, m=T(sx * (t / 2 + 0.03), 1.1, w / 2 - 0.35))
    write(OUTG + 'sp_esc_door.glb', m, {k: MATS[k] for k in ('dark', 'iron', 'gold')})
    from shrink_glb import shrink
    shrink(OUTG + 'sp_esc_door.glb', OUTG + 'sp_esc_door.glb', 256)


def card_images():
    """small copies of 24 Mudwater cards for the memory game (cheap pictures, not text)"""
    os.makedirs(OUT + 'esc', exist_ok=True)
    have = [n for n in range(1, 121) if os.path.exists(MW + 'mwc_%03d.jpg' % n)]
    pick = random.Random(7).sample(have, min(24, len(have)))
    for n in pick:
        p = OUT + 'esc/k_%03d.jpg' % n
        if not os.path.exists(p): Image.open(MW + 'mwc_%03d.jpg' % n).convert('RGB').resize((216, 300), Image.LANCZOS).save(p, quality=84)
    bp = OUT + 'esc/back.jpg'
    if not os.path.exists(bp): Image.open(MW + 'mwc_back.jpg').convert('RGB').resize((216, 300), Image.LANCZOS).save(bp, quality=84)
    return sorted(pick)
