"""(v55) ART WALL: whichever way Otherside sends the click spot (the wall's axes, the world's axes, centimetres, Unreal's axes), the
dots must land exactly where the player clicked. Each format gets a fresh world and 3 clicks; the dots' places are checked.
   python3 arttest.py /home/claude/spire/out/spire.html"""
import sys, time, json, math
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m): print(('OK   ' if c else 'FAIL ') + m); (None if c else fails.append(m))
D = json.loads(open(sys.argv[1]).read().split('const D = ')[1].split(';\n')[0]); AW = D['artwall']; W = AW['cols'] * AW['cell']; H = AW['rows'] * AW['cell']; ry = math.radians(AW['ry'])
F = {'wall axes, metres': lambda lx, ly, d: {'x': lx, 'y': ly, 'z': d},
     'world axes, metres': lambda lx, ly, d: {'x': lx * math.cos(ry) + d * math.sin(ry), 'y': ly, 'z': -lx * math.sin(ry) + d * math.cos(ry)},
     'wall axes, centimetres': lambda lx, ly, d: {'x': lx * 100, 'y': ly * 100, 'z': d * 100},
     'world axes, centimetres': lambda lx, ly, d: {'x': (lx * math.cos(ry) + d * math.sin(ry)) * 100, 'y': ly * 100, 'z': (-lx * math.sin(ry) + d * math.cos(ry)) * 100},
     'Unreal axes, centimetres': lambda lx, ly, d: {'x': d * 100, 'y': lx * 100, 'z': ly * 100},
     'whole-document spot, metres': lambda lx, ly, d: {'x': AW['cx'] + lx * math.cos(ry) + d * math.sin(ry), 'y': AW['y0'] + H / 2 + ly, 'z': AW['z'] - lx * math.sin(ry) + d * math.cos(ry) - D['FRONT']}}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    for nm, f in F.items():
        pg = b.new_page(); pg.goto("file://" + sys.argv[1]); time.sleep(1)
        pg.evaluate("() => { for (let i = 1; i < 6; i++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:i}})); document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true})); }"); time.sleep(3)
        good = 0
        for (lx, ly) in ((-7.3, 2.1), (4.45, -2.85), (10.05, 0.35)):
            pg.evaluate("""([W, pos]) => { const b = Array.from(document.querySelectorAll('m-cube')).find(c => c.getAttribute('collide') === 'true' && c.getAttribute('opacity') === '0' && Math.abs(+c.getAttribute('width') - W) < 0.01);
              b.dispatchEvent(new CustomEvent('click', {detail: {connectionId: 2, position: pos}, bubbles: true})); }""", [W, f(lx, ly, 0.04)]); time.sleep(0.15)
            d = pg.evaluate("() => { const c = Array.from(document.querySelectorAll('m-cylinder')).filter(c => c.getAttribute('rx') === '90' && c.getAttribute('height') === '0.01').pop(); return c ? [+c.getAttribute('x'), +c.getAttribute('y')] : null; }")
            if d and abs(d[0] - lx) < 0.08 and abs(d[1] - (ly + H / 2)) < 0.08: good += 1
            else: print('    clicked', (lx, ly), 'dot at', d)
        ok(good == 3, "%s: 3 of 3 dots exactly where clicked (%d)" % (nm, good))
        pg.close()
    # no spot at all (or 0,0,0): the wall switches to the click net, and a click on a net square paints a dot inside that square
    for nm, det in (('no spot at all', '{connectionId: 2}'), ('an empty 0,0,0 spot', '{connectionId: 2, position: {x: 0, y: 0, z: 0}}')):
        pg = b.new_page(); pg.goto("file://" + sys.argv[1]); time.sleep(1)
        pg.evaluate("() => { for (let i = 1; i < 6; i++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:i}})); document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 build', connectionId:1}, bubbles:true})); }"); time.sleep(3)
        pg.evaluate("""([W]) => { const b = Array.from(document.querySelectorAll('m-cube')).find(c => c.getAttribute('collide') === 'true' && c.getAttribute('opacity') === '0' && Math.abs(+c.getAttribute('width') - W) < 0.01);
              b.dispatchEvent(new CustomEvent('click', {detail: %s, bubbles: true})); }""" % det, [W]); time.sleep(0.3)
        net = pg.evaluate("() => Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('opacity') === '0' && c.getAttribute('width') === '0.49').length")
        good = 0
        for (lx, ly) in ((-7.3, 2.1), (4.45, -2.85), (10.05, 0.35)):
            cx, cy = (math.floor((lx + W / 2) / 0.5) + 0.5) * 0.5 - W / 2, (math.floor((ly + H / 2) / 0.5) + 0.5) * 0.5
            pg.evaluate("""([cx, cy]) => { const h = Array.from(document.querySelectorAll('m-cube')).find(c => c.getAttribute('width') === '0.49' && Math.abs(+c.getAttribute('x') - cx) < 0.01 && Math.abs(+c.getAttribute('y') - cy) < 0.01);
                h.dispatchEvent(new CustomEvent('click', {detail: {connectionId: 3}, bubbles: true})); }""", [cx, cy]); time.sleep(0.15)
            d = pg.evaluate("() => { const c = Array.from(document.querySelectorAll('m-cylinder')).filter(c => c.getAttribute('rx') === '90' && c.getAttribute('height') === '0.01').pop(); return c ? [+c.getAttribute('x'), +c.getAttribute('y')] : null; }")
            if d and abs(d[0] - cx) <= 0.3 and abs(d[1] - cy) <= 0.3: good += 1
            else: print('    square', (cx, cy), 'dot at', d)
        ok(net == 768 and good == 3, "%s: the wall switches to the click net (%d squares) and 3 of 3 clicks paint a dot in the clicked square (%d)" % (nm, net, good))
        pg.close()
    b.close()
print("FAILS:", len(fails))
