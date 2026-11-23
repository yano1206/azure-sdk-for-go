"""Rasterises the per-frame quads produced by verify_runtime.mjs (official spine-core runtime) into PNG frames."""
import json,sys,numpy as np
from PIL import Image,ImageDraw
frames=json.load(open(sys.argv[1])); out=sys.argv[2]
S=1.8; W,H=480,480; CX,CY=W/2,H-40; SS=2
ims={}
for f,items in enumerate(frames):
  can=Image.new('RGBA',(W*SS,H*SS),(238,242,248,255))
  for name,*v in items:
    im=ims.setdefault(name,Image.open(f'{sys.argv[3]}/{name}.png').convert('RGBA'))
    w,h=im.size
    P=[(CX*SS+v[i]*S*SS, CY*SS-v[i+1]*S*SS) for i in range(0,8,2)]  # BL, UL, UR, BR
    # affine src->dst: (0,h)->P0, (0,0)->P1, (w,0)->P2
    o=np.array(P[1]); ax=(np.array(P[2])-o)/w; ay=(np.array(P[0])-o)/h
    M=np.array([[ax[0],ay[0],o[0]],[ax[1],ay[1],o[1]],[0,0,1]]); Mi=np.linalg.inv(M)
    can.alpha_composite(im.transform(can.size,Image.AFFINE,tuple(Mi[:2].ravel()),Image.BICUBIC))
  can=can.resize((W,H),Image.LANCZOS)
  ImageDraw.Draw(can).text((8,H-16),f'frame {f:03d}  t={f/30:.2f}s',fill=(120,120,140,255))
  can.convert('RGB').save(f'{out}/f{f:03d}.png')
