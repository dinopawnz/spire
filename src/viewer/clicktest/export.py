"""export every element of the built world (after LIVE BUILD) with its world matrix -> /home/claude/viewer/clicktest/scene.json"""
import sys, time, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page()
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    pg.evaluate("() => { for (let id = 1; id <= 3; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }")
    pg.evaluate("() => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true}))")
    time.sleep(8)
    out = pg.evaluate("""() => {
      const num = (e, a, d) => { const v = parseFloat(e.getAttribute(a)); return isNaN(v) ? d : v; };
      const mat = (e) => { let m = new DOMMatrix(); const chain = []; for (let n = e; n && n.tagName && n.tagName.toLowerCase().startsWith('m-'); n = n.parentElement) chain.unshift(n);
        for (const n of chain) { m = m.translate(num(n,'x',0), num(n,'y',0), num(n,'z',0)).rotate(num(n,'rx',0), num(n,'ry',0), num(n,'rz',0)).scale(num(n,'sx',1), num(n,'sy',1), num(n,'sz',1)); }
        return Array.from(m.toFloat64Array()); };
      const vis = (e) => { for (let n = e; n && n.tagName; n = n.parentElement) { if (n.getAttribute && n.getAttribute('visible') === 'false') return false; } return true; };
      const els = [];
      document.querySelectorAll('m-model, m-cube, m-cylinder, m-sphere, m-image, m-label, m-plane').forEach((e, i) => {
        const t = e.tagName.toLowerCase();
        els.push({ i, t, src: e.getAttribute('src') || '', m: mat(e), collide: e.getAttribute('collide') !== 'false', vis: vis(e), op: num(e,'opacity',1),
          w: num(e,'width',1), h: num(e,'height',1), d: num(e,'depth',1), r: num(e,'radius',0.5), click: !!(e._listeners) });
      });
      return els; }""")
    json.dump(out, open('/home/claude/viewer/clicktest/scene.json', 'w'))
    print(len(out), 'elements')
    b.close()
