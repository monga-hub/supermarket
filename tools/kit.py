# Costruisce kit.png + kit.json dai fogli AI (kit/foglio-mobili.jpg, kit/foglio-prodotti.jpg).
# Ogni mobile viene ritagliato, scalato e inclinato perché il suo bordo anteriore in basso
# combaci con L caselle della griglia (una casella = 58,30 px lungo l'asse).
# Uso (da spesa-nonna/):  python3 tools/kit.py
import json, numpy as np
from PIL import Image, ImageDraw
from scontorna import alpha

MOB = alpha('kit/foglio-mobili.jpg')
PRO = alpha('kit/foglio-prodotti.jpg')
MOB2 = alpha('kit/foglio-mobili2.jpg')
PRO2 = alpha('kit/foglio-prodotti2.jpg')
MAC = alpha('kit/foglio-macelleria.jpg')

# il foglio mobili ha righe chiare del pavimento sotto lo scaffale doppio: lì uso una soglia più larga
def loose(img, box):
    c = np.asarray(img.crop(box)).copy()
    rgb = c[:, :, :3].astype(int); mx, mn = rgb.max(2), rgb.min(2)
    bgl = ((mn > 178) & (mx - mn < 48)) | (c[:, :, 3] == 0)
    m = c[:, :, 3] == 0
    while True:
        d = m.copy(); d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]; d &= bgl
        if (d == m).all(): break
        m = d
    c[:, :, 3] = np.where(m, 0, c[:, :, 3]); return Image.fromarray(c, 'RGBA')

# nome: riquadro nel foglio, A = angolo anteriore-basso lontano, B = angolo anteriore-basso vicino,
# L caselle, sv = scala verticale (None = uguale all'orizzontale), mirror = il pezzo nel foglio guarda dall'altra parte
PIECES = {
  'scaffale': dict(box=(90, 74, 880, 770), A=(232, 481), B=(752, 750), L=4, loose=True,
                   boards=[334, 234, 134, 24], spans=[(.03, .44), (.52, .96)]),
  'muro':     dict(box=(950, 134, 1372, 720), A=(961, 564), B=(1270, 719), L=3,
                   boards=[362, 222, 132, 37], spans=[(.02, 1.0)]),
  'frigo':    dict(box=(1460, 128, 1928, 862), A=(1468, 704), B=(1787, 861), L=2, sv=.45,
                   boards=[346, 256, 166, 86], spans=[(.06, .46), (.56, .94)],
                   glass=[[(1490, 304), (1600, 354), (1600, 694), (1490, 640)], [(1645, 370), (1770, 434), (1770, 784), (1645, 718)]]),
  'cassetta': dict(box=(892, 976, 1250, 1292), A=(904, 1213), B=(1061, 1287), L=1),
  'pane':     dict(box=(1330, 944, 1856, 1500), A=(1338, 1322), B=(1684, 1495), L=2, sv=.42,
                   glass=[[(1368, 1075), (1500, 985), (1812, 1165), (1812, 1435), (1705, 1482), (1385, 1322)]], brownKeep=True),
  'cassa':    dict(box=(208, 1406, 990, 1976), A=(720, 1800), B=(390, 1972), L=3, mirror=True),
  # foglio 2 (s2): A = estremo lontano del lato lungo, B = angolo vicino, nel foglio originale
  'cassa2':   dict(s2=1, box=(1068, 68, 1822, 633), A=(1750, 360), B=(1250, 615), L=3, sv=.45, mirror=True),
  'salumi':   dict(s2=1, box=(1128, 566, 1837, 1212), A=(1800, 975), B=(1335, 1200), L=3, mirror=True),
  'bancale':  dict(s2=1, box=(144, 1477, 798, 1903), A=(794, 1696), B=(413, 1899), L=2, mirror=True),
  'cesta':    dict(s2=1, box=(916, 1321, 1284, 1863), A=(925, 1773), B=(1077, 1859), L=.7),
  'testata':  dict(s2=1, box=(1478, 1261, 1855, 1903), A=(1486, 1767), B=(1762, 1899), L=1, sv=.3,
                   boards=[347, 241, 135, 30], spans=[(.05, .85)]),
  'bilancia': dict(box=(1347, 1607, 1610, 1864), A=(1358, 1813), B=(1467, 1862), L=.9),
  # foglio macelleria: L in proporzione al bancone (715 px = 3 caselle)
  'macelleria': dict(sheet=MAC, box=(130, 480, 1330, 1470), A=(200, 1060), B=(915, 1455), L=3),
  'display':    dict(sheet=MAC, box=(1475, 130, 1880, 535), A=(1482, 357), B=(1797, 530), L=1.32),
  'insegna':    dict(sheet=MAC, box=(1475, 555, 1878, 1035), A=(1482, 826), B=(1862, 1022), L=1.6),
}
PRODS = {  # riquadri trovati per righe/colonne vuote; h = altezza finale in px di gioco
  'ACQUA': ((140, 107, 241, 543), 34), 'VINO': ((327, 107, 440, 543), 40), 'OLIO': ((531, 107, 657, 543), 34),
  'BIBITE': ((754, 107, 883, 543), 22), 'CONSERVE': ((978, 107, 1142, 543), 22), 'BISCOTTI': ((1231, 107, 1428, 543), 26),  'CAFFÈ': ((130, 629, 374, 1042), 28), 'CEREALI': ((451, 629, 689, 1042), 34),
  'RISO': ((773, 629, 968, 1042), 26), 'LATTE': ((1040, 629, 1193, 1042), 32), 'YOGURT': ((1228, 629, 1377, 1042), 15),
  'BURRO': ((1388, 629, 1570, 1042), 13), 'FORMAGGI': ((1602, 629, 1925, 1042), 22),
  'MELE': ((141, 1245, 386, 1460), 30), 'ARANCE': ((449, 1245, 690, 1460), 30), 'BANANE': ((757, 1245, 985, 1460), 30),
  'POMODORI': ((1354, 1245, 1596, 1460), 30), 'UVA': ((1664, 1245, 1881, 1460), 36),
  'INSALATA': ((757, 1573, 976, 1804), 34), 'CAVOLI': ((1061, 1573, 1283, 1804), 34), 'BROCCOLI': ((1365, 1573, 1578, 1804), 34),
  'CAROTE': ((1644, 1573, 1903, 1804), 30),
}

