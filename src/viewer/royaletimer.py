import sys, time, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    pg.evaluate("() => { for (let id = 1; id <= 3; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }")
    say = lambda c: pg.evaluate("(c) => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:1}, bubbles:true}))", c)
    say("build"); time.sleep(3)
    pg.evaluate("""() => { const f = (n, name, d) => n.dispatchEvent(new CustomEvent(name, {detail: d, bubbles: true}));
      const slabs = Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('collision-interval') === '90' && c.getAttribute('depth') === '5.5');
      const tiles = Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('width') === '2.46' && c.getAttribute('height') === '0.1');
      f(slabs[0], 'collisionstart', {connectionId: 2}); f(slabs[3], 'collisionstart', {connectionId: 3});
      document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 royale start', connectionId:1}, bubbles:true}));
      f(tiles[44], 'click', {connectionId: 2}); setTimeout(() => f(tiles[45], 'click', {connectionId: 3}), 500); }""")
    t0 = time.time()
    while time.time() - t0 < 200:
        time.sleep(5)
        l = json.loads(pg.evaluate("() => document.querySelector('[data-ack]').getAttribute('data-ack')"))['l']
        if any('OVER' in m['t'] for m in l): break
    print("ended after", round(time.time() - t0), "s:", [m['t'] for m in l if 'OVER' in m['t']])
    print("ERRORS:", errs or "none"); b.close()
