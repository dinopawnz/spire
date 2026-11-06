"""usage: python3 shot.py scenes.json   -- each scene: {"out": "x.png", ...view.html scene...}. Serves /home/claude on :8765."""
import json, sys, subprocess, time, urllib.parse
from playwright.sync_api import sync_playwright

srv = subprocess.Popen(['python3', '-m', 'http.server', '8765', '-d', '/home/claude'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    scenes = json.load(open(sys.argv[1]))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        for sc in scenes:
            pg = b.new_page(viewport={'width': sc.get('w', 1280), 'height': sc.get('h', 720)})
            pg.on('console', lambda m: print('  console:', m.text) if 'ERR' in m.text or 'rror' in m.text else None)
            pg.goto('http://localhost:8765/viewer/view.html#' + urllib.parse.quote(json.dumps(sc)))
            pg.wait_for_function('window.__done === true', timeout=600000)
            pg.screenshot(path=sc['out'])
            print(sc['out'], 'tris', pg.evaluate('window.__tris'))
            pg.close()
        b.close()
finally:
    srv.terminate()
