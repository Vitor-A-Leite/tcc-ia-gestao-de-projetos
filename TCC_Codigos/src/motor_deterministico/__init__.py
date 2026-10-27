"""Motor puro de prazo/custo. Sem importação do pipeline legado ou adaptador LLM."""
from .motor import calcular, preparar
from .conhecimento import EntradaInvalida

__all__ = ['calcular', 'preparar', 'EntradaInvalida']
