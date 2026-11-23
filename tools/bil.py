# Ritaglia il foglio della schermata bilancia (kit/bil-pezzi.jpg) in PNG singoli e misura i tasti del tastierino.
# Lo sfondo (kit/bil-sfondo.jpg) viene solo rimpicciolito.
import json, sys, numpy as np
from PIL import Image
sys.path.insert(0, 'tools'); from scontorna import alpha
im = alpha('kit/bil-pezzi.jpg'); A = np.asarray(im)[:, :, 3] > 0
sx, sy = im.width / 2000, im.height / 1091
# riquadri a occhio (sul foglio 2000x1091): dentro ognuno prendo il contorno vero
BOX = {'scale': (140, 80, 960, 490), 'bag': (1425, 55, 1725, 400), 'basket': (1330, 415, 1805, 775), 'label': (190, 740, 445, 920),
       'keypad': (620, 525, 1130, 1005), 'button': (1270, 805, 1485, 1005), 'sign': (1555, 790, 1885, 1020)}
out = {}
for k, (x0, y0, x1, y1) in BOX.items():
    x0, x1, y0, y1 = int(x0 * sx), int(x1 * sx), int(y0 * sy), int(y1 * sy)
    sub = A[y0:y1, x0:x1]; ys, xs = np.where(sub)
    c = im.crop((x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1))
    if c.width > 600: c = c.resize((600, round(c.height * 600 / c.width)), Image.LANCZOS)
    c.save(f'bil-{k}.png', optimize=True); out[k] = c.size
# tasti: pixel chiari o colorati (non il grigio della cornice), divisi in righe e colonne dove c'è cornice
kp = np.asarray(Image.open('bil-keypad.png').convert('RGB')).astype(int)
key = (kp.min(2) > 200) | (kp.max(2) - kp.min(2) > 40)
def runs(p, thr):
    on = p > thr; r = []; s = None
    for i, v in enumerate(on):
        if v and s is None: s = i
        if not v and s is not None: r.append((s, i)); s = None
    if s is not None: r.append((s, len(on)))
    return [x for x in r if x[1] - x[0] > 8]
cols = runs(key.sum(0), key.shape[0] * .45); rows = runs(key[:, :int(key.shape[1] * .5)].sum(1), key.shape[1] * .2)
H, W = key.shape
out['keys'] = {'cols': [[round(a / W * 100, 1), round(b / W * 100, 1)] for a, b in cols], 'rows': [[round(a / H * 100, 1), round(b / H * 100, 1)] for a, b in rows]}
# display verde della bilancia, in % del pezzo
sc = np.asarray(Image.open('bil-scale.png').convert('RGB')).astype(int)
g = (sc[:, :, 1] > sc[:, :, 0] + 15) & (sc[:, :, 1] > sc[:, :, 2]); ys, xs = np.where(g)
h, w = g.shape; out['display'] = [round(xs.min() / w * 100, 1), round(ys.min() / h * 100, 1), round(xs.max() / w * 100, 1), round(ys.max() / h * 100, 1)]
bg = Image.open('kit/bil-sfondo.jpg').convert('RGB'); bg.resize((1280, round(bg.height * 1280 / bg.width)), Image.LANCZOS).save('bil-sfondo.jpg', quality=82)
print(json.dumps(out))
