"""Mud Royale: refills (a card every 10 s, max 5) + the 30-second finale + full 3:00 game. ~3.2 min."""
import sys, time, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    pg.evaluate("() => { for (let id = 1; id <= 3; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }")
    pg.evaluate("() => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true}))"); time.sleep(3)
    pg.evaluate("""() => { const f = (n, name, d) => n.dispatchEvent(new CustomEvent(name, {detail: d, bubbles: true}));
      window.__f = f;
      window.__tiles = Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('width') === '2.46' && c.getAttribute('height') === '0.1');
      const slabs = Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('collision-interval') === '90' && c.getAttribute('depth') === '5.5');
      f(slabs[0], 'collisionstart', {connectionId: 2}); f(slabs[1], 'collisionstart', {connectionId: 3});
      document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 royale start', connectionId:1}, bubbles:true})); }""")
    hand = lambda id: pg.evaluate("""(id) => { const g = Array.from(document.querySelectorAll('m-group[visible-to="' + id + '"]')).filter(g => g.querySelector('m-image[src*="royale/c_"]'))[0]; return g ? g.querySelectorAll('m-image').length : 0; }""", id)
    t0 = time.time(); nxt = 0
    for k in range(5):                        # bot 2 dumps all 5 cards
        pg.evaluate("(i) => __f(__tiles[i], 'click', {connectionId: 2})", nxt); nxt += 1; time.sleep(0.4)
    log = []
    print("after playing 5:", hand(2), "cards | bot 3 untouched:", hand(3))
    for sec in (11.5, 22, 33):
        time.sleep(max(0, sec - (time.time() - t0))); log.append((sec, hand(2), hand(3)))
    print("bot 2 cards at ~11 s / 22 s / 33 s:", [h for _, h, _ in log], "| bot 3 stays at", [h3 for _, _, h3 in log])
    assert [h for _, h, _ in log] == [1, 2, 3] and all(h3 == 5 for _, _, h3 in log)
    time.sleep(max(0, 151.5 - (time.time() - t0)))
    bar = pg.evaluate("() => Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('width') === '6.2').map(c => c.getAttribute('color'))")
    msg = pg.evaluate("() => document.querySelectorAll('m-group[visible-to=\"2\"] m-model[src*=\"r_30\"]').length")
    print("at 2:28 left-ish: bar colours", bar, "| 30-second message models for bot 2:", msg)
    while time.time() - t0 < 200:
        time.sleep(3)
        l = json.loads(pg.evaluate("() => document.querySelector('[data-ack]').getAttribute('data-ack')"))['l']
        if any('OVER' in m['t'] for m in l): break
    print("ended after", round(time.time() - t0), "s:", [m['t'] for m in l if 'OVER' in m['t']][-1:])
    print("ERRORS:", errs or "none"); b.close()
