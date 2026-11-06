"""Swamp folk: every line they speak, as (1) a speech-bubble GLB  sb_<npc>_<key>.glb  and (2) a voice file vo_<npc>_<key>.mp3
(ElevenLabs, made by voices.py once the key is in). out/npc.json carries durations + bubble aspect for the MML.
Line keys: greet = said once a minute when you walk up; t1..tn = click to talk (cycles); anything else = triggered by a game."""
import os, json, math, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from glb import *

OUT = '/home/claude/spire/out/glb/'
TMP = '/home/claude/spire/out/sprite_png/'
INTERB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'

NPC = {
  'ferryman': dict(name='Ferryman Moss', voice='old man, slow, raspy southern drawl', lines=dict(
    greet="Evenin', traveler. Welcome to the Mudwater Spire. Sign the book inside the doors, the lounge is straight ahead, and the games are upstairs. Mind the gators.",
    t1="Two brass lifts wait in the back corners of the lounge, and there's a stair tower at each end. Ride up, climb up, just don't fall in.",
    t2="Upstairs is the Hall of Fakes. Four hundred portraits, one true card. Find it first and you're a finalist.",
    t3="Above that, Mud Royale: teams fightin' over a giant board. Then the Mudroom Escape, room after room of puzzles. And the roof... well. Go see the roof.",
    t4="First thing inside, right in the middle of the entrance: the Mudwater Sign-Up Book. Sign it, so the swamp knows your name.")),
  'barkeep': dict(name='Mama Silt', voice='warm, husky middle-aged southern woman, playful', lines=dict(
    greet="Well, look what the tide dragged in! Pull up a stool, sugar. First round's on the swamp.",
    t1="Pull any tap on the bar and I'll slide one down to you. Don't you drop it.",
    t2="Them portraits upstairs? Half the forgers in the bayou painted 'em. Check the little things, darlin'. The little things.",
    t3="Old Skipper up on the roof deck swears he sailed with the Drowned Captain. Ask him, if you've got an hour.",
    t4="The jukebox takes no coins tonight. Give it a tap and it'll change its tune.",
    t5="Hear that fire cracklin'? It's for warmin' hands, not roastin' marshmallows. Gator Pete learned that the hard way.",
    t6="This spire's been standin' on these stilts longer than the cypress been growin'. Creaks a bit. So do I.",
    t7="You win somethin' up there tonight, you come back and tell Mama all about it.",
    pour0="Here she comes!", pour1="Catch!", pour2="One swamp ale, extra mud.", pour3="Comin' down the bar!")),
  'skipper': dict(name='Old Skipper', voice='gruff old sea captain, storyteller, deep', lines=dict(
    greet="Ahoy there. Best view in the swamp, this roof. Mind the edge.",
    t1="Forty years I poled these waters. Saw the Drowned Captain's lantern once. Still see it when I close my eyes.",
    t2="On a clear night you can see the whole bayou from up here. On a stormy night... you see things you shouldn't.",
    t3="That steeple behind me? Built from the mast of the Drowned Captain's ship. Or so the barkeep tells it.",
    t4="Win somethin' tonight and they'll sing about you down at the lounge for a year.",
    t5="Rule one of the bayou: never trust a smilin' gator. Rule two: never trust a portrait that smiles back.")),
  'gator': dict(name='Gator Pete', voice='big friendly deep-voiced man, slow and goofy', lines=dict(
    greet="Heh. Warm yourself by the fire, friend. Plenty of room. I only bite on Tuesdays.",
    t1="I went up the Hall of Fakes once. Picked the wrong picture, had to wait five whole seconds. Felt like five years.",
    t2="Thing about forgeries: the painter always gets bored on the details. Numbers. Colours. Dates. Look close.",
    t3="Only four get into the big glass hall in the middle. Everybody else presses their snouts on the glass. I fogged it up good.",
    t4="Card tables are free. I'm not allowed to play anymore. Long story. Involves a tail.",
    t5="Ever seen the swamp from the roof deck? Prettiest thing in the whole bayou.")),
  'appraiser': dict(name='The Appraiser', voice='precise, refined older British man, theatrical whisper', lines=dict(
    greet="Welcome to the Hall of Fakes. Three hundred and ninety-nine forgeries. One original. Climb, look, and choose wisely.",
    t1="A wrong choice costs you five seconds. Patience is the cheapest tool an appraiser owns.",
    t2="Four rounds. Each round, the first to find the original is summoned to the glass finals hall in the middle of this room.",
    t3="Don't trust the frame. Trust the details. The numbers, the year, the colours of the smallest things.",
    t4="Two rows of portraits, all the way up the ramp. The answer may be at the bottom... or at the very top.",
    open="The hunt begins! Find the true Founder!", thin="The forgers lose their nerve. Fewer fakes remain.",
    finals="The glass is clear. Finalists, find the true Black Flag!", won="We have a champion! The true Black Flag is found!",
    round="A finalist! Off to the glass hall with you. Everyone else, the portraits are being shuffled.", next="A new round! Every portrait has moved. Find the Founder again!")),
  'operator': dict(name='The Lift Boss', voice='bright, brassy old-time lift attendant, southern lilt, quick and cheerful', lines=dict(
    greet="Step lively, folks, and mind the gate! The Lift Boss, at your service.",
    t1="This here's the Grand Cage. Solid brass, swamp glass, and the smoothest ride in the bayou. Push your floor on the panel, lounge at the bottom, roof at the top.",
    t2="Lounge, Hall of Fakes, Mud Royale, the Mudroom Escape, and the roof deck. Name it and I'll haul it.",
    t3="Hold the rail, sugar. Watch the floors go by through the glass.",
    t4="Two cages, one in each back corner. If mine's full, my cousin across the way will haul you.",
    up="Goin' up!", down="Goin' down!", close="Mind the gate!",
    s_lounge="Ground floor! The Lounge. Taps are flowin'.",
    s_hall="The Hall of Fakes! Look close, now.",
    s_gallery="The Gallery! Top of the Hall of Fakes ramp.",
    s_rooms="The Mudroom Escape! Pick your team's door.",
    s_cards="Mud Royale! Pick a team and grab some squares.",
    s_roof="Top of the house! The roof deck. Mind the edge, y'all.")),
  'dealer': dict(name='The Dealer', voice='smooth, sly, fast-talking riverboat card dealer, playful', lines=dict(
    greet="Step right up, friend. Pull up a chair, and let the swamp deal you in.",
    t1="This floor's for Mud Royale. Join a team, take a hand of Mudwater cards, and capture squares on the giant board.",
    t2="Two minutes on the clock. When it runs out, the team holdin' the most squares takes the whole board.",
    t3="Play your cards by the Mudwater rules and you'll steal squares right out from under the other teams.",
    t4="Upgrades, captures, rocks. It's all in the rules boards. Read 'em twice.",
    final="Ladies and gators, the teams are set! Two minutes on the clock. Capture all you can!",
    won="Time! The team with the most squares takes Mud Royale!")),
}

