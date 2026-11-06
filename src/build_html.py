"""bake every position the game needs into spire.html (from the layout JSONs the build scripts write)."""
import json, sys
O = '/home/claude/spire/out/'
VER = sys.argv[1] if len(sys.argv) > 1 else '1'
BASE = sys.argv[2] if len(sys.argv) > 2 else 'https://raw.githubusercontent.com/dinopawnz/spire/main/'
VOICES = 'true' if '--voices' in sys.argv else 'false'
L = json.load(open(O + 'layout.json')); KX_, KZ_ = L['X1'] / 42.5, L['Z1'] / 30.0; LL = json.load(open(O + 'lift_layout.json')); F1 = json.load(open(O + 'f1_layout.json'))
F2 = json.load(open(O + 'f2_layout.json')); NPC = json.load(open(O + 'npc.json')); SP = json.load(open(O + 'sprites.json'))
real_hall = json.load(open(O + 'hall/answer.json'))['real']; real_vault = json.load(open(O + 'vault/answer.json'))['real']
FL = L['FL']; Y1 = FL['lounge'] + 0.005; Y2 = FL['hall']; YG = FL['gallery']
r = lambda v: round(v, 3)
import math
import numpy as np
RXZ = F2['room']; YV = F2['yv']; MO = F2['moat']
D = {
  'FRONT': L['walk']['z1'],
  'L': {'porch': FL['lounge'], 'f2': FL['hall'], 'gallery': FL['gallery'], 'f3': FL['cards'], 'f4': FL['rooms'], 'roof': FL['roof'], 'X1': L['X1'], 'Z1': L['Z1'],
        'walk_y': L['walk']['y1'], 'walk_z0': L['walk']['z0'], 'walk_z1': L['walk']['z1'], 'walk_w': L['walk']['w'], 'porch_box': L['porch_box'],
        },
  'room': RXZ, 'yv': YV,
  'ms': SP['ms'],
  'npc': {k: {'lines': v['lines']} for k, v in NPC.items()},
  'npcH': {'ferryman': 1.6, 'barkeep': 1.6, 'gator': 2.2, 'skipper': 1.85, 'appraiser': 1.8, 'dealer': 1.7, 'operator': 2.0},
  'where': {'ferryman': [2.2, L['walk']['y1'], r(L['walk']['z1'] - 3.5), -15], 'barkeep': [F1['bar'][0], Y1, r(F1['bar'][1] + 3.0), 0], 'gator': [19.5, Y1, r(25.5 + L['Z1'] - 30.0), 120],
            'appraiser': [r(29.0 * L['X1'] / 42.5), Y2, r(15.5 * L['Z1'] / 30.0), 240], 'skipper': [8.0, FL['roof'], 12.0, 200], 'dealer': [0.0, FL['cards'], 0.0, 0]},
  'taps': [[t[0], r(t[1] + 0.07), t[2], t[3]] for t in F1['taps']],
  'barTop': r(Y1 + 1.165), 'trayTop': r(Y1 + 1.195), 'barRound': F1['bar'],
  'books': [[0.0, FL['lounge'], r(L['Z1'] + 7.0), 0]],          # ONE sign-up book, OUTSIDE on the porch in front of the doors (owner, v21)          # ONE sign-up book, in the middle of the main entrance (owner)
  'chand': F1['rings'],
  'chand2': [],
  'lifts': LL['lifts'], 'sheaveY': LL['sheave_y'], 'hitch': LL['hitch'], 'rope': LL['rope'], 'sheaveR': LL['sheave_r'], 'cwZ': LL['cw_z'], 'cabApo': L['cab_apo'], 'doorW': L['door_w'], 'doorH': L['door_h'], 'cabWallH': 3.45, 'cabGateH': 3.35,       # v24: taller cabs (2.6 / 2.5 + 0.85)
  'hall': [[p['x'], p['y'], p['z'], p['ry']] for p in F2['hall']], 'vault': [[p['x'], p['y'], p['z'], p['ry']] for p in F2['vault']],
  'realHall': real_hall, 'realVault': real_vault, 'hallImgs': F2['imgs'],
  'vaultDoor': F2['door'],
  'refs': [[r(-24.0 * KX_), Y2, r(12.0 * KZ_)], [r(24.0 * KX_), Y2, r(-12.0 * KZ_)], [r(-12.0 * KX_), Y2, r(-20.0 * KZ_)], [r(12.0 * KX_), Y2, r(20.0 * KZ_)]], 'refFlag': F2['plinth'],
  'bannerAt': [[0.0, 0.0, r(22.6 * KZ_), 2.2]],
  'signs': {'hall': [r(L['band']['xo'] - 0.4), r(Y2 + 3.0), 1.5, 270], 'vault': [-6.6, r(YV + 2.6), r(RXZ[1] + 0.3), 0]},
  'finalBoards': [[6.6, r(YV + 2.6), r(RXZ[1] + 0.3), 0], [-7.6, r(Y1 + 3.0), r(L['Z1'] - 0.55), 180]],
  'stairs': [[s_ * (L['sw']['xi'] - 0.35), r(FL[k] + 3.6), (L['sw']['zl'] + L['sw']['z0']) / 2, 90 if s_ < 0 else 270] for k in L['keys'] for s_ in (1, -1)],
  'npcCap': {'operator': {'inCab': True, 'y': 2.25}, 'barkeep': {'y': 2.3, 'fwd': 0.9}, 'appraiser': {'fwd': 0.4}, 'dealer': {'fwd': 0.4}},
}
# ---- outside: the Mudwater Coliseum's swamp dressing (served from the dinopawnz/mudwater repo)
import random as _r
rg = _r.Random(5413); DECO = []; SDECO = []
def sd(f, x, y, z, ry=0, s=1.0): SDECO.append([f, r(x), r(y), r(z), round(ry, 1), round(s, 3)])
def dz(f, x, y, z, ry=0, s=1.0): DECO.append([f, r(x), r(y), r(z), round(ry, 1), round(s, 3)])
dz('water', 0, 0.0, 25, 0, 2.3); dz('mwm_lake', 0, 0.0, 25, 0, 2.3)
for f, x, z, ry in [('bog_mangrove_tree_a_lite', -78, -40, 30), ('bog_mangrove_tree_b_lite', 82, -30, 200), ('bog_mangrove_tree_a_lite', -86, 58, 120), ('bog_mangrove_tree_b_lite', 90, 64, 300),
                    ('bog_acorn_house_lite', -46, 88, 140), ('bog_giant_acorn_lite', 52, 95, 220), ('bog_giant_tree_trunk_lite', -32, -80, 0), ('bog_giant_trunk_lite', 42, -82, 90),
                    ('bog_tree_trunk_a_lite', -22, 98, 45), ('bog_tree_trunk_b_lite', 24, 124, 160), ('bog_root_pathway_lite', -72, 128, 30), ('bog_tree_trunk_b_lite', -100, 10, 250),
                    ('bog_tree_trunk_a_lite', 104, 14, 80)]:
    dz(f, x, 0.0, z, ry)
