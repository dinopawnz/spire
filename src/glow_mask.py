"""Make the pale shelf mushrooms on a Meshy model glow amber: finds the mushroom-coloured texels in the base colour
(light peach/orange, brighter than bark, not green moss) and adds them as an emissive texture. Everything else stays unlit.
    python3 glow_mask.py in.glb out.glb [strength]"""
import sys, io, json, struct
import numpy as np
from PIL import Image, ImageFilter
from glb import read_glb

def pack(js, b, dst):
    b = bytearray(b)
    while len(b) % 4: b.append(0)
    js['buffers'] = [{'byteLength': len(b)}]
    j = json.dumps(js, separators=(',', ':')).encode()
    while len(j) % 4: j += b' '
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(b)) + struct.pack('<II', len(j), 0x4E4F534A) + j + struct.pack('<II', len(b), 0x004E4942) + bytes(b)
    open(dst, 'wb').write(out); return len(out)

def glow(src, dst, strength=0.9, preview=None):
    js, b = read_glb(src); b = bytearray(b)
    mat = js['materials'][0]; bi = mat['pbrMetallicRoughness']['baseColorTexture']['index']
    img = js['images'][js['textures'][bi]['source']]; v = js['bufferViews'][img['bufferView']]
    im = Image.open(io.BytesIO(bytes(b[v.get('byteOffset', 0): v.get('byteOffset', 0) + v['byteLength']]))).convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255
    r, g, bl = a[..., 0], a[..., 1], a[..., 2]
    lum = a.mean(-1)
    m = (r > 0.55) & (r > g * 1.08) & (g > bl * 1.12) & (lum > 0.45) & (g > 0.38)     # light peach / orange caps
    mask = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.5))
    mk = np.asarray(mask).astype(np.float32)[..., None] / 255
    em = np.clip(a * mk * 1.15, 0, 1)                      # glow in the cap's own colour
    out = io.BytesIO(); Image.fromarray((em * 255).astype(np.uint8)).save(out, 'JPEG', quality=88); data = out.getvalue()
    while len(b) % 4: b.append(0)
    js['bufferViews'].append({'buffer': 0, 'byteOffset': len(b), 'byteLength': len(data)}); b.extend(data)
    js['images'].append({'bufferView': len(js['bufferViews']) - 1, 'mimeType': 'image/jpeg'})
    js['textures'].append({'source': len(js['images']) - 1, **({'sampler': js['textures'][bi]['sampler']} if 'sampler' in js['textures'][bi] else {})})
    mat['emissiveTexture'] = {'index': len(js['textures']) - 1}
    mat['emissiveFactor'] = [1.0, 0.55, 0.18]
    mat.setdefault('extensions', {})['KHR_materials_emissive_strength'] = {'emissiveStrength': strength}
    js.setdefault('extensionsUsed', [])
    if 'KHR_materials_emissive_strength' not in js['extensionsUsed']: js['extensionsUsed'].append('KHR_materials_emissive_strength')
    if preview: Image.fromarray((em * 255).astype(np.uint8)).resize((512, 512)).save(preview)
    print(dst, 'glowing texels', round(float(m.mean()) * 100, 2), '%', pack(js, b, dst) // 1024, 'KB')

if __name__ == '__main__':
    glow(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.9, sys.argv[4] if len(sys.argv) > 4 else None)
