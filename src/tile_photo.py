"""Make Meshy photo textures tile seamlessly and write colour + normal maps into tex/.
  python3 tile_photo.py wood  src.png  name     -> planks: cut top/bottom on board seams (natural vertical repeat), wrap-blend left/right
  python3 tile_photo.py water src.png  name     -> waterfall sheet: one vertical period, brightness becomes transparency (PNG)
"""
import sys, numpy as np
from PIL import Image, ImageFilter
from textures import normal_map, OUT

def lum(a): return a.mean(-1)

def flatten(a, r):
    low = np.array(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
    return np.clip(a * (low.mean((0, 1)) / np.maximum(low, 0.02)) ** 0.8, 0, 1)

def xwrap(a, band=0.12):
    """blend the left and right edges into each other (grain runs along x, so this hides well)"""
    h, w = a.shape[:2]; b = np.roll(a, w // 2, 1)
    x = np.arange(w) / (w - 1); d = np.minimum(x, 1 - x)
    m = np.clip((d - 0.02) / band, 0, 1)[None, :, None]
    return a * m + b * (1 - m)

def wood(src, name, N=2048):
    a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32) / 255
    a = a[int(a.shape[0] * 0.01): int(a.shape[0] * 0.99)]
    # board seams = dark rows; cut from the first seam to the last one so the top and bottom meet on a seam
    prof = np.convolve(lum(a).mean(1), np.ones(5) / 5, 'same')
    h = len(prof); thr = np.percentile(prof, 8)
    rows = [i for i in range(3, h - 3) if prof[i] <= thr and prof[i] == prof[i - 3:i + 4].min()]
    top = min(rows, key=lambda i: abs(i - 0.06 * h)); bot = min(rows, key=lambda i: abs(i - 0.94 * h))
    a = a[top:bot]
    a = flatten(a, 120)
    a = xwrap(a)
    im = Image.fromarray((a * 255).astype(np.uint8)).resize((N, N), Image.LANCZOS)
    im.save(OUT + '/' + name + '.jpg', quality=92)
    g = np.asarray(im.convert('L')).astype(np.float32) / 255
    hp = g - np.asarray(im.convert('L').filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255
    normal_map(hp * 6.0, 2.5).save(OUT + '/' + name + '_n.jpg', quality=90)
    t = im.resize((512, 512)); tile = Image.new('RGB', (1024, 1024)); [tile.paste(t, (x, y)) for x in (0, 512) for y in (0, 512)]
    tile.save('/home/claude/shots/tile_' + name + '.jpg', quality=85)
    print(name, 'cut rows', top, bot, 'of', h)

def water(src, name):
    a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32) / 255
    h = a.shape[0]
    a = a[int(h * 0.52): int(h * 0.98)]                                 # one of the two stacked copies
    h, w = a.shape[:2]; b = np.roll(a, h // 2, 0)                        # make it loop top-to-bottom
    y = np.arange(h) / (h - 1); d = np.minimum(y, 1 - y)
    m = np.clip((d - 0.02) / 0.18, 0, 1)[:, None, None]
    a = a * m + b * (1 - m)
    l = np.clip((lum(a) - 0.06) / 0.7, 0, 1)
    rgb = np.clip(a * 1.15 + np.array([0.02, 0.05, 0.05]), 0, 1)
    out = np.dstack([rgb, l ** 0.9])
    im = Image.fromarray((out * 255).astype(np.uint8), 'RGBA').resize((512, 512), Image.LANCZOS)
    im.save('/home/claude/spire/out/' + name + '.png', optimize=True)
    bg = Image.new('RGBA', (512, 1024), (10, 12, 12, 255)); bg.alpha_composite(im, (0, 0)); bg.alpha_composite(im, (0, 512))
    bg.convert('RGB').save('/home/claude/shots/tile_' + name + '.jpg', quality=85)
    print(name, 'water sheet done')

if __name__ == '__main__':
    {'wood': wood, 'water': water}[sys.argv[1]](sys.argv[2], sys.argv[3])
