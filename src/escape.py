"""MUDWATER ESCAPE (game 3, floor 4 'rooms', y 40). Called by build_html.py: escape.apply(D, L, FL).

The owner's rules: all the teams begin in a different room; to progress they solve clues/puzzles to get to the next room, which may or may
not be on another floor. Built inside floor 4 (no taller tower needed): the floor is ~10 m high, so it gets a second level at +5.3 m.

  6 teams, one lane each: 3 lanes on the west half, 3 on the east half (z bands -36..-12, -12..12, 12..36).
  In every lane (u = metres in from the outer wall, v = metres along the lane from its middle). (v51) Every door is a CODE LOCK
  (12-key keypad; a wrong code locks that keypad for 30 s, so guessing is slow):
    R1 lower, outer (u 0..18)  - CRITTER SUMS: 8 chests hold picture sums (2 are FAKE); a painting gives the order of 4 critters
    R2 lower, inner (u 18..36) - SWAMP CIPHER: a message in secret marks; the key is torn in 6 pieces (in chests); the message asks
                                 a sum about things you count in the room (7 candles, 4 frogs, 5 lanterns, 6 chests)
       -> a stair (in an enclosed well carved out of R1's corner) climbs to the upper level
    R3 upper, outer            - WITCH'S EYE: the code floats in the air as paint strokes that only line up from one of 3 eyes
    R4 upper, inner            - WARDEN'S RIDDLE: 5 apes on 5 stools, hats/drinks/pets, clues on the walls and in chests
    -> the last door opens into the VICTORY HALL (upper level, the middle strip |x| < 8). First team out wins.
  Doors: D0 start door (outer wall, from the side aisle where the lifts + stairs arrive), D1 R1->R2, D2 R2->stair, D3 R3->R4, D4 R4->hall.
  The middle strip downstairs is the hosts' / spectators' corridor (glass into every R2), with a stair up to the Victory Hall (glass into
  every R4). Progress boards in both.
Writes sp_escape.glb (everything static), sp_escape_col.glb (invisible colliders), sp_esc_door.glb, sp_esc_lid.glb, esc/*.jpg (puzzles) and
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
WATER = dict(color=(0.02, 0.045, 0.035, 1), metal=0.0, rough=0.55, emis=(0.004, 0.014, 0.011))


def r3(v): return round(float(v), 3)


def apply(D, L, FL):
    Y0 = FL['rooms']; YU = Y0 + UP; YT = Y0 + 10.0
    vis, col = Mesh(), Mesh()
    mats = {k: MATS[k] for k in ('plank', 'dark', 'iron', 'gold', 'glass', 'glow', 'moss', 'rope', 'bartop', 'wetfloor', 'black', 'leather')}
    mats['wax'] = dict(color=(0.93, 0.88, 0.74, 1), rough=0.7, emis=(0.08, 0.06, 0.03))
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
        # (v45, owner: "the bottom of the door is blocked by wood") the low wall under the windows now stops either side of the last door
        for (a, b) in ((Zl, zc - DW / 2), (zc + DW / 2, Zh)): blk('plank', cx, YU + 0.45, (a + b) / 2, WT, 0.9, b - a)
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
        # ================= (v51, owner: "give them something that stumps them... difficult enough for 20+ people") every door is a
        # CODE LOCK now: R1 CRITTER SUMS, R2 SWAMP CIPHER, R3 WITCH'S EYE, R4 WARDEN'S RIDDLE. No pads, no frogs, no memory cards.
        def face_ry(f): return {'+u': ryi, '-u': ryo, '+v': 0.0, '-v': 180.0}[f]
        chests, kp = [], []

        def chest(room, u, v, f, yfl):
            """a wooden chest (body baked here; the lid is its own model so it can swing open). Front faces f."""
            x, z, ry = X(u), zc + v, face_ry(f)
            Mx = M(T(x, yfl, z), Ry(ry))
            box(vis, 'plank', 0.9, 0.42, 0.6, m=M(Mx, T(0, 0.21, 0)), uvs=0.8)
            for bx in (-0.3, 0.3): box(vis, 'iron', 0.06, 0.44, 0.62, m=M(Mx, T(bx, 0.21, 0)), uvs=0.4)
            box(vis, 'dark', 0.94, 0.06, 0.64, m=M(Mx, T(0, 0.03, 0)), uvs=0.6)
            box(col, 'col', 0.9, 0.5, 0.6, m=M(Mx, T(0, 0.25, 0)))
            chests.append([room, r3(x), r3(yfl), r3(z), r3(ry)])

        def keypad(uw, f, v, yfl):
            """the iron back plate of a 12-key keypad on the wall at u=uw, facing f (-1 = toward the outer wall, +1 = toward the
            middle). The keys, numbers and screen are added by the game."""
            sgn = -1 if f < 0 else 1
            box(vis, 'iron', 0.08, 2.45, 1.5, m=T(X(uw + sgn * 0.19), yfl + 1.8, zc + v), uvs=0.6)
            box(vis, 'gold', 0.1, 0.06, 1.56, m=T(X(uw + sgn * 0.2), yfl + 3.04, zc + v))
            box(vis, 'gold', 0.1, 0.06, 1.56, m=T(X(uw + sgn * 0.2), yfl + 0.56, zc + v))
            kp.append([r3(X(uw + sgn * 0.25)), r3(yfl + 1.5), r3(zc + v), ryo if f < 0 else ryi])

        def frame_on_x(uw, f, v, y, w, h):          # a dark board with a gold rim on a wall that runs along z
            sgn = -1 if f < 0 else 1
            bevel_box(vis, 'dark', 0.08, h + 0.16, w + 0.16, 0.02, m=T(X(uw + sgn * 0.19), y, zc + v), uvs=1.0)
            bevel_box(vis, 'gold', 0.06, h + 0.26, w + 0.26, 0.02, m=T(X(uw + sgn * 0.165), y, zc + v))
            return [r3(X(uw + sgn * 0.24)), r3(y), r3(zc + v), ryo if f < 0 else ryi]

        def frame_on_z(vw, f, u, y, w, h):          # the same on a lane wall (runs along x); f = +1 faces +z
            bevel_box(vis, 'dark', w + 0.16, h + 0.16, 0.08, 0.02, m=T(X(u), y, zc + vw + f * 0.19), uvs=1.0)
            bevel_box(vis, 'gold', w + 0.26, h + 0.26, 0.06, 0.02, m=T(X(u), y, zc + vw + f * 0.165))
            return [r3(X(u)), r3(y), r3(zc + vw + f * 0.24), 0.0 if f > 0 else 180.0]

        # ---- R1 CRITTER SUMS: 8 chests (picture sums inside), the painting (the code's order), a keypad by the door to R2
        for (u, v, f) in ((0.6, -10.4, '+u'), (0.6, 10.4, '+u'), (4.5, -11.3, '+v'), (9.0, -11.3, '+v'), (13.0, -11.3, '+v'),
                          (15.6, -11.3, '+v'), (5.0, 11.3, '-v'), (10.0, 11.3, '-v')):
            chest(0, u, v, f, Y0)
        for (u, v) in ((3, -6), (6, 3), (10.5, -3)): sdeco.append(['sp_lantern_%s' % 'abc'[rng.randrange(3)], r3(X(u)), r3(YU - 0.3), r3(zc + v), rng.uniform(0, 360), 1.0])
        paint = frame_on_x(0, 1, 6.5, Y0 + 2.1, 2.5, 1.05)
        keypad(18, -1, -4.1, Y0)
        # ---- R2 SWAMP CIPHER: the coded message on the wall, EXACTLY 7 candles, 4 frogs, 5 lanterns and 6 chests to count
        msg = frame_on_x(18, 1, -1.5, Y0 + 2.45, 5.0, 1.7)
        keypad(18, 1, 6.5, Y0)
        tx, tz = X(27), zc                                            # the candle table (long side along the lane)
        bevel_box(vis, 'dark', 1.2, 0.08, 3.0, 0.02, m=T(tx, Y0 + 0.9, tz), uvs=1.2)
        for (dx, dz) in ((-0.5, -1.35), (0.5, -1.35), (-0.5, 1.35), (0.5, 1.35)): box(vis, 'dark', 0.08, 0.86, 0.08, m=T(tx + dx, Y0 + 0.43, tz + dz), uvs=1.0)
        box(col, 'col', 1.2, 0.95, 3.0, m=T(tx, Y0 + 0.47, tz))
        for k in range(7):
            cz = tz + (k - 3) * 0.4; ch = 0.22 + 0.06 * ((k * 3) % 4)
            cyl(vis, 'gold', 0.08, 0.02, 12, m=T(tx, Y0 + 0.94, cz))
            cyl(vis, 'wax', 0.045, ch, 10, m=T(tx, Y0 + 0.96, cz))
            sphere(vis, 'glow', 0.035, 8, 6, m=M(T(tx, Y0 + 0.96 + ch + 0.05, cz), np.diag([1, 1.7, 1, 1])))
        shx, shy, shz = X(27), Y0 + 1.45, zc + HALF - WT / 2 - 0.22   # the frog shelf on the far lane wall
        bevel_box(vis, 'dark', 3.0, 0.06, 0.44, 0.02, m=T(shx, shy, shz), uvs=1.2)
        for dx in (-1.2, 1.2): box(vis, 'iron', 0.05, 0.3, 0.3, m=T(shx + dx, shy - 0.18, shz + 0.07))
        for k in range(4):
            deco('frogtree', shx + (k - 1.5) * 0.72, shy + 0.03, shz - 0.02, 180, 0.5)
        for (u, v) in ((21, -6), (27, -6), (33, -6), (21, 6), (33, 6)):
            sdeco.append(['sp_lantern_%s' % 'abc'[rng.randrange(3)], r3(X(u)), r3(YU - 0.3), r3(zc + v), rng.uniform(0, 360), 1.0])
        for (u, v, f) in ((20.5, -11.3, '+v'), (33.5, -11.3, '+v'), (23.0, 11.3, '-v'), (31.0, 11.3, '-v'), (35.4, -5.0, '-u'), (35.4, 4.0, '-u')):
            chest(1, u, v, f, Y0)
        # ---- R3 WITCH'S EYE: three painted eyes on the floor (one is true); the code floats in the air as paint strokes that only
        # line up from the true eye (made by the game). Keypad by the door to R4.
        eye = dict(spots=[[r3(X(u)), r3(YU), r3(zc + v)] for (u, v) in ((2.5, 9.5), (2.0, -3.0), (10.0, 9.5))],
                   c=[r3(X(13.0)), r3(YU + 2.8), r3(zc - 9.0)])
        keypad(18, -1, -4.1, YU)
        for (u, v) in ((6, -11), (16, 6)): sdeco.append(['sp_lantern_%s' % 'abc'[rng.randrange(3)], r3(X(u)), r3(YT - 0.3), r3(zc + v), rng.uniform(0, 360), 1.0])
        # (v52, owner: "add clickable things to the room to trick players into thinking there is something they're supposed to be
        # deciphering... and to waste their time") a crystal ball (shows random numbers), 5 potion bottles (change colour), a spell book
        # (strange pages). None of them mean anything. Kept out of the lines of sight from the 3 hidden spots.
        bx_, bz_ = X(6.0), zc - 10.4                                                    # crystal ball pedestal
        cyl(vis, 'dark', 0.32, 0.08, 16, m=T(bx_, YU, bz_)); cyl(vis, 'dark', 0.12, 0.95, 12, m=T(bx_, YU, bz_)); cyl(vis, 'gold', 0.26, 0.1, 16, m=T(bx_, YU + 0.95, bz_), r2=0.2)
        box(col, 'col', 0.6, 1.1, 0.6, m=T(bx_, YU + 0.55, bz_))
        px_ = X(0.42)                                                                   # potion shelf on the outer wall
        bevel_box(vis, 'dark', 0.4, 0.06, 2.6, 0.02, m=T(px_, YU + 1.3, zc - 8.0), uvs=1.2)
        for dz_ in (-1.1, 1.1): box(vis, 'iron', 0.3, 0.3, 0.05, m=T(X(0.3), YU + 1.12, zc - 8.0 + dz_))
        lx_, lz_ = X(8.0), zc + 4.0                                                     # spell book lectern, the book faces the outer wall
        box(vis, 'dark', 0.5, 0.06, 0.5, m=T(lx_, YU + 0.03, lz_)); box(vis, 'dark', 0.12, 1.05, 0.12, m=T(lx_, YU + 0.55, lz_))
        bevel_box(vis, 'plank', 0.7, 0.05, 0.55, 0.02, m=M(T(lx_, YU + 1.12, lz_), Ry(ryo), Rx(-25)), uvs=0.8)
        box(col, 'col', 0.7, 1.2, 0.6, m=T(lx_, YU + 0.6, lz_))
        decoy = dict(ball=[r3(bx_), r3(YU + 1.33), r3(bz_)], potions=[[r3(X(0.42)), r3(YU + 1.33), r3(zc - 8.0 + (j - 2) * 0.5)] for j in range(5)],
                     book=[r3(lx_), r3(YU + 1.2), r3(lz_), ryo])
        cyl(vis, 'black', 0.55, 0.7, 18, m=T(X(16.0), YU, zc - 10.8), r2=0.62); cyl(vis, 'glow', 0.5, 0.02, 18, m=T(X(16.0), YU + 0.62, zc - 10.8))   # the witch's cauldron (out of the way)
        box(col, 'col', 1.2, 0.7, 1.2, m=T(X(16.0), YU + 0.35, zc - 10.8))
        # ---- R4 WARDEN'S RIDDLE: a bar with 5 numbered stools, the question board, 8 clue notes on the walls, 6 chests
        bz = zc + HALF - WT / 2 - 0.36
        bevel_box(vis, 'bartop', 12.4, 0.08, 0.8, 0.02, m=T(X(27), YU + 1.1, bz), uvs=2.0)
        box(vis, 'dark', 12.0, 1.06, 0.6, m=T(X(27), YU + 0.53, bz + 0.08), uvs=1.6)
        box(col, 'col', 12.4, 1.15, 0.8, m=T(X(27), YU + 0.57, bz))
        stools = []
        for k in range(1, 6):
            u = 27 - (3 - k) * 2 * s                                  # stool 1 is on the LEFT as you face the bar (looking toward +z)
            sx_, sz_ = X(u), bz - 1.05
            cyl(vis, 'iron', 0.22, 0.04, 14, m=T(sx_, YU, sz_)); cyl(vis, 'iron', 0.04, 0.72, 8, m=T(sx_, YU, sz_))
            cyl(vis, 'leather', 0.24, 0.1, 16, m=T(sx_, YU + 0.72, sz_)); cyl(vis, 'gold', 0.2, 0.02, 14, m=T(sx_, YU + 0.32, sz_))
            stools.append([r3(sx_), r3(YU + 2.1), r3(zc + HALF - WT / 2 - 0.05), 180.0])     # big stool number on the wall over it
            bevel_box(vis, 'dark', 0.8, 0.8, 0.06, 0.02, m=T(sx_, YU + 2.1, zc + HALF - WT / 2 - 0.02)); bevel_box(vis, 'gold', 0.9, 0.9, 0.04, 0.02, m=T(sx_, YU + 2.1, zc + HALF - WT / 2 - 0.005))
        board = frame_on_x(18, 1, 3.5, YU + 2.45, 4.2, 2.0)
        wnotes = [frame_on_z(-HALF + WT / 2, 1, u, YU + 1.95, 1.7, 0.57) for u in (21.0, 24.5, 28.0, 31.5)]      # (v52) 5 clue frames (6-10 clues now)
        wnotes += [frame_on_x(18, 1, v, YU + 1.95, 1.7, 0.57) for v in (8.4,)]
        for (u, v, f) in ((35.4, -9.0, '-u'), (35.4, -5.5, '-u'), (35.4, 6.5, '-u'), (35.4, 9.3, '-u'), (24.5, -2.5, '-u'), (29.5, 3.5, '-u')):
            chest(3, u, v, f, YU)
        keypad(36, -1, 2.75, YU)
        rw_, rd_ = 12.5, 21.5
        for (dx, dz, w_, d_) in ((0, rd_ / 2 - 0.35, rw_ - 0.4, 0.12), (0, -rd_ / 2 + 0.35, rw_ - 0.4, 0.12), (rw_ / 2 - 0.35, 0, 0.12, rd_ - 0.4), (-rw_ / 2 + 0.35, 0, 0.12, rd_ - 0.4)):
            box(vis, 'esc%d' % ti, w_, 0.01, d_, m=T(X(7.25) + dx, Y0 + 0.085, zc + dz))
        teams.append(dict(
            k=key, c=hx, side=s, zc=zc, word='e_' + key,
            rug=[r3(X(7.25)), r3(Y0), zc, 12.5, 21.5],
            doors=[[r3(X(0)), Y0, zc], [r3(X(18)), Y0, zc - 7], [r3(X(18)), Y0, zc + 10], [r3(X(18)), YU, zc - 7], [r3(X(36)), YU, zc]],
            kp=kp, chests=chests, paint=paint, msg=msg, board=board, wnotes=wnotes, stools=stools, eye=eye, decoy=decoy,
            rsigns=[[r3(X(0.25)), r3(Y0 + 2.7), r3(zc - 6.0), ryi, 'esc_r1'], [r3(X(27)), r3(Y0 + 3.1), r3(zc - HALF + WT / 2 + 0.06), 0.0, 'esc_r2'],
                    [r3(X(0.25)), r3(YU + 2.6), r3(zc + 0.5), ryi, 'esc_r3'], [r3(X(18.2)), r3(YU + 2.45), r3(zc - 2.6), ryi, 'esc_r4']],
            hint=[[r3(X(9)), r3(Y0 + 3.6), zc, ryi], [r3(X(27)), r3(Y0 + 3.6), zc, ryi], [r3(X(9)), r3(YU + 3.6), zc, ryi], [r3(X(27)), r3(YU + 3.6), zc, ryi]]))
    # ---- the middle: corridor downstairs (open at both ends), Victory Hall upstairs, the stair between them
    slab(-XC, -3.0, -ZB, ZB, YU); slab(3.0, XC, -ZB, ZB, YU); slab(-3.0, 3.0, -ZB, 23.5, YU); slab(-3.0, 3.0, 34.0, ZB, YU)
    ramp(0.0, 5.6, 33.5, 23.5, Y0, YU)
    rail(-3.0, 23.5, -3.0, 34.0, YU); rail(3.0, 23.5, 3.0, 34.0, YU); rail(-3.0, 34.0, 3.0, 34.0, YU)
    for zz in (-ZB, ZB):
        wall_z(zz, -XC, XC, YU, YT)
        blk('dark', 0.0, YU - 0.35, zz, 2 * XC, 0.7, WT + 0.1)
    # the progress boards (corridor + Victory Hall): a dark board with a gold rim; the lamps/clock are drawn by the game
    # (v52, owner: "this board too uses a very primitive design") the boards are a painted picture now (esc/board_bg.jpg: frame, title,
    # team plates, room rows, gem sockets, the winner plaque); the game lays glowing gems, counts, the clock, medals and the winner on it
    boards = [[0.0, Y0 + 2.55, -ZB + 0.6, 0.0], [0.0, YU + 2.37, -ZB + 0.6, 0.0]]
    for (bx, by, bz, _) in boards:
        bevel_box(vis, 'dark', 8.9, 4.6, 0.16, 0.05, m=T(bx, by, bz - 0.1), uvs=2.0)
        bevel_box(vis, 'gold', 9.0, 0.1, 0.2, 0.02, m=T(bx, by + 2.32, bz - 0.1)); bevel_box(vis, 'gold', 9.0, 0.1, 0.2, 0.02, m=T(bx, by - 2.32, bz - 0.1))
    # Victory Hall dressing: a gold-rimmed dais in the middle, lantern rings of light
    cyl(vis, 'dark', 3.2, 0.18, 32, m=T(0, YU, 0)); cyl(vis, 'gold', 3.3, 0.04, 32, m=T(0, YU + 0.15, 0))
    box(col, 'col', 6.0, 0.18, 6.0, m=T(0, YU + 0.09, 0))
    for z in (-24, -12, 0, 12): sdeco.append(['sp_lantern_%s' % 'abc'[rng.randrange(3)], 0.0, r3(YT - 0.3), float(z), rng.uniform(0, 360), 1.2])
    # (v51) no lanterns in the corridor any more: the cipher room counts LANTERNS and the corridor shows through its glass
    write(OUTG + 'sp_escape.glb', vis, mats)
    from shrink_glb import shrink
    shrink(OUTG + 'sp_escape.glb', OUTG + 'sp_escape.glb', 512)
    write(OUTG + 'sp_escape_col.glb', col, colm)
    door_glb(); lid_glb()
    import escape_puzzles as EP
    pools = EP.build_all()
    D['escape'] = dict(y0=Y0, yu=YU, teams=teams, boards=boards, vh=[0.0, r3(YU + 0.2), 0.0], slide=SLIDE, dw=DW, dh=DH, lock=30000,
                       sums=[dict(notes=p['notes'], paint=p['paint'], code=p['code'], fake=p['fake']) for p in pools['sums']],
                       cipher=[dict(msg=p['msg'], mh=p['mh'], keys=p['keys'], code=p['code'], q=p['q']) for p in pools['cipher']],
                       riddle=[dict(notes=p['notes'], code=p['code']) for p in pools['riddle']], empty=pools['empty'], pages=pools['pages'],
                       signs=[[r3(s * (XO + 1.2)), r3(Y0 + 2.4), z, 90 * s] for s in (-1, 1) for z in (-12.0, 12.0)])
    print('escape: 6 teams x 4 code rooms, victory hall at y %.1f; pools %d sums, %d ciphers, %d riddles' % (YU, len(pools['sums']), len(pools['cipher']), len(pools['riddle'])))


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


def lid_glb():
    """a chest lid: origin at the hinge (back top edge of the chest), the lid reaches toward +z; it opens by turning rx negative"""
    m = Mesh()
    bevel_box(m, 'plank', 0.94, 0.14, 0.62, 0.02, m=T(0, 0.07, 0.31), uvs=0.8)
    for bx in (-0.3, 0.3): box(m, 'iron', 0.06, 0.16, 0.64, m=T(bx, 0.07, 0.31), uvs=0.4)
    box(m, 'gold', 0.14, 0.16, 0.04, m=T(0, 0.0, 0.63))
    write(OUTG + 'sp_esc_lid.glb', m, {k: MATS[k] for k in ('plank', 'iron', 'gold')})
    from shrink_glb import shrink
    shrink(OUTG + 'sp_esc_lid.glb', OUTG + 'sp_esc_lid.glb', 256)


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
