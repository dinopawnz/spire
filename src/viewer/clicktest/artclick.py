"""(v51) every escape keypad key and every chest must be clickable: export the world in a live game (all 4 rooms showing, chests in
rooms 1/2/4 half opened so their notes float), then cast click rays at each key / chest from where a player stands (straight on, from
the sides, from above) and report anything in the way.   python3 escclick.py /home/claude/spire/out/spire.html"""
import sys, time, json, math, subprocess
from collections import Counter
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page()
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    pg.evaluate("() => { for (let id = 1; id <= 14; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }")
    pg.evaluate("() => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true}))"); time.sleep(4)
    pg.evaluate("""() => { const fire = (n, name, d) => n.dispatchEvent(new CustomEvent(name, {detail: d, bubbles: true}));
      const rugs = Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('collision-interval') === '120');
      rugs.forEach((r, t) => fire(r, 'collisionstart', {connectionId: 2 + t}));
      const ES = window.__ES; ES.start(); [1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5].forEach(k => ES.skip(k));
      const hb = (g) => Array.from(g.children).filter(c => c.tagName.toLowerCase() === 'm-cube' && c.getAttribute('opacity') === '0');
      ES._T.forEach((T) => T.chests.forEach((C, i) => { if (i % 2 === 0 && C.room <= T.stage) fire(hb(C.g)[0], 'click', {connectionId: 2}); }));
      const AWW = 24.0; const big = Array.from(document.querySelectorAll('m-cube')).find(c => c.getAttribute('collide') === 'true' && c.getAttribute('opacity') === '0' && Math.abs(+c.getAttribute('width') - AWW) < 0.01);
      big.setAttribute('data-tag', 'key art');
      Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('opacity') === '0' && c.getAttribute('width') === '0.18' && c.getAttribute('height') === '0.3').forEach((c, i) => c.setAttribute('data-tag', 'shut pot ' + i)); }""")
    time.sleep(2)
    out = pg.evaluate("""() => {
      const num = (e, a, d) => { const v = parseFloat(e.getAttribute(a)); return isNaN(v) ? d : v; };
      const mat = (e) => { let m = new DOMMatrix(); const chain = []; for (let n = e; n && n.tagName && n.tagName.toLowerCase().startsWith('m-'); n = n.parentElement) chain.unshift(n);
        for (const n of chain) { m = m.translate(num(n,'x',0), num(n,'y',0), num(n,'z',0)).rotate(num(n,'rx',0), num(n,'ry',0), num(n,'rz',0)).scale(num(n,'sx',1), num(n,'sy',1), num(n,'sz',1)); }
        return Array.from(m.toFloat64Array()); };
      const vis = (e) => { for (let n = e; n && n.tagName; n = n.parentElement) { if (n.getAttribute && n.getAttribute('visible') === 'false') return false; } return true; };
      const els = [];
      document.querySelectorAll('m-model, m-cube, m-cylinder, m-sphere, m-image, m-label, m-plane').forEach((e, i) => {
        els.push({ i, t: e.tagName.toLowerCase(), src: e.getAttribute('src') || '', tag: e.getAttribute('data-tag') || '', m: mat(e), collide: e.getAttribute('collide') !== 'false', vis: vis(e), op: num(e,'opacity',1),
          w: num(e,'width',1), h: num(e,'height',1), d: num(e,'depth',1), r: num(e,'radius',0.5) });
      });
      return els; }""")
    b.close()
json.dump(out, open('/home/claude/viewer/clicktest/scene2.json', 'w'))
tg = []
for e in out:
    if not e['tag']: continue
    m = e['m']; x, y, z = m[12], m[13], m[14]; ry = math.degrees(math.atan2(m[8], m[10]))
    if e['tag'] == 'key art':
        import math as _m
        a = _m.radians(ry)
        for lx in (-10, -5, 0, 5, 10):
            for ly in (-3, 0, 3):
                tg.append([x + lx * _m.cos(a), y + ly, z - lx * _m.sin(a), ry, e['i'], 3.0, -1.0 - ly * 0.5])
        continue
    if e['tag'].startswith('key'):
        for dist in (1.2, 2.2):
            for yaw in (-30, 0, 30):
                for dy in (0.0, 1.0): tg.append([x, y, z, ry + yaw, e['i'], dist, dy])
    elif e['tag'].startswith('shut'):
        for yaw in (-40, 0, 40):
            for (dist, dy) in ((1.5, 1.2), (2.5, 2.0), (1.2, 0.3)): tg.append([x, y, z, ry + yaw, e['i'], dist, dy])
srv = subprocess.Popen(['python3', '-m', 'http.server', '8765', '-d', '/home/claude'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = b.new_page(); pg.on('pageerror', lambda e: print('ERR', e))
        pg.goto('http://localhost:8765/viewer/clicktest/ray2.html'); pg.wait_for_function('window.__ready', timeout=600000)
        res = pg.evaluate('(t) => window.__test(t)', tg)
        b.close()
finally:
    srv.terminate()
tag = {e['i']: e['tag'] for e in out}
keys = [r for r in res if tag[r['label']].startswith('key')]; ch = [r for r in res if tag[r['label']].startswith('shut')]
bad = lambda r: r['colliders'] or r['visible'] or r['me'] is None
print('art wall + pots: targets %d, rays %d, blocked %d' % (len(set(r['label'] for r in keys)), len(keys), sum(1 for r in keys if bad(r))))
print('closed chests %d, rays %d, blocked %d' % (len(set(r['label'] for r in ch)), len(ch), sum(1 for r in ch if bad(r))))
print(Counter((h['src'].split('/')[-1] or h['t']) + (' (collider)' if h['col'] else '') for r in res if bad(r) for h in (r['colliders'] + r['visible'])).most_common(12))
print('hidden boxes in the way (other buttons):', Counter(tag[r['label']].split()[0] for r in res if r['hidden']))
for r in [r for r in res if bad(r)][:5]: print(tag[r['label']], r)
