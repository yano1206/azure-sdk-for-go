import json,numpy as np
from PIL import Image
from scipy.signal import fftconvolve
p=json.load(open('parts_sheet.json'))
SRC='/root/.claude/uploads/dd7f8791-9470-5f94-8946-57cf04bd5098/1dbd80dc-image.png'
sheet=np.array(Image.open(SRC)).astype(float)/255
src=Image.open(SRC)
def match(img,region):
  x0,y0,x1,y1=region
  I=sheet[y0:y1,x0:x1,:3]*(sheet[y0:y1,x0:x1,3:]>0.4)
  T=np.array(img).astype(float)/255
  M=(T[...,3]>0.6).astype(float); T=T[...,:3]
  if I.shape[0]<T.shape[0] or I.shape[1]<T.shape[1]: return None
  ssd=0
  for c in range(3):
    Ic=I[...,c]
    ssd=ssd+fftconvolve(Ic**2,M[::-1,::-1],'valid')-2*fftconvolve(Ic,(M*T[...,c])[::-1,::-1],'valid')+(M*T[...,c]**2).sum()
  iy,ix=np.unravel_index(np.argmin(ssd),ssd.shape)
  return x0+ix,y0+iy,ssd.min()/M.sum()
prior={'PG':dict(eyeA=(237,180),browA=(238,150),nose=(186,195),mouthC=(207,215)),
'TG':dict(eyeA=(412,178),eyeB=(475,178),browA=(402,148),browB=(482,145),nose=(434,203),mouthC=(455,220)),
'F':dict(eyeA=(641,178),eyeB=(709,178),browA=(628,145),browB=(718,145),nose=(680,203),mouthC=(680,222)),
'TD':dict(eyeA=(884,178),eyeB=(942,178),browA=(860,145),browB=(945,148),nose=(902,205),mouthC=(895,222)),
'PD':dict(eyeB=(1105,180),browB=(1103,150),nose=(1158,197),mouthC=(1118,218))}
R=22; out={}
for v,d in prior.items():
  for r,(cx,cy) in d.items():
    k=f'{r}_{v}'; im=Image.open(f'images/{k}.png'); best=None
    for s in np.arange(0.35,0.86,0.025):
      t=im.resize((max(3,round(im.width*s)),max(3,round(im.height*s))),Image.LANCZOS)
      reg=(cx-t.width//2-R,cy-t.height//2-R,cx+t.width-t.width//2+R,cy+t.height-t.height//2+R)
      m=match(t,reg)
      if m and (best is None or m[2]<best[3]): best=(m[0],m[1],s,m[2],t.width,t.height)
    x,y,s,e,w,h=best
    out[k]=dict(cx=x+w/2,cy=y+h/2,s=round(float(s),3)); print(k,round(s,3),round(e,3))
json.dump(out,open('match.json','w'),indent=1)