def bubble(name, text, key):
    W = 1200; pad = 56
    fb = ImageFont.truetype(INTERB, 46); fh = ImageFont.truetype(LORA, 54)
    try: fh.set_variation_by_name('Bold')
    except Exception: pass
    lines = textwrap.wrap(text, 40)
    lh = 60; H = pad * 2 + 70 + lh * len(lines) + 40
    img = Image.new('RGBA', (W, H + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    # drop glow, parchment body, tail
    sh = Image.new('L', img.size, 0); ds = ImageDraw.Draw(sh); ds.rounded_rectangle((14, 14, W - 14, H - 6), 48, fill=200)
    ds.polygon([(W * 0.42, H - 10), (W * 0.5, H + 52), (W * 0.56, H - 10)], fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(10)); img.putalpha(sh)
    img = Image.composite(Image.new('RGBA', img.size, (20, 12, 4, 255)), img, sh.point(lambda v: 0)); img.putalpha(sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((22, 22, W - 22, H - 18), 40, fill=(246, 232, 196, 255), outline=(120, 82, 34, 255), width=8)
    d.polygon([(W * 0.43, H - 24), (W * 0.5, H + 44), (W * 0.55, H - 24)], fill=(246, 232, 196, 255))
    d.line([(W * 0.43, H - 20), (W * 0.5, H + 44), (W * 0.55, H - 20)], fill=(120, 82, 34, 255), width=8)
    # paper grain
    rng = np.random.default_rng(len(text)); a = np.asarray(img).astype(float)
    n = rng.normal(0, 6, a.shape[:2]); a[..., :3] += n[..., None] * (a[..., 3:4] > 250)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    d.text((pad, pad - 6), name.upper(), font=fh, fill=(28, 110, 96))
    d.line([(pad, pad + 66), (W - pad, pad + 66)], fill=(180, 140, 80), width=3)
    for i, t in enumerate(lines): d.text((pad, pad + 86 + i * lh), t, font=fb, fill=(52, 30, 12))
    p = TMP + 'sb_' + key + '.png'; img.save(p)
    asp = img.size[0] / img.size[1]
    m = Mesh(); quad(m, 'txt', asp, 1.0, T(0, 0, 0), double=True)
    write(OUT + 'sb_' + key + '.glb', m, {'txt': dict(tex=p, alpha='BLEND', double=True, unlit=True)})
    return round(asp, 3)

def note_sprite():
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 220)
    img = Image.new('RGBA', (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.text((40, 10), '♫', font=f, fill=(255, 210, 110, 255))
    g = img.filter(ImageFilter.GaussianBlur(10)); out = Image.alpha_composite(g, img)
    p = TMP + 'ms_note.png'; out.save(p)
    m = Mesh(); quad(m, 'txt', 1.0, 1.0, T(0, 0, 0), double=True)
    write(OUT + 'ms_note.glb', m, {'txt': dict(tex=p, emis_tex=p, emis=(1, 1, 1), alpha='BLEND', double=True, unlit=True)})

if __name__ == '__main__':
    meta = {}
    durs = json.load(open('out/vo_durations.json')) if os.path.exists('out/vo_durations.json') else {}
    for k, n in NPC.items():
        meta[k] = {'name': n['name'], 'lines': {}}
        for lk, text in n['lines'].items():
            key = k + '_' + lk
            asp = bubble(n['name'], text, key)
            dur = durs.get(key) or round(0.9 + len(text.split()) * 0.36, 2)
            meta[k]['lines'][lk] = [asp, round(dur, 2)]
    note_sprite()
    json.dump(meta, open('out/npc.json', 'w'), indent=0)
    print(sum(len(v['lines']) for v in meta.values()), 'lines')
