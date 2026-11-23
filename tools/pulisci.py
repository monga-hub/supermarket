# Toglie i clienti dipinti dal fondale: ogni tassello 24x24 del contorno viene riempito
# copiando il punto dell'immagine che meglio combacia col bordo intorno (timbro clone automatico).
import sys, numpy as np
from PIL import Image, ImageDraw
SRC, OUT = sys.argv[1], sys.argv[2]
im = Image.open(SRC).convert('RGB'); a = np.asarray(im).astype(np.int16).copy(); H, W, _ = a.shape
P = {
 'p1': [(188,640),(262,640),(270,700),(272,855),(240,868),(185,872),(150,880),(120,860),(95,800),(95,720),(125,712),(190,712)],
 'p2': [(740,935),(812,935),(822,1000),(830,1120),(832,1158),(760,1162),(728,1140),(735,1060),(742,1000)],
 'p4': [(1310,545),(1378,545),(1392,610),(1400,650),(1450,640),(1525,690),(1525,800),(1480,835),(1430,835),(1390,815),(1300,805),(1300,740),(1312,640)],
 'p5': [(1572,1038),(1648,1038),(1662,1110),(1664,1262),(1600,1272),(1560,1262),(1540,1275),(1500,1278),(1470,1250),(1462,1150),(1492,1118),(1572,1110)],
 'p7': [(2005,285),(2065,285),(2072,340),(2072,500),(2040,507),(1998,500),(1998,380)],
}
which = sys.argv[3].split(',') if len(sys.argv) > 3 else list(P)
mimg = Image.new('L', (W, H), 0); d = ImageDraw.Draw(mimg)
for k in which: d.polygon(P[k], fill=255)
hole = np.asarray(mimg) > 0
FLOORONLY = Image.new('L', (W, H), 0); ImageDraw.Draw(FLOORONLY).polygon(P['p5'], fill=255) if 'p5' in which else None
FLOORONLY = np.asarray(FLOORONLY) > 0
af = a.astype(float); sat = (af.max(2) - af.min(2)) / (af.max(2) + 1)
floorish = (sat < 0.22) & (af.mean(2) > 120)   # piastrelle: grigio-azzurro chiaro poco saturo
forbid = hole.copy()                      # sorgenti vietate: dentro i buchi ancora da riempire
T, R = 24, 10                             # tassello, larghezza del bordo di confronto
def dil(m, r):
  o = m.copy()
  for dy in range(-r, r+1):
    for dx in range(-r, r+1):
      if dx*dx+dy*dy <= r*r: o |= np.roll(np.roll(m, dy, 0), dx, 1)
  return o
def dil0(m, r):
  o = m.copy()
  for dy in range(-r, r+1):
    for dx in range(-r, r+1): o |= np.roll(np.roll(m, dy, 0), dx, 1)
  return o
hole = dil0(hole, 3); forbid = hole.copy()
ys, xs = np.nonzero(hole)
tiles = sorted({(y//T, x//T) for y, x in zip(ys, xs)}, key=lambda t: (t[0], t[1]))
for ty, tx in tiles:
  y0, x0 = ty*T, tx*T
  Y0, X0, Y1, X1 = max(0,y0-R), max(0,x0-R), min(H,y0+T+R), min(W,x0+T+R)
  win = np.zeros((Y1-Y0, X1-X0), bool); tm = hole[Y0:Y1, X0:X1].copy(); tm[:] = False
  tm[y0-Y0:y0-Y0+T, x0-X0:x0-X0+T] = hole[y0:y0+T, x0:x0+T]
  if not tm.any(): continue
  band = dil(tm, R) & ~forbid[Y0:Y1, X0:X1]
  need = dil(tm, R)
  ref = a[Y0:Y1, X0:X1]; best = None
  cand = [(m*58+n*58+jx, m*30-n*30+jy) for m in range(-4,5) for n in range(-4,5) for jx in (-4,-2,0,2,4) for jy in (-2,0,2) if (m,n)!=(0,0)]
  for dx, dy in cand:
      sy0, sx0 = Y0+dy, X0+dx
      if sy0 < 0 or sx0 < 0 or sy0+(Y1-Y0) > H or sx0+(X1-X0) > W: continue
      if (forbid[sy0:sy0+Y1-Y0, sx0:sx0+X1-X0] & need).any(): continue
      if FLOORONLY[y0, x0] and floorish[sy0:sy0+Y1-Y0, sx0:sx0+X1-X0][tm].mean() < 0.97: continue
      c = np.abs(a[sy0:sy0+Y1-Y0, sx0:sx0+X1-X0][band] - ref[band]).mean() + 0.01*(abs(dx)+abs(dy))
      if best is None or c < best[0]: best = (c, dx, dy)
  if best is None: print('nessuna sorgente', y0, x0); continue
  c, dx, dy = best
  for ddy in (-1, 0, 1):                  # rifinitura al pixel
    for ddx in (-1, 0, 1):
      sy0, sx0 = Y0+dy+ddy, X0+dx+ddx
      if sy0 < 0 or sx0 < 0 or sy0+(Y1-Y0) > H or sx0+(X1-X0) > W: continue
      if (forbid[sy0:sy0+Y1-Y0, sx0:sx0+X1-X0] & need).any(): continue
      cc = np.abs(a[sy0:sy0+Y1-Y0, sx0:sx0+X1-X0][band] - ref[band]).mean() + 0.01*(abs(dx+ddx)+abs(dy+ddy))
      if cc < c: c, best = cc, (cc, dx+ddx, dy+ddy)
  _, dx, dy = best
  src = a[Y0+dy:Y1+dy, X0+dx:X1+dx]
  ref[tm] = src[tm]; hole[Y0:Y1, X0:X1][tm] = False; forbid[Y0:Y1, X0:X1][tm] = False
Image.fromarray(a.astype(np.uint8)).save(OUT, quality=95)
print('ok', len(tiles), 'tasselli')
