"""Small numpy glTF 2.0 (.glb) toolkit for the Mudwater Spire.
Mesh = per-material buckets of triangles (pos, normal, uv, colour). Helpers build planks, beams, logs, lathe shapes,
tubes (rope, rails), extrusions and textured quads, all placed with 4x4 transforms. write() packs one .glb with
embedded textures (JPEG/PNG), PBR materials, optional normal maps, emissive, alpha.
"""
import json, struct, math, io, os
import numpy as np

# ------------------------------------------------------------------ transforms
def T(x=0, y=0, z=0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m
def S(x=1, y=None, z=None):
    y = x if y is None else y; z = x if z is None else z
    return np.diag([x, y, z, 1.0])
def Rx(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a); m = np.eye(4); m[1, 1] = c; m[1, 2] = -s; m[2, 1] = s; m[2, 2] = c; return m
def Ry(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a); m = np.eye(4); m[0, 0] = c; m[0, 2] = s; m[2, 0] = -s; m[2, 2] = c; return m
def Rz(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a); m = np.eye(4); m[0, 0] = c; m[0, 1] = -s; m[1, 0] = s; m[1, 1] = c; return m
def M(*ms):
    out = np.eye(4)
    for m in ms: out = out @ m
    return out
def look_basis(d, up=(0, 1, 0)):
    """rotation whose +z points along d"""
    d = np.asarray(d, float); d = d / (np.linalg.norm(d) + 1e-12)
    up = np.asarray(up, float)
    if abs(np.dot(up, d)) > 0.98: up = np.array([1.0, 0, 0])
    x = np.cross(up, d); x /= np.linalg.norm(x); y = np.cross(d, x)
    m = np.eye(4); m[:3, 0] = x; m[:3, 1] = y; m[:3, 2] = d; return m

# ------------------------------------------------------------------ mesh
class Mesh:
    def __init__(self):
        self.b = {}          # material -> [pos list, nrm, uv, col, idx]
    def add(self, mat, pos, nrm, uv, idx, col=None, m=None):
        pos = np.asarray(pos, np.float64); nrm = np.asarray(nrm, np.float64); uv = np.asarray(uv, np.float64)
        idx = np.asarray(idx, np.int64).reshape(-1)
        if col is None: col = np.ones((len(pos), 4))
        else:
            col = np.asarray(col, np.float64)
            if col.ndim == 1: col = np.tile(np.r_[col, [1.0] * (4 - len(col))], (len(pos), 1))
            elif col.shape[1] == 3: col = np.c_[col, np.ones(len(col))]
        if m is not None:
            p4 = np.c_[pos, np.ones(len(pos))] @ m.T; pos = p4[:, :3]
            nm = np.linalg.inv(m[:3, :3]).T; nrm = nrm @ nm.T
            if np.linalg.det(m[:3, :3]) < 0: idx = idx.reshape(-1, 3)[:, ::-1].reshape(-1)
        n = np.linalg.norm(nrm, axis=1, keepdims=True); nrm = nrm / np.where(n > 1e-12, n, 1)
        bk = self.b.setdefault(mat, [[], [], [], [], [], 0])
        bk[0].append(pos); bk[1].append(nrm); bk[2].append(uv); bk[3].append(col); bk[4].append(idx + bk[5]); bk[5] += len(pos)
    def merge(self, other, m=None):
        for mat, bk in other.b.items():
            if not bk[0]: continue
            self.add(mat, np.vstack(bk[0]), np.vstack(bk[1]), np.vstack(bk[2]), np.concatenate(bk[4]), np.vstack(bk[3]), m)
    def tris(self):
        return sum(len(np.concatenate(bk[4])) // 3 for bk in self.b.values() if bk[4])
    def bounds(self):
        P = np.vstack([np.vstack(bk[0]) for bk in self.b.values() if bk[0]]); return P.min(0), P.max(0)

# ------------------------------------------------------------------ primitives (all return into a Mesh)
def quad(mesh, mat, w, h, m=None, uv=(0, 0, 1, 1), col=None, double=False):
    """plane in XY, facing +z, centred"""
    x, y = w / 2, h / 2; u0, v0, u1, v1 = uv
    P = [[-x, -y, 0], [x, -y, 0], [x, y, 0], [-x, y, 0]]; N = [[0, 0, 1]] * 4
    U = [[u0, v1], [u1, v1], [u1, v0], [u0, v0]]
    mesh.add(mat, P, N, U, [0, 1, 2, 0, 2, 3], col, m)
    if double: mesh.add(mat, P, [[0, 0, -1]] * 4, [[u1, v1], [u0, v1], [u0, v0], [u1, v0]], [0, 2, 1, 0, 3, 2], col, m)

def box(mesh, mat, sx, sy, sz, m=None, col=None, uvs=1.0, faces='xXyYzZ', uvoff=(0, 0)):
    """axis box centred at origin; world-scale UVs (1 unit of texture per `uvs` metres); grain runs along the longest axis"""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    long_axis = int(np.argmax([sx, sy, sz]))
    F = {'X': ([1, 0, 0], [0, 1, 2]), 'x': ([-1, 0, 0], [0, 1, 2]), 'Y': ([0, 1, 0], [1, 0, 2]), 'y': ([0, -1, 0], [1, 0, 2]), 'Z': ([0, 0, 1], [2, 0, 1]), 'z': ([0, 0, -1], [2, 0, 1])}
    ou, ov = uvoff
    for f in faces:
        n, (ax, a1, a2) = F[f]; n = np.array(n, float); s = n[ax]
        h = [hx, hy, hz]
        # the two in-plane axes; u follows the longest in-plane axis
        ia, ib = a1, a2
        if ib == long_axis: ia, ib = ib, ia
        corners = []
        for (ua, ub) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            p = [0, 0, 0]; p[ax] = s * h[ax]; p[ia] = ua * h[ia]; p[ib] = ub * h[ib]; corners.append(p)
        P = np.array(corners)
        U = np.c_[(P[:, ia] + h[ia]) / uvs + ou, (P[:, ib] + h[ib]) / uvs + ov]
        # winding so the face points along n
        e1 = P[1] - P[0]; e2 = P[2] - P[0]
        idx = [0, 1, 2, 0, 2, 3] if np.dot(np.cross(e1, e2), n) > 0 else [0, 2, 1, 0, 3, 2]
        mesh.add(mat, P, [n] * 4, U, idx, col, m)

def bevel_box(mesh, mat, sx, sy, sz, b=0.02, m=None, col=None, uvs=1.0, uvoff=(0, 0)):
    """box with chamfered edges (catches light on every plank edge)"""
    b = min(b, sx / 3, sy / 3, sz / 3)
    box(mesh, mat, sx - 2 * b, sy, sz - 2 * b, m, col, uvs, 'yY', uvoff)
    box(mesh, mat, sx, sy - 2 * b, sz - 2 * b, m, col, uvs, 'xX', uvoff)
    box(mesh, mat, sx - 2 * b, sy - 2 * b, sz, m, col, uvs, 'zZ', uvoff)
    # 12 chamfer strips
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    def strip(a, bq, c, d, n, L):
        P = np.array([a, bq, c, d], float); nn = np.array(n, float); nn /= np.linalg.norm(nn)
        U = np.array([[0, 0], [L / uvs, 0], [L / uvs, 0.05], [0, 0.05]]) + uvoff
        e1 = P[1] - P[0]; e2 = P[2] - P[0]
        idx = [0, 1, 2, 0, 2, 3] if np.dot(np.cross(e1, e2), nn) > 0 else [0, 2, 1, 0, 3, 2]
        mesh.add(mat, P, [nn] * 4, U, idx, col, m)
    for sxs in (-1, 1):
        for sys_ in (-1, 1):   # edges along z
            strip([sxs * hx, sys_ * (hy - b), -hz + b], [sxs * hx, sys_ * (hy - b), hz - b], [sxs * (hx - b), sys_ * hy, hz - b], [sxs * (hx - b), sys_ * hy, -hz + b], [sxs, sys_, 0], sz)
        for szs in (-1, 1):    # edges along y
            strip([sxs * hx, -hy + b, szs * (hz - b)], [sxs * hx, hy - b, szs * (hz - b)], [sxs * (hx - b), hy - b, szs * hz], [sxs * (hx - b), -hy + b, szs * hz], [sxs, 0, szs], sy)
    for sys_ in (-1, 1):
        for szs in (-1, 1):    # edges along x
            strip([-hx + b, sys_ * hy, szs * (hz - b)], [hx - b, sys_ * hy, szs * (hz - b)], [hx - b, sys_ * (hy - b), szs * hz], [-hx + b, sys_ * (hy - b), szs * hz], [0, sys_, szs], sx)
    # 8 corner triangles
    for sxs in (-1, 1):
        for sys_ in (-1, 1):
            for szs in (-1, 1):
                P = np.array([[sxs * hx, sys_ * (hy - b), szs * (hz - b)], [sxs * (hx - b), sys_ * hy, szs * (hz - b)], [sxs * (hx - b), sys_ * (hy - b), szs * hz]])
                n = np.array([sxs, sys_, szs], float)
                idx = [0, 1, 2] if np.dot(np.cross(P[1] - P[0], P[2] - P[0]), n) > 0 else [0, 2, 1]
                mesh.add(mat, P, [n] * 3, [[0, 0], [0.02, 0], [0, 0.02]], idx, col, m)

def lathe(mesh, mat, prof, seg=24, m=None, col=None, uvs_u=1.0, uv_v=None, cap_top=False, cap_bot=False, a0=0, a1=360, smooth=True):
    """revolve profile [(r, y), ...] about the y axis. u wraps around (uvs_u repeats), v follows the profile length"""
    prof = np.asarray(prof, float); n = len(prof)
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(prof, axis=0), axis=1))]
    V = L / (L[-1] if uv_v is None else uv_v) if uv_v != 0 else L
    full = (a1 - a0) >= 360
    cols = seg + 1
    ang = np.radians(np.linspace(a0, a1, cols))
    # profile normals (2D) via neighbours
    d = np.gradient(prof, axis=0); nr = np.c_[d[:, 1], -d[:, 0]]; nr /= np.linalg.norm(nr, axis=1, keepdims=True) + 1e-12
    P = []; N = []; U = []
    for j, a in enumerate(ang):
        ca, sa = math.cos(a), math.sin(a)
        for i in range(n):
            r, y = prof[i]; P.append([r * sa, y, r * ca]); N.append([nr[i, 0] * sa, nr[i, 1], nr[i, 0] * ca]); U.append([j / seg * uvs_u, V[i]])
    I = []
    for j in range(seg):
        for i in range(n - 1):
            a = j * n + i; b = (j + 1) * n + i
            I += [a, a + 1, b + 1, a, b + 1, b]
    P = np.array(P); N = np.array(N)
    # fix winding: outward normals should agree with triangle orientation
    t = np.array(I[:3]); f = np.cross(P[t[1]] - P[t[0]], P[t[2]] - P[t[0]])
    if np.dot(f, N[t[0]]) < 0: I = list(np.array(I).reshape(-1, 3)[:, ::-1].reshape(-1))
    mesh.add(mat, P, N, U, I, col, m)
    for cap, k, ny in ((cap_top, n - 1, 1), (cap_bot, 0, -1)):
        if not cap: continue
        r, y = prof[k]
        if r < 1e-6: continue
        Pc = [[0, y, 0]] + [[r * math.sin(a), y, r * math.cos(a)] for a in ang]
        Uc = [[0.5, 0.5]] + [[0.5 + 0.5 * math.sin(a), 0.5 + 0.5 * math.cos(a)] for a in ang]
        Ic = []
        for j in range(seg): Ic += [0, j + 1, j + 2] if ny > 0 else [0, j + 2, j + 1]
        Pc = np.array(Pc)
        tt = Ic[:3]; f = np.cross(Pc[tt[1]] - Pc[tt[0]], Pc[tt[2]] - Pc[tt[0]])
        if f[1] * ny < 0: Ic = list(np.array(Ic).reshape(-1, 3)[:, ::-1].reshape(-1))
        mesh.add(mat, Pc, [[0, ny, 0]] * len(Pc), Uc, Ic, col, m)

