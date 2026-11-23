# Toglie lo sfondo bianco dai fogli AI: è sfondo tutto ciò che è chiaro e poco colorato E tocca il bordo.
import sys, numpy as np
from PIL import Image
def alpha(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    mx, mn = a.max(2), a.min(2)
    bgl = (mn > 240) & (mx - mn < 14)          # solo il bianco del foglio
    m = np.zeros_like(bgl); m[0,:]=m[-1,:]=m[:,0]=m[:,-1]=True; m &= bgl
    while True:
        d = m.copy(); d[1:]|=m[:-1]; d[:-1]|=m[1:]; d[:,1:]|=m[:,:-1]; d[:,:-1]|=m[:,1:]; d &= bgl
        if (d == m).all(): break
        m = d
    rgba = np.dstack([a, np.where(m, 0, 255)]).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')
if __name__ == '__main__':
    alpha(sys.argv[1]).save(sys.argv[2])
