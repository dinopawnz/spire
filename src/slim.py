"""(v24) SLIM - keep the build light enough for 100+ players. Run after the builders (and after meshy_props.py, which rewrites sp_m_*):
    python3 slim.py
1. Built pieces (shell, lounge, hall, lifts, boardwalk, neon): every texture re-encoded at most 1024 px (they were 2048 - the biggest part of
   each download, and the same wood photos are inside several files).
2. Meshy pieces that repeat many times or are big: simplified with gltfpack (-sp -se 0.02: across texture seams, 2% shape error) from the
   full-detail originals kept in out/glb/hi/. Textures and glow are kept.
Needs: npm i gltfpack (in /home/claude/tools)."""
import os, sys, shutil, subprocess
sys.path.insert(0, '/home/claude/spire')
from glb import read_glb
from shrink_glb import shrink

G = '/home/claude/spire/out/glb/'
GP = '/home/claude/tools/node_modules/.bin/gltfpack'
TEX_1024 = ['sp_shell', 'sp_f1_lounge', 'sp_f2_hall', 'sp_f2_vault', 'sp_lift_shaft', 'sp_lift_shaft_g', 'sp_lift_cab', 'sp_boardwalk', 'sp_neon']
TARGET = {'sp_m_armchair': 2400, 'sp_m_sofa': 3200, 'sp_m_cardtable': 2600, 'sp_m_stool': 1200, 'sp_m_ivy': 2400, 'sp_mtree_1': 10000, 'sp_mtree_2': 10000,
          'sp_m_booth': 8000, 'sp_m_pond': 9000, 'sp_m_grotto': 9000, 'sp_m_coffeetable': 1800, 'sp_m_barrel': 1500, 'sp_m_bench': 2000,
          'sp_m_fireplace': 9000, 'sp_m_crag': 9000, 'sp_m_gable': 7000, 'sp_m_doorleaf': 2500, 'sp_m_signframe': 5000, 'sp_m_lectern': 3000,
          'sp_m_bottles': 2500, 'sp_m_glassrack': 2000, 'sp_m_beermug': 1500}

def tris(p):
    js, _ = read_glb(p); return sum(js['accessors'][pr['indices']]['count'] // 3 for m in js['meshes'] for pr in m['primitives'] if 'indices' in pr)

if __name__ == '__main__':
    for f in TEX_1024:
        p = G + f + '.glb'
        if not os.path.exists(p): continue
        a = os.path.getsize(p); shrink(p, p, 1024); print('%-16s %5.1f -> %5.1f MB' % (f, a / 1e6, os.path.getsize(p) / 1e6))
    os.makedirs(G + 'hi', exist_ok=True)
    for f, tgt in TARGET.items():
        src = G + f + '.glb'; hi = G + 'hi/' + f + '.glb'
        if not os.path.exists(src): continue
        if not os.path.exists(hi) or os.path.getmtime(src) > os.path.getmtime(hi) + 5 and tris(src) > tgt * 1.6: shutil.copy(src, hi)   # a fresh full-detail model
        t0 = tris(hi); r = max(0.05, min(1.0, tgt / t0))
        if r >= 0.95: continue
        out = subprocess.run([GP, '-i', hi, '-o', src, '-noq', '-kn', '-km', '-si', '%.3f' % r, '-sp', '-se', '0.02'], capture_output=True, text=True)
        if out.returncode: shutil.copy(hi, src); print('FAIL', f); continue
        print('%-16s %6d -> %6d tris' % (f, t0, tris(src)))
