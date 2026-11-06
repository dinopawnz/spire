"""(v23) THE SKY: a full 360-degree night sky dome + a separate, always-round half moon.

Inputs (Meshy text-to-image, made once, kept in tex/): tex/sky_a.png, tex/sky_b.png (two wide night-sky photos, horizon at the bottom edge),
tex/moon_src.png (a half moon on black).
Outputs: out/glb/sp_sky.glb (inside-out sphere, unlit, radius 480 m), out/sky_moon.png (moon with transparency), out/sky_moonglow.png.

How the panorama is put together (equirectangular, 4096 x 2048, horizon on the middle row):
  - photo A covers the half of the sky behind the building (-z), photo B the half behind the boardwalk (+z); they overlap 16 degrees at
    both joins and cross-fade there, so there is no seam
  - each photo covers elevation 0..72 degrees; above that the sky fades smoothly into a star field drawn for the dome (stars stay round
    right up to the top, no pinching)
  - along the horizon: a soft misty glow fading into the dark below (no painted trees).
"""
import math, os, numpy as np
from PIL import Image, ImageFilter
from glb import *

TEX = '/home/claude/spire/tex/'
OUT = '/home/claude/spire/out/'
W, H = 4096, 2048
rng = np.random.default_rng(11)

def load(name, crop):
    im = Image.open(TEX + name).convert('RGB').crop(crop)
    return np.asarray(im).astype(np.float32) / 255.0

A = load('sky_a.png', (0, 78, 1376, 713))
B = load('sky_b.png', (72, 71, 1303, 696))

def sample(img, u, v):
    """bilinear sample img at normalized u (0..1 left->right), v (0..1 top->bottom); arrays"""
    h, w, _ = img.shape
    x = np.clip(u * (w - 1), 0, w - 1); y = np.clip(v * (h - 1), 0, h - 1)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); x1 = np.minimum(x0 + 1, w - 1); y1 = np.minimum(y0 + 1, h - 1)
    fx = (x - x0)[..., None]; fy = (y - y0)[..., None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x1] * fx * (1 - fy) + img[y1, x0] * (1 - fx) * fy + img[y1, x1] * fx * fy)

# azimuth of every column: 0 deg = -z (behind the building, what you face walking in), increasing clockwise seen from above
cols = np.arange(W); rows = np.arange(H)
az = (cols + 0.5) / W * 360.0                       # 0..360
el = 90.0 - (rows + 0.5) / H * 180.0                # +90 (top) .. -90
AZ, EL = np.meshgrid(az, el)

E_TOP = 72.0                                       # the photos cover 0..E_TOP degrees
OV = 16.0                                          # overlap at the joins
def band(img, a0):
    """img spread over azimuth a0-OV/2 .. a0+180+OV/2; returns colour + weight (cross-fade ramps at both ends)"""
    span = 180.0 + OV
    da = (AZ - (a0 - OV / 2)) % 360.0
    inside = da <= span
    u = da / span; v = 1.0 - np.clip(EL / E_TOP, 0, 1)
    col = sample(img, u, v)
    w = np.clip(np.minimum(da, span - da) / OV, 0, 1) * inside
    return col, w

ca, wa = band(A, 270.0)                            # photo A centred on azimuth 0 (behind the building)
cb, wb = band(B, 90.0)                             # photo B centred on azimuth 180 (behind the boardwalk)
ws = wa + wb + 1e-6
sky = (ca * wa[..., None] + cb * wb[..., None]) / ws[..., None]
# ---- bayou grading (owner: night in the bayou, not outer space): the purple / pink of the Milky Way turns warm smoky gold and soft white
L_ = (0.3 * sky[..., 0] + 0.59 * sky[..., 1] + 0.11 * sky[..., 2])[..., None]
purple = np.clip((np.minimum(sky[..., 0], sky[..., 2]) - sky[..., 1]) * 9.0, 0, 1)[..., None]
warm = L_ * np.array([1.18, 1.0, 0.74], np.float32)
sky = sky * (1 - purple) + warm * purple
sky = np.clip(sky * np.array([1.03, 1.0, 0.94], np.float32), 0, 1)          # a touch warmer overall
# a faint green-gold swamp mist hanging low on the horizon
mist_col = np.array([0.36, 0.42, 0.27], np.float32)
m_ = (0.42 * np.exp(-np.clip(EL, 0, None) / 3.0) * (EL >= 0))[..., None]
sky = sky * (1 - m_) + mist_col * m_

