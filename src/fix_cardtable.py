"""(v30, owner: "we cannot have regular cards in a mudwater themed building") the Meshy card table came with ordinary playing
cards painted into its felt. This paints them out of the texture (felt green filled in from the surrounding cloth), so the
real Mudwater cards (card_spread.py) can be dealt on top. Rewrites /home/claude/meshy/models/cardtable.glb (original kept as
cardtable_orig.glb); then run meshy_props.py cardtable."""
import io, json, os, shutil, struct, sys
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, '/home/claude/spire')
from glb import read_glb
NAME = sys.argv[1] if len(sys.argv) > 1 else 'cardtable'          # cardtable (cards on green felt) | coffeetable (cards on oak)
SRC = '/home/claude/meshy/models/%s.glb' % NAME; ORIG = '/home/claude/meshy/models/%s_orig.glb' % NAME
if not os.path.exists(ORIG): shutil.copy(SRC, ORIG)
js, b = read_glb(ORIG); b = bytearray(b)
src = js['textures'][js['materials'][0]['pbrMetallicRoughness']['baseColorTexture']['index']]['source']
v = js['bufferViews'][js['images'][src]['bufferView']]; o = v.get('byteOffset', 0)
im = Image.open(io.BytesIO(bytes(b[o:o + v['byteLength']]))).convert('RGB'); A = np.asarray(im).astype(np.float32) / 255
hsv = np.asarray(im.convert('HSV')).astype(np.float32) / 255; H, S, V = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
if NAME == 'cardtable':
    green = (H > 90) & (H < 180) & (S > 0.25) & (V > 0.12)          # the felt
    card = (V > 0.55) & (S < 0.38)                                   # the white / cream card faces
else:
    green = (H > 15) & (H < 45) & (S > 0.35) & (V > 0.18) & (V < 0.62)   # the oak planks
    card = (H > 18) & (H < 58) & (S > 0.08) & (S < 0.42) & (V > 0.6)     # the cream card faces (not the grey pewter)
from scipy import ndimage as nd
card = nd.binary_closing(card, iterations=4)                     # swallow the red / black pips and corner numbers
card = nd.binary_fill_holes(card)
lab, n = nd.label(card); keep = np.zeros_like(card)
gd = nd.binary_dilation(green, iterations=6)
for k in range(1, n + 1):
    c = lab == k
    if c.sum() <= 40: continue
    ring = nd.binary_dilation(c, iterations=5) & ~c
    pips = (((H < 15) | (H > 340)) & (S > 0.45) & (V > 0.3) & c).sum() + ((V < 0.2) & c).sum()
    if NAME == 'cardtable' or (gd & ring).sum() > 0.5 * ring.sum() or pips > 6: keep |= c      # coffee table: only cream patches lying on the oak (not the lantern glass)
keep = nd.binary_dilation(keep, iterations=3)
print('card pixels painted out:', int(keep.sum()), 'of', keep.size)
# fill: nearest felt colour, then soften with the felt's own texture noise
idx, dist = nd.distance_transform_edt(~(green & ~keep), return_distances=True, return_indices=True)[::-1]
fill = A[idx[0], idx[1]]
felt = np.median(A[green & ~keep], axis=0); far = dist > 40           # islands with no felt nearby: plain felt colour
fill[far] = felt
rng = np.random.default_rng(3); fill = fill * (0.94 + 0.08 * rng.random(fill.shape[:2]))[..., None]
out = A.copy(); out[keep] = fill[keep]
img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
blur = img.filter(ImageFilter.GaussianBlur(1.2)); m = Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
img = Image.composite(blur, img, m)
img.save('/home/claude/shots/%s_fixed.png' % NAME)
buf = io.BytesIO(); img.save(buf, 'PNG'); data = buf.getvalue()
# rebuild the binary with the new image
views = js['bufferViews']; nb = bytearray(); nv = []
for vi, vv in enumerate(views):
    d = bytes(b[vv.get('byteOffset', 0): vv.get('byteOffset', 0) + vv['byteLength']])
    if vi == js['images'][src]['bufferView']: d = data; js['images'][src]['mimeType'] = 'image/png'
    while len(nb) % 4: nb.append(0)
    x = dict(vv); x['byteOffset'] = len(nb); x['byteLength'] = len(d); nb.extend(d); nv.append(x)
while len(nb) % 4: nb.append(0)
js['bufferViews'] = nv; js['buffers'] = [{'byteLength': len(nb)}]
j = json.dumps(js, separators=(',', ':')).encode()
while len(j) % 4: j += b' '
open(SRC, 'wb').write(struct.pack('<III', 0x46546C67, 2, 28 + len(j) + len(nb)) + struct.pack('<II', len(j), 0x4E4F534A) + j + struct.pack('<II', len(nb), 0x004E4942) + bytes(nb))
print('wrote', SRC)
