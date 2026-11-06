"""(v31, owner: "animate kodas ripping mudwater packs and looking at their new cards") a seated Koda holding a MUDWATER pack:
it turns the pack over, tears the foil strip off the top, pulls out a fan of five real Mudwater cards, leans in to look at them,
wiggles with excitement, then puts them away - and a fresh pack appears. 14 s loop, one glTF clip (played with anim=self in MML).
  python3 koda_pack.py <src koda.glb> <dst.glb> [seed]"""
import math, os, sys, random, itertools
import numpy as np
from PIL import Image
sys.path.insert(0, '/home/claude/spire')
from glb import Mesh, write, quad, box, T, M, Rx, Ry, Rz
import koda_rig as K
from koda_rig import X, Y_, Z
MW = '/home/claude/mudwater_repo/'; TMP = '/home/claude/spire/out/cards_small/'; os.makedirs(TMP, exist_ok=True)
PW, PH, PD, CUT = 0.165, 0.26, 0.018, 0.84          # pack size in Koda model units (the Koda is ~0.9 tall); the tear line at 82 %

def small(name, h=300):
    p = TMP + 'pk_' + name
    if not os.path.exists(p): Image.open(MW + name).convert('RGB').resize((int(h * 0.72), h), Image.LANCZOS).save(p, quality=86)
    return p

def pack_parts(tmpdir):
    import io, json
    from glb import read_glb
    js, b = read_glb(MW + 'mw_pack.glb'); v = js['bufferViews'][js['images'][0]['bufferView']]
    face = tmpdir + 'pack_face.jpg'
    Image.open(io.BytesIO(b[v.get('byteOffset', 0): v.get('byteOffset', 0) + v['byteLength']])).convert('RGB').resize((260, 415), Image.LANCZOS).save(face, quality=88)
    mats = dict(face=dict(tex=face, emis_tex=face, emis=(0.35, 0.35, 0.35), rough=0.35, metal=0.2),
                side=dict(color=(0.06, 0.06, 0.065, 1), metal=0.6, rough=0.35))
    out = []
    for (name, f0, f1) in (('body', 0.0, CUT), ('strip', CUT, 1.0)):
        m = Mesh(); h = PH * (f1 - f0); yc = -PH / 2 + PH * (f0 + f1) / 2
        quad(m, 'face', PW, h, M(T(0, yc, PD / 2)), uv=(0, 1 - f1, 1, 1 - f0))
        quad(m, 'face', PW, h, M(T(0, yc, -PD / 2), Ry(180)), uv=(0, 1 - f1, 1, 1 - f0))
        box(m, 'side', PW, h, PD * 0.96, m=T(0, yc, 0), faces='xXyY')
        p = tmpdir + 'pack_%s.glb' % name; write(p, m, mats); out.append(p)
    return out

def fan_part(tmpdir, seed):
    R = random.Random(seed); m = Mesh(); mats = {}; ch = 0.21; cw = ch * 0.72
    back = small('mwc_back.jpg'); mats['back'] = dict(tex=back, emis_tex=back, emis=(0.25, 0.25, 0.25), rough=0.5)
    have = [n for n in range(1, 121) if os.path.exists(MW + 'mwc_%03d.jpg' % n)]
    for i, c in enumerate(R.sample(have, 5)):
        f = small('mwc_%03d.jpg' % c); mats['c%d' % i] = dict(tex=f, emis_tex=f, emis=(0.3, 0.3, 0.3), rough=0.5)
        a = -28 + 14 * i; dz = -0.0015 * i
        quad(m, 'c%d' % i, cw, ch, M(Rz(-a), T(0, ch * 0.42, dz)))                      # face toward +z of the fan (the Koda)
        quad(m, 'back', cw, ch, M(Rz(-a), T(0, ch * 0.42, dz - 0.0007), Ry(180)))       # Mudwater card backs toward the room
    p = tmpdir + 'pack_fan.glb'; write(p, m, mats); return p

def reach(rig, base, side, tgt, grid=None):
    """brute-force arm angles so the hand lands on tgt (model space); mirrored for the left arm"""
    sg = 1 if side == 'r' else -1; best = (1e9, None)
    for a, b, c, d in itertools.product(range(-110, 1, 10), range(-50, 51, 10), range(-30, 151, 15), range(-60, 61, 20)):
        p = base + [('upperarm_' + side, X, a), ('upperarm_' + side, Y_, sg * b), ('lowerarm_' + side, Y_, sg * c), ('lowerarm_' + side, X, d)]
        h = rig.world_m(p, 'hand_' + side)[:3, 3]; e = np.linalg.norm(h - tgt) + 0.0002 * (abs(a) + abs(c)) / 10
        if e < best[0]: best = (e, (a, b, c, d))
    a, b, c, d = best[1]
    return [('upperarm_' + side, X, a), ('upperarm_' + side, Y_, sg * b), ('lowerarm_' + side, Y_, sg * c), ('lowerarm_' + side, X, d)], best[0]

