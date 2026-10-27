from copy import deepcopy
from pathlib import Path
import json,shutil,sqlite3,tempfile,unittest
from diagnostico_etapa9 import executar,LedgerDiagnostico,fingerprint_original,IDS
from piloto_real.ledger import Bloqueio,RESERVA
from interpretacao_no.adaptadores import FalhaTransporte

ROOT=Path(__file__).resolve().parents[2]
SNAP=ROOT/'outputs/etapa9_coleta_20261026/snapshot_pos_parada'


def resposta(payload):
    entrada=json.loads(payload['input'][1]['content'])
    q=dict(estado='indeterminado',valor=None,direcao='desconhecida',evidencias=[],lacunas=['MOCK diagnóstico sem magnitude'],motivo=None)
    if 'contexto'in entrada:
        c=entrada['contexto'];a={k:deepcopy(c[k]) for k in ('execucao_id','evento_id','no_id','revisao','contexto_hash','predecessores_versoes')}
        a.update(schema_version='1.0-proposta',analise_id='MOCK',avaliacao=dict(prazo=q,custo=deepcopy(q)),propostas=[],justificativa='MOCK sem cálculo/efeito de projeto',lacunas=[])
    else:
        a={k:entrada[k] for k in ('execucao_id','projeto_id','versao','evento_id','view_hash')}
        for k in ('fim_base','fim_novo','delta_dias','custo_base','custo_novo','delta_centavos'):
            a[k]={**deepcopy(q),'unidade':'dia_corrido' if k in ('fim_base','fim_novo','delta_dias') else 'BRL_centavo'}
        a['justificativa']='MOCK de contrato, não previsão de IA'
    return dict(id='mock',model='gpt-6-luna',status='completed',output=[dict(type='message',content=[dict(type='output_text',text=json.dumps(a))])],usage=dict(input_tokens=100,output_tokens=100,total_tokens=200,input_tokens_details=dict(cached_tokens=0,cache_write_tokens=0),output_tokens_details=dict(reasoning_tokens=50)))


class Fake:
    def __init__(self,modo=None):self.modo=modo;self.calls=[]
    def post(self,path,payload,timeout):
        self.calls.append((path,deepcopy(payload),timeout))
        if path:return dict(object='response.input_tokens',input_tokens=100)
        if self.modo=='timeout':raise FalhaTransporte('timeout','Timeout MOCK')
        if self.modo=='interrupt':raise KeyboardInterrupt()
        r=resposta(payload)
        if self.modo=='incomplete':r['status']='incomplete'
        if self.modo=='formato':r['output'][0]['content'][0]['text']='{invalid'
        if self.modo=='modelo':r['model']='outro_modelo'
        return r


class Diagnostico(unittest.TestCase):
    def copiar(self,tmp):
        p=Path(tmp)/'carteira';p.mkdir()
        for n in ('ledger.sqlite','plano.json','manifesto.json'):shutil.copyfile(SNAP/n,p/n)
        return p,Path(tmp)/'diagnostico'
    def test_dois_validos_payload_identico_saldo_agregado_original_intacto(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,o=self.copiar(tmp);f=Fake();r=executar(p,o,http=f,coletar=True)
            self.assertTrue(r['original_preservado']);self.assertEqual([x['estado']for x in r['resultados']],['completa_valida']*2)
            self.assertEqual(r['orcamento_acumulado']['tentativas_reservadas'],15)
            self.assertLess(r['orcamento_acumulado']['comprometido_nanoUSD'],196729825)
            with LedgerDiagnostico(p)as l:
                self.assertEqual([x[1]for x in f.calls if x[0]==''],[x['payload']for x in l.fontes])
                self.assertEqual(l.db.execute('SELECT count(*) FROM slots').fetchone()[0],90)
                self.assertEqual(l.db.execute('SELECT count(*) FROM parada').fetchone()[0],1)
            self.assertTrue(all(179<call[2]<=180 for call in f.calls))
            n=len(f.calls);r2=executar(p,o,http=f,coletar=True)
            self.assertEqual(len(f.calls),n);self.assertEqual(r2,r)
    def test_primeira_timeout_incomplete_formato_desvio_nao_faz_segunda(self):
        for modo in ('timeout','incomplete','formato','modelo'):
            with self.subTest(modo=modo),tempfile.TemporaryDirectory()as tmp:
                p,o=self.copiar(tmp);f=Fake(modo);r=executar(p,o,http=f,coletar=True)
                self.assertEqual(len(f.calls),2)
                self.assertEqual(r['resultados'][1]['estado'],'nao_executada_primeira_sem_resposta_valida')
                self.assertEqual(r['orcamento_acumulado']['tentativas_reservadas'],14)
                if modo=='timeout':self.assertEqual(r['orcamento_acumulado']['comprometido_nanoUSD'],163729825+RESERVA)
    def test_interrupt_retomada_sem_replay_e_reserva_mantida(self):
        with tempfile.TemporaryDirectory()as tmp:
            p,o=self.copiar(tmp);f=Fake('interrupt')
            with self.assertRaises(KeyboardInterrupt):executar(p,o,http=f,coletar=True)
            g=Fake();r=executar(p,o,http=g,coletar=True)
            self.assertFalse(g.calls);self.assertEqual(r['resultados'][0]['estado'],'interrompida_sem_replay')
            self.assertEqual(r['orcamento_acumulado']['comprometido_nanoUSD'],163729825+RESERVA)
    def test_lock_mesma_carteira_e_segunda_antes_da_primeira_bloqueados(self):
        with tempfile.TemporaryDirectory()as tmp:
            p,o=self.copiar(tmp)
            with LedgerDiagnostico(p)as l:
                with self.assertRaises(Bloqueio):LedgerDiagnostico(p)
                with self.assertRaises(Bloqueio):l.iniciar_diag(IDS[1])
                with self.assertRaises(Bloqueio):l.iniciar_diag('slot_original')
                self.assertTrue(l.preservar_original())
    def test_orcamento_global_insuficiente_nao_envia(self):
        with tempfile.TemporaryDirectory()as tmp:
            p,o=self.copiar(tmp)
            with LedgerDiagnostico(p)as l:
                with l.db:l.db.execute('INSERT INTO chamadas(slot,request_hash,estado,comprometido) VALUES(?,?,?,?)',('outro','x','custo_desconhecido',4900000000))
            f=Fake();r=executar(p,o,http=f,coletar=True)
            self.assertFalse(f.calls);self.assertEqual(r['resultados'][0]['estado'],'erro_operacional')
    def test_payload_modificado_rejeitado_e_sem_carteira_nova(self):
        with tempfile.TemporaryDirectory()as tmp:
            p,o=self.copiar(tmp)
            with LedgerDiagnostico(p)as l:
                l.iniciar_diag(IDS[0])
                with self.assertRaises(Bloqueio):l.reservar(IDS[0],'hash_alterado')
            with self.assertRaises(Bloqueio):LedgerDiagnostico(Path(tmp)/'carteira_nova')
    def test_preparacao_nao_envia_nem_reserva(self):
        with tempfile.TemporaryDirectory()as tmp:
            p,o=self.copiar(tmp);r=executar(p,o,coletar=False)
            self.assertEqual(r['estado'],'adendo_preparado_sem_rede');self.assertEqual(r['orcamento_acumulado']['tentativas_reservadas'],13)


if __name__=='__main__':unittest.main()
