# Disegna la nonna (fronte e spalle) a 24x55 "pixel d'arte"; nel gioco ogni pixel vale 4 pixel del fondale.
import numpy as np
from PIL import Image

PAL = {
 'k':'#2b1d1f',
 'W':'#fbfaf7','H':'#dcdbe2','h':'#aeadbd','j':'#7d7b90',
 'S':'#fbd9be','s':'#efb995','t':'#cc8d6d','r':'#ee9a8e','v':'#a24f4a','e':'#2b1d1f',
 'g':'#6b4a3a','L':'#e8f4f6',
 'c':'#fbf7ee','C':'#d8cfc3',
 'P':'#c9a3dc','p':'#a67cc0','q':'#7d559b','Q':'#563670','y':'#f3d27a',
 'M':'#8e4a6c','m':'#6d3253','n':'#4c2039',
 'T':'#e0c2a8','u':'#b8977f',
 'B':'#6a3d24','b':'#40220f',
 'O':'#e8bd6c','o':'#c08a3e','x':'#8a5a26','R':'#d94a4a','w':'#fff6ee',
}
W, Hh = 24, 55

HEAD_FRONT = [
 "..........kkkk..........",
 ".........kWWHhk.........",
 ".........kWHHhk.........",
 "........kkhHhhkk........",
 "......kkWWWHHHhhkk......",
 ".....kWWHHHHHHHHhhk.....",
 "....kWHHHHHHHHHHHhhk....",
 "...kWHHHHHHHHHHHHHhhk...",
 "...kHHHHHHHhhHHHHHhjk...",
 "...kHHhhSSSSSSSShHhjk...",
 "...kHhShhhSSShhhSthjk...",
 "...kHhSgggSSSgggSthjk...",
 "...kHhgLeLgggLeLgthjk...",
 "...kHhSgggStSgggSthjk...",
 "...khhrrSSStSSSrrthjk...",
 "...khjSSSvSSSvSSttjjk...",
 "....ktSSSSvvvSSSttjk....",
 ".....ktSSSSSSSSSttk.....",
 "......kkkkSSSSkkkk......",
]
HEAD_BACK = [
 "..........kkkk..........",
 ".........kWWHhk.........",
 ".........kWHHhk.........",
 "........kkjhhjkk........",
 "......kkWHhHHhHhkk......",
 ".....kWWHhHHHHhHhhk.....",
 "....kWHHHhHHHHhHHhhk....",
 "...kWHHHHhHHHHhHHHhhk...",
 "...kHWHHHHhHHhHHHHhjk...",
 "...kHHWHHHhHHhHHHhhjk...",
 "...kHHHHHHHhhHHHHHhjk...",
 "...kHHHHHHHHHHHHHhhjk...",
 "...kHHHHHHHHHHHHhhhjk...",
 "...ktHhHHHHHHHHHhhjtk...",
 "...ktshHHHHHHHHhhjstk...",
 "....ksjhhHHHHHhhjjsk....",
 ".....kkjjhhhhhjjjkk.....",
 "......kkkkkkkkkkkk......",
 "......kkkksttskkkk......",
]

