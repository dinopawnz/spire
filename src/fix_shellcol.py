"""(v55, owner: "fix the portrait frames but make sure for 100 percent certainty that they remain clickable") the shell's invisible
wall round the two stair towers (x = +-51.675..52.125, z -9.5..9.5) has its hall-side face 7 cm IN FRONT of the portraits hung on the
tower walls (x = +-51.74), so it caught their clicks (v48 had moved those 48 pictures 15 cm off their frames to get round it). This moves
that face 12 cm BEHIND the portraits (to x = +-51.86) on the boxes that span the Hall of Fakes floor (y 10.5..32), keeping the rest.
Run after build_rect_v9.py (which writes sp_shell_col.glb):   python3 fix_shellcol.py out/glb/sp_shell_col.glb"""
import sys
import numpy as np
p = sys.argv[1]
b = bytearray(open(p, 'rb').read())
import json, struct
n = struct.unpack('<I', b[12:16])[0]; js = json.loads(b[20:20 + n]); bin0 = 20 + n + 8
pr = js['meshes'][0]['primitives'][0]; a = js['accessors'][pr['attributes']['POSITION']]; bv = js['bufferViews'][a['bufferView']]
off = bin0 + bv.get('byteOffset', 0) + a.get('byteOffset', 0)
V = np.frombuffer(b, np.float32, a['count'] * 3, off).reshape(-1, 3).copy()
moved = 0
for i in range(len(V) // 24):
    B = V[i * 24:(i + 1) * 24]
    lo, hi = B.min(0), B.max(0)
    if not (abs(abs(lo[0] if lo[0] > 0 else hi[0]) - 51.675) < 0.002 and abs(lo[0]) > 51 and abs(hi[0]) > 51): continue
    if hi[1] <= 10.5 or lo[1] >= 32 or lo[2] < -9.6 or hi[2] > 9.6: continue
    sel = np.abs(np.abs(B[:, 0]) - 51.675) < 0.002
    B[sel, 0] = np.sign(B[sel, 0]) * 51.86; moved += 1
V_ = V.astype(np.float32).tobytes(); b[off:off + len(V_)] = V_
# keep the accessor min/max honest
open(p, 'wb').write(b)
print('shell collider: moved the face of %d boxes behind the stair-tower portraits' % moved)
