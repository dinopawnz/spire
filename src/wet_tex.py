"""The lounge floor from the owner's concept: dark swamp planks, wet and glossy, mud packed in the gaps and smeared across the boards,
darker soaked patches. Writes tex/wetfloor.jpg (colour), tex/wetfloor_n.jpg (bumps) and tex/wetfloor_mr.png (G = roughness: wet = shiny).
Seamless (all noise is made in the frequency domain, from textures.py)."""
import numpy as np
from PIL import Image, ImageFilter
from textures import fbm, norm01, colorize, normal_map, to_img, OUT

def wetfloor(n=2048, rows=6, seed=31):
    grain = fbm(n, 9, 5, aniso=20, seed=seed)
    rings = np.sin(grain * 9 + fbm(n, 60, 3, aniso=8, seed=seed + 9) * 6)
    big = fbm(n, 160, 3, seed=seed + 20)
    y = np.arange(n)[:, None] * np.ones((1, n)); x = np.ones((n, 1)) * np.arange(n)[None, :]
    bh = n / rows; row = (y // bh).astype(int)
    r = np.random.default_rng(seed)
    tint = r.uniform(-0.15, 0.15, rows); joint = r.uniform(0, n, rows)
    t = 0.48 + 0.16 * grain + 0.1 * rings + 0.1 * big + tint[row]
    edge = np.minimum(y % bh, bh - (y % bh))
    gap = np.clip((edge - 3) / 7.0, 0, 1)
    jd = np.abs(((x - joint[row]) + n / 2) % n - n / 2)
    gap = np.minimum(gap, np.clip((jd - 3) / 6.0, 0, 1))
    wearedge = np.clip(1 - np.minimum(edge, jd) / 26.0, 0, 1) * gap          # worn, slightly paler board edges
    wood = colorize(t, [(0, (18, 11, 6)), (0.4, (46, 29, 16)), (0.7, (72, 46, 26)), (1, (98, 66, 38))])
    # mud: packed into every gap, plus smears across the boards
    smear = norm01(fbm(n, 110, 5, aniso=1.6, seed=seed + 40))
    smear = np.clip((smear - 0.6) / 0.22, 0, 1) ** 1.5 * np.clip(0.6 + 0.8 * norm01(fbm(n, 6, 3, seed=seed + 41)), 0, 1)
    gapmud = np.clip(1 - gap, 0, 1)
    gapmud = np.array(Image.fromarray((gapmud * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5))).astype(float) / 255
    mud = np.clip(np.maximum(smear * 0.85, gapmud), 0, 1)
    mudv = norm01(fbm(n, 14, 4, seed=seed + 60))
    mudcol = colorize(mudv, [(0, (34, 25, 15)), (0.5, (58, 43, 26)), (1, (78, 60, 38))])
    wood = wood * (1 + 0.35 * wearedge[..., None])
    rgb = wood * (1 - smear[..., None] * 0.85) + mudcol * (smear[..., None] * 0.85)
    seam = np.array([0.07, 0.05, 0.03])                                      # black mud packed in the seams
    rgb = rgb * gap[..., None] + seam * (1 - gap[..., None])
    # soaked patches: darker, richer
    wet = norm01(fbm(n, 140, 4, seed=seed + 80))
    wet = np.clip((wet - 0.35) / 0.4, 0, 1)
    rgb = rgb * (1 - 0.32 * wet[..., None])
    # roughness: soaked = mirror-like, damp wood = satin, dry mud ridges = matte
    rough = 0.32 - 0.24 * wet + 0.25 * mud * (1 - wet) + 0.06 * (1 - gap)
    rough = np.clip(rough, 0.05, 0.75)
    mr = np.dstack([np.ones_like(rough), rough, np.zeros_like(rough)])
    # bumps: grain and gaps, softened under the mud and where water lies
    h = (0.35 * grain + 0.25 * rings) * (1 - 0.7 * mud) * (1 - 0.5 * wet) - 2.2 * (1 - gap) * (1 - 0.6 * gapmud) + 0.6 * smear * (1 - wet)
    to_img(rgb).save(OUT + '/wetfloor.jpg', quality=90)
    normal_map(h, 1.6).save(OUT + '/wetfloor_n.jpg', quality=90)
    to_img(mr).save(OUT + '/wetfloor_mr.png', optimize=True)
    to_img(rgb).resize((768, 768)).save('/home/claude/shots/wetfloor_preview.jpg', quality=88)

if __name__ == '__main__':
    wetfloor()
    print('wetfloor done')
