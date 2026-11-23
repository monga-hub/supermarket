# Compone il fondale pulito: sceglie per ogni cliente la versione migliore e ricostruisce l'angolo del banco frutta.
import sys, numpy as np
from PIL import Image, ImageDraw
sys.argv=[sys.argv[0]]+sys.argv[1:]
c2=np.asarray(Image.open(sys.argv[1]).convert('RGB')).copy(); c3=np.asarray(Image.open(sys.argv[2]).convert('RGB'))
H,W,_=c2.shape
def poly(P):
  m=Image.new('L',(W,H),0);ImageDraw.Draw(m).polygon(P,fill=255);return np.asarray(m)>0
from pulisci_masks import P
for k in ('p5','p7'):
  m=poly(P[k]); m=np.asarray(Image.fromarray(m.astype(np.uint8)*255).resize((W,H)))>0
  big=m.copy()
  for dy in range(-4,5):
    for dx in range(-4,5): big|=np.roll(np.roll(m,dy,0),dx,1)
  c2[big]=c3[big]
# fianco del banco: banda tra y_top e y_bot, prolungata copiando il legno a passo 40 lungo l'asse
yt=lambda x:1165-0.52*(x-1420); yb=lambda x:1230-0.52*(x-1420)
out=c2.copy()
for x in range(1462,1582):
  k=int(np.ceil((x-1455)/40))*40; sx=x-k; d=int(round(0.52*k))
  for y in range(int(yt(x))-2,int(yb(x))+1):
    out[y,x]=c2[y+d,sx]
for x in range(1576,1584):                      # spigolo destro scuro
  for y in range(int(yt(x))-2,int(yb(x))+1): out[y,x]=(58,32,16)
for x in range(1462,1584):                      # bordo inferiore scuro + ombra sul pavimento
  y=int(yb(x)); out[y-1:y+2,x]=(58,32,16); out[y+2:y+9,x]=(out[y+2:y+9,x]*0.82).astype(np.uint8)
for (x0,y0,x1,y1) in ((1436,824,1472,868),(1488,814,1528,852)):   # ruote del carrello rimaste sotto lo scaffale
  src=out[y0:y1,x0+116:x1+116].astype(float)
  k=out[y1:y1+6,x0:x1].reshape(-1,3).astype(float).mean(0)/out[y1:y1+6,x0+116:x1+116].reshape(-1,3).astype(float).mean(0)
  out[y0:y1,x0:x1]=np.clip(src*k,0,255).astype(np.uint8)
from PIL import ImageFilter                     # ombra morbida sotto lo scaffale: nasconde le giunture
sm=Image.new('L',(W,H),0); ImageDraw.Draw(sm).polygon([(1425,812),(1535,800),(1535,858),(1480,872),(1425,880)],fill=255)
sm=np.asarray(sm.filter(ImageFilter.GaussianBlur(10))).astype(float)/255
out=(out.astype(float)*(1-0.16*sm[...,None])).astype(np.uint8)
Image.fromarray(out).save(sys.argv[3],quality=95)
