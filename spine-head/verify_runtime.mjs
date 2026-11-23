// Loads export/head.json + head.atlas with the official spine-core 4.2 runtime,
// plays 'head_turn' frame by frame (30 fps) and dumps world-space quads for each visible attachment.
import fs from 'fs'; import path from 'path';
import * as spine from '@esotericsoftware/spine-core';
const dir=process.argv[2];
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(dir,'head.atlas'),'utf8'));
for (const p of atlas.pages) p.setTexture(new (class extends spine.Texture{setFilters(){} setWraps(){} dispose(){}})({width:p.width,height:p.height}));
const json=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas));
const data=json.readSkeletonData(JSON.parse(fs.readFileSync(path.join(dir,'head.json'),'utf8')));
const sk=new spine.Skeleton(data); const st=new spine.AnimationState(new spine.AnimationStateData(data));
const anim=data.findAnimation('head_turn'); st.setAnimation(0,'head_turn',true);
console.error(`bones=${data.bones.length} slots=${data.slots.length} anim=${anim.name} duration=${anim.duration}s`);
const frames=[]; const v=new Float32Array(8);
sk.setToSetupPose(); sk.updateWorldTransform(spine.Physics.update);
for(let f=0;f<240;f++){
  if(f>0) st.update(1/30); st.apply(sk); sk.updateWorldTransform(spine.Physics.update);
  const items=[];
  for(const s of sk.drawOrder){const a=s.getAttachment(); if(!(a instanceof spine.RegionAttachment)) continue;
    a.computeWorldVertices(s,v,0,2); items.push([a.name,...Array.from(v).map(x=>+x.toFixed(2))]);}
  frames.push(items);
}
fs.writeFileSync(process.argv[3],JSON.stringify(frames)); console.error('frames',frames.length);
