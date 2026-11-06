"""bake every position the game needs into spire.html (from the layout JSONs the build scripts write)."""
import json, sys, os
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
  'bannerAt': [[0.0, 0.0, 22.6, 2.2]],      # [x, z, HEIGHT, radius] (v34 fix: v24 scaled the height by mistake and lifted the signs through the hall ceiling onto floor 3)
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
import royale; royale.apply(D, L, FL)      # (v34) MUD ROYALE on floor 3
import band; band.apply(D, F1)
# the Mudwater Swamp Blues (swamp_jazz.py): speakers round every floor, the roof and out on the water
X1_, Z1_ = L['X1'], L['Z1']
spk = [[sx * X1_ * 0.5, FL['lounge'] + 5.5, sz * Z1_ * 0.5] for sx in (-1, 1) for sz in (-1, 1)] + [[0.0, FL['lounge'] + 5.5, 0.0]]
spk += [[sx * X1_ * 0.55, FL['hall'] + 9.0, 0.0] for sx in (-1, 1)] + [[0.0, FL['cards'] + 3.0, 0.0], [0.0, FL['rooms'] + 3.0, 0.0]]
spk += [[sx * 20.0, FL['roof'] + 3.0, 0.0] for sx in (-1, 1)] + [[0.0, 2.5, L['walk']['z1'] - 10.0], [0.0, 2.5, Z1_ + 25.0]]
# the swamp radio (music_prep.py): real public-domain 1920s jazz records; falls back to the original Swamp Blues
_mt = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music_tracks.json')
_tracks = [t[:4] for t in json.load(open(_mt))] if os.path.exists(_mt) else [['swamp_jazz_00', 46957, 'Mudwater Swamp Blues', 'the Spire band'], ['swamp_jazz_01', 46957, 'Mudwater Swamp Blues', 'the Spire band']]
D['music'] = dict(tracks=_tracks, gap=1500, vol=0.5, speakers=[[round(v, 2) for v in p] for p in spk])                    # the lounge stage band (drums, harp, guitar, piano, microphone)                 # the roof: the grand finale photo terrace          # the outside, to the owner's concept
# THE OWNER'S KODAS (koda_rig.py adds their animations): two in the card-room / fireside armchairs, two on bar stools with a beer,
# two strolling round the island bar. [file, x, y, z, ry, scale, walk radius (0 = sitting), walk lap ms (+ = clockwise from above)]
KS = 1.25
import tables as _tb
_chairs = {(round(e[1], 1), round(e[3], 1)): e for e in F1.get('mprops', []) if e[0] == 'sp_m_armchair'}   # keyed by the original spots
_tb.resize(F1.get('mprops', []))          # (v42, owner) card tables lower, the armchairs round them bigger (entries changed in place)
_stools = [e for e in F1.get('mprops', []) if e[0] == 'sp_m_stool']
def _seat(e, top, butt, back):
    ry = e[4]; x = e[1] - back * math.sin(math.radians(ry)); z = e[3] - back * math.cos(math.radians(ry))
    k = e[5] / 0.6309; top *= k; back *= k                      # (v42) chairs can be scaled up (card-table chairs)
    x = e[1] - back * math.sin(math.radians(ry)); z = e[3] - back * math.cos(math.radians(ry))
    floor = e[2] + (-0.9517) * e[5]
    return [round(x, 3), round(floor + top - butt * KS, 3), round(z, 3), ry]
kodas = []
for name, xz in (('sp_koda_5077', (13.2, -8.8)), ('sp_koda_9924', (21.8, 37.5))):
    e = _chairs.get(xz)
    if e: kodas.append([name] + _seat(e, 0.6, 0.072, 0.12) + [KS, 0, 0])
bx, bz = 0.0, 1.0
for name, k in (('sp_koda_119', 0), ('sp_koda_9929', 2)):
    if k < len(_stools):
        e = _stools[k]; ry = math.degrees(math.atan2(bx - e[1], bz - e[3]))
        kodas.append([name, e[1], round(e[2] - 0.9517 * e[5] + 0.9 - 0.042 * KS, 3), e[3], round(ry, 1), KS, 0, 0])
