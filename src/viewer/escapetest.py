"""MUDWATER ESCAPE bot test: 45 bots walk onto the 6 team rugs (some switch), host starts (start doors shut, late joiner refused),
then teams solve the 4 code rooms (v51): open the chests, check the pictures, type codes on the 12-key keypads (one wrong code first:
30 s lock), check the witch's strokes line up only from the true eye. Checks doors, boards, finish order, hint/skip/raffle/end/open.
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
    pg.evaluate("() => { const C = __ES._T[0].chests[0]; __X.f(__X.hb(C.g), 'click', {connectionId: 5}); }")
    ok(not pg.evaluate("() => __ES._T[0].chests[0].open"), "before START a chest won't open")
    ok(pg.evaluate("() => __ES._T[1].shown.length") == 0, "before START no puzzle pictures are up")
    say("escape start"); print(ack()); time.sleep(2.6)
    ok(all(abs(dz(k, 0)) < 0.05 for k in range(6)), "START shut every start door")
    pg.evaluate("() => { window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:60}})); __X.f(__X.rugs[0], 'collisionstart', {connectionId: 60}); }")
    say("escape"); ok("RED %dp" % want[0] in ack(), "late joiner not added")
    def press(k, r, seq, who=2):
        for kk in seq:
            i = "123456789C0K".index(kk)
            pg.evaluate("([k, r, i, w]) => { const hb = Array.from(__ES._T[k].kp[r].g.children).filter(c => c.tagName.toLowerCase() === 'm-cube' && c.getAttribute('opacity') === '0'); __X.f(hb[i], 'click', {connectionId: w}); }", [k, r, i, who])
            time.sleep(0.17)
    shown = lambda k, r: pg.evaluate("([k, r]) => __ES._T[k].kp[r].disp.querySelectorAll('m-model').length", [k, r])
    def chests(k, room):
        n = pg.evaluate("([k, room]) => { const L = __ES._T[k].chests.filter(C => C.room === room); L.forEach(C => __X.f(__X.hb(C.g), 'click', {connectionId: 5})); return L.map(C => C.note && C.note.getAttribute('src').split('/').pop().split('?')[0]); }", [k, room])
        return n
    def solve(k, wrong_first):
        T = "__ES._T[%d]" % k
        codes = pg.evaluate("(k) => __ES._T[k].codes", k)
        # ---- R1: open the 8 chests (8 different picture sums), type the code (a wrong one first -> 30 s lock)
        n1 = chests(k, 0)
        ok(len(n1) == 8 and all(n1) and len(set(n1)) == 8, "team %d: R1 8 chests open, 8 different sums %s" % (k, n1[:2]))
        paint = pg.evaluate("(k) => __ES._T[k].shown.map(n => n.getAttribute('src').split('/').pop().split('?')[0])", k)
        ok(len(paint) == 1 and paint[0].endswith('_p.jpg'), "team %d: the code painting is up (%s)" % (k, paint))
        if wrong_first:
            press(k, 0, "12"); ok(shown(k, 0) == 2, "team %d: screen shows 2 typed digits" % k)
            press(k, 0, "C"); ok(shown(k, 0) == 0, "team %d: CLR empties the screen" % k)
            press(k, 0, str((int(codes[0][0]) + 1) % 10) + codes[0][1:] + "K"); time.sleep(1.2)
            ok(abs(dz(k, 1)) < 0.05, "team %d: wrong code keeps door 1 shut" % k)
            press(k, 0, codes[0] + "K", who=7); time.sleep(1.5)
            ok(abs(dz(k, 1)) < 0.05, "team %d: while locked, even the RIGHT code does nothing" % k)
            red = pg.evaluate("(k) => Array.from(__ES._T[k].kp[0].disp.querySelectorAll('m-model')).map(m => m.getAttribute('src').match(/ms_(r\\d)/)[1]).join('')", k)
            ok(red.startswith('r'), "team %d: screen counts down in red (%s)" % (k, red))
            time.sleep(28.5)
        press(k, 0, codes[0] + "K"); time.sleep(3.2)
        ok(abs(dz(k, 1) + 2.5) < 0.05, "team %d: code %s opens door 1" % (k, codes[0]))
        # ---- R2: the message is up, 6 chests hold 6 key pieces
        n2 = chests(k, 1)
        ok(len(n2) == 6 and len(set(n2)) == 6 and all('_k' in x for x in n2), "team %d: R2 6 chests, 6 key pieces" % k)
        press(k, 1, codes[1] + "K"); time.sleep(3.2)
        ok(abs(dz(k, 2) + 2.5) < 0.05, "team %d: cipher answer %s opens door 2" % (k, codes[1]))
        # ---- R3: the floating code lines up from the true eye only
        geo = pg.evaluate("""(k) => { const T = __ES._T[k]; return { eyeI: T.eyeI, bars: Array.from(T.bars.children).map(o => { const c = o.firstElementChild;
              return [+o.getAttribute('x'), +o.getAttribute('y'), +o.getAttribute('z'), +o.getAttribute('ry'), +c.getAttribute('rx'), +c.getAttribute('width'), +c.getAttribute('height')]; }) }; }""", k)
        E3 = TMS[k]['eye']; import math
        def spread(spot):
            V = [spot[0], spot[1] + 2.2, spot[2]]; C = E3['c']
            f = [C[i] - V[i] for i in range(3)]; L = math.sqrt(sum(v * v for v in f)); f = [v / L for v in f]
            hr = math.hypot(f[0], f[2]); rt = [-f[2] / hr, 0, f[0] / hr]
            up = [rt[1] * f[2] - rt[2] * f[1], rt[2] * f[0] - rt[0] * f[2], rt[0] * f[1] - rt[1] * f[0]]
            pts = []
            for (x, y, z, *_r) in geo['bars']:
                d = [x - V[0], y - V[1], z - V[2]]; dep = sum(d[i] * f[i] for i in range(3))
                pts.append((sum(d[i] * rt[i] for i in range(3)) / dep * L, sum(d[i] * up[i] for i in range(3)) / dep * L, dep / L))
            return pts
        def ideal_err(spot):      # for the true eye, every stroke projects onto the digit plane at a "grid" spot: |x|,|y| multiples of the segment layout
            U = 1.1 * math.dist([spot[0], spot[1] + 2.2, spot[2]], E3['c']) / 20
            P = spread(spot); n_dig = sum(len(["abcdef", "bc", "abged", "abgcd", "fgbc", "afgcd", "afgedc", "abc", "abcdefg", "abcdfg"][int(c)]) for c in codes[2])
            errs_ = []
            for (sx, sy, dep) in P[:n_dig]:
                gx = sx / U; gy = sy / U
                cands = [(j - 1.5) * 1.6 + ox for j in range(4) for ox in (-0.5, 0, 0.5)]
                errs_.append(min(abs(gx - c) for c in cands) + min(abs(gy - c) for c in (-1, -0.5, 0, 0.5, 1)))
            return max(errs_), n_dig
        e_true, nd = ideal_err(E3['spots'][geo['eyeI']])
        e_wrong = max(ideal_err(E3['spots'][j])[0] for j in range(3) if j != geo['eyeI'])
        ok(len(geo['bars']) == nd + 9, "team %d: %d strokes for code %s + 9 strays" % (k, len(geo['bars']), codes[2]))
        ok(e_true < 0.02 and e_wrong > 0.15, "team %d: strokes line up from the true eye (err %.3f) but not from the others (err %.2f)" % (k, e_true, e_wrong))
        press(k, 2, codes[2] + "K"); time.sleep(3.2)
        ok(abs(dz(k, 3) + 2.5) < 0.05, "team %d: witch code %s opens door 3" % (k, codes[2]))
        ok(pg.evaluate("(k) => __ES._T[k].bars === null", k), "team %d: floating strokes removed after R3" % k)
        # ---- R4: 8 clue notes on the walls, 6 chests (the rest of the clues + junk)
        n4 = chests(k, 3); walls = pg.evaluate("(k) => __ES._T[k].shown.filter(n => /w\\d+_/.test(n.getAttribute('src'))).length", k)
        clues = sum(1 for x in n4 if not x.startswith('w_empty'))
        n_cl = pg.evaluate("(k) => window.__ES._T[k].codes && 0", k)
        total = len(json.loads(open(sys.argv[1]).read().split('const D = ')[1].split(';\n')[0])['escape']['riddle'][pg.evaluate("(k) => __ES._T[k].si[2]", k)]['notes'])
        ok(walls + clues == total and clues >= 2, "team %d: all %d riddle clues findable: %d on the walls, %d in chests" % (k, total, walls, clues))
        press(k, 3, codes[3] + "K"); time.sleep(3.2)
        ok(abs(dz(k, 4) + 2.5) < 0.05, "team %d: riddle answer %s opens the Victory Hall door" % (k, codes[3]))
    TMS = json.loads(open(sys.argv[1]).read().split('const D = ')[1].split(';\n')[0])['escape']['teams']
    t0 = time.time()
    solve(2, True)
    say("escape"); print(ack())
    lamps = pg.evaluate("() => Array.from(document.querySelectorAll('m-image[src*=\"gem_2.png\"]')).filter(s => s.getAttribute('visible') === 'true').length")
    ok(lamps == 8, "progress boards: team green 4 gems lit on both boards (%d)" % lamps)
    med = pg.evaluate("() => document.querySelectorAll('m-image[src*=\"medal_0.png\"]').length"); ok(med == 2, "1ST medal under green on both boards")
    ban = pg.evaluate("() => document.querySelectorAll('m-image[src*=\"win_2.jpg\"]').length"); ok(ban == 2, "GREEN ESCAPED FIRST banner on both boards")
    acks = pg.evaluate("() => JSON.parse(document.querySelector('[data-ack]').getAttribute('data-ack')).l.map(a => a.t)")
    ok(any("GREEN ESCAPED FIRST" in a for a in acks), "host told: GREEN ESCAPED FIRST")
    solve(4, False)
    acks = pg.evaluate("() => JSON.parse(document.querySelector('[data-ack]').getAttribute('data-ack')).l.map(a => a.t)")
    ok(any("PURPLE OUT IN PLACE 2" in a for a in acks), "purple second")
    # host tools
    say("escape hint red"); print(ack())
    fk = pg.evaluate("() => { const T = __ES._T[0]; return T.chests.filter(C => C.open).map(C => [T.map0[C.j], C.g.querySelector('m-label') ? 1 : 0]); }")
    fake = pg.evaluate("() => __ES._T[0].si[0]"); fakes = json.loads(open(sys.argv[1]).read().split('const D = ')[1].split(';\n')[0])['escape']['sums'][fake]['fake']
    ok(len(fk) == 2 and sorted(f[0] for f in fk) == sorted(fakes) and all(f[1] for f in fk), "R1 hint opens exactly the 2 fake sums, marked FAKE")
    for r in range(3):
        say("escape skip red"); print(ack()); time.sleep(2.5); ok(abs(dz(0, r + 1) + 2.5) < 0.05, "skip opened red's door %d" % (r + 1))
        say("escape hint red"); print(ack())
    say("escape raffle"); r = ack(); print(r); ok("RAFFLE WINNER (GREEN)" in r, "raffle picks from the winning team")
    say("escape end"); print(ack()); time.sleep(2.6)
    ok(all(abs(dz(k, d) + 2.5) < 0.05 for k in range(6) for d in range(5)), "END opened every door")
    say("escape open"); print(ack()); time.sleep(2.6)
    ok(all(abs(dz(k, 0) + 2.5) < 0.05 for k in range(6)) and all(abs(dz(k, d)) < 0.05 for k in range(6) for d in range(1, 5)), "OPEN: fresh game, start doors open")
    ok(pg.evaluate("() => __ES._T.every(T => T.chests.every(C => !C.open) && !T.shown.length && !T.hints.length && T.stage === 0)"), "OPEN: chests shut, pictures and hints gone")
    sets = pg.evaluate("() => __ES._T.map(T => T.si.join(','))"); ok(len(set(sets)) == 6, "every team got a different puzzle set %s" % sets)
    say("escape"); print(ack())
    print("ERRORS:", errs or "none", "| %.0f s" % (time.time() - t0))
    b.close()
