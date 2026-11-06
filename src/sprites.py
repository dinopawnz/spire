"""Text as images (the arena never uses m-label for fixed words: text lags, images don't).
 ms_<key>.glb : floating glowing words, a two-sided quad 1 m tall (scale it in MML), width = aspect.
 sg_<key>.glb : a painted wooden signboard (carved frame, brass corners) with the words burned in.
Also the swamp-gold digit set ms_d0..ms_d9 and ms_slash for counters."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from glb import *
from kit import MATS, TEX, tint

OUT = '/home/claude/spire/out/glb/'
TMP = '/home/claude/spire/out/sprite_png/'
os.makedirs(TMP, exist_ok=True)
INTER = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
INTERB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'

def font(path, size, bold=True):
    f = ImageFont.truetype(path, size)
    if 'Lora' in path:
        try: f.set_variation_by_name('Bold')
        except Exception: pass
    return f

PAL = {'gold': ((255, 226, 140), (214, 150, 40)), 'red': ((255, 120, 100), (200, 30, 30)), 'teal': ((150, 255, 236), (30, 190, 170)),
       'cream': ((255, 248, 225), (220, 200, 160)), 'green': ((190, 255, 150), (60, 190, 60)),
       'blue': ((170, 210, 255), (40, 110, 230)), 'purple': ((225, 190, 255), (150, 80, 220)), 'orange': ((255, 205, 150), (240, 120, 30))}

def glow_text(lines, color='gold', size=150, face=INTER, pad=60, line_gap=0.18):
    f = font(face, size)
    ws = [f.getbbox(t) for t in lines]
    W = max(b[2] - b[0] for b in ws) + 2 * pad
    lh = int(size * (1 + line_gap)); H = lh * len(lines) + 2 * pad
    mask = Image.new('L', (W, H), 0); d = ImageDraw.Draw(mask)
    for i, t in enumerate(lines):
        b = f.getbbox(t); x = (W - (b[2] - b[0])) // 2 - b[0]; y = pad + i * lh - b[1] + (lh - size) // 2
        d.text((x, y), t, font=f, fill=255)
    top, bot = PAL[color]
    grad = np.zeros((H, W, 3))
    for c in range(3): grad[..., c] = np.linspace(top[c], bot[c], H)[:, None]
    m = np.asarray(mask).astype(float) / 255
    outline = np.asarray(mask.filter(ImageFilter.MaxFilter(13))).astype(float) / 255
    glow = np.asarray(mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(18))).astype(float) / 255
    rgb = grad * m[..., None] + np.array([30, 14, 4]) * (1 - m[..., None])
    glowc = np.array(bot) * 0.9
    a = np.maximum(m, outline * 0.95)
    rgb = np.where((outline > m)[..., None], np.array([28, 14, 6]), rgb)
    a2 = np.maximum(a, glow * 0.55)
    rgb = np.where((a2 > a)[..., None], glowc, rgb)
    img = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a2 * 255]).astype(np.uint8), 'RGBA')
    return img

def sprite1(key):
    """one-sided copy (ms1_<key>.glb) for signs hung back to back - the far side no longer shows through mirrored"""
    p = TMP + 'ms_' + key + '.png'; w, h = Image.open(p).size; asp = w / h
    m = Mesh(); quad(m, 'txt', asp, 1.0, T(0, 0, 0))
    write(OUT + 'ms1_' + key + '.glb', m, {'txt': dict(tex=p, emis_tex=p, emis=(1, 1, 1), alpha='BLEND', unlit=True)})

def sprite(key, lines, color='gold', size=150, face=INTER):
    img = glow_text(lines if isinstance(lines, list) else [lines], color, size, face)
    # power-of-two-friendly: cap width at 2048
    if img.size[0] > 2048: img = img.resize((2048, int(img.size[1] * 2048 / img.size[0])), Image.LANCZOS)
    p = TMP + 'ms_' + key + '.png'; img.save(p)
    w, h = img.size; asp = w / h
    m = Mesh(); quad(m, 'txt', asp, 1.0, T(0, 0, 0), double=True)
    write(OUT + 'ms_' + key + '.glb', m, {'txt': dict(tex=p, emis_tex=p, emis=(1, 1, 1), alpha='BLEND', double=True, unlit=True)})
    return asp

def signboard(key, title, body, w=4.0, h=None, title_size=120, body_size=64, ink=(46, 26, 10), board=(196, 160, 110), sub=None):
    """painted wooden board with burned-in text; returns aspect"""
    PX = 512 / 2.0                                    # pixels per metre
    ft = font(LORA, title_size); fb = font(INTERB, body_size)
    # wrap body to width
    maxw = int(w * PX * 2) - 120
    def wrap(t, f):
        out = []
        for para in t.split('\n'):
            cur = ''
            for wd in para.split(' '):
                nx = (cur + ' ' + wd).strip()
                if f.getlength(nx) > maxw and cur: out.append(cur); cur = wd
                else: cur = nx
            out.append(cur)
        return out
    blines = wrap(body, fb) if body else []
    th = int(title_size * 1.3) if title else 0
    Hpx = 80 + th + len(blines) * int(body_size * 1.32) + 70
    Wpx = int(w * PX * 2)
    if h: Hpx = max(Hpx, int(h * PX * 2))
    # wood background from the pale plank texture, tinted
    wood = Image.open(TEX + 'wood_pale.jpg').convert('RGB').resize((Wpx, Wpx)).crop((0, 0, Wpx, Hpx))
    wood = Image.blend(wood, Image.new('RGB', wood.size, board), 0.35)
    d = ImageDraw.Draw(wood)
    y = 50
    if title:
        x = (Wpx - ft.getlength(title)) / 2
        d.text((x + 3, y + 3), title, font=ft, fill=(250, 220, 150))
        d.text((x, y), title, font=ft, fill=(120, 40, 12)); y += th
        d.line([(Wpx * 0.2, y - 8), (Wpx * 0.8, y - 8)], fill=ink, width=5)
    for t in blines:
        x = (Wpx - fb.getlength(t)) / 2
        d.text((x, y), t, font=fb, fill=ink); y += int(body_size * 1.32)
    # burned edges
    a = np.asarray(wood).astype(float)
    yy, xx = np.mgrid[0:Hpx, 0:Wpx]
    e = np.minimum.reduce([xx, yy, Wpx - xx, Hpx - yy]).astype(float)
    a *= (0.55 + 0.45 * np.clip(e / 40, 0, 1))[..., None]
    wood = Image.fromarray(a.astype(np.uint8))
    p = TMP + 'sg_' + key + '.jpg'; wood.save(p, quality=88)
    W_ = w; H_ = w * Hpx / Wpx
    m = Mesh(); rng = random.Random(len(key))
    quad(m, 'paint', W_, H_, T(0, 0, 0.051))
    box(m, 'dark', W_ + 0.02, H_ + 0.02, 0.1, m=T(0, 0, 0))
    for s in (-1, 1):
        bevel_box(m, 'dark', 0.12, H_ + 0.3, 0.16, 0.03, m=T(s * (W_ / 2 + 0.06), 0, 0.02))
    for s in (-1, 1):
        bevel_box(m, 'dark', W_ + 0.36, 0.12, 0.16, 0.03, m=T(0, s * (H_ / 2 + 0.06), 0.02))
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(m, 'brass', 0.18, 0.18, 0.04, m=T(sx * (W_ / 2 + 0.06), sy * (H_ / 2 + 0.06), 0.11))
    mats = dict(MATS); mats['paint'] = dict(tex=p, emis_tex=p, emis=(0.35, 0.3, 0.25), rough=0.85)
    write(OUT + 'sg_' + key + '.glb', m, mats)
    return W_, H_

SPRITES = {
    # Hall of Fakes
    'forgery': (['FORGERY!'], 'red'), 'wait': (['WAIT'], 'red'), 'secs': (['SECONDS'], 'cream'),
    'found': (['YOU FOUND', 'THE REAL ONE!'], 'gold'), 'finalist': (['YOU\'RE IN THE FINALS!', 'GO UP TO THE VAULT'], 'gold'),
    'vaultfull': (['THE VAULT IS FULL'], 'teal'), 'notyet': (['THE HUNT HASN\'T', 'STARTED YET'], 'cream'),
    'roundover': (['THIS ROUND', 'IS OVER'], 'cream'), 'already': (['YOU\'RE ALREADY', 'IN THE FINALS'], 'teal'),
    'finalsonly': (['ONLY THE FINALISTS', 'PICK IN HERE'], 'cream'), 'winner': (['WINNER!'], 'gold'),
    'findflag': (['FIND THE REAL', 'BLACK FLAG'], 'red'), 'findfounder': (['FIND THE REAL', 'FOUNDER'], 'teal'),
    'finalists': (['FINALISTS'], 'gold'), 'remain': (['PORTRAITS LEFT'], 'cream'), 'slash': (['/'], 'gold'),
    'thinned': (['THE FORGERS FLED!', 'FEWER PORTRAITS NOW'], 'teal'), 'finalsgo': (['THE FINALS', 'HAVE BEGUN'], 'gold'),
    'gone': (['THAT ONE WAS', 'TAKEN DOWN'], 'cream'), 'vaultwait': (['THE VAULT OPENS', 'FOR FINALISTS'], 'cream'),
    'champion': (['CHAMPION OF', 'THE HALL OF FAKES'], 'gold'),
    'shuffling': (['FINALIST FOUND!', 'SHUFFLING THE HALL'], 'gold'), 'allfound': (['ALL 4 FINALISTS', 'ARE FOUND'], 'gold'),
    'nextin': (['NEXT ROUND IN'], 'cream'), 'getready': (['GET READY FOR', 'THE NEXT ROUND'], 'teal'),
    # elevators
    'going_up': (['GOING UP'], 'gold'), 'going_down': (['GOING DOWN'], 'gold'),
    'lift_here': (['THE CAGE', 'IS HERE'], 'teal'), 'lift_coming': (['CAGE', 'ON ITS WAY'], 'cream'), 'lift_full': (['CAGE FULL', 'NEXT ONE!'], 'red'),
    'lift_express': (['EXPRESS'], 'red'), 'lift_finalists': (['FINALISTS ONLY', 'TO THE VAULT'], 'teal'),
    'fl_lounge': (['THE LOUNGE'], 'gold'), 'fl_hall': (['HALL OF FAKES'], 'gold'), 'fl_gallery': (['THE GALLERY'], 'gold'),
    'fl_cards': (['MUD ROYALE'], 'gold'), 'fl_deck': (["CAPTAIN'S DECK"], 'gold'),
    'fl_rooms': (['MUDWATER ESCAPE'], 'gold'), 'fl_roof': (['ROOF DECK'], 'gold'), 'stairs': (['STAIRS'], 'gold'),
    'realone': (['THE REAL ONE'], 'gold'),
    'signup': (['MUDWATER', 'SIGN-UP BOOK'], 'gold'), 'signup_sub': (['SIGN YOUR NAME HERE'], 'cream'),
    'bt_cardshop': (['CARD SHOP'], 'gold'), 'bt_merch': (['MUDWATER MERCH'], 'gold'), 'bt_trophies': (['TROPHY ROOM'], 'gold'), 'bt_photos': (['PHOTO BOOTH'], 'gold'),
}
# MUD ROYALE (v34)
SPRITES.update({
    'rt_0': (['GATORS'], 'green'), 'rt_1': (['CRAWDADS'], 'red'), 'rt_2': (['BULLFROGS'], 'gold'), 'rt_3': (['CATFISH'], 'teal'),
    'royale': (['MUD ROYALE'], 'gold'), 'r_hand': (['YOUR HAND'], 'cream'), 'r_join': (['STAND HERE', 'TO JOIN'], 'cream'),
    'r_players': (['PLAYERS'], 'cream'), 'r_squares': (['SQUARES'], 'cream'), 'r_wins': (['WINS!'], 'gold'), 'r_tie': (["IT'S A TIE!"], 'gold'),
    'r_mvp': (['MVP'], 'gold'), 'r_colon': ([':'], 'gold'), 'r_go': (['GO!', 'PLACE YOUR CARDS'], 'gold'), 'r_out': (['NEW CARD COMING', 'ONE EVERY 10 SECONDS'], 'cream'), 'r_30': (['30 SECONDS LEFT!'], 'red'),
    'r_noteam': (['STAND ON A TEAM PAD', 'BEFORE THE START'], 'cream'), 'r_taken': (['THAT SQUARE', 'IS TAKEN'], 'red'),
    'r_youre': (["YOU'RE ON"], 'cream'), 'r_wait': (['WAIT FOR THE', 'HOST TO START'], 'cream'), 'r_time': (['TIME!'], 'red'),
    'r_pick': (['PICK A TEAM'], 'gold'), 'aw_sign': (['SIGN THE ART WALL', 'AT THE LECTERN'], 'gold'), 'r_full': (['BOARD FULL!', 'UPGRADE CARDS'], 'gold'), 'r_weak': (['NEED A STRONGER', 'CARD TO UPGRADE'], 'red'), 'r_capture': (['CAPTURED!'], 'gold'), 'r_lvup': (['ONLY LEVEL 1 GOES ON AN EMPTY SQUARE', 'CLICK A CARD TWICE TO PLAY IT AS A ROCK'], 'red'), 'r_lvlow': (['UPGRADE = EXACTLY ONE LEVEL HIGHER', "ON YOUR TEAM'S SQUARE"], 'red'), 'r_enemy': (['NOT ON AN ENEMY SQUARE', 'CAPTURE IT INSTEAD'], 'red'), 'r_rock1': (['ONE ROCK AT A TIME', 'COVER YOUR ROCK FIRST'], 'red'), 'r_rockon': (['ROCK'], 'cream'), 'r_tip': (['CLICK A CARD TWICE = PLAY IT FACE DOWN AS A ROCK'], 'cream'), 'r_ready': (['GET READY'], 'teal'),
})
# MUDWATER ESCAPE (v43)
SPRITES.update({
    'e_title': (['MUDWATER ESCAPE'], 'gold'), 'e_red': (['RED'], 'red'), 'e_gold': (['GOLD'], 'gold'), 'e_green': (['GREEN'], 'green'),
    'e_blue': (['BLUE'], 'blue'), 'e_purple': (['PURPLE'], 'purple'), 'e_orange': (['ORANGE'], 'orange'),
})
for k in range(10): SPRITES['d%d' % k] = ([str(k)], 'gold')
for k in range(10): SPRITES['r%d' % k] = ([str(k)], 'red')
for k in range(1, 5): SPRITES['round%d' % k] = (['ROUND %d OF 4' % k], 'teal')

SIGNS = {
    'hall_rules': ('THE HALL OF FAKES', 'Four hundred portraits of The Founder hang along the ramp that climbs round this hall.\nThree hundred and ninety-nine are FORGERIES - an earring, a number, a colour, a letter wrong.\nONE is real - it looks exactly like THE REAL ONE on the pillars.\nClick the real one. Guess wrong and you wait 5 seconds.\nFOUR ROUNDS: the first to find it each round goes to the glass FINALS HALL in the middle.\nThen the portraits are shuffled and the next round begins.', 6.0),
    'vault_rules': ('THE FINALS VAULT', 'Four finalists. A hundred portraits of BLACK FLAG. One is real.\nThe glass unfrosts when the host starts the finals.\nWrong click = 5 seconds out. First to find it wins.', 5.0),
    'gallery': ('THE GALLERY', 'Watch the finals through the glass.', 3.6),
    'royale_rules': ('MUD ROYALE', 'Four teams: Gators, Crawdads, Bullfrogs, Catfish.\nWALK ONTO a team pad to join. You can switch until the host starts.\nAt the start everyone gets 5 Mudwater cards (on the YOUR HAND boards) + a new card every 10 seconds.\nPLACE: Level 1 cards go face up on empty squares. UPGRADE: a card exactly ONE level higher on top of your team\'s square (II on I, III on II...).\nROCK: click a card twice to play it face down on an empty square - it cannot capture or be captured, counts as Level 1; one rock each at a time.\nYour card CAPTURES an enemy card next to it if its number on that side (the big numbers) is higher.\nBoard full? Keep upgrading your squares - upgrades capture too.\nAfter 3 minutes the team holding the most squares wins.', 6.0),
    'lifts': ('THE LIFTS', 'Every floor: Lounge - Hall of Fakes - Gallery - Mud Royale - Mudwater Escape - Roof Deck', 3.6),
    'esc_r1': ('ROOM 1 - THE LANTERN CODE', 'Four coloured lanterns are hidden in this room.\nFind them and CLICK each one to see its number.\nThe PAINTING shows the colours in order.\nType the 4 numbers in that order on the KEYPAD by the door.', 4.4),
    'esc_r2': ('ROOM 2 - THE LILY PADS', 'Stand on the lily pads TOGETHER:\n4 players on 4 pads at the same time\n(fewer if your team is small).\nStay on them for 2 seconds and the door opens.', 4.2),
    'esc_r3': ('ROOM 3 - CARD MEMORY', 'Click the cards on the wall to turn them over.\nFind all 6 matching PAIRS.\nTwo that don\'t match turn back over.', 4.0),
    'esc_r4': ('ROOM 4 - THE FROG CHOIR', 'Watch the frogs light up in order.\nThen CLICK the frogs in the same order.\n3 rounds - each one longer.\nThen run through the last door to the VICTORY HALL!', 4.2),
    'escape_rules': ('MUDWATER ESCAPE', 'Six teams. Walk in through a coloured door to join that team - you can switch until the host starts.\nThen the doors lock. Solve each room to open the door to the next one:\n1. LANTERN CODE - find 4 hidden lanterns, read their numbers in the painting\'s colour order, type the code.\n2. LILY PADS - stand on the lily pads together (4 at once).\n3. CARD MEMORY - find the 6 pairs of Mudwater cards.\n4. FROG CHOIR - copy the frogs\' song, 3 rounds.\nFirst team into the VICTORY HALL wins!', 6.0),
}

if __name__ == '__main__':
    asp = {}
    for k, (lines, color) in SPRITES.items(): asp[k] = round(sprite(k, lines, color), 4); sprite1(k)
    sg = {}
    for k, (t, b, w) in SIGNS.items(): sg[k] = [round(v, 3) for v in signboard(k, t, b, w)]
    import json; json.dump({'ms': asp, 'sg': sg}, open('/home/claude/spire/out/sprites.json', 'w'))
    print(len(asp), 'sprites,', len(sg), 'signs')
