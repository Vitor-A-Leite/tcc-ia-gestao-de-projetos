"""Configuração local exclusiva. Nunca exibe chave nem importa .env legado."""
import getpass
import os
from pathlib import Path
import stat
import sys


def _arquivo(path):
    s=Path(path).lstat()
    if not stat.S_ISREG(s.st_mode) or stat.S_IMODE(s.st_mode)!=0o600 or s.st_uid!=os.getuid():
        raise ValueError('Arquivo de chave deve ser regular, próprio e ter permissão0600')
    return s


def presente(path):
    # Não lê conteúdo; indica somente existência segura ou presença no ambiente.
    if bool(os.environ.get('OPENAI_API_KEY')): return True
    try: _arquivo(path);return True
    except FileNotFoundError:return False


def carregar(path):
    # Executado apenas pelo usuário ao rodar o lote, nunca na inspeção do agente.
    k=os.environ.get('OPENAI_API_KEY')
    if k:return k
    _arquivo(path)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        s=os.fstat(fd)
        if stat.S_IMODE(s.st_mode)!=0o600 or not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid():raise ValueError('Arquivo de chave inseguro')
        with os.fdopen(fd,'r',encoding='utf-8',closefd=False) as f:linha=f.read(4097)
    finally:os.close(fd)
    if len(linha)>4096 or not linha.startswith('OPENAI_API_KEY='):raise ValueError('Formato local inválido')
    k=linha[len('OPENAI_API_KEY='):].strip()
    if not k or any(c.isspace() for c in k):raise ValueError('Chave local ausente/formato inválido')
    return k


def configurar(path):
    if not sys.stdin.isatty():raise ValueError('Execute em terminal interativo; entrada oculta obrigatória')
    k=getpass.getpass('Chave da API OpenAI (entrada oculta): ')
    if not k or len(k)>4000 or any(c.isspace() for c in k):raise ValueError('Entrada inválida')
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,'w',closefd=False) as f:f.write('OPENAI_API_KEY='+k+'\n');f.flush();os.fsync(f.fileno())
    finally:os.close(fd)
    print('Chave configurada localmente; valor não exibido. Arquivo existente nunca é sobrescrito.')
