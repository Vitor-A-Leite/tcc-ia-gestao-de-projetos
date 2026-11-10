"""Etapa Alfa documental 1.0.0 — isolada dos experimentos congelados."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
SRC = REPO / 'TCC_Codigos/src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
VERSION = '1.0.0'
