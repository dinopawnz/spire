"""Copy every file the built spire.html actually uses (that is new or changed) into the GitHub repo clone, then commit and push.
No manual uploading needed.

Usage (after `python3 build_html.py <ver>`):
    python3 sync_to_repo.py "v15: what changed"            # copy + commit + push to main (goes LIVE)
    python3 sync_to_repo.py "wip" --branch my-test-branch  # push to a side branch instead (safe, not live)
    python3 sync_to_repo.py --dry                          # just list what would be copied

How it works:
  1. runs viewer/refcheck2.js on out/spire.html in a fake browser; it writes /tmp/refs.json = every model/sound the page loads
  2. adds the pictures loaded by m-image (bio_*.png, water_fall.png) which refcheck2 does not see
  3. finds each file in out/, out/glb/, out/snd/ or upload/, compares it with the repo copy, copies only the new/changed ones
  4. copies out/spire.html + out/spire_remote.html, then git add / commit / push
Paths: workspace /home/claude/spire, repo clone /home/claude/spire_repo, viewer /home/claude/viewer (edit below if different).
GitHub's limit is 100 MB per file - keep every GLB under that (shrink_glb.py re-encodes textures smaller).
"""
import json, os, sys, shutil, filecmp, subprocess, glob

SP, REPO, VIEW = '/home/claude/spire', '/home/claude/spire_repo', '/home/claude/viewer'
BASE = 'https://raw.githubusercontent.com/dinopawnz/spire/main/'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
dry = '--dry' in sys.argv
branch = sys.argv[sys.argv.index('--branch') + 1] if '--branch' in sys.argv else None
if branch and branch in args: args.remove(branch)
msg = args[0] if args else 'update build'

# refcheck2 runs in headless Chrome (chrometest.py), since jsdom may not be installable; works for pages built against any branch
subprocess.run(['python3', VIEW + '/chrometest.py', VIEW + '/refcheck2.js', SP + '/out/spire.html', SP + '/out'], check=True, timeout=600, stdout=subprocess.DEVNULL)
import re
refs = [re.sub(r'^https://raw\.githubusercontent\.com/dinopawnz/spire/[^/]+/', '', r) for r in json.load(open('/tmp/refs.json')) if '/dinopawnz/spire/' in r]
refs = [r.split('?')[0] for r in refs]
refs += [os.path.basename(p) for p in glob.glob(SP + '/out/snd/band_*.mp3') + glob.glob(SP + '/out/snd/swamp_jazz_*.mp3') + glob.glob(SP + '/out/snd/radio_*.mp3') + glob.glob(SP + '/out/snd/frog_*.mp3') + glob.glob(SP + '/out/snd/piano_*.mp3') + glob.glob(SP + '/out/snd/harp_*.mp3')] + ['citadel_fx_keyglow.glb', 'citadel_fx_string.glb']       # stage band sounds (played on click, not in the DOM)
refs += [os.path.relpath(p, SP + '/out/bio') for p in glob.glob(SP + '/out/bio/*.png')] + ['water_fall.png', 'water_fall2.png', 'fall_glow.png', 'foam.png', 'fire_flame.png', 'fire_glow.png', 'fire_teal.png', 'sky_moon.png', 'sky_moonglow.png']

todo = {}
for f in sorted(set(refs)):
    for src in (SP + '/out/' + f, SP + '/out/glb/' + f, SP + '/out/snd/' + f, SP + '/out/bio/' + f, SP + '/upload/' + f):
        if os.path.isfile(src):
            if not os.path.exists(REPO + '/' + f) or not filecmp.cmp(src, REPO + '/' + f, shallow=False): todo[f] = src
            break
    else:
        if not os.path.exists(REPO + '/' + f): print('!! no built file for', f)
for f in ('spire.html', 'spire_remote.html'): todo[f] = SP + '/out/' + f
big = [f for f, s in todo.items() if os.path.getsize(s) > 95e6]
if big: sys.exit('!! over GitHub 100 MB limit: %s' % big)
print(len(todo), 'files to send:', ', '.join(todo))
if dry: sys.exit(0)

git = lambda *a: subprocess.run(['git', '-C', REPO] + list(a), check=True)
if branch: git('checkout', '-B', branch)
for f, s in todo.items():
    os.makedirs(os.path.dirname(REPO + '/' + f) or REPO, exist_ok=True); shutil.copy2(s, REPO + '/' + f)
git('add', '-A'); git('commit', '-m', msg); git('push', '-u', 'origin', branch or 'main')
print('pushed. Files go live at', BASE.replace('/main/', '/' + (branch or 'main') + '/'), '(GitHub caches ~5 min; bump the version number in build_html.py to bust caches)')
