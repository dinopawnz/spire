import json, time, urllib.request, threading
KEY = open('/home/claude/.meshy_key').read().strip()
def call(path, data=None):
    req = urllib.request.Request('https://api.meshy.ai/openapi/v1/' + path, data=json.dumps(data).encode() if data else None, headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=120))
def run(name, tid, poly):
    r = call('remesh', dict(input_task_id=tid, target_polycount=poly, topology='triangle', target_formats=['glb']))['result']
    while True:
        d = call('remesh/' + r)
        if d['status'] in ('SUCCEEDED', 'FAILED', 'CANCELED'): break
        time.sleep(6)
    print(name, d['status'], d.get('task_error'), flush=True)
    if d['status'] == 'SUCCEEDED': urllib.request.urlretrieve(d['model_urls']['glb'], 'models/%s.glb' % name)
th = [threading.Thread(target=run, args=a) for a in (('hanglantern', '01a1b00d-f7c9-75de-a00b-4eea06f28213', 500), ('floatlantern', '01a1b00d-f03b-7016-bb39-319968b14615', 700))]
[t.start() for t in th]; [t.join() for t in th]
