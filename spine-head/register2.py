import json,numpy as np
from PIL import Image
exec(open('register.py').read().split('pos={}')[0])
prior={'PG':dict(eyeA=(237,180),browA=(238,150),nose=(186,195),mouthC=(207,215)),
'TG':dict(eyeA=(412,178),eyeB=(475,178),browA=(402,148),browB=(482,145),nose=(434,203),mouthC=(455,220)),
'F':dict(eyeA=(641,178),eyeB=(709,178),browA=(628,145),browB=(718,145),nose=(680,203),mouthC=(680,222)),
'TD':dict(eyeA=(884,178),eyeB=(942,178),browA=(860,145),browB=(945,148),nose=(902,205),mouthC=(895,222)),
'PD':dict(eyeB=(1105,180),browB=(1103,150),nose=(1158,197),mouthC=(1118,218))}
pos=json.load(open('placement.json'))
R=16
for v,d in prior.items():
  for r,(cx,cy) in d.items():
    k=f'{r}_{v}'; w,h=p[k]['w'],p[k]['h']
    reg=(cx-w//2-R,cy-h//2-R,cx+w-w//2+R,cy+h-h//2+R)
    x,y,e=match(k,reg); pos[k]=[int(x),int(y)]; print(k,x-(cx-w//2),y-(cy-h//2),round(e,3))
for k,v in p.items():
  r=v['row']
  if r=='lid':
    e=k.replace('lid','eye'); ex,ey=pos[e]; ev=p[e]
    pos[k]=[int(ex+ev['w']/2-v['w']/2), int(ey+ev['h']*0.30-v['h']/2)]
  if r=='mouthO':
    c='mouthC_'+v['view']; cx,cy=pos[c]; cv=p[c]
    pos[k]=[int(cx+cv['w']/2-v['w']/2), int(cy-3)]
json.dump(pos,open('placement.json','w'),indent=1)
# composite check
order=['base','eyeA','eyeB','browA','browB','nose','mouthC','hair']
W=Image.new('RGBA',(1199,560),(255,255,255,255))
src=Image.open('/root/.claude/uploads/dd7f8791-9470-5f94-8946-57cf04bd5098/1dbd80dc-image.png').crop((0,40,1199,290))
W.alpha_composite(src,(0,0))
for k in [f'{r}_{v}' for v in prior for r in order]:
  if k in pos: W.alpha_composite(Image.open(f'images/{k}.png'),(pos[k][0],pos[k][1]-40+260))
W.convert('RGB').save('/tmp/claude-0/-home-user-azure-sdk-for-go/dd7f8791-9470-5f94-8946-57cf04bd5098/scratchpad/cmp.png')
