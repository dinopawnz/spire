"""bake every position the game needs into spire.html (from the layout JSONs the build scripts write)."""
import json, sys
O = '/home/claude/spire/out/'
VER = sys.argv[1] if len(sys.argv) > 1 else '1'
BASE = sys.argv[2] if len(sys.argv) > 2 else 'https://raw.githubusercontent.com/dinopawnz/spire/main/'
VOICES = 'true' if '--voices' in sys.argv else 'false'
L = json.load(open(O + 'layout.json')); LL = json.load(open(O + 'lift_layout.json')); F1 = json.load(open(O + 'f1_layout.json'))
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
  'where': {'ferryman': [2.2, L['walk']['y1'], r(L['walk']['z1'] - 3.5), -15], 'barkeep': [F1['bar'][0], Y1, r(F1['bar'][1] + 3.0), 0], 'gator': [19.5, Y1, 25.5, 120],
            'appraiser': [29.0, Y2, 15.5, 240], 'skipper': [8.0, FL['roof'], 12.0, 200], 'dealer': [0.0, FL['cards'], 0.0, 0]},
  'taps': [[t[0], r(t[1] + 0.07), t[2], t[3]] for t in F1['taps']],
  'barTop': r(Y1 + 1.165), 'trayTop': r(Y1 + 1.195), 'barRound': F1['bar'],
  'books': [[6.5, FL['lounge'], 34.0, 0], [-6.5, FL['lounge'], 34.0, 0]],
  'chand': F1['rings'],
  'chand2': [],
  'lifts': LL['lifts'], 'sheaveY': LL['sheave_y'], 'hitch': LL['hitch'], 'rope': LL['rope'], 'sheaveR': LL['sheave_r'], 'cwZ': LL['cw_z'], 'cabApo': L['cab_apo'],
  'hall': [[p['x'], p['y'], p['z'], p['ry']] for p in F2['hall']], 'vault': [[p['x'], p['y'], p['z'], p['ry']] for p in F2['vault']],
  'realHall': real_hall, 'realVault': real_vault, 'hallImgs': F2['imgs'],
  'vaultDoor': F2['door'],
  'refs': [[-24.0, Y2, 12.0], [24.0, Y2, -12.0], [-12.0, Y2, -20.0], [12.0, Y2, 20.0]], 'refFlag': F2['plinth'],
  'bannerAt': [[0.0, 0.0, 22.6, 2.2]],
  'signs': {'hall': [34.0, r(Y2 + 3.0), 1.5, 270], 'vault': [-6.6, r(YV + 2.6), r(RXZ[1] + 0.3), 0]},
  'finalBoards': [[6.6, r(YV + 2.6), r(RXZ[1] + 0.3), 0], [-7.6, r(Y1 + 3.0), 29.45, 180]],
  'stairs': [[s_ * (L['sw']['xi'] - 0.35), r(FL[k] + 3.6), (L['sw']['zl'] + L['sw']['z0']) / 2, 90 if s_ < 0 else 270] for k in L['keys'] for s_ in (1, -1)],
  'npcCap': {'operator': {'inCab': True, 'y': 2.25}, 'barkeep': {'y': 2.3, 'fwd': 0.9}, 'appraiser': {'fwd': 0.4}, 'dealer': {'fwd': 0.4}},
}
# ---- outside: the Mudwater Coliseum's swamp dressing (served from the dinopawnz/mudwater repo)
import random as _r
rg = _r.Random(5413); DECO = []; SDECO = []
def sd(f, x, y, z, ry=0, s=1.0): SDECO.append([f, r(x), r(y), r(z), round(ry, 1), round(s, 3)])
def dz(f, x, y, z, ry=0, s=1.0): DECO.append([f, r(x), r(y), r(z), round(ry, 1), round(s, 3)])
dz('water', 0, 0.0, 25, 0, 1.7); dz('mwm_lake', 0, 0.0, 25, 0, 1.7)
for f, x, z, ry in [('bog_mangrove_tree_a_lite', -78, -40, 30), ('bog_mangrove_tree_b_lite', 82, -30, 200), ('bog_mangrove_tree_a_lite', -86, 58, 120), ('bog_mangrove_tree_b_lite', 90, 64, 300),
                    ('bog_acorn_house_lite', -46, 88, 140), ('bog_giant_acorn_lite', 52, 95, 220), ('bog_giant_tree_trunk_lite', -32, -80, 0), ('bog_giant_trunk_lite', 42, -82, 90),
                    ('bog_tree_trunk_a_lite', -22, 66, 45), ('bog_tree_trunk_b_lite', 24, 124, 160), ('bog_root_pathway_lite', -72, 128, 30), ('bog_tree_trunk_b_lite', -100, 10, 250),
                    ('bog_tree_trunk_a_lite', 104, 14, 80)]:
    dz(f, x, 0.0, z, ry)
