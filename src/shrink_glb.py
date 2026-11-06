"""shrink a GLB: re-encode every embedded image as a JPEG (or PNG if it needs alpha) at most N px. Geometry untouched.
   python3 shrink_glb.py in.glb out.glb 1024"""
import sys, json, struct, io
import numpy as np
from PIL import Image
from glb import read_glb

def shrink(src, dst, N=1024, q=86):
    js, b = read_glb(src)
    views = js['bufferViews']; img_views = {im['bufferView']: k for k, im in enumerate(js.get('images', []))}
    newbin = bytearray(); newviews = []
    for vi, v in enumerate(views):
        data = b[v.get('byteOffset', 0): v.get('byteOffset', 0) + v['byteLength']]
        if vi in img_views:
            im = Image.open(io.BytesIO(data)); im.load()
            alpha = im.mode in ('RGBA', 'LA') and np.asarray(im.convert('RGBA'))[..., 3].min() < 250
            if max(im.size) > N: im = im.resize((min(N, im.size[0]), min(N, im.size[1])), Image.LANCZOS)
            out = io.BytesIO()
            if alpha: im.save(out, 'PNG', optimize=True); mime = 'image/png'
            else: im.convert('RGB').save(out, 'JPEG', quality=q); mime = 'image/jpeg'
            data = out.getvalue(); js['images'][img_views[vi]]['mimeType'] = mime
        while len(newbin) % 4: newbin.append(0)
        nv = dict(v); nv['byteOffset'] = len(newbin); nv['byteLength'] = len(data); newbin.extend(data); newviews.append(nv)
    while len(newbin) % 4: newbin.append(0)
    js['bufferViews'] = newviews; js['buffers'] = [{'byteLength': len(newbin)}]
    j = json.dumps(js, separators=(',', ':')).encode()
    while len(j) % 4: j += b' '
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(newbin)) + struct.pack('<II', len(j), 0x4E4F534A) + j + struct.pack('<II', len(newbin), 0x004E4942) + bytes(newbin)
    open(dst, 'wb').write(out); return len(out)

if __name__ == '__main__':
    print(shrink(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1024) // 1024, 'KB')
