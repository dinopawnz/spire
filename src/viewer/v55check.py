"""(v55) checks: art wall paints from every way a click spot can arrive (wall axes, world axes, centimetres, Unreal axes) and no sound
on paint / sign; CELEBRATE makes a silent 30 s show and cleans up after itself; FORCE OPEN / OPEN ALL FLOORS on the lifts; the Mud
Match real portrait moves to a new spot every round.   python3 v55check.py /home/claude/spire/out/spire.html"""
import sys, time, json, math
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m): print(('OK   ' if c else 'FAIL ') + m); (None if c else fails.append(m))
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    for i in range(1, 8): pg.evaluate("(i) => window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:i}}))", i)
    say = lambda c, who=1: pg.evaluate("([c, w]) => { document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:w}, bubbles:true})); return JSON.parse(document.querySelector('[data-ack]').getAttribute('data-ack')).t; }", [c, who])
    say("remote", 7); say("build"); time.sleep(3)
    D = json.loads(open(sys.argv[1]).read().split('const D = ')[1].split(';\n')[0]); AW = D['artwall']; W = AW['cols'] * AW['cell']; H = AW['rows'] * AW['cell']
    audios = lambda: pg.evaluate("() => document.querySelectorAll('m-audio').length")
    # ---- art wall
    a0 = audios()
    pg.evaluate("""() => { const pots = Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('opacity') === '0' && c.getAttribute('width') === '0.18' && c.getAttribute('height') === '0.3');
       pots[1].dispatchEvent(new CustomEvent('click', {detail: {connectionId: 2}, bubbles: true})); }""")
    ok(audios() == a0, "clicking a paint pot makes no sound")
    big = """() => Array.from(document.querySelectorAll('m-cube')).find(c => c.getAttribute('collide') === 'true' && c.getAttribute('opacity') === '0' && Math.abs(+c.getAttribute('width') - %f) < 0.01)""" % W
    ry = math.radians(AW['ry'])
    def click(pos, who):
        pg.evaluate("([f, pos, w]) => { const b = (" + big + ")(); b.dispatchEvent(new CustomEvent('click', {detail: {connectionId: w, position: pos}, bubbles: true})); }", [0, pos, who]); time.sleep(0.15)
    dots = lambda: pg.evaluate("() => Array.from(document.querySelectorAll('m-cylinder')).filter(c => c.getAttribute('rx') === '90' && c.getAttribute('height') === '0.01').length")
    def forms(lx, ly):
        return [('wall axes (metres)', {'x': lx, 'y': ly, 'z': 0.03}),
                ('world axes (metres)', {'x': lx * math.cos(ry) + 0.03 * math.sin(ry), 'y': ly, 'z': -lx * math.sin(ry) + 0.03 * math.cos(ry)}),
                ('wall axes (centimetres)', {'x': lx * 100, 'y': ly * 100, 'z': 3}),
                ('Unreal axes (cm, z up)', {'x': 3, 'y': lx * 100, 'z': ly * 100})]
    for k in range(4):
        nm, pos = forms(-5 + 3 * k, -1.5 + k)[k]
        n0 = dots(); click(pos, 3 + k)
        ok(dots() == n0 + 1, "art wall paints a dot when the click spot comes as %s" % nm)
    n0 = dots(); click({'x': 900, 'y': 900, 'z': 900}, 2); ok(dots() == n0, "a click spot far off the canvas paints nothing")
    print('   ', say("art")[:200])
    # sign the art wall / guest book: no chime
    a0 = audios()
    pg.evaluate("() => Array.from(document.querySelectorAll('m-prompt')).forEach((pr, i) => { if (pr.id === 'sp-host') return; pr.dispatchEvent(new CustomEvent('prompt', {detail: {connectionId: 4, value: 'Tester' + i}, bubbles: true})); })")
    ok(audios() == a0, "signing the art wall / the sign-up book makes no sound")
    # ---- fireworks
    srcs = lambda: pg.evaluate("() => Array.from(document.querySelectorAll('m-audio')).map(a => (a.getAttribute('src') || '').split('/').pop().split('?')[0])")
    s0 = srcs(); a0 = audios(); print(say("celebrate"))
    peak = 0; t0 = time.time()
    while time.time() - t0 < 40:
        n = pg.evaluate("() => document.querySelectorAll('m-model[src*=\"fw_\"]').length"); peak = max(peak, n); time.sleep(1)
    ok(peak >= 8, "fireworks: many shells in the air at once (peak %d models)" % peak)
    ok(pg.evaluate("() => document.querySelectorAll('m-model[src*=\"fw_\"]').length") == 0, "every firework is cleaned up after the show")
    new = [x for x in srcs() if x not in s0]
    ok(not any('winner' in x or 'firework' in x or 'boom' in x for x in new), "the fireworks are silent (new sounds during the show: %s)" % new)
    # ---- lifts
    print(say("lift B 3")); time.sleep(2)
    print(say("lift B open")); time.sleep(3)
    st = json.loads(pg.evaluate("() => document.querySelector('[data-game]').getAttribute('data-game')"))['lifts']['B']
    ok(st['open'] and not st['busy'], "FORCE OPEN mid-ride: the cage stops and opens (%s)" % st)
    print(say("lift B openall")); time.sleep(2)
    gp = pg.evaluate("() => Array.from(document.querySelectorAll('m-cube')).filter(c => +c.getAttribute('y') === -300).length")
    ok(gp >= 4, "OPEN ALL FLOORS: every landing door of that shaft is open (%d walls dropped)" % gp)
    print(say("lift B 0")); time.sleep(3)
    gp2 = pg.evaluate("() => Array.from(document.querySelectorAll('m-cube')).filter(c => +c.getAttribute('y') === -300).length")
    ok(gp2 < gp, "the next ride shuts the other floors' doors again (%d -> %d)" % (gp, gp2))
    # ---- Mud Match: the real portrait moves every round
    print(say("hall open")); slots = []
    for r in range(4):
        real = D['realHall']
        s_ = pg.evaluate("(real) => Array.from(document.querySelectorAll('m-model[src*=\"portraits/pf_\"]')).findIndex(m => m.getAttribute('src').includes('pf_' + String(real).padStart(4, '0') + '.glb'))", real)
        slots.append(s_)
        pg.evaluate("(s) => { const m = document.querySelectorAll('m-model[src*=\"portraits/pf_\"]')[s]; m.dispatchEvent(new CustomEvent('click', {detail: {connectionId: 2 + %d}, bubbles: true})); }" % r, s_)
        time.sleep(0.5); print('   ', say("hall next"))
    ok(len(set(slots)) == 4, "the real Founder hangs in a different place every round: slots %s" % slots)
    print("ERRORS:", errs or "none", "| FAILS:", len(fails))
    b.close()
