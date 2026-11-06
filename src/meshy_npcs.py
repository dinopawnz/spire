"""Mudwater Spire NPCs through the Meshy API: preview (shape) -> refine (paint) -> rig (skeleton) -> animations.
Resumable: every task id is kept in out/meshy/state.json, so rerunning never pays twice for a finished step.
    python3 meshy_npcs.py            run / resume everything
Key is read from /home/claude/.meshy_key (never written into the build)."""
import json, os, sys, time, base64, urllib.request, urllib.error

KEY = open('/home/claude/.meshy_key').read().strip()
API = 'https://api.meshy.ai/openapi/'
OUT = '/home/claude/spire/out/meshy/'
os.makedirs(OUT, exist_ok=True)
import glob
STATE = OUT + 'state.json'                                    # legacy shared file (read only)
S = json.load(open(STATE)) if os.path.exists(STATE) else {}
for f in glob.glob(OUT + 'state_*.json'): S[f[len(OUT) + 6:-5]] = json.load(open(f))
MINE = set()
def save():
    for n in MINE:
        if n in S: json.dump(S[n], open(OUT + 'state_%s.json' % n, 'w'), indent=1)

STYLE = ('Full-body stylized 3D game character, hand-painted cartoon look, friendly chunky proportions, standing upright on two legs '
         'in a relaxed A-pose with arms held away from the body, feet apart, facing forward, empty hands, no props, no base. ')
NPCS = {
  'ferryman': dict(h=1.6, anims=[11, 313, 290, 41], prompt=STYLE + 'An elderly anthropomorphic snapping turtle ferryman from the bayou: wrinkled olive-brown skin, '
                   'a mossy domed shell on his back, a wide frayed straw hat, a patched dark oilskin raincoat with a rope belt, rolled trouser legs, bare webbed feet, '
                   'kind sleepy eyes and white whiskers on his chin.',
                   tex='Weathered olive and brown turtle skin, mossy green shell with algae, faded straw hat, dark teal patched oilskin coat, hemp rope belt, soft swamp lantern-light mood.'),
  'barkeep': dict(h=1.6, anims=[0, 314, 342, 290], prompt=STYLE + 'A plump cheerful middle-aged FROG woman bartender (amphibian, no ears, no fur): a wide flat frog head with a very wide '
                  'smiling mouth, big bulging golden frog eyes on top of the head, smooth spotted frog skin, a short thick neck, a round pear-shaped body, '
                  'a red headscarf knotted on top, a cream blouse with rolled sleeves, a long leather bar apron, big webbed frog feet and webbed fingers.',
                  tex='Glossy olive-green frog skin with darker spots and a pale yellow belly, red headscarf with white polka dots, cream cotton blouse, worn brown leather apron with brass buckle.'),
  'gator': dict(h=2.2, anims=[12, 313, 317, 28], prompt=STYLE + 'A big gentle anthropomorphic alligator man: tall and broad with a round belly, bumpy dark green scaly hide, '
                'a long snout with a goofy toothy grin, faded blue denim overalls over a red plaid flannel shirt, a short thick tail, bare clawed feet.',
                tex='Dark mossy green alligator scales with a cream belly, white teeth, faded blue denim overalls with brass buttons, red and black plaid flannel shirt.'),
  'skipper': dict(h=1.85, anims=[243, 310, 290, 59], prompt=STYLE + 'A big burly ELDERLY gorilla-like ape sea captain, about seventy years old: a heavy brow, a wide flat ape nose and muzzle, '
                  'long arms, grey-brown fur going white, a big bushy white beard, a stocky barrel chest and slight belly, a navy double-breasted peacoat with brass buttons, '
                  'a flat white merchant captain cap with a black visor (not a pirate hat), a red neckerchief, black boots. Wise, weathered, kind.',
                  tex='Grey-brown ape fur, snowy white beard, navy wool peacoat with shiny brass buttons, off-white captain cap with gold anchor badge, red neckerchief, scuffed black leather boots.'),
  'appraiser': dict(h=1.8, anims=[0, 314, 42, 317], prompt=STYLE + 'An elegant anthropomorphic raccoon art appraiser: slim and tall, grey striped fur with a black bandit mask, '
                    'a gold monocle over one eye, a brown tweed three-piece suit with waistcoat and a gold pocket-watch chain, a burgundy bow tie, white gloves, polished shoes.',
                    tex='Grey raccoon fur with a black eye mask and striped tail, brown herringbone tweed suit, mustard waistcoat, gold monocle and watch chain, burgundy silk bow tie, white gloves.'),
  'dealer': dict(h=1.7, anims=[11, 56, 313, 298], prompt=STYLE + 'A sly grinning anthropomorphic opossum card dealer: grey fur, a long pointed pink snout, round ears, '
                 'a green translucent dealer visor, a white shirt with red sleeve garters, a black satin vest, a red bow tie, black trousers, a long bare tail.',
                 tex='Silver-grey opossum fur with a white face and pink snout and ears, translucent green visor, crisp white shirt, red sleeve garters, black satin vest, red bow tie.'),
}

