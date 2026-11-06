"""THE OWNER'S KODAS in the lounge (owner: "have the kodas seated on the chairs around the first floor and walking around and having
a beer on one of the bar stools"). The Koda GLBs come rigged (UE5-mannequin skeleton, T-pose, no animation). This adds a looping
animation clip to each one (played in MML with anim = the same file, like the castle's characters):
  sit   - sitting back in a lounge armchair: breathing, looking round the room now and then, a tap of the foot
  bar   - perched on a bar stool with a Meshy beer stein in the right hand, lifting it for a swig every few seconds
  walk  - a walk cycle in place (the MML moves the Koda round the island bar)
and shrinks the textures. Poses are written as rotations about WORLD axes in the T-pose (Koda faces +z, its left is +x),
applied bone by bone down the chain, so "knee +80 about x" means the same thing whatever the bone's own axes are.
  python3 koda_rig.py <src.glb> <dst.glb> <sit|bar|walk>"""
import json, math, struct, sys, io
import numpy as np
from glb import read_glb

def q_from_m(R):
    t = np.trace(R)
    if t > 0:
        s = math.sqrt(t + 1) * 2; return np.array([(R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s, s / 4])
    i = int(np.argmax(np.diag(R)))
    if i == 0:
        s = math.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2]) * 2; return np.array([s / 4, (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s, (R[2, 1] - R[1, 2]) / s])
    if i == 1:
        s = math.sqrt(1 + R[1, 1] - R[0, 0] - R[2, 2]) * 2; return np.array([(R[0, 1] + R[1, 0]) / s, s / 4, (R[1, 2] + R[2, 1]) / s, (R[0, 2] - R[2, 0]) / s])
    s = math.sqrt(1 + R[2, 2] - R[0, 0] - R[1, 1]) * 2; return np.array([(R[0, 2] + R[2, 0]) / s, (R[1, 2] + R[2, 1]) / s, s / 4, (R[1, 0] - R[0, 1]) / s])

def m_from_q(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])

def axang(ax, deg):
    ax = np.array(ax, float); ax /= np.linalg.norm(ax); a = math.radians(deg); c, s = math.cos(a), math.sin(a); x, y, z = ax
    return np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                     [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                     [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])

X, Y_, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)

