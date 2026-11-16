 <div align="center">

<sub>PESQUISA CIENTÍFICA · UNILASALLE RJ · 2026</sub>

# Rodovias em Dados

**Análise temporal, estatística e geoespacial dos sinistros nas rodovias federais brasileiras.**

Brasil · 2023–2025 · Dados oficiais da PRF

<br>

<a href="https://igorbatistapdev.github.io/Rodovias-Em-Dados/">
  <img src="assets/readme-cta.svg" alt="Acessar artigo interativo" width="320">
</a>

<br>

<a href="https://igorbatistapdev.github.io/Rodovias-Em-Dados/">Acessar pesquisa</a> &nbsp;·&nbsp;
<a href="previews/Rodovias_em_Dados_2026_Artigo_Final_ABNT.pdf">Ler em PDF</a> &nbsp;·&nbsp;
<a href="data/processed/">Explorar dados</a>

</div>

---

## A pesquisa

O **Rodovias em Dados** é um artigo científico digital que investiga a evolução, a gravidade e a distribuição territorial dos sinistros nas rodovias federais brasileiras entre 2023 e 2025.

A partir dos microdados públicos da **Polícia Rodoviária Federal (PRF)**, a pesquisa reúne análise estatística, processamento reproduzível em Python e visualizações interativas, apresentando os resultados em uma experiência de leitura editorial.

<div align="center">
  <a href="https://igorbatistapdev.github.io/Rodovias-Em-Dados/">
    <img src="previews/Preview_desktop_final.png" alt="Interface do artigo Rodovias em Dados" width="850">
  </a>
  <sub>Prévia do artigo interativo · <a href="previews/Preview_mobile_final.png">Visualizar versão mobile</a></sub>
</div>

## Panorama dos dados

| Sinistros analisados | Mortes registradas | Pessoas feridas |
| :---: | :---: | :---: |
| **213.497** | **17.833** | **246.608** |

*Registros oficiais de 2023 a 2025, agrupados por ocorrência. Os indicadores representam contagens absolutas e não taxas de risco ajustadas ao fluxo de veículos.*

## Objetivos da investigação

A pesquisa é orientada por três questões:

**01. Evolução temporal**  
Como os registros de sinistros variaram ao longo do período analisado?

**02. Padrões e gravidade**  
Quais características temporais e classificações se destacam nos registros?

**03. Distribuição territorial**  
Como os sinistros se distribuem entre estados e rodovias federais?

## Metodologia

O projeto utiliza um fluxo de processamento reproduzível, desde a obtenção dos dados oficiais até a publicação dos resultados.

**Coleta → Validação → Tratamento → Análise → Visualização**

**Tecnologias:** Python, Pandas, NumPy, SQLite, Matplotlib, HTML, CSS e JavaScript.

<details>
<summary><strong>Executar o projeto localmente</strong></summary>

### Visualizar o artigo

Na raiz do projeto:

```powershell
python -m http.server 8000 -d docs
```

Acesse `http://localhost:8000`.

### Reproduzir a análise

Recomenda-se Python 3.13.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/run_pipeline.py
.\.venv\Scripts\python.exe -m pytest -q
```

O arquivo `templates/article.html` contém a estrutura original do artigo. O pipeline gera `docs/index.html` automaticamente.

</details>

## Ciência aberta e documentação

A pesquisa adota princípios **FAIR** de organização, acessibilidade, interoperabilidade e reutilização dos dados.

- [Fonte oficial dos dados — PRF](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf)
- [Dados e resultados processados](data/processed/)
- [Auditoria e rastreabilidade](data/processed/auditoria.json)
- [Referências e conformidade ABNT](REFERENCIAS_E_ABNT.md)
- [Relatório de qualidade](RELATORIO_QA.md)

A análise possui caráter **exploratório e descritivo**. Seus resultados não estabelecem relações causais nem permitem comparar diretamente riscos sem considerar a exposição ao tráfego.

---

<div align="center">

**Igor Batista Pereira**

Sistemas de Informação · Unilasalle RJ  
Disciplina: Linguagem de Programação  
Professor Alexandre Neves Louzada

<sub>2026 · Pesquisa acadêmica com dados públicos</sub>

<sub>Código sob licença <a href="LICENSE">MIT</a> · <a href="LICENSE-CONTENT.md">Licenciamento do conteúdo científico</a></sub>

</div>
