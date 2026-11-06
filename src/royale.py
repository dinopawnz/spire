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
        mats['team%d' % ti] = team_mat(rgb, 0.35)
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
    print('royale: board %dx%d (%.1f m squares), %d pens, scoreboard, %d hand boards, %d cards' % (N, N, TS, len(PENS), len(D['royale']['hands']), 120))
