"""Recria indicadores, figuras SVG, banco SQLite e artigo final.

Uso: python scripts/run_pipeline.py
"""
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CMDS=[
 [sys.executable,'-m','src.etl'],
 [sys.executable,'-m','src.visualizations'],
 [sys.executable,'-m','src.persist'],
 [sys.executable,'scripts/refinar_artigo.py'],
]
def verificar_ambiente():
 """Fornece um erro compreensível quando o ambiente não foi preparado."""
 versao = sys.version_info[:2]
 if not ((3, 11) <= versao <= (3, 13)):
  raise SystemExit(
   "\nVersão de Python incompatível: " + sys.version.split()[0] + ".\n"
   "Este projeto usa pandas==2.2.3 e requer Python 3.11–3.13 (recomendado: 3.13).\n"
   "Windows PowerShell (na raiz do projeto):\n"
   "  py -3.13 -m venv .venv\n"
   "  .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt\n"
   "  .\\.venv\\Scripts\\python.exe scripts/run_pipeline.py\n"
   "Você pode manter o Python 3.14 instalado para outros projetos."
  )
 try:
  import numpy  # noqa: F401
  import pandas  # noqa: F401
 except ImportError as exc:
  raise SystemExit(
   "\nDependências ainda não instaladas: " + str(exc) + "\n"
   "Instale os pacotes com o mesmo Python que vai executar o pipeline:\n"
   "  python -m pip install -r requirements.txt\n"
  ) from exc


if __name__=='__main__':
 verificar_ambiente()
 for cmd in CMDS:
  print('\nEXECUTANDO:', ' '.join(cmd),flush=True)
  subprocess.run(cmd,cwd=ROOT,check=True)
 print('\nPipeline completo. Abra docs/index.html para conferir as visualizações.')