def lerp_arm(A, B, t):
    return [(b0, ax, a0 + (b1 - a0) * t) for (b0, ax, a0), (_, _, b1) in zip(A, B)]

def build(src, dst, seed=1):
    rig = K.Rig(src)
    base = K.sit_base() + [('upperarm_l', Z, -58), ('upperarm_r', Z, 58), ('spine_01', X, -8)]
    hipz = 0.0
    # hand targets (model space, Koda faces +z): pack held at the chest, right hand pinching the top, then yanking up/out;
    # the fan lifted up in front of the face
    L_rest, e1 = reach(rig, base, 'l', np.array([0.05, 0.40, 0.19]))
    R_pinch, e2 = reach(rig, base, 'r', np.array([-0.035, 0.49, 0.19]))
    R_yank, e3 = reach(rig, base, 'r', np.array([-0.2, 0.6, 0.12]))
    R_rest, e4 = reach(rig, base, 'r', np.array([-0.16, 0.34, 0.14]))
    L_look, e5 = reach(rig, base, 'l', np.array([0.02, 0.47, 0.23]))
    print('reach errors', [round(float(e), 3) for e in (e1, e2, e3, e4, e5)])
    def pose(l, r, head=0.0, look=0.0, wig=0.0, breathe=0.0):
        return base + l + r + [('neck_01', X, head * 0.5), ('head', X, head), ('neck_01', Y_, look), ('spine_03', Z, wig), ('spine_03', X, breathe)]
    K_ = []
    def k(t, l, r, **kw): K_.append((t, pose(l, r, **kw), (0, 0, 0)))
    k(0.0, L_rest, R_pinch, head=-12)
    k(1.0, L_rest, R_pinch, head=-14, look=10)
    k(1.8, L_rest, R_pinch, head=-12, look=-6)
    k(2.4, L_rest, R_pinch, head=-16)
    k(2.75, L_rest, R_yank, head=-6, wig=4)                           # RIP
    k(3.2, L_rest, R_rest, head=-14)
    k(3.9, lerp_arm(L_rest, L_look, 0.6), R_rest, head=-18)
    k(4.6, L_look, R_rest, head=-22, look=4)
    k(6.0, L_look, R_rest, head=-24, look=-6, breathe=-3)
    k(6.6, L_look, R_rest, head=-20, wig=6)
    k(6.9, L_look, R_rest, head=-20, wig=-6)
    k(7.2, L_look, R_rest, head=-20, wig=6)
    k(7.5, L_look, R_rest, head=-22, wig=0)
    k(9.0, L_look, R_rest, head=-26, look=8)
    k(10.2, L_rest, R_rest, head=-12)
    k(11.2, L_rest, lerp_arm(R_rest, R_pinch, 0.7), head=-10)
    k(12.4, L_rest, R_pinch, head=-12)
    PER = 14.0
    # props
    tmp = '/tmp/claude-0/-home-claude/5ddaad6a-f847-5413-a277-78b451d1faa9/scratchpad/kpack_%d/' % seed; os.makedirs(tmp, exist_ok=True)
    body, strip = pack_parts(tmp); fan = fan_part(tmp, seed)
    p0 = pose(L_rest, R_pinch)
    HL = rig.world_m(p0, 'hand_l'); HR = rig.world_m(p0, 'hand_r')
    pc = (HL[:3, 3] + np.array([-0.03, 0.09, 0.035]))                 # the pack stands up in the left palm, face to the room
    W = np.eye(4); W[:3, 3] = pc
    nb = rig.attach(body, 'hand_l', np.linalg.inv(HL) @ W)
    nr = rig.attach(strip, 'hand_r', np.linalg.inv(HR) @ W)           # same world place, but carried off by the right hand
    pl = pose(L_look, R_rest); HL2 = rig.world_m(pl, 'hand_l')
    Wf = np.eye(4); Wf[:3, :3] = K.axang(Y_, 180) @ K.axang(X, 12); Wf[:3, 3] = HL2[:3, 3] + np.array([-0.02, 0.03, 0.02])   # fan faces the Koda
    nf = rig.attach(fan, 'hand_l', np.linalg.inv(HL2) @ Wf)
    S = lambda n: rig.js['nodes'][n]['scale']
    def sc(n, keys):                                                  # [(t, factor)] -> scale track
        b = np.array(S(n)); return (n, 'scale', [t for t, _ in keys], [list(b * max(f, 1e-4)) for _, f in keys])
    extra = [sc(nb, [(0, 1), (3.3, 1), (3.6, 0), (11.0, 0), (11.6, 1), (PER, 1)]),
             sc(nr, [(0, 1), (2.9, 1), (3.15, 0), (11.0, 0), (11.6, 1), (PER, 1)]),
             sc(nf, [(0, 0), (3.3, 0), (3.8, 1), (9.9, 1), (10.3, 0), (PER, 0)])]
    rig.add_clip('pack', K_, PER, extra)
    print(dst, rig.save(dst) // 1024, 'KB')

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1)
