"""(v30, owner: "we literally have mudwater cards to play with") real MUDWATER cards dealt on every card table:
a two-card hand in front of each of the four seats (bottom edge toward the player, fanned a little), a face-down Mudwater
deck in the middle with one card turned up beside it. 4 different deals -> out/glb/sp_mw_deal_0..3.glb (origin = the centre
of the felt, y 0 = the felt surface, seats at 45/135/225/315 degrees like build_lounge.card_tables)."""
import math, random
from PIL import Image
from glb import Mesh, write, quad, box, T, M, Rx, Ry
SRC = '/home/claude/mudwater_repo/'; TMP = '/home/claude/spire/out/cards_small/'; OUT = '/home/claude/spire/out/glb/'
import os; os.makedirs(TMP, exist_ok=True)
CH = 0.30; CW = CH * 720 / 1000                                  # a card 30 cm tall (the tables are big, scaled-up furniture)

def tex(name, h=320):
    p = TMP + 'deal_' + name
    if not os.path.exists(p): Image.open(SRC + name).convert('RGB').resize((int(h * 0.72), h), Image.LANCZOS).save(p, quality=84)
    return p

def deal(k, seed):
    R = random.Random(seed); m = Mesh(); mats = {}
    have = [n for n in range(1, 121) if os.path.exists(SRC + 'mwc_%03d.jpg' % n)]
    picks = R.sample(have, 9)
    mats['back'] = dict(tex=tex('mwc_back.jpg'), rough=0.55, emis=(0.08, 0.08, 0.08), emis_tex=tex('mwc_back.jpg'))
    mats['edge'] = dict(color=(0.86, 0.82, 0.74, 1), rough=0.8)
    y = 0.004; n = 0
    def face(i, x, z, ry, lift):
        name = 'c%d' % i; f = tex('mwc_%03d.jpg' % picks[i])
        mats[name] = dict(tex=f, emis_tex=f, emis=(0.14, 0.14, 0.14), rough=0.5)
        quad(m, name, CW, CH, M(T(x, y + lift, z), Ry(ry), Rx(-90)))
    for s in range(4):                                           # a hand in front of each seat
        a = 45 + 90 * s; r = 0.62
        for j in range(2):
            fan = (-9 if j == 0 else 9) + R.uniform(-3, 3); off = (-0.07 if j == 0 else 0.07)
            x = r * math.sin(math.radians(a)) + off * math.cos(math.radians(a)); z = r * math.cos(math.radians(a)) - off * math.sin(math.radians(a))
            face(n, x, z, a + fan, 0.001 * j); n += 1
    # the deck: a squared-up stack of Mudwater card backs, and the top card turned over beside it
    dk = R.uniform(0, 360)
    box(m, 'edge', CW, 0.03, CH, m=M(T(-0.12, y + 0.015, 0.02), Ry(dk)))
    quad(m, 'back', CW, CH, M(T(-0.12, y + 0.031, 0.02), Ry(dk), Rx(-90)))
    face(8, 0.16, -0.04, R.uniform(0, 360), 0.0)
    write(OUT + 'sp_mw_deal_%d.glb' % k, m, mats)

def fan(k, seed, ch=0.27):
    """a hand of Mudwater cards fanned out on a coffee table (face up), and the deck beside it"""
    R = random.Random(seed); m = Mesh(); mats = {}; cw = ch * 0.72
    have = [n for n in range(1, 121) if os.path.exists(SRC + 'mwc_%03d.jpg' % n)]
    picks = R.sample(have, 5)
    for i, c in enumerate(picks):
        f = tex('mwc_%03d.jpg' % c); mats['c%d' % i] = dict(tex=f, emis_tex=f, emis=(0.14, 0.14, 0.14), rough=0.5)
        a = -36 + 18 * i
        quad(m, 'c%d' % i, cw, ch, M(T(0, 0.004 + 0.0012 * i, 0.12), Ry(a), T(0, 0, -ch * 0.5), Rx(-90)))
    mats['back'] = dict(tex=tex('mwc_back.jpg'), emis_tex=tex('mwc_back.jpg'), emis=(0.08, 0.08, 0.08), rough=0.55)
    mats['edge'] = dict(color=(0.86, 0.82, 0.74, 1), rough=0.8)
    box(m, 'edge', cw, 0.025, ch, m=M(T(0.34, 0.0125, 0.05), Ry(R.uniform(-20, 20))))
    quad(m, 'back', cw, ch, M(T(0.34, 0.026, 0.05), Ry(0), Rx(-90)))
    write(OUT + 'sp_mw_fan_%d.glb' % k, m, mats)

if __name__ == '__main__':
    for k in range(4): deal(k, 900 + k)
    for k in range(2): fan(k, 950 + k)
    print('deals written')
