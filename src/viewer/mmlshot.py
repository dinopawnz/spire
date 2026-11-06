"""Render the REAL world page: python3 mmlshot.py shots.json
shots.json = {"page": "/home/claude/spire/out/spire.html", "pos": [x,y,z] (player position, building coords, picks the zone),
              "opts": {...mmlrender options...}, "shots": [{"out": "a.png", "cam": [x,y,z], "at": [x,y,z], "fov": 60}],
              "cmds": ["lite on", ...]  (optional extra host commands)}
Serves /home/claude on :8766. Model/image URLs on raw.githubusercontent are mapped to local files:
fresh build output (spire/out) first, then the spire repo clone, then the mudwater repo clone."""
import json, os, sys, subprocess, time
from playwright.sync_api import sync_playwright

HOME = '/home/claude'
def file_map():
    m = {}
    def add(prefix, root, rel_base=None):
        for d, _, fs in os.walk(root):
            if '/.git' in d: continue
            for f in fs:
                full = os.path.join(d, f); rel = os.path.relpath(full, rel_base or root)
                url = '/' + os.path.relpath(full, HOME)
                for k in (prefix + rel, prefix + f):
                    m.setdefault(k, url)
    # spire: fresh build output wins over the repo copy
    add('spire/', HOME + '/spire/out/glb'); add('spire/', HOME + '/spire/out')
    add('spire/', HOME + '/spire_repo')
    add('mudwater/', HOME + '/mudwater_repo')
    return m

cfg = json.load(open(sys.argv[1]))
FM = file_map()
srv = subprocess.Popen(['python3', '-m', 'http.server', '8766', '-d', HOME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        o = cfg.get('opts', {}); W, H = o.get('w', 1280), o.get('h', 720)
        pg = b.new_page(viewport={'width': W, 'height': H})
        pg.on('console', lambda m: print('  console:', m.text[:200]) if ('ERR' in m.text or 'rror' in m.text) else None)
        pg.on('pageerror', lambda e: print('  pageerror:', str(e)[:300]))
        pg.goto('http://localhost:8766/' + os.path.relpath(cfg['page'], HOME))
        pos = cfg.get('pos', [0, 4.6, 20])
        res = pg.evaluate("""([pos, cmds]) => {
          const fire = (n, name, detail) => n.dispatchEvent(new CustomEvent(name, { detail, bubbles: true }));
          for (const id of [1, 99]) window.dispatchEvent(new CustomEvent('connected', { detail: { connectionId: id } }));
          const host = document.getElementById('sp-host'), board = document.getElementById('sp-remote');
          const say = (c) => { fire(host, 'prompt', { value: '7747 ' + c, connectionId: 99 }); return (JSON.parse(board.getAttribute('data-ack') || '{}')).t; };
          const out = [say('remote'), say('build')];
          const probe = document.querySelector('m-position-probe');
          if (probe) fire(probe, 'positionmove', { connectionId: 1, elementRelative: { position: { x: pos[0], y: pos[1], z: pos[2] } } });
          for (const c of cmds) out.push(say(c));
          let wg = probe; while (wg && wg.parentElement && wg.parentElement.id !== 'root') wg = wg.parentElement;
          return { out, worldZ: wg ? parseFloat(wg.getAttribute('z') || '0') : 0, n: document.querySelectorAll('*').length };
        }""", [pos, cfg.get('cmds', [])])
        print('page:', res)
        if cfg.get('js'):                                  # optional staging script (e.g. bots join + play), runs after the build
            print('js:', pg.evaluate("async () => { const fire = (n, name, detail) => n.dispatchEvent(new CustomEvent(name, { detail, bubbles: true })); const sleep = (ms) => new Promise(r => setTimeout(r, ms)); " + cfg['js'] + " }"))
        pg.wait_for_timeout(int(cfg.get('settle_ms', 1500)))
        o = dict(o); o['map'] = FM; o['viewer'] = 1; o['worldZ'] = res['worldZ']
        pg.evaluate("""(o) => {
          const im = document.createElement('script'); im.type = 'importmap';
          im.textContent = JSON.stringify({ imports: { three: '/viewer/node_modules/three/build/three.module.js', 'three/addons/': '/viewer/node_modules/three/examples/jsm/' } });
          document.head.appendChild(im);
          window.__opt = o;
          const s = document.createElement('script'); s.type = 'module';
          s.textContent = "import { setup } from '/viewer/mmlrender.js'; setup(window.__opt).catch(e => console.log('ERR setup ' + e.stack));";
          document.head.appendChild(s);
        }""", o)
        pg.wait_for_function('window.__ready === true', timeout=900000)
        print('stats:', pg.evaluate('window.__stats'))
        for s in cfg['shots']:
            pg.evaluate('(c) => window.__shoot(c)', s)
            pg.screenshot(path=s['out']); print('wrote', s['out'])
        b.close()
finally:
    srv.terminate()
