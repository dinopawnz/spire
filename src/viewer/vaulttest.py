"""(v55) VAULT DOOR TEST: 4 finalists + 8 other players + a late joiner. Checks who the vault door (and its invisible wall) is shut for
at every step: before the host opens it (shut for everyone, finalists too), after OPEN (open only for the finalists), after START THE
FINALS, after a late joiner connects, after LOCK; a non-finalist inside is reported; non-finalists can't pick; a finalist's wrong pick
locks them 10 s; REMOVE takes a finalist out (and the door shuts for them).   python3 vaulttest.py /home/claude/spire/out/spire.html"""
import sys, time, json
from playwright.sync_api import sync_playwright
fails = []
def ok(c, m): print(('OK   ' if c else 'FAIL ') + m); (None if c else fails.append(m))
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + sys.argv[1]); time.sleep(1)
    conn = lambda i: pg.evaluate("(i) => window.dispatchEvent(new CustomEvent('connected', {detail:{connectionId:i}}))", i)
    for i in range(1, 14): conn(i)
    say = lambda c, who=1: pg.evaluate("([c, w]) => { document.getElementById('sp-host').dispatchEvent(new CustomEvent('prompt', {detail:{value:'7747 '+c, connectionId:w}, bubbles:true})); return JSON.parse(document.querySelector('[data-ack]').getAttribute('data-ack')).t; }", [c, who])
    say("remote", 13)                    # #13 is the host's remote (not a player)
    say("build"); time.sleep(3)
    G = lambda: json.loads(pg.evaluate("() => document.querySelector('[data-game]').getAttribute('data-game')"))
    VIS = """() => { const d = document.querySelector('m-model[src*="sp_vault_door"]'); const pad = Array.from(document.querySelectorAll('m-cube')).find(c => c.getAttribute('width') === '3.2' && c.getAttribute('height') === '3.6');
      return [d.getAttribute('visible-to'), pad.getAttribute('visible-to')]; }"""
    def shut_for():
        v = pg.evaluate(VIS); ids = list(range(1, 13)) + extra
        res = []
        for va in v: res.append(set(ids) if va is None else set(int(x) for x in va.split() if x != '-1'))
        return res
    extra = []
    FIN = [3, 5, 7, 9]; OTHERS = [i for i in range(1, 13) if i not in FIN]
    print(say("hall open"))
    for f in FIN: print(say("finalist %d" % f))
    for (d, pad) in [shut_for()]: ok(d == set(range(1, 13)) and pad == set(range(1, 13)), "before OPEN THE VAULT DOOR: door + wall shut for all 12 (finalists too)")
    print(say("hall door open"))
    d, pad = shut_for()
    ok(d == set(OTHERS) and pad == set(OTHERS), "after OPEN: door + wall gone for the 4 finalists only, still shut for the 8 others %s" % sorted(pad))
    conn(20); extra = [20]; time.sleep(0.3)
    d, pad = shut_for(); ok(20 in d and 20 in pad, "a player who connects later meets the shut door too")
    # a non-finalist standing inside the vault is reported
    pg.evaluate("""() => { const pr = document.querySelector('m-position-probe'); pr.dispatchEvent(new CustomEvent('positionenter', {detail: {connectionId: 4, elementRelative: {position: {x: 2, y: 10.6, z: 3}}}, bubbles: true})); }""")
    time.sleep(1.2); g = G(); ok(len(g['intruders']) == 1 and g['vaultDoor'] is True, "a non-finalist inside the glass room is reported to the host: %s" % g['intruders'])
    print(say("hall finals")); time.sleep(0.5)
    d, pad = shut_for(); ok(d == set(OTHERS + [20]) and pad == set(OTHERS + [20]), "START THE FINALS does not open the door for anyone else")
    frost = pg.evaluate("() => !!document.querySelector('m-model[src*=\"sp_vault_frost\"]')"); print('   frost still there right after start (it sinks over 2 s):', frost)
    # picks: a non-finalist can't pick; a finalist's wrong pick = 10 s
    r = pg.evaluate("""() => { const ms = Array.from(document.querySelectorAll('m-model[src*="portraits/pv_"]'));
       ms[0].dispatchEvent(new CustomEvent('click', {detail: {connectionId: 4}, bubbles: true}));
       const before = document.querySelectorAll('m-model[src*="portraits/pv_"]').length; return [ms.length, before]; }""")
    real = json.loads(open(sys.argv[1]).read().split('const D = ')[1].split(';\n')[0])['realVault']
    wrong = pg.evaluate("""(real) => { const ms = Array.from(document.querySelectorAll('m-model[src*="portraits/pv_"]'));
       const m = ms.find(m => !m.getAttribute('src').includes('pv_' + String(real).padStart(3, '0') + '.glb')); m.dispatchEvent(new CustomEvent('click', {detail: {connectionId: 3}, bubbles: true})); return 1; }""", real)
    time.sleep(1.2)
    pl = json.loads(pg.evaluate("() => document.querySelector('[data-players]').getAttribute('data-players')"))
    w3 = [q for q in pl if q[0] == 3][0][4]; w4 = [q for q in pl if q[0] == 4][0][4]
    ok(9 <= w3 <= 10, "a finalist's wrong pick in the vault locks them for 10 seconds (%d s left)" % w3)
    ok(w4 == 0 and G()['ph'] == 'finals', "a non-finalist's click in the vault does nothing")
    print(say("hall door close")); d, pad = shut_for(); ok(d == set(range(1, 13)) | {20} and pad == d, "LOCK THE VAULT DOOR: shut for everyone again")
    print(say("hall door open")); print(say("hall unfinalist 9")); d, pad = shut_for()
    ok(9 in d and 9 in pad and 3 not in pad, "REMOVE a finalist: the door shuts for them, stays open for the other finalists")
    ok(G()['fin'] == 3, "3 finalists left")
    print("ERRORS:", errs or "none", "| FAILS:", len(fails))
    b.close()
