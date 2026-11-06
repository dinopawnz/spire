"""the REFERENCE PILLARS: what the real card looks like, on all four sides, so players know what to hunt for.
sp_ref_founder.glb : Hall of Fakes floor centre - the real #62 The Founder, big, in gilt frames, plaque: THE REAL ONE / FIND ITS TWIN ON THE STAIRS
sp_ref_flag.glb    : on the vault's plinth - the real #100 Black Flag for the finalists (smaller)
The card images are the untouched originals (the forgery press leaves the real one exactly like this)."""
import math, sys
from PIL import Image, ImageDraw, ImageFont
sys.argv = ['x']
from glb import *
from kit import *
MW = '/home/claude/dinopawnz/mudwater/'
TMP = '/home/claude/spire/out/sprite_png/'
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'; INTERB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
def lora(n):
    f = ImageFont.truetype(LORA, n)
    try: f.set_variation_by_name('Bold')
    except Exception: pass
    return f
def plaque(path, l1, l2):
    W, H = 1400, 330
    img = Image.open(TEX + 'wood_dark.jpg').convert('RGB').resize((W, W)).crop((0, 0, W, H)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((16, 16, W - 16, H - 16), 24, outline=(214, 160, 70), width=8)
    f = lora(112); tw = d.textlength(l1, font=f); d.text(((W - tw) / 2 + 4, 44 + 4), l1, font=f, fill=(20, 10, 4)); d.text(((W - tw) / 2, 44), l1, font=f, fill=(246, 210, 120))
    f2 = ImageFont.truetype(INTERB, 54); tw = d.textlength(l2, font=f2); d.text(((W - tw) / 2, 212), l2, font=f2, fill=(150, 228, 205))
    img.save(path, quality=90); return path
def gilt(m, w, h, mm, bw=0.12):
    for sx in (-1, 1): bevel_box(m, 'gold', bw, h + 2 * bw, 0.1, 0.03, m=M(mm, T(sx * (w / 2 + bw / 2), 0, 0.03)))
    for sy in (-1, 1): bevel_box(m, 'gold', w + 2 * bw, bw, 0.1, 0.03, m=M(mm, T(0, sy * (h / 2 + bw / 2), 0.03)))
    for sx in (-1, 1):
        for sy in (-1, 1): lathe(m, 'gold', [(0.0, 0), (0.07, 0), (0.05, 0.04), (0.0, 0.07)], 8, m=M(mm, T(sx * (w / 2 + bw / 2), sy * (h / 2 + bw / 2), 0.08), Rx(90)))
def pillar(card, out, cw, l1, l2, H=None):
    ch = cw * 1000 / 720; W = cw + 0.55; H = H or ch + 1.5
    m = Mesh(); mats = dict(MATS)
    mats['card'] = dict(tex=MW + 'mwc_%03d.jpg' % card, emis_tex=MW + 'mwc_%03d.jpg' % card, emis=(0.42, 0.42, 0.42), rough=0.5)
    pp = plaque(TMP + 'ref_%d.jpg' % card, l1, l2)
    mats['plq'] = dict(tex=pp, emis_tex=pp, emis=(0.45, 0.4, 0.32), rough=0.6)
    # the column: dark carved wood with brass bands, a stepped base and cap, a glowing jar finial
    bevel_box(m, 'dark', W, H, W, 0.05, m=T(0, H / 2, 0), uvs=2.0)
    for y, s_ in ((0.08, 0.3), (0.22, 0.18), (H - 0.06, 0.22), (H + 0.08, 0.1)):
        bevel_box(m, 'mud' if y < 1 else 'dark', W + s_, 0.16, W + s_, 0.03, m=T(0, y, 0), uvs=2.0)
    for y in (0.32, H - 0.18): box(m, 'brass', W + 0.03, 0.05, W + 0.03, m=T(0, y, 0))
    lathe(m, 'brass', [(0.0, H + 0.16), (0.32, H + 0.16), (0.2, H + 0.32), (0.12, H + 0.36), (0.0, H + 0.4)], 12)
    lathe(m, 'glow', [(0.0, H + 0.38), (0.16, H + 0.44), (0.19, H + 0.66), (0.13, H + 0.84), (0.0, H + 0.88)], 12)
    lathe(m, 'brass', [(0.0, H + 0.86), (0.17, H + 0.9), (0.0, H + 1.0)], 10)
    pw = W - 0.12; ph = pw / (1400 / 330)
    for a in (0, 90, 180, 270):
        F = M(Ry(a), T(0, 0, W / 2 + 0.005))
        cy = 0.42 + ph + 0.22 + ch / 2
        quad(m, 'card', cw, ch, M(F, T(0, cy, 0.012)))
        quad(m, 'black', cw + 0.06, ch + 0.06, M(F, T(0, cy, 0.006)))
        gilt(m, cw, ch, M(F, T(0, cy, 0)))
        quad(m, 'plq', pw, ph, M(F, T(0, 0.42 + ph / 2, 0.02)))
        box(m, 'brass', pw + 0.06, 0.04, 0.04, m=M(F, T(0, 0.42 + ph + 0.02, 0.02)))
    print(out, write('/home/claude/spire/out/glb/' + out, m, mats))
    return H
pillar(62, 'sp_ref_founder.glb', 2.4, 'THE REAL ONE', 'FIND ITS TWIN ON THE STAIRS')
pillar(100, 'sp_ref_flag.glb', 0.72, 'THE REAL BLACK FLAG', 'FIND ITS TWIN IN THE VAULT', H=1.75)
