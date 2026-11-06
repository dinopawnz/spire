"""MUDWATER SPIRE - floor 3: THE SWAMP GAUNTLET (card hall).
sp_f3_room.glb   : static dressing - gaming floor inlays, card-back rugs, the round centre stage with four stairways,
                   the four-faced giant screen hanging over the stage, green card lamps over every table,
                   the TOP STREAKS board on the back wall, two HOW TO PLAY boards, framed cards, sconces.
sp_f3_col.glb    : stage + stairs + tables (invisible, walkable / solid).
sp_gt_table.glb  : one card table (inlaid 3x3 board, two slanted hand racks). Origin = floor centre, seats on -z (GOLD) and +z (TEAL).
sp_gt_sq.glb     : one clickable board square plate.     sp_gt_rim_g / _t : owner frames.   sp_gt_sel.glb : selected-card glow.
sp_gt_hint.glb   : legal-square marker.                  sp_gt_btn.glb : brass push-plate under rack buttons.
out/f3_layout.json : table positions, stage + screen geometry, all the local offsets the MML uses."""
import math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from glb import *
from kit import *

OUT = '/home/claude/spire/out/glb/'
MW = '/home/claude/dinopawnz/mudwater/'
TMP = '/home/claude/spire/out/sprite_png/'
rng = random.Random(33)
LY = json.load(open('/home/claude/spire/out/layout.json'))
Y = LY['f3'] + 0.005
CEIL = LY['f4'] - 0.45
M_ = dict(MATS)
M_['rug'] = dict(tex=MW + 'mwcb_back.jpg', rough=1.0)
M_['felt'] = dict(tex=TEX + 'leather_green.jpg', color=(0.55, 0.8, 0.6, 1), rough=0.95)
M_['shade'] = dict(color=(0.12, 0.45, 0.25, 0.92), emis=(0.05, 0.25, 0.1), alpha='BLEND', rough=0.2, double=True)
M_['bulb'] = dict(color=(1, 0.9, 0.6, 1), emis=(1, 0.85, 0.5), emis_strength=3.0)
M_['gglow'] = dict(color=(1.0, 0.78, 0.25, 1), emis=(1.0, 0.7, 0.15), emis_strength=2.5, unlit=True)
M_['tglow'] = dict(color=(0.2, 1.0, 0.9, 1), emis=(0.15, 1.0, 0.85), emis_strength=2.5, unlit=True)
M_['wglow'] = dict(color=(1.0, 0.95, 0.75, 0.9), emis=(1.0, 0.95, 0.7), emis_strength=2.0, unlit=True, alpha='BLEND')
M_['screen'] = dict(color=(0.02, 0.025, 0.03, 1), rough=0.3, metal=0.2)
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
INTERB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
INTERK = '/usr/share/fonts/opentype/inter/Inter-Black.otf'

R_T = 17.0                      # tables pushed out so the two lift shafts (r 9.3-13.9) stand in the aisle
A3 = LY['A3']
ANG = [11.25 + 22.5 * k for k in range(16)]
# board on the table top: 3 x 3 squares, pitch (x, z); slot 1 = far-left as GOLD sees it
PX, PZ = 0.47, 0.64
CARD_W, CARD_H = 0.40, 0.556
TOP = 0.95
RACK = dict(z=1.27, y=TOP + 0.17, rx=-35, cw=0.17, ch=0.236, px=0.195, rows=(-0.12, 0.15))

def lora(size):
    f = ImageFont.truetype(LORA, size)
    try: f.set_variation_by_name('Bold')
    except Exception: pass
    return f

