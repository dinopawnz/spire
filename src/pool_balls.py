"""Pool balls for the lounge pool tables: a smooth UV sphere per ball with a painted texture (solid or stripe, white number
circles on two sides, glossy) -> out/glb/sp_ball_0..15.glb (0 = the cue ball). Radius R (m)."""
import math, os, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from glb import Mesh, write
OUT = '/home/claude/spire/out/glb/'; R = 0.048
COL = {1: '#f2c21b', 2: '#1f4fb8', 3: '#c8261e', 4: '#5b2a86', 5: '#e8711c', 6: '#1e7a3c', 7: '#7a1f22', 8: '#111111'}
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if not os.path.exists(FONT): FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'

def texture(n, W=512, H=256):
    im = Image.new('RGB', (W, H), '#f4f0e4'); d = ImageDraw.Draw(im)
    if n:
        c = COL[n if n <= 8 else n - 8]
        if n <= 8: d.rectangle([0, 0, W, H], fill=c)
        else: d.rectangle([0, int(H * 0.3), W, int(H * 0.7)], fill=c)
        f = ImageFont.truetype(FONT, 46)
        for cx in (W * 0.25, W * 0.75):                                 # number circles on opposite sides
            rx, ry = 34, 34
            d.ellipse([cx - rx, H / 2 - ry, cx + rx, H / 2 + ry], fill='#f4f0e4')
            t = str(n); bw = d.textlength(t, font=f)
            d.text((cx - bw / 2, H / 2 - 28), t, font=f, fill='#111111')
    else:                                                               # the cue ball: a small red dot like a training ball
        for cx in (W * 0.25, W * 0.75): d.ellipse([cx - 9, H / 2 - 9, cx + 9, H / 2 + 9], fill='#c8261e')
    b = io.BytesIO(); im.save(b, 'PNG'); return b.getvalue()

def ball(n, seg=24, rings=16):
    P, N, U, I = [], [], [], []
    for j in range(rings + 1):
        v = j / rings; th = math.pi * v
        for i in range(seg + 1):
            u = i / seg; ph = 2 * math.pi * u
            nx, ny, nz = math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph)
            P.append([R * nx, R * ny, R * nz]); N.append([nx, ny, nz]); U.append([1 - u, v])
    for j in range(rings):
        for i in range(seg):
            a = j * (seg + 1) + i; b = a + seg + 1
            I += [a, a + 1, b, a + 1, b + 1, b]
    m = Mesh(); m.add('ball', P, N, U, I)
    write(OUT + 'sp_ball_%d.glb' % n, m, {'ball': dict(tex=texture(n), rough=0.12, metal=0.0)})

if __name__ == '__main__':
    for n in range(16): ball(n)
    print('balls written')
