import sys, time, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    pg.evaluate("() => { for (let id = 1; id <= 3; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true})); }")
    time.sleep(7)
    r = pg.evaluate("""() => ({ visTo: Array.from(document.querySelectorAll('[visible-to]')).filter(n => !n.closest('[data-priv]')).map(n => n.tagName + ' ' + (n.getAttribute('visible-to')||'').slice(0,20) + ' kids=' + n.children.length).slice(0, 12),
        gatesInGroups: Array.from(document.querySelectorAll('m-model[src*="sp_lift_lgate"]')).filter(g => g.closest('[visible-to]')).length,
        gates: document.querySelectorAll('m-model[src*="sp_lift_lgate"]').length })""")
    print(json.dumps(r, indent=0)); print("ERRORS:", errs or "none"); b.close()