for name, r, lap in (('sp_koda_9372', 9.5, 133000), ('sp_koda_9923', 12.5, -175000)):
    kodas.append([name, bx, round(FL['lounge'] + 0.005, 3), bz, 0, KS, r, lap])
D['kodas'] = kodas
# (v38) more of the owner's Kodas: 6833 strolls a loop through the open floor between the island bar and the front seating,
# 2168 stands between the pool tables watching the games. [file, [[x, z], ...] waypoints, y, scale, walking speed m/s]
FLY = round(FL['lounge'] + 0.005, 3)
# (v42, owner: "some of the koda animations end up breaking and they walk in place after a while") no more timer-driven waypoint
# walks: every walker now rides a slowly turning group (a looping animation the clients play on their own, like the island-bar
# walkers), so there is nothing to fall out of step. 6833 circles the open floor in front of the island bar, 6895 (new) the open
# floor east of the bar; 554 (new) stands near the stage watching the band. [file, centre x, y, centre z, 0, scale, radius, lap ms]
D['kodaPaths'] = []
_lap = lambda r: int(round(2 * math.pi * r / 0.45 * 1000))
D['kodas'] += [['sp_koda_6833', 3.0, FLY, 22.0, 0, KS, 4.5, _lap(4.5)], ['sp_koda_6895', 24.0, FLY, 2.0, 0, KS, 4.2, -_lap(4.2)]]
D['kodas'].append(['sp_koda_2168', 45.2, FLY, 7.75, 90.0, KS, 0, 0])
D['kodas'].append(['sp_koda_554', -6.0, FLY, -28.0, round(math.degrees(math.atan2(0 - -6.0, -36.2 - -28.0)), 1), KS, 0, 0])
# (v38, owner) a guest ape (#6136, not one of the hosts' apes) lounging in the free fireside armchair with a cigar; the MML puffs smoke
# from his mouth when he leans back to blow it out (clip 'cigar', 12 s: draws at 6.2-7.6 s, blows at ~9 s)
AS = 0.9
_e = _chairs.get((26.2, 37.5))
if _e:
    ax, _ay, az, ary = _seat(_e, 0.6, 0.0, 0.18)
    ay = round(_e[2] - 0.9517 * _e[5] + 0.6 - (1.015 - 0.11) * AS - 0.06, 3)
    c_, s_ = math.cos(math.radians(ary)), math.sin(math.radians(ary)); mx, my, mz = 0.0, 1.70 * AS, 0.06 * AS   # his mouth, in his own frame
    D['loungers'] = [['sp_ape_6136', ax, ay, az, ary, AS, [round(ax + mx * c_ + mz * s_, 3), round(ay + my, 3), round(az - mx * s_ + mz * c_, 3)], 12000, 9000]]
# (v30, owner) real MUDWATER cards dealt on every card table (card_spread.py), never ordinary playing cards
for i, e in enumerate([e for e in F1.get('mprops', []) if e[0] == 'sp_m_cardtable']):
    D['sdeco'].append(['sp_mw_deal_%d' % (i % 4), e[1], round(_tb.top(e) + 0.004, 3), e[3], (i * 90) % 360, 1.0])
for i, e in enumerate([e for e in F1.get('mprops', []) if e[0] == 'sp_m_coffeetable']):     # and a Mudwater hand on each coffee table
    c, s_ = math.cos(math.radians(e[4])), math.sin(math.radians(e[4])); lx, lz = -0.03 * e[5], 0.08 * e[5]
    D['sdeco'].append(['sp_mw_fan_%d' % (i % 2), round(e[1] + lx * c + lz * s_, 3), round(e[2] + 0.134 * e[5] + 0.03, 3), round(e[3] - lx * s_ + lz * c, 3), e[4], 1.0])
