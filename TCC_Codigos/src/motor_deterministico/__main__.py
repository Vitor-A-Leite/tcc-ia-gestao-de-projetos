"""CLI explícita: recebe somente estado e, opcionalmente, fixture manual selecionada."""
import argparse
import json
from pathlib import Path
from .motor import calcular


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('estado', type=Path)
    parser.add_argument('--entrada-manual', type=Path)
    args = parser.parse_args()
    estado = json.loads(args.estado.read_text())
    entrada = json.loads(args.entrada_manual.read_text()) if args.entrada_manual else {}
    resultado = calcular(estado, entrada.get('evento'), entrada.get('propostas', []), entrada.get('politica'))
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 2 if resultado['execucao']['estado'] == 'erro' else 0


if __name__ == '__main__':
    raise SystemExit(main())
