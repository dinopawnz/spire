"""LIFT BOT TEST - a crowd of bots uses the lifts for a long (fast-forwarded) session and every half second the test checks
what a real rider would run into. Usage: python3 lifttest.py /home/claude/spire/out/spire.html [bots] [minutes]
Checks: the cab never moves with a door open; a landing door is never open unless the cab is right there; when a door is open
BOTH leaves are folded and BOTH invisible gate walls are gone (riders can walk out); the cab floor collider stays under every
rider for the whole ride (no drops, no jumps); every call is answered; nobody waits forever."""
import json, os, random, subprocess, sys, time
from playwright.sync_api import sync_playwright

HOME = '/home/claude'
page_path = sys.argv[1]
NB = int(sys.argv[2]) if len(sys.argv) > 2 else 30
MINUTES = float(sys.argv[3]) if len(sys.argv) > 3 else 20
LL = json.load(open('/home/claude/spire/out/lift_layout.json'))
rng = random.Random(7)

JS_HELPERS = r"""
window.__T = {
  ease: { easeInOutSine: (p) => -(Math.cos(Math.PI * p) - 1) / 2, easeInOutQuad: (p) => p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2,
          easeInOutCubic: (p) => p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2, easeOutQuad: (p) => 1 - (1 - p) * (1 - p),
          easeInQuad: (p) => p * p, linear: (p) => p },
  now() { return document.timeline.currentTime; },
  val(el, attr) {          // the value a client shows right now: a running m-attr-anim wins over the attribute
    const t = this.now();
    for (const a of el.children) {
      if (a.tagName.toLowerCase() !== 'm-attr-anim' || a.getAttribute('attr') !== attr) continue;
      const st = parseFloat(a.getAttribute('start-time') || '0'), d = parseFloat(a.getAttribute('duration')), s = parseFloat(a.getAttribute('start')), e = parseFloat(a.getAttribute('end'));
      const loop = a.getAttribute('loop') !== 'false';
      let p = (t - st) / d; if (loop) p = p - Math.floor(p); p = Math.max(0, Math.min(1, p));
      const f = this.ease[a.getAttribute('easing') || 'linear'] || this.ease.linear;
      return s + (e - s) * f(p);
    }
    if (el.tagName.toLowerCase() === 'm-attr-lerp') return NaN;
    const v = el.getAttribute(attr); return v === null ? (attr[0] === 's' ? 1 : 0) : parseFloat(v);
  },
  lerps() { return document.querySelectorAll('m-attr-lerp').length; },
  fire(n, name, detail) { n.dispatchEvent(new CustomEvent(name, { detail, bubbles: true })); },
};
"""