dz('mwm_spire', -175, 0, -135, 20, 1.0); dz('mwm_spire', 195, 0, -95, 140, 0.8); dz('mwm_spire', -210, 0, 150, 260, 0.7)
for k in range(16):                      # a ring of cypress, leaving the boardwalk side open
    a = -150 + k * 20
    if abs(a) < 25: continue
    rad = rg.uniform(135, 170); x = rad * math.sin(math.radians(a)); z = 25 + rad * math.cos(math.radians(a))
    dz('cypress_%d_lite' % (k % 3 + 1), x, 0.0, z, rg.uniform(0, 360), rg.uniform(0.9, 1.25))
wy = lambda z: L['walk']['y1'] + (FL['lounge'] - L['walk']['y1']) * (L['walk']['z1'] - z) / (L['walk']['z1'] - L['walk']['z0'])
for k, z in enumerate(range(int(L['walk']['z0']) + 4, int(L['walk']['z1']) - 2, 9)):          # lantern posts on the boardwalk rails, alternating sides
    sx = 1 if k % 2 else -1
    pass                                           # (v24, owner) the old Coliseum hook-post lanterns are gone: the Meshy lantern posts (outside.py) light the boardwalk
for k, z in enumerate(range(int(L['walk']['z0']) + 5, int(L['walk']['z1']) - 2, 7)):          # glow plants and reeds in the water along the boardwalk
    for sx in (-1, 1):
        dz('bog_glowplant_%s_lite' % ('a' if (k + (sx > 0)) % 2 else 'b'), sx * rg.uniform(6.0, 7.5), 0.0, z + rg.uniform(-1.5, 1.5), rg.uniform(0, 360), rg.uniform(0.8, 1.2))
        dz('reeds', sx * rg.uniform(8.0, 11.0), 0.0, z + rg.uniform(-2, 2), rg.uniform(0, 360), rg.uniform(0.9, 1.4))
