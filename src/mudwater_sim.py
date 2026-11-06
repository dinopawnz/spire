"""Mudwater rules engine + random-game simulator (counts how many legal moves a player really has each turn)."""
import json, random, math
C = {int(k): v for k, v in json.load(open('/home/claude/spire/cards/cards.json')).items()}
BYLV = {l: [n for n in C if C[n]['lv'] == l] for l in range(1, 6)}
NB = {i: [(j, side) for j, side in ((i - 3, 't'), (i + 3, 'b'), (i - 1 if i % 3 else -1, 'l'), (i + 1 if i % 3 != 2 else -1, 'r')) if 0 <= j < 9] for i in range(9)}
OPP = {'t': 'b', 'b': 't', 'l': 'r', 'r': 'l'}
def hand(rng):
    h = rng.sample(BYLV[1], 5) + rng.sample(BYLV[2], 3) + rng.sample(BYLV[3], 2) + rng.sample(BYLV[4], 2) + rng.sample(BYLV[5], 1)
    rest = [n for n in C if n not in h]; h.append(rng.choice(rest)); rng.shuffle(h); h.pop()      # 14 cards, one drawn as the ante
    return h
def moves(s, p):
    """legal moves for player p: (kind, card, square)"""
    out = []; hd = s['hand'][p]; empty = [i for i in range(9) if s['top'][i] is None]
    for c in hd:
        lvc = C[c]['lv']
        if lvc == 1: out += [('place', c, i) for i in empty]
        if not s['rock'][p]: out += [('rock', c, i) for i in empty]
        for i in range(9):
            t = s['top'][i]
            if t is not None and s['own'][i] == p and (1 if s['face'][i] == 'down' else C[t]['lv']) == lvc - 1: out.append(('up', c, i))
    return out
def play(s, p, m):
    kind, c, i = m; s['hand'][p].remove(c)
    if kind == 'rock':
        s['top'][i] = c; s['own'][i] = p; s['face'][i] = 'down'; s['rock'][p] = i; return
    if kind == 'up' and s['rock'][p] == i: s['rock'][p] = None
    s['top'][i] = c; s['own'][i] = p; s['face'][i] = 'up'
    for j, side in NB[i]:
        if s['top'][j] is not None and s['own'][j] != p and s['face'][j] == 'up' and C[c][side] > C[s['top'][j]][OPP[side]]: s['own'][j] = p
def new_game(rng): return {'top': [None] * 9, 'own': [None] * 9, 'face': [None] * 9, 'rock': [None, None], 'hand': [hand(rng), hand(rng)]}
if __name__ == '__main__':
    rng = random.Random(1); B = []; plies = []; logs = []
    for g in range(3000):
        s = new_game(rng); p = 0; passes = 0; n = 0; lg = 0
        while sum(t is not None for t in s['top']) < 9 and passes < 2:
            ms = moves(s, p)
            if not ms: passes += 1
            else: passes = 0; B.append(len(ms)); lg += math.log10(len(ms)); play(s, p, rng.choice(ms)); n += 1
            p = 1 - p
        plies.append(n); logs.append(lg)
    B.sort()
    print('legal moves per turn: average %.0f, middle %d, most %d' % (sum(B) / len(B), B[len(B) // 2], B[-1]))
    print('turns per game: average %.1f' % (sum(plies) / len(plies)))
    print('possible games (hands known, one deal): about 10^%.0f' % (sum(logs) / len(logs)))
