"""ETL reproduzível: sinistros por ocorrência (PRF 2023–2025).

Uso:
    python -m src.etl
    python -m src.etl --raw-dir data/raw --out-dir data/processed

Origem: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf
Os três ZIPs não são alterados. Exporta análises agregadas, trilha de auditoria e
JSON público (sem IDs/pessoas/coords individuais) para GitHub Pages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import zipfile

import numpy as np
import pandas as pd

YEARS = (2023, 2024, 2025)
NUMERIC = ("mortos", "feridos", "feridos_leves", "feridos_graves", "pessoas", "veiculos", "br", "km", "latitude", "longitude")
REQUIRED = {"id", "data_inversa", "uf", "br", "tipo_acidente", "causa_acidente", "classificacao_acidente", "mortos", "feridos", "latitude", "longitude", "condicao_metereologica", "tipo_pista"}
GDRIVE_FILES = {
    2023: "1-WO3SfNrwwZ5_l7fRTiwBKRw7mi1-HUq",
    2024: "14lB0vqMFkaZj8HZ44b0njYgxs9nAN8KO",
    2025: "1-G3MdmHBt6CprDwcW99xxC4BZ2DU5ryR",
}


def sha256_file(path: Path) -> str:
    hash_ = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            hash_.update(block)
    return hash_.hexdigest()


def load_year(year: int, raw_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    zip_path = raw_dir / f"datatran{year}.zip"
    if not zip_path.is_file():
        raise FileNotFoundError(f"Arquivo ausente: {zip_path}. Consulte scripts/download_data.py")
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Arquivo não é ZIP válido: {zip_path}")
    with zipfile.ZipFile(zip_path) as bundle:
        files = [i for i in bundle.infolist() if i.filename.lower().endswith(".csv") and not i.is_dir()]
        if len(files) != 1:
            raise ValueError(f"ZIP {year}: esperado exatamente 1 CSV, obtidos {len(files)}")
        # Em base de ocorrência a PRF usa separador ';', decimais com vírgula e Latin-1.
        with bundle.open(files[0]) as f:
            df = pd.read_csv(f, sep=";", encoding="latin1", decimal=",", low_memory=False)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"ZIP {year}: colunas faltantes: {sorted(missing)}")
    audit: dict[str, Any] = {
        "year": year,
        "file": zip_path.name,
        "sha256": sha256_file(zip_path),
        "source_url": f"https://drive.google.com/file/d/{GDRIVE_FILES[year]}/view",
        "rows_read": int(len(df)),
        "columns": list(map(str, df.columns)),
        "duplicates_full": int(df.duplicated().sum()),
        "duplicates_id": int(df["id"].duplicated().sum()),
    }
    df = df.drop_duplicates().copy()
    # Um registro por ID; duplicações são removidas e auditadas.
    df = df.drop_duplicates(subset=["id"], keep="first").copy()
    for col in NUMERIC:
        if col not in df:
            continue
        if df[col].dtype == "object":
            df[col] = df[col].astype("string").str.replace(",", ".", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["data_inversa"] = pd.to_datetime(df["data_inversa"], format="%Y-%m-%d", errors="coerce")
    audit["invalid_date"] = int(df["data_inversa"].isna().sum())
    audit["rows_outside_year"] = int((df["data_inversa"].dt.year != year).sum())
    # Datas inválidas e anos inconsistentes não entram nos indicadores deste recorte.
    df = df.loc[df["data_inversa"].dt.year == year].copy()
    df["ano"] = year
    df["mes"] = df["data_inversa"].dt.month.astype("int8")
    # Recorte horário validado; não inferir hora quando faltante ou malformada.
    if "horario" in df:
        horas = df["horario"].astype("string").str.extract(r"^(\d{2}):[0-5]\d(?::[0-5]\d)?$")[0]
    else:
        horas = pd.Series(pd.NA, index=df.index, dtype="string")
        audit["missing_hour_column"] = True
    df["hora"] = pd.to_numeric(horas, errors="coerce").where(lambda x: x.between(0,23)).astype("Int64")
    df["dia_num"] = df["data_inversa"].dt.dayofweek.astype("int8")
    audit["invalid_hour"] = int(df["hora"].isna().sum())
    audit["negative_deaths"] = int(df["mortos"].lt(0).sum())
    audit["negative_injured"] = int(df["feridos"].lt(0).sum())
    if audit["negative_deaths"] or audit["negative_injured"]:
        raise ValueError(f"ZIP {year}: contagens negativas detectadas; revise antes de agregar")
    df["uf"] = df["uf"].astype("string").str.strip().str.upper()
    df["br_label"] = "BR-" + df["br"].astype("Int64").astype("string").str.zfill(3)
    df["fatal"] = df["mortos"].fillna(0).gt(0)
    df["localizacao_valida"] = (df["latitude"].between(-35, 6) & df["longitude"].between(-74, -32))
    audit["rows_after_validation"] = int(len(df))
    audit["invalid_coordinates"] = int((~df["localizacao_valida"]).sum())
    audit["missing_uf"] = int(df["uf"].isna().sum())
    audit["missing_type"] = int(df["tipo_acidente"].isna().sum())
    audit["missing_cause"] = int(df["causa_acidente"].isna().sum())
    audit["missing_classification"] = int(df["classificacao_acidente"].isna().sum())
    audit["missing_death_count"] = int(df["mortos"].isna().sum())
    audit["date_min"] = df["data_inversa"].min().strftime("%Y-%m-%d") if len(df) else None
    audit["date_max"] = df["data_inversa"].max().strftime("%Y-%m-%d") if len(df) else None
    return df, audit


def _entries(df: pd.DataFrame, field: str, count: int = 10) -> list[dict[str, Any]]:
    grouped = df.dropna(subset=[field]).groupby(field, dropna=False).agg(
        accidents=("id", "size"), deaths=("mortos", "sum"), injured=("feridos", "sum"), fatal_accidents=("fatal", "sum")
    ).reset_index().sort_values("accidents", ascending=False).head(count)
    return [{"name": str(row[field]), "accidents": int(row.accidents), "deaths": int(row.deaths), "injured": int(row.injured), "fatal_accidents": int(row.fatal_accidents)} for _, row in grouped.iterrows()]


def build_summary(all_: pd.DataFrame, audit: list[dict[str, Any]]) -> dict[str, Any]:
    annual = []
    monthly = []
    for year, part in all_.groupby("ano", sort=True):
        annual.append({"year": int(year), "accidents": int(len(part)), "deaths": int(part["mortos"].sum()), "injured": int(part["feridos"].sum()), "fatal_accidents": int(part["fatal"].sum())})
        for month in range(1, 13):
            one = part.loc[part["mes"] == month]
            monthly.append({"year": int(year), "month": month, "accidents": int(len(one)), "deaths": int(one["mortos"].sum()), "injured": int(one["feridos"].sum())})
    # Recortes adicionais: horário (00–23), semana (seg–dom), municípios e UFs por ano.
    hour = []
    for h in range(24):
        part = all_.loc[all_["hora"] == h]
        hour.append({"hour": h, "accidents": int(len(part)),
                     "deaths": int(part["mortos"].sum()),
                     "injured": int(part["feridos"].sum()),
                     "fatal_accidents": int(part["fatal"].sum())})
    weekday = []
    names = ("Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo")
    for d in range(7):
        part = all_.loc[all_["dia_num"] == d]
        weekday.append({"day": d, "name": names[d], "accidents": int(len(part)),
                        "deaths": int(part["mortos"].sum()),
                        "injured": int(part["feridos"].sum())})
    uf_annual = []
    for (year, uf), part in all_.dropna(subset=["uf"]).groupby(["ano", "uf"]):
        uf_annual.append({"year": int(year), "uf": str(uf),
                          "accidents": int(len(part)), "deaths": int(part["mortos"].sum()),
                          "injured": int(part["feridos"].sum())})
    monthly_vals = np.asarray([x["accidents"] for x in monthly],dtype=float)
    q1,q3 = np.percentile(monthly_vals,[25,75])
    eda = {
       "monthly_accidents_mean": round(float(monthly_vals.mean()),2),
       "monthly_accidents_median": round(float(np.median(monthly_vals)),2),
       "monthly_accidents_std_population": round(float(monthly_vals.std(ddof=0)),2),
       "monthly_accidents_q1": round(float(q1),2),
       "monthly_accidents_q3": round(float(q3),2),
       "monthly_highest": max(monthly,key=lambda x:x["accidents"]),
       "monthly_lowest": min(monthly,key=lambda x:x["accidents"]),
       "sample_size_months": len(monthly),
       "note": "Estatísticas descritivas dos 36 totais mensais; não são taxas por exposição ao tráfego."
    }
    sample2025 = all_.loc[all_["ano"] == 2025]
    # Métrica de gravidade: proporção de ocorrências com pelo menos 1 morte.
    gravity = {}
    for col in ("tipo_pista", "condicao_metereologica", "fase_dia"):
        frame = sample2025.dropna(subset=[col]).groupby(col).agg(accidents=("id", "size"), fatal_accidents=("fatal", "sum"), deaths=("mortos", "sum")).reset_index()
        frame = frame.loc[frame.accidents >= 100].sort_values("accidents", ascending=False)
        gravity[col] = [{"name": str(row[col]), "accidents": int(row.accidents), "fatal_accidents": int(row.fatal_accidents), "deaths": int(row.deaths), "fatal_rate": round(float(row.fatal_accidents / row.accidents * 100), 2)} for _, row in frame.iterrows()]
    validity = sample2025.loc[sample2025.localizacao_valida].copy()
    # Arredondamento geográfico em células de 0,5 grau para anonimizar e reduzir tamanho.
    validity["lat_cell"] = np.floor(validity["latitude"] * 2) / 2 + 0.25
    validity["lon_cell"] = np.floor(validity["longitude"] * 2) / 2 + 0.25
    grid = validity.groupby(["lat_cell", "lon_cell"]).size().sort_values(ascending=False).reset_index(name="count")
    heatmap = [[float(x.lat_cell), float(x.lon_cell), int(x["count"])] for _, x in grid.iterrows()]
    # Agrupamento por município exige UF para evitar colisões entre homônimos.
    if "municipio" not in sample2025:
        sample2025 = sample2025.copy()
        sample2025["municipio"] = pd.NA
    towns = (sample2025.dropna(subset=["municipio", "uf"])
             .groupby(["uf", "municipio"]).agg(
                 accidents=("id", "size"), deaths=("mortos", "sum"),
                 injured=("feridos", "sum"))
             .reset_index().sort_values("accidents", ascending=False).head(20))
    municipalities = [{"name": f"{x.municipio} · {x.uf}",
                       "accidents": int(x.accidents), "deaths": int(x.deaths),
                       "injured": int(x.injured)} for x in towns.itertuples()]
    # Totais por tipo de sinistro. Ao comparar fatalidade usar o denominador
    # de sinistros daquele tipo, e não o total de mortes.
    fatal_type = (sample2025.dropna(subset=["tipo_acidente"])
                  .groupby("tipo_acidente").agg(
                       accidents=("id", "size"), fatal_accidents=("fatal", "sum"))
                  .reset_index())
    fatal_type = fatal_type.loc[fatal_type.accidents >= 100].copy()
    fatal_type["fatal_rate"] = (fatal_type.fatal_accidents / fatal_type.accidents * 100).round(2)
    fatal_type = fatal_type.sort_values("fatal_rate", ascending=False)
    fatal_by_type = [{"name": str(x.tipo_acidente), "accidents": int(x.accidents),
                      "fatal_accidents": int(x.fatal_accidents),
                      "fatal_rate": float(x.fatal_rate)} for x in fatal_type.itertuples()]
    return {
        "meta": {"source": "PRF/BAT — acidentes agrupados por ocorrência", "period": "2023–2025", "updated_from": "arquivos ZIP oficiais disponibilizados pela PRF", "unit": "uma linha por ocorrência", "note": "Contagens absolutas não medem risco ajustado à exposição ao tráfego.", "map_grid_resolution_degrees": 0.5},
        "annual": annual, "monthly": monthly,
        "hourly": hour, "weekday": weekday, "uf_annual": uf_annual,
        "eda_summary": eda,
        "top_municipalities_2025": municipalities,
        "fatal_by_type_2025": fatal_by_type,
        "top_types_2025": _entries(sample2025, "tipo_acidente", 12),
        "top_causes_2025": _entries(sample2025, "causa_acidente", 12),
        "top_states_2025": _entries(sample2025, "uf", 27),
        "top_roads_2025": _entries(sample2025, "br_label", 15),
        "severity_2025": gravity, "map_grid_2025": heatmap,
        "map_valid_points_2025": int(len(validity)), "map_excluded_points_2025": int(len(sample2025)-len(validity)),
        "audit": audit,
    }


def run_etl(raw_dir: Path, out_dir: Path, site_data_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    site_data_dir.mkdir(parents=True, exist_ok=True)
    frames=[];audits=[]
    for year in YEARS:
        df,audit=load_year(year,raw_dir)
        frames.append(df);audits.append(audit)
    all_=pd.concat(frames,ignore_index=True)
    if all_.duplicated(subset=["id"]).any():
        # Um mesmo id em anos diferentes seria estranho; falhar em vez de contar duas vezes.
        raise ValueError("Há IDs repetidos entre anos diferentes. Audite os dados antes de continuar.")
    summary=build_summary(all_,audits)
    output=site_data_dir/"analysis.json"
    output.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    (out_dir/"auditoria.json").write_text(json.dumps(audits,ensure_ascii=False,indent=2),encoding="utf-8")
    # Persistência aberta compactada: somente agregações por UF e dia, sem
    # coordenadas individuais, IDs de sinistro ou dados pessoais.
    daily_uf = (all_.dropna(subset=["uf", "data_inversa"])
                .groupby(["data_inversa", "uf"]).agg(
                    sinistros=("id", "size"), mortos=("mortos", "sum"),
                    feridos=("feridos", "sum"),
                    ocorrencias_fatais=("fatal", "sum"))
                .reset_index().sort_values(["data_inversa", "uf"]))
    daily_uf.to_csv(out_dir/"sinistros_diarios_uf_2023_2025.csv.gz", index=False,
                    compression="gzip", encoding="utf-8")
    pd.DataFrame(summary["annual"]).to_csv(out_dir/"serie_anual.csv",index=False,encoding="utf-8")
    # CSVs agregados servidos diretamente no GitHub Pages.
    download_dir=site_data_dir/"csv"
    download_dir.mkdir(parents=True,exist_ok=True)
    for key, filename in (("annual","serie-anual"),("monthly","serie-mensal"),
                          ("hourly","distribuicao-horaria"),("weekday","dias-semana"),
                          ("uf_annual","ufs-por-ano"),
                          ("top_states_2025","estados-2025"),
                          ("top_roads_2025","rodovias-2025"),
                          ("top_municipalities_2025","municipios-2025"),
                          ("fatal_by_type_2025","fatalidade-por-tipo-2025")):
        pd.DataFrame(summary[key]).to_csv(download_dir/f"{filename}.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(summary["monthly"]).to_csv(out_dir/"serie_mensal.csv",index=False,encoding="utf-8")
    pd.DataFrame(summary["top_states_2025"]).to_csv(out_dir/"uf_2025.csv",index=False,encoding="utf-8")
    pd.DataFrame(summary["top_roads_2025"]).to_csv(out_dir/"rodovias_2025.csv",index=False,encoding="utf-8")
    print(json.dumps({"annual":summary["annual"],"rows":len(all_),"map_cells":len(summary["map_grid_2025"]),"output":str(output)},ensure_ascii=False,indent=2))
    return summary


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir",type=Path,default=Path("data/raw"))
    parser.add_argument("--out-dir",type=Path,default=Path("data/processed"))
    parser.add_argument("--site-data-dir",type=Path,default=Path("docs/assets/data"))
    args=parser.parse_args()
    run_etl(args.raw_dir,args.out_dir,args.site_data_dir)

if __name__ == "__main__":
    main()
