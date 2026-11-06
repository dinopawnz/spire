"""spectacle pieces: neon falling streaks + coloured light beams (unlit, see-through, glowing)."""
import math
import numpy as np
from PIL import Image
from glb import *
from kit import *
OUT = '/home/claude/spire/out/glb/'
COL = {'t': (0.25, 1.0, 0.85), 'g': (1.0, 0.78, 0.25), 'p': (1.0, 0.35, 0.85), 'b': (0.35, 0.6, 1.0)}
def grad(name, fn, w=8, h=256):
    a = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        v = fn(y / (h - 1)); a[y, :, :3] = 255; a[y, :, 3] = int(255 * v)
    p = TEX + name + '.png'; Image.fromarray(a, 'RGBA').save(p); return p
streak_tex = grad('fx_streak', lambda t: t ** 0.6 * min(1, (1 - t) * 12))          # bright head at the bottom (image bottom), long fading tail up
beam_tex = grad('fx_beam', lambda t: (1 - t) ** 1.8 * 0.9)                       # bright at the base, fades out up the beam
for k, c in COL.items():
    m = Mesh()
    quad(m, 's', 0.14, 7.0, M(T(0, 3.5, 0)), double=True)
    quad(m, 's', 0.14, 7.0, M(T(0, 3.5, 0), Ry(90)), double=True)
    write(OUT + 'sp_streak_%s.glb' % k, m, {'s': dict(tex=streak_tex, color=c + (1.0,), emis=c, emis_strength=2.5, alpha='BLEND', unlit=True, double=True)})
    m = Mesh()
    lathe(m, 'b', [(0.02, 0.0), (1.0, 1.0)], 24)
    write(OUT + 'sp_beam_%s.glb' % k, m, {'b': dict(tex=beam_tex, color=c + (0.55,), emis=c, emis_strength=1.5, alpha='BLEND', unlit=True, double=True)})
print('fx done')

# ---- swamp magic: will-o'-wisps (a glowing core inside soft crossed halos, readable from any side) and faint moonlight shafts
def radial(name):
    n = 128; a = np.zeros((n, n, 4), np.uint8)
    yy, xx = np.mgrid[0:n, 0:n]; d = np.sqrt((xx - n / 2 + 0.5) ** 2 + (yy - n / 2 + 0.5) ** 2) / (n / 2)
    a[..., :3] = 255; a[..., 3] = (np.clip(1 - d, 0, 1) ** 2.2 * 255).astype(np.uint8)
    p = TEX + name + '.png'; Image.fromarray(a, 'RGBA').save(p); return p
halo = radial('fx_halo')
for k, c in (('t', (0.45, 1.0, 0.75)), ('g', (1.0, 0.85, 0.45))):
    m = Mesh()
    sphere(m, 'core', 0.12, 10, 6)
    for ry in (0, 60, 120): quad(m, 'halo', 1.6, 1.6, Ry(ry), double=True)
    quad(m, 'halo', 1.6, 1.6, Rx(90), double=True)
    write(OUT + 'sp_wisp_%s.glb' % k, m, {'core': dict(color=c + (1,), emis=c, emis_strength=3.0, unlit=True),
                                          'halo': dict(tex=halo, color=c + (0.9,), emis=c, emis_strength=2.0, alpha='BLEND', unlit=True, double=True)})
moon_tex = grad('fx_moon', lambda t: 0.07 * min(1, t * 4) * min(1, (1 - t) * 3))      # faint, soft at both ends
m = Mesh(); lathe(m, 'b', [(1.0, 0.0), (0.25, 1.0)], 24)                             # wide at the bottom (on the ground), narrow at the sky end
write(OUT + 'sp_moonbeam.glb', m, {'b': dict(tex=moon_tex, color=(0.75, 0.85, 1.0, 1.0), emis=(0.7, 0.8, 1.0), emis_strength=1.2, alpha='BLEND', unlit=True, double=True)})
print('swamp fx done')