def cyl(mesh, mat, r, h, seg=16, m=None, col=None, caps=True, uvs_u=1.0, uv_v=None, r2=None):
    r2 = r if r2 is None else r2
    lathe(mesh, mat, [(r, 0), (r2, h)], seg, m, col, uvs_u, uv_v if uv_v is not None else 1.0, caps, caps)

def tube(mesh, mat, path, r, seg=8, m=None, col=None, uvs=1.0, closed=False, twist=0.0, radii=None):
    """sweep a circle along a polyline (rope, rails, pipes). twist = turns of texture twist per metre (rope look)"""
    path = np.asarray(path, float); n = len(path)
    if n < 2: return
    tang = np.gradient(path, axis=0); tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-12
    # parallel-transport frame
    up = np.array([0, 1.0, 0]) if abs(tang[0][1]) < 0.9 else np.array([1.0, 0, 0])
    nrm = np.cross(tang[0], up); nrm /= np.linalg.norm(nrm)
    frames = []
    for i in range(n):
        if i:
            t0, t1 = tang[i - 1], tang[i]; v = np.cross(t0, t1); s = np.linalg.norm(v)
            if s > 1e-9:
                v /= s; ang = math.atan2(s, np.dot(t0, t1))
                nrm = nrm * math.cos(ang) + np.cross(v, nrm) * math.sin(ang) + v * np.dot(v, nrm) * (1 - math.cos(ang))
        b = np.cross(tang[i], nrm); frames.append((nrm.copy(), b))
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    P = []; N = []; U = []
    for i in range(n):
        nn, bb = frames[i]; rr = r if radii is None else radii[i]
        for j in range(seg + 1):
            a = 2 * math.pi * j / seg
            d = nn * math.cos(a) + bb * math.sin(a)
            P.append(path[i] + d * rr); N.append(d); U.append([j / seg + L[i] * twist, L[i] / uvs])
    I = []
    for i in range(n - 1):
        for j in range(seg):
            a = i * (seg + 1) + j; b = a + seg + 1
            I += [a, b, b + 1, a, b + 1, a + 1]
    P = np.array(P); N = np.array(N)
    t = I[:3]; f = np.cross(P[t[1]] - P[t[0]], P[t[2]] - P[t[0]])
    if np.dot(f, N[t[0]]) < 0: I = list(np.array(I).reshape(-1, 3)[:, ::-1].reshape(-1))
    mesh.add(mat, P, N, U, I, col, m)

