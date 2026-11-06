"""Run the jsdom test scripts (simtest.js, roundtest.js, biotest.js, refcheck2.js) in real headless Chrome instead of jsdom
(jsdom can't be installed in this workspace). Usage:  python3 chrometest.py simtest.js /home/claude/spire/out/spire.html [/home/claude/spire/out]
The test file is used as-is: the jsdom/fs lines are swapped for a tiny browser shim, process.exit() ends the run,
fs.writeFileSync() files are written back to disk here (refcheck2 -> /tmp/refs.json)."""
import json, os, re, subprocess, sys, time
from playwright.sync_api import sync_playwright

HOME = '/home/claude'
test, page = sys.argv[1], sys.argv[2]
outdir = sys.argv[3] if len(sys.argv) > 3 else None
src = open(test).read()
src = re.sub(r'const \{ JSDOM \} = require\("jsdom"\);', '', src)
src = re.sub(r'const (fs|path) = require\("(fs|path)"\);', '', src)
src = re.sub(r'const html = fs\.readFileSync\([^;]*\);', '', src)
src = re.sub(r'const dom = new JSDOM\([^;]*\);', 'const dom = { window };', src)
src = src.replace('process.exit(0)', '(window.__testDone = true)')
existing = []
if outdir:
    for d, _, fs_ in os.walk(outdir):
        for f in fs_: existing.append(os.path.relpath(os.path.join(d, f), outdir))
shim = """
const __files = {}; window.__files = __files; const __exist = new Set(%s);
const fs = { writeFileSync: (p, data) => { __files[p] = String(data); }, existsSync: (p) => __exist.has(String(p).replace(/^%s\\/?/, '')) };
const path = { join: (...a) => a.join('/').replace(/\\/+/g, '/') };
const process = { argv: ['node', 'test', %s, %s], exit: () => { window.__testDone = true; } };
""" % (json.dumps(existing), re.escape(outdir or '/nonexistent').replace('/', '\\/'), json.dumps(page), json.dumps(outdir or ''))
port = 8767
srv = subprocess.Popen(['python3', '-m', 'http.server', str(port), '-d', HOME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
code = 0
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = b.new_page()
        logs = []
        pg.on('console', lambda m: (print(m.text), logs.append(m.text)))
        pg.on('pageerror', lambda e: print('PAGEERROR:', e))
        pg.goto('http://localhost:%d/%s' % (port, os.path.relpath(page, HOME)))
        pg.evaluate('(code) => { const s = document.createElement("script"); s.textContent = code; document.body.appendChild(s); }', '(function(){' + shim + src + '\n})();')
        pg.wait_for_function('window.__testDone === true', timeout=600000)
        for fp, data in pg.evaluate('window.__files').items():
            open(fp, 'w').write(data)
        b.close()
finally:
    srv.terminate()
