import time, json
from collections import Counter
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page()
    pg.goto("file:///home/claude/spire/out/spire.html"); time.sleep(1)
    pg.evaluate("() => { for (let i = 1; i < 6; i++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:i}})); document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true})); }"); time.sleep(3)
    print(pg.evaluate("""() => { const fire = (n, name, d) => n.dispatchEvent(new CustomEvent(name, {detail: d, bubbles: true}));
      const slabs = Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('collision-interval') === '90' && c.getAttribute('depth') === '5.5');
      const RY = window.__RY; RY.open(); fire(slabs[0], 'collisionstart', {connectionId: 2}); fire(slabs[1], 'collisionstart', {connectionId: 3}); const r = RY.start();
      const LV = window.__RLV, l1 = LV.map((v, i) => v === 1 ? i : -1).filter(i => i >= 0);
      const t2 = RY.roster.get(2); for (let i = 0; i < 12; i++) RY.board[i] = { team: t2, c: l1[i % l1.length], g: document.createElement('m-group') };
      return r; }"""))
    got = Counter()
    for it in range(14):
        pg.evaluate("() => { const H = window.__RY.hands.get(2); H.cards = H.cards.map(() => null); H.due = H.cards.map(() => 1); }")
        time.sleep(1.3)
        for c in pg.evaluate("() => window.__RY.hands.get(2).cards.map(c => c === null ? 0 : window.__RLV[c])"):
            if c: got[c] += 1
    n = sum(got.values()); print('cards dealt', n, {k: '%d%%' % (100 * v // n) for k, v in sorted(got.items())})
    b.close()