def extrude(mesh, mat, poly, depth, m=None, col=None, uvs=1.0, cap=True, cap_mat=None, cap_uv=None):
    """prism from a 2D polygon in XY (counter-clockwise) from z=0 to z=depth"""
    poly = np.asarray(poly, float); n = len(poly)
    P = []; N = []; U = []; I = []
    L = 0
    for i in range(n):
        a = poly[i]; b = poly[(i + 1) % n]; e = b - a; ln = np.linalg.norm(e); nn = np.array([e[1], -e[0], 0]) / (ln + 1e-12)
        k = len(P)
        P += [[a[0], a[1], 0], [b[0], b[1], 0], [b[0], b[1], depth], [a[0], a[1], depth]]; N += [nn] * 4
        U += [[L / uvs, 0], [(L + ln) / uvs, 0], [(L + ln) / uvs, depth / uvs], [L / uvs, depth / uvs]]; L += ln
        I += [k, k + 1, k + 2, k, k + 2, k + 3]
    P = np.array(P); N = np.array(N)
    t = I[:3]; f = np.cross(P[t[1]] - P[t[0]], P[t[2]] - P[t[0]])
    if np.dot(f, N[0]) < 0: I = list(np.array(I).reshape(-1, 3)[:, ::-1].reshape(-1))
    mesh.add(mat, P, N, U, I, col, m)
    if cap:
        tri = ear_clip(poly)
        mn = poly.min(0); mx = poly.max(0); span = (mx - mn).max() + 1e-9
        Uc = (poly - mn) / span if cap_uv is None else cap_uv(poly)
        for z, nz in ((depth, 1), (0, -1)):
            Pc = np.c_[poly, np.full(n, z)]
            idx = np.array(tri).reshape(-1, 3)
            f = np.cross(Pc[idx[0, 1]] - Pc[idx[0, 0]], Pc[idx[0, 2]] - Pc[idx[0, 0]])
            if f[2] * nz < 0: idx = idx[:, ::-1]
            mesh.add(cap_mat or mat, Pc, [[0, 0, nz]] * n, Uc, idx.reshape(-1), col, m)