# ---------------------------------------------------------------------------------------------------- boards (baked text)
def wood_board(W, H, title, body_fn, path):
    """carved dark-wood board with a parchment face; body_fn(draw, img, x0, y0, x1, y1) paints the content"""
    base = Image.open(TEX + 'wood_dark.jpg').convert('RGB').resize((512, 512))
    img = Image.new('RGB', (W, H))
    for x in range(0, W, 512):
        for y in range(0, H, 512): img.paste(base, (x, y))
    d = ImageDraw.Draw(img)
    m = int(W * 0.035)
    d.rounded_rectangle((m, m, W - m, H - m), 30, fill=(236, 220, 180), outline=(150, 108, 40), width=10)
    d.rounded_rectangle((m + 18, m + 18, W - m - 18, H - m - 18), 22, outline=(176, 130, 52), width=4)
    f = lora(int(H * 0.085))
    tw = d.textlength(title, font=f)
    d.text(((W - tw) / 2, m + 34), title, font=f, fill=(24, 96, 84))
    yl = m + 40 + int(H * 0.1)
    d.line((m + 60, yl, W - m - 60, yl), fill=(176, 130, 52), width=4)
    body_fn(d, img, m + 70, yl + 26, W - m - 70, H - m - 40)
    img.save(path, quality=90)
    return path

def leaderboard_tex():
    def body(d, img, x0, y0, x1, y1):
        fh = ImageFont.truetype(INTERK, 46); fr = lora(64)
        d.text((x0 + 10, y0), 'RANK', font=fh, fill=(120, 80, 30))
        d.text((x0 + 260, y0), 'PLAYER', font=fh, fill=(120, 80, 30))
        t = 'STREAK'; d.text((x1 - 10 - d.textlength(t, font=fh), y0), t, font=fh, fill=(120, 80, 30))
        rows = 10; rh = (y1 - y0 - 70) / rows
        for i in range(rows):
            y = y0 + 70 + i * rh
            if i % 2 == 0: d.rectangle((x0, y, x1, y + rh - 6), fill=(226, 206, 160))
            col = [(196, 140, 20), (140, 140, 150), (170, 100, 50)][i] if i < 3 else (90, 60, 30)
            d.text((x0 + 40, y + rh * 0.1), '%d.' % (i + 1), font=fr, fill=col)
    return wood_board(2048, 1408, 'TOP WIN STREAKS', body, TMP + 'f3_leaders.jpg')

RULES = ["Click SIT HERE at any table.",
         "Wait for a challenger, or PLAY THE DEALER.",
         "Pick a card in your rack, then a square.",
         "Level I cards go on empty squares.",
         "Upgrade your own card exactly one level up.",
         "A higher number on the touching edge captures.",
         "One ROCK (a face-down card) at a time.",
         "Board full: most squares wins.",
         "Winners keep the seat. Losers? Sit right back down.",
         "Longest win streaks play THE FINAL on the stage."]

def rules_tex():
    def body(d, img, x0, y0, x1, y1):
        f = ImageFont.truetype(INTERB, 50); rh = (y1 - y0) / len(RULES)
        for i, t in enumerate(RULES):
            y = y0 + i * rh
            d.ellipse((x0, y + 14, x0 + 26, y + 40), fill=(24, 96, 84))
            d.text((x0 + 48, y), t, font=f, fill=(52, 30, 12))
    return wood_board(1536, 1400, 'THE SWAMP GAUNTLET', body, TMP + 'f3_rules.jpg')

