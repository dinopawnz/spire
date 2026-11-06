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
    # (v32, owner: "turn the drums around ... facing the audience", "sound different depending on which piece you hit")
    # the kit turned 180 so the bass drum faces the crowd and the drummer sits behind it; one click zone per piece, placed on
    # the piece itself (positions read off a top view of the Meshy model, model units), each with its own real recording.
    DK = 180.0; d = put('drumkit', 0.0, zb + 3.0, DK, 4.0, 'w')
    if d:
        W, H, Dd = d; pads.append([0.0, y + H * 0.17, zb + 3.0, W * 0.55, H * 0.34, Dd * 0.45, 0])
        mn, mx = outside.META['drumkit']; s_ = W / (mx[0] - mn[0]); cxm, czm = (mn[0] + mx[0]) / 2, (mn[2] + mx[2]) / 2
        c, sn = math.cos(math.radians(DK)), math.sin(math.radians(DK))
        PIECES = [('hihat', -0.79, 0.15, -0.11, 0.42), ('crash', -0.48, 0.42, -0.59, 0.5), ('crash', 0.77, 0.36, -0.24, 0.5),
                  ('snare', -0.26, -0.05, 0.08, 0.4), ('tom_hi', -0.11, 0.08, -0.35, 0.36), ('tom_hi', 0.32, 0.08, -0.32, 0.36),
                  ('tom_lo', 0.61, -0.05, 0.06, 0.45), ('kick', 0.13, -0.3, -0.5, 0.55)]
        for (k, lx, ly, lz, sz) in PIECES:
            ox, oz = (lx - cxm) * s_, (lz - czm) * s_
            wx, wz = ox * c + oz * sn, -ox * sn + oz * c
            # (v44, owner: "all the instruments work on stage except for the drums") the click box used to sit INSIDE each drum, so the
            # drum itself caught the click; now it sits on top of the piece and reaches up 0.5 m (click the top of the drum)
            # (v52, owner: "a little hard to click the cymbals and individual drums") bigger click boxes that WRAP each piece (drum head /
            # cymbal in the middle of the box, 0.35 m below it to 0.45 m above it, 95% of the piece's width) so a click anywhere on the
            # piece you can see lands on that piece's own box, not on the kit model
            hits.append([round(wx, 3), round(y + (ly - mn[1]) * s_ + 0.05, 3), round(zb + 3.0 + wz, 3), round(sz * s_ * 0.95, 3), 0.8, round(sz * s_ * 0.95, 3), 0, 'drum', k])
        # ...and the drum kit model itself is clickable too: the click's spot on the model picks the nearest piece
        ek = D['sdeco'].pop(); D['bandDrum'] = dict(e=ek, pieces=[[k, lx, ly, lz] for (k, lx, ly, lz, _) in PIECES])
    # the grand piano and the harp from the owner's castle build (Dippy's Lost Crown): every key / string plays its own recorded
    # note (piano_<midi>.mp3, harp_<midi>.mp3). Their key/string layouts (castle_instruments.json) are in each model's own space.
    import json
    CI = json.load(open('/home/claude/spire/castle_instruments.json'))
    def xf(lx, lz, P, a, S):
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        return P[0] + S * (lx * c + lz * s_), P[2] + S * (-lx * s_ + lz * c)
    PS, PA = 1.3, 115.0; PP = (-4.3, y, sz_ - 0.4)                 # piano: the player stands behind the keyboard facing the crowd (no stool - stand and play)
    add(['sp_band_piano', PP[0], y, PP[2], PA, PS])
    keys = []
    for (lx, ly, lz, w, d, midi, black) in CI['piano']['keys']:
        wx, wz = xf(lx, lz, PP, PA, PS); keys.append([round(wx, 3), round(y + ly * PS, 3), round(wz, 3), round(w * PS, 3), round(d * PS, 3), midi, black])
    D['bandPiano'] = dict(ry=CI['piano']['ry'] + PA, keys=keys)
    bx, bz = xf(-0.25, 0.0, PP, PA, PS); pads.append([round(bx, 3), y + 0.45, round(bz, 3), 1.3 * PS, 0.9, 1.4 * PS, PA])     # the body only - the keys stay clickable
    HS, HA = 1.35, 160.0; HP = (4.5, y, sz_ - 0.8)                  # harp: (v32, owner) turned round to face the audience like the piano
    add(['sp_band_harp', HP[0], y, HP[2], HA, HS])
    strs = []
    for (lx, ly, lz, ln, midi) in CI['harp']['strings']:
        wx, wz = xf(lx, lz, HP, HA, HS); strs.append([round(wx, 3), round(y + ly * HS, 3), round(wz, 3), round(ln * HS, 3), midi])
    D['bandHarp'] = dict(ry=CI['harp']['ry'] + HA, strings=strs)
    pads.append([HP[0], y + 0.12, HP[2], 0.9 * HS, 0.24, 0.5 * HS, HA])                              # the base only - every string stays clickable
    # the guitar (no stand) hangs at hip height, tilted like it's being played: stand behind it and you're the guitarist.
    # (owner) [x, y centre, z, ry, rz tilt, scale] - the model's neck runs up +y; rz -55 swings the neck to the player's left.
    if 'guitarsolo' in outside.META:
        mn, mx = outside.META['guitarsolo']; gs = 1.6 / (mx[1] - mn[1]); GX, GZ = 2.4, zf - 2.2        # (v32, owner) bigger guitar, easier to see and play
        D['bandGuitar'] = [GX, round(y + 1.12, 3), round(GZ, 3), -10.0, -55.0, round(gs, 4)]
        hits.append([GX, round(y + 1.12, 3), round(GZ, 3), 1.5, 1.1, 0.5, -10.0, 'guitar', 0])
    m = put('microphone', 0.0, zf - 1.4, 0, 1.75, 'h')
    if m: pads.append([0.0, y + 0.85, zf - 1.4, 0.35, 1.7, 0.35, 0])
    print('band: %d clickable zones' % len(hits))