ROWS2 = [(100, 365), (405, 703), (720, 1024), (1034, 1368), (1416, 1693), (1750, 1946)]
PRODS2 = {
  'PASTA': [(117, 289, 0, 30), (321, 495, 0, 30), (525, 699, 0, 30)],
  'BISCOTTI': [(771, 905, 0, 28), (954, 1086, 0, 28), (1134, 1269, 0, 28), (1353, 1516, 0, 24), (1557, 1720, 0, 24), (1764, 1925, 0, 24)],
  'CEREALI': [(117, 291, 1, 34), (322, 496, 1, 34), (522, 696, 1, 34), (937, 1104, 1, 34)],
  'CAFFÈ': [(756, 909, 1, 30), (1128, 1285, 1, 30)],
  'RISO': [(1367, 1521, 1, 28), (1572, 1727, 1, 28), (1775, 1930, 1, 28)],
  'CONSERVE': [(124, 269, 2, 24), (324, 470, 2, 24), (519, 666, 2, 24), (752, 891, 2, 24), (938, 1078, 2, 24)],
  'OLIO': [(1606, 1708, 2, 34), (1804, 1896, 2, 34)],
  'VINO': [(147, 237, 3, 40), (341, 430, 3, 40), (532, 624, 3, 40)],
  'ACQUA': [(760, 853, 3, 34), (942, 1034, 3, 34), (1126, 1220, 3, 34)],
  'BIBITE': [(1402, 1516, 3, 22), (1597, 1710, 3, 22), (1791, 1904, 3, 22)],
  'SUCCHI': [(134, 267, 4, 30), (329, 464, 4, 30), (525, 658, 4, 30)],
  'LATTE': [(737, 863, 4, 32), (922, 1048, 4, 32), (1107, 1233, 4, 32)],
  'YOGURT': [(1361, 1520, 4, 16), (1559, 1719, 4, 16), (1756, 1917, 4, 16)],
  'PANE': [(139, 428, 5, 20), (519, 945, 5, 14), (1026, 1517, 5, 12), (1605, 1877, 5, 16)],
}

