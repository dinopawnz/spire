"""Turn a Meshy-generated photo floor (meshy/floor2.png) into a seamless PBR set for the lounge:
tex/wetfloor.jpg (colour), tex/wetfloor_n.jpg (bumps from detail), tex/wetfloor_mr.png (G = roughness, glossy where wet/dark mud).
Seamless by blending with a half-offset copy under a soft, noisy mask; baked highlights are tamed so the tiling doesn't show."""
import numpy as np, sys
from PIL import Image, ImageFilter
from textures import fbm, norm01, normal_map, to_img, OUT
src = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/meshy/floor2.png'
N = 2048
im = Image.open(src).convert('RGB').resize((N, N), Image.LANCZOS)
a = np.array(im).astype(np.float32) / 255
# tame the baked-in lantern highlights (they would repeat across the floor)
lum = a.mean(-1, keepdims=True)
knee = 0.3
over = np.clip(lum - knee, 0, None)
a = a * np.where(lum > knee, (knee + over * 0.12) / np.maximum(lum, 1e-4), 1.0)
# flatten very large-scale brightness variation (photo vignetting / light falloff)
low = np.array(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(N // 6))).astype(np.float32) / 255
a = np.clip(a * (low.mean((0, 1)) / np.maximum(low, 0.02)) ** 0.85, 0, 1)
# seamless: blend with a half-shifted copy; the mask is 1 in the middle, 0 at the edges, with a noisy border so no straight cross-fade line
b = np.roll(np.roll(a, N // 2, 0), N // 2, 1)
yy, xx = np.mgrid[0:N, 0:N] / (N - 1)
d = np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy))
nz = norm01(fbm(N, 40, 4, seed=77))
w = np.clip((d + (nz - 0.5) * 0.12 - 0.07) / 0.1, 0, 1)[..., None]
c = a * w + b * (1 - w)
Image.fromarray((c * 255).astype(np.uint8)).save(OUT + '/wetfloor.jpg', quality=92)
# bumps: fine detail from brightness (dark seams sink), large shapes removed
g = c.mean(-1)
hp = g - np.array(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))).astype(np.float32) / 255
normal_map(hp * 6.0, 3.0).save(OUT + '/wetfloor_n.jpg', quality=92)
# roughness: wood fairly glossy (wet), muddy smooth patches glossier, bright dry ridges a bit rougher
sat = c.max(-1) - c.min(-1)
rough = np.clip(0.3 - 0.12 * norm01(-hp) + 0.18 * norm01(g) ** 2 - 0.08 * norm01(sat), 0.06, 0.6)
to_img(np.dstack([np.ones_like(rough), rough, np.zeros_like(rough)])).save(OUT + '/wetfloor_mr.png', optimize=True)
t = Image.fromarray((c * 255).astype(np.uint8)).resize((512, 512))
tile = Image.new('RGB', (1024, 1024)); [tile.paste(t, (x, y)) for x in (0, 512) for y in (0, 512)]
tile.save('/home/claude/shots/wetfloor_tiled.jpg', quality=88)
print('photo floor done')
