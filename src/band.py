"""THE LOUNGE STAGE BAND: Meshy drum kit, harp, guitar on a stand, upright piano and a vintage microphone on the lounge stage.
Called by build_html.py: band.apply(D, F1). Writes D['bandHits'] = clickable zones [x, y, z, w, h, d, ry, instrument, key]
(piano: 8 slices low->high left to right; harp: 8 bands low->high bottom to top; drums: a 3x2 grid; guitar: one zone that
strums the next chord) and solid pads. The sounds are out/snd/band_*.mp3 (band_sounds.py); playing + the host's
INSTRUMENTS ON/OFF switch live in spire_src.html."""
import math
from outside import place
import outside

def apply(D, F1):
    sx_, sy_, sz_ = F1['stage']                       # stage centre top (build_lounge.stage: x -7.3..7.3, depth 11.4, front at z1)
    y = sy_; zf = sz_ + 5.7; zb = sz_ - 5.7
    add = D['sdeco'].append; pads = D.setdefault('pads', []); hits = D['bandHits'] = []
    def put(name, x, z, ry, size, axis):
        if name not in outside.META: return None
        e = place(name, x, y, z, ry, size, axis); add(e)
        mn, mx = outside.META[name]; s = e[5]
        return (mx[0] - mn[0]) * s, (mx[1] - mn[1]) * s, (mx[2] - mn[2]) * s
    def zones(x, z, ry, W, H, Dd, inst, keys, along='x', pad=True):
        if pad: pads.append([x, y + H * 0.45, z, W * 0.82, H * 0.9, Dd * 0.82, ry])
        n = len(keys); c, s = math.cos(math.radians(ry)), math.sin(math.radians(ry))
        for i, k in enumerate(keys):
            if along == 'x':                                # slices left -> right across the instrument's width
                u = -W / 2 + W * (i + 0.5) / n; hx, hz = x + u * c, z - u * s
                hits.append([round(hx, 3), round(y + H / 2, 3), round(hz, 3), round(W / n + 0.02, 3), round(H + 0.05, 3), round(Dd + 0.1, 3), ry, inst, k])
            else:                                           # bands bottom -> top
                hits.append([x, round(y + H * (i + 0.5) / n, 3), z, round(W + 0.1, 3), round(H / n + 0.02, 3), round(Dd + 0.1, 3), ry, inst, k])
    # drums at the back, piano left, harp right, guitar front-right, the microphone front and centre
    d = put('drumkit', 0.0, zb + 3.0, 0, 4.0, 'w')
    if d:
        W, H, Dd = d; pads.append([0.0, y + H * 0.4, zb + 3.0, W * 0.8, H * 0.8, Dd * 0.8, 0])
        for row, ks in enumerate((('snare', 'kick', 'tom_lo'), ('hihat', 'tom_hi', 'crash'))):
            for i, k in enumerate(ks):
                hits.append([round(-W / 2 + W * (i + 0.5) / 3, 3), round(y + H * (0.25 + 0.5 * row), 3), round(zb + 3.0, 3), round(W / 3 + 0.02, 3), round(H / 2 + 0.02, 3), round(Dd + 0.1, 3), 0, 'drum', k])
    # the grand piano and the harp from the owner's castle build (Dippy's Lost Crown): every key / string plays its own recorded
    # note (piano_<midi>.mp3, harp_<midi>.mp3). Their key/string layouts (castle_instruments.json) are in each model's own space.
    import json
    CI = json.load(open('/home/claude/spire/castle_instruments.json'))
    def xf(lx, lz, P, a, S):
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        return P[0] + S * (lx * c + lz * s_), P[2] + S * (-lx * s_ + lz * c)
    PS, PA = 1.3, -65.0; PP = (-4.3, y, sz_ - 0.6)                 # piano: keyboard toward the crowd, angled to the middle
    add(['sp_band_piano', PP[0], y, PP[2], PA, PS])
    keys = []
    for (lx, ly, lz, w, d, midi, black) in CI['piano']['keys']:
        wx, wz = xf(lx, lz, PP, PA, PS); keys.append([round(wx, 3), round(y + ly * PS, 3), round(wz, 3), round(w * PS, 3), round(d * PS, 3), midi, black])
    D['bandPiano'] = dict(ry=CI['piano']['ry'] + PA, keys=keys)
    bx, bz = xf(-0.25, 0.0, PP, PA, PS); pads.append([round(bx, 3), y + 0.45, round(bz, 3), 1.3 * PS, 0.9, 1.4 * PS, PA])     # the body only - the keys stay clickable
    HS, HA = 1.35, -20.0; HP = (4.5, y, sz_ - 0.8)                  # harp: strings facing the crowd, turned to the middle
    add(['sp_band_harp', HP[0], y, HP[2], HA, HS])
    strs = []
    for (lx, ly, lz, ln, midi) in CI['harp']['strings']:
        wx, wz = xf(lx, lz, HP, HA, HS); strs.append([round(wx, 3), round(y + ly * HS, 3), round(wz, 3), round(ln * HS, 3), midi])
    D['bandHarp'] = dict(ry=CI['harp']['ry'] + HA, strings=strs)
    pads.append([HP[0], y + 0.12, HP[2], 0.9 * HS, 0.24, 0.5 * HS, HA])                              # the base only - every string stays clickable
    g = put('guitar', 2.6, zf - 2.0, -20, 1.6, 'h')
    if g: zones(2.6, zf - 2.0, -20, g[0], g[1], g[2], 'guitar', [0], 'x')
    m = put('microphone', 0.0, zf - 1.4, 0, 1.75, 'h')
    if m: pads.append([0.0, y + 0.85, zf - 1.4, 0.35, 1.7, 0.35, 0])
    print('band: %d clickable zones' % len(hits))
