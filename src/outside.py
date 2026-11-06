"""THE OUTSIDE, to the owner's concept (reference/19_outside_concept.png). Called by build_html.py: outside.apply(D, L, FL, rg).
Everything is placed from the building's own numbers (L['X1'], L['Z1'], the boardwalk), so it follows when the building grows.
  - the boardwalk: carved Meshy railings both sides, Meshy lantern posts with glowing glass every few metres
  - the water: giant Meshy lily pads, glowing teal Meshy crystal clusters, Meshy bonsai islets round the building
  - the sky: Meshy floating rock islands (bobbing slowly), tall floating cliffs far out, a starry night
  - the front: two tall green banners on the facade, a gold baroque Meshy frame round the MUDWATER sign over the doors
  - lanterns hanging under every balcony, moss clumps under the lower ones
  - the floating Mudwater book over the roof in slowly turning gold rings and a gold glyph ring, a gold beam under it
  - strings of warm gold lights linking the floating cards
  - out: the cartoon acorn houses / mangroves / root stumps / red glow plants, the moonbeam slabs"""
import json, math, os, random
import numpy as np
from glb import Mesh, write, quad, tube, sphere, box, T, M, Ry, Rx, S
from kit import MATS

OUTG = '/home/claude/spire/out/glb/'
META = json.load(open(OUTG + 'meshy_meta.json'))
CARTOON = ('bog_acorn_house_lite', 'bog_giant_acorn_lite', 'bog_mangrove_tree_a_lite', 'bog_mangrove_tree_b_lite', 'bog_giant_tree_trunk_lite',
           'bog_giant_trunk_lite', 'bog_tree_trunk_a_lite', 'bog_tree_trunk_b_lite', 'bog_root_pathway_lite', 'mwm_spire', 'lantern_post')
r3 = lambda v: round(float(v), 3)

def place(name, x, y, z, ry, size, axis='l'):
    """[file, x, y, z, ry, s] for a Meshy model standing on (x, y, z), its footprint centred there, sized `size` m along axis"""
    mn, mx = META[name]
    ext = {'w': mx[0] - mn[0], 'h': mx[1] - mn[1], 'd': mx[2] - mn[2], 'l': max(mx[0] - mn[0], mx[2] - mn[2])}[axis]
    s = size / ext
    ccx, ccz = -(mn[0] + mx[0]) / 2 * s, -(mn[2] + mx[2]) / 2 * s
    c, sn = math.cos(math.radians(ry)), math.sin(math.radians(ry))
    return ['sp_m_' + name, r3(x + ccx * c + ccz * sn), r3(y - mn[1] * s), r3(z - ccx * sn + ccz * c), round(ry, 1), round(s, 4)]

def strands(gal):
    """a string of warm gold lights from every floating card to the next, one GLB per ring (rides in the ring's spin group)"""
    mats = dict(gold=MATS['gold'], bulb=dict(color=(1.0, 0.85, 0.5, 1), emis=(1.0, 0.75, 0.35), emis_strength=3.0))
    files = []
    for ri, ring in enumerate(gal):
        m = Mesh(); R = ring['r']; cs = ring['cards']
        for k in range(len(cs)):
            a0, d0 = cs[k][1], cs[k][2]; a1, d1 = cs[(k + 1) % len(cs)][1], cs[(k + 1) % len(cs)][2]
            if a1 < a0: a1 += 360
            p0 = np.array([R * math.sin(math.radians(a0)), d0 + 4.0, R * math.cos(math.radians(a0))])
            p1 = np.array([R * math.sin(math.radians(a1)), d1 + 4.0, R * math.cos(math.radians(a1))])
            pts = []
            for u in np.linspace(0, 1, 12):
                a = math.radians(a0 + (a1 - a0) * u)
                pts.append((R * math.sin(a), d0 + (d1 - d0) * u + 4.0 - 2.2 * math.sin(math.pi * u), R * math.cos(a)))
            tube(m, 'gold', pts, 0.035, 4)
            for p in pts[1:-1]: sphere(m, 'bulb', 0.16, 5, 3, m=T(p[0], p[1] - 0.12, p[2]))
        f = 'sp_strand_%d' % ri; write(OUTG + f + '.glb', m, mats); files.append(f)
    return files

