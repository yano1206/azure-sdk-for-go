# Final layout: centre (sheet px) + scale for each attachment, per view. Edit 'prior' to tweak.
import json
from PIL import Image
S=0.62
m=json.load(open('match.json')); p=json.load(open('parts_sheet.json'))
exec(open('register3.py').read().split('prior=')[1].split('\nR=')[0].join(['prior=','\n']))
OV=json.load(open('overrides.json')) if __import__('os').path.exists('overrides.json') else {}
L={}
for v,d in prior.items():
  for r,(cx,cy) in d.items():
    k=f'{r}_{v}'
    if r.startswith('eye') and m[k]['cx'] and abs(m[k]['s']-S)<0.08: cx,cy=m[k]['cx'],m[k]['cy']
    cx,cy=OV.get(k,(cx,cy)); L[k]=[cx,cy,S]
  # lids over eyes, open mouth from closed mouth
  for r in ('A','B'):
    if f'eye{r}_{v}' in L:
      ex,ey,_=L[f'eye{r}_{v}']; eh=p[f'eye{r}_{v}']['h']*S
      L[f'lid{r}_{v}']=list(OV.get(f'lid{r}_{v}',(ex,ey-eh*0.05)))+[S]
  mx,my,_=L[f'mouthC_{v}']; L[f'mouthO_{v}']=list(OV.get(f'mouthO_{v}',(mx,my+p[f'mouthO_{v}']['h']*S*0.35)))+[S]
  for r in ('base','hair'):
    k=f'{r}_{v}'; pp=p[k]; pos=json.load(open('placement.json'))[k]
    L[k]=[pos[0]+pp['w']/2,pos[1]+pp['h']/2,1.0]
json.dump(L,open('layout.json','w'),indent=1)
def comp(v,keys):
  W=Image.new('RGBA',(215,260),(255,255,255,255)); x0=[160,370,580,795,1000][['PG','TG','F','TD','PD'].index(v)]
  for k in keys:
    if k not in L: continue
    cx,cy,s=L[k]; im=Image.open(f'images/{k}.png'); im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS)
    W.alpha_composite(im,(round(cx-im.width/2-x0),round(cy-im.height/2-30)))
  return W
if __name__=='__main__':
  src=Image.open('/root/.claude/uploads/dd7f8791-9470-5f94-8946-57cf04bd5098/1dbd80dc-image.png')
  out=Image.new('RGB',(215*5,260*3),'white')
  for i,v in enumerate(['PG','TG','F','TD','PD']):
    x0=[160,370,580,795,1000][i]; c=Image.new('RGBA',(215,260),'white'); c.alpha_composite(src.crop((x0,30,x0+215,290)))
    out.paste(c.convert('RGB'),(215*i,0))
    o=['base','eyeA','eyeB','browA','browB','nose','mouthC','hair']
    out.paste(comp(v,[f'{r}_{v}' for r in o]).convert('RGB'),(215*i,260))
    o=['base','lidA','lidB','browA','browB','nose','mouthO','hair']
    out.paste(comp(v,[f'{r}_{v}' for r in o]).convert('RGB'),(215*i,520))
  out.save('/tmp/claude-0/-home-user-azure-sdk-for-go/dd7f8791-9470-5f94-8946-57cf04bd5098/scratchpad/cmp.png')
