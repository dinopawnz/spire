import json, numpy as np, math, sys
from glb import read_glb
F2 = json.load(open('out/f2_layout.json'))
def tris(path):
    js, binb = read_glb(path); out = []
    def acc(i):
        a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
        n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
        dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a['componentType']]
        off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
        arr = np.frombuffer(binb, dt, a['count'] * n, off)
        return arr.reshape(-1, n) if n > 1 else arr
    for m in js['meshes']:
        for p in m['primitives']:
            P = acc(p['attributes']['POSITION']); I = acc(p['indices']).astype(int); out.append(P[I.reshape(-1, 3)])
    return np.concatenate(out)
for key, hw, hh in (('hall', 0.55, 0.77), ('vault', 0.55, 0.77)):
    slots = F2[key]
    for f in sys.argv[1:]:
        T = tris(f); hits = 0
        for s in slots:
            a = math.radians(s['ry']); n = np.array([math.sin(a), 0, math.cos(a)]); u = np.array([math.cos(a), 0, -math.sin(a)])
            # any vertex of a triangle inside the picture rectangle and within 8 cm behind .. 60 cm in front
            V = T.reshape(-1, 3) - np.array([s['x'], s['y'], s['z']])
            dn = V @ n; du = V @ u; dy = V[:, 1]
            m = (dn > -0.08) & (dn < 0.6) & (np.abs(du) < hw) & (np.abs(dy) < hh)
            if m.any(): hits += 1
        print(key, f.split('/')[-1], 'portraits touched:', hits, '/', len(slots))