def tight(im):
    bb = im.getchannel('A').getbbox(); return im.crop(bb), bb

def furniture(name, p):
    sheet = p.get('sheet') or (MOB2 if p.get('s2') else MOB)
    src = loose(sheet, p['box']) if p.get('loose') else sheet.crop(p['box'])
    ox, oy = p['box'][:2]
    # tengo solo il pezzo attaccato al punto B (via i frammenti dei mobili vicini nel riquadro)
    arr = np.asarray(src).copy(); on = arr[:, :, 3] > 0
    m = np.zeros_like(on); by, bx = p['B'][1] - oy, p['B'][0] - ox
    m[max(0, by - 4):by + 1, max(0, bx - 6):bx + 7] = True; m &= on
    while True:
        d = m.copy(); d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
        d[1:, 1:] |= m[:-1, :-1]; d[:-1, :-1] |= m[1:, 1:]; d[1:, :-1] |= m[:-1, 1:]; d[:-1, 1:] |= m[1:, :-1]; d &= on
        if (d == m).all(): break
        m = d
    arr[:, :, 3] = np.where(m, arr[:, :, 3], 0); src = Image.fromarray(arr, 'RGBA')
    A = (p['A'][0] - ox, p['A'][1] - oy); B = (p['B'][0] - ox, p['B'][1] - oy)
    if p.get('glass'):  # versione "vetro": i vetri diventano semitrasparenti, così i prodotti si vedono dietro
        mask = Image.new('L', src.size, 0); d = ImageDraw.Draw(mask)
        for g in p['glass']: d.polygon([(x - ox, y - oy) for x, y in g], fill=255)
        s = np.asarray(src).copy(); inside = np.asarray(mask) > 0
        rgb = s[:, :, :3].astype(int)
        keep = (rgb[:, :, 0] > rgb[:, :, 2] + 25) if p.get('brownKeep') else np.zeros(inside.shape, bool)
        s[:, :, 3] = np.where(inside & ~keep, np.minimum(s[:, :, 3], 38), s[:, :, 3])
        over = Image.fromarray(s, 'RGBA')
    if p.get('mirror'):
        W = src.width; src = src.transpose(Image.FLIP_LEFT_RIGHT); A = (W - 1 - A[0], A[1]); B = (W - 1 - B[0], B[1])
    ux, uy = (B[0] - A[0]) / p['L'], (B[1] - A[1]) / p['L']
    a = 58 / ux; sv = p.get('sv') or a
    k = (30 - sv * uy) / 58                     # inclinazione per far tornare il passo 58,30
    def warp(im):
        w, h = round(im.width * a), round(im.height * sv)
        im = im.convert('RGBa').resize((w, h), Image.LANCZOS)
        lo, hi = min(0, k * w), max(0, k * w)
        H2 = int(h + hi - lo) + 2
        # y_dest = y + k*x - lo  →  y_src = y_dest - k*x + lo
        im = im.transform((w, H2), Image.AFFINE, (1, 0, 0, -k, 1, lo), resample=Image.BICUBIC)
        return im.convert('RGBA'), lo
    if name == 'cassetta':  # i buchi bianchi tra le doghe diventano legno in ombra
        s = np.asarray(src).copy(); rgb = s[:, :, :3].astype(int)
        hole = (rgb.min(2) > 200) & (s[:, :, 3] > 0); s[hole, :3] = (74, 44, 26); src = Image.fromarray(s, 'RGBA')
    if name == 'cesta':  # il bianco chiuso tra le gambe diventa trasparente (parto dal fondo e allargo solo dentro il bianco)
        s = np.asarray(src).copy(); white = (s[:, :, :3].min(2) >= 238) & (s[:, :, 3] > 0)
        m = np.zeros_like(white); cut = int(white.shape[0] * .65); m[cut:] = white[cut:]
        while True:
            d = m.copy(); d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]; d &= white
            if (d == m).all(): break
            m = d
        s[m, 3] = 0; src = Image.fromarray(s, 'RGBA')
    img, lo = warp(src)
    ax, ay = A[0] * a, A[1] * sv + k * A[0] * a - lo
    img, bb = tight(img); ax -= bb[0]; ay -= bb[1]
    out = {'img': img, 'ax': round(ax, 1), 'ay': round(ay, 1), 'L': p['L'], 'sv': round(sv, 4)}
    if p.get('glass'):
        o, _ = warp(over); out['over'] = o.crop(bb)
    if 'boards' in p: out['boards'] = [round(h * sv, 1) for h in p['boards']]; out['spans'] = p['spans']
    return out

