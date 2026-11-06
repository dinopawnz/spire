import sys, time, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    pg.evaluate("() => { for (let id = 1; id <= 4; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true})); }")
    time.sleep(7)
    r = pg.evaluate("""() => { const out = [];
      document.querySelectorAll('m-label').forEach(l => { let n = l, path = []; while (n && n.parentElement) { if (n.id) path.push('#' + n.id); n = n.parentElement; }
        out.push([String(l.getAttribute('content')).slice(0, 50), l.getAttribute('visible-to') || l.parentElement.getAttribute('visible-to') || 'everyone', l.getAttribute('x') + ',' + l.getAttribute('y') + ',' + l.getAttribute('z'), path.join(' ')]); });
      return { labels: out, images: document.querySelectorAll('m-image').length, models: document.querySelectorAll('m-model').length }; }""")
    print("m-label (text) elements after the build:", len(r['labels']))
    for l in r['labels']: print("  ", l)
    print("m-image:", r['images'], " m-model:", r['models'])
    print("ERRORS:", errs or "none"); b.close()