dz('mwm_spire', -175, 0, -135, 20, 1.0); dz('mwm_spire', 195, 0, -95, 140, 0.8); dz('mwm_spire', -210, 0, 150, 260, 0.7)
for k in range(16):                      # a ring of cypress, leaving the boardwalk side open
    a = -150 + k * 20
    if abs(a) < 25: continue
    rad = rg.uniform(115, 145); x = rad * math.sin(math.radians(a)); z = 25 + rad * math.cos(math.radians(a))
    dz('cypress_%d_lite' % (k % 3 + 1), x, 0.0, z, rg.uniform(0, 360), rg.uniform(0.9, 1.25))
wy = lambda z: L['walk']['y1'] + (FL['lounge'] - L['walk']['y1']) * (L['walk']['z1'] - z) / (L['walk']['z1'] - L['walk']['z0'])
for k, z in enumerate(range(46, 106, 9)):          # lantern posts on the boardwalk rails, alternating sides
    sx = 1 if k % 2 else -1
    dz('lantern_post', sx * (L['walk']['w'] / 2 + 0.1), wy(z), z, 90 if sx < 0 else -90)
for k, z in enumerate(range(47, 106, 7)):          # glow plants and reeds in the water along the boardwalk
    for sx in (-1, 1):
        dz('bog_glowplant_%s_lite' % ('a' if (k + (sx > 0)) % 2 else 'b'), sx * rg.uniform(6.0, 7.5), 0.0, z + rg.uniform(-1.5, 1.5), rg.uniform(0, 360), rg.uniform(0.8, 1.2))
        dz('reeds', sx * rg.uniform(8.0, 11.0), 0.0, z + rg.uniform(-2, 2), rg.uniform(0, 360), rg.uniform(0.9, 1.4))
for k in range(26):                                # reeds and glow plants round the porch edge
    side = k % 4; t = rg.uniform(-1, 1)
    x, z = [(t * 50, -39.5), (52.5, t * 38), (t * 50, 44.5), (-52.5, t * 38)][side]
    if side == 2 and abs(x) < 8: continue
    dz('reeds' if k % 3 else 'bog_glowplant_a_lite', x + rg.uniform(-1, 1), 0.0, z + rg.uniform(-1, 1), rg.uniform(0, 360), rg.uniform(0.9, 1.4))
for k in range(22):                                # lily pads + moss rafts on the water
    a = rg.uniform(0, 360); rad = rg.uniform(58, 105)
    dz('lilypads' if k % 3 else 'bog_moss_c_lite', rad * math.sin(math.radians(a)), 0.02, 20 + rad * math.cos(math.radians(a)), rg.uniform(0, 360), rg.uniform(0.8, 1.5))
for (x, z, ry) in [(9, 56, 80), (-11, 80, -100), (56, 8, 10), (-57, -18, 170), (14, 98, 30)]:
    dz('rowboat', x, 0.05, z, ry)
for k in range(30):                                # floating lanterns drifting on the swamp
    a = rg.uniform(0, 360); rad = rg.uniform(50, 120)
    dz('mwm_floatlantern', rad * math.sin(math.radians(a)), 0.0, 25 + rad * math.cos(math.radians(a)), rg.uniform(0, 360), rg.uniform(1.0, 1.6))