def req(method, path, body=None, raw_url=None):
    url = raw_url or API + path
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(r, timeout=120) as f: return json.loads(f.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:400]
            if e.code == 429 or e.code >= 500:
                if method == 'POST': raise RuntimeError('POST %s -> %d %s (not retried, check tasks first)' % (path, e.code, msg))
                time.sleep(5); continue
            raise RuntimeError('%s %s -> %d %s' % (method, path, e.code, msg))
        except Exception as e:
            if method == 'POST': raise
            time.sleep(5)
    raise RuntimeError('gave up on ' + path)

def wait(path):
    t0 = time.time()
    while time.time() - t0 < 3600:
        t = req('GET', path)
        if t['status'] == 'SUCCEEDED': return t
        if t['status'] in ('FAILED', 'CANCELED'): raise RuntimeError('%s %s: %s' % (path, t['status'], (t.get('task_error') or {}).get('message')))
        time.sleep(6)
    raise TimeoutError(path)

def dl(url, path):
    with urllib.request.urlopen(urllib.request.Request(url), timeout=300) as f: open(path, 'wb').write(f.read())
    return path

def step(name, key, create, poll_path):
    """create once (id stored), then wait and store the finished task"""
    st = S.setdefault(name, {})
    if st.get(key + '_done'): return st[key + '_done']
    if not st.get(key):
        st[key] = create(); save(); print(name, key, 'created', st[key], flush=True)
    t = wait(poll_path(st[key]))
    st[key + '_done'] = t; save(); print(name, key, 'done (%s credits)' % t.get('consumed_credits'), flush=True)
    return t

def run_npc(name, spec):
    p = step(name, 'preview', lambda: req('POST', 'v2/text-to-3d', dict(mode='preview', prompt=spec['prompt'], model_type='smart-topology', ai_model='meshy-t2.5',
                                                                         target_polycount=20000, pose_mode='a-pose', target_formats=['glb']))['result'],
             lambda i: 'v2/text-to-3d/' + i)
    if not os.path.exists(OUT + name + '_preview.png') and p.get('thumbnail_url'): dl(p['thumbnail_url'], OUT + name + '_preview.png')
    if S[name].get('hold'): return
    r = step(name, 'refine', lambda: req('POST', 'v2/text-to-3d', dict(mode='refine', preview_task_id=S[name]['preview'], ai_model='latest', enable_pbr=True,
                                                                        texture_prompt=spec['tex'], texture_resolution='2k', target_formats=['glb']))['result'],
             lambda i: 'v2/text-to-3d/' + i)
    if not os.path.exists(OUT + name + '_textured.glb'): dl(r['model_urls']['glb'], OUT + name + '_textured.glb')
    if r.get('thumbnail_url') and not os.path.exists(OUT + name + '_textured.png'): dl(r['thumbnail_url'], OUT + name + '_textured.png')
    rig_and_animate(name, dict(input_task_id=S[name]['refine'], height_meters=spec['h']), spec['anims'])

