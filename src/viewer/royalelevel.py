"""MUD ROYALE level rule (v45, owner): LEVEL 1 cards go on empty squares; LEVEL 2+ cards are upgrades - only on top of a lower-level
card (an enemy card becomes yours). Full board: same level + higher total may upgrade. Starting hands hold at least 2 level-1 cards.
python3 royalelevel.py /home/claude/spire/out/spire.html"""
import sys, time, json, random
from playwright.sync_api import sync_playwright
rng = random.Random(9); bad = 0
def ok(c, m):
    global bad
    print(('OK   ' if c else 'FAIL ') + m); bad += (not c)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    NB = 24
    pg.evaluate("(n) => { for (let id = 1; id <= n + 1; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }", NB)
    say = lambda c: pg.evaluate("(c) => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:1}, bubbles:true}))", c)
    say("build"); time.sleep(3)
    pg.evaluate("""() => { const f = (n, name, d) => n.dispatchEvent(new CustomEvent(name, {detail: d, bubbles: true}));
      window.__R = { f, slabs: Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('collision-interval') === '90' && c.getAttribute('depth') === '5.5'),
        tiles: Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('width') === '2.46' && c.getAttribute('height') === '0.1') }; }""")
    for id in range(2, NB + 2): pg.evaluate("([id, t]) => __R.f(__R.slabs[t], 'collisionstart', {connectionId: id})", [id, id % 4])
    say("royale start"); time.sleep(0.5)
    LV = pg.evaluate("() => __RLV")
    hands = lambda: pg.evaluate("() => Object.fromEntries(Array.from(__RY.hands.entries()).map(([id, H]) => [id, H.cards]))")
    h0 = hands()
    ok(all(sum(1 for c in cs if c is not None and LV[c] == 1) >= 2 for cs in h0.values()), "every starting hand has 2+ level-1 cards")
    board = lambda: pg.evaluate("() => __RY.board.map(b => b ? [b.c, b.team] : null)")
    def play(id, slot, tile):
        pg.evaluate("([id, k]) => { __RY.hands.get(id).sel = k; }", [id, slot])
        before = hands()[str(id)][slot]
        time.sleep(0.36); pg.evaluate("([id, i]) => __R.f(__R.tiles[i], 'click', {connectionId: id})", [id, tile])
        seen[0] = max(seen[0], pg.evaluate("() => Array.from(document.querySelectorAll('m-model')).filter(m => /ms_r_lvup|ms_r_lvlow/.test(m.getAttribute('src'))).length"))
        return hands()[str(id)][slot] is None and before is not None
    n_ok1 = n_ref = n_up = n_upref = 0; wrong = 0; seen = [0]
    for rnd in range(3):
        for id in range(2, NB + 2):
            cs = hands()[str(id)]
            for slot, c in enumerate(cs):
                if c is None: continue
                B = board(); empty = [i for i, x in enumerate(B) if x is None]
                if LV[c] == 1:
                    if not empty: continue
                    if play(id, slot, rng.choice(empty)): n_ok1 += 1
                    else: wrong += 1; print("  level-1 refused on empty square", id, c)
                else:
                    if empty:                                            # level 2+ on an empty square: must be refused
                        if play(id, slot, rng.choice(empty)): wrong += 1; print("  level", LV[c], "card went on an empty square!")
                        else: n_ref += 1
                    B = board()
                    lower = [i for i, x in enumerate(B) if x and LV[x[0]] < LV[c]]
                    same = [i for i, x in enumerate(B) if x and LV[x[0]] >= LV[c]]
                    if same and None in B:
                        if play(id, slot, rng.choice(same)): wrong += 1; print("  upgrade onto same/higher level allowed (board not full)")
                        else: n_upref += 1
                    if lower:
                        t = rng.choice(lower); was = B[t]
                        if play(id, slot, t):
                            n_up += 1; nb = board()[t]
                            if not (nb and nb[0] == c and nb[1] == (id % 4)): wrong += 1; print("  upgrade square wrong", nb)
                        else: wrong += 1; print("  upgrade onto lower level refused", LV[c], LV[was[0]])
                break
    ok(wrong == 0, "level-1 on empty: %d placed | level 2+ on empty refused: %d | upgrades on lower level: %d | upgrades onto same/higher refused: %d | wrong: %d" % (n_ok1, n_ref, n_up, n_upref, wrong))
    msgs = seen[0]
    ok(msgs > 0 or n_ref == 0, "players are told why (%d level messages shown)" % msgs)
    say("royale stop"); time.sleep(0.3)
    print("ERRORS:", errs or "none"); b.close()
    sys.exit(1 if bad or errs else 0)