class Rig:
    def __init__(self, path):
        self.js, self.bin = read_glb(path); self.bin = bytearray(self.bin)
        N = self.js['nodes']; self.idx = {n.get('name'): i for i, n in enumerate(N)}
        self.parent = {}
        for i, n in enumerate(N):
            for c in n.get('children', []): self.parent[c] = i
        self.T, self.R, self.S = {}, {}, {}
        for i, n in enumerate(N):                                   # every node to TRS (animated nodes may not use 'matrix')
            if 'matrix' in n:
                M = np.array(n.pop('matrix')).reshape(4, 4).T; t = M[:3, 3]; A = M[:3, :3]
                s = np.linalg.norm(A, axis=0); R = A / s
                n['translation'] = [float(v) for v in t]; n['rotation'] = [float(v) for v in q_from_m(R)]; n['scale'] = [float(v) for v in s]
            self.T[i] = np.array(n.get('translation', [0, 0, 0]), float); self.R[i] = m_from_q(n.get('rotation', [0, 0, 0, 1]))
        self.W = {}
        def wr(i):                                                  # bind world rotation
            if i in self.W: return self.W[i]
            p = self.parent.get(i); self.W[i] = (wr(p) if p is not None else np.eye(3)) @ self.R[i]; return self.W[i]
        for i in range(len(N)): wr(i)

    def local_q(self, pose):
        """pose: [(bone, axis, deg), ...] world-axis rotations in the T-pose -> {node: local quaternion}"""
        D = {}
        for (b, ax, deg) in pose:
            i = self.idx[b]; Wb = self.W[i]
            D[i] = (Wb.T @ axang(ax, deg) @ Wb) @ D.get(i, np.eye(3))        # later entries apply after earlier ones
        return {i: q_from_m(self.R[i] @ d) for i, d in D.items()}

    def add_clip(self, name, keys, period):
        """keys: [(t seconds, pose list, pelvis offset xyz)] - the first key is repeated at t=period so the loop is seamless"""
        keys = list(keys) + [(period, keys[0][1], keys[0][2])]
        bones = sorted({self.idx[b] for (_, p, _) in keys for (b, _, _) in p})
        per = [self.local_q(p) for (_, p, _) in keys]
        times = np.array([k[0] for k in keys], np.float32)
        acc0 = len(self.js['accessors']); chans, samps = [], []
        def put(arr, typ, mm=False):
            arr = np.ascontiguousarray(arr, np.float32)
            while len(self.bin) % 4: self.bin.append(0)
            self.js['bufferViews'].append({'buffer': 0, 'byteOffset': len(self.bin), 'byteLength': arr.nbytes}); self.bin.extend(arr.tobytes())
            a = {'bufferView': len(self.js['bufferViews']) - 1, 'componentType': 5126, 'count': len(arr), 'type': typ}
            if mm: a['min'] = [float(arr.min())]; a['max'] = [float(arr.max())]
            self.js['accessors'].append(a); return len(self.js['accessors']) - 1
        ta = put(times, 'SCALAR', True)
        for i in bones:
            qs = []
            for k in range(len(keys)):
                q = per[k].get(i, q_from_m(self.R[i]))
                if qs and np.dot(q, qs[-1]) < 0: q = -q
                qs.append(q)
            samps.append({'input': ta, 'output': put(np.array(qs), 'VEC4'), 'interpolation': 'LINEAR'})
            chans.append({'sampler': len(samps) - 1, 'target': {'node': i, 'path': 'rotation'}})
        pi = self.idx['pelvis']
        if any(np.any(k[2]) for k in keys):
            pp = self.parent.get(pi); Wp = self.W[pp] if pp is not None else np.eye(3)
            tr = np.array([self.T[pi] + Wp.T @ np.array(k[2], float) for k in keys])
            samps.append({'input': ta, 'output': put(tr, 'VEC3'), 'interpolation': 'LINEAR'})
            chans.append({'sampler': len(samps) - 1, 'target': {'node': pi, 'path': 'translation'}})
        self.js['animations'] = [{'name': name, 'channels': chans, 'samplers': samps}]

    def world_m(self, pose, bone):
        """4x4 world matrix of `bone` in `pose` (for attaching props)"""
        lq = self.local_q(pose); chain = []; i = self.idx[bone]
        while i is not None: chain.append(i); i = self.parent.get(i)
        M = np.eye(4)
        for i in reversed(chain):
            L = np.eye(4); L[:3, :3] = m_from_q(lq[i]) if i in lq else self.R[i]
            L[:3, :3] *= np.array(self.js['nodes'][i].get('scale', [1, 1, 1])); L[:3, 3] = self.T[i]; M = M @ L
        return M

    def attach(self, glb_path, bone, Mlocal):
        """merge another GLB's meshes in as a child of `bone`, with local matrix Mlocal"""
        js2, b2 = read_glb(glb_path)
        while len(self.bin) % 4: self.bin.append(0)
        off = len(self.bin); self.bin.extend(b2)
        nv, na, nm, ni, nt, ns, nmesh, nn = (len(self.js.get(k, [])) for k in ('bufferViews', 'accessors', 'materials', 'images', 'textures', 'samplers', 'meshes', 'nodes'))
        for v in js2['bufferViews']: v = dict(v); v['buffer'] = 0; v['byteOffset'] = v.get('byteOffset', 0) + off; self.js['bufferViews'].append(v)
        for a in js2['accessors']: a = dict(a); a['bufferView'] += nv; self.js['accessors'].append(a)
        for im in js2.get('images', []): im = dict(im); im['bufferView'] += nv; self.js.setdefault('images', []).append(im)
        self.js.setdefault('samplers', []).extend(js2.get('samplers', []))
        for t in js2.get('textures', []):
            t = dict(t); t['source'] += ni
            if 'sampler' in t: t['sampler'] += ns
            self.js.setdefault('textures', []).append(t)
        def fix_tex(o):                                             # every *Texture {index} in a material
            if isinstance(o, dict):
                for k, v in o.items():
                    if k.endswith('Texture') and isinstance(v, dict) and 'index' in v: v['index'] += nt
                    fix_tex(v)
        for m in js2.get('materials', []): m = json.loads(json.dumps(m)); fix_tex(m); self.js['materials'].append(m)
        for me in js2['meshes']:
            me = json.loads(json.dumps(me))
            for p in me['primitives']:
                p['attributes'] = {k: v + na for k, v in p['attributes'].items()}
                if 'indices' in p: p['indices'] += na
                if 'material' in p: p['material'] += nm
            self.js['meshes'].append(me)
        for n in js2['nodes']:
            n = json.loads(json.dumps(n))
            if 'mesh' in n: n['mesh'] += nmesh
            if 'children' in n: n['children'] = [c + nn for c in n['children']]
            self.js['nodes'].append(n)
        roots = [r + nn for r in js2['scenes'][js2.get('scene', 0)]['nodes']]
        holder = {'name': 'held_prop', 'matrix': [float(v) for v in Mlocal.T.reshape(-1)], 'children': roots}
        self.js['nodes'].append(holder); self.js['nodes'][self.idx[bone]].setdefault('children', []).append(len(self.js['nodes']) - 1)

    def save(self, path, tex=512):
        self.js['buffers'] = [{'byteLength': len(self.bin)}]
        j = json.dumps(self.js, separators=(',', ':')).encode()
        while len(j) % 4: j += b' '
        while len(self.bin) % 4: self.bin.append(0)
        raw = struct.pack('<III', 0x46546C67, 2, 28 + len(j) + len(self.bin)) + struct.pack('<II', len(j), 0x4E4F534A) + j + struct.pack('<II', len(self.bin), 0x004E4942) + bytes(self.bin)
        tmp = path + '.full.glb'; open(tmp, 'wb').write(raw)
        from shrink_glb import shrink
        n = shrink(tmp, path, tex, 84)
        import os; os.remove(tmp); return n

