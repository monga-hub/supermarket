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
EXT = alpha('kit/foglio-extra.jpg')
SCA = alpha('kit/foglio-scaffali.jpg')
FRI = alpha('kit/foglio-frighi.jpg')
CAS = alpha('kit/foglio-cassette.jpg')
BAN = alpha('kit/foglio-banchi.jpg')
CES = alpha('kit/foglio-ceste.jpg')
VUO = alpha('kit/foglio-vuoti.jpg')
MC2 = alpha('kit/foglio-macelleria3.jpg')

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
# mobili già pieni (un foglio per tipo): box, A = angolo anteriore-basso a sinistra, B = punto più basso
def full(sheet, L, sv, items):
    return {n: dict(sheet=sheet, box=(x0 - 4, y0 - 4, x1 + 4, y1 + 4), A=A, B=B, L=L, sv=sv) for n, (x0, y0, x1, y1), A, B in items}
PIECES |= full(SCA, 2, .42, [  # scaffale da 2 caselle, ripetuto lungo il mobile
  ('s:PASTA', (85, 137, 413, 921), (85, 775), (316, 920)), ('s:BISCOTTI', (475, 137, 801, 921), (475, 776), (704, 920)),
  ('s:CEREALI', (864, 119, 1190, 921), (864, 775), (1093, 920)), ('s:CONSERVE', (1253, 137, 1579, 921), (1253, 776), (1484, 920)),
  ('s:CAFFÈ', (1640, 137, 1966, 921), (1640, 777), (1871, 920)),
  ('s:OLIO', (85, 1097, 413, 1924), (85, 1787), (314, 1923)), ('s:VINO', (475, 1097, 802, 1924), (475, 1787), (703, 1923)),
  ('s:ACQUA', (863, 1098, 1190, 1924), (863, 1790), (1090, 1923)), ('s:BIBITE', (1251, 1097, 1579, 1924), (1251, 1787), (1480, 1923)),
  ('s:RISO', (1637, 1097, 1967, 1924), (1637, 1787), (1869, 1923))])
PIECES |= full(FRI, 2, .45, [  # dal foglio: 1° in alto, 2° in alto, 3° e 4° in basso
  ('f:LATTE', (158, 158, 649, 965), (158, 792), (497, 964)), ('f:YOGURT', (1052, 212, 1474, 965), (1052, 817), (1344, 964)),
  ('f:SUCCHI', (1048, 1049, 1474, 1799), (1048, 1646), (1350, 1798)), ('f:BURRO', (1521, 1068, 1938, 1816), (1521, 1668), (1812, 1815))])
PIECES |= full(CAS, 1, None, [
  ('c:MELE', (196, 161, 605, 628), (196, 517), (409, 627)), ('c:BANANE', (825, 155, 1233, 628), (825, 517), (1035, 627)),
  ('c:ARANCE', (1453, 172, 1861, 628), (1453, 518), (1664, 627)), ('c:POMODORI', (197, 791, 604, 1258), (197, 1147), (406, 1257)),
  ('c:INSALATA', (820, 790, 1228, 1258), (820, 1147), (1031, 1257)), ('c:BROCCOLI', (1445, 790, 1853, 1258), (1445, 1147), (1655, 1257)),
  ('c:UVA', (196, 1404, 604, 1882), (196, 1775), (404, 1881)), ('c:CAVOLI', (820, 1428, 1228, 1882), (820, 1775), (1027, 1881)),
  ('c:CAROTE', (1446, 1404, 1853, 1882), (1446, 1775), (1653, 1881))])

# vuoti per l'esaurito: lo scaffale stretto del foglio ha la stessa forma di quelli pieni (quello largo non lo uso)
PIECES |= full(VUO, 2, .42, [('v:scaffale', (864, 137, 1190, 921), (864, 778), (1093, 920))])
PIECES |= full(VUO, 2, .45, [('v:frigo', (1411, 104, 1943, 1034), (1411, 833), (1783, 1033))])
PIECES |= full(VUO, .7, None, [('v:cesta', (194, 1233, 739, 1916), (194, 1761), (468, 1915))])
PIECES |= full(VUO, 2, None, [('v:bancale', (1147, 1376, 1961, 1914), (1147, 1704), (1533, 1913))])

# macelleria lunga: 3 segmenti di bancone da 5/3 di casella, messi in fila (5 caselle + distributore)
PIECES |= full(MC2, 5 / 3, None, [('mac1', (60, 505, 790, 1255), (129, 987), (580, 1246)),
  ('mac2', (925, 466, 1655, 1245), (994, 972), (1445, 1234)), ('mac3', (1775, 484, 2505, 1270), (1844, 1020), (2261, 1261))])

# testate: metà destra dello scaffale pieno (1 casella, col fianco)
PIECES |= {'t:' + n[2:]: dict(p, box=((p['A'][0] + p['B'][0]) // 2, *p['box'][1:]), A=((p['A'][0] + p['B'][0]) // 2, (p['A'][1] + p['B'][1]) // 2), L=1)
           for n, p in list(PIECES.items()) if n.startswith('s:') or n == 'v:scaffale'}
PIECES |= full(CES, .7, None, [(n, (x0, y0, x1, y1), (x0 + 15, yl), B) for n, (x0, y0, x1, y1), yl, B in [
  ('k:PASTA', (68, 235, 431, 888), 790, (249, 887)), ('k:BISCOTTI', (463, 240, 812, 888), 790, (636, 887)),
  ('k:CEREALI', (850, 235, 1199, 888), 790, (1024, 887)), ('k:CONSERVE', (1237, 286, 1586, 888), 790, (1410, 887)),
  ('k:CAFFÈ', (1623, 262, 1973, 888), 790, (1798, 887)),
  ('k:OLIO', (77, 1128, 423, 1769), 1676, (250, 1768)), ('k:VINO', (465, 1125, 810, 1768), 1676, (637, 1767)),
  ('k:ACQUA', (851, 1147, 1197, 1768), 1676, (1024, 1767)), ('k:BIBITE', (1238, 1188, 1584, 1768), 1676, (1411, 1767)),
  ('k:RISO', (1626, 1149, 1971, 1768), 1676, (1799, 1767))]])
PIECES |= full(BAN, 2, None, [('b:ACQUA', (120, 367, 603, 913), (120, 801), (336, 912)), ('b:BIBITE', (649, 370, 1107, 907), (649, 798), (859, 906))])
PIECES |= full(BAN, 1.5, None, [('salumi2', (1036, 1058, 1558, 1813), (1036, 1573), (1395, 1812))])  # ripetuto 2 volte sul banco da 3
PIECES |= full(BAN, .8, None, [('bilancia2', (1667, 1100, 1966, 1867), (1667, 1792), (1815, 1866))])
PIECES['pane2'] = dict(full(BAN, 2, None, [('x', (1207, 270, 1891, 922), (1880, 670), (1394, 921))])['x'], mirror=True)

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
    if p.get('erase'):  # via i pezzi estranei attaccati al mobile (poligono in coordinate del foglio)
        s = np.asarray(src).copy(); mk = Image.new('L', src.size, 0)
        ImageDraw.Draw(mk).polygon([(x - ox, y - oy) for x, y in p['erase']], fill=255); s[np.asarray(mk) > 0, 3] = 0; src = Image.fromarray(s, 'RGBA')
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
    items['cartello'] = {'img': product((180, 165, 530, 625), 38, EXT)}
    items['carrelli'] = {'img': product((670, 95, 1345, 785), 62, EXT)}
    items['cestini'] = {'img': product((1480, 160, 1845, 760), 48, EXT)}
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
