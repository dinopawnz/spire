"""python3 gen.py out.png "prompt"  -> Meshy text-to-image (nano-banana-pro), waits, downloads"""
import json, sys, time, urllib.request
KEY = open('/home/claude/.meshy_key').read().strip()
def call(url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=60))
out, prompt = sys.argv[1], sys.argv[2]
tid = call('https://api.meshy.ai/openapi/v1/text-to-image', dict(ai_model='nano-banana-pro', aspect_ratio=sys.argv[3] if len(sys.argv) > 3 else '1:1', prompt=prompt))['result']
for _ in range(100):
    d = call('https://api.meshy.ai/openapi/v1/text-to-image/' + tid)
    if d['status'] in ('SUCCEEDED', 'FAILED', 'CANCELED'): break
    time.sleep(5)
print(out, d['status'], d.get('consumed_credits'), d.get('task_error'))
if d['status'] == 'SUCCEEDED': urllib.request.urlretrieve(d['image_urls'][0], out)
