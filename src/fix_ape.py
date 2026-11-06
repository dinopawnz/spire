"""Put the original multi-material look back on Meshy's rigged + animated copy of the user's ape (#5413).
Meshy kept the original UVs but merged every part into one material (the tie-dye shirt). We find, for each triangle,
which original part it came from (nearest original vertex after undoing Meshy's rescale), split the one primitive into
one primitive per part, and copy the original materials + textures in.
    python3 fix_ape.py out/meshy/operator_anim.glb /home/claude/apes/ape_5413_small.glb out/glb/npc_operator.glb"""
import sys, json, struct
import numpy as np
from scipy.spatial import cKDTree
from glb import read_glb

def acc(js, b, i):
    a = js['accessors'][i]; v = js['bufferViews'][a['bufferView']]
    n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
    ct = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a['componentType']]
    sz = np.dtype(ct).itemsize; st = v.get('byteStride') or n * sz; off = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    raw = np.frombuffer(b, np.uint8, st * (a['count'] - 1) + n * sz, off)
    out = np.lib.stride_tricks.as_strided(raw, (a['count'], n * sz), (st, 1)).copy().view(ct).reshape(a['count'], n)
    return out if n > 1 else out[:, 0]

def main(meshy_path, orig_path, out_path):
    m, mb = read_glb(meshy_path); o, ob = read_glb(orig_path)
    # original parts (positions, uvs, material)
    OP, OU, OM = [], [], []
    for me in o['meshes']:
        for p in me['primitives']:
            P = acc(o, ob, p['attributes']['POSITION']); OP.append(P); OU.append(acc(o, ob, p['attributes']['TEXCOORD_0'])); OM.append(np.full(len(P), p['material']))
    OP = np.vstack(OP); OU = np.vstack(OU); OM = np.concatenate(OM)
    prim = m['meshes'][0]['primitives'][0]
    MP = acc(m, mb, prim['attributes']['POSITION']); MU = acc(m, mb, prim['attributes']['TEXCOORD_0']); MI = acc(m, mb, prim['indices']).reshape(-1, 3)
    # undo Meshy's rescale / recentre: fit per-axis scale + offset from the bounding boxes
    s = (MP.max(0) - MP.min(0)) / (OP.max(0) - OP.min(0)); s[:] = s.mean()
    off = MP.min(0) - OP.min(0) * s
    A = OP * s + off
    # match on position AND uv (parts touch each other, the uv decides)
    tree = cKDTree(np.c_[A, OU * 0.5])
    d, idx = tree.query(np.c_[MP, MU * 0.5])
    print('match distance: median %.5f  95%% %.5f  max %.4f' % (np.median(d), np.percentile(d, 95), d.max()))
    vpart = OM[idx]
    tri_part = np.array([np.bincount(vpart[t], minlength=OM.max() + 1).argmax() for t in MI])
    # ---- rebuild: copy original images / textures / samplers / materials into the meshy file
    bin_ = bytearray(mb)
    def add_view(data, target=None):
        while len(bin_) % 4: bin_.append(0)
        v = {'buffer': 0, 'byteOffset': len(bin_), 'byteLength': len(data)}
        if target: v['target'] = target
        bin_.extend(data); m['bufferViews'].append(v); return len(m['bufferViews']) - 1
    img0 = len(m.get('images', [])); m.setdefault('images', [])
    for im in o.get('images', []):
        v = o['bufferViews'][im['bufferView']]; data = ob[v.get('byteOffset', 0): v.get('byteOffset', 0) + v['byteLength']]
        m['images'].append({'bufferView': add_view(data), 'mimeType': im['mimeType']})
    smp0 = len(m.get('samplers', [])); m.setdefault('samplers', []).extend(o.get('samplers', [{}]))
    tex0 = len(m.get('textures', [])); m.setdefault('textures', [])
    for t in o.get('textures', []):
        t = dict(t); t['source'] = t['source'] + img0
        if 'sampler' in t: t['sampler'] += smp0
        m['textures'].append(t)
    def remap(x):
        if isinstance(x, dict):
            return {k: (v + tex0 if k == 'index' and isinstance(v, int) else remap(v)) for k, v in x.items()}
        if isinstance(x, list): return [remap(v) for v in x]
        return x
    mat0 = len(m['materials'])
    for mat in o['materials']: m['materials'].append(remap(mat))
    if o.get('extensionsUsed'): m['extensionsUsed'] = sorted(set(m.get('extensionsUsed', [])) | set(o['extensionsUsed']))
    prims = []
    for part in np.unique(tri_part):
        I = MI[tri_part == part].reshape(-1).astype(np.uint32)
        vi = add_view(I.tobytes(), 34963)
        m['accessors'].append({'bufferView': vi, 'componentType': 5125, 'count': int(len(I)), 'type': 'SCALAR'})
        p = dict(prim); p['indices'] = len(m['accessors']) - 1; p['material'] = mat0 + int(part); prims.append(p)
        print('  part %-28s %6d tris' % (o['materials'][part]['name'], len(I) // 3))
    m['meshes'][0]['primitives'] = prims
    while len(bin_) % 4: bin_.append(0)
    m['buffers'] = [{'byteLength': len(bin_)}]
    j = json.dumps(m, separators=(',', ':')).encode()
    while len(j) % 4: j += b' '
    open(out_path, 'wb').write(struct.pack('<III', 0x46546C67, 2, 28 + len(j) + len(bin_)) + struct.pack('<II', len(j), 0x4E4F534A) + j
                               + struct.pack('<II', len(bin_), 0x004E4942) + bytes(bin_))
    print('wrote', out_path, len(bin_) // 1024, 'KB')

if __name__ == '__main__':
    main(*sys.argv[1:4])
