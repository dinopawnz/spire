import time, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page()
    pg.goto("file:///home/claude/spire/out/spire.html"); time.sleep(1)
    pg.evaluate("() => { for (let id = 1; id <= 12; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }")
    pg.evaluate("() => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true}))"); time.sleep(4)
    D = json.loads(open('/home/claude/spire/out/spire.html').read().split('const D = ')[1].split(';\n')[0])
    H = [h for h in D['bandHits'] if h[7] == 'drum']
    got = []
    for i, h in enumerate(H):
        r = pg.evaluate("""([h, id]) => { const c = Array.from(document.querySelectorAll('m-cube')).find(c => Math.abs(+c.getAttribute('x') - h[0]) < 0.002 && Math.abs(+c.getAttribute('z') - h[2]) < 0.002 && Math.abs(+c.getAttribute('width') - h[3]) < 0.002);
            if (!c) return 'NO BOX'; c.dispatchEvent(new CustomEvent('click', {detail: {connectionId: id}, bubbles: true}));
            const a = Array.from(document.querySelectorAll('m-audio')).map(a => a.getAttribute('src')).filter(s => /band_drum/.test(s)); return a[a.length - 1].split('/').pop().split('?')[0]; }""", [h, 2 + i])
        got.append((h[8], r)); time.sleep(2.6)
    for k, r in got: print(('OK   ' if r == 'band_drum_%s.mp3' % k else 'FAIL ') + k, '->', r)
    b.close()