for (x, z) in [(-62, -8), (62, -8), (-50, 78), (50, 78), (0, -70)]: dz('fireflies', x, 0.0, z, rg.uniform(0, 360))
for (x, z, ry) in [(0, -45, 0), (-62, 30, 90), (62, 30, 270)]: dz('mist', x, 0.0, z, ry)
for (x, z) in [(-7.2, 36.0), (7.2, 36.0)]: dz('mwx_brazier', x, FL['lounge'], z, 0, 0.75)
for sx in (-1, 1): dz('mwx_brazier', sx * 5.6, L['walk']['y1'], L['walk']['z1'] - 1.5, 0, 0.6)
y2 = FL['hall'] + 0.05                             # jar lanterns hanging from the Floor 2 pent-roof eaves all round
for x in [-37.1 + 10.6 * k for k in range(8)]:
    if abs(x) > 0.5 or True: dz('mwm_jarlantern', x, y2, L['Z1'] + 2.0, 0); dz('mwm_jarlantern', x, y2, -L['Z1'] - 2.0, 0)
for z in [-25.0 + 10.0 * k for k in range(6)]:
    dz('mwm_jarlantern', L['X1'] + 2.0, y2, z, 0); dz('mwm_jarlantern', -L['X1'] - 2.0, y2, z, 0)
for k in range(24):                                # shelf mushrooms on the outside posts
    side = rg.choice(['f', 'b', 'e', 'w']); y = rg.uniform(4.5, 30.0)
    if side in 'fb':
        x = -L['X1'] + 2 * L['X1'] * rg.randint(1, 15) / 16; z = (L['Z1'] + 0.85) * (1 if side == 'f' else -1); ry = 0 if side == 'f' else 180
    else:
        z = -L['Z1'] + 2 * L['Z1'] * rg.randint(1, 11) / 12; x = (L['X1'] + 0.85) * (1 if side == 'e' else -1); ry = 90 if side == 'e' else 270
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
dz('bog_tree_trunk_a_lite', -23.0, Y2, -16.0, 40, 0.8); dz('bog_tree_trunk_b_lite', 23.0, Y2, 16.0, 210, 0.8)
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
dz('mw_motes', 0.0, Y2, 0.0, 0, 0.55); dz('mist', 0.0, Y2 - 0.1, 14.0, 0, 0.7)
pc = L['portico']; dz('mw_logo', 0, r(pc['y'] + 0.25), r(pc['z'] + 0.3), 0, 2.0)
# ---- THE LIVING SWAMP: glowing veins on every floor and stair run (they breathe in slow waves), glowing vines on the walls, rising spores
bio = dict(floor=[], wall=[], spores=[], runs=F2['runs'], band=F2['band'], floors=[FL[k] for k in L['keys']])
def wave(x, z): return int(math.hypot(x, z) * 260) % 9000
for x in []:                                            # (lounge floor veins removed - wet muddy planks instead)
    for z in np.arange(-23.5, 24, 9.4):
        if math.hypot(x - F1['bar'][0], z - F1['bar'][1]) < 7.5: continue
        bio['floor'].append([r(x), r(Y1 + 0.03), r(z), 11.0, 9.4, 0, wave(x, z), int(rg.uniform(6500, 9000)), 1])
for x in np.arange(-24.0, 25, 12.0):                     # the Hall of Fakes floor, round the moat
    for z in np.arange(-20.0, 21, 10.0):
        if abs(x) < RXZ[0] + MO + 5 and abs(z) < RXZ[1] + MO + 4: continue
        bio['floor'].append([r(x), r(Y2 + 0.03), r(z), 12.0, 10.0, 0, wave(x, z), int(rg.uniform(6500, 9000))])