for k in range(26):                                # reeds and glow plants round the porch edge
    side = k % 4; t = rg.uniform(-1, 1)
    PX_, PZB, PZF = L['porch_box']['x'], L['porch_box']['zb'], L['porch_box']['zf']
    x, z = [(t * PX_, PZB - 2.5), (PX_ + 2.5, PZB + (t + 1) / 2 * (PZF - PZB)), (t * PX_, PZF + 2.5), (-PX_ - 2.5, PZB + (t + 1) / 2 * (PZF - PZB))][side]
    if side == 2 and abs(x) < 8: continue
    dz('reeds' if k % 3 else 'bog_glowplant_a_lite', x + rg.uniform(-1, 1), 0.0, z + rg.uniform(-1, 1), rg.uniform(0, 360), rg.uniform(0.9, 1.4))
for k in range(22):                                # lily pads + moss rafts on the water
    a = rg.uniform(0, 360); rad = rg.uniform(92, 140)
    dz('lilypads' if k % 3 else 'bog_moss_c_lite', rad * math.sin(math.radians(a)), 0.02, 20 + rad * math.cos(math.radians(a)), rg.uniform(0, 360), rg.uniform(0.8, 1.5))
for (x, z, ry) in [(9, 68, 80), (-11, 92, -100), (76, 8, 10), (-77, -18, 170), (14, 110, 30)]:
    dz('rowboat', x, 0.05, z, ry)
for k in range(30):                                # floating lanterns drifting on the swamp
    a = rg.uniform(0, 360); rad = rg.uniform(92, 150)
    dz('mwm_floatlantern', rad * math.sin(math.radians(a)), 0.0, 25 + rad * math.cos(math.radians(a)), rg.uniform(0, 360), rg.uniform(1.0, 1.6))
for (x, z) in [(-82, -8), (82, -8), (-60, 95), (60, 95), (0, -80)]: dz('fireflies', x, 0.0, z, rg.uniform(0, 360))
for (x, z, ry) in [(0, -62, 0), (-82, 30, 90), (82, 30, 270)]: dz('mist', x, 0.0, z, ry)
for (x, z) in [(-7.2, L['Z1'] + 6.0), (7.2, L['Z1'] + 6.0)]: dz('mwx_brazier', x, FL['lounge'], z, 0, 0.75)
for sx in (-1, 1): dz('mwx_brazier', sx * 5.6, L['walk']['y1'], L['walk']['z1'] - 1.5, 0, 0.6)
# (v23, owner) the goblet braziers burn: [x, top of the bowl, z, bowl radius] for the game's animated fire
D['fireBowls'] = [[e[1], r(e[2] + 4.55 * e[5]), e[3], round(1.5 * e[5], 3)] for e in DECO if e[0] == 'mwx_brazier']
y2 = FL['hall'] + 0.05                             # jar lanterns hanging from the Floor 2 pent-roof eaves all round
for x in [-L['X1'] + 2 * L['X1'] * (k + 0.5) / 11 for k in range(11)]:
    if abs(x) > 0.5 or True: dz('mwm_jarlantern', x, y2, L['Z1'] + 2.0, 0); dz('mwm_jarlantern', x, y2, -L['Z1'] - 2.0, 0)
for z in list(np.linspace(-(L['Z1'] - 5), L['Z1'] - 5, 8)):
    dz('mwm_jarlantern', L['X1'] + 2.0, y2, z, 0); dz('mwm_jarlantern', -L['X1'] - 2.0, y2, z, 0)
for k in range(24):                                # shelf mushrooms on the outside posts
    side = rg.choice(['f', 'b', 'e', 'w']); y = rg.uniform(4.5, 30.0)
    if side in 'fb':
        x = -L['X1'] + 2 * L['X1'] * rg.randint(1, 21) / 22; z = (L['Z1'] + 0.85) * (1 if side == 'f' else -1); ry = 0 if side == 'f' else 180
    else:
        z = -L['Z1'] + 2 * L['Z1'] * rg.randint(1, 15) / 16; x = (L['X1'] + 0.85) * (1 if side == 'e' else -1); ry = 90 if side == 'e' else 270
    dz('mwm_shelfshroom', x, y, z, ry, rg.uniform(0.6, 1.0))
