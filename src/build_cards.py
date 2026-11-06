"""giant floating Mudwater cards for the galaxy: gc_001..120.glb - the real card art on the front, the card back behind,
a gold rim and a soft glow. 1 m tall (scaled up in the game). Textures shrunk to 512 px tall to keep downloads light."""
from PIL import Image
from glb import *
from kit import *
SRC = '/home/claude/mudwater_repo/'; SM = '/home/claude/spire/out/cards_small/'; OUT = '/home/claude/spire/out/glb/'
H = 1.0; W = H * 720 / 1000
def small(name):
    p = SM + name
    Image.open(SRC + name).convert('RGB').resize((369, 512), Image.LANCZOS).save(p, quality=86)
    return p
back = small('mwc_back.jpg')
for n in range(1, 121):
    front = small('mwc_%03d.jpg' % n)
    m = Mesh()
    quad(m, 'front', W, H, T(0, 0, 0.012))
    quad(m, 'back', W, H, M(T(0, 0, -0.012), Ry(180)))
    for (sx, sy, w, h) in ((0, H / 2 + 0.006, W + 0.012, 0.012), (0, -H / 2 - 0.006, W + 0.012, 0.012), (W / 2 + 0.006, 0, 0.012, H), (-W / 2 - 0.006, 0, 0.012, H)):
        box(m, 'rim', w, h, 0.03, m=T(sx, sy, 0))          # a thin gold edge, like the real card's border
    mats = {'front': dict(tex=front, emis_tex=front, emis=(0.55, 0.55, 0.55), rough=0.4),
            'back': dict(tex=back, emis_tex=back, emis=(0.45, 0.45, 0.45), rough=0.5),
            'rim': dict(color=(1.0, 0.8, 0.35, 1), metal=1.0, rough=0.25, emis=(0.5, 0.35, 0.08)),
            'glow': dict(color=(0.55, 1.0, 0.85, 0.22), emis=(0.4, 0.9, 0.75), alpha='BLEND', unlit=True, double=True)}
    write(OUT + 'gc_%03d.glb' % n, m, mats)
print('cards done')
