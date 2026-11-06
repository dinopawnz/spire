"""Warm amber versions of the lounge glow textures (out/bio/bio_veins_amber.png, bio_wall_amber.png).
Thin veins only: the soft yellow clouds behind the veins are dropped, and the colour goes from lemon to amber,
so the lounge floor reads as wet wood with a few embers of light running through it (not neon)."""
import numpy as np
from PIL import Image, ImageFilter
SRC = '/home/claude/spire_repo/'; OUT = '/home/claude/spire/out/bio/'
for src, dst, keep in (('bio_veins_gold.png', 'bio_veins_amber.png', 0.55), ('bio_wall_gold.png', 'bio_wall_amber.png', 0.6)):
    a = np.array(Image.open(SRC + src).convert('RGBA')).astype(np.float32) / 255
    al = a[..., 3]
    # keep the bright thin lines, fade out the wide soft glow
    v = np.clip((al - 0.18) / 0.6, 0, 1) ** 1.3
    halo = np.array(Image.fromarray((v * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2))).astype(np.float32) / 255
    alpha = np.clip(v * 0.95 + halo * 0.35, 0, 1) * keep
    rgb = np.zeros(al.shape + (3,), np.float32)
    core = np.clip(v * 1.4, 0, 1)[..., None]
    rgb[:] = np.array([1.0, 0.55, 0.16]) * (1 - core) + np.array([1.0, 0.8, 0.45]) * core
    out = np.dstack([rgb, alpha])
    Image.fromarray((out * 255).astype(np.uint8), 'RGBA').save(OUT + dst, optimize=True)
    print(dst, 'cover', round(float((alpha > 0.1).mean()), 3))

# ---- warm light pool (lantern light spilling on the wet floor), baked into the lounge model: tex/pool.png
from textures import fbm, norm01
n = 512
yy, xx = np.mgrid[0:n, 0:n] / (n - 1) * 2 - 1
ang = np.arctan2(yy, xx); rr = np.hypot(xx, yy)
wob = 1 + 0.12 * np.sin(ang * 3 + 0.7) + 0.08 * np.sin(ang * 5 + 2.1)        # irregular edge, never a clean circle
fall = np.clip(1 - rr / (0.95 * wob), 0, 1) ** 2.2
streak = 0.75 + 0.25 * norm01(fbm(n, 12, 3, aniso=0.25, seed=5))               # broken up like light on wet boards
alpha = np.clip(fall * streak, 0, 1) * 0.8
rgb = np.zeros((n, n, 3)); rgb[:] = [1.0, 0.62, 0.24]
rgb = rgb * (1 - fall[..., None] ** 3 * 0.0) + np.array([1.0, 0.86, 0.55]) * (fall[..., None] ** 4)
Image.fromarray((np.dstack([np.clip(rgb, 0, 1), alpha]) * 255).astype(np.uint8), 'RGBA').save('/home/claude/spire/tex/pool.png', optimize=True)
# ---- the lounge footstep ripple in amber (the Hall of Fakes keeps the teal one)
ring = Image.open(SRC + 'bio_ring.png').convert('RGBA')
a = np.array(ring).astype(np.float32) / 255
lum = a[..., :3].max(-1, keepdims=True)
amber = np.dstack([np.clip(lum * np.array([1.0, 0.7, 0.3]) + (lum ** 4) * 0.3, 0, 1), a[..., 3]])
Image.fromarray((amber * 255).astype(np.uint8), 'RGBA').save(OUT + 'bio_ring_amber.png', optimize=True)
print('pool + amber ring done')
