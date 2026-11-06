"""MUD ROYALE bot test: 40 bots step onto team pads (some switch), host starts, bots play every card by clicking hand cards and squares,
captures are checked against the card numbers, late joiners can't play, END NOW crowns a winner + MVP, NEW GAME reopens.
python3 royaletest.py /home/claude/spire/out/spire.html"""
import sys, time, json, random
from playwright.sync_api import sync_playwright
CARDS = json.load(open('/home/claude/spire/cards/cards.json'))
V = lambda n: [CARDS[str(n)][k] for k in ('t', 'l', 'r', 'b')]
rng = random.Random(5)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    NB = 40
    pg.evaluate("(n) => { for (let id = 1; id <= n + 1; id++) window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:id}})); }", NB)
    say = lambda c: pg.evaluate("(c) => document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:1}, bubbles:true}))", c)
    ack = lambda: json.loads(pg.evaluate("() => document.querySelector('[data-ack]').getAttribute('data-ack')"))['t']
    say("build"); time.sleep(3)
    pg.evaluate("""() => { const f = (n, name, d) => n.dispatchEvent(new CustomEvent(name, {detail: d, bubbles: true}));
      window.__R = { f,
        slabs: Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('collision-interval') === '90' && c.getAttribute('depth') === '5.5'),
        tiles: Array.from(document.querySelectorAll('m-cube')).filter(c => c.getAttribute('width') === '2.46' && c.getAttribute('height') === '0.1') }; }""")
    print("pads", pg.evaluate("() => __R.slabs.length"), "squares", pg.evaluate("() => __R.tiles.length"))
    # bots 2..41 step on pads; 10 of them switch once
    team = {}
    for id in range(2, NB + 2):
        t = rng.randrange(4); team[id] = t
        pg.evaluate("([id, t]) => __R.f(__R.slabs[t], 'collisionstart', {connectionId: id})", [id, t])
    for id in rng.sample(range(2, NB + 2), 10):
        t = (team[id] + 1) % 4; team[id] = t
        pg.evaluate("([id, t]) => __R.f(__R.slabs[t], 'collisionmove', {connectionId: id})", [id, t])
    say("royale"); print(ack())
    want = [sum(1 for v in team.values() if v == k) for k in range(4)]
    print("expected per team", want)
    say("royale start"); print(ack())
    # a late joiner (id 50) can't join now
    pg.evaluate("() => { window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:50}})); __R.f(__R.slabs[0], 'collisionstart', {connectionId: 50}); }")
    hand = lambda id: pg.evaluate("""(id) => { const gs = Array.from(document.querySelectorAll('m-group[visible-to="' + id + '"]')).filter(g => g.querySelector('m-image[src*="royale/c_"]'));
        if (!gs.length) return null; const g = gs[0];
        return Array.from(g.querySelectorAll('m-image')).map(im => [parseInt(im.getAttribute('src').match(/c_(\\d+)/)[1]), parseFloat(im.getAttribute('x'))]); }""", id)
    print("bot 2 hand:", hand(2), "| late joiner hand:", hand(50))
    board = {}            # tile -> [card, team]
    caps_ok = caps_bad = 0
    N = 10
    for rnd in range(5):
        for id in range(2, NB + 2):
            h = hand(id)
            if not h: continue
            pick = rng.randrange(len(h))                                  # click a hand card (on the first hand board)
            pg.evaluate("""([id, x]) => { const g = Array.from(document.querySelectorAll('m-group[visible-to="' + id + '"]')).filter(g => g.querySelector('m-image[src*="royale/c_"]'))[0];
                const hb = Array.from(g.querySelectorAll('m-cube')).find(c => c.getAttribute('x') === String(x) && c.getAttribute('opacity') === '0'); __R.f(hb, 'click', {connectionId: id}); }""", [id, h[pick][1]])
            card = h[pick][0]
            free = [i for i in range(100) if i not in board]
            if not free: break
            i = rng.choice(free)
            time.sleep(0.36 / 40)
            pg.evaluate("([id, i]) => __R.f(__R.tiles[i], 'click', {connectionId: id})", [id, i])
            # expected captures
            mine = V(card); exp = []
            for d, ms, ts in ((-N, 0, 3), (N, 3, 0), (-1, 1, 2), (1, 2, 1)):
                j = i + d
                if j < 0 or j >= 100 or (d == -1 and i % N == 0) or (d == 1 and i % N == N - 1) or j not in board: continue
                if board[j][1] != team[id] and mine[ms] > V(board[j][0])[ts]: exp.append(j)
            board[i] = [card, team[id]]
            for j in exp: board[j][1] = team[id]
        time.sleep(0.4)
    # compare the page's board with the model
    glows = pg.evaluate("""() => { const out = {}; __R.tiles.forEach((t, i) => {}); 
        return Array.from(document.querySelectorAll('m-image[src*="royale/t_"]')).map(im => { const g = im.parentNode; return [parseFloat(g.getAttribute('x')), parseFloat(g.getAttribute('z')), parseInt(im.getAttribute('src').match(/t_(\\d)/)[1])]; }); }""")
    page = {}
    for x, z, t in glows:
        c = int(round((x + 13 - 1.3) / 2.6)); r = int(round((z + 13 - 1.3) / 2.6)); page[r * 10 + c] = t
    same = sum(1 for i in board if page.get(i) == board[i][1])
    print("squares placed", len(board), "| page agrees with the card-number model on", same, "of", len(board))
    say("royale"); print(ack()); assert "LIVE" in ack(), "the game must keep running when the board is full"
    # UPGRADES: every bot with cards left tries a random square; stronger total replaces, weaker is refused
    tot = lambda n: sum(V(n)); up_ok = up_refused = mism = 0
    for id in range(2, NB + 2):
        h = hand(id)
        if not h: continue
        card, x = h[0]
        pg.evaluate("""([id, x]) => { const g = Array.from(document.querySelectorAll('m-group[visible-to="' + id + '"]')).filter(g => g.querySelector('m-image[src*="royale/c_"]'))[0];
            const hb = Array.from(g.querySelectorAll('m-cube')).find(c => c.getAttribute('x') === String(x) && c.getAttribute('opacity') === '0'); __R.f(hb, 'click', {connectionId: id}); }""", [id, x])
        i = rng.randrange(100); time.sleep(0.01)
        pg.evaluate("([id, i]) => __R.f(__R.tiles[i], 'click', {connectionId: id})", [id, i])
        after = hand(id) or []
        used = len(after) < len(h)
        if tot(card) > tot(board[i][0]):
            up_ok += used; mism += (not used)
            if used:
                board[i] = [card, team[id]]; mine = V(card)
                for d, ms, ts in ((-N, 0, 3), (N, 3, 0), (-1, 1, 2), (1, 2, 1)):
                    j = i + d
                    if j < 0 or j >= 100 or (d == -1 and i % N == 0) or (d == 1 and i % N == N - 1): continue
                    if board[j][1] != team[id] and mine[ms] > V(board[j][0])[ts]: board[j][1] = team[id]
        else:
            up_refused += (not used); mism += used
    glows = pg.evaluate("""() => Array.from(document.querySelectorAll('m-image[src*="royale/t_"]')).map(im => { const g = im.parentNode; return [parseFloat(g.getAttribute('x')), parseFloat(g.getAttribute('z')), parseInt(im.getAttribute('src').match(/t_(\\d)/)[1])]; })""")
    page = {}
    for x, z, t in glows: page[int(round((z + 11.7) / 2.6)) * 10 + int(round((x + 11.7) / 2.6))] = t
    print("upgrades done", up_ok, "| weaker refused", up_refused, "| wrong", mism, "| squares on page", len(glows), "| page agrees on", sum(1 for i in board if page.get(i) == board[i][1]), "of 100")
    assert mism == 0 and len(glows) == 100
    say("royale stop"); time.sleep(0.3)
    print([m for m in json.loads(pg.evaluate("() => document.querySelector('[data-ack]').getAttribute('data-ack')"))['l'] if 'OVER' in m['t']][-1]['t'])
    per = [sum(1 for v in board.values() if v[1] == k) for k in range(4)]; print("model per team", per)
    say("royale open"); print(ack())
    say("royale"); print(ack())
    print("ERRORS:", errs or "none"); b.close()
