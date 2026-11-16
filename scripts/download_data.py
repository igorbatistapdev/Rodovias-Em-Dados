"""Opcional: baixar ZIPs originais da PRF via Google Drive.

Uso: python scripts/download_data.py
Observação: arquivos originais já estão inclusos no pacote entregue.
O download sobrescreve arquivos somente com --replace, e valide o ZIP.
"""
import argparse
from pathlib import Path
import zipfile
import gdown

URLS = {
    2023: "https://drive.google.com/file/d/1-WO3SfNrwwZ5_l7fRTiwBKRw7mi1-HUq/view",
    2024: "https://drive.google.com/file/d/14lB0vqMFkaZj8HZ44b0njYgxs9nAN8KO/view",
    2025: "https://drive.google.com/file/d/1-G3MdmHBt6CprDwcW99xxC4BZ2DU5ryR/view",
}


def download(raw: Path, replace: bool = False) -> None:
    raw.mkdir(parents=True, exist_ok=True)
    for year, url in URLS.items():
        dest=raw / f"datatran{year}.zip"
        if dest.exists() and not replace:
            print(f"{dest} já existe; não sobrescrito")
            continue
        temp=dest.with_suffix('.download')
        try:
            gdown.download(url=url, output=str(temp), quiet=False, fuzzy=True)
            if not temp.exists() or not zipfile.is_zipfile(temp):
                raise RuntimeError(f"Download de {year} inválido. Confira o link oficial.")
            with zipfile.ZipFile(temp) as file:
                name=f"datatran{year}.csv"
                if name not in file.namelist():
                    raise RuntimeError(f"O ZIP de {year} não contém {name}.")
            temp.replace(dest)
            print(f"Validado: {dest}")
        finally:
            if temp.exists(): temp.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--raw-dir', type=Path, default=Path('data/raw'))
    parser.add_argument('--replace',action='store_true')
    args=parser.parse_args()
    download(args.raw_dir,args.replace)
