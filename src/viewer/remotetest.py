import time, subprocess
from playwright.sync_api import sync_playwright
srv = subprocess.Popen(['python3', '-m', 'http.server', '8766', '-d', '/home/claude/spire/out'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = b.new_page(viewport={'width': 1400, 'height': 1600})
        pg.on('console', lambda m: print('  console:', m.text[:200]))
        pg.goto('http://localhost:8766/spire_remote.html?url=ws://localhost:7079&pin=7747')
        time.sleep(4)
        def press(label):
            pg.once('dialog', lambda d: d.accept())
            pg.locator('button.btn', has_text=label).first.click(); time.sleep(2.5)
        press('LIVE BUILD'); time.sleep(3)
        press('OPEN THE HALL'); press('THIN THE FAKES')
        pg.locator('button.btn', has_text='Captain').first.click(); time.sleep(3)
        pg.screenshot(path='/home/claude/shots/remote.png', full_page=False)
        print(pg.locator('#log, .log').first.inner_text()[:1500] if pg.locator('#log, .log').count() else pg.inner_text('body')[-1500:])
        b.close()
finally:
    srv.terminate()
