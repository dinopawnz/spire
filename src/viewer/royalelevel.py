"""MUD ROYALE - the OFFICIAL Mudwater rules (v47, owner's rules sheet): PLACE a level-1 card face up on an empty square; UPGRADE with a
card exactly ONE level higher on top of a square YOUR TEAM controls (never an enemy's); ROCK = any card face down (click it twice) on an
empty square - captures nothing, can't be captured, counts as level 1, one per player at a time. Captures: higher touching number wins.
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
    LV = pg.evaluate("() => __RLV"); team = lambda id: id % 4
    hands = lambda: pg.evaluate("() => Object.fromEntries(Array.from(__RY.hands.entries()).map(([id, H]) => [id, H.cards]))")
    ok(all(sum(1 for c in cs if c is not None and LV[c] == 1) >= 2 for cs in hands().values()), "every starting hand has 2+ level-1 cards")
    board = lambda: pg.evaluate("() => __RY.board.map(b => b ? [b.c, b.team, b.rock ? 1 : 0, b.by] : null)")
    lvl = lambda sq: 1 if sq[2] else LV[sq[0]]
    seen = [0]
    def play(id, slot, tile, rock=False):
        pg.evaluate("([id, k, r]) => { const H = __RY.hands.get(id); H.sel = k; H.rock = r; }", [id, slot, rock])
        before = hands()[str(id)][slot]
        time.sleep(0.36); pg.evaluate("([id, i]) => __R.f(__R.tiles[i], 'click', {connectionId: id})", [id, tile])
        seen[0] = max(seen[0], pg.evaluate("() => Array.from(document.querySelectorAll('m-model')).filter(m => /ms_r_lvup|ms_r_lvlow|ms_r_enemy|ms_r_rock1/.test(m.getAttribute('src'))).length"))
        return hands()[str(id)][slot] is None and before is not None
    st = dict(place=0, lvup_ref=0, up=0, up_ref_lv=0, up_ref_enemy=0, rock=0, rock2_ref=0, rock_cap=0); wrong = 0
    for rnd in range(4):
        for id in range(2, NB + 2):
            cs = hands()[str(id)]
            for slot, c in enumerate(cs):
                if c is None: continue
                B = board(); empty = [i for i, x in enumerate(B) if x is None]
                if False and rnd == 1 and empty:          # (v50) no rocks any more                                   # rocks: one is fine, a second (while the first is uncovered) is refused
                    mine_rock = any(x and x[2] and x[3] == id for x in B)
                    r = play(id, slot, rng.choice(empty), True)
                    if mine_rock: st['rock2_ref'] += (not r); wrong += r
                    else: st['rock'] += r; wrong += (not r)
                    break
                if LV[c] == 1:
                    if empty: wrong += not play(id, slot, rng.choice(empty)); st['place'] += 1
                    break
                if empty:
                    if play(id, slot, rng.choice(empty)): wrong += 1; print("  level", LV[c], "went on an empty square!")
                    else: st['lvup_ref'] += 1
                B = board()
                good = [i for i, x in enumerate(B) if x and x[1] == team(id) and lvl(x) == LV[c] - 1]
                enemy = [i for i, x in enumerate(B) if x and x[1] != team(id) and lvl(x) == LV[c] - 1]
                jump = [i for i, x in enumerate(B) if x and x[1] == team(id) and lvl(x) < LV[c] - 1]
                if enemy:
                    if play(id, slot, rng.choice(enemy)): wrong += 1; print("  upgrade on an ENEMY square allowed!")
                    else: st['up_ref_enemy'] += 1
                if jump:
                    if play(id, slot, rng.choice(jump)): wrong += 1; print("  upgrade jumped more than one level!")
                    else: st['up_ref_lv'] += 1
                if good:
                    t = rng.choice(good)
                    if play(id, slot, t): st['up'] += 1
                    else: wrong += 1; print("  legal upgrade refused", LV[c], board()[t])
                break
    # rocks are never captured: every rock is still its owner's team
    B = board(); rocks = [x for x in B if x and x[2]]
    ok(len(rocks) == 0, "no rocks in our version (%d on the board)" % len(rocks))
    ok(wrong == 0, "  ".join("%s %d" % kv for kv in st.items()) + " | wrong %d" % wrong)
    ok(seen[0] > 0, "players are told why a play is refused (%d messages seen)" % seen[0])
    say("royale stop"); time.sleep(0.3)
    print("ERRORS:", errs or "none"); b.close()
    sys.exit(1 if bad or errs else 0)
