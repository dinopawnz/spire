import sys, time, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    say = lambda c: pg.evaluate("(c) => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:1}, bubbles:true}))", c)
    pg.evaluate("() => { for (const id of [1,2]) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }")
    say("build"); time.sleep(7)
    q = "() => ({ cards: document.querySelectorAll('m-model[src*=\"gc_\"]').length, cardAnims: document.querySelectorAll('m-attr-anim[data-lite-anim]').length, anims: document.querySelectorAll('m-attr-anim').length })"
    print("normal:", pg.evaluate(q)); say("lite on"); time.sleep(0.5); print("lite on:", pg.evaluate(q)); say("lite off"); time.sleep(0.5); print("lite off:", pg.evaluate(q))
    print("ERRORS:", errs or "none"); b.close()
