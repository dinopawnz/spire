"""(v31, owner: "interactable pool tables that people can actually play ... somewhere on the first floor in an open space")
Two Meshy pool tables on the open east side of the lounge, a Meshy cue rack and a how-to-play plaque on the east wall.
Writes D['pool'] for spire_src.html (the physics + playing live there): table frames, felt size, pockets, ball radius,
rail buttons, the cue. Called by build_html.py: pool.apply(D, FL)."""
import math
import outside
from outside import place

def apply(D, FL):
    if 'pooltable' not in outside.META: return
    Y = FL['lounge'] + 0.005
    L = 3.4                                                         # table length (m); playing area measured from the model:
    mn, mx = outside.META['pooltable']; s = L / max(mx[0] - mn[0], mx[2] - mn[2])
    felt = round((0.2729 - mn[1]) * s + 0.002, 4)                   #   felt at y 0.2729, cushion noses at |x| 0.84, |z| 0.44 (model units)
    hw, hd = round(0.84 * s, 4), round(0.44 * s, 4)
    e = place('pooltable', 0, 0, 0, 0, L, 'l')
    cue = place('poolcue', 0, 0, 0, 0, 1.45, 'l') if 'poolcue' in outside.META else None
    tables = [[49.0, Y, 2.5, 90.0], [49.0, Y, 13.0, 90.0]]
    pads = D.setdefault('pads', [])
    for (x, y, z, ry) in tables:
        pads.append([x, y + (felt - 0.03) / 2, z, L * 0.96, felt - 0.03, (mx[2] - mn[2]) * s * 0.96, ry])
    if 'cuerack' in outside.META:
        D['sdeco'].append(place('cuerack', 59.55, Y + 0.55, 7.75, -90, 2.3, 'h'))
    D['pool'] = dict(tables=tables, model=[e[0], e[1], e[2], e[3], e[5]], felt=felt, hw=hw, hd=hd, r=0.048,
                     pockets=[[sx * hw, sz * hd] for sx in (-1, 0, 1) for sz in (-1, 1)],
                     cue=([cue[0], cue[1], cue[2], cue[3], cue[5]] if cue else None), howto=[59.45, Y + 2.3, -2.656, -90.0, 2.4],
                     howto2=[59.45, Y + 2.3, 18.594, -90.0, 2.4])
    print('pool: %d tables, felt %.2f m, playing area %.2f x %.2f m' % (len(tables), felt, 2 * hw, 2 * hd))