# ---- the upper sky: smooth gradient from the photos' top colour to a deep zenith blue, with a dome-correct star field
top_a = A[:12].reshape(-1, 3).mean(0); top_b = B[:12].reshape(-1, 3).mean(0)
top_col = (top_a + top_b) / 2
zen_col = top_col * 0.75
t = np.clip((EL - (E_TOP - 12.0)) / 12.0, 0, 1)[..., None]          # fade the last 12 degrees of the photos into the procedural upper sky
upper = top_col + (zen_col - top_col) * np.clip((EL - E_TOP) / (90 - E_TOP), 0, 1)[..., None]
stars = np.zeros((H, W, 3), np.float32)
N = 9000
sz = rng.uniform(-1, 1, N) ** 0                     # placeholder to keep rng order stable
# points uniform on the upper cap (elevation > 40)
zz = rng.uniform(math.sin(math.radians(40)), 1.0, N); th = rng.uniform(0, 2 * math.pi, N)
e_s = np.degrees(np.arcsin(zz)); a_s = np.degrees(th)
mag = rng.power(0.25, N)                            # most faint, a few bright
tint = np.stack([1 - 0.15 * rng.random(N), 1 - 0.08 * rng.random(N), 1 - 0.0 * rng.random(N)], 1)
tint[rng.random(N) < 0.15] = [1.0, 0.9, 0.75]
for i in range(N):
    r_ = int((90 - e_s[i]) / 180 * H); c_ = int(a_s[i] / 360 * W) % W
    wpx = max(1, int(round(1.0 / max(0.05, math.cos(math.radians(e_s[i]))))))     # wider near the top: round on the dome
    b = 0.25 + 0.75 * mag[i] ** 3
    for dc in range(-(wpx // 2), wpx // 2 + 1):
        stars[r_, (c_ + dc) % W] = np.maximum(stars[r_, (c_ + dc) % W], tint[i] * b)
        if mag[i] > 0.97 and 0 < r_ < H - 1:
            stars[r_ - 1, (c_ + dc) % W] = np.maximum(stars[r_ - 1, (c_ + dc) % W], tint[i] * b * 0.45)
            stars[r_ + 1, (c_ + dc) % W] = np.maximum(stars[r_ + 1, (c_ + dc) % W], tint[i] * b * 0.45)
upper = np.clip(upper + stars, 0, 1)
sky = sky * (1 - t) + upper * t

# ---- the horizon: no painted trees (the real swamp is all round you) - just a soft misty glow at the horizon fading down into the dark
hz = sky[H // 2 - 2].copy()                                         # the warm haze colour along the horizon, per column
px_per_deg = H / 180.0
dark = np.array([0.02, 0.03, 0.045], np.float32)
below = rows[H // 2:] - H // 2
fade = np.exp(-below / (px_per_deg * 3.0))[:, None, None]           # mist glow dying away over ~3 degrees below the horizon
sky[H // 2:] = dark[None, None, :] * (1 - fade) + (hz[None, :, :] * 0.8 + mist_col * 0.1) * fade
img = Image.fromarray((np.clip(sky, 0, 1) * 255).astype(np.uint8))
img.save(TEX + 'sky_pano.jpg', quality=90)
img.resize((1024, 512)).save('/tmp/sky_pano_small.jpg', quality=85)

# ---- the dome: an inside-out sphere, unlit (glows with its own picture), radius 480
R = 480.0; nu, nv = 96, 48
P, N_, U, I = [], [], [], []
for j in range(nv + 1):
    e = 90.0 - 180.0 * j / nv
    for i in range(nu + 1):
        a = 360.0 * i / nu
        # azimuth 0 = -z, clockwise from above: x = sin(a), z = -cos(a)
        x_ = R * math.cos(math.radians(e)) * math.sin(math.radians(a)); y_ = R * math.sin(math.radians(e)); z_ = -R * math.cos(math.radians(e)) * math.cos(math.radians(a))
        P.append([x_, y_, z_]); N_.append([-x_ / R, -y_ / R, -z_ / R]); U.append([i / nu, j / nv])
for j in range(nv):
    for i in range(nu):
        a = j * (nu + 1) + i; b = a + nu + 1
        I += [a, a + 1, b, a + 1, b + 1, b]
P = np.array(P); I_ = np.array(I).reshape(-1, 3)
fn = np.cross(P[I_[0, 1]] - P[I_[0, 0]], P[I_[0, 2]] - P[I_[0, 0]])
if np.dot(fn, -P[I_[0, 0]]) < 0: I = list(I_[:, ::-1].reshape(-1))     # faces point inward
m = Mesh(); m.add('sky', P, N_, U, I)
write(OUT + 'glb/sp_sky.glb', m, {'sky': dict(tex=TEX + 'sky_pano.jpg', emis_tex=TEX + 'sky_pano.jpg', emis=(1.0, 1.0, 1.0), color=(0, 0, 0, 1), double=True, rough=1.0, metal=0.0)})

# ---- the moon (owner's pick: a glowing golden crescent): cut out of its black background, its own warm halo kept; the dark part of the
# disc stays solid so the stars don't shine through it, like a real moon
src = np.asarray(Image.open(TEX + 'moon_src.png').convert('RGB')).astype(np.float32) / 255.0
DCX, DCY, DR = 522, 506, 350                                               # the moon disc in the source picture
side = int(DR * 2.7); x0, y0 = DCX - side // 2, DCY - side // 2
mi = Image.open(TEX + 'moon_src.png').convert('RGB').crop((x0, y0, x0 + side, y0 + side)).resize((768, 768), Image.LANCZOS)
ma = np.asarray(mi).astype(np.float32) / 255.0
lum = ma.max(axis=2)
alpha = np.clip((lum - 0.012) / 0.22, 0, 1) ** 0.8
yy, xx = np.mgrid[0:768, 0:768]; d = np.hypot(xx - 384, yy - 384) / (DR / side * 768)
disc = np.clip((1.0 - d) / 0.02, 0, 1)
alpha = np.maximum(alpha, disc * 0.62)                                      # the whole disc solid (soft 2% edge)
night = np.array([0.045, 0.07, 0.12], np.float32)                          # the dark part takes the deep blue of the night sky (faint earthshine)
lit = np.clip((lum - 0.03) / 0.25, 0, 1)[..., None]
rgb = np.clip(ma * 1.1, 0, 1) * lit + (night + ma * 0.6) * (1 - lit)
rgba = np.dstack([rgb, alpha])
Image.fromarray((rgba * 255).astype(np.uint8)).save(OUT + 'sky_moon.png')
mi = Image.fromarray((ma * 255).astype(np.uint8))
g = 512; yy, xx = np.mgrid[0:g, 0:g]; d = np.hypot(xx - g / 2, yy - g / 2) / (g / 2)
glow_a = np.clip(np.exp(-d * 3.2) * 1.0 - 0.02, 0, 1) * (d < 1)
gl = np.dstack([np.full((g, g), 1.0), np.full((g, g), 0.8), np.full((g, g), 0.5), glow_a])      # warm gold
Image.fromarray((gl * 255).astype(np.uint8)).save(OUT + 'sky_moonglow.png')
print('sky: pano', img.size, 'dome', len(P), 'verts; moon', mi.size)
