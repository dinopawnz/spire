"""Split each NPC's multi-clip GLB into tiny animation-only GLBs (skeleton nodes + one clip, no mesh / textures),
named npc_<key>_<clip>.glb with clip = idle / talk / a3 / a4 / a5 in the file's clip order, for MML's m-model anim="...".
The full npc_<key>.glb stays the visible model (its first clip is the idle)."""
import json, struct, sys, os
import numpy as np
from glb import read_glb

NAMES = ['idle', 'talk', 'a3', 'a4', 'a5']

def split(src, out_prefix):
    js, b = read_glb(src); out = []
    for k, an in enumerate(js.get('animations', [])):
        j = {'asset': js['asset'], 'scene': 0, 'scenes': js['scenes'], 'nodes': [], 'animations': []}
        for n in js['nodes']:
            n2 = {kk: vv for kk, vv in n.items() if kk not in ('mesh', 'skin', 'camera')}; j['nodes'].append(n2)
        acc_map = {}; accs = []; views = []; buf = bytearray()
        def take(ai):
            if ai in acc_map: return acc_map[ai]
            a = dict(js['accessors'][ai]); v = js['bufferViews'][a['bufferView']]
            n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]; sz = {5126: 4, 5123: 2, 5125: 4, 5121: 1}[a['componentType']]
            st = v.get('byteStride') or n * sz; off = v.get('byteOffset', 0) + a.get('byteOffset', 0)
            raw = b''.join(b[off + i * st: off + i * st + n * sz] for i in range(a['count'])) if st != n * sz else b[off: off + a['count'] * n * sz]
            while len(buf) % 4: buf.append(0)
            views.append({'buffer': 0, 'byteOffset': len(buf), 'byteLength': len(raw)}); buf.extend(raw)
            a['bufferView'] = len(views) - 1; a.pop('byteOffset', None); accs.append(a); acc_map[ai] = len(accs) - 1; return acc_map[ai]
        an2 = {'name': an.get('name', NAMES[k]), 'channels': an['channels'], 'samplers': [dict(s, input=take(s['input']), output=take(s['output'])) for s in an['samplers']]}
        j['animations'] = [an2]; j['accessors'] = accs; j['bufferViews'] = views
        while len(buf) % 4: buf.append(0)
        j['buffers'] = [{'byteLength': len(buf)}]
        js_b = json.dumps(j, separators=(',', ':')).encode()
        while len(js_b) % 4: js_b += b' '
        p = '%s_%s.glb' % (out_prefix, NAMES[k])
        open(p, 'wb').write(struct.pack('<III', 0x46546C67, 2, 28 + len(js_b) + len(buf)) + struct.pack('<II', len(js_b), 0x4E4F534A) + js_b + struct.pack('<II', len(buf), 0x004E4942) + bytes(buf))
        out.append((os.path.basename(p), an.get('name'), round(max(js['accessors'][s['input']]['max'][0] for s in an['samplers']), 2), len(buf) // 1024))
    return out

if __name__ == '__main__':
    meta = {}
    for key in ['operator', 'ferryman', 'barkeep', 'gator', 'skipper', 'appraiser', 'dealer']:
        r = split('/home/claude/spire/out/glb/npc_%s.glb' % key, '/home/claude/spire/out/glb/npc_%s' % key)
        meta[key] = {NAMES[i]: [x[1], x[2]] for i, x in enumerate(r)}
        print(key, r)
    json.dump(meta, open('/home/claude/spire/out/npc_clips.json', 'w'))
