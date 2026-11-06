"""HALL OF FAKES load test: 100 bots click portraits as fast as players would (each bot every 0.4-1.2 s, wrong picks lock them 5 s)
for 60 s of a round, then one bot finds the real one. Measures how long the world takes per click, how many elements it creates,
and that every click is handled. python3 hallload.py /home/claude/spire/out/spire.html"""
import sys, time, json, random
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    NB = 100
    pg.evaluate("(n) => { for (let id = 1; id <= n + 1; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }", NB)
    say = lambda c: pg.evaluate("(c) => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:1}, bubbles:true}))", c)
    ack = lambda: json.loads(pg.evaluate("() => document.querySelector('[data-ack]').getAttribute('data-ack')"))['t']
    say("build"); time.sleep(4)
    say("hall open"); print(ack()); time.sleep(1)
    n0 = pg.evaluate("() => document.querySelectorAll('*').length")
    # every bot clicks on its own schedule inside the page (real timers), for 60 s; we record handler time per click
    r = pg.evaluate("""async (NB) => {
      const ps = Array.from(document.querySelectorAll('m-model')).filter(m => /portraits\\/pf_/.test(m.getAttribute('src')));
      const real = ps.find(m => m.getAttribute('src').includes('pf_' + String(__realHall()).padStart(4, '0')));
      let clicks = 0, worst = 0, total = 0, maxEls = 0; const t0 = performance.now();
      const bots = [];
      for (let id = 2; id <= NB + 1; id++) bots.push((async () => {
        while (performance.now() - t0 < 60000) {
          await new Promise(r => setTimeout(r, 400 + Math.random() * 800));
          let m = ps[Math.floor(Math.random() * ps.length)]; if (m === real) continue;
          const a = performance.now(); m.dispatchEvent(new CustomEvent('click', { detail: { connectionId: id }, bubbles: true }));
          const d = performance.now() - a; clicks++; total += d; worst = Math.max(worst, d);
          if (clicks % 200 === 0) maxEls = Math.max(maxEls, document.querySelectorAll('*').length);
        }
      })());
      await Promise.all(bots);
      window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:150}})); real.dispatchEvent(new CustomEvent('click', { detail: { connectionId: 150 }, bubbles: true }));   // a fresh player (bots may be locked out)
      return { clicks, avgMs: +(total / clicks).toFixed(3), worstMs: +worst.toFixed(2), maxEls, ps: ps.length };
    }""", NB)
    print("100 bots for 60 s:", r, "| elements before", n0)
    acks = pg.evaluate("() => JSON.parse(document.querySelector('[data-ack]').getAttribute('data-ack')).l.map(a => a.t)")
    print("winner registered:", any("ROUND 1 WON" in a for a in acks))
    print("ERRORS:", errs or "none"); b.close()
