from pathlib import Path
from zipfile import ZipFile
import pandas as pd
import pytest
from src.etl import load_year, build_summary


def fixture_zip(tmp_path: Path, year=2025):
    columns=['id','data_inversa','uf','br','tipo_acidente','causa_acidente','classificacao_acidente','mortos','feridos','latitude','longitude','condicao_metereologica','tipo_pista','fase_dia']
    data=[
        [1, f'{year}-01-01','RJ',101,'Colisão traseira','Falha de reação','Sem Vítimas',0,0,'-22,8','-43,2','Céu Claro','Dupla','Pleno dia'],
        [2, f'{year}-02-02','MG',116,'Colisão frontal','Ultrapassagem indevida','Com Vítimas Fatais',2,1,'-20,5','-44,0','Chuva','Simples','Plena Noite'],
        [2, f'{year}-02-02','MG',116,'Colisão frontal','Ultrapassagem indevida','Com Vítimas Fatais',2,1,'-20,5','-44,0','Chuva','Simples','Plena Noite'],
    ]
    # Escrever exatamente como os CSVs originais: campo delimitado por ';'.
    import csv, io
    sio=io.StringIO()
    writer=csv.writer(sio,delimiter=';',quoting=csv.QUOTE_MINIMAL)
    writer.writerow(columns);writer.writerows(data)
    with ZipFile(tmp_path/f'datatran{year}.zip','w') as z: z.writestr(f'datatran{year}.csv',sio.getvalue().encode('latin1'))


def test_leitura_e_duplicatas(tmp_path):
    fixture_zip(tmp_path)
    df, audit=load_year(2025,tmp_path)
    assert audit['rows_read']==3
    assert audit['duplicates_full']==1
    assert audit['rows_after_validation']==2
    assert audit['invalid_coordinates']==0
    assert df['mortos'].sum()==2
    assert df['latitude'].dtype.kind=='f'
    assert df['fatal'].sum()==1


def test_agregacao_reproduz_totais(tmp_path):
    fixture_zip(tmp_path)
    df,audit=load_year(2025,tmp_path)
    result=build_summary(df,[audit])
    assert result['annual'][0]['accidents']==2
    assert result['annual'][0]['deaths']==2
    assert result['annual'][0]['injured']==1
    assert sum(x['accidents'] for x in result['monthly'])==2
    assert result['top_states_2025'][0]['accidents']==1


def test_falha_arquivo_ausente(tmp_path):
    with pytest.raises(FileNotFoundError):load_year(2025,tmp_path)


def test_anos_csv_reais_existem():
    root=Path(__file__).resolve().parents[1]
    for year in (2023,2024,2025): assert (root/'data/raw'/f'datatran{year}.zip').exists()
