"""(v54, owner: "what is this weird thing below the piano") the stage piano model (from the castle build) has a slanted board hanging
under its body down to the floor (part of its wood mesh). This removes every wood triangle that sits below the piano's body (the
legs are a different material and stay) by turning those triangles into empty ones (same file layout, nothing else changes).
   python3 fix_piano.py out/glb/sp_band_piano.glb"""
import json, struct, sys
import numpy as np
p = sys.argv[1]
b = bytearray(open(p, 'rb').read()); n = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + n]); bin0 = 20 + n + 8
def view(i, dt, comp):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]; o = bin0 + bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(b, dt, a['count'] * comp, o).reshape(-1, comp) if comp > 1 else np.frombuffer(b, dt, a['count'], o), o
dropped = 0
for m in j['meshes']:
    for pr in m['primitives']:
        if j['materials'][pr['material']].get('name', '') != 'floor3_white_wood' and m.get('name') != 'floor3_white_wood': continue
        P, _ = view(pr['attributes']['POSITION'], np.float32, 3)
        ia = j['accessors'][pr['indices']]; dt = {5123: np.uint16, 5125: np.uint32}[ia['componentType']]
        I, off = view(pr['indices'], dt, 1); I = I.copy().reshape(-1, 3)
        low = P[I][:, :, 1].max(1) < 0.66                    # the whole triangle is below the body
        dropped += int(low.sum()); I[low] = I[low][:, :1]
        b[off:off + I.nbytes] = I.astype(dt).tobytes()
open(p, 'wb').write(b)
print('piano: removed %d triangles of the board under the body' % dropped)