# ---------------------------------------------------------------- the poses
ARMS_DOWN = [('upperarm_l', Z, -72), ('upperarm_r', Z, 72)]
def sit_base(knee=12, hip=-84):
    return [('thigh_l', X, hip), ('thigh_r', X, hip), ('calf_l', X, knee), ('calf_r', X, knee), ('foot_l', X, -10), ('foot_r', X, -10)]

def clip_sit(rig):
    hands = [('lowerarm_l', Y_, -62), ('lowerarm_r', Y_, 62)]
    base = sit_base() + [('upperarm_l', Z, -58), ('upperarm_r', Z, 58)] + hands + [('spine_01', X, -8)]      # elbows out on the armrests
    def k(t, look=0, breathe=0, tap=0, lean=0):
        return (t, base + [('spine_03', X, breathe), ('neck_01', Y_, look * 0.6), ('head', Y_, look * 0.5), ('head', X, -4 + lean), ('calf_r', X, -tap)], (0, 0, 0))
    keys = [k(0.0), k(1.6, breathe=-2.5), k(3.2), k(4.0, look=28, lean=-3), k(6.0, look=30, breathe=-2.5, lean=-3), k(7.0),
            k(8.6, breathe=-2.5), k(9.4, look=-26), k(11.0, look=-24, breathe=-2.5), k(12.0, tap=14), k(12.3), k(12.6, tap=14), k(12.9), k(14.2, breathe=-2.5)]
    rig.add_clip('sit', keys, 16.0)

GRIP = [(f + '_0%d_r' % j, Z, a) for f in ('index', 'middle', 'ring', 'pinky') for (j, a) in ((1, 55), (2, 65), (3, 45))]
def bar_arm(sip):     # the stein hand: resting at the chest -> up at the mouth (angles found by a reach search, koda #119)
    return [('upperarm_r', X, -50 - 40 * sip), ('upperarm_r', Y_, 30 + 10 * sip), ('lowerarm_r', Y_, 45 - 30 * sip), ('lowerarm_r', X, -15 + 15 * sip)]
def clip_bar(rig):
    rest = sit_base(knee=38, hip=-80) + ARMS_DOWN + [('lowerarm_l', Y_, -70), ('spine_01', X, -4)] + GRIP
    def k(t, sip=0.0, look=0, breathe=0):
        return (t, rest + bar_arm(sip) + [('spine_03', X, breathe), ('neck_01', Y_, look * 0.6 * (1 - sip)), ('head', X, 8 * sip)], (0, 0, 0))
    keys = [k(0.0), k(1.5, breathe=-2.5), k(3.0, look=22), k(4.2, look=22, breathe=-2.5), k(5.2),
            k(6.0, sip=1.0), k(7.4, sip=1.0), k(8.2), k(9.6, breathe=-2.5), k(10.6, look=-20), k(12.0, look=-20, breathe=-2.5)]
    rig.add_clip('bar', keys, 13.0)
    return rest + bar_arm(0)

def clip_walk(rig, period=1.1):
    def k(t, ph):
        s = math.sin(ph); c = math.cos(ph)
        p = ARMS_DOWN + [('thigh_l', X, -26 * s), ('thigh_r', X, 26 * s),
             ('calf_l', X, 32 * max(0, math.sin(ph + 1.2)) + 4), ('calf_r', X, 32 * max(0, math.sin(ph + 1.2 + math.pi)) + 4),
             ('foot_l', X, 10 * c), ('foot_r', X, -10 * c),
             ('upperarm_l', X, 22 * s), ('upperarm_r', X, -22 * s), ('lowerarm_l', Y_, -20), ('lowerarm_r', Y_, 20),
             ('spine_01', Y_, 6 * s), ('spine_03', Y_, -4 * s), ('spine_01', Z, 2.5 * s), ('head', X, -3)]
        return (t, p, (0.0, 0.012 * abs(c) - 0.006, 0.0))
    n = 12
    rig.add_clip('walk', [k(period * i / n, 2 * math.pi * i / n) for i in range(n)], period)

if __name__ == '__main__':
    src, dst, kind = sys.argv[1], sys.argv[2], sys.argv[3]
    rig = Rig(src)
    if kind == 'sit': clip_sit(rig)
    elif kind == 'walk': clip_walk(rig)
    elif kind == 'bar':
        rest = clip_bar(rig)
        Hm = rig.world_m(rest, 'hand_r')                             # the stein, upright in the world in the resting pose, in the palm
        pr = Hm[:3, 3]; Wm = np.eye(4); MUGH = 0.16
        js2, _ = read_glb('/home/claude/spire/out/glb/sp_mug.glb')
        Wm[:3, :3] *= 0.85; Wm[:3, 3] = pr + np.array([-0.032, -0.06, 0.035])
        rig.attach('/home/claude/spire/out/glb/sp_mug.glb', 'hand_r', np.linalg.inv(Hm) @ Wm)
    print(dst, rig.save(dst) // 1024, 'KB')