def product(box, h, sheet=None):
    h = round(h * 1.8)  # più grandi del necessario: nel gioco si rimpiccioliscono senza sfocare
    im, _ = tight((sheet or PRO).crop(box)); s = h / im.height
    return im.convert('RGBa').resize((max(1, round(im.width * s)), h), Image.LANCZOS).convert('RGBA')

if __name__ == '__main__':
    items = {}
    for n, p in PIECES.items():
        f = furniture(n, p); items[n] = f
        if 'over' in f: items[n + ':vetro'] = {'img': f.pop('over'), 'ax': f['ax'], 'ay': f['ay']}
    for n, (box, h) in PRODS.items(): items['p:' + n + ':0'] = {'img': product(box, h)}
    items['p:CARNE:0'] = {'img': product((1389, 1555, 1833, 1833), 30, MAC)}
    items['distributore'] = {'img': product((1109, 187, 1304, 699), 70, MAC)}
    # insalata e cavolo nel foglio sono quasi uguali: insalata verso il giallo-chiaro, cavolo verso il verde-azzurro
    import colorsys
    for n, dh, kv, add in (('INSALATA', -.06, 1.12, .05), ('CAVOLI', .08, .95, 0)):
        a = np.asarray(items['p:' + n + ':0']['img']).astype(float); rgb = a[:, :, :3] / 255
        for i in range(a.shape[0]):
            for j in range(a.shape[1]):
                H, S, V = colorsys.rgb_to_hsv(*rgb[i, j])
                if S > .12 and .15 < H < .5: rgb[i, j] = colorsys.hsv_to_rgb(H + dh, min(1, S * (1.1 if dh < 0 else 1)), min(1, V * kv + add))
        a[:, :, :3] = rgb * 255; items['p:' + n + ':0']['img'] = Image.fromarray(a.astype('uint8'), 'RGBA')
    for n, lst in PRODS2.items():
        k0 = 1 if n in PRODS else 0
        for k, (x0, x1, row, h) in enumerate(lst):
            y0, y1 = ROWS2[row]; items[f'p:{n}:{k + k0}'] = {'img': product((x0, y0, x1, y1), h, PRO2)}
    # impacchetto a righe
    W = 1024; x = y = rowh = 0; meta = {}
    order = sorted(items, key=lambda n: -items[n]['img'].height)
    for n in order:
        im = items[n]['img']
        if x + im.width > W: x = 0; y += rowh + 2; rowh = 0
        items[n]['pos'] = (x, y); x += im.width + 2; rowh = max(rowh, im.height)
    atlas = Image.new('RGBA', (W, y + rowh))
    for n, it in items.items():
        atlas.alpha_composite(it['img'], it['pos'])
        meta[n] = {k: v for k, v in it.items() if k not in ('img', 'pos')} | {'r': [*it['pos'], it['img'].width, it['img'].height]}
    atlas.save('kit.png', optimize=True)
    json.dump(meta, open('kit.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(atlas.size, {n: m['r'] for n, m in meta.items() if not n.startswith('p:')})