def ear_clip(poly):
    pts = [tuple(p) for p in poly]; idx = list(range(len(pts))); out = []
    def area(ix):
        s = 0
        for i in range(len(ix)): a = pts[ix[i]]; b = pts[ix[(i + 1) % len(ix)]]; s += a[0] * b[1] - b[0] * a[1]
        return s
    if area(idx) < 0: idx = idx[::-1]
    def inside(p, a, b, c):
        def sgn(p1, p2, p3): return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        d1, d2, d3 = sgn(p, a, b), sgn(p, b, c), sgn(p, c, a)
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))
    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1; done = False
        for i in range(len(idx)):
            a, b, c = idx[i - 1], idx[i], idx[(i + 1) % len(idx)]
            A, B, C = pts[a], pts[b], pts[c]
            if (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0]) <= 0: continue
            if any(inside(pts[k], A, B, C) for k in idx if k not in (a, b, c)): continue
            out += [a, b, c]; idx.pop(i); done = True; break
        if not done: break
    if len(idx) == 3: out += idx
    return out

def sphere(mesh, mat, r, seg=16, rings=10, m=None, col=None):
    prof = [(r * math.sin(math.pi * i / rings), -r * math.cos(math.pi * i / rings)) for i in range(rings + 1)]
    lathe(mesh, mat, prof, seg, m, col)

