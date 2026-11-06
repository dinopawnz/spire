import sys, time, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    say = lambda c: pg.evaluate("(c) => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:1}, bubbles:true}))", c)
    ack = lambda: json.loads(pg.evaluate("() => document.querySelector('[data-ack]').getAttribute('data-ack')"))['t']
    pg.evaluate("() => { for (let id = 1; id <= 3; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }")
    say("build"); time.sleep(4)
    gates = lambda: pg.evaluate("""() => Array.from(document.querySelectorAll('m-model[src*="sp_lift_lgate"]')).map(g => [Math.round(+g.getAttribute('x')), +(+g.getAttribute('y')).toFixed(1), g.getAttribute('sx'), Array.from(g.children).map(a => a.getAttribute('attr') + ':' + a.getAttribute('start') + '>' + a.getAttribute('end')).join(',')])""")
    print("stops:", ack() if False else "")
    for dest in ("cards", "rooms", "lounge", "cards"):
        say("lift B " + dest); print(ack())
        for i in range(70):
            time.sleep(1); say("liftstat"); st = json.loads(ack()[6:])["B"]
            if st["at"] == dest and st["open"] and not st["busy"]: break
        time.sleep(1.5)
        g = [x for x in gates() if x[0] > 0]
        print(dest, st, "\n   B landing gates (x, y, sx, anims):", g)
    print("ERRORS:", errs or "none"); b.close()
