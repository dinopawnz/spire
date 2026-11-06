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
# (v42, owner: "make each floating card one object instead of 3") the art, the back and the gold edge now share ONE picture
# (front | back | a strip of gold), so each card is a single piece to draw instead of three
AW = 768; G0, G1 = 742 / AW, 766 / AW
def edge_box(m, w, h, d, at):
    for (mm, fw, fh) in ((M(at, T(0, 0, d / 2)), w, h), (M(at, T(0, 0, -d / 2), Ry(180)), w, h), (M(at, T(w / 2, 0, 0), Ry(90)), d, h),
                         (M(at, T(-w / 2, 0, 0), Ry(-90)), d, h), (M(at, T(0, h / 2, 0), Rx(-90)), w, d), (M(at, T(0, -h / 2, 0), Rx(90)), w, d)):
        quad(m, 'card', fw, fh, mm, uv=(G0, 0.3, G1, 0.7))
bimg = Image.open(back)
for n in range(1, 121):
    front = small('mwc_%03d.jpg' % n)
    at = Image.new('RGB', (AW, 512), (255, 204, 89))
    at.paste(Image.open(front), (0, 0)); at.paste(bimg, (369, 0))
    ap = SM + 'gca_%03d.jpg' % n; at.save(ap, quality=86)
    m = Mesh()
    quad(m, 'card', W, H, T(0, 0, 0.012), uv=(0, 0, 369 / AW, 1))
    quad(m, 'card', W, H, M(T(0, 0, -0.012), Ry(180)), uv=(369 / AW, 0, 738 / AW, 1))
    for (sx, sy, w, h) in ((0, H / 2 + 0.006, W + 0.012, 0.012), (0, -H / 2 - 0.006, W + 0.012, 0.012), (W / 2 + 0.006, 0, 0.012, H), (-W / 2 - 0.006, 0, 0.012, H)):
        edge_box(m, w, h, 0.03, T(sx, sy, 0))          # a thin gold edge, like the real card's border
    mats = {'card': dict(tex=ap, emis_tex=ap, emis=(0.52, 0.52, 0.52), rough=0.42, metal=0.15)}
    write(OUT + 'gc_%03d.glb' % n, m, mats)
print('cards done')