def front_banner():
    """the same green Mudwater banner as inside the lounge (logo + gold card-back emblem, pointed bottom), big, on a gold rod"""
    m = Mesh(); w, h, tip = 6.6, 17.0, 2.4
    B = '/home/claude/spire/tex/banner_mw.jpg'
    mats = dict(gold=MATS['gold'], iron=MATS['iron'], ban=dict(tex=B, rough=0.9, emis_tex=B, emis=(0.1, 0.1, 0.08)))
    P = np.array([[-w / 2, 0, 0], [w / 2, 0, 0], [w / 2, -h, 0], [0, -h - tip, 0], [-w / 2, -h, 0]])
    U = [[0, 0], [1, 0], [1, h / (h + tip)], [0.5, 1], [0, h / (h + tip)]]
    for side, nz in ((0, 1), (1, -1)):
        I = [0, 4, 1, 1, 4, 2, 2, 4, 3] if side == 0 else [0, 1, 4, 1, 2, 4, 2, 3, 4]
        m.add('ban', np.c_[P[:, 0], P[:, 1] - 0.2, P[:, 2] + nz * 0.02], [[0, 0, nz]] * 5, U, I)
    tube(m, 'iron', [(-w / 2 - 0.5, 0, 0), (w / 2 + 0.5, 0, 0)], 0.1, 8)
    for sx in (-1, 1): sphere(m, 'gold', 0.2, 8, 6, m=T(sx * (w / 2 + 0.55), 0, 0))
    write(OUTG + 'sp_frontbanner.glb', m, mats)
    return h + tip

CRAG_NOTCH, CRAG_FRONT, CRAG_DX, CRAG_W = 0.80, 0.29, 0.10, 0.20     # where the crag's notch + channel are (fractions of its size)
ISLANDS = False      # Meshy floating islands + far cliffs in the sky (owner turned off in v21)
BONSAI = False       # Meshy bonsai islets on the water (owner turned off in v21)

