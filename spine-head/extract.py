import sys,json,numpy as np
from PIL import Image
from scipy import ndimage
src=sys.argv[1]
a=np.array(Image.open(src)).astype(np.uint8)
al=a[...,3]
clean=a.copy(); clean[...,3]=np.where(al>200,255,np.where(al>100,al,0))  # keep AA edge, drop red noise
mask=al>100
rows={'preview':(54,270),'base':(293,481),'hair':(508,675),'eye':(700,772),'lid':(834,853),'brow':(911,940),'nose':(995,1040),'mouthC':(1104,1134),'mouthO':(1201,1268)}
colx=[160,370,580,795,1000,1199]; views=['PG','TG','F','TD','PD']
parts={}
for r,(y0,y1) in rows.items():
  y0-=4;y1+=4
  lab,n=ndimage.label(mask[y0:y1,160:],structure=np.ones((3,3)))
  objs=ndimage.find_objects(lab)
  comps=[]
  for i,s in enumerate(objs):
    size=(lab[s]==i+1).sum()
    if size<25: continue
    cx=(s[1].start+s[1].stop)/2+160
    comps.append((cx,i+1,s,size))
  for vi,v in enumerate(views):
    cs=[c for c in comps if colx[vi]<=c[0]<colx[vi+1]]
    # group: biggest pieces; small fragments (<3% of max) dropped as parasites
    if not cs: print('none',r,v);continue
    mx=max(c[3] for c in cs); cs=[c for c in cs if c[3]>0.03*mx]
    if r in('eye','lid','brow') and v in('TG','F','TD'):
      cs=sorted(cs,key=lambda c:-c[3])[:2]; groups=[[c] for c in sorted(cs,key=lambda c:c[0])]
      names=[r+'A',r+'B']   # A = image-left, B = image-right
    else:
      groups=[cs]; names=[r if r not in('eye','lid','brow') else r+('A' if v=='PG' else 'B')]
    for nm,g in zip(names,groups):
      m=np.zeros_like(mask[y0:y1,160:])
      for c in g: m|=lab==c[1]
      m=ndimage.binary_dilation(m,iterations=2)
      ys,xs=np.nonzero(m); bx0,bx1,by0,by1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
      crop=clean[y0+by0:y0+by1,160+bx0:160+bx1].copy()
      crop[...,3]=np.where(m[by0:by1,bx0:bx1],crop[...,3],0)
      key=f'{nm}_{v}'
      Image.fromarray(crop).save(f'images/{key}.png')
      parts[key]=dict(x=int(160+bx0),y=int(y0+by0),w=int(bx1-bx0),h=int(by1-by0),view=v,row=r)
json.dump(parts,open('parts_sheet.json','w'),indent=1)
print(len(parts),sorted(parts))
