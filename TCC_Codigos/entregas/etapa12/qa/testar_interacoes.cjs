/* Testes de integração das funções de apresentação com um duplo mínimo de DOM.
   Não inicia navegador e não comprova renderização CSS. Nenhuma rede é permitida. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
class Element {
  constructor(tag){this.tagName=tag;this.children=[];this.attributes={};this.dataset={};this._text='';this.disabled=false;}
  set textContent(t){this._text=String(t??'');this.children=[];}
  get textContent(){return this._text+this.children.map(x=>x.textContent??String(x)).join(' ');}
  append(...xs){for(const x of xs){this.children.push(x);if(typeof x==='object')x.parent=this;}}
  replaceChildren(...xs){this._text='';this.children=[];this.append(...xs);}
  setAttribute(k,v){this.attributes[k]=String(v);if(k.startsWith('data-'))this.dataset[k.slice(5)]=String(v);}
  showModal(){this.open=true;} close(){this.open=false;}
  click(){if(!this.disabled)this.onclick?.();if(this.tagName==='a'&&this.download)downloads.push(this.download);}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(x=>x!==this);}
}
const walk=e=>[e,...e.children.filter(x=>x instanceof Element).flatMap(walk)];
const html=fs.readFileSync(path.join(root,'demonstracao/index.html'),'utf8');
const ids=Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m=>[m[1],new Element('div')]));
const tabs=[...html.matchAll(/<button data-tab="([^"]+)"[^>]*>([^<]+)/g)].map(m=>{const e=new Element('button');e.dataset.tab=m[1];e.textContent=m[2];return e;});
const downloads=[],blobs=[],body=new Element('body');body.append(...Object.values(ids),...tabs);
let printed=0;
const document={body,createElement:t=>new Element(t),createElementNS:(_,t)=>new Element(t),getElementById:id=>ids[id]||walk(body).find(x=>x.id===id),querySelectorAll:s=>{assert.equal(s,'[data-tab]');return tabs;}};
const blocked=()=>{throw Error('A apresentação tentou usar rede ou transporte');};
const context={window:{print:()=>printed++},document,Node:Element,Intl,Map,Set,JSON,Math,Number,Blob,URL:{createObjectURL:b=>{blobs.push(b);return 'blob:teste';},revokeObjectURL:()=>{}},setTimeout:fn=>fn(),fetch:blocked,XMLHttpRequest:blocked,WebSocket:blocked};
vm.createContext(context);
for(const name of ['dados.js','app.js'])vm.runInContext(fs.readFileSync(path.join(root,'demonstracao',name),'utf8'),context,{filename:name});
const D=context.window.EXPERIMENTO;
const show=name=>tabs.find(x=>x.dataset.tab===name).click();
const text=()=>ids.painel.textContent;
const buttons=()=>walk(ids.painel).filter(x=>x.tagName==='button');
let states=0,sources=0,steps=0;
for(let i=0;i<3;i++){
  ids.caso.value=String(i);ids.caso.onchange();
  show('comparacao');states++;assert.equal(walk(ids.painel).filter(x=>x.tagName==='article').length,3);
  assert(!text().includes('undefined'));assert(text().includes('Resposta completa')||text().includes('Resposta parcial'));
  if(i===1){assert.equal(text().split('Resposta inválida').length-1,2);assert(text().includes('Consultar resposta rejeitada'));assert(text().includes('Indeterminado'));assert(!text().includes('Total novo: R$ 0'));}
  if(i===2){assert(text().includes('116,00'));assert(text().includes('0 dias'));}
  const source=buttons().find(x=>x.className==='source');source.click();assert(ids['fonte-dialog'].open);assert(ids['fonte-text'].textContent.length>20);ids['fechar-fonte'].click();assert(!ids['fonte-dialog'].open);
  show('cadeia');states++;
  for(let k=0;k<6;k++){
    if(k)buttons().find(x=>x.textContent==='Próximo →').click();
    steps++;assert(text().includes(`Passo ${k+1} de 6`));assert(text().includes('Livro de parcelas únicas'));
    assert.equal(walk(ids.painel).filter(x=>x.tagName==='g').length,6);assert(!text().includes('undefined'));
    const h=D.cases[i].records.H.resultado,n=h.resultados_nos.find(n=>n.no_id===h.rastro_orquestracao[k].no_id);
    assert(text().includes('D'+n.fim.valor));
    const b=buttons().find(x=>x.className==='source');assert(b);b.click();assert(!ids['fonte-text'].textContent.includes('não disponível'));ids['fechar-fonte'].click();sources++;
  }
  assert(buttons().find(x=>x.textContent==='Próximo →').disabled);
  const node=walk(ids.painel).find(x=>x.tagName==='g');node.onkeydown({key:'Enter',preventDefault(){}});assert(text().includes('Passo 1 de 6'));
  show('fontes');states++;
  for(const c of ['B','H','T']){const select=document.getElementById('condicao-fonte');select.value=c;select.onchange();assert(walk(ids.painel).filter(x=>x.tagName==='article').length>0);assert(!text().includes('undefined'));sources++;}
  show('avaliacao');states++;assert(text().includes('3/3'));assert(text().includes('2/2'));assert(text().includes('4.567653865'));assert(text().includes('0.432346135'));
  ids.exportar.click();assert.equal(downloads.at(-1),D.cases[i].id+'-evidencias.json');
}
ids.imprimir.click();assert.equal(printed,1);assert.equal(blobs.length,3);
(async()=>{for(let i=0;i<3;i++){const obj=JSON.parse(await blobs[i].text());assert.equal(obj.caso.id,D.cases[i].id);assert.equal(obj.auditorias.length,6);assert.equal(obj.selo_origem,D.source_seal_sha256);}
const report={ok:true,ambiente:'Node com duplo mínimo de DOM; não é teste visual de navegador',casos:3,areas_caso:states,passos_H:steps,consultas_fontes:sources,exportacoes:3,chamadas_rede:0};fs.writeFileSync(path.join(__dirname,'interacoes.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));})().catch(e=>{console.error(e);process.exitCode=1;});
