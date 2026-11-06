"""MUD ROYALE (game 2, floor 3 'cards', y 32) - the arena. Called by build_html.py: royale.apply(D, L, FL).

The owner's rules (agreed): players WALK ONTO a team's area to join it and can switch until the host presses START. Then every player
gets 5 Mudwater cards and places them on squares of a 196-square board (14 x 14; it was 10 x 10 until v36). After 3 minutes the team holding the most squares wins.
Placing a card next to an enemy card captures it when your card's number on that side beats theirs (each card has top / left / right /
bottom numbers, printed in its corner) - the Mudwater card rules, like the owner's Territory game but with cards.

Built here (static GLBs) + D['royale'] for the game code in spire_src.html (block "MUD ROYALE"):
  sp_royale.glb (one model, shared textures): corner score signs (no hanging scoreboard - owner) +
                         a low dais with the 14 x 14 board (green felt squares, gold inlay, dark timber frame, gilt corner diamonds)
  sp_royale_pens.glb   : 4 team pens round the board (rope-and-post fences, team-colour flag poles, a hanging name board each)
  sp_royale_score.glb  : a four-sided scoreboard hanging over the middle of the board on chains
  sp_royale_hands.glb  : 4 hanging "YOUR HAND" boards, one over each edge of the board, tilted down at the players
  royale/c_NNN.jpg     : small copies of the 120 Mudwater cards (the board + hands show these as images - cheap to draw)
  royale/t_N.png       : the team glow under a card (who owns the square)"""
import math, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from glb import Mesh, write, box, bevel_box, tube, sphere, cyl, T, M, Ry, Rx
from kit import MATS

OUT = '/home/claude/spire/out/'
OUTG = OUT + 'glb/'
MW = '/home/claude/dinopawnz/mudwater/'

TEAMS = [  # key, name sprite, colour (hex for the page), rgb 0..1 for the models
    ('gators', 'rt_0', '#56d364', (0.30, 0.78, 0.36)),
    ('crawdads', 'rt_1', '#e5533d', (0.86, 0.30, 0.22)),
    ('bullfrogs', 'rt_2', '#f2b632', (0.95, 0.70, 0.18)),
    ('catfish', 'rt_3', '#33c9c0', (0.20, 0.76, 0.72)),
]
N, TS = 14, 2.6                      # (v36, owner) 14 x 14 = 196 squares, 2.6 m each (36.4 m board) for 100+ players
B = N * TS / 2                       # half the board = 18.2 m
DH = 0.12                            # the dais is 12 cm high: you walk straight up onto it
FRAME = 1.3                          # timber frame round the squares
PENS = [(0.0, -29.0, 0.0), (33.0, 0.0, -90.0), (0.0, 29.0, 180.0), (-33.0, 0.0, 90.0)]   # x, z, ry: each pen faces the board
PEN_W, PEN_D = 12.0, 6.0


BADGE_FONT = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'


def badge_card(src, vals, size=(360, 500)):
    """(v37, owner) one BIG number on each side of the card - top, left, right, bottom - so a player only reads the edge that is
    touching the card they're battling (the printed numbers are tiny and all bunched in the top-left corner)"""
    from PIL import ImageFont
    W, H = size
    im = Image.open(src).convert('RGB').resize(size, Image.LANCZOS).convert('RGBA')
    lay = Image.new('RGBA', size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    R = 46; f = ImageFont.truetype(BADGE_FONT, 74)
    t, l, r, b = vals
    for (cx, cy, v) in ((W / 2, R + 8, t), (R + 8, H / 2, l), (W - R - 8, H / 2, r), (W / 2, H - R - 8, b)):
        sh = Image.new('RGBA', size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx - R - 4, cy - R + 2, cx + R + 4, cy + R + 10], fill=(0, 0, 0, 150))
        lay = Image.alpha_composite(lay, sh.filter(ImageFilter.GaussianBlur(5))); d = ImageDraw.Draw(lay)
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(214, 168, 66, 255))                  # gold rim
        d.ellipse([cx - R + 6, cy - R + 6, cx + R - 6, cy + R - 6], fill=(28, 18, 10, 255))      # dark centre
        d.text((cx, cy + 2), str(v), font=f, fill=(255, 238, 196, 255), anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0, 255))
    return Image.alpha_composite(im, lay).convert('RGB')


