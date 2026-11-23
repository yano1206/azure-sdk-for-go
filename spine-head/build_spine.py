"""Builds head.json (Spine 4.2 skeleton + 'head_turn' animation) and head.atlas/head.png from images/ and layout.json."""
import json,numpy as np
from PIL import Image
L=json.load(open('layout.json')); VIEWS=['PG','TG','F','TD','PD']; FPS=30
# ---- neck pivot per view: bottom-centre of the neck on base_<view>
pivot={}
for v in VIEWS:
  im=np.array(Image.open(f'images/base_{v}.png'))[...,3]>128
  ys=np.nonzero(im.any(1))[0]; yb=ys.max(); xs=np.nonzero(im[yb-6])[0]
  cx,cy,_=L[f'base_{v}']; h,w=im.shape
  pivot[v]=(cx-w/2+(xs.min()+xs.max())/2, cy-h/2+yb-3)
def sp(k):  # attachment centre in skeleton space (Y up, origin = neck base)
  cx,cy,s=L[k]; v=k.split('_')[1]; px,py=pivot[v]; return cx-px, py-cy, s
BONES=[dict(name='root'),
 dict(name='neck',parent='root',x=0,y=0,length=30,rotation=90),
 dict(name='head',parent='neck',x=30,y=0,length=150,rotation=0),
 dict(name='face',parent='head',x=95,y=0),
 dict(name='eyes',parent='face'),dict(name='brows',parent='face'),
 dict(name='nose',parent='face'),dict(name='mouth',parent='face'),
 dict(name='hair',parent='head',x=150,y=0)]
# world positions of bones (setup: neck/head rotated 90 -> local x = world y)
BW={'root':(0,0),'neck':(0,0),'head':(0,30),'face':(0,125),'eyes':(0,125),'brows':(0,125),'nose':(0,125),'mouth':(0,125),'hair':(0,180)}
BROT={'root':0}  # all others world-rot 90
SLOTS=[('base','head','base'),('eyeA','eyes','eyeA'),('lidA','eyes',None),('eyeB','eyes','eyeB'),('lidB','eyes',None),
 ('browA','brows','browA'),('browB','brows','browB'),('nose','nose','nose'),('mouth','mouth','mouthC'),('hair','hair','hair')]
SLOT_PREFIX={'base':['base'],'eyeA':['eyeA'],'lidA':['lidA'],'eyeB':['eyeB'],'lidB':['lidB'],'browA':['browA'],'browB':['browB'],'nose':['nose'],'mouth':['mouthC','mouthO'],'hair':['hair']}
skin={}
for sname,bone,_ in SLOTS:
  d={}
  for pre in SLOT_PREFIX[sname]:
    for v in VIEWS:
      k=f'{pre}_{v}'
      if k not in L: continue
      x,y,s=sp(k); bx,by=BW[bone]; im=Image.open(f'images/{k}.png')
      dx,dy=x-bx,y-by
      if bone!='root': dx,dy=dy,-dx   # into bone-local frame rotated 90deg
      d[k]=dict(x=round(dx,2),y=round(dy,2),rotation=-90,scaleX=s,scaleY=s,width=im.width,height=im.height)
  skin[sname]=d
slots=[dict(name=n,bone=b,**({'attachment':f'{a}_F'} if a else {})) for n,b,a in SLOTS]
# ---------------- animation ----------------
def ease(t0,v0,t1,v1,k=0.38):  # Spine 4.x bezier: absolute (time,value) control points, one set per channel
  dt=t1-t0; return [t0+dt*k,v0,t1-dt*k,v1]
def timeline(keys,chan=('value',)):
  """keys: list of (frame, values-tuple, mode) mode in 'ease','linear','stepped'"""
  out=[]
  for i,(f,vals,mode) in enumerate(keys):
    e={'time':round(f/FPS,4)}
    for c,v in zip(chan,vals): e[c]=v
    if i+1<len(keys):
      f1,v1,_=keys[i+1]
      if mode=='stepped': e['curve']='stepped'
      elif mode=='ease':
        cv=[]
        for a,b in zip(vals,v1): cv+=ease(f/FPS,a,f1/FPS,b)
        e['curve']=[round(x,4) for x in cv]
    out.append(e)
  return out