def body(front=True):
  g = [['.']*W for _ in range(Hh)]
  def put(x, y, ch):
    if 0 <= x < W and 0 <= y < Hh: g[y][x] = ch
  head = HEAD_FRONT if front else HEAD_BACK
  for y, row in enumerate(head):
    assert len(row) == W, (y, len(row))
    for x, ch in enumerate(row):
      if ch != '.': g[y][x] = ch
  # spalle
  if front:
    for x, ch in zip(range(5, 19), "kPPccSSccPPpkk"): put(x, 19, ch)
    for x, ch in zip(range(4, 20), "kPPPPcCttCcpppqk"): put(x, 20, ch)
    for x in (10, 11, 12, 13): put(x, 21 if x in (10, 13) else 22, 'w')   # perle
  else:
    for x, ch in zip(range(5, 19), "kPPPpppppppqkk"): put(x, 19, ch)
    for x, ch in zip(range(4, 20), "kPPPPppppppppqqk"): put(x, 20, ch)
  # busto e braccia (righe 21-32)
  for y in range(21, 33):
    arm_end = 30
    for x in range(7, 17):                       # busto
      ch = 'P' if x <= 8 else ('q' if x >= 15 else 'p')
      put(x, y, ch)
    if front:
      bw = 4 if y <= 23 else (2 if y <= 26 else 0)   # camicetta a V
      for x in range(12 - bw//2, 12 + bw//2): put(x, y, 'c' if x < 12 else 'C')
      if y > 26: put(11, y, 'q')                  # bordo del golf chiuso
      if y in (25, 28, 31): put(10, y, 'y')       # bottoni
    else:
      if y in (24, 25): put(11, y, 'q'); put(12, y, 'q')   # piega centrale
    if y <= arm_end:
      for x, ch in zip((3, 4, 5), "PPq"): put(x, y, ch)
      for x, ch in zip((18, 19, 20), "pqQ"): put(x, y, ch)
      put(6, y, 'Q'); put(17, y, 'Q')
    if y == 30:
      for x in (3, 4, 5, 18, 19, 20): put(x, y, 'Q')      # polsini
  for x in range(7, 17): put(x, 32, 'q')        # orlo del golf
  # mani
  for y in (31, 32):
    for x, ch in zip((3, 4, 5), "Sst"): put(x, y, ch)
    for x, ch in zip((18, 19, 20), "Sst"): put(x, y, ch)
  # gonna (33-45) a campana con pieghe
  for y in range(33, 46):
    half = 6 + (y - 33) // 4
    x0, x1 = 12 - half, 12 + half - 1
    for x in range(x0, x1 + 1):
      ch = 'M' if x <= x0 + 1 else ('n' if x >= x1 - 1 else 'm')
      if y >= 36 and x in (9, 14): ch = 'n'
      if y >= 37 and x in (10, 15) and x < x1 - 1: ch = 'M'
      put(x, y, ch)
  for x in range(12 - 9, 12 + 9): put(x, 45, 'n')
  # gambe
  for y in range(46, 52):
    for x, ch in zip((8, 9, 10), "TTu"): put(x, y, ch)
    for x, ch in zip((13, 14, 15), "TTu"): put(x, y, ch)
  # scarpe
  for x in range(6, 11): put(x, 52, 'B')
  for x in range(13, 18): put(x, 52, 'B')
  for x in range(6, 11): put(x, 53, 'b' if not front else 'B')
  for x in range(13, 18): put(x, 53, 'b' if not front else 'B')
  if front:
    put(7, 52, 'O'); put(14, 52, 'O')             # riflesso
  return g

def basket(g, left):
  # cestino di vimini col manico; a destra (vista di fronte) o a sinistra (di spalle)
  bx = 0 if left else 15
  hx = 4 if left else 19
  rows = [
   "...kkkk..",
   "..k....k.",
   ".k......k",
   ".k......k",
   "kwRwRwRwk",
   "kOOOOOOOk",
   "kxoxoxoxk",
   "koxoxoxok",
   "kxoxoxoxk",
   "koxoxoxok",
   ".kxxxxxk.",
   "..kkkkk..",
  ]
  if left: rows = [r[::-1] for r in rows]
  for dy, r in enumerate(rows):
    for dx, ch in enumerate(r):
      x, y = bx + dx, 27 + dy
      if ch == '.' or not (0 <= x < W): continue
      if ch == 'k' and dy < 4 and g[y][x] != '.': g[y][x] = 'x'; continue  # manico davanti al corpo
      g[y][x] = ch
  for x, ch in zip((hx - 1, hx, hx + 1), "Sst"): g[31][x] = ch   # mano sul manico

def outline(g):
  out = [r[:] for r in g]
  for y in range(Hh):
    for x in range(W):
      if g[y][x] != '.': continue
      for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        X, Y = x+dx, y+dy
        if 0 <= X < W and 0 <= Y < Hh and g[Y][X] not in '.k':
          out[y][x] = 'k'; break
  return out

def legs_step(g, which):
  # sposta una gamba (e la scarpa) di un pixel in su e in avanti: passo
  out = [r[:] for r in g]
  xs = range(5, 12) if which == 0 else range(12, 19)
  for y in range(46, 55):
    for x in xs: out[y][x] = '.'
  for y in range(46, 55):
    for x in xs:
      if g[y][x] != '.' and y - 1 >= 46: out[y-1][x] = g[y][x]
  return out

def to_img(g):
  a = np.zeros((Hh, W, 4), np.uint8)
  for y in range(Hh):
    for x in range(W):
      ch = g[y][x]
      if ch == '.': continue
      c = PAL[ch]; a[y, x] = [int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16), 255]
  return Image.fromarray(a)

def frames():
  out = {}
  for name, front in (('fronte', True), ('spalle', False)):
    g = body(front); basket(g, left=not front); g = outline(g)
    out[name] = [g, legs_step(g, 0), g, legs_step(g, 1)]
  return out

if __name__ == '__main__':
  import sys
  F = frames(); S = 4
  sheet = Image.new('RGBA', (W*S*8 + 8*8, Hh*S), (0, 0, 0, 0)); x = 0
  for name in ('fronte', 'spalle'):
    for g in F[name]:
      sheet.paste(to_img(g).resize((W*S, Hh*S), Image.NEAREST), (x, 0)); x += W*S + 8
  sheet.save(sys.argv[1])


