'use strict';
const $ = id => document.getElementById(id);
const esc = value => String(value ?? '—').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money = v => v == null ? 'Indeterminado' : (v / 100).toLocaleString('pt-BR', {style:'currency',currency:'BRL'});
const day = v => v == null ? 'Indeterminado' : `D${v}`;
const fmt = v => JSON.stringify(v, null, 2);
let catalog, project, result, session = null, inspected = 'SUP_MOTOR';
let entries = new Set(), pending = new Set(), dirty = false, busy = false, loading = true;
let poll = null, playback = null, step = 0, caseGeneration = 0, lastRevision = null;
const currentCase = () => catalog.casos.find(c => c.id === $('cenario').value);
const name = id => catalog.catalogo.find(n => n.id === id)?.nome || id;
const executable = id => catalog.catalogo.some(n => n.id === id);
const editable = () => !loading && !busy && (!session || session.estado === 'pronta');
const trace = () => (result?.rastro_orquestracao || []).filter(t => ['interpretado','reuso_cache'].includes(t.processamento) && ['interpretado','reutilizado_com_vinculo'].includes(result.estados_selecao?.[t.no_id]));
const statusNames = {interpretado:'Interpretado',reutilizado_com_vinculo:'Reutilizado com contexto válido',fora_do_escopo_justificado:'Fora da região de interpretação',pendente:'Pendente',bloqueado_por_limite:'Pendente pelo limite'};

