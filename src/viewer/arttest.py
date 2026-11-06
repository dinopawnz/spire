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
    r = pg.evaluate("""() => {
      const fire = (n, name, d) => n.dispatchEvent(new CustomEvent(name, {detail: d, bubbles: true}));
      // the canvas group: the m-group holding the 24 m wide click target
      const big = Array.from(document.querySelectorAll('m-cube')).find(c => c.getAttribute('width') === '24' && c.getAttribute('height') === '8');
      const AG = big.parentNode;
      const pots = Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('width') === '0.18' && c.getAttribute('height') === '0.3');
      fire(pots[8], 'click', {connectionId: 2});          // player 2 picks blue
      fire(big, 'click', {connectionId: 2, position: {x: -11.9, y: -3.9, z: 0.03}});   // bottom-left square
      fire(big, 'click', {connectionId: 3, position: {x: 0.1, y: 0.1, z: 0.03}});      // player 3, default red, middle
      const painted = () => Array.from(AG.children).filter(c => c.tagName === 'M-CUBE' && c.getAttribute('depth') === '0.02').map(c => [c.getAttribute('x'), c.getAttribute('y'), c.getAttribute('color')]);
      const a = painted();
      fire(pots[13], 'click', {connectionId: 2});         // eraser
      return new Promise(res => setTimeout(() => { fire(big, 'click', {connectionId: 2, position: {x: -11.9, y: -3.9, z: 0}}); 
        const b_ = painted();
        fire(big, 'click', {connectionId: 3});            // a click with no position -> grid mode
        const grid = Array.from(AG.children).filter(c => c.tagName === 'M-CUBE' && c.getAttribute('depth') === '0.05');
        setTimeout(() => { fire(grid[31], 'click', {connectionId: 3}); 
          const pr = Array.from(document.querySelectorAll('m-prompt')).find(p => (p.getAttribute('message') || '').includes('Art Wall'));
          fire(pr, 'prompt', {connectionId: 3, value: 'Dinopawnz'});
          const lab = Array.from(document.querySelectorAll('m-label')).find(l => (l.getAttribute('content') || '').includes('Dinopawnz'));
          res({pots: pots.length, a, b: b_, grid: grid.length, afterGrid: painted(), board: lab && lab.getAttribute('content')}); }, 100); }, 100)); }""")
    print(json.dumps(r, indent=0)[:900])
    say("art"); print(ack()); say("art clear"); print(ack()); say("art"); print(ack())
    print("ERRORS:", errs or "none"); b.close()
