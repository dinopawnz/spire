"""MUDWATER ESCAPE puzzles (v51, owner: "give them something that stumps them... that takes them a little while to think of the answer
and might make them work together... difficult enough for 20+ people"). Pre-made POOLS of puzzle sets (each with a checked, unique
answer) are drawn as pictures (cheap to show - no text labels); the game picks a different set for every team, every game.

  ROOM 1  CRITTER SUMS   5 critters with secret values 1-9; 8 picture sums hidden in chests - 6 true, 2 FAKE (they don't fit);
                         a painting shows 4 critters in a row: the code is their values in that order (4 digits).
  ROOM 2  SWAMP CIPHER   a message in a secret symbol alphabet (pigpen marks, letters shuffled per set); the key is torn into 6
                         pieces hidden in chests; the message is a question about things you can COUNT in the room -> the answer.
  ROOM 3  WITCH'S EYE    (made live by the game: random digits drawn by floating paint that only lines up from one spot)
  ROOM 4  WARDEN'S RIDDLE 5 Apes on 5 bar stools; hats, drinks and pets; 10-14 clues (some in chests); type each pet's seat (5 digits).
Writes out/esc/*.png and returns the pools for D['escape']."""
import itertools, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = '/home/claude/spire/out/esc/'
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
INTERB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
INTERX = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
CRITTERS = ['gator', 'frog', 'crawdad', 'catfish', 'turtle']
CCOL = {'gator': (64, 140, 60), 'frog': (120, 190, 60), 'crawdad': (200, 60, 40), 'catfish': (60, 120, 190), 'turtle': (150, 110, 60)}
# the countable things built in the cipher room (escape.py places exactly these)
COUNTS = dict(CANDLES=7, FROGS=4, LANTERNS=5, CHESTS=6)


def font(p, s):
    try: return ImageFont.truetype(p, s)
    except Exception: return ImageFont.truetype(INTERB, s)


