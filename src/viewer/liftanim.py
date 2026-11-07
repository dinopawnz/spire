import time
from playwright.sync_api import sync_playwright
JS = r"""() => Array.from(document.querySelectorAll('m-attr-anim')).filter(a => a.getAttribute('attr') === 'y' || a.getAttribute('attr') === 'sy').map(a => (a.parentElement.getAttribute('src') || 'group').split('/').pop().split('?')[0]).join(',')"""
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page()
    pg.goto("file:///home/claude/spire/out/spire.html"); time.sleep(1)
    pg.evaluate("() => { for (let id = 1; id <= 3; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }")
    say = lambda c: pg.evaluate("(c) => { document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:1}, bubbles:true})); return JSON.parse(document.querySelector('[data-ack]').getAttribute('data-ack')).t; }", c)
    say("build"); time.sleep(3)
    for f in ["3", "1", "4", "0"]:
        print(say("lift B " + f)); time.sleep(16); print('  ', pg.evaluate(JS))
    b.close()
