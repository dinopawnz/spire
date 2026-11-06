import sys, time, json, collections
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page()
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    pg.evaluate("() => { for (let id = 1; id <= 3; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true})); }")
    time.sleep(8)
    r = pg.evaluate("""() => Array.from(document.querySelectorAll('m-attr-anim')).map(a => { const p = a.parentElement; const m = p.tagName === 'M-MODEL' ? p : (p.querySelector('m-model') || p.querySelector('m-image') || p);
        const s = (m.getAttribute('src') || m.tagName).split('/').pop().split('?')[0].replace(/\\d+/g, '#'); return s + ' :' + a.getAttribute('attr') + (a.getAttribute('loop') === 'false' ? ' once' : ''); })""")
    b.close()
c = collections.Counter(r)
for k, v in c.most_common(30): print("%4d  %s" % (v, k))
