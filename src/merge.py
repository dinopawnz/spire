"""(v42, owner: "we gotta figure out how to bring the frame rate as high as possible while maintaining as much of the epic look")
MERGE REPEATS: every frame a computer draws each separate object one by one, and ~3,500 of the build's objects were the same few
models placed over and over (lanterns, chains, rings, armchairs, sofas, vines, reeds, windows, railings, dealt cards...). Here all
the copies of one model on one floor are baked into ONE model file (same textures, same look, same place), so the game draws them
in one go. Called by build_html.py on D['sdeco'] (+ the lantern rings) at the very end; replaced entries become one entry each.

Merged files are named  mg_<original>.glb  so the LITE-mode filter (which matches the original names) still finds them.
Not merged: things that move, are clicked, or are too heavy to copy (big trees, booths: the file would get huge for little gain)."""
import json, math, os, struct, sys
import numpy as np
sys.path.insert(0, '/home/claude/spire')
from glb import read_glb

G = '/home/claude/spire/out/glb/'
MAX_TRIS_EACH = 3600          # copy only models up to this size per instance
MAX_TRIS_FILE = 160000        # split very big groups into several files
MIN_COUNT = 3
BUDGET_MB = 15.0             # extra download allowed for merging
MIN_SCORE = 15.0            # objects saved per extra MB, at least (windows, posts, reeds, chairs, vines: too costly for what they save)
SKIP = ('sp_mtree', 'sp_m_booth', 'sp_m_pond', 'sp_m_grotto', 'sp_m_fireplace', 'sp_m_crag', 'sp_m_gable', 'sp_shell', 'sp_f1_', 'sp_f2_')

def _local(n):
    if 'matrix' in n: return np.array(n['matrix'], float).reshape(4, 4).T
    x, y, z, w = n.get('rotation', [0, 0, 0, 1])
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    L = np.eye(4); L[:3, :3] = R * np.array(n.get('scale', [1, 1, 1])); L[:3, 3] = n.get('translation', [0, 0, 0]); return L

class Src:
    """a model file, its primitives baked into model space: [(material, {attr: array}, indices)]"""
    def __init__(self, path):
        self.js, self.b = read_glb(path); js = self.js; self.prims = []
        def read(i):
            a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]; o = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
            n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
            dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8, 5122: np.int16, 5120: np.int8}[a['componentType']]
            isz = np.dtype(dt).itemsize; st = bv.get('byteStride') or n * isz
            raw = np.frombuffer(self.b, np.uint8, st * (a['count'] - 1) + n * isz, o)
            arr = np.lib.stride_tricks.as_strided(raw, (a['count'], n * isz), (st, 1)).copy().view(dt).reshape(a['count'], n).astype(np.float64 if dt != np.uint32 else np.uint32)
            if a.get('normalized') and dt in (np.uint8, np.uint16, np.int8, np.int16):
                arr = arr / float(np.iinfo(dt).max)
            return arr
        def walk(i, Mp):
            n = js['nodes'][i]; Mw = Mp @ _local(n)
            if 'mesh' in n and 'skin' not in n:
                for p in js['meshes'][n['mesh']]['primitives']:
                    if p.get('mode', 4) != 4: continue
                    at = {}
                    for k in ('POSITION', 'NORMAL', 'TEXCOORD_0', 'TEXCOORD_1', 'COLOR_0'):
                        if k in p['attributes']: at[k] = read(p['attributes'][k])
                    P = at['POSITION']; at['POSITION'] = (np.c_[P, np.ones(len(P))] @ Mw.T)[:, :3]
                    if 'NORMAL' in at: at['NORMAL'] = at['NORMAL'] @ np.linalg.inv(Mw[:3, :3])
                    idx = read(p['indices']).reshape(-1).astype(np.int64) if 'indices' in p else np.arange(len(P))
                    self.prims.append((p.get('material', -1), at, idx))
            for c in n.get('children', []): walk(c, Mw)
        for r in js['scenes'][js.get('scene', 0)]['nodes']: walk(r, np.eye(4))
        self.tris = sum(len(i) // 3 for _, _, i in self.prims)
        self.animated = bool(js.get('animations')) or any('skin' in n for n in js['nodes'])

def xform(x, y, z, ry, sx, sy, sz):
    c, s = math.cos(math.radians(ry)), math.sin(math.radians(ry))
    M = np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], float)
    M[:3, :3] = M[:3, :3] @ np.diag([sx, sy, sz]); M[:3, 3] = [x, y, z]; return M