# ---------- altri clienti: stesse basi della nonna, ricolorate e con capelli/pantaloni diversi
CAST = {
 'nonna':   dict(),
 'signora': dict(bun=False, long=True, glasses=False, basket=False,
                 hair=('#b07850','#8e5a36','#6c4024','#4c2c18'), top=('#9fd8cc','#74bfb0','#4f998c','#346d63'),
                 bottom=('#6c94cc','#4f74ac','#36558a'), pants=True, shoes=('#6a3d24','#40220f')),
 'signore': dict(bun=False, short=True, glasses=False, basket=False,
                 hair=('#6a4a3a','#4a3224','#34221a','#22160e'), top=('#7aa6e0','#5684c8','#3b62a0','#284478'),
                 bottom=('#8a6446','#6c4a32','#4c3222'), pants=True, shoes=('#3a2a22','#1e1410'),
                 skin=('#f0c8a8','#dca482','#b47c5c')),
 'ragazza': dict(bun=False, glasses=False, basket=False,
                 hair=('#d8784a','#b85a32','#8e4224','#66301a'), top=('#f0c64a','#d9a62a','#b0821c','#7a5810'),
                 bottom=('#c8584a','#a8403a','#7c2c28'), shoes=('#b83a30','#7a2018')),
 'ragazzo': dict(bun=False, short=True, glasses=False, basket=False,
                 hair=('#f8e0a0','#e8c470','#c89c48','#9a7430'), top=('#f07a6a','#d8524a','#a83a36','#742424'),
                 bottom=('#6c94cc','#4f74ac','#36558a'), pants=True, shoes=('#f4f4f4','#a8a8b4'),
                 skin=('#e0b090','#c89070','#a06c50')),
}

def make(spec, front):
  g = body(front)
  if spec.get('basket', True): basket(g, left=not front)
  if not spec.get('bun', True):
    for y in range(0, 4): g[y] = ['.']*W
    for x in range(W):
      if g[4][x] in 'WHhj': g[4][x] = 'H'
  if not spec.get('glasses', True) and front:
    for y in (11, 12, 13):
      for x in range(W):
        if g[y][x] in 'gL': g[y][x] = 'S'
    for x in range(W):
      if g[10][x] == 'h' and 6 <= x <= 16: g[10][x] = 'j'
  if spec.get('short'):
    if front:
      for y in range(11, 17):
        for x in (3, 4, 18, 19, 20): g[y][x] = '.'
        if g[y][5] in 'WHhj': g[y][5] = 'S'
        if g[y][17] in 'WHhj': g[y][17] = 't'
      for y in (12, 13): g[y][4] = 't'; g[y][19] = 't'
    else:
      for y in range(14, 17):
        for x in range(5, 19):
          if g[y][x] in 'WHhj': g[y][x] = 's' if 7 <= x <= 16 else 't'
  if spec.get('long'):
    for y in range(15, 26):
      for x in ((3, 4, 5, 18, 19, 20) if front else range(4, 20)):
        if g[y][x] not in '.' or y < 26: g[y][x] = ('h' if x in (5, 18) and front else 'H')
    for x in range(W):
      if front and g[21][x] == 'w': g[21][x] = 'p'
  for y in range(W and Hh):
    for x in range(W):
      if g[y][x] == 'w' and y in (21, 22): g[y][x] = 'p'
  if spec.get('pants'):
    for y in range(40, 52):
      for x in (11, 12): g[y][x] = '.'
    for y in range(46, 52):
      for x in range(7, 17):
        if g[y][x] == '.' and x not in (11, 12): g[y][x] = 'n' if x in (10, 16) else 'm'
  g = outline(g)
  pal = dict(PAL)
  if 'hair' in spec: pal.update(zip('WHhj', spec['hair']))
  if 'top' in spec: pal.update(zip('PpqQ', spec['top']))
  if 'bottom' in spec: pal.update(zip('Mmn', spec['bottom']))
  if spec.get('pants'): pal.update({'T': spec['bottom'][1], 'u': spec['bottom'][2]})
  if 'shoes' in spec: pal.update(zip('Bb', spec['shoes']))
  if 'skin' in spec: pal.update(zip('Sst', spec['skin']))
  return g, pal

def img(g, pal):
  a = np.zeros((len(g), len(g[0]), 4), np.uint8)
  for y, row in enumerate(g):
    for x, ch in enumerate(row):
      if ch == '.': continue
      c = pal[ch]; a[y, x] = [int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16), 255]
  return Image.fromarray(a)

