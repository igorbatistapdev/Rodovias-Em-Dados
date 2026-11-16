"""Gera figuras científicas estáticas a partir de estatísticas PRF.

Execução: python -m src.visualizations
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

BG = "#FFFEFA"
FOREST = "#233C36"
SAGE = "#3F769C"
COPPER = "#BA704C"
PURPLE = "#75668F"
GOLD = "#AE8540"
OCHRE = "#BA704C"
MUTED = "#51685B"


def setup() -> None:
    sns.set_theme(style="whitegrid", context="paper", palette=[SAGE, COPPER, PURPLE, GOLD])
    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG,
        "axes.edgecolor": "#D5DBD2", "axes.labelcolor": FOREST,
        "text.color": FOREST, "xtick.color": MUTED, "ytick.color": MUTED,
        "grid.color": "#D5DBD2", "font.family": "DejaVu Sans",
        "font.size": 12, "axes.titlesize": 19, "axes.titleweight": "bold",
        "axes.titlepad": 18, "savefig.facecolor": BG, "savefig.transparent": False,
    })


def save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, bbox_inches="tight", pad_inches=.28, format="svg")
    plt.close(fig)


def generate(summary: dict, images_dir: Path) -> None:
    images_dir.mkdir(parents=True, exist_ok=True)
    setup()
    annual = summary["annual"]
    x=np.arange(len(annual)); vals=np.array([e["accidents"] for e in annual]); deaths=np.array([e["deaths"] for e in annual]); years=[str(e["year"]) for e in annual]
    fig,axes=plt.subplots(1,2,figsize=(12,4.8), gridspec_kw={"width_ratios":[1.2,1]})
    bars=axes[0].bar(x,vals,width=.62,color=SAGE)
    axes[0].set_title("Sinistros registrados por ano",loc="left")
    axes[0].set_xticks(x,years);axes[0].set_ylim(0,max(vals)*1.23)
    axes[0].set_ylabel("Ocorrências")
    axes[0].bar_label(bars,labels=[f"{v:,}".replace(",",".") for v in vals],padding=7,color=FOREST,fontsize=12,fontweight="bold")
    axes[1].plot(x,deaths,color=OCHRE,linewidth=2.7,marker="o",markersize=8)
    for xi,val in zip(x,deaths): axes[1].annotate(f"{val:,}".replace(",","."),(xi,val),xytext=(0,11),textcoords="offset points",ha="center",fontweight="bold")
    axes[1].set_ylim(0,max(deaths)*1.24);axes[1].set_xticks(x,years);axes[1].set_ylabel("Mortes")
    axes[1].set_title("Mortes registradas por ano",loc="left")
    for ax in axes:
        ax.spines[["top","right"]].set_visible(False)
        ax.grid(axis="x",visible=False)
    fig.subplots_adjust(wspace=.3)
    save(fig, images_dir/"grafico-anual.svg")

    types=summary["top_types_2025"][:6][::-1]
    fig,ax=plt.subplots(figsize=(11.3,5.2))
    bar=ax.barh([row["name"] for row in types],[row["accidents"] for row in types],color=[SAGE,PURPLE,COPPER,GOLD,"#508B80","#6B7F99"],height=.63)
    ax.bar_label(bar,labels=[f'{i["accidents"]:,}'.replace(",",".") for i in types],padding=8,fontsize=11,fontweight="bold")
    ax.set_xlim(0,max(i["accidents"] for i in types)*1.22)
    ax.set_title("Tipos de sinistro mais frequentes | 2025",loc="left")
    ax.spines[["top","right"]].set_visible(False);ax.grid(axis="y",visible=False)
    save(fig, images_dir/"grafico-tipos.svg")

    states=summary["top_states_2025"][:8][::-1]
    fig,ax=plt.subplots(figsize=(11.2,5.3))
    bar=ax.barh([i["name"] for i in states],[i["accidents"] for i in states],color=PURPLE,height=.67)
    ax.bar_label(bar,labels=[f'{i["accidents"]:,}'.replace(",",".") for i in states],padding=7,fontweight="bold")
    ax.set_xlim(0,max(i["accidents"] for i in states)*1.22)
    ax.set_title("Unidades federativas com mais sinistros | 2025",loc="left")
    ax.spines[["top","right"]].set_visible(False);ax.grid(axis="y",visible=False)
    save(fig, images_dir/"grafico-ufs.svg")

    # Proporção de ocorrências com ao menos uma morte, por tipo de pista.
    severity = summary["severity_2025"]["tipo_pista"]
    labels = [row["name"] for row in severity]
    percentages = [row["fatal_rate"] for row in severity]
    fig, ax = plt.subplots(figsize=(10.8, 4.4))
    bars = ax.barh(labels, percentages, color=COPPER, height=.57)
    ax.invert_yaxis()
    ax.set_xlim(0, max(percentages) * 1.25)
    ax.set_title("Proporção de ocorrências com morte por tipo de pista | 2025", loc="left")
    ax.set_xlabel("Percentual de sinistros com ao menos uma morte")
    ax.bar_label(bars, labels=[f"{pct:.2f}%".replace(".", ",") for pct in percentages], padding=8, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", visible=False)
    save(fig, images_dir / "grafico-gravidade.svg")

    # Panorama das 24 horas, a partir do campo horario validado pelo ETL.
    hourly = summary["hourly"]
    fig, ax = plt.subplots(figsize=(13,4.6))
    hours=[v["hour"] for v in hourly]
    vals=[v["accidents"] for v in hourly]
    bars=ax.bar(hours, vals, color=SAGE, width=.78)
    peak=max(vals); peak_hour=hours[vals.index(peak)]
    bars[peak_hour].set_color(COPPER)
    ax.set_xticks(range(0,24,2),[f"{h:02d}h" for h in range(0,24,2)])
    ax.set_ylabel("Registros de sinistros")
    ax.set_title("Distribuição por hora do registro | 2023–2025",loc="left")
    ax.set_xlim(-.7,23.7);ax.set_ylim(0,max(vals)*1.22)
    ax.annotate(f"{peak:,}".replace(",","."), (peak_hour,peak), xytext=(0,11),textcoords="offset points",ha="center",fontweight="bold",color=FOREST)
    ax.spines[["top","right"]].set_visible(False);ax.grid(axis="x",visible=False)
    save(fig,images_dir/"grafico-horario.svg")


def main() -> None:
    summary=json.loads(Path("docs/assets/data/analysis.json").read_text(encoding="utf-8"))
    generate(summary,Path("docs/assets/images"))
    print("Figuras SVG geradas a partir dos dados PRF processados")

if __name__=="__main__": main()
