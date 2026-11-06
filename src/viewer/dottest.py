import sys, time, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    say = lambda c: pg.evaluate("(c) => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:1}, bubbles:true}))", c)
    ack = lambda: json.loads(pg.evaluate("() => document.querySelector('[data-ack]').getAttribute('data-ack')"))['t']
    pg.evaluate("() => { for (const id of [1,2,3]) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }")
    say("build"); time.sleep(3)
    r = pg.evaluate("""async () => { const sleep = (ms) => new Promise(r => setTimeout(r, ms)); const fire = (n, name, d) => n.dispatchEvent(new CustomEvent(name, {detail: d, bubbles: true}));
      const big = Array.from(document.querySelectorAll('m-cube')).find(c => c.getAttribute('width') === '24' && c.getAttribute('height') === '8');
      const AG = big.parentNode, dots = () => Array.from(AG.children).filter(c => c.tagName === 'M-CUBE' && c.getAttribute('depth') === '0.01');
      const pots = Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('width') === '0.18' && c.getAttribute('height') === '0.3');
      fire(pots[8], 'click', {connectionId: 2});
      for (let i = 0; i < 30; i++) { fire(big, 'click', {connectionId: 2, position: {x: -3 + i * 0.1, y: 0.5, z: 0.03}}); await sleep(95); }   // a line of dots
      const line = dots().length, one = dots()[0], w = one.getAttribute('width'), col = one.getAttribute('color');
      fire(big, 'click', {connectionId: 3, position: {x: -3.0, y: 0.5, z: 0.03}}); await sleep(100);      // red over the first blue dot: replaced, not stacked
      const after = dots().length, recol = dots().find(d => Math.abs(+d.getAttribute('x') - (-2.95)) < 0.01);
      fire(pots[13], 'click', {connectionId: 2}); await sleep(100);
      fire(big, 'click', {connectionId: 2, position: {x: -2.0, y: 0.5, z: 0.03}}); await sleep(100);
      return { line, size: w, col, after, recoloured: recol && recol.getAttribute('color'), afterErase: dots().length }; }""")
    print(r); say("art"); print(ack())
    print("ERRORS:", errs or "none"); b.close()
