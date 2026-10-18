"""Caminhos e configuração da execução local, sem serviços de notebook."""
import os
from pathlib import Path
import re


def repository_root(start: str | Path | None = None) -> Path:
    current = Path(start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        project = candidate / "TCC_Codigos"
        if (project / "data/project_graph.json").is_file() and (project / "src/tcc_agent").is_dir():
            return candidate
    raise FileNotFoundError("Execute a partir da raiz do repositório TCC ou de uma subpasta.")


def load_local_env(root: str | Path) -> None:
    """Lê KEY=value do .env local; variáveis já exportadas têm precedência.

    Não executa comandos, não expande variáveis e não exibe valores.
    """
    env_file = Path(root) / ".env"
    if not env_file.is_file():
        return
    for number, raw in enumerate(env_file.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError(f"Formato inválido na linha {number} do .env; use KEY=value.")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)