def card_images():
    """small jpgs of the 120 cards with the big side numbers baked in (images are cheap to draw - no text elements)"""
    os.makedirs(OUT + 'royale', exist_ok=True)
    cards = json.load(open('/home/claude/spire/cards/cards.json'))
    for k in range(1, 121):
        dst = OUT + 'royale/c_%03d.jpg' % k
        v = cards[str(k)]
        badge_card(MW + 'mwc_%03d.jpg' % k, (v['t'], v['l'], v['r'], v['b'])).save(dst, quality=84, optimize=True)
    for ti, (_, _, hx, rgb) in enumerate(TEAMS):
        S = 256; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        c = tuple(int(v * 255) for v in rgb)
        d.rectangle([0, 0, S - 1, S - 1], fill=c + (120,))
        glow = Image.new('RGBA', (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
        g.rectangle([6, 6, S - 7, S - 7], outline=c + (255,), width=16)
        glow = glow.filter(ImageFilter.GaussianBlur(5))
        im = Image.alpha_composite(im, glow)
        ImageDraw.Draw(im).rectangle([10, 10, S - 11, S - 11], outline=(255, 255, 255, 230), width=3)
        im.save(OUT + 'royale/t_%d.png' % ti)
    if not os.path.exists(OUT + 'royale/back.jpg'):
        Image.open(MW + 'mwc_back.jpg').convert('RGB').resize((288, 400), Image.LANCZOS).save(OUT + 'royale/back.jpg', quality=82, optimize=True)


def board_glb(m, mats, Y):
    felt = {k: v for k, v in MATS['leatherg'].items() if k in ('tex', 'nrm')}
    mats['feltA'] = dict(felt, color=(0.30, 0.55, 0.33, 1), rough=0.85, emis=(0.02, 0.05, 0.025))
    mats['feltB'] = dict(felt, color=(0.21, 0.42, 0.25, 1), rough=0.85, emis=(0.015, 0.04, 0.02))
    W = 2 * (B + FRAME)
    bevel_box(m, 'dark', W, DH, W, 0.03, m=T(0, Y + DH / 2, 0), uvs=4.0)                      # the dais / frame
    for sx in (-1, 1):                                                                          # gilt edge all round
        bevel_box(m, 'gold', 0.12, 0.05, W, 0.01, m=T(sx * (W / 2 - 0.06), Y + DH + 0.02, 0))
        bevel_box(m, 'gold', W, 0.05, 0.12, 0.01, m=T(0, Y + DH + 0.02, sx * (W / 2 - 0.06)))
    for r in range(N):
        for c in range(N):
            x, z = -B + TS * (c + 0.5), -B + TS * (r + 0.5)
            box(m, 'feltA' if (r + c) % 2 == 0 else 'feltB', TS - 0.1, 0.02, TS - 0.1, m=T(x, Y + DH + 0.01, z), uvs=1.0)
    for k in range(N + 1):                                                                      # gold inlay lines between the squares
        v = -B + TS * k
        box(m, 'gold', 0.07, 0.025, 2 * B + 0.07, m=T(v, Y + DH + 0.012, 0))
        box(m, 'gold', 2 * B + 0.07, 0.025, 0.07, m=T(0, Y + DH + 0.012, v))
    for sx in (-1, 1):                                                                          # gilt diamonds in the frame corners
        for sz in (-1, 1):
            box(m, 'gold', 0.7, 0.03, 0.7, m=M(T(sx * (B + FRAME / 2), Y + DH + 0.015, sz * (B + FRAME / 2)), Ry(45)))
    # ramps on every side so nobody trips (the dais is only 12 cm)
    for a in (0, 90, 180, 270):
        bevel_box(m, 'dark', 2 * B, 0.06, 0.8, 0.02, m=M(Ry(a), T(0, Y + 0.03, B + FRAME + 0.4)), uvs=3.0)


def team_mat(rgb, glow=0.25):
    return dict(color=rgb + (1,), emis=tuple(v * glow for v in rgb), rough=0.8)


def pens_glb(m, mats, Y):
    for ti, (_, _, _, rgb) in enumerate(TEAMS):
        mats['team%d' % ti] = team_mat(rgb, 0.12)          # (v39) less glow: the flags read as cloth, not washed out
    for ti, (px, pz, ry) in enumerate(PENS):
        W_ = M(T(px, 0, pz), Ry(ry))
        L_ = lambda x, y, z: M(W_, T(x, y, z))
        # posts + rope on the three outer sides (the side facing the board is open)
        pts = [(-PEN_W / 2, PEN_D / 2), (-PEN_W / 2, -PEN_D / 2), (PEN_W / 2, -PEN_D / 2), (PEN_W / 2, PEN_D / 2)]
        for (x, z) in pts + [(-PEN_W / 2, 0), (PEN_W / 2, 0), (-PEN_W / 6, -PEN_D / 2), (PEN_W / 6, -PEN_D / 2)]:
            bevel_box(m, 'dark', 0.22, 1.15, 0.22, 0.02, m=L_(x, Y + 0.575, z), uvs=1.0)
            sphere(m, 'gold', 0.13, 8, 6, m=L_(x, Y + 1.2, z))
        for (a, b) in zip(pts[:-1], pts[1:]):
            for hy in (0.6, 1.0):
                P = [L_(a[0] + (b[0] - a[0]) * u, Y + hy - 0.08 * math.sin(math.pi * u), a[1] + (b[1] - a[1]) * u)[:3, 3] for u in np.linspace(0, 1, 9)]
                tube(m, 'rope', P, 0.035, 5)
        # a tall flag pole at the back with a team-colour banner, and the hanging name board between two posts
        bevel_box(m, 'dark', 0.25, 6.6, 0.25, 0.02, m=L_(-PEN_W / 2 + 0.6, Y + 3.3, -PEN_D / 2 - 0.2), uvs=1.5)
        sphere(m, 'gold', 0.2, 10, 8, m=L_(-PEN_W / 2 + 0.6, Y + 6.7, -PEN_D / 2 - 0.2))
        P = np.array([[0, 0, 0], [2.2, 0, 0], [2.2, -2.6, 0], [1.1, -3.3, 0], [0, -2.6, 0]], float)
        for nz in (1, -1):
            I = [0, 4, 1, 1, 4, 2, 2, 4, 3] if nz == 1 else [0, 1, 4, 1, 2, 4, 2, 3, 4]
            Pw = [(L_(-PEN_W / 2 + 0.75 + p[0], Y + 6.3 + p[1], -PEN_D / 2 - 0.2 + nz * 0.01))[:3, 3] for p in P]
            m.add('team%d' % ti, Pw, [list((M(Ry(ry)) @ np.array([0, 0, nz, 0]))[:3])] * 5, [[0, 0]] * 5, I)
        for sx in (-1, 1):                                                       # the name board's two posts
            bevel_box(m, 'dark', 0.24, 4.9, 0.24, 0.02, m=L_(sx * 3.4, Y + 2.45, -PEN_D / 2 - 0.2), uvs=1.5)
        bevel_box(m, 'dark', 7.2, 1.9, 0.16, 0.03, m=L_(0, Y + 3.95, -PEN_D / 2 - 0.25), uvs=2.0)
        bevel_box(m, 'team%d' % ti, 7.3, 0.12, 0.2, 0.01, m=L_(0, Y + 4.95, -PEN_D / 2 - 0.25))
        bevel_box(m, 'team%d' % ti, 7.3, 0.12, 0.2, 0.01, m=L_(0, Y + 2.95, -PEN_D / 2 - 0.25))


SC_W, SC_H, SC_B = 6.8, 2.9, 0.95                       # corner score signs: face width, face height, height of the bottom edge
CORNER = 24.0                                            # they stand at the four corners of the board, facing it


def corner_frames():
    """[x, z, ry] of the four corner score signs; ry turns the face towards the middle of the board"""
    return [[sx * CORNER, sz * CORNER, round(math.degrees(math.atan2(-sx, -sz)), 1)] for sx in (-1, 1) for sz in (-1, 1)]


def score_glb(m, mats, Y):
    """(v36, owner: no jumbotron - "we just need to clearly see who's winning from signs around the board") a sturdy double-sided timber
    sign at each corner: the scores face the board, the rules face outwards"""
    for ti, (_, _, _, rgb) in enumerate(TEAMS): mats['team%d' % ti] = team_mat(rgb, 0.45)
    mats['face'] = dict(color=(0.05, 0.035, 0.025, 1), rough=0.9)
    for (x, z, ry) in corner_frames():
        W_ = M(T(x, Y, z), Ry(ry)); L_ = lambda a, b, c: M(W_, T(a, b, c))
        for px in (-SC_W / 2 - 0.15, SC_W / 2 + 0.15):                       # two big posts with gilt caps
            bevel_box(m, 'dark', 0.3, SC_B + SC_H + 0.5, 0.3, 0.03, m=L_(px, (SC_B + SC_H + 0.5) / 2, 0), uvs=1.5)
            sphere(m, 'gold', 0.17, 10, 8, m=L_(px, SC_B + SC_H + 0.6, 0))
        bevel_box(m, 'dark', SC_W + 0.3, SC_H + 0.3, 0.22, 0.03, m=L_(0, SC_B + SC_H / 2, 0), uvs=2.0)
        bevel_box(m, 'face', SC_W, SC_H, 0.05, 0.01, m=L_(0, SC_B + SC_H / 2, 0.11), uvs=2.0)
        for yy in (SC_B + 0.04, SC_B + SC_H - 0.04):
            bevel_box(m, 'gold', SC_W + 0.35, 0.06, 0.28, 0.01, m=L_(0, yy, 0))
        for k in range(4):                                                    # a colour strip over each team's column
            bevel_box(m, 'team%d' % k, 1.35, 0.07, 0.04, 0.01, m=L_(-2.4 + 1.6 * k, SC_B + 2.02, 0.15))
        bevel_box(m, 'dark', SC_W + 0.9, 0.16, 0.6, 0.03, m=L_(0, SC_B + SC_H + 0.3, 0), uvs=2.0)   # a little roof


HB_Y, HB_OUT, HB_TILT = 5.45, 0.6, 27.0                # hand boards: centre height, how far outside the board edge, tilt down


def hand_frames():
    """[x, y, z, ry, tilt] of the 4 hand boards: over each edge of the board, facing the middle"""
    out = []
    for ry in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(ry); d = B + FRAME + HB_OUT
        out.append([round(-d * math.sin(a), 3), HB_Y, round(-d * math.cos(a), 3), ry, HB_TILT])
    return out


def hands_glb(m, mats, Y):
    mats['face'] = dict(color=(0.07, 0.05, 0.035, 1), rough=0.9)
    for (x, y, z, ry, tilt) in hand_frames():
        W_ = M(T(x, Y + y, z), Ry(ry), Rx(tilt))          # tilted so the face looks down at the players
        bevel_box(m, 'dark', 11.4, 3.5, 0.14, 0.03, m=M(W_, T(0, 0, -0.1)), uvs=2.5)
        bevel_box(m, 'face', 10.9, 3.0, 0.05, 0.01, m=M(W_, T(0, -0.05, -0.02)), uvs=2.0)
        for yy in (1.72, -1.72):
            bevel_box(m, 'gold', 11.5, 0.07, 0.18, 0.01, m=M(W_, T(0, yy, -0.05)))
        for sx in (-1, 1):                                                       # chains up to the ceiling
            top = M(W_, T(sx * 5.2, 1.75, -0.1))[:3, 3]
            tube(m, 'iron', [tuple(top), (top[0], Y + 7.95, top[2])], 0.03, 5)


# ---------------------------------------------------------------- (v39) FLOOR 3 DRESSED TO THE LOUNGE'S STANDARD (owner: "every floor
# still maintains the same standard as the first floor in terms of looks and beauty"). The same pieces as the lounge, laid out round the
# arena: string lights under the whole ceiling, iron lanterns + lantern rings (over the pens, the seating and the board), warm light pools
# on the floor, glossy puddles, green Mudwater banners, framed Mudwater cards on the plain wall panels, giant Meshy swamp trees, and
# spectator lounges (Chesterfield sofa groups with a fanned Mudwater hand on the coffee table, card tables dealt with real Mudwater cards).
TEX = '/home/claude/spire/tex/'
TREES3 = [(-40.0, 24.0), (40.0, 24.0), (-40.0, -24.0), (40.0, -24.0), (-14.0, 37.5), (14.0, 37.5), (-14.0, -37.5), (14.0, -37.5)]
SOFAS3 = [(-44.0, 31.5), (44.0, 31.5), (-30.0, -37.0), (30.0, -37.0)]
CARDS3 = [(-44.0, -17.0), (44.0, -17.0), (-44.0, 17.0), (44.0, 17.0)]
RINGS3 = [[0.0, -29.0, 0.9], [0.0, 29.0, 0.9], [-33.0, 0.0, 0.9], [33.0, 0.0, 0.9], [-9.0, -9.0, 0.8], [9.0, -9.0, 0.8], [-9.0, 9.0, 0.8], [9.0, 9.0, 0.8],
          [-44.0, 31.5, 0.8], [44.0, 31.5, 0.8], [-30.0, -37.0, 0.8], [30.0, -37.0, 0.8], [-44.0, -17.0, 0.7], [44.0, -17.0, 0.7], [-44.0, 17.0, 0.7], [44.0, 17.0, 0.7]]
def decor(D, L, FL):
    import random
    Y = FL['cards']; CEIL = FL['rooms']; X1, Z1 = L['X1'], L['Z1']; rng = random.Random(3132)
    m = Mesh(); mats = dict(MATS)
    for n_, r_ in (('dec_puddle1', 0.12), ('dec_puddle2', 0.12), ('dec_puddle3', 0.14)):
        mats[n_] = dict(tex=TEX + n_ + '.png', emis_tex=TEX + n_ + '.png', emis=(0.2, 0.15, 0.1), alpha='BLEND', rough=r_, metal=0.0)
    mats['pool'] = dict(tex=TEX + 'pool.png', emis_tex=TEX + 'pool.png', emis=(1.0, 0.62, 0.26), alpha='BLEND', rough=0.2)
    mats['banner'] = dict(tex=TEX + 'banner_mw.jpg', rough=0.9, double=True)
    from glb import quad, lathe
    sd = D.setdefault('sdeco', [])
    def busy(x, z, pad=0.0):                                   # the arena, the pens, the corner signs, the lift lobbies and the stair doors
        if abs(x) < B + FRAME + 1.5 + pad and abs(z) < B + FRAME + 1.5 + pad: return True
        if any(math.hypot(x - px, z - pz) < 7.5 + pad for (px, pz, _) in PENS): return True
        if any(math.hypot(x - sx * CORNER, z - sz * CORNER) < 4.5 + pad for sx in (-1, 1) for sz in (-1, 1)): return True
        if abs(x) > X1 - 13 and z < -Z1 + 17: return True                      # lift lobbies
        if abs(x) > X1 - 16 and abs(z) < 10.5: return True                     # stair doors
        return False
    # string lights criss-crossing under the whole ceiling
    yc = CEIL - 0.62
    ends = [((x, -Z1 + 3), (-x * 0.6, Z1 - 3)) for x in np.linspace(-X1 + 8, X1 - 8, 11)] + [((-X1 + 8, z), (X1 - 8, -z * 0.5)) for z in np.linspace(-Z1 + 6, Z1 - 6, 7)]
    for (a, b) in ends:
        a = np.array(a); b = np.array(b); ln = np.linalg.norm(b - a); n = int(ln / 6)
        for s_ in range(n):
            p0 = a + (b - a) * s_ / n; p1 = a + (b - a) * (s_ + 1) / n
            pts = [(p0[0] + (p1[0] - p0[0]) * u, yc - 0.7 * math.sin(math.pi * u), p0[1] + (p1[1] - p0[1]) * u) for u in np.linspace(0, 1, 8)]
            tube(m, 'dark', pts, 0.012, 3)
            for q in pts[1:-1]: sphere(m, 'glow', 0.07, 5, 3, m=T(q[0], q[1] - 0.08, q[2]))
    # green Mudwater banners on iron rods round the arena
    for (x, z, ry) in [(-15, -31, 0), (15, -31, 0), (-15, 31, 180), (15, 31, 180), (-35, -14, 90), (-35, 14, 90), (35, -14, -90), (35, 14, -90),
                       (-52, 31, 90), (52, 31, -90), (-50, -16, 90), (50, -16, -90)]:
        mm = M(T(x, CEIL - 0.7, z), Ry(ry)); w, h = 1.6, 4.0
        P = np.array([[-w / 2, 0, 0], [w / 2, 0, 0], [w / 2, -h, 0], [0, -h - 0.6, 0], [-w / 2, -h, 0]])
        U = [[0, 0], [1, 0], [1, h / (h + 0.6)], [0.5, 1], [0, h / (h + 0.6)]]
        for side, nz in ((0, 1), (1, -1)):
            I = [0, 4, 1, 1, 4, 2, 2, 4, 3] if side == 0 else [0, 1, 4, 1, 2, 4, 2, 3, 4]
            Pw = [(mm @ np.array([p[0], p[1], p[2] + nz * 0.01, 1.0]))[:3] for p in P]
            m.add('banner', Pw, [list((mm @ np.array([0, 0, nz, 0.0]))[:3])] * 5, U, I)
        tube(m, 'iron', [tuple((mm @ np.array([-(w + 0.4) / 2, 0.05, 0, 1.0]))[:3]), tuple((mm @ np.array([(w + 0.4) / 2, 0.05, 0, 1.0]))[:3])], 0.04, 8)
        tube(m, 'iron', [(x, CEIL - 0.65, z), (x, CEIL - 0.45, z)], 0.012, 3)
    # framed Mudwater cards on the plain wall panels (never over a window - owner), plus the stair-tower walls facing the room
    wins = [(w[0], w[2], w[3]) for w in L.get('ext_windows', []) if Y < w[1] < CEIL]
    def clear(sd_, x, z):
        if sd_ in ('front', 'back'): return all(abs(x - wx) > 2.8 for (wx, wz, f) in wins if abs(wz - z) < 1.0)
        return all(abs(z - wz) > 2.8 for (wx, wz, f) in wins if abs(abs(wx) - abs(x)) < 1.0)
    art = []; cards = iter([62, 100, 5, 14, 26, 27, 28, 31, 32, 35, 37, 39, 42, 43, 44, 47, 48, 50, 51, 53, 54, 55, 56, 58, 60, 63, 64, 65, 66, 68, 70, 71, 72, 74, 75, 77])
    def frame(x, z, ry, n):
        w, h = 1.6, 2.22; mm = M(T(x, Y + 3.1, z), Ry(ry))
        bevel_box(m, 'gold', w + 0.28, h + 0.28, 0.06, 0.02, m=mm)
        box(m, 'brass', 0.5, 0.04, 0.16, m=M(mm, T(0, h / 2 + 0.32, 0.05))); sphere(m, 'glow', 0.06, 8, 6, m=M(mm, T(0, h / 2 + 0.38, 0.12)))
        p = mm @ np.array([0, 0, 0.065, 1.0]); art.append([n, round(float(p[0]), 3), round(float(p[1]), 3), round(float(p[2]), 3), ry, w, h])
    for (sd_, x, z, kind) in L.get('lounge_bays', []):
        if kind not in ('', 'brace'): continue
        if sd_ == 'front' and abs(x) > 6 and clear('front', x, z): frame(x, Z1 - 0.12, 180, next(cards))
        if sd_ in ('west', 'east') and abs(z) > 11.0 and z > -27.0 and clear(sd_, (-X1 if sd_ == 'west' else X1), z):
            frame(-X1 + 0.12 if sd_ == 'west' else X1 - 0.12, z, 90 if sd_ == 'west' else -90, next(cards))
    for zz in (-3.0, 3.0):
        frame(-L['sw']['xi'] + 0.25, zz + (7.0 if zz > 0 else -7.0), 90, next(cards)); frame(L['sw']['xi'] - 0.25, zz + (7.0 if zz > 0 else -7.0), -90, next(cards))
    # giant Meshy swamp trees (the lounge's trunks; colliders so nobody walks through them)
    for i, (x, z) in enumerate(TREES3):
        sd.append(['sp_mtree_%d' % (1 + i % 2), x, round(Y + (0.946 if i % 2 == 0 else 0.951) * 4.0 - 0.08 + 0.25, 3), z, (i * 67 + 20) % 360, 4.0])
        D.setdefault('pads', []).append([x, Y + 3.5, z, 2.6, 7.0, 2.6, 0])
    # spectator lounges: Chesterfields round a coffee table with a fanned Mudwater hand; card tables dealt with real Mudwater cards
    dy = Y - 3.0
    for (cx, cz) in SOFAS3:
        sd += [['sp_m_sofa', cx, 3.52 + dy, cz - 2.3, 0.0, 1.47], ['sp_m_sofa', cx, 3.52 + dy, cz + 2.3, 180.0, 1.47],
               ['sp_m_sofa', cx - 2.9, 3.41 + dy, cz, 90.0, 1.16], ['sp_m_sofa', cx + 2.9, 3.41 + dy, cz, -90.0, 1.16],
               ['sp_m_coffeetable', cx, 3.71 + dy, cz, 0.0, 1.16], ['sp_mw_fan_%d' % (int(cx > 0)), cx - 0.035, 3.897 + dy, cz + 0.092, 0.0, 1.0],
               ['sp_m_barrel', cx + 4.4, 3.43 + dy, cz - 3.0, 0.0, 0.47]]
        D['pads'] += [[cx, Y + 0.45, cz, 5.4, 0.9, 6.0, 0]]
    for k, (cx, cz) in enumerate(CARDS3):
        sd += [['sp_m_cardtable', cx, 3.86 + dy, cz, 162.9, 1.21], ['sp_mw_deal_%d' % (k % 4), cx, 4.692 + dy, cz, (k * 90) % 360, 1.0]]
        for (ox, oz, ary) in ((1.17, 1.17, -135.0), (1.17, -1.17, -45.0), (-1.17, -1.17, 45.0), (-1.17, 1.17, 135.0)):
            sd.append(['sp_m_armchair', cx + ox, 3.6 + dy, cz + oz, ary, 0.63])
    # iron lanterns hanging from the ceiling, and the warm pools of light they (and the rings) throw on the floor
    lan = []
    for _ in range(4000):
        if len(lan) >= 60: break
        x, z = rng.uniform(-X1 + 6, X1 - 6), rng.uniform(-Z1 + 4, Z1 - 4)
        if abs(abs(x) - (B + FRAME + 0.6)) < 2.2 and abs(z) < B + 6 or abs(abs(z) - (B + FRAME + 0.6)) < 2.2 and abs(x) < B + 6: continue   # the hand boards
        if any(math.hypot(x - tx, z - tz) < 3.6 for tx, tz in TREES3) or any(math.hypot(x - c[0], z - c[1]) < 3.6 for c in RINGS3): continue
        if all(math.hypot(x - q[1], z - q[3]) > 4.0 for q in lan):
            lan.append(['sp_lantern_' + 'abc'[rng.randint(0, 2)], round(x, 2), CEIL - 0.5, round(z, 2), round(rng.uniform(0, 60), 1), 1.0])
    sd += lan
    def pool(x, z, r, a, rot, y=Y + 0.02):
        quad(m, 'pool', 2 * r, 2 * r, M(T(x, y, z), Ry(rot), Rx(-90)), col=(1, 1, 1, a))
    for f, x, y, z, ry, s_ in lan:
        if busy(x, z): continue
        k = 'abc'.index(f[-1]); pool(x, z, (1.5, 1.8, 2.1)[k], (0.32, 0.42, 0.55)[k], ry * 6)
    for x, z, s_ in RINGS3:
        if abs(x) < B and abs(z) < B: continue
        pool(x, z, 4.3 * s_, 0.55, x * 7 + z, y=Y + 0.16 if any(math.hypot(x - px, z - pz) < 1 for (px, pz, _) in PENS) else Y + 0.02)
    # glossy puddles on the planks round the arena (5 mm apart so they never flicker)
    placed = []
    for k in range(46):
        for _ in range(60):
            x, z = rng.uniform(-X1 + 5, X1 - 5), rng.uniform(-Z1 + 3, Z1 - 3)
            if busy(x, z, 1.0) or any(math.hypot(x - tx, z - tz) < 4.5 for tx, tz in TREES3 + SOFAS3 + CARDS3): continue
            if all(math.hypot(x - px, z - pz) > 3.0 for px, pz in placed): break
        placed.append((x, z)); sz = rng.uniform(2.0, 4.0)
        quad(m, ['dec_puddle1', 'dec_puddle2', 'dec_puddle1', 'dec_puddle3'][k % 4], sz, sz * rng.uniform(0.75, 1.0), M(T(x, Y + 0.008 + 0.005 * (k % 3), z), Ry(rng.uniform(0, 360)), Rx(-90)))
    write(OUTG + 'sp_royale_decor.glb', m, mats)
    D.setdefault('roofModels', []).append(['sp_royale_decor', 0, 0, 0])
    D['chand3'] = RINGS3
    D['royale']['art'] = art
    return art


def apply(D, L, FL):
    Y = FL['cards']
    card_images()
    m = Mesh(); mats = dict(MATS)                                  # ONE model for the whole arena: the wood/gold textures are shared
    board_glb(m, mats, Y); pens_glb(m, mats, Y); score_glb(m, mats, Y); hands_glb(m, mats, Y)
    signs = []                                                      # the rules ride on the back of each corner sign, facing out
    for (x, z, ry) in corner_frames():
        a = math.radians(ry)
        signs.append([round(x - 0.12 * math.sin(a), 3), Y + SC_B + SC_H / 2, round(z - 0.12 * math.cos(a), 3), round(ry + 180, 1)])
    write(OUTG + 'sp_royale.glb', m, mats)
    D.setdefault('roofModels', []).append(['sp_royale', 0, 0, 0])
    pads = D.setdefault('pads', [])
    W = 2 * (B + FRAME)
    pads.append([0.0, Y + DH / 2, 0.0, W, DH, W, 0])                              # stand on the dais (its top is the board)
    cards = json.load(open('/home/claude/spire/cards/cards.json'))
    D['royale'] = dict(
        y=Y, top=round(Y + DH + 0.02, 3), n=N, ts=TS, half=B,
        teams=[[k, spr, hx] for (k, spr, hx, _) in TEAMS],
        pens=[[x, z, ry, PEN_W, PEN_D] for (x, z, ry) in PENS],
        score=[[x, Y + SC_B, z, ry] for (x, z, ry) in corner_frames()],
        hands=hand_frames(),
        cards=[[cards[str(k)]['t'], cards[str(k)]['l'], cards[str(k)]['r'], cards[str(k)]['b']] for k in range(1, 121)],
        secs=180, hand=5, refill=10, signs=signs,
    )
    art = decor(D, L, FL)
    for (n_, *_r) in art:                                                  # plain (no badge) card art for the wall frames
        dst = OUT + 'royale/w_%03d.jpg' % n_
        if not os.path.exists(dst): Image.open(MW + 'mwc_%03d.jpg' % n_).convert('RGB').resize((288, 400), Image.LANCZOS).save(dst, quality=84, optimize=True)
    print('royale decor: %d framed cards, %d trees, %d rings' % (len(art), len(TREES3), len(RINGS3)))
    print('royale: board %dx%d (%.1f m squares), %d pens, scoreboard, %d hand boards, %d cards' % (N, N, TS, len(PENS), len(D['royale']['hands']), 120))
