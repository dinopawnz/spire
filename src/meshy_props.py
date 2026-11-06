"""Prepare Meshy models for the build: /home/claude/meshy/models/<name>.glb -> out/glb/sp_m_<name>.glb
(textures shrunk: 2048 px for big hero pieces, 1024 for furniture; glowing mushrooms/embers where it fits),
and out/glb/meshy_meta.json = {name: [min xyz, max xyz]} (model space, node transforms applied) for build_lounge.mp()."""
import json, os, glob, struct, sys
import numpy as np
sys.path.insert(0, '/home/claude/spire')
from glb import read_glb
from shrink_glb import shrink
from glow_mask import glow

SRC = '/home/claude/meshy/models/'; OUT = '/home/claude/spire/out/glb/'
BIG = {'photoarch': 2048, 'grotto': 2048, 'pond': 2048, 'booth': 2048, 'fireplace': 2048, 'tome': 2048, 'island': 2048, 'cliff': 2048, 'bonsai': 2048, 'crag': 2048, 'vines': 1024, 'ivy': 1024, 'gable': 2048, 'bottles': 1024, 'glassrack': 1024, 'beermug': 512, 'frogbull': 512, 'frogtree': 512, 'dragonfly': 512, 'turtle': 1024}
GLOW = {'pond': 0.9, 'fireplace': 1.2, 'lanternpost': 1.4, 'crystals': ('teal', 2.2), 'tome': ('gold', 1.6), 'signframe': ('gold', 0.5), 'window': ('pane', 2.2), 'gable': ('pane', 1.6), 'floatlantern': ('warm', 1.8), 'hanglantern': ('pane', 3.0), 'firepit': ('warm', 1.6)}

def bounds(path):
    js, _ = read_glb(path)
    nodes = js.get('nodes', []); mn = np.full(3, 1e9); mx = np.full(3, -1e9)
    def mat(n):
        if 'matrix' in n: return np.array(n['matrix']).reshape(4, 4).T
        m = np.eye(4)
        if 'scale' in n: m = np.diag(list(n['scale']) + [1]) @ m
        if 'rotation' in n:
            x, y, z, w = n['rotation']
            R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
            r4 = np.eye(4); r4[:3, :3] = R; m = r4 @ m
        if 'translation' in n: t = np.eye(4); t[:3, 3] = n['translation']; m = t @ m
        return m
    def walk(i, parent):
        nonlocal mn, mx
        n = nodes[i]; m = parent @ mat(n)
        if 'mesh' in n:
            for p in js['meshes'][n['mesh']]['primitives']:
                a = js['accessors'][p['attributes']['POSITION']]
                lo, hi = np.array(a['min']), np.array(a['max'])
                corners = np.array([[x, y, z, 1] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) @ m.T
                mn = np.minimum(mn, corners[:, :3].min(0)); mx = np.maximum(mx, corners[:, :3].max(0))
        for c in n.get('children', []): walk(c, m)
    for r in js['scenes'][js.get('scene', 0)]['nodes']: walk(r, np.eye(4))
    return mn.tolist(), mx.tolist()

meta_p = OUT + 'meshy_meta.json'
meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
only = sys.argv[1:]
for f in sorted(glob.glob(SRC + '*.glb')):
    name = os.path.basename(f)[:-4]
    if only and name not in only: continue
    dst = OUT + 'sp_m_' + name + '.glb'
    if os.path.exists(dst) and name in meta and os.path.getmtime(dst) > os.path.getmtime(f) and not only: continue
    shrink(f, dst, BIG.get(name, 1024))
    if name in GLOW:
        import glow_mask; g = GLOW[name]; glow_mask.MODE, st = (g[0], g[1]) if isinstance(g, tuple) else ('warm', g)
        glow_mask.glow(dst, dst, st)
    meta[name] = bounds(dst)
    print(name, os.path.getsize(dst) // 1024, 'KB', [round(v, 2) for v in meta[name][0]], [round(v, 2) for v in meta[name][1]])
json.dump(meta, open(meta_p, 'w'))