import pool; pool.apply(D, FL)
# THE BAYOU GARDEN POND comes alive (owner: "ribbitting frogs... fill it with something appropriate"): Meshy lily pads with
# bullfrogs and green treefrogs sitting on them (they croak - a real Everglades pig frog recording, public domain, NPS - and hop
# round when you click them), a red-eared slider basking on a log at the edge, dragonflies darting over the water.
import outside as _o
PCX, PCZ, WY = -25.0, 4.0, FL['lounge'] + 0.125                     # pond centre (build_lounge.garden) and its water level
_rp = _r.Random(808)
# a still, tea-dark water surface over the open middle of the pond (players can wade through it), lily pads floating on it
from glb import Mesh as _Mesh, write as _write
_wm = _Mesh(); _bl = [(PCX + (4.6 + 0.5 * math.sin(3 * t) + 0.3 * math.cos(5 * t)) * math.cos(t), PCZ + (4.2 + 0.4 * math.sin(2 * t + 1)) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
_P = [[x, WY + 0.04, z] for x, z in _bl] + [[PCX, WY + 0.04, PCZ]]; _n = len(_bl)
_I = []
for i in range(_n): _I += [_n, (i + 1) % _n, i]
_wm.add('water', _P, [[0, 1, 0]] * len(_P), [[p[0] / 3, p[2] / 3] for p in _P], _I)
_write(O + 'glb/sp_pond_water.glb', _wm, dict(water=dict(color=(0.05, 0.11, 0.08, 0.72), metal=0.0, rough=0.04, emis=(0.01, 0.05, 0.04), alpha='BLEND', double=True)))
D.setdefault('roofModels', []).append(['sp_pond_water', 0, 0, 0])
pads_ = [(-2.3, -0.9, 'frogbull', 0.52), (1.9, 1.5, 'frogtree', 0.32), (2.7, -1.7, 'frogbull', 0.46), (-0.7, 2.2, 'frogtree', 0.3), (-1.0, -2.4, 'frogbull', 0.5), (0.6, -0.2, None, 0)]
frogs_ = []
for (dx, dz, kind, sz) in pads_:
    x, z = PCX + dx, PCZ + dz
    if 'lily' in _o.META: D['sdeco'].append(_o.place('lily', x, WY + 0.035, z, _rp.uniform(0, 360), 1.5 if kind else 1.1, 'l'))
    if kind and kind in _o.META:
        e = _o.place(kind, 0, 0, 0, 0, sz, 'l'); ry = math.degrees(math.atan2(-dx, -dz)) + _rp.uniform(-140, 140)
        frogs_.append([e[0], round(x, 3), round(WY + 0.1, 3), round(z, 3), round(ry, 1), e[1], e[2], e[3], e[5], 0 if kind == 'frogbull' else 1])
turtle_ = _o.place('turtle', PCX + 3.7, WY - 0.12, PCZ + 0.4, -95, 1.1, 'l') if 'turtle' in _o.META else None
if turtle_: D['sdeco'].append(turtle_)
flies_ = []
if 'dragonfly' in _o.META:
    e = _o.place('dragonfly', 0, 0, 0, 0, 0.4, 'w')
    for k in range(4):
        flies_.append([e[0], round(PCX + _rp.uniform(-2.5, 2.5), 2), round(WY + 0.6 + _rp.uniform(0, 0.9), 2), round(PCZ + _rp.uniform(-2, 2), 2), e[5]])
D['pond'] = dict(frogs=frogs_, flies=flies_, sounds=['frog_0', 'frog_1', 'frog_2', 'frog_3'])
print('pond: %d frogs, %d dragonflies, turtle %s' % (len(frogs_), len(flies_), bool(turtle_)))
print('kodas', [(k[0], k[1:4]) for k in kodas])
print('deco pieces', len(D['deco']))

# (v42, fps) every repeated static model on a floor baked into one file (merge.py); set NOMERGE=1 to build without it
if not os.environ.get('NOMERGE'):
    import merge as _mg
    _mg.merge_all(D, L)

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