# view schedule (frames). Turns: left 30->44, back 78->92, right 120->134, back 165->179
SW=[(0,'F'),(36,'TG'),(44,'PG'),(84,'TG'),(92,'F'),(126,'TD'),(134,'PD'),(171,'TD'),(179,'F')]
BLINKS=[21,64,108,152,226]; BLINK_LEN=4
SMILE=(192,218)
def view_at(f): return [v for t,v in SW if t<=f][-1]
def state(f):
  v=view_at(f); blink=any(b<=f<b+BLINK_LEN for b in BLINKS)
  st={}
  for sname,_,_ in SLOTS:
    if sname in('eyeA','eyeB'): k=None if blink else f'{sname}_{v}'
    elif sname in('lidA','lidB'): k=f'{sname}_{v}' if blink else None
    elif sname=='mouth': k=f"{'mouthO' if SMILE[0]<=f<SMILE[1] else 'mouthC'}_{v}"
    else: k=f'{sname}_{v}'
    st[sname]=k if (k and k in L) else None
  return st
att={}
prev=None
for f in range(0,240):
  s=state(f)
  for n,k in s.items():
    if prev is None or prev[n]!=k: att.setdefault(n,[]).append({'time':round(f/FPS,4),'name':k})
  prev=s
slots_anim={n:{'attachment':a} for n,a in att.items()}
# head tilt / drift. dir: -1 = turning to image-left
turns=[(30,44,-1,'out'),(78,92,+1,'back'),(120,134,+1,'out'),(165,179,-1,'back')]
rot=[(0,(0,),'ease')]; tx=[(0,(0,0),'ease')]; sc=[(0,(1,1),'ease')]
face=[(0,(0,0),'ease')]; hair=[(0,(0,),'ease')]
head_pose={'F':(0,0),'PG':(4,-5),'PD':(-4,5)}  # (tilt deg, x shift) held in profile
cur='F'
for a,b,d,kind in turns:
  target='PG' if (kind=='out' and d<0) else 'PD' if kind=='out' else 'F'
  r0,x0=head_pose[cur]; r1,x1=head_pose[target]
  rot+=[(a-6,(r0,),'ease'),(a,(r0-2*d*-1*0+(-d)*1.5,),'ease'),(b,(r1-d*1.5,),'ease'),(b+8,(r1,),'ease')]
  tx+=[(a-6,(x0,0),'ease'),(a+ (b-a)//2,(x0+(x1-x0)*0.6,-2.5),'ease'),(b,(x1+d*1.5,0),'ease'),(b+8,(x1,0),'ease')]
  for sw in [t for t,_ in SW if a<=t<=b]:
    sc+=[(sw-4,(1,1),'ease'),(sw,(0.965,1.012),'ease'),(sw+5,(1,1),'ease')]
    face+=[(sw-5,(0,0),'ease'),(sw-1,(d*4,0),'stepped'),(sw,(-d*3,0),'ease'),(sw+5,(0,0),'ease')]
  hair+=[(a,(0,),'ease'),(b-2,(d*2.5,),'ease'),(b+6,(-d*3.5,),'ease'),(b+14,(d*1.2,),'ease'),(b+22,(0,),'ease')]
  cur=target
# smile: small lift + tilt, hair bounce
rot+=[(SMILE[0]-6,(0,),'ease'),(SMILE[0]+4,(3,),'ease'),(SMILE[1]-4,(2,),'ease'),(SMILE[1]+8,(0,),'ease'),(239,(0,),'ease'),(240,(0,),'linear')]
tx+=[(SMILE[0]-6,(0,0),'ease'),(SMILE[0]+3,(0,4),'ease'),(SMILE[0]+9,(0,2),'ease'),(SMILE[1]+6,(0,0),'ease'),(240,(0,0),'linear')]
sc+=[(SMILE[0]-2,(1,1),'ease'),(SMILE[0]+2,(1.025,0.975),'ease'),(SMILE[0]+7,(0.99,1.02),'ease'),(SMILE[0]+12,(1,1),'ease'),(240,(1,1),'linear')]
hair+=[(SMILE[0]+2,(0,),'ease'),(SMILE[0]+7,(-2,),'ease'),(SMILE[0]+13,(1.2,),'ease'),(SMILE[0]+20,(0,),'ease'),(240,(0,),'linear')]
face+=[(240,(0,0),'linear')]
# brows raise for smile and at each turn start
brow=[(0,(0,0),'ease')]
for a,b,d,k in turns: brow+=[(a-4,(0,0),'ease'),(a+3,(0,2.5),'ease'),(b+6,(0,0),'ease')]
brow+=[(SMILE[0]-3,(0,0),'ease'),(SMILE[0]+3,(0,4),'ease'),(SMILE[1]-2,(0,3),'ease'),(SMILE[1]+6,(0,0),'ease'),(240,(0,0),'linear')]
mouth=[(0,(1,1),'ease'),(SMILE[0]-1,(1,1),'ease'),(SMILE[0],(0.85,0.8),'ease'),(SMILE[0]+4,(1.06,1.08),'ease'),(SMILE[0]+9,(1,1),'ease'),(SMILE[1]-1,(1,1),'ease'),(SMILE[1],(1.04,0.9),'ease'),(SMILE[1]+4,(1,1),'ease'),(240,(1,1),'linear')]
# idle breathing-ish micro sway on hair
def clean(keys):  # sort, drop duplicates in time (keep last)
  d={}
  for k in keys: d[k[0]]=k
  return [d[f] for f in sorted(d)]
# neck/head transforms are in bone-local space rotated 90deg: local x = world up, local y = world left
def to_local(keys): return [(f,(v[1],-v[0]),m) for f,v,m in keys]
anim={'slots':slots_anim,'bones':{
 'head':{'rotate':timeline(clean(rot)),'scale':timeline(clean([(f,(v[1],v[0]),m) for f,v,m in sc]),('x','y'))},
 'neck':{'translate':timeline(clean(to_local(tx)),('x','y'))},
 'face':{'translate':timeline(clean(to_local(face)),('x','y'))},
 'brows':{'translate':timeline(clean(to_local(brow)),('x','y'))},
 'mouth':{'scale':timeline(clean([(f,(v[1],v[0]),m) for f,v,m in mouth]),('x','y'))},
 'hair':{'rotate':timeline(clean(hair))}}}
sk={'skeleton':{'hash':'headturn01','spine':'4.2.43','x':-130,'y':-10,'width':260,'height':260,'fps':FPS,'images':'./images/','audio':''},
 'bones':BONES,'slots':slots,'skins':[{'name':'default','attachments':skin}],'animations':{'head_turn':anim}}
json.dump(sk,open('head.json','w'),indent=1)
# ---- atlas (libGDX/Spine 4 text format)
names=sorted(k for d in skin.values() for k in d)
ims={n:Image.open(f'images/{n}.png') for n in names}
W=1024; x=y=rowh=0; P=2; pos={}
for n in sorted(names,key=lambda n:-ims[n].height):
  im=ims[n]
  if x+im.width+P>W: x=0;y+=rowh+P;rowh=0
  pos[n]=(x,y); x+=im.width+P; rowh=max(rowh,im.height)
H=1<<int(np.ceil(np.log2(y+rowh)))
page=Image.new('RGBA',(W,H),(0,0,0,0))
for n,(px,py) in pos.items(): page.paste(ims[n],(px,py))
page.save('export/head.png')
with open('export/head.atlas','w') as f:
  f.write(f'head.png\nsize:{W},{H}\nfilter:Linear,Linear\npma:false\n')
  for n in names:
    px,py=pos[n]; w,h=ims[n].size; f.write(f'{n}\nbounds:{px},{py},{w},{h}\n')
print('slots',len(slots),'attachments',len(names),'pivots',{k:(round(a),round(b)) for k,(a,b) in pivot.items()})