def main():
    srv = subprocess.Popen(['python3', '-m', 'http.server', '8768', '-d', HOME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    problems = {}; stats = dict(rides=0, calls=0, waits=[], ticks=0)
    streak = {}; seen_now = set()
    def bad(kind, msg, key=None):
        if key is not None:                        # door states: only a problem if it lasts longer than a door takes to move
            seen_now.add(key); streak[key] = streak.get(key, 0) + 1
            if streak[key] < 4: return
        problems.setdefault(kind, []).append(msg)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
            ctx = b.new_context()
            pg = ctx.new_page()
            pg.on('pageerror', lambda e: bad('page error', str(e)[:200]))
            # one clock for everything: document.timeline follows the (fake, fast-forwardable) Date
            pg.add_init_script("""(() => { const T0 = Date.now(); Object.defineProperty(document, 'timeline', { configurable: true, value: { get currentTime() { return Date.now() - T0; } } }); })();""")
            pg.clock.install()
            pg.goto('http://localhost:8768/' + os.path.relpath(page_path, HOME))
            pg.evaluate(JS_HELPERS)
            pg.evaluate("""() => { for (const id of [999]) window.dispatchEvent(new CustomEvent('connected', { detail: { connectionId: id } }));
              const host = document.getElementById('sp-host'); const say = (c) => __T.fire(host, 'prompt', { value: '7747 ' + c, connectionId: 999 });
              say('remote'); say('build'); }""")
            pg.clock.run_for(3000)
            # find each lift's moving group, gate pads, landing pads + leaves, buttons (by the layout's coordinates)
            info = pg.evaluate("""(LL) => {
              const out = {};
              const near = (el, p, tol) => Math.abs(parseFloat(el.getAttribute('x')||0)-p[0]) < tol && Math.abs(parseFloat(el.getAttribute('z')||0)-p[2]) < tol;
              const cabs = Array.from(document.querySelectorAll('m-group')).filter((g) => Array.from(g.children).some((c) => (c.getAttribute('src')||'').includes('sp_lift_cab.glb')));
              window.__L = {};
              LL.lifts.forEach((Lf) => {
                const CG = cabs.find((g) => Math.abs(parseFloat(g.getAttribute('x')) - Lf.x) < 0.1 && Math.abs(parseFloat(g.getAttribute('z')) - Lf.z) < 0.1);
                const kids = Array.from(CG.children);
                const leaves = kids.filter((c) => (c.getAttribute('src')||'').includes('sp_lift_cgate.glb'));
                const cgPad = kids.filter((c) => c.tagName.toLowerCase() === 'm-cube' && c.getAttribute('collide') === 'true' && parseFloat(c.getAttribute('width')) === 1.8 && parseFloat(c.getAttribute('height')) === 2.5)[0];
                const floors = kids.filter((c) => c.tagName.toLowerCase() === 'm-cube' && c.getAttribute('collide') === 'true' && parseFloat(c.getAttribute('width')) === 4.05);
                const btns = Array.from(CG.querySelectorAll('m-cube')).filter((c) => c.getAttribute('collide') === 'false' && Math.abs(parseFloat(c.getAttribute('width')) - 0.98) < 0.01);
                const L = { CG, leaves, cgPad, floors, btns, lands: [] };
                const all = Array.from(document.querySelectorAll('m-cube, m-model, m-group'));
                const gps = all.filter((e) => e.tagName.toLowerCase() === 'm-cube' && e.getAttribute('collide') === 'true' && near(e, Lf.portals[0].gate_col, 0.02) && Math.abs(parseFloat(e.getAttribute('width')) - 1.85) < 0.01);   // one per floor, in floor order
                Lf.portals.forEach((po, k) => {
                  const gp = gps[k];
                  const lv = all.filter((e) => (e.getAttribute('src')||'').includes('sp_lift_lgate.glb') && (near(e, po.gate_r, 0.02) || near(e, po.gate_l, 0.02)) && Math.abs(parseFloat(e.getAttribute('y')) - po.gate_r[1]) < 0.05);
                  const cb = all.find((e) => e.tagName.toLowerCase() === 'm-group' && near(e, po.call, 0.02) && Math.abs(parseFloat(e.getAttribute('y')) - po.call[1]) < 0.05);
                  const hb = cb ? Array.from(cb.children).find((c) => c.tagName.toLowerCase() === 'm-cube') : null;
                  L.lands.push({ gp, lv, hb, gpY: po.gate_col[1] + 1.45, y: po.y });
                });
                window.__L[Lf.id] = L;
                out[Lf.id] = { leaves: leaves.length, cgPad: !!cgPad, floors: floors.length, btns: btns.length, lands: L.lands.map((l) => [!!l.gp, l.lv.length, !!l.hb]) };
              });
              return out;
            }""", LL)
            print('found:', json.dumps(info))
            for lid, inf in info.items():
                if inf['leaves'] != 2: bad('door leaves', '%s cab has %d gate leaves' % (lid, inf['leaves']))
                for k, (gp, nlv, hb) in enumerate(inf['lands']):
                    if not gp or nlv != 2 or not hb: bad('landing parts', '%s floor %d: pad %s leaves %d button %s' % (lid, k, gp, nlv, hb))
            lifts = {l['id']: l for l in LL['lifts']}
            ids = list(lifts)
            # bots: each waits on a floor for one lift and wants another floor
            bots = []
            for i in range(NB):
                lid = rng.choice(ids); n = len(lifts[lid]['stops']); f = rng.randrange(n); g = rng.choice([k for k in range(n) if k != f])
                bots.append(dict(id=i + 1, lift=lid, at=f, want=g, state='wait', since=0, called=False, y=lifts[lid]['stops'][f]))
            sim_ms = 0; TICK = 500; T_END = MINUTES * 60000
            while sim_ms < T_END:
                pg.clock.run_for(TICK); sim_ms += TICK; stats['ticks'] += 1
                snap = pg.evaluate("""() => { const o = {}; for (const id in __L) { const L = __L[id];
                    o[id] = { y: __T.val(L.CG, 'y'), cg: __T.val(L.cgPad, 'y'), leaves: L.leaves.map((x) => __T.val(x, 'sx')), moving: Array.from(L.CG.children).some((c) => c.tagName.toLowerCase()==='m-attr-anim' && c.getAttribute('attr')==='y'),
                      lands: L.lands.map((l) => ({ gp: __T.val(l.gp, 'y'), lv: l.lv.map((x) => __T.val(x, 'sx')) })) }; }
                    o.lerps = __T.lerps(); return o; }""")
                for kk in list(streak):
                    if kk not in seen_now: streak.pop(kk)
                seen_now.clear()
                if snap['lerps']: bad('m-attr-lerp left', '%d lerp elements (Otherside ignores them: things jump)' % snap['lerps'])
                for lid, s in snap.items():
                    if lid == 'lerps': continue
                    stops = lifts[lid]['stops']
                    at = min(range(len(stops)), key=lambda k: abs(stops[k] - s['y'])); level = abs(stops[at] - s['y']) < 0.02
                    cab_open = s['cg'] < -10
                    if s['moving'] and not level and cab_open: bad('moving with door open', '%s at y %.2f t=%ds' % (lid, s['y'], sim_ms // 1000))
                    for k, l in enumerate(s['lands']):
                        lopen = l['gp'] < -100
                        if lopen and not (level and at == k): bad('shaft door open, no cab', '%s floor %d open while cab at y %.2f t=%ds' % (lid, k, s['y'], sim_ms // 1000))
                        if lopen and level and at == k:
                            # someone may walk through: both leaves must be folded, and the cab gate wall gone too
                            if max(l['lv']) > 0.3 or max(s['leaves']) > 0.3: bad('door looks shut but is open', '%s floor %d leaves landing %s cab %s t=%ds' % (lid, k, [round(v, 2) for v in l['lv']], [round(v, 2) for v in s['leaves']], sim_ms // 1000), key=('shut', lid, k))
                            if not cab_open: bad("can't get out", '%s floor %d: landing open but cab gate wall still there t=%ds' % (lid, k, sim_ms // 1000))
                        if not lopen and (min(l['lv']) < 0.9) and not (level and at == k and (s['moving'] is False)):
                            pass
                    # visual: leaves folded while the wall is still there = "the door is open but I walk into glass"
                    if level and not cab_open and max(s['leaves']) < 0.3 and min(s['lands'][at]['lv']) < 0.3: bad('open-looking door is solid', '%s floor %d t=%ds' % (lid, at, sim_ms // 1000), key=('solid', lid, at))
                    if s['leaves'][0] < 0.3 and s['leaves'][1] > 0.9 or s['leaves'][1] < 0.3 and s['leaves'][0] > 0.9: bad('only one cab leaf open', '%s %s t=%ds' % (lid, [round(v, 2) for v in s['leaves']], sim_ms // 1000))
                # bots act
                for bt in bots:
                    s = snap[bt['lift']]; stops = lifts[bt['lift']]['stops']
                    at = min(range(len(stops)), key=lambda k: abs(stops[k] - s['y'])); level = abs(stops[at] - s['y']) < 0.02
                    walk_open = level and s['cg'] < -10 and s['lands'][at]['gp'] < -100
                    if bt['state'] == 'wait':
                        if walk_open and at == bt['at']:
                            bt['state'] = 'ride'; stats['waits'].append((sim_ms - bt['since']) / 1000); bt['since'] = sim_ms
                            pg.evaluate("([lid, k, id]) => __T.fire(__L[lid].btns[k], 'click', { connectionId: id })", [bt['lift'], bt['want'], bt['id']])
                        elif not bt['called'] or (sim_ms - bt['since']) % 30000 < TICK:
                            pg.evaluate("([lid, k, id]) => __T.fire(__L[lid].lands[k].hb, 'click', { connectionId: id })", [bt['lift'], bt['at'], bt['id']])
                            bt['called'] = True; stats['calls'] += 1
                        if sim_ms - bt['since'] > 240000: bad('waited over 4 minutes', 'bot %d on %s floor %d' % (bt['id'], bt['lift'], bt['at'])); bt['since'] = sim_ms
                    elif bt['state'] == 'ride':
                        # the rider stands on the cab floor: the floor top must be right under them, every tick
                        top = s['y']; v = (top - bt['y']) / (TICK / 1000); acc = (v - bt.get('v', 0.0)) / (TICK / 1000)
                        if abs(top - bt['y']) > 2.0: bad('cab jumps (teleport)', 'bot %d: cab floor moved %.2f m in 0.5 s (%s)' % (bt['id'], top - bt['y'], bt['lift']))
                        elif acc < -6.0: bad('rider would lift off', 'bot %d: floor dropped away at %.1f m/s2 (%s)' % (bt['id'], acc, bt['lift']))
                        elif acc > 12.0: bad('rider would be flung', 'bot %d: floor pushed up at %.1f m/s2 (%s)' % (bt['id'], acc, bt['lift']))
                        bt['y'] = top; bt['v'] = v
                        if walk_open and at == bt['want']:
                            stats['rides'] += 1; bt['state'] = 'wait'; bt['at'] = at
                            bt['want'] = rng.choice([k for k in range(len(stops)) if k != at]); bt['since'] = sim_ms; bt['called'] = False
                        elif sim_ms - bt['since'] > 300000: bad('ride over 5 minutes', 'bot %d on %s' % (bt['id'], bt['lift'])); bt['since'] = sim_ms
                        elif rng.random() < 0.02:     # impatient riders press their floor again / press other floors
                            pg.evaluate("([lid, k, id]) => __T.fire(__L[lid].btns[k], 'click', { connectionId: id })", [bt['lift'], rng.randrange(len(stops)), bt['id']])
            b.close()
    finally:
        srv.terminate()
    w = sorted(stats['waits'])
    print('simulated %.0f min, %d bots: %d rides, %d call presses, wait median %.0fs max %.0fs' % (MINUTES, NB, stats['rides'], stats['calls'], w[len(w) // 2] if w else -1, w[-1] if w else -1))
    if not problems: print('NO PROBLEMS FOUND')
    for k, v in problems.items(): print('PROBLEM %-28s x%-5d e.g. %s' % (k, len(v), v[0]))

main()