async function api(path, body) {
  const r = await fetch(path, body ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)} : {});
  const data = await r.json();
  if (!r.ok) throw Error(data.erro || r.statusText);
  return data;
}
function error(e) { $('erro').textContent = e.message || String(e); }
function clearError() { $('erro').textContent = ''; }
function markDirty() { dirty = true; updateButtons(); selectionSummary(); }
function selectionSummary() {
  $('selectionSummary').textContent = `${entries.size} entrada(s) · máximo ${$('limite').value || '—'} nós${dirty ? ' · confirmar alterações' : ''}`;
}
function updateButtons() {
  const ready = !loading && !busy && session?.estado === 'pronta';
  const over = session && session.solicitacoes_previstas > Number($('chamadas').value);
  $('prever').disabled = !editable();
  $('executar').disabled = !ready || dirty || session.selecao_confirmada === false || over;
  $('sugerir').disabled = !editable();
  $('nova').disabled = loading || busy || session?.estado === 'executando';
  $('cenario').disabled = loading || busy || session?.estado === 'executando';
  for (const id of ['limite','chamadas','escopo','todos']) $(id).disabled = !editable();
  $('prosseguir').disabled = busy || !pending.size;
  $('cancelar').hidden = !session || !['pronta','pausada','executando','falha'].includes(session.estado);
  $('export').disabled = !result?.execucao;
  if (ready && over) error('A região mais a sugestão excede o orçamento. Ajuste o máximo de solicitações em Entradas e limites.');
}
function choices() {
  const box = $('nos'), search = $('busca').value.toLocaleLowerCase();
  box.replaceChildren();
  for (const n of catalog.catalogo) {
    if (![n.id,n.nome,n.tipo].join(' ').toLocaleLowerCase().includes(search)) continue;
    const label = document.createElement('label'); label.className = 'nodechoice';
    const input = document.createElement('input'); input.type = 'checkbox'; input.checked = entries.has(n.id); input.disabled = !editable();
    input.onchange = () => { input.checked ? entries.add(n.id) : entries.delete(n.id); markDirty(); graph(); detail(); };
    const text = document.createElement('span'); text.textContent = n.nome;
    const small = document.createElement('small'); small.textContent = `${n.id} · ${Alfa3D.types[n.tipo] || n.tipo}`; text.append(small);
    label.append(input, text); box.append(label);
  }
}
function sourcesHtml(sources) {
  return sources.map(f => `<div class="source"><b>${esc(f.documento_id || 'Fonte')} · v${esc(f.versao || '1')} · ${esc(f.trecho_id || f.id)} ${esc(f.localizador)}</b><br>${esc(f.texto || f.trecho)}</div>`).join('');
}
function getSources() {
  const all = {};
  for (const n of project.grafo.nodes) if (n.documento) for (const t of n.documento.trechos) all[t.id] = {...t,documento_id:n.documento.id,versao:n.documento.versao,trecho_id:t.id};
  return all;
}
const scene = new Alfa3D.Graph3D($('graph'), {onSelect:selectNode,onView:view => {
  $('graphCount').textContent = `${view.visible}/${view.total} entidades no enquadramento · ${view.edges} relações visíveis · ${view.temporal} temporais`;
  $('graphZoom').textContent = `${Math.round(view.zoom * 100)}%`;
  $('graphTooltip').hidden = !view.hover;
  if (view.hover) $('graphTooltip').textContent = `${Alfa3D.types[view.hover.type] || view.hover.type} · ${view.hover.name} · ${view.hover.id}`;
}});
function graph() {
  if (!project || !result) return;
  $('nodePicker').value = inspected;
  $('selectionStatus').textContent = `Inspecionando: ${inspected}${entries.has(inspected) ? ' · ponto de entrada' : ''}`;
  scene.update({result:{...result,grafo:project.grafo,rastro_orquestracao:trace()},graphKey:project,
    selected:inspected,step,documental:$('docEdges').checked,contextual:$('contextEdges').checked,labels:$('showLabels').checked,
    seeds:entries,region:new Set(session?.regiao.nos || []),pending:new Set(session && session.estado !== 'pronta' ? session.pendentes : [])});
}
function selectNode(id) { inspected = id; graph(); detail(); }
function detail() {
  if (!project) return;
  const n = project.grafo.nodes.find(n => n.id === inspected); if (!n) return;
  $('nodeTitle').textContent = n.name;
  $('toggleEntry').hidden = !executable(n.id); $('toggleEntry').disabled = !editable();
  $('toggleEntry').textContent = entries.has(n.id) ? 'Remover das entradas' : 'Selecionar como entrada';
  $('entryStatus').textContent = executable(n.id) ? `${n.id} · ${entries.has(n.id) ? 'Entrada selecionada' : 'Ponto executável'}` : `${n.id} · Entidade de contexto/documento: inspecione seus vínculos.`;
  const all = getSources();
  if (n.documento) {
    const d = n.documento;
    $('detail').innerHTML = `<p><span class="pill">${esc(d.papel)}</span> v${esc(d.versao)} · ${esc(d.formato)}</p><p class="subtle">${esc(d.autoria)} · versão anterior: ${esc(d.anterior || 'nenhuma')}.</p>${sourcesHtml(d.trechos.map(t => ({...t,documento_id:d.id,versao:d.versao,trecho_id:t.id})))}<h3>Vínculos</h3><pre>${esc(fmt(project.grafo.edges.filter(e => e.source === n.id || e.target === n.id).map(e => ({relacao:e.type,origem:e.source,destino:e.target,trecho:e.trecho}))))}</pre>`;
    return;
  }
  const t = result.rastro_orquestracao?.find(t => t.no_id === n.id), base = result.baseline_nos?.[n.id], next = result.estado_projetado_nos?.[n.id];
  let html = `<p><span class="pill">${esc(Alfa3D.types[n.type] || n.type)}</span></p>`;
  const state = result.estados_selecao?.[n.id];
  if (state) html += `<p class="status-local">${esc(statusNames[state] || state)}</p>`;
  if (session?.regiao.motivos[n.id]) html += `<p class="subtle">${esc(session.regiao.motivos[n.id].join('; '))}</p>`;
  if (base) html += `<h3>Estado temporal</h3><p>Base: ${day(base.inicio.valor)} → ${day(base.fim.valor)}<br>Projeção auxiliar condicional: ${day(next?.inicio?.valor)} → ${day(next?.fim?.valor)}<br>Folga na base: ${esc(result.folgas_base_dias?.[n.id])} dias</p><p class="hint">A projeção auxiliar não confirma um total quando há pendências.</p>`;
  html += `<details open><summary>Parâmetros e fontes</summary><pre>${esc(fmt(n.parametros || {}))}</pre>${sourcesHtml((n.fontes || []).map(r => all[r.fonte_id]).filter(Boolean))}</details>`;
  if (t) html += `<h3>Análise local</h3><p>${esc(t.analise?.justificativa || t.motivo || t.processamento)}</p>${t.analise ? `<details><summary>Propostas e evidências</summary><pre>${esc(fmt(t.analise.propostas))}</pre></details><details><summary>Fontes consultadas</summary>${sourcesHtml(t.fontes || [])}</details>` : '<p class="subtle">Este nó não recebeu interpretação local nesta passagem.</p>'}`;
  const effects = (result.propagacao || []).filter(e => e.origem === n.id || e.destino === n.id);
  if (effects.length) html += `<h3>Efeitos recebidos e transmitidos</h3><pre>${esc(fmt(effects.map(e => ({origem:e.origem,destino:e.destino,estado:e.estado,regra:e.regra}))))}</pre>`;
  const cost = (result.efeitos_financeiros || []).filter(e => e.proprietario === n.id);
  if (cost.length) html += `<h3>Efeitos financeiros sob custódia</h3><pre>${esc(fmt(cost))}</pre>`;
  $('detail').innerHTML = html;
}
function stopPlayback() { clearInterval(playback); playback = null; $('play').textContent = '▶ Reproduzir análise'; }
function updateStep() {
  const steps = trace(); step = Math.min(Number($('step').value), steps.length);
  $('stepLabel').textContent = `${step} / ${steps.length}`;
  $('stepText').textContent = step ? `${steps[step-1].no_id}: ${steps[step-1].processamento === 'reuso_cache' ? 'resposta reutilizada' : 'interpretação simulada'}. Reprodução do rastro; cartões mostram o resultado disponível.` : 'A reprodução mostra apenas interpretações registradas; não executa novas chamadas.';
  graph();
}
function renderReview() {
  const r = result, docs = r.verificacao_documental;
  $('reviewVersion').textContent = docs?.afirmacoes?.[0]?.unidade.split(':')[0] || '';
  $('claims').innerHTML = docs ? docs.afirmacoes.map(a => `<tr><td>${esc(a.trecho_id)}</td><td>${esc(a.conteudo_atual)}</td><td>${a.calculado?.estado === 'exato' ? a.afirmacao.unidade === 'BRL_centavo' ? money(a.calculado.valor) : esc(a.calculado.valor) : 'Não determinado'}</td><td><span class="pill ${esc(a.estado)}">${esc(a.estado.replaceAll('_',' '))}</span>${a.motivo ? `<br><small>${esc(a.motivo)}</small>` : ''}</td></tr>`).join('') : '<tr><td colspan="4" class="empty">Execute a análise para verificar as afirmações.</td></tr>';
  $('recommendations').innerHTML = !docs ? '' : docs.recomendacoes.length ? docs.recomendacoes.map(x => `<article class="recommendation"><h3>${esc(x.documento_id)} v${esc(x.versao_base)} · ${esc(x.localizador)} · ${esc(x.campo)}</h3><p class="before">Atual: ${esc(x.conteudo_atual)}</p><p class="after">Proposta: ${esc(x.alteracao_proposta)}</p><p>${esc(x.justificativa)}</p><span class="pill revisar">Aguardando validação humana · não executada</span><details><summary>Evidências e cálculo (${x.evidencias.length} trechos)</summary>${sourcesHtml(x.evidencias)}<pre>${esc(fmt(x.calculo_ref))}</pre></details></article>`).join('') : '<p class="empty">Nenhuma revisão recomendada. Confira os campos não verificáveis e as pendências antes de concluir ausência de impacto.</p>';
  $('triage').innerHTML = (docs?.triagem_outros_artefatos || []).map(x => `<p><b>${esc(x.documento_id)}</b>: ${esc(x.estado)}<br>${esc(x.regra)}</p>`).join('') || '<p class="empty">Triagem disponível após a execução.</p>';
  $('costBook').innerHTML = r.livro_parcelas?.length ? `<table><thead><tr><th>Obrigação única</th><th>Base</th><th>Novo</th><th>Impacto</th></tr></thead><tbody>${r.livro_parcelas.map(p => `<tr><td>${esc(p.parcela_id)} ${esc(p.regra_id || '')}</td><td>${money(p.base_centavos)}</td><td>${money(p.novo.valor)}</td><td>${money(p.delta.valor)}</td></tr>`).join('')}</tbody></table>` : '<p class="empty">Sem fechamento financeiro disponível.</p>';
  $('routing').textContent = fmt(session ? {regiao:session.regiao,fechamento:r.registro_operacional?.fechamento_final,decisoes:r.registro_operacional?.decisoes,pendencias:r.pendencias_execucao} : {});
}
function metrics() {
  const r = result, done = !!r?.execucao;
  $('finish').textContent = done ? `${day(project.fim_base.valor)} → ${day(r.fim_novo?.valor)}` : day(project.fim_base.valor);
  $('deltaDays').textContent = !done ? 'Referência inicial · aguardando análise' : `Prazo ${r.completude?.prazo || r.execucao.estado} · ${r.delta_dias?.valor == null ? 'impacto indeterminado' : 'impacto de '+r.delta_dias.valor+' dias'}`;
  $('cost').textContent = money(done ? r.custo_novo?.valor : project.custo_base.valor);
  $('deltaCost').textContent = !done ? 'Referência inicial · aguardando análise' : `Custo ${r.completude?.custo || r.execucao.estado} · impacto ${money(r.delta_centavos?.valor)}`;
  const count = Object.values(r.estados_selecao || {}).filter(x => ['interpretado','reutilizado_com_vinculo'].includes(x)).length;
  $('coverage').textContent = `${count} / ${session?.regiao.nos.length || '—'} nós da região`;
  $('recsCount').textContent = `${r.verificacao_documental?.recomendacoes.length || 0} recomendações · ${catalog.catalogo.length} pontos elegíveis`;
}
function continuation() {
  const paused = session?.estado === 'pausada';
  $('continuationControls').hidden = !paused; $('prosseguir').hidden = !paused;
  const box = $('pendencias'); box.replaceChildren();
  if (paused) {
    for (const n of session.pendentes) {
      const label = document.createElement('label'); label.className = 'pendingchoice';
      const input = document.createElement('input'); input.type = 'checkbox'; input.checked = pending.has(n); input.disabled = busy;
      input.onchange = () => { input.checked ? pending.add(n) : pending.delete(n); continuationEstimate(); updateButtons(); };
      const text = document.createElement('span'); text.textContent = `${name(n)} · ${n}`;
      const deps = session.dependencias_pendentes?.[n] || [];
      if (deps.length) { const small = document.createElement('small'); small.textContent = ' — depende de '+deps.join(', '); text.append(small); }
      label.append(input,text); box.append(label);
    }
  } else if (session?.pendentes?.length) box.innerHTML = `<p class="subtle">${session.pendentes.length} nós permanecem pendentes. Consulte a cobertura registrada.</p>`;
  continuationEstimate();
}
function continuationEstimate() {
  $('continuationEstimate').textContent = session?.estado === 'pausada' ? `${pending.size} nós selecionados para continuar. Previsão mínima: ${pending.size} solicitações locais adicionais; dependências e reanálises podem exigir nova escolha. O limite informado é acumulado.` : '';
}
function renderSession(s) {
  session = s; localStorage.setItem('alfa_v2_session', s.id);
  if (s.estado !== 'executando') pending = new Set([...pending].filter(n => s.pendentes.includes(n)));
  result = s.resultado.execucao ? {...project,...s.resultado,grafo:project.grafo} : project;
  const labels = {pronta:'Entradas confirmadas. Pronto para analisar.',executando:'Análise em andamento'+(s.em_voo ? ' · '+name(s.em_voo.no_id) : ''),pausada:'Análise parcial: escolha pendentes para continuar ou cancele.',concluida:'Processamento concluído. Confira a completude dos resultados.',cancelada:'Análise cancelada. Resultados parciais preservados.',falha:'Falha na análise. Consulte as pendências.',obsoleta:'Dados mudaram. Inicie uma nova análise.'};
  $('estado').textContent = s.selecao_confirmada === false ? 'Sugestão recebida: revise as entradas e confirme antes de executar.' : labels[s.estado] || s.estado;
  $('executionStatus').textContent = labels[s.estado] || s.estado;
  $('consumo').textContent = `${s.consumo.solicitacoes_simuladas} solicitações simuladas · ${s.consumo.chamadas_api} chamadas de API · ${s.consumo.segundos.toFixed(2)} s de software · nenhum documento oficial alterado`;
  $('contagem').textContent = `${s.regiao.nos.length} na região / ${s.selecao.maximo_disponivel} elegíveis`;
  $('preview').textContent = `${s.regiao.nos.length} interpretações locais previstas; teto de ${s.selecao.limite_nos_analise} nós. Previsão total de ${s.solicitacoes_previstas} solicitações, incluindo consumo anterior.`;
  if (lastRevision !== s.revisao) {
    lastRevision = s.revisao; stopPlayback(); step = trace().length; $('step').max = step; $('step').value = step;
    $('continuationLimit').value = s.selecao.limite_nos_analise; $('continuationLimit').max = s.selecao.maximo_disponivel;
    $('continuationCalls').value = s.limites.max_solicitacoes;
  }
  for (const id of ['play','prev','next','step']) $(id).disabled = !trace().length || busy || s.estado === 'executando';
  metrics(); renderReview(); continuation(); choices(); selectionSummary(); detail(); updateStep(); updateButtons();
  if (s.erro_interface) error(s.erro_interface);
}
async function setCase(restore = null) {
  const generation = ++caseGeneration; loading = true; clearTimeout(poll); poll = null; stopPlayback(); busy = false;
  session = null; project = null; result = null; pending = new Set(); dirty = false; lastRevision = null; clearError();
  localStorage.removeItem('alfa_v2_session'); $('busca').value = ''; $('executionStatus').textContent = 'Nenhuma execução iniciada.';
  $('estado').textContent = 'Carregando o projeto…'; updateButtons();
  const c = currentCase();
  try {
    const p = await api('/api/projeto?cenario='+encodeURIComponent(c.id)); if (generation !== caseGeneration) return;
    project = p; result = p; entries = new Set(restore?.selecao.nos_entrada || c.mencoes); inspected = [...entries][0] || catalog.catalogo[0].id;
    $('limite').value = restore?.selecao.limite_nos_analise || catalog.catalogo.length; $('limite').max = catalog.catalogo.length;
    $('chamadas').value = restore?.limites.max_solicitacoes ?? 32; $('escopo').value = restore?.selecao.escopo || 'impacto_do_evento';
    $('maximo').textContent = `Máximo disponível para análise: ${catalog.catalogo.length} nós. Total do grafo com documentos: ${p.grafo.nodes.length}.`;
    $('origin').innerHTML = `<p><b>${esc(p.documento_origem.nome)}</b> · ${esc(p.documento_origem.id)} · v${esc(p.documento_origem.versao)}</p>${p.documento_origem.trechos.map(t => `<blockquote>${esc(t.texto)}<br><small>${esc(t.id)} · ${esc(t.localizador)}</small></blockquote>`).join('')}`;
    $('nodePicker').replaceChildren();
    for (const [type,label] of Object.entries(Alfa3D.types)) { const group = document.createElement('optgroup'); group.label = label; for (const n of p.grafo.nodes.filter(n => n.type === type)) group.append(new Option(`${n.name} · ${n.id}`, n.id)); if (group.children.length) $('nodePicker').append(group); }
    step = 0; $('step').value = 0; $('step').max = 0; for (const id of ['play','prev','next','step']) $(id).disabled = true;
    $('estado').textContent = 'Ainda não iniciada. Selecione as entradas e confirme a região.'; $('consumo').textContent = 'Simulação offline · zero chamadas pagas';
    $('preview').textContent = 'Inspecione um nó para incluí-lo nas entradas ou use a lista de seleção.'; $('contagem').textContent = '';
    loading = false;
    if (restore) { renderSession(restore); if (restore.estado === 'executando') { busy = true; pollSession(restore.revisao-1); } }
    else { choices(); graph(); detail(); selectionSummary(); metrics(); renderReview(); continuation(); updateStep(); updateButtons(); }
  } catch (e) { loading = false; error(e); updateButtons(); }
}
async function prepare() {
  clearError();
  const body = {cenario:currentCase().id,entradas:[...entries],limite:$('limite').value,max_solicitacoes:Number($('chamadas').value),escopo:$('escopo').value,confirmar_divergencia:$('escopo').value === 'teste_delimitado'};
  const s = await api(session ? '/api/selecionar' : '/api/preparar', session ? {...body,id:session.id} : body);
  dirty = false; renderSession(s); return s;
}
async function pollSession(startRevision) {
  if (!session) return;
  try {
    const s = await api('/api/sessao?id='+encodeURIComponent(session.id));
    const ended = s.estado !== 'executando' && (s.revisao > startRevision || s.erro_interface);
    if (ended) busy = false;
    renderSession(s);
    if (!ended) poll = setTimeout(() => pollSession(startRevision), 650);
  } catch(e) { busy = false; error(e); updateButtons(); }
}
async function run(continuar) {
  if (busy || !session) return;
  clearError();
  if (!continuar && (dirty || session.selecao_confirmada === false)) return error('Confirme as entradas antes de executar.');
  if (continuar && !pending.size) return error('Selecione ao menos um nó pendente.');
  const body = {id:session.id,acao_id:crypto.randomUUID(),revisao:session.revisao,limite:$(continuar ? 'continuationLimit' : 'limite').value,max_solicitacoes:Number($(continuar ? 'continuationCalls' : 'chamadas').value)};
  if (continuar) body.selecionados = [...pending];
  busy = true; stopPlayback(); updateButtons(); choices(); detail();
  try { await api('/api/executar', body); pollSession(body.revisao); }
  catch(e) { busy = false; error(e); updateButtons(); }
}
function expandPanel(expand) {
  document.querySelector('.workspace').classList.toggle('expanded',expand); document.body.classList.toggle('graph-expanded',expand);
  $('fullscreen').textContent = expand ? '⛶ Reduzir painel' : '⛶ Ampliar painel'; $('fullscreen').setAttribute('aria-pressed',String(expand)); scene.invalidate();
}
$('nodePicker').onchange = () => selectNode($('nodePicker').value);
$('toggleEntry').onclick = () => { if (!editable() || !executable(inspected)) return; entries.has(inspected) ? entries.delete(inspected) : entries.add(inspected); markDirty(); choices(); graph(); detail(); };
for (const id of ['docEdges','contextEdges','showLabels']) $(id).onchange = graph;
$('orbitLeft').onclick=()=>scene.orbit(-.18,0); $('orbitRight').onclick=()=>scene.orbit(.18,0);
$('orbitUp').onclick=()=>scene.orbit(0,-.18); $('orbitDown').onclick=()=>scene.orbit(0,.18);
$('zoomIn').onclick=()=>scene.zoom(1.2); $('zoomOut').onclick=()=>scene.zoom(1/1.2); $('resetView').onclick=()=>scene.reset();
$('fullscreen').onclick=()=>expandPanel(!document.querySelector('.workspace').classList.contains('expanded'));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.querySelector('.workspace').classList.contains('expanded')){expandPanel(false);$('fullscreen').focus();}});
$('step').oninput=()=>{stopPlayback();updateStep();}; $('prev').onclick=()=>{stopPlayback();$('step').value=Math.max(0,step-1);updateStep();}; $('next').onclick=()=>{stopPlayback();$('step').value=Math.min(trace().length,step+1);updateStep();};
$('play').onclick=()=>{if(playback){stopPlayback();return;}if(step===trace().length){$('step').value=0;updateStep();}$('play').textContent='Ⅱ Pausar';playback=setInterval(()=>{$('step').value=step+1;updateStep();if(step===trace().length)stopPlayback();},650);};
$('prever').onclick=()=>prepare().catch(error); $('executar').onclick=()=>run(false); $('prosseguir').onclick=()=>run(true);
$('nova').onclick=()=>setCase(); $('cenario').onchange=()=>setCase(); $('busca').oninput=choices;
$('limite').oninput=markDirty; $('escopo').onchange=markDirty; $('todos').onclick=()=>{$('limite').value=catalog.catalogo.length;markDirty();};
$('chamadas').oninput=()=>{clearError();updateButtons();};
$('selectPending').onclick=()=>{pending=new Set(session.pendentes);continuation();updateButtons();};
$('sugerir').onclick=async()=>{if(!editable())return;try{clearError();if(!session)await prepare();markDirty();busy=true;updateButtons();const suggestion=await api('/api/sugerir',{id:session.id,pedido_id:crypto.randomUUID()});entries=new Set(suggestion.sugestoes.map(x=>x.no_id));const s=await api('/api/sessao?id='+session.id);busy=false;renderSession(s);document.querySelector('.selection-config').open=true;}catch(e){busy=false;error(e);updateButtons();}};
$('cancelar').onclick=async()=>{try{clearError();const s=await api('/api/cancelar',{id:session.id});if(s.estado==='cancelada'){busy=false;clearTimeout(poll);}renderSession(s);}catch(e){error(e);}};
$('export').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([fmt({...session,resultado:result})],{type:'application/json'}));a.download=`Alfa-v2-${session.cenario_id}-${session.id}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
(async()=>{try{catalog=await api('/api/catalogo');for(const c of catalog.casos)$('cenario').append(new Option(c.id+' · '+c.relato.slice(0,55),c.id));$('cenario').value='D02';const saved=localStorage.getItem('alfa_v2_session');let restore=null;if(saved){try{restore=await api('/api/sessao?id='+encodeURIComponent(saved));$('cenario').value=restore.cenario_id;}catch{localStorage.removeItem('alfa_v2_session');}}await setCase(restore);}catch(e){error(e);}})();
