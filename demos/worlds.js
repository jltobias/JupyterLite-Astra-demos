import * as THREE from './vendor/three.module.min.js';

// Original teaching scenes. No remote textures, maps, fonts, telemetry, or API calls.
const $ = id => document.getElementById(id);
let coastlines=[];
try {
  const response=await fetch('./data/ne_110m_land.geojson');
  if(!response.ok)throw new Error('Bundled land data could not be loaded');
  const data=await response.json();
  for(const feature of data.features){const g=feature.geometry;const polygons=g.type==='Polygon'?[g.coordinates]:g.coordinates;for(const polygon of polygons)coastlines.push(...polygon);}
} catch(error) { console.warn(error.message); }
const catalog = {
  terrain: { title:'Terrain & water', tag:'CONNECTED WATER / SYNTHETIC TERRAIN', notebook:'07_terrain_water', source:'tidal-garden-ocean-guide',
    question:'Which valleys connect to the sea as the water rises?', p:['Water elevation',-50,350,5,80,' m'], s:['Vertical exaggeration',.5,3,.1,1.5,'×'],
    explanation:'A sampled height field becomes a colored mesh. Blue water occupies low cells connected to the boundary through four neighbors. The slider is a static water level, not a flood prediction. Vertical exaggeration changes the display, not the elevations.',
    connection:'Compare the contour map, slope field and connected-water algorithm in notebook 07. Inspired by Sonia’s Tidal Garden Ocean Guide.' },
  city: { title:'Procedural city', tag:'FOOTPRINTS → EXTRUSIONS / SYNTHETIC CITY', notebook:'08_neighborhood_3d', source:'seoul-3d-atlas',
    question:'How do building height and sun angle change the street shadows?', p:['Building height',.5,2,.05,1,'×'], s:['Sun elevation',10,80,1,40,'°'],
    explanation:'A repeated street grid and height rules generate this invented neighborhood. The renderer casts directional-light shadows. Sun elevation is chosen directly; it is not calculated from a real place or date. The central green space gives a stable scale reference.',
    connection:'Notebook 08 connects coordinates, footprints and GeoJSON; notebook 15 explains shadow geometry. Inspired by synabreu’s Seoul 3D Atlas and Pietro Schirano’s Map Pin to 3D Neighborhood.' },
  globe: { title:'Globe & routes', tag:'SPHERICAL GEOMETRY / NEW YORK → TOKYO', notebook:'06_globe_projections', source:'equal-earth-map',
    question:'Why does a shortest spherical route bend on a flat map?', p:['Route progress',0,100,1,35,'%'], s:['Grid opacity',.1,.9,.05,.4,''], motion:true,
    explanation:'Made with Natural Earth: the bundled public-domain land outlines are generalized at 1:110 million scale. The graticule shows longitude and latitude. A great-circle arc links rounded New York and Tokyo coordinates. Lines are lifted slightly for visibility; distance uses a 6,371 km sphere.',
    connection:'Compare Mercator and Equal Earth, then derive the arc in notebook 06. Inspired by stevwang.dev’s Equal Earth Map.' },
  ocean: { title:'Ocean in motion', tag:'WAVE SUPERPOSITION / DIMENSIONLESS MODEL', notebook:'10_ocean_flow', source:'sunwake-sailing-game',
    question:'If wave amplitude doubles, must wave speed double too?', p:['Wave amplitude',.2,1.8,.05,1,'×'], s:['Animation speed',.1,2,.1,1,'×'], motion:true,
    explanation:'Three sinusoidal height fields add to form a moving surface. A buoy samples the local height. The horizontal vector field in the notebook is a separate model: these waves do not solve fluid equations or forecast an ocean.',
    connection:'Notebook 10 pairs streamlines, particle animation, integration error and wave surfaces. Inspired by Thomas Ricouard’s Sunwake and ashe’s Navier–Stokes Visual Essay.' },
  voxel: { title:'Voxel island', tag:'HEIGHT FIELD → OCCUPANCY → MATERIAL', notebook:'12_voxel_world', source:'minecraft-style-world',
    question:'What changes when continuous terrain becomes a grid of blocks?', p:['Waterline',1,7,1,3,' voxels'], s:['Terrain relief',.5,1.6,.1,1,'×'],
    explanation:'Integer column heights create a block island. Surface material depends on height above the waterline: rock, grass or sand. The live view draws exposed land cubes and a water plane; notebook 12 counts the full occupied volume.',
    connection:'Double all three dimensions: dense storage grows eightfold. Explore that trade-off in notebook 12. Inspired by Flavio Adamo’s Minecraft-Style World; no game assets are reused.' },
  chaos: { title:'Lorenz attractor', tag:'DETERMINISTIC RULES / SENSITIVE TRAJECTORIES', notebook:'13_lorenz_chaos', source:'lorenz-chaos-explorer',
    question:'Can the same deterministic rules produce very different futures?', p:['Convection parameter ρ',20,40,.5,28,''], s:['Visible trajectory',10,100,1,100,'%'], motion:true,
    explanation:'Two starts differ by only 0.00001. Fourth-order Runge–Kutta integration produces the teal and coral trajectories. Their shared shape does not imply identical timing. Coordinates and time are dimensionless; this is not a weather forecast.',
    connection:'Notebook 13 separates initial-condition sensitivity from numerical step-size error. Inspired by Juy | AI experiments’ Lorenz Chaos Explorer.' }
};
let renderer;
try {
  renderer = new THREE.WebGLRenderer({canvas:$('world'),antialias:true,alpha:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.setClearColor(0x0b1b27,0);
} catch (error) {
  $('world').hidden=true; $('fallback').hidden=false;
  $('metric').textContent='Static learning path available';
}
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42,1,.1,180);
const ambient = new THREE.HemisphereLight(0xcbe9ff,0x344640,2.1); scene.add(ambient);
const sun = new THREE.DirectionalLight(0xffecd6,3.0); sun.position.set(6,10,4); sun.castShadow=true;
sun.shadow.mapSize.set(1024,1024); sun.shadow.camera.left=-10;sun.shadow.camera.right=10;sun.shadow.camera.top=10;sun.shadow.camera.bottom=-10;
sun.shadow.normalBias=.035;scene.add(sun);
const fill = new THREE.DirectionalLight(0x74ccec,1.1);fill.position.set(-6,4,-5);scene.add(fill);
let group = new THREE.Group(); scene.add(group);
let current='terrain',cfg=catalog.terrain,p=80,s=1.5,playing=false,clock=0,lastTime=0,update=()=>{},theta=.65,phi=1.0,radius=17;
const target = new THREE.Vector3(0,0,0);
const mint=0x8ce6c6,coral=0xf4a078;
function material(color,extra={}){return new THREE.MeshStandardMaterial({color,roughness:.72,metalness:.05,...extra});}
function mesh(geometry,mat,x=0,y=0,z=0){const obj=new THREE.Mesh(geometry,mat);obj.position.set(x,y,z);obj.castShadow=true;obj.receiveShadow=true;group.add(obj);return obj;}
function box(w,h,d,color,x=0,y=0,z=0){return mesh(new THREE.BoxGeometry(w,h,d),material(color),x,y,z);}
function line(points,color,opacity=1){const geom=new THREE.BufferGeometry().setFromPoints(points.map(pt=>new THREE.Vector3(...pt)));const obj=new THREE.Line(geom,new THREE.LineBasicMaterial({color,transparent:opacity<1,opacity}));group.add(obj);return obj;}
function grid(size=12,div=12){const obj=new THREE.GridHelper(size,div,0x385e6d,0x203d4a);obj.position.y=-.03;group.add(obj);}
function dispose(){const geometries=new Set(),materials=new Set();group.traverse(o=>{if(o.isInstancedMesh)o.dispose();if(o.geometry)geometries.add(o.geometry);if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>materials.add(m));});for(const g of geometries)g.dispose();for(const m of materials)m.dispose();scene.remove(group);group=new THREE.Group();scene.add(group);update=()=>{};}
function terrainHeight(x,y){return 680*Math.exp(-((x+450)**2+(y-150)**2)/650**2)+440*Math.exp(-((x-550)**2+(y+350)**2)/500**2)-180*Math.exp(-((x+420)**2+(y-130)**2)/150**2)-80;}
function terrain(){
  const n=81,extent=1500,scale=300,verts=[],colors=[],indices=[],heights=[];
  const color=new THREE.Color();
  for(let j=0;j<n;j++)for(let i=0;i<n;i++){
    const x=-extent+2*extent*i/(n-1),y=-extent+2*extent*j/(n-1),h=terrainHeight(x,y);heights.push(h);verts.push(x/scale,h/scale*s,-y/scale);
    if(h<0)color.set(0x597571);else if(h<80)color.set(0xc0bb85);else if(h<330)color.setHSL(.38,.22,.32+(h/330)*.14);else color.setHSL(.13,.12,.46+h/1800);
    colors.push(color.r,color.g,color.b);
    if(i<n-1&&j<n-1){const a=j*n+i;indices.push(a,a+1,a+n,a+1,a+n+1,a+n);}
  }
  const geom=new THREE.BufferGeometry();geom.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));geom.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));geom.setIndex(indices);geom.computeVertexNormals();
  mesh(geom,material(0xffffff,{vertexColors:true,side:THREE.DoubleSide}));
  box(10,.35,10,0x1a3d44,0,-.5,0);
  const wet=new Uint8Array(n*n),queue=[];
  for(let j=0;j<n;j++)for(let i=0;i<n;i++){const k=j*n+i;if((i===0||j===0||i===n-1||j===n-1)&&heights[k]<=p){wet[k]=1;queue.push(k);}}
  for(let q=0;q<queue.length;q++){const k=queue[q],i=k%n,j=Math.floor(k/n);for(const [di,dj] of [[-1,0],[1,0],[0,-1],[0,1]]){const a=i+di,b=j+dj,k2=b*n+a;if(a>=0&&b>=0&&a<n&&b<n&&!wet[k2]&&heights[k2]<=p){wet[k2]=1;queue.push(k2);}}}
  const waterVertices=[],step=10/(n-1),level=p/scale*s+.012;
  for(let j=0;j<n-1;j++)for(let i=0;i<n-1;i++){const k=j*n+i;if(![k,k+1,k+n,k+n+1].every(v=>wet[v]))continue;const x=-5+i*step,z=5-j*step;waterVertices.push(x,level,z,x+step,level,z,x,level,z-step,x+step,level,z,x+step,level,z-step,x,level,z-step);}
  const waterGeometry=new THREE.BufferGeometry();waterGeometry.setAttribute('position',new THREE.Float32BufferAttribute(waterVertices,3));waterGeometry.computeVertexNormals();
  mesh(waterGeometry,material(0x4daec2,{transparent:true,opacity:.72,metalness:.35,side:THREE.DoubleSide})).castShadow=false;
  // Thin horizontal sample lines make the raster structure legible without pretending to be contours.
  for(let j=0;j<n;j+=8){const pts=[];for(let i=0;i<n;i++){const k=j*n+i;pts.push([verts[k*3],verts[k*3+1]+.012,verts[k*3+2]]);}line(pts,0xd6e2ba,.18);}
  $('metric').textContent=`${(queue.length/(n*n)*100).toFixed(1)}% connected water`;
  $('metric-detail').textContent=`81 × 81 samples · elevation ${p} m · ${s.toFixed(1)}× vertical scale`;
}
function city(){
  box(12,.16,12,0x263d45,0,-.15,0);grid(12,15);
  box(4.0,.04,4.0,0x467865,0,-.025,0);
  let count=0,totalHeight=0;
  for(let x=-240;x<=240;x+=80)for(let y=-240;y<=240;y+=80){
    if(Math.abs(x)<90&&Math.abs(y)<90)continue;
    const h=(24+24*(1+Math.sin(x*3.3+y*8.1))/2+90*Math.exp(-(x*x+y*y)/180**2))*p;count++;totalHeight+=h;
    const color=new THREE.Color().setHSL(.46+.06*h/160,.24,.38+.15*h/160);
    box(.96,h/50,.96,color,x/50,h/100,-y/50);
    box(1,.05,1,0xb1d9d5,x/50,h/50+.015,-y/50);
    // Window ribbons follow the same procedural building transform.
    for(let level=.27;level<h/50-.12;level+=.32){box(.985,.035,.985,0x79afa9,x/50,level,-y/50);}
  }
  for(const [x,z] of [[-1,-1],[1,-1],[-1,1],[1,1]]){box(.09,.4,.09,0x876e54,x,.2,z);mesh(new THREE.IcosahedronGeometry(.42,1),material(0x82b585),x,.65,z);}
  const e=THREE.MathUtils.degToRad(s);sun.position.set(10*Math.cos(e)/Math.sqrt(2),10*Math.sin(e),10*Math.cos(e)/Math.sqrt(2));
  $('metric').textContent=`${count} invented buildings`;
  $('metric-detail').textContent=`Mean height ${(totalHeight/count).toFixed(0)} m · sun ${s}° above horizon`;
}
function spherePoint(lon,lat,r=3.7){lon*=Math.PI/180;lat*=Math.PI/180;return new THREE.Vector3(r*Math.cos(lat)*Math.cos(lon),r*Math.sin(lat),-r*Math.cos(lat)*Math.sin(lon));}
function globe(){
  mesh(new THREE.SphereGeometry(3.7,64,48),material(0x15394a,{metalness:.25,roughness:.55}));
  for(const ring of coastlines)line(ring.map(([lon,lat])=>spherePoint(lon,lat,3.735).toArray()),0x9fe4c0,.88);
  for(let lat=-60;lat<=60;lat+=30){const pts=[];for(let lon=-180;lon<=180;lon+=3)pts.push(spherePoint(lon,lat,3.72).toArray());line(pts,0x8ac2c6,s);}
  for(let lon=-180;lon<180;lon+=30){const pts=[];for(let lat=-90;lat<=90;lat+=2)pts.push(spherePoint(lon,lat,3.72).toArray());line(pts,0x8ac2c6,s);}
  const a=spherePoint(-74,40.7,1),b=spherePoint(139.7,35.7,1),angle=Math.acos(a.dot(b));
  const route=t=>a.clone().multiplyScalar(Math.sin((1-t)*angle)).add(b.clone().multiplyScalar(Math.sin(t*angle))).divideScalar(Math.sin(angle)).multiplyScalar(3.77);
  const points=Array.from({length:161},(_,i)=>route(i/160).toArray());line(points,coral);
  for(const pt of [a,b])mesh(new THREE.SphereGeometry(.095,14,12),material(mint),...pt.clone().multiplyScalar(3.77).toArray());
  const marker=mesh(new THREE.SphereGeometry(.13,16,12),new THREE.MeshBasicMaterial({color:0xffe3ae}));marker.position.copy(route(p/100));
  update=(time)=>{const t=(p/100+time*.035)%1;marker.position.copy(route(t));$('metric-detail').textContent=`New York → Tokyo · ${(t*100).toFixed(0)}% of spherical arc`;};
  $('metric').textContent=`${Math.round(6371*angle).toLocaleString()} km great-circle arc`;
  $('metric-detail').textContent=`New York → Tokyo · ${p}% of spherical arc`;
}
function wave(x,y,t){return .25*Math.sin(1.8*x-.9*t)+.12*Math.sin(2.2*y-1.3*t)+.08*Math.sin(x+y-1.8*t);}
function ocean(){
  const geom=new THREE.PlaneGeometry(10,10,70,70);geom.rotateX(-Math.PI/2);
  const obj=mesh(geom,material(0x2793a9,{metalness:.35,roughness:.35,side:THREE.DoubleSide}));obj.castShadow=false;
  box(10,.4,10,0x153b51,0,-.65,0);
  const buoy=mesh(new THREE.SphereGeometry(.17,16,12),material(coral),.8,0,.3);
  const mast=box(.035,.6,.035,0xf1dec7,.8,0,.3);
  const flag=mesh(new THREE.ConeGeometry(.18,.4,3),material(0xf1bf7e));flag.rotation.z=-Math.PI/2;
  update=t=>{const pos=geom.attributes.position;for(let i=0;i<pos.count;i++)pos.setY(i,p*wave(pos.getX(i),pos.getZ(i),t*s));pos.needsUpdate=true;geom.computeVertexNormals();const h=p*wave(.8,.3,t*s);buoy.position.y=h+.09;mast.position.y=h+.35;flag.position.set(1,h+.53,.3);};update(0);
  $('metric').textContent='Three waves. One surface.';
  $('metric-detail').textContent=`Amplitude ×${p.toFixed(2)} · chosen frequencies unchanged`;
}
function voxel(){
  const n=22,unit=.43,heights=[];
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){const u=(i-n/2)/(n/2),v=(j-n/2)/(n/2);heights[i*n+j]=Math.max(0,Math.floor((9*(1-u*u-v*v)+1.4*Math.sin(8*u)*Math.cos(6*v))*s));}
  const cubes=[];let volume=0;
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){const h=heights[i*n+j];volume+=h;const neighbors=[[i-1,j],[i+1,j],[i,j-1],[i,j+1]].map(([a,b])=>a<0||b<0||a>=n||b>=n?0:heights[a*n+b]);const bottom=Math.min(h-1,...neighbors);for(let k=Math.max(0,bottom);k<h;k++)cubes.push({i,j,k,h});}
  const inst=new THREE.InstancedMesh(new THREE.BoxGeometry(unit*.98,unit*.98,unit*.98),material(0xffffff),cubes.length);
  const matrix=new THREE.Matrix4(),color=new THREE.Color();cubes.forEach(({i,j,k,h},index)=>{matrix.makeTranslation((i-n/2)*unit,(k+.5)*unit,(j-n/2)*unit);inst.setMatrixAt(index,matrix);color.set(k<h-1?0x667780:h<=p+1?0xd9bd7d:0x579978);inst.setColorAt(index,color);});inst.castShadow=true;inst.receiveShadow=true;group.add(inst);
  box(10,.28,10,0x193d4c,0,-.18,0);
  const water=mesh(new THREE.PlaneGeometry(n*unit,n*unit),material(0x378fa9,{transparent:true,opacity:.6,metalness:.3,side:THREE.DoubleSide}),-unit/2,p*unit,-unit/2);water.rotation.x=-Math.PI/2;water.castShadow=false;
  $('metric').textContent=`${volume.toLocaleString()} land voxels`;
  $('metric-detail').textContent=`22 × 22 columns · ${cubes.length.toLocaleString()} exposed cubes rendered`;
}
function lorenz(initial,rho){
  const f=([x,y,z])=>[10*(y-x),x*(rho-z)-y,x*y-(8/3)*z],add=(a,b,k)=>a.map((v,i)=>v+k*b[i]);
  let point=initial;const out=[];
  for(let i=0;i<4001;i++){out.push([point[0]/5,(point[2]-25)/5,point[1]/5]);const a=f(point),b=f(add(point,a,.005)),c=f(add(point,b,.005)),d=f(add(point,c,.01));point=point.map((v,j)=>v+.01*(a[j]+2*b[j]+2*c[j]+d[j])/6);}
  return out;
}
function chaos(){
  const lines=[line(lorenz([1,1,1],p),mint,.9),line(lorenz([1.00001,1,1],p),coral,.65)];
  const draw=t=>{const count=Math.max(2,Math.floor(4001*Math.min(1,s/100)));for(const obj of lines)obj.geometry.setDrawRange(0,count);};draw(0);
  update=t=>{const count=Math.max(2,Math.floor((.03+t*.055)%(s/100)*4001));for(const obj of lines)obj.geometry.setDrawRange(0,count);};
  $('metric').textContent='Δ start = 0.00001';
  $('metric-detail').textContent=`ρ = ${p} · RK4 step 0.01 · 40 model-time units`;
}
const builders={terrain,city,globe,ocean,voxel,chaos};
function rebuild(){dispose();sun.position.set(6,10,4);builders[current]();render();}
function setControl(id,spec){const input=$(id);input.min=spec[1];input.max=spec[2];input.step=spec[3];input.value=spec[4];$(id+'-label').textContent=spec[0];}
function values(){p=Number($('primary').value);s=Number($('secondary').value);$('primary-value').textContent=Number(p.toFixed(2))+cfg.p[5];$('secondary-value').textContent=Number(s.toFixed(2))+cfg.s[5];}
function setPlaying(value){playing=value&&!!cfg.motion;$('play').textContent=playing?'Pause motion':'Play motion';$('play').setAttribute('aria-pressed',String(playing));}
function resetView(){theta=current==='globe'?-2.2:.65;phi=current==='globe'?1.06:1.0;radius=current==='chaos'?21:current==='globe'?17:19;target.set(0,current==='city'?.7:current==='terrain'?.6:current==='voxel'?1:0,0);render();}
function select(name,push=true){
  current=catalog[name]?name:'terrain';cfg=catalog[current];clock=0;setPlaying(false);
  document.querySelectorAll('[data-scene]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.scene===current)));
  $('scene-title').textContent=cfg.title;$('scene-tag').textContent=cfg.tag;$('question').textContent=cfg.question;
  $('explanation').textContent=cfg.explanation;$('connection').textContent=cfg.connection;
  $('source').href='https://github.com/magiccreator-ai/awesome-gpt-6-astra#'+cfg.source;
  $('lesson').href='../lite/lab/index.html?path='+cfg.notebook+'.ipynb';$('world').setAttribute('aria-label',cfg.title+'. Drag to orbit, scroll to zoom. Arrow keys orbit; plus and minus zoom.');
  setControl('primary',cfg.p);setControl('secondary',cfg.s);values();$('play').disabled=!cfg.motion;
  if(push)history.replaceState(null,'','?scene='+current);rebuild();resetView();
  document.title=cfg.title+' · Astra World Lab';
}
function render(){if(!renderer)return;const fittedRadius=radius*Math.max(1,1.3/camera.aspect);camera.position.set(target.x+fittedRadius*Math.sin(phi)*Math.sin(theta),target.y+fittedRadius*Math.cos(phi),target.z+fittedRadius*Math.sin(phi)*Math.cos(theta));camera.lookAt(target);renderer.render(scene,camera);}
function resize(){if(!renderer)return;const r=$('viewport').getBoundingClientRect();renderer.setSize(r.width,r.height,false);camera.aspect=r.width/r.height;camera.updateProjectionMatrix();render();}
document.querySelectorAll('[data-scene]').forEach(b=>b.onclick=()=>select(b.dataset.scene));
let controlFrame;
for(const id of ['primary','secondary'])$(id).addEventListener('input',()=>{values();cancelAnimationFrame(controlFrame);controlFrame=requestAnimationFrame(()=>{clock=0;rebuild();});});
$('play').onclick=()=>setPlaying(!playing);$('reset').onclick=resetView;
let pointer=null;
$('world').addEventListener('pointerdown',e=>{pointer={x:e.clientX,y:e.clientY};$('world').setPointerCapture(e.pointerId);});
$('world').addEventListener('pointermove',e=>{if(!pointer)return;theta-=(e.clientX-pointer.x)*.007;phi=THREE.MathUtils.clamp(phi+(e.clientY-pointer.y)*.007,.15,1.55);pointer={x:e.clientX,y:e.clientY};render();});
for(const event of ['pointerup','pointercancel','lostpointercapture'])$('world').addEventListener(event,()=>pointer=null);
$('world').addEventListener('wheel',e=>{e.preventDefault();radius=THREE.MathUtils.clamp(radius*Math.exp(e.deltaY*.001),7,38);render();},{passive:false});
$('world').addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')theta-=.12;if(e.key==='ArrowRight')theta+=.12;if(e.key==='ArrowUp')phi-=.1;if(e.key==='ArrowDown')phi+=.1;if(e.key==='+'||e.key==='=')radius*=.9;if(e.key==='-')radius*=1.1;phi=THREE.MathUtils.clamp(phi,.15,1.55);radius=THREE.MathUtils.clamp(radius,7,38);render();});
document.addEventListener('visibilitychange',()=>{lastTime=0;});
function tick(time){if(playing&&!document.hidden){clock+=lastTime?Math.min((time-lastTime)/1000,.05):0;update(clock);render();}lastTime=time;requestAnimationFrame(tick);}
new ResizeObserver(resize).observe($('viewport'));
$('world').addEventListener('webglcontextlost',e=>{e.preventDefault();setPlaying(false);$('fallback').hidden=false;});
$('world').addEventListener('webglcontextrestored',()=>{$('fallback').hidden=true;rebuild();});
select(new URLSearchParams(location.search).get('scene')||'terrain',false);resize();requestAnimationFrame(tick);
