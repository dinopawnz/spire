"""Meshy batch: for each item, make a clean reference picture (nano-banana-pro, isolated on grey), then image-to-3D (textured, PBR),
download the GLB. Runs all items in parallel.  python3 batch3d.py items.json   (skips items whose GLB already exists)
items.json = [{"name": "...", "prompt": "...", "poly": 20000}, ...]"""
import json, sys, time, base64, os, threading, urllib.request
KEY = open('/home/claude/.meshy_key').read().strip()
API = 'https://api.meshy.ai/openapi/v1/'
OUT = '/home/claude/meshy/models/'; os.makedirs(OUT, exist_ok=True)
STYLE = (" Single object only, a 3D game asset concept, isolated on a plain flat light grey background, the whole object visible, "
         "three-quarter view from slightly above, soft even studio light, photoreal, highly detailed, rich natural materials.")
def call(path, data=None):
    for attempt in range(5):
        try:
            req = urllib.request.Request(API + path, data=json.dumps(data).encode() if data else None,
                                         headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
            return json.load(urllib.request.urlopen(req, timeout=120))
        except Exception as e:
            if attempt == 4: raise
            time.sleep(8 * (attempt + 1))
def wait(kind, tid, limit=1800):
    t0 = time.time()
    while True:
        d = call(kind + '/' + tid)
        if d['status'] in ('SUCCEEDED', 'FAILED', 'CANCELED') or time.time() - t0 > limit: return d
        time.sleep(8)
def log(*a):
    with open(OUT + 'batch.log', 'a') as f: f.write(time.strftime('%H:%M:%S ') + ' '.join(map(str, a)) + '\n')
def run(it):
    n = it['name']; glb = OUT + n + '.glb'
    if os.path.exists(glb): return
    try:
        ref = OUT + n + '_ref.png'
        if not os.path.exists(ref):
            tid = call('text-to-image', dict(ai_model='nano-banana-pro', aspect_ratio='1:1', prompt=it['prompt'] + STYLE))['result']
            d = wait('text-to-image', tid)
            if d['status'] != 'SUCCEEDED': log(n, 'image FAILED', d.get('task_error')); return
            urllib.request.urlretrieve(d['image_urls'][0], ref); log(n, 'ref ok')
        uri = 'data:image/png;base64,' + base64.b64encode(open(ref, 'rb').read()).decode()
        tid = call('image-to-3d', dict(image_url=uri, ai_model='latest', should_texture=True, enable_pbr=True, should_remesh=True,
                                       topology='triangle', target_polycount=it.get('poly', 20000)))['result']
        log(n, '3d task', tid)
        d = wait('image-to-3d', tid)
        if d['status'] != 'SUCCEEDED': log(n, '3d FAILED', d.get('task_error')); return
        urllib.request.urlretrieve(d['model_urls']['glb'], glb); log(n, '3d ok credits', d.get('consumed_credits'))
    except Exception as e:
        log(n, 'ERROR', repr(e))
items = json.load(open(sys.argv[1]))
th = [threading.Thread(target=run, args=(it,)) for it in items]
for t in th: t.start(); time.sleep(1.5)
for t in th: t.join()
log('BATCH DONE', sys.argv[1])