def parchment(w, h, seed=0):
    r = np.random.default_rng(seed)
    base = np.zeros((h, w, 3), np.float32) + np.array([226, 205, 160], np.float32)
    n = r.normal(0, 1, (h // 8 + 1, w // 8 + 1)); n = np.kron(n, np.ones((8, 8)))[:h, :w]
    base += n[..., None] * 6
    yy, xx = np.mgrid[0:h, 0:w]; d = np.minimum.reduce([xx, yy, w - 1 - xx, h - 1 - yy]) / (0.12 * min(w, h))
    base *= (0.72 + 0.28 * np.clip(d, 0, 1))[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    return im


# ------------------------------------------------------------------ critter icons (drawn: a medallion with a silhouette)
def icon(name, S=220):
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = CCOL[name]
    d.ellipse([4, 4, S - 4, S - 4], fill=(30, 22, 14, 255)); d.ellipse([12, 12, S - 12, S - 12], fill=c + (255,))
    k = (20, 14, 8, 255); w = S / 220.0
    P = lambda pts: [(x * w, y * w) for x, y in pts]
    if name == 'gator':
        d.polygon(P([(30, 120), (95, 92), (190, 104), (196, 116), (100, 120), (190, 128), (186, 140), (95, 146), (30, 132)]), fill=k)
        for x in range(105, 190, 14): d.polygon(P([(x, 120), (x + 6, 112), (x + 12, 120)]), fill=(240, 236, 220, 255))
        d.ellipse(P([(84, 84), (100, 100)]), fill=(240, 220, 90, 255))
    elif name == 'frog':
        d.ellipse(P([(40, 80), (180, 180)]), fill=k)
        for ex in (62, 128):
            d.ellipse(P([(ex, 52), (ex + 34, 92)]), fill=k); d.ellipse(P([(ex + 7, 60), (ex + 27, 84)]), fill=(250, 230, 120, 255))
        d.arc(P([(70, 120), (150, 160)]), 10, 170, fill=(250, 230, 120, 255), width=int(5 * w))
    elif name == 'crawdad':
        d.ellipse(P([(88, 70), (132, 175)]), fill=k)
        for sx in (-1, 1):
            cx = 110 + sx * 52
            d.ellipse(P([(cx - 22, 40), (cx + 22, 92)]), fill=k)
            d.polygon(P([(cx - 4, 48), (cx + sx * 10, 30), (cx + 8 * sx, 58)]), fill=CCOL['crawdad'] + (255,))
            d.line(P([(110 + sx * 14, 96), (cx, 80)]), fill=k, width=int(9 * w))
            for yy in (120, 140, 160): d.line(P([(110 + sx * 18, yy), (110 + sx * 46, yy + 10)]), fill=k, width=int(5 * w))
    elif name == 'catfish':
        d.polygon(P([(30, 110), (70, 76), (150, 84), (178, 110), (150, 136), (70, 144)]), fill=k)
        d.polygon(P([(170, 110), (205, 80), (205, 140)]), fill=k)
        for wy, ty in ((100, 70), (120, 150)): d.line(P([(48, wy), (16, ty)]), fill=k, width=int(5 * w))
        d.ellipse(P([(58, 94), (74, 110)]), fill=(240, 236, 220, 255))
    elif name == 'turtle':
        d.chord(P([(40, 60), (180, 180)]), 180, 360, fill=k)
        d.rectangle(P([(40, 118), (180, 132)]), fill=k)
        d.ellipse(P([(170, 96), (206, 126)]), fill=k)
        for (x0, x1) in ((60, 90), (95, 125), (130, 160)): d.rectangle(P([(x0, 84), (x1, 112)]), outline=CCOL['turtle'] + (255,), width=int(4 * w))
        for lx in (60, 150): d.rectangle(P([(lx, 128), (lx + 18, 150)]), fill=k)
    return im


# ------------------------------------------------------------------ ROOM 1: critter sums
def sums_pool(n_sets=12, seed=11):
    os.makedirs(OUT, exist_ok=True)
    ICON = {c: icon(c, 170) for c in CRITTERS}
    rng = random.Random(seed); sets = []
    def render(terms, op, rhs, path, seedn):
        W, H = 980, 300; im = parchment(W, H, seedn).convert('RGBA'); d = ImageDraw.Draw(im); f = font(INTERX, 120)
        x = 40
        for j, t in enumerate(terms):
            im.alpha_composite(ICON[t], (int(x), 65)); x += 178
            if j < len(terms) - 1:
                d.text((x + 8, 150), op, font=f, fill=(50, 30, 12), anchor='lm'); x += 80
        d.text((x + 10, 150), '= ' + str(rhs), font=f, fill=(50, 30, 12), anchor='lm')
        im.convert('RGB').save(path, quality=84)
    while len(sets) < n_sets:
        vals = dict(zip(CRITTERS, rng.sample(range(1, 10), 5)))
        def mk():
            kind = rng.random()
            if kind < 0.3: t = rng.sample(CRITTERS, 2); return (t, 'x', vals[t[0]] * vals[t[1]])
            n = rng.choice([2, 3, 3]); t = [rng.choice(CRITTERS) for _ in range(n)]
            return (t, '+', sum(vals[c] for c in t))
        real = [mk() for _ in range(6)]
        fakes = []
        for _ in range(2):
            t, op, r = mk(); fakes.append((t, op, r + rng.choice([-3, -2, 2, 3, 4])))
        eqs = real + fakes
        # every critter must appear; exactly ONE value assignment satisfies 6+ of the 8 sums (so throwing out the 2 fakes works)
        if not all(any(c in e[0] for e in real) for c in CRITTERS): continue
        good = []
        for perm in itertools.permutations(range(1, 10), 5):
            v = dict(zip(CRITTERS, perm)); ok = 0
            for (t, op, r) in eqs:
                lhs = (v[t[0]] * v[t[1]]) if op == 'x' else sum(v[c] for c in t)
                ok += (lhs == r)
            if ok >= 6: good.append(v)
            if len(good) > 1: break
        if len(good) != 1 or good[0] != vals: continue
        order = rng.sample(CRITTERS, 4)
        k = len(sets); notes = []
        idx = list(range(8)); rng.shuffle(idx)
        for j, e in enumerate([eqs[i] for i in idx]):
            p = 's%02d_%d.jpg' % (k, j); render(e[0], '+' if e[1] == '+' else 'x', e[2], OUT + p, k * 10 + j); notes.append(p)
        # the painting: 4 critters in a row, numbered, on dark green
        W, H = 1000, 420; im = Image.new('RGBA', (W, H), (24, 44, 30, 255)); d = ImageDraw.Draw(im)
        d.rectangle([10, 10, W - 10, H - 10], outline=(214, 168, 66, 255), width=8)
        d.text((W / 2, 50), 'THE CODE', font=font(LORA, 54), fill=(240, 214, 140), anchor='mm')
        for j, c in enumerate(order):
            im.alpha_composite(icon(c, 200), (int(40 + j * 240), 110))
            d.text((140 + j * 240, 360), str(j + 1), font=font(INTERX, 56), fill=(240, 214, 140), anchor='mm')
        pp = 's%02d_p.jpg' % k; im.convert('RGB').save(OUT + pp, quality=86)
        sets.append(dict(notes=notes, paint=pp, code=''.join(str(vals[c]) for c in order), fake=[idx.index(6), idx.index(7)]))
    return sets


# ------------------------------------------------------------------ ROOM 2: swamp cipher (pigpen marks, letters shuffled per set)
QUESTIONS = [("MULTIPLY THE CANDLES BY THE FROGS", lambda c: c['CANDLES'] * c['FROGS']),
             ("ADD THE LANTERNS TO THE CHESTS THEN MULTIPLY BY THE FROGS", lambda c: (c['LANTERNS'] + c['CHESTS']) * c['FROGS']),
             ("MULTIPLY THE CHESTS BY THE CANDLES THEN TAKE AWAY THE LANTERNS", lambda c: c['CHESTS'] * c['CANDLES'] - c['LANTERNS']),
             ("MULTIPLY THE LANTERNS BY THE CANDLES THEN ADD THE FROGS", lambda c: c['LANTERNS'] * c['CANDLES'] + c['FROGS']),
             ("MULTIPLY THE FROGS BY THE LANTERNS BY THE CHESTS", lambda c: c['FROGS'] * c['LANTERNS'] * c['CHESTS']),
             ("ADD THE CANDLES THE FROGS AND THE LANTERNS THEN DOUBLE IT", lambda c: 2 * (c['CANDLES'] + c['FROGS'] + c['LANTERNS'])),
             ("MULTIPLY THE CANDLES BY THEMSELVES", lambda c: c['CANDLES'] * c['CANDLES']),
             ("MULTIPLY THE CHESTS BY THE FROGS THEN ADD THE CANDLES", lambda c: c['CHESTS'] * c['FROGS'] + c['CANDLES'])]


def glyph(d, k, x, y, s, col, wid):
    """pigpen mark number k (0-25) in an s x s box at (x, y)"""
    if k < 18:                                  # grid cells: which sides are drawn depends on the cell; dot for the second grid
        cell = k % 9; r, c = divmod(cell, 3)
        sides = {'t': r > 0, 'b': r < 2, 'l': c > 0, 'r': c < 2}
        if sides['t']: d.line([(x, y), (x + s, y)], fill=col, width=wid)
        if sides['b']: d.line([(x, y + s), (x + s, y + s)], fill=col, width=wid)
        if sides['l']: d.line([(x, y), (x, y + s)], fill=col, width=wid)
        if sides['r']: d.line([(x + s, y), (x + s, y + s)], fill=col, width=wid)
        if k >= 9: d.ellipse([x + s / 2 - wid, y + s / 2 - wid, x + s / 2 + wid, y + s / 2 + wid], fill=col)
    else:                                       # the X marks: a V pointing one of 4 ways, dot for the second set
        q = (k - 18) % 4; cx, cy = x + s / 2, y + s / 2
        tips = [((x, y), (cx, y + s), (x + s, y)), ((x, y + s), (cx, y), (x + s, y + s)), ((x, y), (x + s, cy), (x, y + s)), ((x + s, y), (x, cy), (x + s, y + s))][q]
        d.line(list(tips), fill=col, width=wid, joint='curve')
        if k >= 22: d.ellipse([cx - wid, cy - wid, cx + wid, cy + wid], fill=col)


def cipher_pool(seed=21):
    os.makedirs(OUT, exist_ok=True); rng = random.Random(seed); sets = []
    for k, (q, fn) in enumerate(QUESTIONS):
        ans = fn(COUNTS)
        perm = list(range(26)); rng.shuffle(perm)                  # letter -> mark, different in every set
        mark = {chr(65 + i): perm[i] for i in range(26)}
        # the message board: words in marks, wrapped
        words = q.split(); lines = []; cur = []
        for wd in words:
            if sum(len(x) + 1 for x in cur) + len(wd) > 20 and cur: lines.append(cur); cur = []
            cur.append(wd)
        lines.append(cur)
        S, G = 52, 18; W = 1800; H = 150 + len(lines) * (S + 60)
        im = parchment(W, H, 500 + k); d = ImageDraw.Draw(im)
        d.text((W / 2, 50), 'A MESSAGE FROM THE WARDEN', font=font(LORA, 52), fill=(110, 40, 14), anchor='mm')
        for li, ln in enumerate(lines):
            txt = ' '.join(ln); x = (W - len(txt) * (S + G)) / 2; y = 120 + li * (S + 60)
            for ch in txt:
                if ch != ' ': glyph(d, mark[ch], x, y, S, (40, 22, 8), 6)
                x += S + G
        mp = 'c%02d_m.jpg' % k; im.save(OUT + mp, quality=86); mh = round(H / W, 4)
        # the key, torn in 6 pieces: every letter of the message on one piece
        used = sorted(set(q.replace(' ', ''))); rng.shuffle(used)
        chunks = [used[i::6] for i in range(6)]
        pieces = []
        for j, ch in enumerate(chunks):
            Wp, Hp = 700, 140 + 0 * len(ch); Hp = 160
            im = parchment(Wp, Hp, 900 + k * 10 + j); d = ImageDraw.Draw(im); f = font(INTERX, 64)
            x = 30
            for L in sorted(ch):
                glyph(d, mark[L], x, 45, 64, (40, 22, 8), 7); d.text((x + 82, 77), '= ' + L, font=f, fill=(110, 40, 14), anchor='lm'); x += 230
            pp = 'c%02d_k%d.jpg' % (k, j); im.save(OUT + pp, quality=84); pieces.append(pp)
        sets.append(dict(msg=mp, mh=mh, keys=pieces, code=str(ans), q=q))
    return sets


# ------------------------------------------------------------------ ROOM 4: the warden's riddle (logic grid, unique answer)
PETS = ['GATOR', 'FROG', 'CRAWDAD', 'CATFISH', 'TURTLE']
HATS = ['RED', 'GOLD', 'GREEN', 'BLUE', 'PURPLE']
DRINKS = ['MOONSHINE', 'SWAMP TEA', 'ROOT BEER', 'MUD COFFEE', 'LEMONADE']
CATS = [('pet', PETS), ('hat', HATS), ('drink', DRINKS)]
PERMS = np.array(list(itertools.permutations(range(5))))        # PERMS[p][v] = seat (0-4) of value v


def who(cat, v):
    n = CATS[cat][1][v]
    return {0: 'the ape with the %s' % n.lower(), 1: 'the ape in the %s hat' % n.lower(), 2: 'the %s drinker' % n.lower()}[cat]


def riddle_pool(n_sets=12, seed=31):
    os.makedirs(OUT, exist_ok=True); rng = random.Random(seed); sets = []
    # seat arrays for every combination: S[c] has shape (120,) per value -> broadcast to (120,120,120)
    def seat(cat, v):
        a = PERMS[:, v]
        return a.reshape([-1 if i == cat else 1 for i in range(3)])
    def mask(cl):
        t = cl[0]
        if t == 'at': return seat(cl[1], cl[2]) == cl[3]
        if t == 'same': return seat(cl[1], cl[2]) == seat(cl[3], cl[4])
        if t == 'diff': return seat(cl[1], cl[2]) != seat(cl[3], cl[4])
        if t == 'left': return seat(cl[1], cl[2]) + 1 == seat(cl[3], cl[4])
        if t == 'next': return np.abs(seat(cl[1], cl[2]) - seat(cl[3], cl[4])) == 1
        if t == 'before': return seat(cl[1], cl[2]) < seat(cl[3], cl[4])
        if t == 'notend': return (seat(cl[1], cl[2]) != 0) & (seat(cl[1], cl[2]) != 4)
        if t == 'end': return (seat(cl[1], cl[2]) == 0) | (seat(cl[1], cl[2]) == 4)
    def count(cls):
        m = np.ones((120, 120, 120), bool)
        for cl in cls: m &= np.broadcast_to(mask(cl), m.shape)
        return int(m.sum())
    def text(cl):
        t = cl[0]
        if t == 'at': return '%s sat on stool %d.' % (who(cl[1], cl[2]).capitalize(), cl[3] + 1)
        if t == 'same': return '%s was %s.' % (who(cl[1], cl[2]).capitalize(), who(cl[3], cl[4]).replace('the ape with', 'the one with').replace('the ape in', 'the one in'))
        if t == 'diff': return '%s was NOT %s.' % (who(cl[1], cl[2]).capitalize(), who(cl[3], cl[4]).replace('the ape with', 'the one with').replace('the ape in', 'the one in'))
        if t == 'left': return '%s sat directly LEFT of %s.' % (who(cl[1], cl[2]).capitalize(), who(cl[3], cl[4]))
        if t == 'next': return '%s and %s sat next to each other.' % (who(cl[1], cl[2]).capitalize(), who(cl[3], cl[4]))
        if t == 'before': return '%s sat somewhere to the left of %s.' % (who(cl[1], cl[2]).capitalize(), who(cl[3], cl[4]))
        if t == 'notend': return '%s did not sit at either end.' % who(cl[1], cl[2]).capitalize()
        if t == 'end': return '%s sat at one of the two ends.' % who(cl[1], cl[2]).capitalize()
    while len(sets) < n_sets:
        sol = [rng.sample(range(5), 5) for _ in range(3)]           # sol[cat][v] = seat
        def rand_clue():
            t = rng.choices(['at', 'same', 'diff', 'left', 'next', 'before', 'notend', 'end'], [1, 5, 2, 4, 3, 3, 2, 1])[0]
            c1, c2 = rng.randrange(3), rng.randrange(3); v1, v2 = rng.randrange(5), rng.randrange(5)
            if t in ('at',): return ('at', c1, v1, sol[c1][v1])
            if t in ('notend', 'end'):
                s = sol[c1][v1]
                if (t == 'notend') != (s in (1, 2, 3)): return None
                return (t, c1, v1)
            if c1 == c2: return None
            s1, s2 = sol[c1][v1], sol[c2][v2]
            ok = {'same': s1 == s2, 'diff': s1 != s2, 'left': s1 + 1 == s2, 'next': abs(s1 - s2) == 1, 'before': s1 < s2}[t]
            return (t, c1, v1, c2, v2) if ok else None
        cls = []; tries = 0
        while count(cls) > 1 and tries < 400:
            cl = rand_clue(); tries += 1
            if cl and cl not in cls and count(cls + [cl]) < count(cls): cls.append(cl)
        if count(cls) != 1: continue
        for cl in list(cls):                                        # drop clues that aren't needed (keeps it tight)
            rest = [c for c in cls if c != cl]
            if count(rest) == 1: cls = rest
        if not (9 <= len(cls) <= 14) or sum(1 for c in cls if c[0] == 'at') > 1: continue
        k = len(sets); rng.shuffle(cls); notes = []
        for j, cl in enumerate(cls):
            W, H = 900, 300; im = parchment(W, H, 700 + k * 20 + j); d = ImageDraw.Draw(im); f = font(INTERB, 46)
            words = text(cl).split(); lines = []; cur = ''
            for wd in words:
                nx = (cur + ' ' + wd).strip()
                if f.getlength(nx) > W - 90 and cur: lines.append(cur); cur = wd
                else: cur = nx
            lines.append(cur)
            y0 = H / 2 - len(lines) * 30
            for i, ln in enumerate(lines): d.text((W / 2, y0 + 30 + i * 60), ln, font=f, fill=(46, 26, 10), anchor='mm')
            p = 'w%02d_%d.jpg' % (k, j); im.save(OUT + p, quality=84); notes.append(p)
        code = ''.join(str(sol[0][v] + 1) for v in range(5))      # stool of the gator, frog, crawdad, catfish, turtle
        sets.append(dict(notes=notes, code=code, n=len(cls), clues=[text(c) for c in cls]))
    # the question board (same for every set)
    W, H = 1600, 760; im = parchment(W, H, 77); d = ImageDraw.Draw(im)
    d.text((W / 2, 70), "THE WARDEN'S RIDDLE", font=font(LORA, 76), fill=(110, 40, 14), anchor='mm')
    body = ["Five Apes sat on the five stools at this bar.", "Each wore a different HAT, drank a different DRINK", "and brought a different PET.",
            "The clues are pinned around the room - and hidden in chests.", "WHICH STOOL DID EACH PET SIT ON?",
            "Type the stool numbers in this order:", "GATOR  -  FROG  -  CRAWDAD  -  CATFISH  -  TURTLE",
            "Left and right = as you face the bar (stool 1 is on the left)."]
    for i, ln in enumerate(body):
        d.text((W / 2, 170 + i * 72), ln, font=font(INTERB if i not in (4, 6) else INTERX, 44 if i not in (4, 6) else 50), fill=(46, 26, 10) if i not in (4, 6) else (110, 40, 14), anchor='mm')
    im.save(OUT + 'w_board.jpg', quality=86)
    return sets


def eye_png():
    S = 512; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([20, 150, S - 20, S - 150], fill=(230, 210, 255, 230)); d.ellipse([170, 170, 342, 342], fill=(120, 40, 170, 255))
    d.ellipse([220, 220, 292, 292], fill=(10, 0, 20, 255)); d.ellipse([235, 228, 255, 248], fill=(255, 255, 255, 255))
    for a in range(-60, 61, 20):
        x = S / 2 + 200 * math.sin(math.radians(a)); d.line([(x, 150 - 0 * abs(a)), (x + 10 * math.sin(math.radians(a)), 100)], fill=(230, 210, 255, 230), width=10)
    im.filter(ImageFilter.GaussianBlur(1)).save(OUT + 'eye.png')


EMPTY = ['Nothing in here but swamp mud.', 'A crawdad pinches your finger. No clue here.', 'Just an old boot. Keep looking!',
         'The Warden was here. That is all.', 'Empty. Try another chest.', 'A soggy sandwich. No clue here.']


def empty_notes():
    out = []
    for j, t in enumerate(EMPTY):
        W, H = 900, 300; im = parchment(W, H, 1300 + j); d = ImageDraw.Draw(im)
        d.text((W / 2, H / 2), t, font=font(INTERB, 42), fill=(90, 70, 50), anchor='mm')
        p = 'w_empty%d.jpg' % j; im.save(OUT + p, quality=82); out.append(p)
    return out


def keypad_png():
    """the face of every keypad: 1-9, CLR, 0, OK on dark buttons (keys 140 px apart = 0.42 m)"""
    P = 140; W, H = 3 * P + 26, 4 * P + 26
    im = Image.new('RGB', (W, H), (26, 20, 14)); d = ImageDraw.Draw(im)
    labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'CLR', '0', 'OK']
    for i, L in enumerate(labels):
        c, r = i % 3, i // 3; x0, y0 = 13 + c * P + 8, 13 + r * P + 8
        fill = (120, 30, 22) if L == 'CLR' else (30, 110, 40) if L == 'OK' else (58, 44, 30)
        d.rounded_rectangle([x0, y0, x0 + P - 16, y0 + P - 16], 18, fill=fill, outline=(214, 168, 66), width=5)
        d.text((x0 + (P - 16) / 2, y0 + (P - 16) / 2), L, font=font(INTERX, 72 if len(L) == 1 else 44), fill=(255, 226, 150), anchor='mm')
    im.save(OUT + 'keypad.jpg', quality=88)


def build_all():
    eye_png(); keypad_png()
    return dict(sums=sums_pool(), cipher=cipher_pool(), riddle=riddle_pool(), counts=COUNTS, empty=empty_notes())


if __name__ == '__main__':
    import json, time
    t = time.time(); P = build_all()
    print('sums', len(P['sums']), P['sums'][0]['code'], '| cipher', len(P['cipher']), [c['code'] for c in P['cipher']],
          '| riddle', len(P['riddle']), [r['n'] for r in P['riddle']], '%.0f s' % (time.time() - t))
    print(P['riddle'][0]['clues'], P['riddle'][0]['code'])
