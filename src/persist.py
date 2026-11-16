"""Persistência opcional dos agregados em SQLite usando SQLAlchemy.

Não contém registros individuais, apenas estatísticas por ano, mês, UF e rodovia.
Uso: python -m src.persist
"""
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

TABLES = {
    'serie_anual': 'serie_anual.csv',
    'serie_mensal': 'serie_mensal.csv',
    'sinistros_uf_2025': 'uf_2025.csv',
    'sinistros_rodovia_2025': 'rodovias_2025.csv',
}


def persist(processed: Path=Path('data/processed')) -> Path:
    out=processed/'analise_prf.sqlite'
    processed.mkdir(parents=True,exist_ok=True)
    engine=create_engine(f'sqlite:///{out.resolve().as_posix()}')
    for table,file in TABLES.items():
        df=pd.read_csv(processed/file)
        df.to_sql(table, engine, if_exists='replace', index=False)
    engine.dispose()
    return out


if __name__ == '__main__':
    print(persist())