def write(src, mats, out):
    """bake every instance matrix of `src` into one GLB at `out`"""
    js = src.js; groups = {}
    for (mi, at, idx) in src.prims:
        key = (mi, tuple(sorted(at)))
        groups.setdefault(key, []).append((at, idx))
    binb = bytearray(); bvs, accs = [], []
    def put(arr, typ, comp, target=None, mm=False):
        data = np.ascontiguousarray(arr).tobytes()
        while len(binb) % 4: binb.append(0)
        bv = {'buffer': 0, 'byteOffset': len(binb), 'byteLength': len(data)}
        if target: bv['target'] = target
        bvs.append(bv); binb.extend(data)
        a = {'bufferView': len(bvs) - 1, 'componentType': comp, 'count': len(arr), 'type': typ}
        if mm: a['min'] = [float(v) for v in arr.min(0)]; a['max'] = [float(v) for v in arr.max(0)]
        accs.append(a); return len(accs) - 1
    prims_out = []
    for (mi, keys), parts in groups.items():
        cols = {k: [] for k in keys}; idxs = []; base = 0
        for M in mats:
            Ni = np.linalg.inv(M[:3, :3]).T
            for at, idx in parts:
                n = len(at['POSITION'])
                for k in keys:
                    v = at[k]
                    if k == 'POSITION': v = (np.c_[v, np.ones(n)] @ M.T)[:, :3]
                    elif k == 'NORMAL':
                        v = v @ Ni.T; v = v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-12)
                    cols[k].append(v)
                idxs.append(idx + base); base += n
        attrs = {}
        for k in keys:
            v = np.concatenate(cols[k]).astype(np.float32)
            typ = {1: 'SCALAR', 2: 'VEC2', 3: 'VEC3', 4: 'VEC4'}[v.shape[1]]
            attrs[k] = put(v, typ, 5126, 34962, mm=(k == 'POSITION'))
        ind = np.concatenate(idxs)
        ind = ind.astype(np.uint16) if base < 65536 else ind.astype(np.uint32)
        pr = {'attributes': attrs, 'indices': put(ind.reshape(-1, 1), 'SCALAR', 5123 if ind.dtype == np.uint16 else 5125, 34963)}
        if mi >= 0: pr['material'] = mi
        prims_out.append(pr)
    # textures, images, samplers, materials: copied as they are
    out_js = {'asset': {'version': '2.0', 'generator': 'spire merge.py'}, 'scene': 0, 'scenes': [{'nodes': [0]}],
              'nodes': [{'mesh': 0, 'name': os.path.basename(out)[:-4]}], 'meshes': [{'primitives': prims_out}]}
    for k in ('materials', 'textures', 'samplers', 'extensionsUsed', 'extensionsRequired'):
        if js.get(k): out_js[k] = json.loads(json.dumps(js[k]))
    if js.get('images'):
        ims = []
        for im in js['images']:
            im = dict(im)
            if 'bufferView' in im:
                v = js['bufferViews'][im['bufferView']]; d = src.b[v.get('byteOffset', 0): v.get('byteOffset', 0) + v['byteLength']]
                while len(binb) % 4: binb.append(0)
                bvs.append({'buffer': 0, 'byteOffset': len(binb), 'byteLength': len(d)}); binb.extend(d); im['bufferView'] = len(bvs) - 1
            ims.append(im)
        out_js['images'] = ims
    if out_js.get('extensionsRequired'):
        out_js['extensionsRequired'] = [e for e in out_js['extensionsRequired'] if e not in ('KHR_mesh_quantization', 'EXT_meshopt_compression', 'KHR_draco_mesh_compression')] or None
        if not out_js['extensionsRequired']: del out_js['extensionsRequired']
    out_js['bufferViews'] = bvs; out_js['accessors'] = accs; out_js['buffers'] = [{'byteLength': len(binb)}]
    j = json.dumps(out_js, separators=(',', ':')).encode()
    while len(j) % 4: j += b' '
    while len(binb) % 4: binb.append(0)
    open(out, 'wb').write(struct.pack('<III', 0x46546C67, 2, 28 + len(j) + len(binb)) + struct.pack('<II', len(j), 0x4E4F534A) + j
                          + struct.pack('<II', len(binb), 0x004E4942) + bytes(binb))

