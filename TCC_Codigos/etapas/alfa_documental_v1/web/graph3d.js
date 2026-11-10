/* Visualização 3D 1.1 — coordenadas XYZ, câmera orbital e projeção em Canvas.
 * Reaproveita a abordagem do observatorio3d; não executa cálculos de impacto.
 * Layout espacial não representa duração, custo ou intensidade de impacto.
 */
'use strict';
(function (root) {
  const palette = {Supplier:'#b65b24', Component:'#2476b0', Task:'#4b7957',
    Test:'#8960ae', Milestone:'#b34867', Document:'#7253bf', Person:'#697d79', ProjectArea:'#697d79'};
  const types = {Supplier:'Fornecedor', Component:'Componente', Task:'Atividade',
    Test:'Teste', Milestone:'Marco', Document:'Documento', Person:'Pessoa', ProjectArea:'Área'};
  const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));

  function layout(graph) {
    const ids = new Set(graph.nodes.map(n => n.id));
    if (ids.size !== graph.nodes.length) throw Error('IDs duplicados no grafo 3D.');
    for (const e of graph.edges) if (!ids.has(e.source) || !ids.has(e.target))
      throw Error('Relação sem entidade cadastrada: ' + e.id);
    const executable = graph.nodes.filter(n => n.parametros?.duracao !== undefined);
    const temporal = graph.edges.filter(e => e.classe === 'temporal');
    const levels = new Map(), pending = new Set(executable.map(n => n.id));
    while (pending.size) {
      const ready = [...pending].filter(id => !temporal.some(e => e.target === id && pending.has(e.source)));
      if (!ready.length) throw Error('Ciclo temporal: não é possível organizar a visão 3D.');
      for (const id of ready) {
        const parents = temporal.filter(e => e.target === id);
        if (parents.some(e => !levels.has(e.source))) throw Error('Precedência fora da rede executável.');
        levels.set(id, parents.length ? 1 + Math.max(...parents.map(e => levels.get(e.source))) : 0);
        pending.delete(id);
      }
    }
    const last = Math.max(0, ...levels.values()), positions = new Map();
    for (let rank = 0; rank <= last; rank++) {
      const group = executable.filter(n => levels.get(n.id) === rank).sort((a,b) => a.id.localeCompare(b.id));
      const branches = group.filter(n => !['Task','Milestone'].includes(n.type));
      group.forEach(n => {
        const i = branches.indexOf(n), angle = 2 * Math.PI * i / Math.max(1, branches.length) + .35;
        const radius = branches.length > 1 ? 95 + branches.length * 7 : 100;
        positions.set(n.id, {x:(rank-last/2)*78,
          y:i < 0 ? 0 : Math.sin(angle)*radius,
          z:i < 0 ? 0 : Math.cos(angle)*radius});
      });
    }
    // Documents and context occupy separate spatial bands, but remain full entities.
    const docs = graph.nodes.filter(n => n.type === 'Document');
    docs.forEach((n,i) => positions.set(n.id, {x:(i-(docs.length-1)/2)*87, y:228, z:(i%2 ? 1 : -1)*75}));
    const context = graph.nodes.filter(n => !positions.has(n.id));
    context.forEach((n,i) => positions.set(n.id, {x:(i-(context.length-1)/2)*85, y:-228, z:(i%2 ? 1 : -1)*65}));
    return graph.nodes.map(n => ({...n, ...positions.get(n.id)}));
  }

  function rotate(p, camera) {
    const x = p.x*Math.cos(camera.yaw)+p.z*Math.sin(camera.yaw);
    const z = -p.x*Math.sin(camera.yaw)+p.z*Math.cos(camera.yaw);
    return {x, y:p.y*Math.cos(camera.pitch)-z*Math.sin(camera.pitch),
      z:p.y*Math.sin(camera.pitch)+z*Math.cos(camera.pitch)};
  }
  function project(p, camera, view) {
    const r = rotate(p, camera), perspective = 1600/(1600+r.z);
    return {...p, x:view.width/2+camera.panX+r.x*view.scale*camera.zoom*perspective,
      y:view.height/2+camera.panY+r.y*view.scale*camera.zoom*perspective,
      depth:r.z, r:clamp(9*view.scale*camera.zoom*perspective, 6, 28)};
  }
  function pick(points, x, y) {
    return points.slice().sort((a,b) => a.depth-b.depth)
      .find(p => Math.hypot(p.x-x,p.y-y) <= p.r+6);
  }

  class Graph3D {
    constructor(canvas, options) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      if (!this.ctx) throw Error('Canvas indisponível neste navegador.');
      this.options = options;
      this.positions = [];
      this.points = [];
      this.hover = null;
      this.reset();
      this.bind();
      this.resizeObserver = new ResizeObserver(() => this.invalidate());
      this.resizeObserver.observe(canvas);
    }
    reset() {
      this.camera = {yaw:-.32, pitch:.42, zoom:1, panX:0, panY:0};
      this.invalidate();
    }
    orbit(dx,dy) {
      this.camera.yaw += dx;
      this.camera.pitch = clamp(this.camera.pitch+dy,-1.3,1.3);
      this.invalidate();
    }
    zoom(factor) { this.camera.zoom = clamp(this.camera.zoom*factor,.4,4); this.invalidate(); }
    invalidate() {
      // This is an event-driven scene, not a continuous animation. Paint on the
      // event itself, including when browsers suspend background animation frames.
      this.draw();
    }
    update(state) {
      if (this.result !== state.result) {
        this.result = state.result;
        this.positions = layout(state.result.grafo);
        this.effects = new Map(state.result.propagacao.map(e => [e.relacao_id,e]));
        this.changed = new Set(state.result.nos_com_mudanca_quantitativa);
        this.reset();
      }
      this.state = state;
      this.visited = new Set(state.result.rastro_orquestracao.slice(0,state.step).map(t => t.no_id));
      this.current = state.result.rastro_orquestracao[state.step-1]?.no_id;
      this.invalidate();
    }
    bind() {
      const c = this.canvas;
      c.addEventListener('contextmenu', e => e.preventDefault());
      c.addEventListener('pointerdown', e => {
        if (this.drag) { this.drag=null; return; }
        c.focus({preventScroll:true});
        this.drag = {id:e.pointerId,x:e.clientX,y:e.clientY,distance:0,pan:e.shiftKey||e.metaKey||e.button===2};
        c.setPointerCapture(e.pointerId);
      });
      c.addEventListener('pointermove', e => {
        const rect = c.getBoundingClientRect();
        if (this.drag?.id === e.pointerId) {
          const dx=e.clientX-this.drag.x, dy=e.clientY-this.drag.y;
          this.drag.distance += Math.abs(dx)+Math.abs(dy);
          if (this.drag.pan) {this.camera.panX+=dx; this.camera.panY+=dy; this.invalidate();}
          else this.orbit(dx*.006,dy*.006);
          this.drag.x=e.clientX; this.drag.y=e.clientY;
          this.hover=null;
        } else {
          const hit=pick(this.points,e.clientX-rect.left,e.clientY-rect.top);
          if (this.hover !== hit?.id) { this.hover=hit?.id; this.invalidate(); }
          c.style.cursor=hit?'pointer':'grab';
        }
      });
      c.addEventListener('pointerup', e => {
        if (this.drag?.id !== e.pointerId) return;
        if (this.drag.distance < 5 && !this.drag.pan) {
          const rect=c.getBoundingClientRect(), hit=pick(this.points,e.clientX-rect.left,e.clientY-rect.top);
          if (hit) this.options.onSelect(hit.id);
        }
        this.drag=null;
      });
      for (const name of ['pointercancel','lostpointercapture']) c.addEventListener(name,()=>this.drag=null);
      c.addEventListener('pointerleave',()=>{this.hover=null;this.invalidate();});
      c.addEventListener('wheel', e => {
        e.preventDefault();
        const unit=e.deltaMode===1?16:e.deltaMode===2?c.clientHeight:1;
        if (e.metaKey||e.shiftKey) {
          this.camera.panX-=e.deltaX*unit;this.camera.panY-=e.deltaY*unit;this.invalidate();
        } else this.zoom(Math.exp(-e.deltaY*unit*.0015));
      }, {passive:false});
      c.addEventListener('keydown', e => {
        const actions={ArrowLeft:()=>this.orbit(-.12,0),ArrowRight:()=>this.orbit(.12,0),
          ArrowUp:()=>this.orbit(0,-.12),ArrowDown:()=>this.orbit(0,.12),
          '+':()=>this.zoom(1.15),'=':()=>this.zoom(1.15),'-':()=>this.zoom(1/1.15),'0':()=>this.reset()};
        if (actions[e.key]) {e.preventDefault();actions[e.key]();}
      });
    }
    shape(type,x,y,r) {
      const c=this.ctx;
      c.beginPath();
      if (type==='Person') {c.arc(x,y,r,0,Math.PI*2);return;}
      if (type==='Document') {c.rect(x-r*.75,y-r*1.1,r*1.5,r*2.2);return;}
      const sides={Supplier:6,Component:4,Task:3,Test:5,Milestone:4,ProjectArea:8}[type]||6;
      const start=type==='Component'?Math.PI/4:-Math.PI/2;
      for(let i=0;i<sides;i++) {
        const a=start+i*2*Math.PI/sides;
        if(i===0)c.moveTo(x+Math.cos(a)*r,y+Math.sin(a)*r);else c.lineTo(x+Math.cos(a)*r,y+Math.sin(a)*r);
      }
      c.closePath();
    }
    draw() {
      if (!this.state) return;
      const c=this.ctx, canvas=this.canvas, width=canvas.clientWidth, height=canvas.clientHeight;
      if (!width||!height) return;
      const dpr=Math.min(window.devicePixelRatio||1,2);
      if (canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)) {
        canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
      }
      c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,width,height);
      const scale=Math.min((width-90)/1000,(height-100)/680);
      const view={width,height,scale};
      const projectPoint=p=>project(p,this.camera,view);
      const nodes=this.positions.map(projectPoint);
      this.points=nodes.filter(n=>n.x>=0&&n.x<=width&&n.y>=0&&n.y<=height);
      const byId=new Map(nodes.map(n=>[n.id,n]));
      const {selected,documental,contextual,labels}=this.state;
      const edges=this.result.grafo.edges.filter(e=>e.classe==='temporal'||e.classe==='financeira'||
        (e.classe==='documental'?documental:contextual));
      const nearby=new Set([selected]);
      for(const e of edges) {if(e.source===selected)nearby.add(e.target);if(e.target===selected)nearby.add(e.source);}
      // Perspective floor makes the third axis visible without encoding a project quantity.
      c.strokeStyle='#dae5de';c.lineWidth=.6;
      for(let x=-500;x<=500;x+=100) this.line(projectPoint({x,y:290,z:-220}),projectPoint({x,y:290,z:220}));
      for(let z=-220;z<=220;z+=55) this.line(projectPoint({x:-500,y:290,z}),projectPoint({x:500,y:290,z}));
      const edgeStates=edges.map(e=>{
        const effect=this.effects.get(e.id), active=this.visited.has(e.source);
        const state=active?effect?.estado:null;
        const on=state==='transmitido'||state==='indeterminado'||['absorvido_ou_dominado','dominado_na_convergencia'].includes(state);
        const focused=e.source===selected||e.target===selected;
        const color=state==='transmitido'?'#db7b22':state==='indeterminado'?'#c94542':
          ['absorvido_ou_dominado','dominado_na_convergencia'].includes(state)?'#13856b':
          e.classe==='documental'?'#9072c2':e.classe==='financeira'?'#b54f79':'#99afa4';
        return {e,on,focused,color};
      });
      // Emphasized causal paths are painted last so the flow remains legible.
      edgeStates.sort((a,b)=>(a.on||a.focused)-(b.on||b.focused));
      for(const {e,on,focused,color} of edgeStates) {
        const a=byId.get(e.source),b=byId.get(e.target);
        c.globalAlpha=on?.9:focused?.75:.28;c.strokeStyle=color;c.lineWidth=on?2.1:focused?1.4:.9;
        c.setLineDash(e.classe==='documental'?[5,5]:e.classe==='financeira'?[3,4]:e.classe==='contextual'?[2,6]:[]);
        this.line(a,b);c.setLineDash([]);
        const angle=Math.atan2(b.y-a.y,b.x-a.x),x=b.x-Math.cos(angle)*(b.r+3),y=b.y-Math.sin(angle)*(b.r+3);
        if(on||focused) {c.beginPath();c.moveTo(x-6*Math.cos(angle-.45),y-6*Math.sin(angle-.45));c.lineTo(x,y);c.lineTo(x-6*Math.cos(angle+.45),y-6*Math.sin(angle+.45));c.stroke();}
      }
      c.globalAlpha=1;
      for(const p of nodes.slice().sort((a,b)=>b.depth-a.depth)) {
        const visited=this.visited.has(p.id),changed=visited&&this.changed.has(p.id);
        const unknown=visited&&this.result.estado_projetado_nos[p.id]?.fim.valor===null;
        const chosen=p.id===selected,current=p.id===this.current;
        c.save();c.globalAlpha=clamp(.92-p.depth/1800,.52,1);
        c.shadowBlur=chosen?14:5;c.shadowColor=chosen?'#658f7c66':'#19332b33';c.shadowOffsetY=3;
        const light=c.createLinearGradient(p.x-p.r,p.y-p.r,p.x+p.r,p.y+p.r);
        light.addColorStop(0,'#fff');light.addColorStop(.35,palette[p.type]||'#64746c');light.addColorStop(1,'#283d3a');
        c.fillStyle=light;this.shape(p.type,p.x,p.y,p.r);c.fill();c.restore();
        c.strokeStyle='#ffffff';c.lineWidth=1;this.shape(p.type,p.x,p.y,p.r);c.stroke();
        if(visited) {c.strokeStyle=unknown?'#c94542':changed?'#db7b22':'#5c9f88';c.lineWidth=2;this.shape(p.type,p.x,p.y,p.r+3);c.stroke();}
        if(chosen||current) {c.strokeStyle=chosen?'#163b30':'#d49518';c.lineWidth=chosen?2.5:2;c.setLineDash(current&&!chosen?[3,3]:[]);this.shape(p.type,p.x,p.y,p.r+7);c.stroke();c.setLineDash([]);}
      }
      this.drawLabels(nodes,nearby,labels,width,height);
      this.orientation(width,height);
      const counts={};for(const e of edges) counts[e.classe]=(counts[e.classe]||0)+1;
      this.options.onView?.({total:nodes.length,visible:this.points.length,edges:edges.length,
        temporal:counts.temporal||0,zoom:this.camera.zoom,hover:this.positions.find(n=>n.id===this.hover)});
    }
    line(a,b) {const c=this.ctx;c.beginPath();c.moveTo(a.x,a.y);c.lineTo(b.x,b.y);c.stroke();}
    drawLabels(nodes,nearby,labels,width,height) {
      const c=this.ctx,selected=this.state.selected,boxes=[];
      const priority=p=>p.id===selected?4:p.id===this.hover?3:p.id===this.current?2:nearby.has(p.id)?1:0;
      nodes=nodes.slice().sort((a,b)=>priority(b)-priority(a)||a.depth-b.depth);
      for(const p of nodes) {
        const important=priority(p)>=2;
        if(!labels&&!important)continue;
        if(p.x<0||p.x>width||p.y<0||p.y>height)continue;
        const text=important?`${p.id} · ${p.name}`:p.id;
        c.font=`${important?'600':'500'} ${important?12:10}px system-ui`;
        const w=Math.min(width-16,c.measureText(text).width+12),h=important?25:20;
        const candidates=[{x:p.x+p.r+9,y:p.y-h/2},{x:p.x-w/2,y:p.y+p.r+9},
          {x:p.x-w-p.r-9,y:p.y-h/2},{x:p.x-w/2,y:p.y-p.r-h-9}]
          .map(b=>({x:clamp(b.x,8,width-w-8),y:clamp(b.y,8,height-h-8),w,h}));
        const overlaps=(a,b)=>a.x<b.x+b.w+3&&a.x+a.w+3>b.x&&a.y<b.y+b.h+2&&a.y+a.h+2>b.y;
        const box=candidates.find(b=>!boxes.some(o=>overlaps(b,o))&&!nodes.some(o=>
          o.id!==p.id&&overlaps(b,{x:o.x-o.r,y:o.y-o.r,w:o.r*2,h:o.r*2})))||(important?candidates[0]:null);
        if(!box)continue;
        boxes.push(box);c.fillStyle=important?'#fff':'#f8fbf9ed';
        c.fillRect(box.x,box.y,box.w,box.h);
        if(important){c.strokeStyle=palette[p.type]||'#64746c';c.lineWidth=1;c.strokeRect(box.x,box.y,box.w,box.h);}
        c.fillStyle=important?'#19332b':'#4f695e';c.textBaseline='middle';
        c.save();c.beginPath();c.rect(box.x+4,box.y,box.w-8,box.h);c.clip();c.fillText(text,box.x+6,box.y+box.h/2);c.restore();
      }
    }
    orientation(width,height) {
      const c=this.ctx,ox=width-46,oy=height-46;
      c.save();c.fillStyle='#ffffffdd';c.beginPath();c.arc(ox,oy,37,0,Math.PI*2);c.fill();
      for(const axis of [{x:1,y:0,z:0,name:'X',color:'#b66461'},{x:0,y:-1,z:0,name:'Y',color:'#3d8c69'},{x:0,y:0,z:1,name:'Z',color:'#487fb3'}]) {
        const a=rotate(axis,this.camera);c.strokeStyle=axis.color;c.lineWidth=1.5;
        this.line({x:ox,y:oy},{x:ox+a.x*24,y:oy+a.y*24});c.fillStyle=axis.color;c.font='600 10px system-ui';c.fillText(axis.name,ox+a.x*30-3,oy+a.y*30);
      }
      c.restore();
    }
  }
  root.Alfa3D={Graph3D,layout,project,pick,types};
  if(typeof module!=='undefined') module.exports=root.Alfa3D;
})(typeof window==='undefined'?globalThis:window);
