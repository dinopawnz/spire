import sys, time, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    pg.evaluate("() => { for (const id of [1,2]) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true})); }")
    time.sleep(3)
    r = pg.evaluate("""async () => { const sleep = (ms) => new Promise(r => setTimeout(r, ms)); const fire = (n, d) => n.dispatchEvent(new CustomEvent('click', {detail: d, bubbles: true}));
      
      const piv = Array.from(document.querySelectorAll('m-model[src*="poolcue"]'))[0].parentElement.parentElement.parentElement;
      const before = piv.getAttribute('ry'); const hb = Array.from(document.querySelectorAll('m-image[src*="pool_btn_l"]'))[0].parentElement.querySelector('m-cube');
      for (let i = 0; i < 4; i++) { fire(hb, {connectionId: 2}); await sleep(150); }
      await sleep(600);
      return { before, after: piv.getAttribute('ry'), anims: piv.querySelectorAll(':scope > m-attr-anim').length }; }""")
    print(r, "ERRORS:", errs or "none"); b.close()