def apply(D, L, FL, rg):
    X1, Z1 = L['X1'], L['Z1']; W = L['walk']; R = random.Random(19)
    add = D['sdeco'].append
    # ---- v25 (owner: "no hideous low quality primitive lanterns", "use Meshy for these plant things too"): every old Coliseum
    #      reed card, jar lantern and floating box lantern becomes its Meshy model, in the same spot and size
    keep = []
    for e in D['deco']:
        f, x, y, z, ry, s = e
        if f == 'reeds':                       # flat reed cards -> Meshy cattail clumps (old card 2.75 m tall at scale 1)
            add(place('cattails', x, y - 0.1, z, ry, 1.8 * s, 'h'))
        elif f == 'mwm_jarlantern':            # jar on a chain (hangs 2.66 m below its point) -> Meshy iron lantern hanging just under it
            hgt = 0.95 * s / 0.85
            add(place('hanglantern', x, y - 0.25 - hgt, z, ry, hgt, 'h'))
        elif f == 'mwm_floatlantern':          # white box on the water -> Meshy paper lantern floating on the water
            add(place('floatlantern', x, y + 0.02, z, ry, 0.84 * s, 'h'))
        else: keep.append(e)
    D['deco'] = keep
    mn, mx = META['floatlantern']                # the sky lanterns rising off the water use the Meshy lantern too
    k = 0.84 / (mx[1] - mn[1])
    D['fx']['lanterns'] = [[x, z, dur, dl, round(sc * k, 4)] for (x, z, dur, dl, sc) in D['fx']['lanterns']]
    D['fx']['skyLantern'] = ['sp_m_floatlantern', round(-mn[1], 4)]
    # ---- out with the cartoon pieces, the moonbeam slabs and the red glow plants out on the water
    # (owner, v21: the original water GLBs stay - nothing is removed from D['deco'])
    for k in range(10):                                   # low mist drifting over the water round the boardwalk and the porch
        a = R.uniform(-150, 150); rr = R.uniform(X1 + 10, X1 + 55)
        D['deco'].append(['mist', r3(rr * math.sin(math.radians(a))), 0.0, r3(Z1 * 0.3 + rr * math.cos(math.radians(a))), round(R.uniform(0, 360), 1), round(R.uniform(0.6, 1.0), 2)])
    # (moonbeams kept)
    # ---- the boardwalk: carved railings both sides, lantern posts at every other joint
    w = L['walk_w']; z0, z1 = L['walk_z0'], L['walk_z0'] + L['walk_len']; ya, yb = FL['lounge'], L['walk_y']
    wy = lambda z: ya + (yb - ya) * (z - z0) / (z1 - z0)
    seg = 3.0; zs = list(np.arange(z0 + 1.0, z1 - 0.5, seg))
    for i, zc in enumerate(zs):
        for sx in (-1, 1):
            add(place('railing', sx * (w / 2 + 0.1), wy(zc + seg / 2) - 0.02, zc + seg / 2, 90, seg, 'w'))
            if i % 2 == 0: add(place('lanternpost', sx * (w / 2 + 0.1), wy(zc), zc, 0, 2.9, 'h'))
    # ---- water: lily pads, glowing crystal clusters, bonsai islets
    def water_spot(rmin, rmax, avoid_walk=7.0):
        for _ in range(200):
            a = R.uniform(0, 2 * math.pi); rr = R.uniform(rmin, rmax)
            x, z = rr * math.sin(a), Z1 * 0.3 + rr * math.cos(a)
            if abs(x) < avoid_walk and z > Z1 - 2: continue                        # keep the boardwalk clear
            if abs(x) < X1 + 9 and abs(z) < Z1 + 12: continue                       # not under the porch
            return x, z
        return None
    for k in range(26):
        p = water_spot(X1 + 14, X1 + 70, 6.5)
        if p: add(place('lily', p[0], 0.06, p[1], R.uniform(0, 360), R.uniform(3.0, 6.0), 'l'))
    for k, zc in enumerate(np.arange(z0 + 6, z1 - 4, 9.0)):                        # crystals close to the boardwalk, both sides
        sx = 1 if k % 2 else -1
        add(place('crystals', sx * R.uniform(w / 2 + 3.0, w / 2 + 6.5), -0.3, zc + R.uniform(-2, 2), R.uniform(0, 360), R.uniform(2.2, 3.6), 'h'))
    for k in range(10):
        p = water_spot(X1 + 18, X1 + 85, 9.0)
        if p: add(place('crystals', p[0], -0.4, p[1], R.uniform(0, 360), R.uniform(2.5, 4.5), 'h'))
    for k in range(9 if BONSAI else 0):
        p = water_spot(X1 + 22, X1 + 80, 14.0)
        if p: add(place('bonsai', p[0], -0.8, p[1], R.uniform(0, 360), R.uniform(14.0, 22.0), 'l'))
    # ---- the sky: floating islands (bob slowly), tall floating cliffs far out
    isl = []
    for k in range(11):
        a = math.radians(-165 + k * 330 / 10 + R.uniform(-10, 10)); rr = R.uniform(X1 + 25, X1 + 75)
        x, z = rr * math.sin(a), Z1 * 0.3 + rr * math.cos(a)
        if abs(x) < 25 and z > 0: x += 40 * (1 if x >= 0 else -1)
        p = place('island', x, R.uniform(26, 70), z, R.uniform(0, 360), R.uniform(22, 36), 'h')
        isl.append(p + [round(R.uniform(1.5, 3.0), 2), int(R.uniform(9000, 16000))])
    for k in range(4):
        a = math.radians(-150 + k * 100 + R.uniform(-15, 15)); rr = R.uniform(X1 + 150, X1 + 200)
        p = place('cliff', rr * math.sin(a), R.uniform(8, 22), Z1 * 0.3 + rr * math.cos(a), R.uniform(0, 360), R.uniform(55, 80), 'h')
        isl.append(p + [round(R.uniform(2.0, 4.0), 2), int(R.uniform(14000, 22000))])
    D['fx']['islands'] = isl if ISLANDS else []
    # ---- the front: tall banners, gold frame round the MUDWATER sign
    bh = front_banner()
    top = max(L['balconies']['lines']) - 0.6; zf = Z1 + L['balconies']['depth'] + 0.35
    D['frontBanners'] = [[sx * 20.0, r3(top), r3(zf)] for sx in (-1, 1)]
    pc = L['portico']
    for sx in (-1, 1):                                     # the great double doors, swung wide open against the front wall
        add(place('doorleaf', sx * (4.5 + 1.45), FL['lounge'], Z1 + 0.42, 0, 5.4, 'h'))
    add(place('signframe', 0.0, pc['y'] - 1.1, pc['z'] + 0.05, 0, 11.0, 'w'))      # 1.5 m higher, clear of heads (owner, v22)
    # ---- lanterns under every balcony edge, moss clumps under the lower balconies on the front
    Dd = L['balconies']['depth']
    for li, y in enumerate(L['balconies']['lines']):
        for side in range(4):
            ln = 2 * X1 if side % 2 == 0 else 2 * Z1
            for t in np.arange(4.0, ln - 2, 10.5):
                u = -ln / 2 + t; o = Dd - 0.35
                x, z = [(u, Z1 + o), (X1 + o, u), (u, -Z1 - o), (-X1 - o, u)][side]
                if side == 0 and y < 12 and abs(x) < 11: continue                  # the portico roof
                add(place('hanglantern', x, y - 0.45 - 0.75, z, R.uniform(0, 60), 0.75, 'h'))     # Meshy iron lantern under the balcony edge (was the code-built one)
        if li < 3:
            for t in np.arange(5.0, 2 * X1 - 3, 15.0):
                x = -X1 + t
                if y < 12 and abs(x) < 11: continue
                add(place('mossclump', x, y - 1.5, Z1 + Dd - 0.1, R.choice([0, 180]), 1.8, 'w'))
    # ---- (v23, owner) two great waterfalls either side of the entrance: tall mossy rock grottos out in the water, turned a little
    # toward the boardwalk, the water (animated by the game, like the lounge falls) pouring down into the swamp in a cloud of mist
    # (owner: the water must come from somewhere) a tall dark mossy crag on each side, made for this (Meshy): a notch in its top edge and
    # a water-worn channel down its face - the water spills out of the notch, down the channel and into the swamp
    HC = 30.0
    cmn, cmx = META['crag']; c_s = (HC + 1.5) / (cmx[1] - cmn[1]); c_w = (cmx[0] - cmn[0]) * c_s; c_d = (cmx[2] - cmn[2]) * c_s
    big = []
    for sx in (-1, 1):
        fx, fz, ry = sx * 33.0, L['walk_z0'] + 30.0, -sx * 45.0
        c, sn = math.cos(math.radians(ry)), math.sin(math.radians(ry))
        fwd = lambda dz, dx=0.0: (fx + sn * dz + c * dx, fz + c * dz - sn * dx)   # dz in front of the crag's centre, dx to its right
        add(place('crag', fx, -1.5, fz, ry, HC + 1.5, 'h'))
        # measured on the model (model units): the groove runs at x +0.07; the notch's lip is at y +0.50; from there down to y 0.0 the groove
        # face is at z ~0.02; below that the rock bulges out to z 0.62 at the waterline (y -0.9). The water follows it in two sheets.
        y_of = lambda ym: -1.5 + (ym - cmn[1]) * c_s; z_of = lambda zm: zm * c_s
        gx_ = 0.07 * c_s; wW = 0.24 * c_s
        y_lip, y_bend, z_up, z_base = y_of(0.50), y_of(0.0), z_of(0.04), z_of(0.64)
        # the face profile under the groove (model y, front-most z), measured; the water runs a hand's width in front of it, segment by segment
        prof = [(0.40, 0.05), (0.02, 0.08), (-0.30, 0.45), (-0.60, 0.57), (-0.93, 0.70)]
        pad = 0.035
        for k in range(len(prof) - 1):
            (ya_, za_), (yb_, zb_) = prof[k + 1], prof[k]            # foot (lower) -> head (upper)
            Ya, Yb = (0.12 if k == len(prof) - 2 else y_of(ya_)), y_of(yb_) + (0.0 if k == 0 else 0.6)
            Za, Zb = z_of(za_ + pad), z_of(zb_ + pad)
            fx_, fz_ = fwd(Za, gx_); ln = math.hypot(Yb - Ya, Za - Zb); tilt = -math.degrees(math.atan2(Za - Zb, Yb - Ya))
            last = (k == len(prof) - 2)
            D['falls'].append([r3(fx_), r3(Ya), r3(fz_), round(wW * (1.0 + 0.08 * k), 2), r3(Ya + ln), ry, 1 if last else 2, round(tilt, 1) or 0.01])
        z_base = z_of(prof[-1][1])
        top = y_lip
        for k in range(3):                                  # mist rolling off the foot of the falls
            mx_, mz_ = fwd(z_base + 3.0 + k * 2.6, gx_)
            D['deco'].append(['mist', r3(mx_ + R.uniform(-2, 2)), 0.0, r3(mz_), round(R.uniform(0, 360), 1), round(R.uniform(0.4, 0.55), 2)])
        big.append((fx, fz, max(c_w, c_d) / 2 + 3.0))
        print('falls', sx, 'crag', round(fx, 1), round(fz, 1), 'size', round(c_w, 1), round(c_d, 1), 'lip', round(y_lip, 1), 'bend', round(y_bend, 1), 'tilt', round(tilt, 1))
    # keep the water round the falls clear of the smaller pieces
    keep = lambda e: all(math.hypot(e[1] - bx, e[3] - bz) > br for (bx, bz, br) in big)
    D['sdeco'][:] = [e for e in D['sdeco'] if e[0] in ('sp_m_crag',) or keep(e)]
    D['deco'][:] = [e for e in D['deco'] if e[0] == 'mist' or keep(e)]
    # (v24, owner) keep the entrance bridge and the porch clear of fog: the mist GLB is a huge sheet (about 82 x 59 m at scale 1),
    # so test each piece's rotated footprint against the walkway and slide it sideways off the bridge, or drop it
    MB = (-40.8, -46.0, 41.2, 13.1)
    clear = (-(L['walk_w'] / 2 + 6.0), L['walk_w'] / 2 + 6.0, Z1 - 1.0, L['walk_z0'] + L['walk_len'] + 10.0)
    def mist_hits(e):
        x, z, ry, sc = e[1], e[3], math.radians(e[4]), e[5]
        c, sn = math.cos(ry), math.sin(ry)
        pts = [(x + (u * c + v * sn) * sc, z + (-u * sn + v * c) * sc) for u in (MB[0], MB[2]) for v in (MB[1], MB[3])]
        xs, zs = [p_[0] for p_ in pts], [p_[1] for p_ in pts]
        return max(xs) > clear[0] and min(xs) < clear[1] and max(zs) > clear[2] and min(zs) < clear[3]
    kept = []
    for e in D['deco']:
        if e[0] != 'mist' or not mist_hits(e): kept.append(e); continue
        e = list(e); e[5] = round(min(e[5], 0.35), 2)              # thinner wisps near the entrance
        sx_ = 1 if e[1] >= 0 else -1
        for _ in range(60):
            if not mist_hits(e): break
            e[1] = r3(e[1] + sx_ * 1.5)
        if not mist_hits(e): kept.append(e)
    print('mist: kept', sum(1 for e in kept if e[0] == 'mist'), 'of', sum(1 for e in D['deco'] if e[0] == 'mist'), '(bridge kept clear)')
    D['deco'][:] = kept
    # ---- (v23, owner's concept) swampy vines everywhere: curtains of hanging vines + Spanish moss off the balcony edges, ivy climbing the walls
    vm, vx = META['vines']; v_asp = (vx[1] - vm[1]) / (vx[0] - vm[0])
    Dd = L['balconies']['depth']; lines = sorted(L['balconies']['lines']); ban_low = max(lines) - 13.0
    def clear_front(x, ytop, ybot):
        if abs(x) < 11.5 and ybot < 21.0: return False                             # the portico, the MUDWATER sign, the door
        if abs(abs(x) - 20.0) < 3.4 and ytop > ban_low: return False               # the two big front banners
        return True
    nv = 0
    for y in lines:
        for side in ('front', 'east', 'west'):
            ln = 2 * X1 if side == 'front' else 2 * Z1
            for t in np.arange(2.0, ln - 2.0, 3.4):
                if R.random() > (0.34 if side == 'front' else 0.12): continue      # (v24) fewer, fuller curtains: frame rate
                w_ = R.uniform(4.0, 5.6); h_ = w_ * v_asp * R.uniform(1.0, 1.35)
                u = -ln / 2 + t + R.uniform(-0.6, 0.6)
                if side == 'front':
                    if not clear_front(u, y, y - h_): continue
                    x, z, ry = u, Z1 + Dd - 0.05, 0
                else:
                    sg = 1 if side == 'east' else -1; x, z, ry = sg * (X1 + Dd - 0.05), u, 90 * sg
                e = place('vines', x, y - 0.05 - h_, z, ry, w_, 'w')
                add(e); nv += 1
    ni = 0
    for k in range(40):                                                            # ivy patches climbing the front wall
        x = R.uniform(-X1 + 2, X1 - 2); y = R.uniform(5.0, max(lines) - 2.0); w_ = R.uniform(3.0, 5.2)
        if not clear_front(x, y + w_, y): continue
        add(place('ivy', x, y, Z1 + 0.16, 0, w_, 'w')); ni += 1
        if ni >= 5: break
    for sx in (-1, 1):                                                             # thick ivy up both front corners
        for y in np.arange(6.0, max(lines) - 3.0, 14.0):
            add(place('ivy', sx * (X1 - 1.2), y, Z1 + 0.16, 0, R.uniform(3.4, 4.4), 'w')); ni += 1
    print('outside: vines', nv, 'ivy', ni)
    # ---- (v23, owner) the windows: Meshy rustic lodge windows (weathered timber frame, mullions, warm glowing panes, mossy sill, shutters)
    # set over each outside window, sized to it
    if 'window' in META:
        wmn, wmx = META['window']; ww0, wh0, wd0 = wmx[0] - wmn[0], wmx[1] - wmn[1], wmx[2] - wmn[2]
        nw = 0
        for (x, y, z, fr, w_, h_) in L.get('ext_windows', []):
            s_ = (w_ + 0.5) / ww0; syr = (h_ + 0.5) / (wh0 * s_)
            ox, oz = math.sin(math.radians(fr)), math.cos(math.radians(fr))
            yb = y - (h_ + 0.5) / 2
            e = place('window', x + ox * (wd0 * s_ / 2 + 0.02), yb, z + oz * (wd0 * s_ / 2 + 0.02), fr, w_ + 0.5, 'w')
            e[2] = round(yb - wmn[1] * s_ * syr, 3); e.append(round(syr, 3)); add(e); nw += 1
        print('outside: lodge windows', nw)
    # ---- (v23) three rustic swamp-timber gables on the front roof edge (Meshy), with a warm glowing window each - a bayou lodge, not a castle
    if 'gable' in META:
        for (gx, gy, gz, gw) in L.get('gables', []):
            gm, gM = META['gable']; d_ = (gM[2] - gm[2]) * gw / (gM[0] - gm[0])
            add(place('gable', gx, gy - 0.3, gz - d_ / 2 + 0.6, 0, gw, 'w'))
    # (owner, v21: the original floating Mudwater pack, gold + teal rings and beam stay on top - no book)
    # (the floating cards stay exactly as they are - owner)
    print('outside: placed', len(D['sdeco']), 'spire models;', len(isl), 'sky islands/cliffs')
