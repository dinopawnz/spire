"""Pool table extras: sounds (ball clacks, cue strike, cushion thump, pocket drop) synthesised from short filtered transients,
and the rail button / how-to-play plaques as images (text baked into the picture: text elements cost frame rate).
-> out/snd/pool_*.mp3, out/pool_*.png"""
import os, subprocess, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SR = 44100; SND = '/home/claude/spire/out/snd/'; IMG = '/home/claude/spire/out/'
rng = np.random.default_rng(11)

def save(name, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    tmp = '/tmp/claude-0/-home-claude/5ddaad6a-f847-5413-a277-78b451d1faa9/scratchpad/' + name + '.wav'
    with wave.open(tmp, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-ac', '1', '-b:a', '96k', SND + name + '.mp3'], check=True)

def room(x, wet=0.12):
    out = x.copy()
    for d, g in ((0.011, 0.5), (0.019, 0.4), (0.031, 0.3), (0.047, 0.2), (0.071, 0.12)):
        k = int(d * SR); out[k:] += x[:-k] * g * wet * 3
    return out

def clack(f0):
    """two hard resin balls: a very short bright click with a couple of ringing partials"""
    n = int(0.25 * SR); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f0 * m * t + rng.uniform(0, 6)) * np.exp(-t * d) for (m, a, d) in ((1, 1.0, 60), (2.31, 0.6, 90), (3.7, 0.35, 130)))
    nz = rng.standard_normal(n); x += 0.8 * (nz - np.convolve(nz, np.ones(3) / 3, 'same')) * np.exp(-t * 900)
    return room(x * np.minimum(1, t / 0.0004))

def thump(f0=110, dur=0.3, nzg=0.4, dec=18):
    n = int(dur * SR); t = np.arange(n) / SR; fr = f0 * (1 + 0.4 * np.exp(-t * 40))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * dec) + nzg * np.convolve(rng.standard_normal(n), np.ones(12) / 12, 'same') * np.exp(-t * 70)
    return room(x)

def drop():
    """the ball falls into the leather pocket, a soft knock and a roll"""
    x = thump(160, 0.6, 0.6, 9)
    n = len(x); t = np.arange(n) / SR
    roll = np.convolve(rng.standard_normal(n), np.ones(30) / 30, 'same') * (t > 0.12) * np.exp(-(t - 0.12).clip(0) * 6) * 0.6
    return x + roll

if __name__ == '__main__':
    os.makedirs(SND, exist_ok=True)
    for k, f0 in enumerate((2900, 3300, 3700)): save('pool_clack_%d' % k, clack(f0))
    save('pool_cue', clack(1800) * 0.6 + thump(220, 0.2, 0.3, 30))
    save('pool_rail', thump(95, 0.35, 0.5, 16))
    save('pool_pocket', drop())
    # plaques: dark carved wood with a gold border and gold lettering
    F = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
    wood = Image.open('/home/claude/meshy/wood_dark.png').convert('RGB') if os.path.exists('/home/claude/meshy/wood_dark.png') else None
    def plaque(name, lines, W=360, H=150, size=58, arrow=None):
        im = (wood.resize((W * 2, W * 2)).crop((0, 0, W, H)) if wood else Image.new('RGB', (W, H), '#3a2416'))
        im = Image.blend(im, Image.new('RGB', (W, H), '#1c120b'), 0.45); d = ImageDraw.Draw(im)
        d.rounded_rectangle([5, 5, W - 6, H - 6], 14, outline='#d6a842', width=5)
        f = ImageFont.truetype(F, size)
        if arrow:
            cx, cy = W / 2, H / 2; s = H * 0.28; sg = -1 if arrow == 'L' else 1
            d.polygon([(cx + sg * s, cy), (cx - sg * s * 0.7, cy - s), (cx - sg * s * 0.7, cy + s)], fill='#f0c454')
        else:
            tot = len(lines) * size * 1.15; y = H / 2 - tot / 2
            for ln in lines:
                w = d.textlength(ln, font=f); d.text((W / 2 - w / 2, y), ln, font=f, fill='#f0c454'); y += size * 1.15
        im.save(IMG + name + '.png')
    plaque('pool_btn_soft', ['SOFT']); plaque('pool_btn_med', ['MEDIUM'], size=50); plaque('pool_btn_hard', ['HARD'])
    plaque('pool_btn_l', [], W=150, arrow='L'); plaque('pool_btn_r', [], W=150, arrow='R')
    plaque('pool_btn_rack', ['NEW RACK'], W=420, size=54)
    plaque('pool_howto', ['HOW TO PLAY POOL', '1  Click the glowing ring', '    on your side of the white ball', '2  Nudge the aim with  <  >',
                          '3  Press SOFT, MEDIUM or HARD', '    to take the shot'], W=820, H=430, size=44)
    print('pool sounds + plaques written')
