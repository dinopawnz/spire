"""EVERY portrait must be clickable: cast a click ray from 2.5 m in front of each portrait (where a player on the ramp stands) at its
centre and report anything in the way (colliders, visible models, invisible boxes).  python3 run.py [scene.json built by export.py]"""
import json, time, subprocess, sys
from playwright.sync_api import sync_playwright
S = json.load(open('/home/claude/viewer/clicktest/scene.json'))
srv = subprocess.Popen(['python3', '-m', 'http.server', '8765', '-d', '/home/claude'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = b.new_page(); pg.on('pageerror', lambda e: print('ERR', e))
        pg.goto('http://localhost:8765/viewer/clicktest/ray.html'); pg.wait_for_function('window.__ready', timeout=600000)
        print('objects', pg.evaluate('window.__ready'))
        D = json.loads(open('/home/claude/spire/out/spire.html').read().split('const D = ')[1].split(';\n')[0])
        tg = []
        for e in S:
            if e['t'] == 'm-model' and '/portraits/p' in e['src']:
                m = e['m']; x, y, z = m[12], m[13], m[14]
                ry = __import__('math').degrees(__import__('math').atan2(m[8], m[10]))
                for dist in (1.5, 2.5, 3.6):                              # near, normal, from the far side of the ramp
                    for yaw in (-35, 0, 35):                                  # and from either side
                        tg.append([x, y, z, ry + yaw, e['src'].split('/')[-1].split('?')[0], dist])
        res = pg.evaluate('(t) => window.__test(t)', tg)
        blocked = [r for r in res if r['colliders'] or r['visible'] or r['hidden'] or r['me'] is None]
        print('click rays tested', len(res), '(9 per portrait) | blocked', len(blocked), '| portraits with any blocked ray', len(set(r['label'] for r in blocked)))
        from collections import Counter
        print(Counter((h['src'] or h['t']) + (' (collider)' if h['col'] else '') for r in blocked for h in (r['colliders'] + r['visible'] + r['hidden'])).most_common(15))
        json.dump(res, open('/home/claude/viewer/clicktest/result.json', 'w'))
        for r in blocked[:6]: print(r)
        b.close()
finally:
    srv.terminate()