# ---------------------------------------------------------------------------------------------------- the card table
def table(m, mm, c=None, big=False):
    w, L = 1.95, 2.95
    bevel_box(m, 'dark', w, 0.09, L, 0.035, m=M(mm, T(0, TOP - 0.045, 0)), uvs=2.0)
    bevel_box(m, 'gold', w + 0.06, 0.03, L + 0.06, 0.012, m=M(mm, T(0, TOP - 0.1, 0)))
    box(m, 'felt', PX * 3 + 0.12, 0.012, PZ * 3 + 0.12, m=M(mm, T(0, TOP + 0.006, 0)), uvs=1.0)
    for k in range(4):                                                        # brass grid lines
        x = (k - 1.5) * PX; box(m, 'brass', 0.018, 0.016, PZ * 3, m=M(mm, T(x, TOP + 0.012, 0)))
        z = (k - 1.5) * PZ; box(m, 'brass', PX * 3, 0.016, 0.018, m=M(mm, T(0, TOP + 0.012, z)))
    for sx in (-1, 1):                                                        # rounded gilt corners + carved apron
        bevel_box(m, 'dark', 0.06, 0.18, L - 0.3, 0.02, m=M(mm, T(sx * (w / 2 - 0.08), TOP - 0.18, 0)))
        for sz in (-1, 1):
            p = np.array([sx * (w / 2 - 0.18), 0, sz * (L / 2 - 0.25)])
            pts = [p + np.array([0.04 * math.sin(t * 3 + sx), t * (TOP - 0.1), 0.04 * math.cos(t * 2 + sz)]) for t in np.linspace(0, 1, 7)]
            tube(m, 'bark', [(mm @ np.append(q, 1))[:3] for q in pts], 0.075, 8, radii=[0.11, 0.085, 0.075, 0.075, 0.08, 0.09, 0.1])
            sphere(m, 'brass', 0.04, 8, 5, m=M(mm, T(sx * (w / 2 - 0.02), TOP - 0.02, sz * (L / 2 - 0.02))))
    for sz in (-1, 1):
        bevel_box(m, 'dark', w - 0.3, 0.18, 0.06, 0.02, m=M(mm, T(0, TOP - 0.18, sz * (L / 2 - 0.08))))
        # slanted hand rack
        rm = M(mm, Ry(0 if sz > 0 else 180), T(0, RACK['y'], RACK['z']), Rx(RACK['rx']))
        bevel_box(m, 'dark', 1.48, 0.6, 0.04, 0.015, m=M(rm, T(0, 0.015, -0.03)))
        for ry_ in RACK['rows']: box(m, 'brass', 1.42, 0.015, 0.04, m=M(rm, T(0, ry_ - RACK['ch'] / 2 - 0.01, 0.0)))
        bevel_box(m, 'gold', 1.52, 0.03, 0.06, 0.01, m=M(rm, T(0, 0.31, -0.03)))
        for sx in (-1, 1): tube(m, 'brass', [(rm @ np.array([sx * 0.66, -0.25, -0.05, 1]))[:3], (mm @ np.array([sx * 0.66, TOP, sz * (RACK['z'] - 0.12), 1]))[:3]], 0.012, 5)
        # chip stacks + a drink at each end, for life
        cx = 0.78
        for j in range(rng.randint(3, 6)): cyl(m, rng.choice(['gold', 'velvet', 'velvett']), 0.03, 0.008, 10, m=M(mm, T(cx, TOP + j * 0.009, sz * 1.05)))
        lathe(m, 'glass', [(0.0, 0), (0.035, 0), (0.04, 0.11), (0.0, 0.11)], 10, m=M(mm, T(-cx, TOP, sz * 1.08)))
    if c is not None:
        collider_box(c, w, TOP, L, M(mm, T(0, TOP / 2, 0)))

def square_plate():
    m = Mesh()
    box(m, 'felt', PX - 0.03, 0.01, PZ - 0.03, m=T(0, 0.005, 0))
    collider_box(m, PX - 0.02, 0.03, PZ - 0.02, T(0, 0.015, 0))
    return m

def rim(mat, w=CARD_W + 0.04, h=CARD_H + 0.04, t=0.022):
    m = Mesh()
    for s in (-1, 1):
        box(m, mat, w + t, 0.012, t, m=T(0, 0.006, s * h / 2))
        box(m, mat, t, 0.012, h, m=T(s * w / 2, 0.006, 0))
    return m

def hint():
    m = Mesh()
    lathe(m, 'wglow', [(0.12, 0), (0.15, 0), (0.15, 0.008), (0.12, 0.008)], 24)
    return m

