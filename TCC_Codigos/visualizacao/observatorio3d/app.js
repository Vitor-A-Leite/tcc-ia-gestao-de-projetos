'use strict';
const $=id=>document.getElementById(id), canvas=$('graph'), ctx=canvas.getContext('2d');
const palette=['#71d6bc','#79b6ff','#e7b77b','#b49af8','#ee91b8','#baca7c','#7ccfdf'];
const typeNames={Supplier:'Fornecedor',Component:'Componente',Task:'Atividade',Milestone:'Marco',Test:'Teste',Person:'Pessoa',ProjectArea:'Área',Document:'Documento'};

const nodeShapes={
 Supplier:{name:'Hexágono',sides:6,angle:0},
 Component:{name:'Quadrado',sides:4,angle:Math.PI/4},
 Task:{name:'Triângulo',sides:3,angle:-Math.PI/2},
 Milestone:{name:'Losango',sides:4,angle:0},
 Test:{name:'Pentágono',sides:5,angle:-Math.PI/2},
 ProjectArea:{name:'Estrela',sides:10,angle:-Math.PI/2,star:true},
 Person:{name:'Círculo'},
 Document:{name:'Octógono',sides:8,angle:Math.PI/8}
};
function shapePoints(type){const shape=nodeShapes[type]||nodeShapes.Person;if(!shape.sides)return null;return Array.from({length:shape.sides},(_,i)=>{const angle=shape.angle+i*2*Math.PI/shape.sides,r=shape.star&&i%2?.48:1;return [Math.cos(angle)*r,Math.sin(angle)*r];});}
function nodePath(type,x,y,r){ctx.beginPath();const points=shapePoints(type);if(!points){ctx.arc(x,y,r,0,Math.PI*2);return;}points.forEach(([px,py],i)=>{if(i===0)ctx.moveTo(x+px*r,y+py*r);else ctx.lineTo(x+px*r,y+py*r);});ctx.closePath();}
function shapeIcon(type){const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','-12 -12 24 24');svg.setAttribute('width','15');svg.setAttribute('height','15');svg.setAttribute('aria-hidden','true');const points=shapePoints(type),shape=document.createElementNS(ns,points?'polygon':'circle');if(points)shape.setAttribute('points',points.map(([x,y])=>`${x*10},${y*10}`).join(' '));else shape.setAttribute('r','10');shape.setAttribute('fill','currentColor');svg.append(shape);return svg;}

let graph, scenarios, colors={}, positions=[], projected=[], events=[], cursor=0, playing=false, busy=false, selected='', yaw=.35,pitch=-.25,zoom=1,panX=0,panY=0, runs=[], currentRun=null;
let allowedTypes=new Set(), visibleIds=new Set();
let active=new Set(), current=null, lastTick=0;
const names={input:'Entrada recebida',processing:'Interpretação',interpretation:'Interpretação disponível',transfer:'Propagação por regra',result:'Resultado do motor',error:'Falha na execução'};
function textBlock(parent,title,value){const b=document.createElement('strong');b.textContent=title;parent.append(b);const p=document.createElement('pre');p.textContent=typeof value==='string'?value:JSON.stringify(value,null,2);parent.append(p);}
function inspect(){const node=graph.nodes.find(n=>n.id===selected), box=$('details');box.replaceChildren();$('nodeTitle').textContent=node?node.name:'Acompanhe o fluxo';$('nodes').value=selected;if(!node){box.textContent='Clique em um nó ou escolha uma entidade na lista.';return;}textBlock(box,'Entidade',node);const position=positions.find(p=>p.id===selected);if(position)textBlock(box,'Coordenadas espaciais (unidades de layout)',{X:+position.x.toFixed(1),Y:+(-position.y).toFixed(1),Z:+position.z.toFixed(1)});const steps=events.slice(0,cursor).filter(e=>e.type==='transfer'&&(e.data.source===selected||e.data.target===selected));const seed=events.slice(0,cursor).find(e=>e.type==='interpretation'&&(e.data.primary_entity===selected||(e.data.related_entities||[]).includes(selected)));textBlock(box,'Entradas recebidas',[...(seed?[{origem:'Interpretação do evento',dados:seed.data}]:[]),...steps.filter(e=>e.data.target===selected).map(e=>e.data)]);textBlock(box,'Saídas transmitidas',steps.filter(e=>e.data.source===selected).map(e=>e.data));textBlock(box,'Processamento','Propagação BFS por dependências, limitada a quatro níveis. Este nó não executa um LLM.');textBlock(box,'Relações na fonte',graph.edges.filter(e=>e.source===selected||e.target===selected));}
function renderState(){active=new Set();current=events[cursor-1]||null;for(const e of events.slice(0,cursor)){if(e.type==='interpretation'){if(e.data.primary_entity)active.add(e.data.primary_entity);(e.data.related_entities||[]).forEach(x=>active.add(x));}if(e.type==='transfer'){active.add(e.data.source);active.add(e.data.target);}}$('timeline').max=events.length;$('timeline').value=cursor;$('counter').textContent=`${cursor} / ${events.length}`;$('eventTitle').textContent=current?names[current.type]||current.type:'Pronto para executar';$('eventData').textContent=current?`Tempo real: ${current.elapsed_ms} ms\n\n${JSON.stringify(current.data,null,2)}`:'Escolha um cenário e execute.';document.querySelectorAll('.stages span').forEach(e=>e.classList.remove('active'));let stage=current?.type;if(stage==='interpretation')stage='processing';if($("stage-"+stage))$("stage-"+stage).classList.add('active');updateFilters();}
function updateFilters(){
 const visible=graph.nodes.filter(n=>allowedTypes.has(n.type)&&(!$('involved').checked||active.has(n.id)));
 visibleIds=new Set(visible.map(n=>n.id));
 if(!visibleIds.has(selected))selected='';
 $('nodes').replaceChildren(new Option('Selecione um nó…',''));
 for(const n of visible)$('nodes').add(new Option(`${n.name} · ${n.id}`,n.id));
 const edges=graph.edges.filter(e=>visibleIds.has(e.source)&&visibleIds.has(e.target));
 $('filterCount').textContent=`${visible.length} / ${graph.nodes.length} nós · ${edges.length} relações`;
 $('emptyGraph').hidden=visible.length>0;
 inspect();
}
$('involved').onchange=()=>{if(graph)updateFilters();};
$('allCategories').onclick=()=>{document.querySelectorAll('#categories input').forEach(input=>{input.checked=true;allowedTypes.add(input.value);});if(graph)updateFilters();};
function controls(){for(const id of ['run','scenario','mode','history','play','step','timeline'])$(id).disabled=busy; $('download').disabled=busy||!events.length;$('play').textContent=playing?'Ⅱ Pausar':'▶ Replay';}
function selectScenario(){$('source').textContent=scenarios.find(s=>s.scenario_id===$('scenario').value).source_text;}
async function history(){const r=await fetch('/api/runs');if(!r.ok)throw Error('Não foi possível carregar os registros.');runs=await r.json();$('history').replaceChildren(new Option('Escolha um replay…',''));for(const r of runs.slice().reverse())$('history').add(new Option(`${r.scenario_id} · ${r.mode==='real'?'IA':'Referência'} · ${new Date(r.created_at).toLocaleString('pt-BR')}`,r.id));}
$('run').onclick=async()=>{busy=true;playing=false;events=[];cursor=0;currentRun=null;controls();renderState();$('badge').textContent=$('mode').value==='real'?'Ao vivo · IA real':'Ao vivo · referência sem IA';try{const response=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({scenario_id:$('scenario').value,mode:$('mode').value})});if(!response.ok)throw Error((await response.json()).error);const reader=response.body.getReader(), decoder=new TextDecoder();let pending='';while(true){const {value,done}=await reader.read();pending+=decoder.decode(value||new Uint8Array(),{stream:!done});let idx;while((idx=pending.indexOf('\n'))>=0){const line=pending.slice(0,idx);pending=pending.slice(idx+1);if(!line)continue;const e=JSON.parse(line);if(e.type==='saved'){currentRun=e.data.id;continue;}events.push(e);cursor=events.length;renderState();}if(done)break;}if(!events.some(e=>['result','error'].includes(e.type)))throw Error('Conexão encerrada antes do resultado.');$('badge').textContent=events.some(e=>e.type==='error')?'Execução com falha':'Concluído · replay disponível';await history();}catch(e){$('badge').textContent='Falha';$('eventTitle').textContent='Não foi possível concluir';$('eventData').textContent=e.message;}finally{busy=false;controls();}};
$('scenario').onchange=selectScenario;
$('nodes').onchange=()=>{selected=$('nodes').value;inspect();};
$('history').onchange=()=>{const r=runs.find(r=>r.id===$('history').value);if(!r)return;playing=false;currentRun=r.id;events=r.events.filter(e=>e.type!=='saved');cursor=0;$('scenario').value=r.scenario_id;selectScenario();$('badge').textContent=`Replay · ${r.mode==='real'?'IA real':'referência sem IA'}`;controls();renderState();};
$('play').onclick=()=>{if(!events.length)return;if(cursor>=events.length)cursor=0;playing=!playing;lastTick=performance.now();controls();renderState();};
$('step').onclick=()=>{playing=false;cursor=Math.min(events.length,cursor+1);controls();renderState();};
$('timeline').oninput=()=>{playing=false;cursor=Number($('timeline').value);controls();renderState();};
$('reset').onclick=()=>{yaw=.35;pitch=-.25;zoom=1;panX=0;panY=0;};
$('download').onclick=()=>{const run=runs.find(r=>r.id===currentRun)||{scenario_id:$('scenario').value,mode:$('mode').value,events};const blob=new Blob([JSON.stringify(run,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`execucao-${currentRun||'parcial'}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
let drag=null;
canvas.onpointerdown=e=>{drag={x:e.clientX,y:e.clientY,distance:0,pan:e.metaKey};canvas.setPointerCapture(e.pointerId);};
canvas.onpointermove=e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.distance+=Math.abs(dx)+Math.abs(dy);if(drag.pan||e.metaKey){panX+=dx;panY+=dy;}else{yaw+=dx*.006;pitch=Math.max(-1.4,Math.min(1.4,pitch+dy*.006));}drag.x=e.clientX;drag.y=e.clientY;};
canvas.onpointerup=e=>{if(drag&&drag.distance<5){const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;const hit=projected.slice().sort((a,b)=>a.z-b.z).find(p=>Math.hypot(p.x-x,p.y-y)<p.r+7);if(hit){selected=selected===hit.id?'':hit.id;inspect();if(selected){document.querySelectorAll('.floating-panel').forEach(panel=>panel.hidden=panel.id!=='inspectionPanel');document.querySelectorAll('[data-panel]').forEach(b=>b.setAttribute('aria-expanded',String(b.dataset.panel==='inspectionPanel')));}else{$('inspectionPanel').hidden=true;document.querySelector('[data-panel="inspectionPanel"]').setAttribute('aria-expanded','false');}}}drag=null;};canvas.onpointercancel=()=>drag=null;
canvas.addEventListener('wheel',e=>{e.preventDefault();const unit=e.deltaMode===1?16:e.deltaMode===2?canvas.clientHeight:1;if(e.metaKey){panX-=e.deltaX*unit;panY-=e.deltaY*unit;}else{zoom=Math.max(.45,Math.min(2.8,zoom*Math.exp(-e.deltaY*unit*.001)));}},{passive:false});
function layout(){// Distribuição tridimensional determinística com atração das relações.
 positions=graph.nodes.map((n,i)=>{const y=1-2*(i+.5)/graph.nodes.length,a=i*2.399963,r=Math.sqrt(1-y*y);return {...n,x:220*r*Math.cos(a),y:220*y,z:220*r*Math.sin(a)};});const byId=Object.fromEntries(positions.map(p=>[p.id,p]));for(let k=0;k<70;k++){const forces=positions.map(()=>({x:0,y:0,z:0}));for(let i=0;i<positions.length;i++)for(let j=i+1;j<positions.length;j++){const a=positions[i],b=positions[j],dx=a.x-b.x,dy=a.y-b.y,dz=a.z-b.z,d=Math.max(20,Math.hypot(dx,dy,dz)),f=1100/d**2;for(const [key,v] of [['x',dx],['y',dy],['z',dz]]){forces[i][key]+=v*f;forces[j][key]-=v*f;}}for(const e of graph.edges){const a=byId[e.source],b=byId[e.target],i=positions.indexOf(a),j=positions.indexOf(b);for(const key of ['x','y','z']){const f=(b[key]-a[key])*.006;forces[i][key]+=f;forces[j][key]-=f;}}positions.forEach((p,i)=>{for(const key of ['x','y','z'])p[key]+=(forces[i][key]-p[key]*.003)*.8;});}const radius=Math.max(...positions.map(p=>Math.hypot(p.x,p.y,p.z)));positions.forEach(p=>{for(const key of ['x','y','z'])p[key]*=230/radius;});}
function draw(now){requestAnimationFrame(draw);if(!graph)return;if(playing&&now-lastTick>Number($('speed').value)){lastTick=now;cursor=Math.min(events.length,cursor+1);if(cursor===events.length){playing=false;controls();}renderState();}const w=canvas.clientWidth,h=canvas.clientHeight,dpr=window.devicePixelRatio||1;if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
const scale=Math.min(w,h)/620*zoom;
// Uma única transformação de câmera para nós, chão e coordenadas.
function project(p){const x=p.x*Math.cos(yaw)+p.z*Math.sin(yaw),z0=-p.x*Math.sin(yaw)+p.z*Math.cos(yaw),y=p.y*Math.cos(pitch)-z0*Math.sin(pitch),z=p.y*Math.sin(pitch)+z0*Math.cos(pitch),perspective=850/(850+z);return {...p,x:w/2+panX+x*scale*perspective,y:h/2+panY+y*scale*perspective,z,r:Math.max(6,9*perspective*scale)};}
function line3(a,b,color,alpha=1,width=1){let u=project(a),v=project(b);const near=-800;if(u.z<near&&v.z<near)return;if(u.z<near||v.z<near){const t=(near-u.z)/(v.z-u.z),clipped={x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t,z:a.z+(b.z-a.z)*t};if(u.z<near)u=project(clipped);else v=project(clipped);}ctx.strokeStyle=color;ctx.globalAlpha=alpha;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(u.x,u.y);ctx.lineTo(v.x,v.y);ctx.stroke();}
ctx.save();
for(let i=-1100;i<=1100;i+=50){line3({x:i,y:250,z:-1100},{x:i,y:250,z:1100},'#6387a6',.28);line3({x:-1100,y:250,z:i},{x:1100,y:250,z:i},'#6387a6',.28);}
const chosen=positions.find(p=>p.id===selected);if(chosen){ctx.setLineDash([4,4]);line3(chosen,{x:chosen.x,y:250,z:chosen.z},'#ffffff',.65);ctx.setLineDash([]);}
ctx.restore();
projected=positions.filter(p=>visibleIds.has(p.id)).map(project);
const byId=Object.fromEntries(projected.map(p=>[p.id,p]));const traversed=new Set(events.slice(0,cursor).filter(e=>e.type==='transfer').map(e=>e.data.source+'|'+e.data.target));for(const e of graph.edges){if(!visibleIds.has(e.source)||!visibleIds.has(e.target))continue;const a=byId[e.source],b=byId[e.target],key=e.source+'|'+e.target,on=traversed.has(key),focus=current?.type==='transfer'&&current.data.source===e.source&&current.data.target===e.target;ctx.strokeStyle=focus?'#fff0ae':on?'#67ceb0':'#f0f3f7';const neighbor=selected&&(e.source===selected||e.target===selected);ctx.globalAlpha=selected&&!neighbor?.15:on||neighbor?.9:.45;ctx.lineWidth=focus||neighbor?2.2:1;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();const angle=Math.atan2(b.y-a.y,b.x-a.x),tx=b.x-Math.cos(angle)*(b.r+3),ty=b.y-Math.sin(angle)*(b.r+3);ctx.beginPath();ctx.moveTo(tx,ty);ctx.lineTo(tx-6*Math.cos(angle-.45),ty-6*Math.sin(angle-.45));ctx.moveTo(tx,ty);ctx.lineTo(tx-6*Math.cos(angle+.45),ty-6*Math.sin(angle+.45));ctx.stroke();if(focus){const t=(now%1400)/1400;ctx.fillStyle='#fff2ad';ctx.beginPath();ctx.arc(a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t,4,0,Math.PI*2);ctx.fill();}}ctx.globalAlpha=1;const labelBoxes=[];for(const p of projected.slice().sort((a,b)=>b.z-a.z)){const near=Math.max(.25,Math.min(1,(300-p.z)/500));
const related=!selected||p.id===selected||graph.edges.some(e=>(e.source===selected&&e.target===p.id)||(e.target===selected&&e.source===p.id));
ctx.globalAlpha=related?.48+near*.52:.2;
ctx.save();ctx.shadowColor='rgba(0,0,0,.7)';ctx.shadowBlur=5+near*9;ctx.shadowOffsetY=3+near*3;
const light=ctx.createLinearGradient(p.x-p.r,p.y-p.r,p.x+p.r,p.y+p.r);
light.addColorStop(0,'#f1f8ff');light.addColorStop(.3,colors[p.type]);light.addColorStop(1,'#22354d');ctx.fillStyle=light;
nodePath(p.type,p.x,p.y,p.r);ctx.fill();ctx.restore();
ctx.strokeStyle='rgba(225,244,255,.65)';ctx.lineWidth=.8;nodePath(p.type,p.x,p.y,p.r);ctx.stroke();if(active.has(p.id)||selected===p.id){ctx.strokeStyle=selected===p.id?'#fff':'#89f3ce';ctx.lineWidth=2;nodePath(p.type,p.x,p.y,p.r+4);ctx.stroke();}ctx.font=`${selected===p.id?'600 ':''}10px system-ui`;ctx.fillStyle=active.has(p.id)||selected===p.id?'#fff':'#adc0d4';const lx=p.x+p.r+7,ly=p.y+3,lw=ctx.measureText(p.name).width;const important=selected===p.id||(current?.type==='transfer'&&[current.data.source,current.data.target].includes(p.id));if($('showNames').checked&&(important||!labelBoxes.some(b=>lx<b.x+b.w&&lx+lw>b.x&&ly<b.y+13&&ly+13>b.y))){ctx.save();ctx.fillStyle=selected===p.id?'#193c4c':'rgba(8,18,30,.83)';ctx.fillRect(lx-3,ly-11,lw+6,15);ctx.fillStyle=active.has(p.id)||selected===p.id?'#fff':'#bfd1e2';ctx.fillText(p.name,lx,ly);ctx.restore();labelBoxes.push({x:lx,y:ly,w:lw});}ctx.globalAlpha=1;}drawOrientation();}
(async()=>{try{const r=await fetch('/api/data');if(!r.ok)throw Error('Servidor indisponível');const data=await r.json();graph=data.graph;scenarios=data.scenarios;const types=[...new Set(graph.nodes.map(n=>n.type))];types.forEach((t,i)=>{colors[t]=palette[i%palette.length];allowedTypes.add(t);const label=document.createElement('label'),check=document.createElement('input');check.type='checkbox';check.value=t;check.checked=true;check.onchange=()=>{if(check.checked)allowedTypes.add(t);else allowedTypes.delete(t);updateFilters();};label.append(check,shapeIcon(t),document.createTextNode(typeNames[t]||t));label.title=(nodeShapes[t]||nodeShapes.Person).name;label.style.color=colors[t];$('categories').append(label);const s=document.createElement('span');s.append(shapeIcon(t),document.createTextNode(typeNames[t]||t));s.title=(nodeShapes[t]||nodeShapes.Person).name;s.style.color=colors[t];$('legend').append(s);});for(const s of scenarios)$('scenario').add(new Option(s.scenario_id,s.scenario_id));for(const n of graph.nodes)$('nodes').add(new Option(`${n.name} · ${n.id}`,n.id));$('mode').options[1].disabled=!data.allow_api;if(!data.allow_api)$('mode').options[1].textContent='IA real · iniciar com --allow-api';selectScenario();layout();$('badge').textContent=`${graph.nodes.length} nós · ${graph.edges.length} relações`;await history();renderState();controls();}catch(e){$('badge').textContent='Falha ao carregar';$('eventData').textContent=e.message;$('run').disabled=true;}})();requestAnimationFrame(draw);

// Amplia a área de trabalho inteira para preservar execução, filtros e replay.
const fullscreenPanel=document.querySelector('.workspace');
function syncFullscreen(){const expanded=document.fullscreenElement===fullscreenPanel||fullscreenPanel.classList.contains('expanded');$('fullscreen').textContent=expanded?'⛶ Sair da tela cheia':'⛶ Tela cheia';$('fullscreen').setAttribute('aria-pressed',String(expanded));}
$('fullscreen').onclick=async()=>{
 if(document.fullscreenElement===fullscreenPanel){await document.exitFullscreen();return;}
 if(fullscreenPanel.classList.contains('expanded')){fullscreenPanel.classList.remove('expanded');document.body.classList.remove('graph-expanded');syncFullscreen();return;}
 try{if(!fullscreenPanel.requestFullscreen)throw new Error('Fullscreen indisponível');await fullscreenPanel.requestFullscreen();}
 catch{fullscreenPanel.classList.add('expanded');document.body.classList.add('graph-expanded');}
 syncFullscreen();
};
document.addEventListener('fullscreenchange',syncFullscreen);
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&fullscreenPanel.classList.contains('expanded')){fullscreenPanel.classList.remove('expanded');document.body.classList.remove('graph-expanded');syncFullscreen();}});

function drawOrientation(){
 const c=$('orientation'),g=c.getContext('2d'),dpr=window.devicePixelRatio||1;
 if(c.width!==Math.round(100*dpr)){c.width=Math.round(100*dpr);c.height=Math.round(100*dpr);}
 g.setTransform(dpr,0,0,dpr,0,0);g.clearRect(0,0,100,100);
 const axes=[{x:1,y:0,z:0,label:'X',color:'#ff8790'},{x:0,y:-1,z:0,label:'Y',color:'#8bebaa'},{x:0,y:0,z:1,label:'Z',color:'#83bdff'}].map(a=>{
 const x=a.x*Math.cos(yaw)+a.z*Math.sin(yaw),z0=-a.x*Math.sin(yaw)+a.z*Math.cos(yaw);
 return {...a,x,y:a.y*Math.cos(pitch)-z0*Math.sin(pitch),depth:a.y*Math.sin(pitch)+z0*Math.cos(pitch)};
 }).sort((a,b)=>b.depth-a.depth);
 for(const a of axes){const x=50+a.x*30,y=50+a.y*30;g.strokeStyle=a.color;g.lineWidth=2;g.beginPath();g.moveTo(50,50);g.lineTo(x,y);g.stroke();g.fillStyle=a.color;g.beginPath();g.arc(x,y,3,0,Math.PI*2);g.fill();g.font='bold 11px system-ui';g.textAlign='center';g.textBaseline='middle';g.fillText(a.label,50+a.x*41,50+a.y*41);}
 g.fillStyle='#dce6f2';g.beginPath();g.arc(50,50,3,0,Math.PI*2);g.fill();
}

// Um painel aberto por vez evita sobreposição em janelas estreitas.
document.querySelectorAll('[data-panel]').forEach(button=>button.onclick=()=>{
 const target=$(button.dataset.panel),opening=target.hidden;
 document.querySelectorAll('.floating-panel').forEach(panel=>panel.hidden=true);
 document.querySelectorAll('[data-panel]').forEach(b=>b.setAttribute('aria-expanded','false'));
 target.hidden=!opening;button.setAttribute('aria-expanded',String(opening));
});
