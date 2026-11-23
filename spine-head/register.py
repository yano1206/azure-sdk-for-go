import json,numpy as np
from PIL import Image
from scipy.signal import fftconvolve
p=json.load(open('parts_sheet.json'))
sheet=np.array(Image.open('/root/.claude/uploads/dd7f8791-9470-5f94-8946-57cf04bd5098/1dbd80dc-image.png')).astype(float)/255
colx=[160,370,580,795,1000,1199]; views=['PG','TG','F','TD','PD']
def match(key,region):
  x0,y0,x1,y1=region
  I=sheet[y0:y1,x0:x1,:3]*(sheet[y0:y1,x0:x1,3:]>0.4)
  T=np.array(Image.open(f'images/{key}.png')).astype(float)/255
  M=(T[...,3]>0.6).astype(float); T=T[...,:3]
  Mf=M[::-1,::-1]
  ssd=np.zeros((y1-y0-T.shape[0]+1,x1-x0-T.shape[1]+1))
  for c in range(3):
    Ic=I[...,c]
    t1=fftconvolve(Ic**2,Mf,'valid'); t2=fftconvolve(Ic,(M*T[...,c])[::-1,::-1],'valid')
    ssd+=t1-2*t2+(M*T[...,c]**2).sum()
  iy,ix=np.unravel_index(np.argmin(ssd),ssd.shape)
  return x0+ix,y0+iy,ssd.min()/M.sum()
pos={}
for k,v in p.items():
  if v['row']=='preview': continue
  vi=views.index(v['view']); cx0,cx1=colx[vi],colx[vi+1]
  if v['row'] in ('lid','mouthO'): continue
  if v['row']=='base': reg=(cx0,40,cx1,290)
  else: reg=(cx0,40,cx1,290)
  x,y,e=match(k,reg); pos[k]=[int(x),int(y)]; print(k,x,y,round(e,4))
# lids: over the eye, aligned on eye top (lid arc sits on upper eye edge)
for k,v in p.items():
  r=v['row']
  if r=='lid':
    e=k.replace('lid','eye'); ex,ey=pos[e]; ev=p[e]
    pos[k]=[int(ex+ev['w']/2-v['w']/2), int(ey+ev['h']*0.42-v['h']/2)]
  if r=='mouthO':
    c='mouthC_'+v['view']; cx,cy=pos[c]; cv=p[c]
    pos[k]=[int(cx+cv['w']/2-v['w']/2), int(cy-2)]
json.dump(pos,open('placement.json','w'),indent=1)
