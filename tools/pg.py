# Ritaglia i fogli personaggi (kit/pg-*.jpg) in pose singole e le mette in personaggi2.png + personaggi2.json.
# Le pose sono separate da spazio bianco: divido prima in righe, poi in colonne, guardando dove c'è disegno.
# Ogni posa viene girata in modo da guardare a DESTRA (il gioco specchia da solo quando si va a sinistra).
import json, sys, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'tools'); from scontorna import alpha

def split(prof, n):
    # n pezzi: taglio nei n-1 vuoti più lunghi del profilo
    on = np.where(prof)[0]; gaps = []
    for a, b in zip(on[:-1], on[1:]):
        if b - a > 1: gaps.append((b - a, a, b))
    cuts = sorted(sorted(gaps, reverse=True)[:n - 1], key=lambda g: g[1])
    edges = [on[0]] + [x for g in cuts for x in (g[1] + 1, g[2])] + [on[-1] + 1]
    return [edges[i:i + 2] for i in range(0, len(edges), 2)]

def cut(path, rows):
    im = alpha(path); A = np.asarray(im)[:, :, 3] > 0
    frames = []
    for y0, y1 in split(A.sum(1) > 2, rows):
        band = A[y0:y1]
        for x0, x1 in split(band.sum(0) > 1, 4):
            sub = band[:, x0:x1]; ys = np.where(sub.any(1))[0]
            frames.append(im.crop((x0, y0 + ys[0], x1, y0 + ys[-1] + 1)))
    return frames

# per foglio: altezza in gioco della posa ferma (px del fondale) e, posa per posa, nome e verso (R destra, L sinistra)
SHEETS = {
 'nonna':    (205, 'idle R,w1 R,w2 R,w3 R, bidle R,b1 R,b2 R,b3 R, reach R,bend L,bag R,jump R, scale L,box R,win R,lose R'),
 'baffi':    (250, 'idle R,w1 R,w2 R,w3 R, bidle R,b1 L,-,b3 R, think L,grab L,-,-'),
 'mamma':    (245, 'idle L,w1 R,w2 R,w3 R, -,b1 R,b2 R,b3 R, list R,point R,-,scold R'),
 'anziano':  (240, 'idle R,w1 R,-,-, bidle R,b1 R,b2 R,b3 R, look L,put L,hat L,cane L'),
 'ragazzo':  (235, 'idle R,w1 R,w2 R,w3 R, bidle R,b1 R,-,b3 R, skid R,grab R,trip R,sorry R'),
 'cassieri': (250, 'f_idle L,f_scan L,f_type L,f_wave L, m_idle L,m_scan L,m_type L,m_wave L'),
 'macellaio': (255, 'idle L,chop L,give L,call L'),
 # fogli con più personaggi: la posa si scrive chi:posa
 'nonna2':   (205, 'nonnac:idle R,nonnac:w1 R,nonnac:w2 R,nonnac:w3 R, nonnac:bidle R,nonnac:b1 R,nonnac:b2 R,nonnac:b3 R, nonna:phone R,nonna:slip R,nonna:watch R,nonna:wait R'),
 'pulizie':  (235, 'idle R,w1 R,w2 R,w3 R, mop1 R,mop2 R,sign R,rest R'),
 'magazziniere': (245, 'idle R,w1 R,w2 R,w3 R, carry R,shelf R,kneel R,thumb R'),
 'clienti2': (245, 'dama:idle R,manager:idle R,studente:idle R,tifoso:idle R, papa:idle R,vecchina:idle R,muratore:idle R,riccia:idle R'),
}
CARTS = ('nonnac:', 'papa:', 'vecchina:', 'muratore:', 'riccia:', 'magazziniere:idle', 'magazziniere:w')  # con carrello: àncora a metà tra piedi e ruote
if __name__ == '__main__':
    out, preview = {}, []
    for name, (h, spec) in SHEETS.items():
        spec = [s.strip() for s in spec.split(',')]; fr = cut(f'kit/pg-{name}.jpg', len(spec) // 4)
        print(name, len(fr), 'pose trovate,', len(spec), 'attese'); assert len(fr) == len(spec)
        first = fr[0].height if name != 'cassieri' else fr[0].height
        k = h / first
        for f, s in zip(fr, spec):
            preview.append((name, s, f))
            if s == '-': continue
            pose, side = s.split()
            if side == 'L': f = f.transpose(Image.FLIP_LEFT_RIGHT)
            f = f.resize((max(1, round(f.width * k)), max(1, round(f.height * k))), Image.LANCZOS)
            a = np.asarray(f)[:, :, 3]; bot = a[int(a.shape[0] * .88):]
            xs = np.where(bot.max(0) > 0)[0]
            key = pose if ':' in pose else name + ':' + pose
            ax = (xs[0] + xs[-1]) / 2 if name in ('baffi', 'mamma') or key.startswith(CARTS) or not len(xs) else float(np.median(np.where(bot > 0)[1]))
            out[key] = dict(img=f, ax=round(ax), ay=f.height)
    # impacchetto a scaffale
    W, x, y, rowh, pos = 1400, 0, 0, 0, {}
    for k, v in out.items():
        w, hh = v['img'].size
        if x + w > W: x, y, rowh = 0, y + rowh + 2, 0
        pos[k] = (x, y); x += w + 2; rowh = max(rowh, hh)
    sheet = Image.new('RGBA', (W, y + rowh))
    for k, v in out.items(): sheet.paste(v['img'], pos[k])
    sheet.quantize(256, method=Image.FASTOCTREE, dither=Image.NONE).save('personaggi2.png', optimize=True)  # 256 colori: 3 MB -> 0,7 MB
    json.dump({k: [*pos[k], *v['img'].size, v['ax'], v['ay']] for k, v in out.items()}, open('personaggi2.json', 'w'), separators=(',', ':'))
    # anteprima per controllare versi e tagli
    th = 170; pv = Image.new('RGB', (12 * 130, ((len(preview) + 11) // 12) * (th + 20)), 'white'); d = ImageDraw.Draw(pv)
    for i, (n, s, f) in enumerate(preview):
        t = f.copy(); t.thumbnail((125, th)); X, Y = (i % 12) * 130, (i // 12) * (th + 20)
        pv.paste(t, (X, Y), t); d.text((X, Y + th + 4), n[:4] + ' ' + s, fill='red')
    pv.save(sys.argv[1] if len(sys.argv) > 1 else 'pg-preview.png')
    print(sheet.size)
