"""Conhecimento e intervalos conservadores, em dias/centavos inteiros."""
from __future__ import annotations
from dataclasses import dataclass


class EntradaInvalida(ValueError):
    pass


def exigir(condicao, mensagem):
    if not condicao:
        raise EntradaInvalida(mensagem)


def inteiro(valor, minimo=None):
    exigir(type(valor) is int and (minimo is None or valor >= minimo),
           'Inteiro fora do domínio')
    return valor


@dataclass(frozen=True)
class Intervalo:
    inferior: int | None
    superior: int | None
    evidencias: tuple = ()
    lacunas: tuple = ()

    def somar(self, outro):
        return Intervalo(None if self.inferior is None or outro.inferior is None else self.inferior + outro.inferior,
                         None if self.superior is None or outro.superior is None else self.superior + outro.superior,
                         self.evidencias + outro.evidencias, self.lacunas + outro.lacunas)

    def menos(self, valor):
        return self.somar(Intervalo(-valor, -valor))

    def saida(self, delta=False):
        exato = self.inferior is not None and self.inferior == self.superior
        direcao = 'desconhecida'
        if exato and delta:
            direcao = 'aumento' if self.inferior > 0 else 'reducao' if self.inferior < 0 else 'zero'
        elif not exato and delta:
            if self.inferior is not None and self.inferior > 0:
                direcao = 'aumento'
            elif self.superior is not None and self.superior < 0:
                direcao = 'reducao'
        return dict(estado='exato' if exato else 'direcao' if direcao != 'desconhecida' else 'indeterminado',
                    valor=self.inferior if exato else None, direcao=direcao,
                    evidencias=list({(e['fonte_id'], e['localizador']): e for e in self.evidencias}.values()),
                    lacunas=[] if exato else list(dict.fromkeys(self.lacunas)) or ['Magnitude não determinada'],
                    motivo=None, limites={'inferior': self.inferior, 'superior': self.superior})


def ler(conhecimento, minimo=None):
    c = conhecimento
    exigir(isinstance(c, dict), 'Conhecimento inválido')
    estado = c.get('estado')
    exigir(estado in ('exato', 'direcao', 'indeterminado', 'inaplicavel'), 'Estado desconhecido')
    exigir(isinstance(c.get('evidencias'), list) and isinstance(c.get('lacunas'), list), 'Proveniência ausente')
    if estado == 'exato':
        valor = inteiro(c.get('valor'), minimo)
        exigir(not c['lacunas'] and c['evidencias'], 'Exato exige suporte e nenhuma lacuna')
        exigir(c.get('direcao') == 'desconhecida', 'Entrada absoluta exige direção desconhecida')
        return Intervalo(valor, valor, tuple(c['evidencias']))
    exigir(c.get('valor') is None, 'Lacuna não admite valor')
    if estado == 'inaplicavel':
        exigir(c.get('motivo') and not c['lacunas'] and c.get('direcao') == 'desconhecida', 'Inaplicabilidade inválida')
        raise EntradaInvalida('Atributo quantitativo obrigatório inaplicável')
    exigir(c['lacunas'], 'Lacuna deve ser explícita')
    exigir((estado == 'indeterminado' and c.get('direcao') == 'desconhecida') or
           (estado == 'direcao' and c.get('direcao') in ('aumento', 'reducao')), 'Direção inválida')
    limites = c.get('limites', {})
    lo, hi = limites.get('inferior', minimo), limites.get('superior')
    if lo is not None:
        inteiro(lo, minimo)
    if hi is not None:
        inteiro(hi, minimo)
    exigir(lo is None or hi is None or lo <= hi, 'Limites invertidos')
    exigir(lo != hi or lo is None, 'Intervalo pontual deve ser exato')
    return Intervalo(lo, hi, tuple(c['evidencias']), tuple(c['lacunas']))


def maximo(valores):
    valores = list(valores)
    lo = None if any(v.inferior is None for v in valores) else max(v.inferior for v in valores)
    # Limites inferiores desconhecidos não impedem usar os demais limites conhecidos.
    conhecidos = [v.inferior for v in valores if v.inferior is not None]
    lo = max(conhecidos) if conhecidos else lo
    hi = None if any(v.superior is None for v in valores) else max(v.superior for v in valores)
    return Intervalo(lo, hi, tuple(e for v in valores for e in v.evidencias),
                     tuple(e for v in valores for e in v.lacunas))