# the lounge's bayou garden: lily pads on the glowing pond, glow plants and reeds round its curb, fireflies, lanterns hung from the ceiling
gx, gz = F1['pond']
for k in range(7): dz('lilypads', gx + rg.uniform(-4.5, 4.5), Y1 + 0.13, gz + rg.uniform(-3.5, 3.5), rg.uniform(0, 360), 0.35)
for k in range(12):
    t = k / 12 * 2 * math.pi
    dz('bog_glowplant_%s_lite' % ('a' if k % 2 else 'b') if k % 3 else 'reeds', gx + 8.3 * math.cos(t), Y1 + 0.4, gz + 6.7 * math.sin(t), rg.uniform(0, 360), 0.55 if k % 3 else 0.7)
dz('mw_motes', gx, Y1 - 0.5, gz, 0, 0.22)
# the Hall of Fakes, swamp-dressed: lanterns under the winding stair, two great root stumps, glow plants, reeds and lily pads round the moat,
# fireflies and a low fog over the floor
for (x, y, z) in F2['lanterns']: dz('mwm_jarlantern', x, y, z, rg.uniform(0, 360), 0.8)
dz('bog_tree_trunk_a_lite', -23.0 * KX_, Y2, -16.0 * KZ_, 40, 0.8); dz('bog_tree_trunk_b_lite', 23.0 * KX_, Y2, 16.0 * KZ_, 210, 0.8)
ox, oz = RXZ[0] + MO, RXZ[1] + MO
for k in range(22):
    side = k % 4; t = rg.uniform(-0.95, 0.95)
    x, z = [(t * ox, oz + 0.9), (ox + 0.9, t * oz), (t * ox, -oz - 0.9), (-ox - 0.9, t * oz)][side]
    if side == 0 and abs(x) < 3.0: continue
    dz('bog_glowplant_%s_lite' % ('a' if k % 2 else 'b') if k % 3 else 'reeds', x, Y2, z, rg.uniform(0, 360), 0.65 if k % 3 else 0.8)
for k in range(14):
    side = k % 4; t = rg.uniform(-0.9, 0.9)
    x, z = [(t * (ox - 1.6), oz - 1.6), (ox - 1.6, t * (oz - 1.6)), (t * (ox - 1.6), -oz + 1.6), (-ox + 1.6, t * (oz - 1.6))][side]
    if side == 0 and abs(x) < 2.5: continue
    dz('lilypads', x, Y2 + 0.1, z, rg.uniform(0, 360), 0.22)
dz('mw_motes', 0.0, Y2, 0.0, 0, 0.55); dz('mist', 0.0, Y2 - 0.1, 14.0 * KZ_, 0, 0.9)
pc = L['portico']; dz('mw_logo', 0, r(pc['y'] + 2.65), r(pc['z'] + 0.45), 0, 2.55)        # big, inside the gold Meshy frame
# ---- THE LIVING SWAMP: glowing veins on every floor and stair run (they breathe in slow waves), glowing vines on the walls, rising spores
bio = dict(floor=[], wall=[], spores=[], runs=F2['runs'], band=F2['band'], floors=[FL[k] for k in L['keys']])
def wave(x, z): return int(math.hypot(x, z) * 260) % 9000
for x in []:                                            # (lounge floor veins removed - wet muddy planks instead)
    for z in np.arange(-23.5, 24, 9.4):
        if math.hypot(x - F1['bar'][0], z - F1['bar'][1]) < 7.5: continue
        bio['floor'].append([r(x), r(Y1 + 0.03), r(z), 11.0, 9.4, 0, wave(x, z), int(rg.uniform(6500, 9000)), 1])
BXI, BZI = L['band']['xi'], L['band']['zi']                          # the Hall of Fakes floor, wall to wall inside the ramp, round the moat
nx_, nz_ = int(round(2 * BXI / 12.0)), int(round(2 * BZI / 11.0)); tw, td = 2 * BXI / nx_, 2 * BZI / nz_
for i in range(nx_):
    for j in range(nz_):
        x = -BXI + (i + 0.5) * tw; z = -BZI + (j + 0.5) * td
        if abs(x) < RXZ[0] + MO + tw / 2 and abs(z) < RXZ[1] + MO + td / 2: continue
        bio['floor'].append([r(x), r(Y2 + 0.03), r(z), round(tw, 2), round(td, 2), 0, wave(x, z), int(rg.uniform(6500, 9000))])