for (x0, z0, y0, x1, z1, y1, ax, wc) in F2['runs']:      # every run of the winding stair, in 6 m pieces
    ln = math.hypot(x1 - x0, z1 - z0); n = int(ln // 6); hd = math.degrees(math.atan2(x1 - x0, z1 - z0))
    for k in range(n):
        t = (k + 0.5) / n; x = x0 + (x1 - x0) * t; z = z0 + (z1 - z0) * t; y = y0 + (y1 - y0) * t
        bio['floor'].append([r(x), r(y + 0.1), r(z), 4.0, r(ln / n), round(hd, 1), wave(x, z), int(rg.uniform(6500, 9000))])
        if k % 2 == 0:                                   # glowing vines on the wall above the portraits
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
for (fx_, fy_, fz_, fw_, ft_) in F1['falls']:
    dz('mist', fx_, Y1 - 0.2, fz_ + 2.0, 0, 0.25); dz('mw_motes', fx_, Y1, fz_ + 2.0, 0, 0.12)
    for k in range(4): dz('bog_glowplant_%s_lite' % ('a' if k % 2 else 'b'), fx_ + (-3.6 if k < 2 else 3.6), Y1 + 0.3, fz_ + 1.2 + (k % 2) * 1.6, rg.uniform(0, 360), 0.5)
SDECO = F1['lanterns']        # iron lanterns over the lounge (placed in build_lounge.py, which also bakes their light pools)
SDECO = SDECO + F1.get('trees', [])   # the giant Meshy tree trunks growing through the lounge
SDECO = SDECO + F1.get('mprops', [])  # Meshy furniture, pond rim, grottos, booths, hearth (sp_m_*.glb)
D['sdeco'] = SDECO
D['deco'] = DECO
gal = []; cards = list(range(1, 121)); rg.shuffle(cards); ci = 0
for (n, rad, y, rx, rz, per, sc) in ((34, 78.0, 56.0, 7.0, -4.0, 300000, 9.0), (40, 100.0, 70.0, -5.0, 6.0, 380000, 11.0), (46, 124.0, 44.0, 4.0, 8.0, 460000, 13.0)):
    ring = dict(y=y, z=20.0, rx=rx, rz=rz, r=rad, period=per, cards=[])
    for k in range(n):
        ring['cards'].append([cards[ci], round(360.0 * k / n + rg.uniform(-3, 3), 1), round(rg.uniform(-5, 5), 1), round(sc * rg.uniform(0.85, 1.15), 2)]); ci += 1
    gal.append(ring)
D['galaxy'] = gal
# ---- THE SHOW (swamp magic): the swamp night sky, the giant floating Mudwater pack, moonlight through the mist, will-o'-wisps drifting
# over the water, sky lanterns rising, clouds of fireflies, a glowing bayou rune circle round the island and rings round the steeple
fx = dict(sky=['mw_sky', 0.0, 0.0, 20.0, 3.0], pack=[0.0, 90.0, 4.0, 4.0], moon=[], wisps=[], lanterns=[], runes=[], motes=[])
fx['packRings'] = [['fx_ring_gold', 0.0, 19.0, 72.0, 0.0, 26000], ['fx_ring_teal', 0.0, 24.0, 18.0, 10.0, 34000]]
fx['packBeam'] = ['mwm_diskbeam_t', 0.0, FL['roof'] + 0.5, 4.0, 7.0, 8.5]
fx['moon'] = [[-62.0, 0.0, 58.0, -14.0, 8.0, 16.0, 150.0], [64.0, 0.0, -28.0, 10.0, -12.0, 14.0, 140.0]]
for k in range(70):
    a = rg.uniform(0, 360); rad = rg.uniform(50, 125)
    fx['wisps'].append(['sp_wisp_' + ('t' if k % 3 else 'g'), r(rad * math.sin(math.radians(a))), round(rg.uniform(1.0, 4.5), 2), r(20 + rad * math.cos(math.radians(a))),
                        round(rg.uniform(4, 12), 1), round(rg.uniform(4, 12), 1), int(rg.uniform(9000, 20000)), int(rg.uniform(0, 15000)), round(rg.uniform(0.7, 1.3), 2)])
for k in range(42):
    a = rg.uniform(0, 360); rad = rg.uniform(46, 115)
    fx['lanterns'].append([r(rad * math.sin(math.radians(a))), r(20 + rad * math.cos(math.radians(a))), int(rg.uniform(70000, 115000)), int(rg.uniform(0, 100000)), round(rg.uniform(1.4, 2.2), 2)])
stx, stz = 0.0, (-29.6 + -19.0) / 2; sty = FL['roof'] + 9.5
fx['runes'] = []
fx['motes'] = [['mw_motes', -45.0, 0.0, -40.0], ['mw_motes', 45.0, 0.0, -40.0], ['mw_motes', -45.0, 0.0, 60.0], ['mw_motes', 45.0, 0.0, 60.0],
               ['mwx_fireflies', 0.0, 0.0, 20.0], ['mwx_fireflies', 0.0, 18.0, 20.0], ['mwx_fireflies', 30.0, 30.0, 0.0]]
D['fx'] = fx
print('deco pieces', len(DECO))

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