def cart():
  CW, CH = 30, 24
  P2 = {'k':'#2b1d1f','G':'#d7dbe3','g':'#8c94a4','r':'#d84a3a','R':'#a8302a','d':'#5a6070','#':'#3a4050'}
  goods = ['#e84a4a','#f0c040','#58b058','#4a7ad8','#f08a3a','#c058c0','#f4f0e0']
  g = [['.']*CW for _ in range(CH)]
  for x in range(1, CW-1): g[0][x] = 'r'; g[1][x] = 'R'           # maniglia rossa
  for y in range(2, 16):
    inset = (y - 2) // 5
    for x in range(1 + inset, CW - 1 - inset):
      wire = (x - inset) % 3 == 0 or y in (2, 8, 15)
      g[y][x] = ('G' if (x + y) % 2 else 'g') if wire else ('#' if y < 8 else 'd')
  rng = np.random.default_rng(3); rng2 = rng.integers(len(goods), size=(12, 12))
  for y in range(3, 8):
    for x in range(2, CW - 2):
      if g[y][x] == '#': g[y][x] = 'c%d' % (int(rng2[y//2][x//3]))
  for y in range(16, 20):
    for x in (6, CW - 7): g[y][x] = 'g'
  for x in range(5, CW - 5): g[19][x] = 'G'
  for x in (5, 6, 7, CW - 8, CW - 7, CW - 6): g[20][x] = 'd'; g[21][x] = 'd'; g[22][x] = 'k'
  a = np.zeros((CH, CW, 4), np.uint8)
  for y in range(CH):
    for x in range(CW):
      ch = g[y][x]
      if ch == '.': continue
      c = goods[int(ch[1:])] if ch.startswith('c') else P2[ch]
      a[y, x] = [int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16), 255]
  # contorno
  m = a[..., 3] > 0; o = a.copy()
  for y in range(CH):
    for x in range(CW):
      if m[y, x]: continue
      if any(0 <= y+dy < CH and 0 <= x+dx < CW and m[y+dy, x+dx] for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
        o[y, x] = [43, 29, 31, 255]
  return Image.fromarray(o)

def bilancia():
  # bilancia da reparto frutta: testa col display, piatto d'acciaio, mobiletto bianco
  BW, BH = 22, 34
  rows = [
   "....kkkkkkkkkkkkkk....",
   "...kWWWWWWWWWWWWWWk...",
   "...kWddddddddddddWk...",
   "...kWdGGdGGdGGdGGdWk..",
   "...kWdGdddGdGdddGdWk..",
   "...kWdGGdGGdGGdGGdWk..",
   "...kWddddddddddddWk...",
   "...kwwwwwwwwwwwwwwk...",
   "....kkkkkkkkkkkkkk....",
   ".........kssk.........",
   ".........kssk.........",
   ".........kssk.........",
   ".kkkkkkkkkkkkkkkkkkkk.",
   "kSSSSSSSSSSSSSSSSSSSSk",
   "ksssssssssssssssssssssk",
   ".kkkkkkkkkkkkkkkkkkkk.",
   "..kWWWWWWWWWWWWWWWWk..",
   "..kWWWWWWWWWWWWWWWwk..",
   "..kWWRRRRRRRRRRRRWwk..",
   "..kWWWWWWWWWWWWWWWwk..",
   "..kWWWWkkkkkkWWWWWwk..",
   "..kWWWWkppppkWWWWWwk..",
   "..kWWWWkppppkWWWWWwk..",
   "..kWWWWkkkkkkWWWWWwk..",
   "..kWWWWWWWWWWWWWWWwk..",
   "..kWWWWWWWWWWWWWWWwk..",
   "..kWWWWWWWWWWWWWWWwk..",
   "..kWWWWWWWWWWWWWWWwk..",
   "..kwwwwwwwwwwwwwwwwk..",
   "..kssssssssssssssssk..",
   "..kkkkkkkkkkkkkkkkkk..",
  ]
  P3 = {'k':'#2b1d1f','W':'#f4f2ec','w':'#cfcac0','d':'#1c2a22','G':'#7cf08a','S':'#e8ecf2','s':'#9aa2b2','R':'#d84a3a','p':'#f8f8f8'}
  a = np.zeros((BH, BW, 4), np.uint8)
  for y, r in enumerate(rows):
    for x, ch in enumerate(r[:BW]):
      if ch == '.': continue
      c = P3[ch]; a[y, x] = [int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16), 255]
  return Image.fromarray(a)

def atlas(path_png):
  # una riga per personaggio: fronte(fermo,passoA,passoB) + spalle(fermo,passoA,passoB); in fondo il carrello
  names = list(CAST); fw, fh = W, Hh
  sheet = Image.new('RGBA', (fw * 6, fh * len(names) + 34), (0, 0, 0, 0))
  for r, n in enumerate(names):
    for v, front in enumerate((True, False)):
      g, pal = make(CAST[n], front)
      for f, gg in enumerate((g, legs_step(g, 0), legs_step(g, 1))):
        sheet.paste(img(gg, pal), ((v * 3 + f) * fw, r * fh))
  sheet.paste(cart(), (0, fh * len(names))); sheet.paste(bilancia(), (32, fh * len(names)))
  sheet.save(path_png)
  return names