for (x0, z0, y0, x1, z1, y1, ax, wc) in F2['runs']:      # every run of the winding stair, in 6 m pieces
    ln = math.hypot(x1 - x0, z1 - z0); n = int(ln // 6); hd = math.degrees(math.atan2(x1 - x0, z1 - z0))
    for k in range(n):
        t = (k + 0.5) / n; x = x0 + (x1 - x0) * t; z = z0 + (z1 - z0) * t; y = y0 + (y1 - y0) * t
        bio['floor'].append([r(x), r(y + 0.1), r(z), 4.0, r(ln / n), round(hd, 1), wave(x, z), int(rg.uniform(6500, 9000))])
        if False:                                        # (v23) no glowing vines on the portrait walls: they overlapped the upper row
            if ax == 'z': wx, wz, wry = x, wc - math.copysign(0.09, wc), (180 if wc > 0 else 0)
            else: wx, wz, wry = wc - math.copysign(0.09, wc), z, (270 if wc > 0 else 90)
            bio['wall'].append([r(wx), r(y + 4.25), r(wz), 5.5, 2.2, wry, wave(x, z), int(rg.uniform(7000, 10000))])
for k in range(0):                                       # (lounge wall vines removed)
    x = -36 + k * 8.0
    if abs(x) < 6: continue
    bio['wall'].append([r(x), r(Y1 + 6.4), 29.55, 6.0, 2.4, 180, wave(x, 29), int(rg.uniform(7000, 10000)), 1])
    if abs(abs(x) - 13.5) > 4: bio['wall'].append([r(x), r(Y1 + 6.4), -29.55, 6.0, 2.4, 0, wave(x, -29), int(rg.uniform(7000, 10000)), 1])
for k in range(54):                                      # spores rising through the Hall of Fakes and the lounge
    if k < 34: x, y, z = rg.uniform(-28, 28), Y2 + rg.uniform(0, 4), rg.uniform(-23, 23)
    else: x, y, z = rg.uniform(-32, 32), Y1 + rg.uniform(0, 2), rg.uniform(-27, 27)
    bio['spores'].append([r(x), r(y), r(z), round(rg.uniform(0.035, 0.07), 3), int(rg.uniform(14000, 26000)), int(rg.uniform(0, 20000)), 9.0 if k < 34 else 5.5])
D['bio'] = bio
# ---- the new lounge: waterfalls, shop booths, a sky of hanging lanterns
D['falls'] = F1['falls']; D['booths'] = F1['booths']
D['fire'] = F1['fire']        # the hearth's fire point (for the animated flames)
for (fx_, fy_, fz_, fw_, ft_) in F1['falls']:
    dz('mist', fx_, Y1 - 0.2, fz_ + 2.0, 0, 0.25); dz('mw_motes', fx_, Y1, fz_ + 2.0, 0, 0.12)
    for k in range(4): dz('bog_glowplant_%s_lite' % ('a' if k % 2 else 'b'), fx_ + (-3.6 if k < 2 else 3.6), Y1 + 0.3, fz_ + 1.2 + (k % 2) * 1.6, rg.uniform(0, 360), 0.5)
SDECO = F1['lanterns']        # iron lanterns over the lounge (placed in build_lounge.py, which also bakes their light pools)
SDECO = SDECO + F1.get('trees', [])   # the giant Meshy tree trunks growing through the lounge
SDECO = SDECO + F1.get('mprops', [])  # Meshy furniture, pond rim, grottos, booths, hearth (sp_m_*.glb)
D['sdeco'] = SDECO
D['deco'] = DECO
gal = []; cards = list(range(1, 121)); rg.shuffle(cards); ci = 0
for (n, rad, y, rx, rz, per, sc) in ((34, 106.0, 60.0, 7.0, -4.0, 300000, 10.5), (40, 132.0, 74.0, -5.0, 6.0, 380000, 12.5), (46, 158.0, 48.0, 4.0, 8.0, 460000, 14.5)):
    ring = dict(y=y, z=20.0, rx=rx, rz=rz, r=rad, period=per, cards=[])
    for k in range(n):
        ring['cards'].append([cards[ci], round(360.0 * k / n + rg.uniform(-3, 3), 1), round(rg.uniform(-5, 5), 1), round(sc * rg.uniform(0.85, 1.15), 2)]); ci += 1
    gal.append(ring)
D['galaxy'] = gal
# ---- THE SHOW (swamp magic): the swamp night sky, the giant floating Mudwater pack, moonlight through the mist, will-o'-wisps drifting
# over the water, sky lanterns rising, clouds of fireflies, a glowing bayou rune circle round the island and rings round the steeple
fx = dict(sky=['sp_sky', 0.0, 0.0, 20.0, 1.0], pack=[0.0, 90.0, 4.0, 4.0], moon=[], wisps=[], lanterns=[], runes=[], motes=[])
fx['packRings'] = [['fx_ring_gold', 0.0, 19.0, 72.0, 0.0, 26000], ['fx_ring_teal', 0.0, 24.0, 18.0, 10.0, 34000]]
fx['packBeam'] = ['mwm_diskbeam_t', 0.0, FL['roof'] + 0.5, 4.0, 7.0, 8.5]
fx['moonDisc'] = [-226.7, 264.7, -231.8, 42.0, 38.0, 105.0]      # (v23) the golden crescent: x, y, z, turn, tilt, size (m) - up and left of the building as you walk in
fx['moon'] = [[-84.0, 0.0, 72.0, -14.0, 8.0, 16.0, 150.0], [86.0, 0.0, -38.0, 10.0, -12.0, 14.0, 140.0]]
for k in range(70):
    a = rg.uniform(0, 360); rad = rg.uniform(88, 155)
    fx['wisps'].append(['sp_wisp_' + ('t' if k % 3 else 'g'), r(rad * math.sin(math.radians(a))), round(rg.uniform(1.0, 4.5), 2), r(20 + rad * math.cos(math.radians(a))),
                        round(rg.uniform(4, 12), 1), round(rg.uniform(4, 12), 1), int(rg.uniform(9000, 20000)), int(rg.uniform(0, 15000)), round(rg.uniform(0.7, 1.3), 2)])
for k in range(42):
    a = rg.uniform(0, 360); rad = rg.uniform(88, 150)
    fx['lanterns'].append([r(rad * math.sin(math.radians(a))), r(20 + rad * math.cos(math.radians(a))), int(rg.uniform(70000, 115000)), int(rg.uniform(0, 100000)), round(rg.uniform(1.4, 2.2), 2)])
stx, stz = 0.0, (-(L['Z1'] - 0.4) - (L['Z1'] - 11.0)) / 2; sty = FL['roof'] + 9.5
fx['runes'] = []
fx['motes'] = [['mw_motes', -70.0, 0.0, -58.0], ['mw_motes', 70.0, 0.0, -58.0], ['mw_motes', -70.0, 0.0, 78.0], ['mw_motes', 70.0, 0.0, 78.0],
               ['mwx_fireflies', 0.0, 0.0, 20.0], ['mwx_fireflies', 0.0, 18.0, 20.0], ['mwx_fireflies', 30.0, 30.0, 0.0]]
D['fx'] = fx
import outside; outside.apply(D, L, FL, rg)
import roof; roof.apply(D, L, FL)
import band; band.apply(D, F1)                    # the lounge stage band (drums, harp, guitar, piano, microphone)                 # the roof: the grand finale photo terrace          # the outside, to the owner's concept
print('deco pieces', len(D['deco']))

src = open('/home/claude/spire/spire_src.html').read()
out = src.replace('__DATA__', json.dumps(D, separators=(',', ':'))).replace('__BASE__', BASE).replace('__VER__', VER).replace('__VOICES__', VOICES)
open(O + 'spire.html', 'w').write(out)
print('spire.html', len(out) // 1024, 'KB; real hall', real_hall, 'vault', real_vault)

# ---- the remote, with every character's lines on buttons
import importlib.util
spec = importlib.util.spec_from_file_location('npcmod', '/home/claude/spire/npc.py'); nm = importlib.util.module_from_spec(spec)
import sys as _s; _s.argv = ['x']; spec.loader.exec_module(nm)
ORDER = ['operator', 'ferryman', 'barkeep', 'gator', 'appraiser', 'skipper', 'dealer']
lines = [[k, nm.NPC[k]['name'] + (' (your ape - the Grand Cage)' if k == 'operator' else ''), [[lk, t] for lk, t in nm.NPC[k]['lines'].items()]] for k in ORDER]
rem = open('/home/claude/spire/spire_remote_src.html').read().replace('__NPCLINES__', json.dumps(lines))
open(O + 'spire_remote.html', 'w').write(rem)
print('spire_remote.html', len(rem) // 1024, 'KB')