# ---------------------------------------------------------------------------------------------------- the room
def room():
    R = Mesh(); C = Mesh()
    # gaming floor: glossy ring round the stage, glowing mud channel near the walls, card-back rugs under the tables
    lathe(R, 'bartop', [(6.2, Y + 0.012), (9.0, Y + 0.012)], 64, uvs_u=8)
    lathe(R, 'gold', [(8.95, Y + 0.016), (9.1, Y + 0.016)], 64)
    lathe(R, 'mudglow', [(A3 - 3.8, Y + 0.014), (A3 - 3.45, Y + 0.014)], 72, uvs_u=20)
    for a in ANG:
        mm = M(Ry(a), T(0, Y + 0.02, R_T))
        quad(R, 'rug', 3.3, 3.3 * 711 / 512, M(mm, Rx(-90)))
    # tables (static), lamps over them
    for a in ANG:
        mm = M(Ry(a), T(0, Y, R_T))
        table(R, mm, C)
        top = np.array([0, CEIL, 0, 1]); lamp = mm @ np.array([0, Y + 2.3 - Y, 0, 1])
        tube(R, 'iron', [(mm @ np.array([0, CEIL - Y, 0, 1]))[:3], (mm @ np.array([0, 2.75, 0, 1]))[:3]], 0.015, 5)
        for sz in (-0.55, 0.55):
            q = M(mm, T(0, 2.5, sz))
            tube(R, 'iron', [(mm @ np.array([0, 2.75, 0, 1]))[:3], (q @ np.array([0, 0.18, 0, 1]))[:3]], 0.01, 4)
            lathe(R, 'shade', [(0.05, 0.18), (0.34, 0.0), (0.36, -0.03)], 16, m=q)
            lathe(R, 'brass', [(0.0, 0.2), (0.06, 0.18), (0.05, 0.14), (0.0, 0.14)], 8, m=q)
            sphere(R, 'bulb', 0.06, 8, 5, m=M(q, T(0, 0.05, 0)))
    # the stage: round mud-stone dais with a glossy top, gold inlay, glowing lip, four stairways
    SR, SH = 6.2, 1.1
    lathe(R, 'mud', [(SR + 0.15, Y), (SR, Y + 0.15), (SR, Y + SH - 0.12), (SR + 0.12, Y + SH - 0.06), (SR + 0.12, Y + SH)], 64, uvs_u=12)
    lathe(R, 'bartop', [(SR + 0.12, Y + SH), (0.0, Y + SH)], 64, uvs_u=10)
    lathe(R, 'mudglow', [(SR - 0.1, Y + SH + 0.006), (SR + 0.1, Y + SH + 0.006)], 64, uvs_u=16)
    for r in (2.4, 4.6): lathe(R, 'gold', [(r - 0.05, Y + SH + 0.008), (r + 0.05, Y + SH + 0.008)], 64)
    lathe(C, 'col', [(SR + 0.12, Y), (SR + 0.12, Y + SH), (0.0, Y + SH)], 32)
    steps = 5; rise = SH / steps; tread = 0.38
    for a in (45, 135, 225, 315):                # diagonal, so no stairway points at a lift
        base = M(Ry(a), T(0, Y, SR + steps * tread))
        for i in range(steps):
            bevel_box(R, 'mud', 2.6, rise * (i + 1), tread + 0.02, 0.02, m=M(base, T(0, rise * (i + 1) / 2, -tread * (i + 0.5))), uvs=2.0)
            box(R, 'brass', 2.6, 0.02, 0.04, m=M(base, T(0, rise * (i + 1) + 0.004, -tread * i - 0.02)))
        L = steps * tread; sl = math.hypot(L, SH); ang = math.degrees(math.atan2(SH, L))
        box(C, 'col', 2.6, 0.05, sl, m=M(base, T(0, SH / 2, -L / 2), Rx(-ang)))
        for sx in (-1, 1):
            p0 = base @ np.array([sx * 1.4, 1.0, 0.05, 1]); p1 = base @ np.array([sx * 1.4, 1.0 + SH, -L, 1])
            tube(R, 'brass', [p0[:3], p1[:3]], 0.035, 8)
            for p in (p0, p1): cyl(R, 'dark', 0.06, 1.0, 8, m=T(p[0], p[1] - 1.0, p[2]))
    # brass rail round the stage edge, open at the four stairs
    for q in range(4):
        a0, a1 = q * 90 + 59, q * 90 + 121
        pts = [(SR - 0.25) * np.array([math.sin(math.radians(a)), 0, math.cos(math.radians(a))]) + np.array([0, Y + SH + 0.95, 0]) for a in np.linspace(a0, a1, 12)]
        tube(R, 'brass', pts, 0.035, 8)
        for a in np.linspace(a0, a1, 7):
            p = (SR - 0.25) * np.array([math.sin(math.radians(a)), 0, math.cos(math.radians(a))])
            cyl(R, 'dark', 0.035, 0.95, 6, m=T(p[0], Y + SH, p[2]))
    # the final table on the stage
    table(R, T(0, Y + SH, 0), C)
    # the giant screen: four faces, dark wood frame, brass corners, chains to the ceiling
    S = dict(r=3.85, w=7.5, h=4.7, y0=CEIL - 0.5 - 4.7)
    yc = S['y0'] + S['h'] / 2
    for k in range(4):
        fm = M(Ry(k * 90), T(0, yc, S['r']))
        box(R, 'screen', S['w'] - 0.3, S['h'] - 0.3, 0.06, m=fm)
        bevel_box(R, 'dark', S['w'] + 0.2, 0.25, 0.3, 0.04, m=M(fm, T(0, S['h'] / 2, -0.1)), uvs=3.0)
        bevel_box(R, 'dark', S['w'] + 0.2, 0.25, 0.3, 0.04, m=M(fm, T(0, -S['h'] / 2, -0.1)), uvs=3.0)
        bevel_box(R, 'gold', S['w'] + 0.26, 0.05, 0.34, 0.01, m=M(fm, T(0, -S['h'] / 2 - 0.12, -0.1)))
        for sx in (-1, 1): bevel_box(R, 'dark', 0.25, S['h'] + 0.2, 0.3, 0.04, m=M(fm, T(sx * (S['w'] / 2), 0, -0.1)), uvs=3.0)
    box(R, 'dark', 2 * S['r'] - 0.1, 0.12, 2 * S['r'] - 0.1, m=T(0, S['y0'] + S['h'] + 0.05, 0), uvs=3.0)
    box(R, 'dark', 2 * S['r'] - 0.1, 0.12, 2 * S['r'] - 0.1, m=T(0, S['y0'] - 0.05, 0), uvs=3.0)
    for sx in (-1, 1):
        for sz in (-1, 1):
            p = np.array([sx * (S['r'] + 0.05), S['y0'] + S['h'] + 0.12, sz * (S['r'] + 0.05)])
            sphere(R, 'brass', 0.16, 10, 6, m=T(*p))
            sphere(R, 'brass', 0.16, 10, 6, m=T(p[0], S['y0'] - 0.12, p[2]))
            tube(R, 'iron', [p, np.array([p[0] * 0.6, CEIL + 0.3, p[2] * 0.6])], 0.03, 5)
    # walls: TOP STREAKS board on the back wall, HOW TO PLAY boards on the two front diagonals, framed cards on the back diagonals
    M_['leaders'] = dict(tex=leaderboard_tex(), emis_tex=TMP + 'f3_leaders.jpg', emis=(0.35, 0.33, 0.3), rough=0.8)
    M_['rules'] = dict(tex=rules_tex(), emis_tex=TMP + 'f3_rules.jpg', emis=(0.35, 0.33, 0.3), rough=0.8)
    LB = dict(w=8.4, h=8.4 * 1408 / 2048, z=-(A3 - 0.45), y=Y + 4.2)
    quad(R, 'leaders', LB['w'], LB['h'], M(T(0, LB['y'], LB['z'] + 0.12)))
    bevel_box(R, 'dark', LB['w'] + 0.5, LB['h'] + 0.5, 0.18, 0.05, m=T(0, LB['y'], LB['z']), uvs=3.0)
    bevel_box(R, 'gold', LB['w'] + 0.62, 0.08, 0.24, 0.02, m=T(0, LB['y'] + LB['h'] / 2 + 0.28, LB['z']))
    for a in (45, 315):
        mm = M(Ry(a), T(0, Y + 3.9, A3 - 0.5), Ry(180))
        quad(R, 'rules', 5.4, 5.4 * 1400 / 1536, M(mm, T(0, 0, 0.12)))
        bevel_box(R, 'dark', 5.85, 5.4 * 1400 / 1536 + 0.45, 0.18, 0.05, m=mm, uvs=3.0)
    cards = [11, 9, 19, 62, 100, 8, 21, 22]
    for i, a in enumerate((135, 225)):
        for j, t in enumerate((-2.7, 2.7)):
            n = cards[i * 2 + j]
            M_['c%d' % n] = dict(tex=MW + 'mwc_%03d.jpg' % n, emis_tex=MW + 'mwc_%03d.jpg' % n, emis=(0.28, 0.28, 0.28), rough=0.6)
            mm = M(Ry(a), T(t, Y + 3.6, A3 - 0.45), Ry(180))
            quad(R, 'c%d' % n, 2.0, 2.78, M(mm, T(0, 0, 0.07)))
            bevel_box(R, 'gold', 2.3, 3.08, 0.08, 0.02, m=mm)
            lathe(R, 'brass', [(0.0, 0), (0.1, 0), (0.06, 0.18), (0.0, 0.22)], 8, m=M(mm, T(0, 1.75, 0.15)))
            sphere(R, 'bulb', 0.06, 8, 5, m=M(mm, T(0, 1.98, 0.15)))
    # hanging swamp moss + rope swags along the ceiling beams for atmosphere
    for k in range(24):
        a = k * 15 + 7; r = A3 - 6 + (k % 3) * 1.5
        p = np.array([r * math.sin(math.radians(a)), CEIL + 0.2, r * math.cos(math.radians(a))])
        Lm = 0.8 + (k * 37 % 10) / 10 * 1.2
        tube(R, 'moss', [p, p + np.array([0.05, -Lm * 0.5, 0.03]), p + np.array([0, -Lm, 0.06])], 0.06, 5, radii=[0.12, 0.08, 0.02])
    return R, C, dict(stage_r=SR, stage_h=SH, screen=S, leaders=LB)

if __name__ == '__main__':
    R, C, geo = room()
    print('room', write(OUT + 'sp_f3_room.glb', R, M_))
    print('col', write(OUT + 'sp_f3_col.glb', C, M_))
    t = Mesh(); table(t, T(0, 0, 0)); print('table', write(OUT + 'sp_gt_table.glb', t, M_))
    print('sq', write(OUT + 'sp_gt_sq.glb', square_plate(), M_))
    print('rim_g', write(OUT + 'sp_gt_rim_g.glb', rim('gglow'), M_))
    print('rim_t', write(OUT + 'sp_gt_rim_t.glb', rim('tglow'), M_))
    print('sel', write(OUT + 'sp_gt_sel.glb', rim('wglow', RACK['cw'] + 0.03, RACK['ch'] + 0.03, 0.018), M_))
    print('hint', write(OUT + 'sp_gt_hint.glb', hint(), M_))
    json.dump(dict(y=Y, ceil=CEIL, r=R_T, ang=ANG, px=PX, pz=PZ, cw=CARD_W, ch=CARD_H, top=TOP, rack=RACK, **geo),
              open('/home/claude/spire/out/f3_layout.json', 'w'))
