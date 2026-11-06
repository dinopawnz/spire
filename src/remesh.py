"""Meshy remesh: lighter versions of repeated outside pieces.  python3 remesh.py   -> models/<name>.glb replaced (old kept as <name>_hi.glb)"""
import json, time, urllib.request, os, shutil, threading
KEY = open('/home/claude/.meshy_key').read().strip()
def call(path, data=None):
    req = urllib.request.Request('https://api.meshy.ai/openapi/v1/' + path, data=json.dumps(data).encode() if data else None,
                                 headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=120))
JOBS = {'railing': ('01a1af3b-75ba-7388-89e6-228a7ee8ef88', 1800), 'lily': ('01a1af3b-8efd-76ec-b589-22fa0adbe73f', 1200),
        'crystals': ('01a1af3b-7bb8-756d-9bae-01ceea4cc08a', 2500), 'mossclump': ('01a1af3b-a512-7706-a355-2f8374e71b67', 1500),
        'lanternpost': ('01a1af3b-70e6-7245-a012-1b4e5a7f74f0', 2500), 'bonsai': ('01a1af3b-866e-7184-b45f-1e48e555eb85', 8000),
        'island': ('01a1af3b-81d3-742f-8b47-4e7a908ecd00', 12000), 'cliff': ('01a1af3b-a97e-710b-8d19-0327184c0f8f', 14000)}
def run(name, tid, poly):
    try:
        r = call('remesh', dict(input_task_id=tid, target_polycount=poly, topology='triangle', target_formats=['glb']))['result']
        while True:
            d = call('remesh/' + r)
            if d['status'] in ('SUCCEEDED', 'FAILED', 'CANCELED'): break
            time.sleep(6)
        if d['status'] != 'SUCCEEDED': print(name, d['status'], d.get('task_error'), flush=True); return
        src = 'models/%s.glb' % name
        if not os.path.exists('models/%s_hi.glb' % name): shutil.copy(src, 'models/%s_hi.glb' % name)
        urllib.request.urlretrieve(d['model_urls']['glb'], src); print(name, 'ok', d.get('consumed_credits'), flush=True)
    except Exception as e: print(name, 'ERROR', e, flush=True)
th = [threading.Thread(target=run, args=(n, t, p)) for n, (t, p) in JOBS.items()]
[t.start() for t in th]; [t.join() for t in th]