IMG = {
  'barkeep': ('Character concept art for a 3D game, full body, front view, centered, plain light grey background. A plump cheerful anthropomorphic BULLFROG woman bartender: '
              'a wide flat green frog head with huge bulging golden eyes and a very wide friendly smile, no ears, no hair, smooth olive-green spotted frog skin with a pale yellow belly, '
              'a red polka-dot headscarf knotted on top, a cream blouse with rolled sleeves, a long brown leather bar apron, webbed hands, big webbed frog feet. '
              'Stylized hand-painted cartoon style, chunky friendly proportions, standing in an A-pose, empty hands.'),
  'skipper': ('Character concept art for a 3D game, full body, front view, centered, plain light grey background. A burly ELDERLY GORILLA sea captain: '
              'a dark grey gorilla face with a heavy brow ridge, flat wide nose and big muzzle, long powerful arms, grey and white fur, a big bushy white beard, '
              'a navy double-breasted peacoat with brass buttons, a flat white merchant captain cap with a black visor and a gold anchor badge, a red neckerchief, black boots. '
              'Stylized hand-painted cartoon style, chunky friendly proportions, standing in an A-pose, empty hands.'),
}

def run_img_npc(name, spec):
    im = step(name, 'image', lambda: req('POST', 'v1/text-to-image', dict(ai_model='nano-banana-2', prompt=IMG[name], pose_mode='a-pose'))['result'],
              lambda i: 'v1/text-to-image/' + i)
    url = (im.get('image_urls') or [None])[0]
    if url and not os.path.exists(OUT + name + '_concept.png'): dl(url, OUT + name + '_concept.png')
    if S[name].get('hold'): return
    t = step(name, 'i23d', lambda: req('POST', 'v1/image-to-3d', dict(image_url=url, model_type='smart-topology', ai_model='meshy-t2.5', target_polycount=20000,
                                                                       pose_mode='a-pose', should_texture=True, texture_model='meshy-n1', target_formats=['glb']))['result'],
             lambda i: 'v1/image-to-3d/' + i)
    if not os.path.exists(OUT + name + '_textured.glb'): dl(t['model_urls']['glb'], OUT + name + '_textured.glb')
    if t.get('thumbnail_url') and not os.path.exists(OUT + name + '_textured.png'): dl(t['thumbnail_url'], OUT + name + '_textured.png')
    rig_and_animate(name, dict(input_task_id=S[name]['i23d'], height_meters=spec['h']), spec['anims'])

def rig_and_animate(name, rig_body, anims):
    g = step(name, 'rig', lambda: req('POST', 'v1/rigging', rig_body)['result'], lambda i: 'v1/rigging/' + i)
    res = g.get('result', {})
    if res.get('rigged_character_glb_url') and not os.path.exists(OUT + name + '_rigged.glb'): dl(res['rigged_character_glb_url'], OUT + name + '_rigged.glb')
    a = step(name, 'anim', lambda: req('POST', 'v1/animations', dict(rig_task_id=S[name]['rig'], action_ids=anims))['result'], lambda i: 'v1/animations/' + i)
    ar = a.get('result', {})
    url = ar.get('animation_glb_url') or a.get('animation_glb_url')
    if url and not os.path.exists(OUT + name + '_anim.glb'): dl(url, OUT + name + '_anim.glb')

if __name__ == '__main__':
    import threading
    PREVIEW_ONLY = '--preview' in sys.argv
    which = [a for a in sys.argv[1:] if not a.startswith('--')] or list(NPCS)
    REDO = '--redo' in sys.argv
    for n in which:
        MINE.add(n)
        if n in NPCS:
            if REDO: S[n] = {}
            if '--image' in sys.argv: S[n]['via_image'] = True
            S.setdefault(n, {})['hold'] = PREVIEW_ONLY
    save()
    errs = {}
    def go(n):
        try:
            if n == 'operator':
                rig_and_animate('operator', dict(model_url='data:application/octet-stream;base64,' + base64.b64encode(open('/home/claude/apes/ape_5413_small.glb', 'rb').read()).decode(),
                                                 height_meters=2.0), [0, 313, 41, 290, 298])
            elif n in IMG and S[n].get('via_image'): run_img_npc(n, NPCS[n])
            else: run_npc(n, NPCS[n])
        except Exception as e: errs[n] = str(e); print(n, 'ERROR', e, flush=True)
    th = [threading.Thread(target=go, args=(n,)) for n in which]
    for t in th: t.start(); time.sleep(1.5)
    for t in th: t.join()
    print('ALL DONE', 'errors:', errs, flush=True)