def zone(x, y, z, L):
    FL = L['FL']
    if abs(x) > L['X1'] + 1 or abs(z) > L['Z1'] + 1 or y < FL['lounge'] - 1.5: return 'out'
    for name, top in (('f1', FL['hall']), ('f2', FL['gallery']), ('gal', L['f3']), ('f3', L['f4']), ('f4', L['roof'])):
        if y < top - 0.3: return name
    return 'roof'

def merge_all(D, L, verbose=True):
    """D['sdeco'] entries [file, x, y, z, ry, s(, syr)] -> merged files; D['chand*'] lantern rings too. Returns a report."""
    entries = list(D.get('sdeco', []))
    rings = [['sp_lantern_ring', c[0], L['f2'] - 0.5, c[1], 0.0, c[2] if len(c) > 2 else 1.0] for c in D.get('chand', [])] + \
            [['sp_lantern_ring', c[0], L['gallery'] - 0.5, c[1], 0.0, c[2] if len(c) > 2 else 1.0] for c in D.get('chand2', [])] + \
            [['sp_lantern_ring', c[0], L['f4'] - 0.5, c[1], 0.0, c[2] if len(c) > 2 else 1.0] for c in D.get('chand3', [])]
    entries += rings
    # one merged file per MODEL (all floors together: the textures are stored once). Merging costs download size (every copy's
    # shape is stored), so the models are ranked by objects saved per MB and taken until BUDGET_MB is used up.
    by = {}
    for e in entries: by.setdefault(e[0], []).append(e)
    cache, cands, keep, made, report = {}, [], [], [], []
    for f, es in by.items():
        p = G + f + '.glb'
        if len(es) < MIN_COUNT or f.startswith(SKIP) or not os.path.exists(p): keep += es; continue
        if f not in cache: cache[f] = Src(p)
        src = cache[f]
        if src.animated or not 0 < src.tris <= MAX_TRIS_EACH: keep += es; continue
        nv = sum(len(at['POSITION']) for _, at, _ in src.prims)
        vb = sum(len(at['POSITION']) * (4 * sum(v.shape[1] for v in at.values())) + len(ix) * 2 for _, at, ix in src.prims)
        tex = sum(src.js['bufferViews'][im['bufferView']]['byteLength'] for im in src.js.get('images', []) if 'bufferView' in im)
        cost = (vb * len(es) + tex) / 1e6; saved = (len(es) - 1) * len(src.prims)
        cands.append((saved / max(cost, 0.05), f, es, src, cost, saved))
    cands.sort(key=lambda c: -c[0]); used = 0.0
    for score, f, es, src, cost, saved in cands:
        if used + cost > BUDGET_MB or score < MIN_SCORE: keep += es; continue
        used += cost
        per = max(1, MAX_TRIS_FILE // src.tris); chunks = [es[i:i + per] for i in range(0, len(es), per)]
        for k, ch in enumerate(chunks):
            name = 'mg_%s%s' % (f, '' if len(chunks) == 1 else '_%d' % k)
            mats = [xform(e[1], e[2], e[3], e[4], e[5], e[5] * (e[6] if len(e) > 6 and e[6] else 1), e[5]) for e in ch]
            write(src, mats, G + name + '.glb'); made.append([name, 0, 0, 0, 0, 1])
            report.append((name, len(ch), src.tris * len(ch), len(src.prims), os.path.getsize(G + name + '.glb')))
    for score, f, es, src, cost, saved in cands:
        if verbose: print('   %-24s x%-4d saves %4d objects for %5.1f MB  (%5.1f/MB) %s' % (f, len(es), saved, cost, score, 'MERGED' if any(m[0].startswith('mg_' + f) for m in made) else ''))
    D['sdeco'] = keep + made
    D['chand'], D['chand2'], D['chand3'] = [], [], []
    if verbose:
        n_in = sum(r[1] for r in report)
        print('merge: %d copies -> %d files (%d pieces), +%.1f MB' % (n_in, len(report), sum(r[3] for r in report), sum(r[4] for r in report) / 1e6))
    return report

if __name__ == '__main__':
    print('run from build_html.py')