# ------------------------------------------------------------------ writer
def _img_bytes(src):
    if isinstance(src, (bytes, bytearray)): return bytes(src), 'image/png' if src[:4] == b'\x89PNG' else 'image/jpeg'
    data = open(src, 'rb').read()
    return data, 'image/png' if src.lower().endswith('.png') else 'image/jpeg'

def write(path, mesh, mats, name='spire', quantize=False):
    """mats: name -> dict(tex=path|bytes, nrm=path, color=(r,g,b,a), metal=0, rough=0.8, emis=(r,g,b), emis_tex=path,
              alpha='OPAQUE'|'BLEND'|'MASK', double=False, unlit=False)"""
    buf = bytearray(); views = []; accs = []
    def add_view(data, target=None):
        while len(buf) % 4: buf.append(0)
        off = len(buf); buf.extend(data)
        v = {'buffer': 0, 'byteOffset': off, 'byteLength': len(data)}
        if target: v['target'] = target
        views.append(v); return len(views) - 1
    def add_acc(arr, ctype, typ, target, minmax=False, normalized=False):
        arr = np.ascontiguousarray(arr)
        vi = add_view(arr.tobytes(), target)
        a = {'bufferView': vi, 'componentType': ctype, 'count': int(arr.shape[0]), 'type': typ}
        if normalized: a['normalized'] = True
        if minmax: a['min'] = arr.min(0).tolist(); a['max'] = arr.max(0).tolist()
        accs.append(a); return len(accs) - 1
    images = []; textures = []; materials = []; img_cache = {}
    def tex(src):
        key = src if isinstance(src, str) else id(src)
        if key in img_cache: return img_cache[key]
        data, mime = _img_bytes(src)
        vi = add_view(data); images.append({'bufferView': vi, 'mimeType': mime})
        textures.append({'source': len(images) - 1, 'sampler': 0}); img_cache[key] = len(textures) - 1
        return img_cache[key]
    ext_used = set()
    prims = []
    for mname, bk in mesh.b.items():
        if not bk[0]: continue
        md = mats[mname]
        P = np.vstack(bk[0]).astype(np.float32); N = np.vstack(bk[1]).astype(np.float32); U = np.vstack(bk[2]).astype(np.float32)
        C = np.vstack(bk[3]).astype(np.float32); I = np.concatenate(bk[4])
        attrs = {'POSITION': add_acc(P, 5126, 'VEC3', 34962, True), 'NORMAL': add_acc(N, 5126, 'VEC3', 34962), 'TEXCOORD_0': add_acc(U, 5126, 'VEC2', 34962)}
        if not np.allclose(C, 1.0): attrs['COLOR_0'] = add_acc(np.round(np.clip(C, 0, 1) * 255).astype(np.uint8), 5121, 'VEC4', 34962, normalized=True)   # (v24) 4 bytes a vertex, not 16 (core glTF, no extension)
        if P.shape[0] < 65536: ia = add_acc(I.astype(np.uint16), 5123, 'SCALAR', 34963)
        else: ia = add_acc(I.astype(np.uint32), 5125, 'SCALAR', 34963)
        pbr = {'baseColorFactor': list(md.get('color', (1, 1, 1, 1))), 'metallicFactor': md.get('metal', 0.0), 'roughnessFactor': md.get('rough', 0.85)}
        if md.get('tex') is not None: pbr['baseColorTexture'] = {'index': tex(md['tex'])}
        mat = {'name': mname, 'pbrMetallicRoughness': pbr}
        if md.get('nrm') is not None: mat['normalTexture'] = {'index': tex(md['nrm']), 'scale': md.get('nrm_scale', 1.0)}
        if md.get('mr') is not None: pbr['metallicRoughnessTexture'] = {'index': tex(md['mr'])}     # G = roughness, B = metalness (multiplied by the factors)
        if md.get('emis') is not None: mat['emissiveFactor'] = list(md['emis'])[:3]
        if md.get('emis_tex') is not None: mat['emissiveTexture'] = {'index': tex(md['emis_tex'])}
        if md.get('emis_strength'):
            mat['extensions'] = {'KHR_materials_emissive_strength': {'emissiveStrength': md['emis_strength']}}; ext_used.add('KHR_materials_emissive_strength')
        if md.get('unlit'):
            mat.setdefault('extensions', {})['KHR_materials_unlit'] = {}; ext_used.add('KHR_materials_unlit')
        if md.get('alpha'): mat['alphaMode'] = md['alpha']
        if md.get('alpha') == 'MASK': mat['alphaCutoff'] = md.get('cutoff', 0.5)
        if md.get('double'): mat['doubleSided'] = True
        materials.append(mat)
        prims.append({'attributes': attrs, 'indices': ia, 'material': len(materials) - 1})
    while len(buf) % 4: buf.append(0)
    gl = {'asset': {'version': '2.0', 'generator': 'mudwater-spire glb.py'}, 'scene': 0, 'scenes': [{'nodes': [0]}],
          'nodes': [{'mesh': 0, 'name': name}], 'meshes': [{'primitives': prims, 'name': name}],
          'accessors': accs, 'bufferViews': views, 'buffers': [{'byteLength': len(buf)}], 'materials': materials}
    if textures:
        gl['textures'] = textures; gl['images'] = images
        gl['samplers'] = [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497}]
    if ext_used: gl['extensionsUsed'] = sorted(ext_used)
    js = json.dumps(gl, separators=(',', ':')).encode()
    while len(js) % 4: js += b' '
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(buf))
    out += struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(buf), 0x004E4942) + bytes(buf)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    open(path, 'wb').write(out)
    return {'file': os.path.basename(path), 'tris': int(sum(len(np.concatenate(bk[4])) // 3 for bk in mesh.b.values() if bk[4])), 'kb': len(out) // 1024}

def read_glb(path):
    data = open(path, 'rb').read(); jl = struct.unpack('<I', data[12:16])[0]
    js = json.loads(data[20:20 + jl]); bin_ = data[20 + jl + 8:]
    return js, bin_
