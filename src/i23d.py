"""python3 i23d.py ref.png out.glb [polycount]  -> Meshy image-to-3D (textured, PBR), waits, downloads the GLB"""
import json, sys, time, base64, urllib.request
KEY = open('/home/claude/.meshy_key').read().strip()
def call(url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=120))
ref, out = sys.argv[1], sys.argv[2]; poly = int(sys.argv[3]) if len(sys.argv) > 3 else 30000
uri = 'data:image/png;base64,' + base64.b64encode(open(ref, 'rb').read()).decode()
body = dict(image_url=uri, ai_model='latest', should_texture=True, enable_pbr=True, should_remesh=True, topology='triangle', target_polycount=poly)
tid = call('https://api.meshy.ai/openapi/v1/image-to-3d', body)['result']
print(out, 'task', tid, flush=True)
t0 = time.time()
while True:
    d = call('https://api.meshy.ai/openapi/v1/image-to-3d/' + tid)
    if d['status'] in ('SUCCEEDED', 'FAILED', 'CANCELED') or time.time() - t0 > 1500: break
    time.sleep(10)
print(out, d['status'], d.get('progress'), 'credits', d.get('consumed_credits'), d.get('task_error'), flush=True)
if d['status'] == 'SUCCEEDED':
    urllib.request.urlretrieve(d['model_urls']['glb'], out)
    json.dump({k: v for k, v in d.items() if k not in ('model_urls', 'texture_urls', 'thumbnail_url')}, open(out + '.json', 'w'))
