import sys, time, json, re
from playwright.sync_api import sync_playwright
page = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + page); time.sleep(1)
    say = lambda c: pg.evaluate("""(c) => { document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:1}, bubbles:true})); }""", c)
    ack = lambda: json.loads(pg.evaluate("() => document.querySelector('[data-ack]').getAttribute('data-ack')"))['t']
    pg.evaluate("() => window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:1}}))")
    say("build"); time.sleep(4)
    stat = lambda: (say("liftstat"), json.loads(ack()[6:]))[1]
    print("start", stat())
    # 1. watchdog heals a jammed idle lift by itself
    say("liftjam B"); print(ack()); time.sleep(0.2); print("jammed", stat()["B"])
    time.sleep(4); s = stat()["B"]; print("after 4 s (no press):", s); assert not s["busy"] and s["heals"] == 1
    # 2. a jammed lift answers a call right away
    say("liftjam D"); say("lift D roof"); print(ack()); time.sleep(0.3); s = stat()["D"]; print("jam + call:", s); assert s["heals"] == 1 and s["busy"]
    # it really rides: wait for the trip
    for i in range(60):
        time.sleep(1); s = stat()["D"]
        if s["at"] == "roof" and s["open"]: break
    print("D after ride:", s); assert s["at"] == "roof"
    # 3. B still works normally after its heal
    say("lift B cards"); 
    for i in range(60):
        time.sleep(1); s = stat()["B"]
        if s["at"] == "cards" and s["open"]: break
    print("B after ride:", s); assert s["at"] == "cards"
    print("ERRORS:", errs or "none"); b.close()
