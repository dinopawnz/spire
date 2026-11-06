import sys, time, json, os, struct, re, collections
from playwright.sync_api import sync_playwright
G = '/home/claude/spire/out/glb/'
def tris(f):
    try:
        b = open(f, 'rb').read(); n = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + n]); t = 0; prims = 0
        for m in j['meshes']:
            for p in m['primitives']:
                a = j['accessors'][p['indices']] if 'indices' in p else j['accessors'][p['attributes']['POSITION']]; t += a['count'] // 3; prims += 1
        return t, prims
    except Exception: return 0, 1
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page()
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    pg.evaluate("() => { for (let id = 1; id <= 3; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true})); }")
    time.sleep(8)
    r = pg.evaluate("""() => { const pos = (n) => { let y = 0; for (let e = n; e && e.tagName; e = e.parentElement) y += +(e.getAttribute('y') || 0); return y; };
        return { models: Array.from(document.querySelectorAll('m-model')).map(m => [m.getAttribute('src').split('/').pop().split('?')[0], pos(m), m.querySelector('m-attr-anim') || m.parentElement.querySelector(':scope > m-attr-anim') ? 1 : 0]),
                 images: document.querySelectorAll('m-image').length, cubes: document.querySelectorAll('m-cube').length, spheres: document.querySelectorAll('m-sphere').length,
                 cyl: document.querySelectorAll('m-cylinder').length, anims: document.querySelectorAll('m-attr-anim').length, audio: document.querySelectorAll('m-audio').length,
                 all: document.querySelectorAll('*').length,
                 animAttrs: Object.entries(Array.from(document.querySelectorAll('m-attr-anim')).reduce((o, a) => { const k = a.getAttribute('attr'); o[k] = (o[k] || 0) + 1; return o; }, {})) }; }""")
    b.close()
cat = collections.defaultdict(lambda: [0, 0, 0]); floors = collections.defaultdict(lambda: [0, 0, 0])
FL = [(-1e9, 2.5, 'outside'), (2.5, 10.4, 'lounge'), (10.4, 31.9, 'hall+gallery'), (31.9, 39.9, 'floor3'), (39.9, 50.9, 'floor4'), (50.9, 1e9, 'roof+sky')]
tot_t = tot_p = 0
for (src, y, an) in r['models']:
    t, pr = tris(G + src)
    key = re.sub(r'(_\d+)+$|\d+$', '', src.replace('.glb', ''))
    cat[key][0] += 1; cat[key][1] += t; cat[key][2] += pr
    fl = next(n for (a, b_, n) in FL if a <= y < b_); floors[fl][0] += 1; floors[fl][1] += t; floors[fl][2] += pr
    tot_t += t; tot_p += pr
print("TOTAL models %d | triangles %.2fM | draw pieces (mesh primitives) %d" % (len(r['models']), tot_t / 1e6, tot_p))
print("images %d cubes %d spheres %d cylinders %d | constantly-moving animations %d | sounds %d | all elements %d" % (r['images'], r['cubes'], r['spheres'], r['cyl'], r['anims'], r['audio'], r['all']))
print("animations by attribute:", sorted(r['animAttrs'], key=lambda x: -x[1])[:8])
print("\nBY FLOOR (models, triangles, draw pieces):")
for k, v in sorted(floors.items(), key=lambda x: -x[1][1]): print("  %-14s %5d models  %6.2fM tris  %5d pieces" % (k, v[0], v[1] / 1e6, v[2]))
print("\nTOP 28 by triangles (count, tris, pieces):")
for k, v in sorted(cat.items(), key=lambda x: -x[1][1])[:28]: print("  %-26s x%-4d %7.0fk tris %5d pieces" % (k, v[0], v[1] / 1e3, v[2]))
print("\nTOP 12 by draw pieces:")
for k, v in sorted(cat.items(), key=lambda x: -x[1][2])[:12]: print("  %-26s x%-4d %5d pieces" % (k, v[0], v[2]))
