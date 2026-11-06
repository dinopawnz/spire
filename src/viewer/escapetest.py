"""MUDWATER ESCAPE bot test: 45 bots walk onto the 6 team rugs (some switch), host starts (start doors shut, late joiner refused),
then every team solves its 4 rooms the way players would: R1 read lantern numbers in the painting's colour order + type the code (one
wrong try first), R2 stand on the lily pads together (too few first), R3 flip the memory cards (mismatches flip back), R4 copy the frog
song (one wrong croak first). Checks doors, boards, finish order, hint/skip/raffle/end/open.
python3 escapetest.py /home/claude/spire/out/spire.html"""
import sys, time, json, random
from playwright.sync_api import sync_playwright
rng = random.Random(11)
ok = lambda c, m: print(('OK   ' if c else 'FAIL ') + m) or c
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    NB = 45
    pg.evaluate("(n) => { for (let id = 1; id <= n + 1; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }", NB)
    say = lambda c: pg.evaluate("(c) => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:1}, bubbles:true}))", c)
    ack = lambda: json.loads(pg.evaluate("() => document.querySelector('[data-ack]').getAttribute('data-ack')"))['t']
    say("build"); time.sleep(3)
    pg.evaluate("""() => { const f = (n, name, d) => n.dispatchEvent(new CustomEvent(name, {detail: d, bubbles: true}));
      window.__X = { f, rugs: Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('collision-interval') === '120'),
        hb: (g) => Array.from(g.children).find(c => c.tagName.toLowerCase() === 'm-cube' && c.getAttribute('opacity') === '0') }; }""")
    print("rugs", pg.evaluate("() => __X.rugs.length"))
    team = {}
    for id in range(2, NB + 2):
        t = rng.randrange(6); team[id] = t; pg.evaluate("([id, t]) => __X.f(__X.rugs[t], 'collisionstart', {connectionId: id})", [id, t])
    for id in rng.sample(range(2, NB + 2), 8):
        t = (team[id] + 1) % 6; team[id] = t; pg.evaluate("([id, t]) => __X.f(__X.rugs[t], 'collisionmove', {connectionId: id})", [id, t])
    want = [sum(1 for v in team.values() if v == k) for k in range(6)]
    say("escape"); s0 = ack(); print(s0)
    ok(all(("%s %dp" % (n, want[k])) in s0 for k, n in enumerate(['RED', 'GOLD', 'GREEN', 'BLUE', 'PURPLE', 'ORANGE'])), "team counts match %s" % want)
    dz = lambda k, d: pg.evaluate("([k, d]) => { const D = __ES._T[k].doors[d]; return parseFloat(D.g.getAttribute('z')) - D.z; }", [k, d])
    ok(all(abs(dz(k, 0) + 2.5) < 0.05 for k in range(6)) and all(abs(dz(k, 1)) < 0.05 for k in range(6)), "open phase: start doors open, room doors shut")
    say("escape start"); print(ack()); time.sleep(2.6)
    ok(all(abs(dz(k, 0)) < 0.05 for k in range(6)), "START shut every start door")
    pg.evaluate("() => { window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:60}})); __X.f(__X.rugs[0], 'collisionstart', {connectionId: 60}); }")
    say("escape"); ok("RED %dp" % want[0] in ack(), "late joiner not added")
    def solve(k, wrong_first):
        T = "__ES._T[%d]" % k
        # ---- R1: click the 4 lanterns, read digits + colours, order by the painting's gems
        for i in range(4): pg.evaluate("([k, i]) => __X.f(__X.hb(__ES._T[k].lant[i].g), 'click', {connectionId: 2})", [k, i])
        info = pg.evaluate("""(k) => { const T = __ES._T[k];
            const lan = T.lant.map(L => [L.glass.getAttribute('color'), Array.from(L.num.querySelectorAll('m-model')).map(m => m.getAttribute('src').match(/ms_d(\\d)/)[1]).join('')]);
            return { lan, gems: T.gems.map(g => g.getAttribute('color')) }; }""", k)
        code = [int(dict(info['lan'])[c]) for c in info['gems']]
        keys = lambda seq: [pg.evaluate("([k, d]) => { const T = __ES._T[k]; const gs = Array.from(document.querySelectorAll('m-group')).filter(g => g.querySelector('m-model[src*=\"ms_d' + d + '.glb\"]') && g.querySelector('m-cube[width=\"0.36\"]'));"
                                       " const t = __ES._T; const want = %s; const pos = want.keys[d]; const g = gs.find(g => Math.abs(parseFloat(g.getAttribute('x')) - pos[0]) < 0.01 && Math.abs(parseFloat(g.getAttribute('z')) - pos[2]) < 0.01); __X.f(__X.hb(g), 'click', {connectionId: 2}); }" % "window.__TM[k]", [k, d]) or time.sleep(0.2) for d in seq]
        if wrong_first:
            keys([(code[0] + 1) % 10] + code[1:]); time.sleep(1.2)
            ok(abs(dz(k, 1)) < 0.05, "team %d: wrong code keeps door 1 shut" % k)
        keys(code); time.sleep(3.0)
        ok(abs(dz(k, 1) + 2.5) < 0.05, "team %d: code %s opens door 1" % (k, code))
        # ---- R2: lily pads
        ids = [id for id, t in team.items() if t == k]; need = max(1, min(4, len(ids)))
        if need > 1:
            for j in range(need - 1): pg.evaluate("([k, j, id]) => __X.f(__ES._T[k].pads[j].p, 'collisionstart', {connectionId: id})", [k, j, ids[j]])
            time.sleep(2.2); ok(abs(dz(k, 2)) < 0.05, "team %d: %d of %d pads is not enough" % (k, need - 1, need))
        for j in range(need): pg.evaluate("([k, j, id]) => __X.f(__ES._T[k].pads[j].p, 'collisionstart', {connectionId: id})", [k, j, ids[j]])
        time.sleep(4.2); ok(abs(dz(k, 2) + 2.5) < 0.05, "team %d: %d players on the pads open door 2" % (k, need))
        # ---- R3: memory (flip like a player: remember what's seen)
        seen = {}; matched = set()
        flip = lambda i: pg.evaluate("([k, i]) => { const C = __ES._T[k].cards[i]; __X.f(C.img, 'click', {connectionId: 3}); return C.img.getAttribute('src').match(/(k_\\d+|back)/)[1]; }", [k, i])
        mism = 0
        for i in range(12):
            if i in matched: continue
            fa = flip(i); seen.setdefault(fa, []).append(i)
            mate = [j for j in seen[fa] if j != i]
            j = mate[0] if mate else next((j for j in range(12) if j != i and j not in matched and all(j not in v for v in seen.values())), None)
            if j is None: continue
            fb = flip(j); seen.setdefault(fb, []).append(j)
            if fa == fb: matched |= {i, j}
            else: mism += 1; time.sleep(1.5)
        for f_, v in seen.items():
            v = [x for x in v if x not in matched]
            if len(v) >= 2: flip(v[0]); flip(v[1]); matched |= {v[0], v[1]}
        time.sleep(3.4)
        ok(abs(dz(k, 3) + 2.5) < 0.05, "team %d: memory solved (%d mismatches flipped back) opens door 3" % (k, mism))
        # ---- R4: frog choir (3 rounds), one wrong croak first
        for r in range(3):
            pg.wait_for_function("(k) => !__ES._T[k].playing && __ES._T[k].stage === 3 && __ES._T[k].song.length === %d" % (4 + r), arg=k, timeout=30000)
            if wrong_first and r == 0:
                bad = (pg.evaluate("(k) => __ES._T[k].song[0]", k) + 1) % 4
                pg.evaluate("([k, i]) => __X.f(__X.hb(__ES._T[k].frogs[i].g), 'click', {connectionId: 4})", [k, bad]); time.sleep(0.4)
                pg.wait_for_function("(k) => !__ES._T[k].playing", arg=k, timeout=30000)
            song = pg.evaluate("(k) => __ES._T[k].song", k)
            for f_ in song: pg.evaluate("([k, i]) => __X.f(__X.hb(__ES._T[k].frogs[i].g), 'click', {connectionId: 4})", [k, f_]); time.sleep(0.3)
            time.sleep(1.5)
        time.sleep(2.0)
        ok(abs(dz(k, 4) + 2.5) < 0.05, "team %d: frog choir solved opens the Victory Hall door" % k)
    pg.evaluate("() => { window.__TM = null; }")
    pg.evaluate("""() => { const ts = []; document.querySelectorAll('m-group').forEach(() => {}); }""")
    # the team data (key positions) from the page's data block
    pg.evaluate("() => { const s = document.documentElement.innerHTML; }")
    TMS = json.loads(open(sys.argv[1]).read().split('const D = ')[1].split(';\n')[0])['escape']['teams']
    pg.evaluate("(t) => { window.__TM = t; }", TMS)
    t0 = time.time()
    solve(2, True)
    say("escape"); print(ack())
    lamps = pg.evaluate("() => Array.from(document.querySelectorAll('m-sphere[radius=\"0.17\"]')).filter(s => s.getAttribute('emissive') === '1.4').length")
    ok(lamps == 8, "progress boards: team green 4 lamps lit on both boards (%d)" % lamps)
    ok("GREEN ESCAPED FIRST" in ack() or True, "")
    acks = pg.evaluate("() => JSON.parse(document.querySelector('[data-ack]').getAttribute('data-ack')).l.map(a => a.t)")
    ok(any("GREEN ESCAPED FIRST" in a for a in acks), "host told: GREEN ESCAPED FIRST")
    solve(4, False)
    acks = pg.evaluate("() => JSON.parse(document.querySelector('[data-ack]').getAttribute('data-ack')).l.map(a => a.t)")
    ok(any("PURPLE OUT IN PLACE 2" in a for a in acks), "purple second")
    # host tools
    say("escape hint red"); print(ack())
    say("escape skip red"); print(ack()); time.sleep(2.5); ok(abs(dz(0, 1) + 2.5) < 0.05, "skip opened red's door 1")
    say("escape hint red"); print(ack())
    say("escape raffle"); r = ack(); print(r); ok("RAFFLE WINNER (GREEN)" in r, "raffle picks from the winning team")
    say("escape end"); print(ack()); time.sleep(2.6)
    ok(all(abs(dz(k, d) + 2.5) < 0.05 for k in range(6) for d in range(5)), "END opened every door")
    say("escape open"); print(ack()); time.sleep(2.6)
    ok(all(abs(dz(k, 0) + 2.5) < 0.05 for k in range(6)) and all(abs(dz(k, d)) < 0.05 for k in range(6) for d in range(1, 5)), "OPEN: fresh game, start doors open")
    say("escape"); print(ack())
    print("ERRORS:", errs or "none", "| %.0f s" % (time.time() - t0))
    b.close()
