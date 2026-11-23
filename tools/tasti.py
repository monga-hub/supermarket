# L'AI non riesce a fare un tastierino 3x4 regolare: prendo un tasto crema, il rosso e il verde
# da kit/bil-tasti.jpg e compongo io la griglia 3x4 con cornice grigia -> bil-keypad.png. Stampa la posizione dei tasti in %.
import json, numpy as np
from PIL import Image, ImageDraw
im = Image.open('kit/bil-tasti.jpg').convert('RGB'); a = np.asarray(im).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
def bbox(m):
    ys, xs = np.where(m); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
red = bbox((r > 220) & (g < 175) & (b < 175)); green = bbox((g > 200) & (r < 195) & (b < 180))
cream = (r > 225) & (g > 210) & (b > 180) & (r - b > 12) & (r - b < 70)
# tasto crema in alto nella colonna del rosso
x0, _, x1, _ = red; col = cream[:, x0 + 5:x1 - 5].mean(1) > .5; ys = np.where(col)[0]
y0 = ys[0]; y1 = y0
while col[y1]: y1 += 1
cr = (x0, y0, x1, y1 + 14)  # +14: il bordino scuro sotto il tasto
kw, kh = red[2] - red[0], red[3] - red[1]
keys = {k: im.crop(bx).resize((kw, kh), Image.NEAREST) for k, bx in [('c', cr), ('r', red), ('g', green)]}
gap, m = 24, 40; W, H = 3 * kw + 2 * gap + 2 * m, 4 * kh + 3 * gap + 2 * m
out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
d.rounded_rectangle((0, 0, W - 1, H - 1), 26, fill=(120, 118, 128)); d.rounded_rectangle((8, 8, W - 9, H - 15), 20, fill=(178, 176, 180))
d.rounded_rectangle((m - 10, m - 10, W - m + 9, H - m + 9), 12, fill=(138, 136, 146))
pos = []
for i in range(12):
    c, rw = i % 3, i // 3; x, y = m + c * (kw + gap), m + rw * (kh + gap)
    out.paste(keys['r' if i == 9 else 'g' if i == 11 else 'c'], (x, y))
    pos.append([round(x / W * 100, 1), round(y / H * 100, 1), round(kw / W * 100, 1), round(kh / H * 100, 1)])
out = out.resize((600, round(H * 600 / W)), Image.NEAREST); out.save('bil-keypad.png', optimize=True)
print(json.dumps({'size': out.size, 'keys': pos}))
