"""H v05 opt-in/offline. Não habilita coleta paga nem altera B/T ou o legado."""
from .contratos import VERSAO,SCHEMA,validar,montar_contexto
from .adaptador import LocalV05,SimuladoV05
from .politica import construir
from .orquestracao import avaliar
from .fronteira import executar_h
