"""read every Mudwater card's edge numbers (t,l,r,b), level (diamonds) and family (badge) off mwc_XXX.jpg"""
import numpy as np, json
from PIL import Image
MW = '/home/claude/dinopawnz/mudwater/'
STAT = {'t': (68, 29, 84, 53), 'l': (39, 58, 53, 82), 'r': (99, 58, 114, 82), 'b': (68, 89, 84, 112)}
DIAM = [(297, 25, 319, 45), (323, 25, 344, 45), (350, 25, 370, 45), (376, 25, 396, 45), (401, 25, 421, 45)]
def glyph(a, box):
    x0, y0, x1, y1 = box; g = a[y0 - 2:y1 + 2, x0 - 3:x1 + 3].min(-1)       # white digits only (the ring is gold: low blue)
    m = (g > 175).astype(float)
    # keep the biggest blob (the digit), drop any ring specks touching the crop edge
    from scipy import ndimage
    lab, n = ndimage.label(m)
    if n > 1:
        sizes = ndimage.sum(m, lab, range(1, n + 1)); m = (lab == (1 + int(np.argmax(sizes)))).astype(float)
    return m
def norm(g):
    ys, xs = np.nonzero(g)
    if len(xs) == 0: return np.zeros((20, 14))
    c = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return np.asarray(Image.fromarray((c * 255).astype(np.uint8)).resize((14, 20), Image.BILINEAR)).astype(float) / 255
G = []; meta = []
cards = {}
for n in range(1, 121):
    a = np.asarray(Image.open(MW + 'mwc_%03d.jpg' % n).convert('RGB')).astype(float)
    for k, box in STAT.items(): G.append(norm(glyph(a, box)).ravel()); meta.append((n, k))
    lv = sum(1 for (x0, y0, x1, y1) in DIAM if a[y0:y1, x0:x1].max(-1).mean() > 70)
    pill = a[35:70, 505:600]
    cards[n] = {'lv': lv, 'pill': pill}
G = np.array(G)
# k-means into 9 clusters (digits 1-9), deterministic init by farthest point
def kmeans(X, k, it=40):
    C = [X[0]]
    for _ in range(k - 1): d = np.min([((X - c) ** 2).sum(1) for c in C], 0); C.append(X[d.argmax()])
    C = np.array(C)
    for _ in range(it):
        lab = np.argmin(((X[:, None] - C[None]) ** 2).sum(-1), 1)
        C = np.array([X[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
    return lab, C
lab, C = kmeans(G, 9)
# montage of each cluster's first 12 members for labelling by eye
rows = []
for j in range(9):
    idx = np.nonzero(lab == j)[0][:14]
    row = np.ones((24, 14 * 18)) * 0.3
    for i, t in enumerate(idx): row[2:22, i * 18:i * 18 + 14] = G[t].reshape(20, 14)
    rows.append(row)
img = np.vstack([np.vstack([r, np.ones((4, r.shape[1])) * 0.6]) for r in rows])
Image.fromarray((img * 255).astype(np.uint8)).resize((img.shape[1] * 3, img.shape[0] * 3), Image.NEAREST).save('/home/claude/shots/digit_clusters.png')
print('cluster sizes', np.bincount(lab, minlength=9).tolist())
json.dump({'lab': lab.tolist(), 'meta': meta, 'lv': {n: cards[n]['lv'] for n in cards}}, open('cards/raw.json', 'w'))
np.save('cards/pills.npy', np.array([cards[n]['pill'] for n in range(1, 121)]))
