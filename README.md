# Rodovias em Dados · Edição final para publicação (v5.1)

**Análise temporal, estatística e geoespacial dos sinistros nas rodovias federais brasileiras (2023–2025).**

Artigo científico digital independente, desenvolvido no curso de **Sistemas de Informação – Unilasalle RJ**, por **Igor Batista Pereira**, para a disciplina Linguagem de Programação, ministrada pelo professor **Alexandre Neves Louzada**.

## Edição revisada v5.1

Esta versão implementa a **direção visual B — Jornalismo de Dados em edição minimalista**. O objetivo é valorizar a leitura acadêmica e os gráficos, eliminando caixas e decorações desnecessárias. O conteúdo é baseado em cálculos verificáveis dos arquivos de acidentes agrupados por ocorrência disponibilizados pela **Polícia Rodoviária Federal (PRF)**.

- **Abertura editorial sem imagem:** título, subtítulo, autoria, recorte e fonte sem painel lateral.
- **Indicadores alinhados:** uma faixa tipográfica de números com divisórias discretas.
- **Três perguntas de pesquisa:** cards numerados 01/02/03, vinculados aos respectivos resultados.
- **Metodologia mais leve:** pipeline de cinco etapas, texto preciso e nota explicativa recolhível.
- **Resultados com narrativa científica:** títulos interpretativos, gráficos amplos, comparações, legendas e ressalvas.
- **Visualizações interativas preservadas:** séries anual/mensal, distribuição por horário/dia, tipos de sinistro, gravidade e rankings territoriais.
- **FAIR compacto:** quatro linhas, reprodução detalhada expansível e exportações CSV/JSON.
- **Sem mapa e sem modo escuro:** removidos da interface conforme as decisões de design.
- **PDF A4:** gráficos vetoriais em impressão, numeração de páginas, referências separadas e quebras revisadas.
- **CSS único reorganizado:** removeu camadas de versões anteriores e manteve a hierarquia mobile.

## Visualização imediata, sem instalar Python

Extraia o arquivo ZIP. Abra **`docs/index.html`** em um navegador atualizado. A página utiliza dados agregados incorporados ao HTML e funciona localmente; a conexão é opcional para carregar as fontes do Google. A aparência mantém fontes alternativas quando não houver conexão.

Para visualizar pelo servidor local (recomendado durante desenvolvimento):

```bash
python -m http.server 8000 -d docs
```

Acesse `http://localhost:8000`.

## Como executar no Windows

O projeto foi testado em **Python 3.13.5**. A combinação de dependências congeladas suporta Python **3.11 a 3.13**; ela não foi validada no Python 3.14.

Se você tiver apenas Python 3.14, pode instalar o 3.13 sem remover a versão atual:

```powershell
winget install --id Python.Python.3.13 --exact --source winget
```

Feche e reabra o terminal para reconhecer a instalação. Na raiz do projeto, execute:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/run_pipeline.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m http.server 8000 -d docs
```

Há também um auxiliar opcional: `scripts/configurar_windows.ps1` (executar com PowerShell e permissão de script adequada), que verifica o Python 3.13, cria o ambiente e instala as dependências.

### Linux/macOS

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/run_pipeline.py
python -m pytest -q
python -m http.server 8000 -d docs
```

## Onde editar o design e o conteúdo

| Arquivo | Responsabilidade |
|---|---|
| `templates/article.html` | Estrutura editorial e texto acadêmico: **fonte do HTML** |
| `docs/assets/css/style.css` | Design minimalista e responsividade da versão 5.0 |
| `docs/assets/css/print.css` | Paginação e impressão A4 |
| `docs/assets/js/main.js` | Séries temporais, tipos, gravidade e ranking |
| `docs/assets/js/interactions.js` | Gráfico horário, downloads, navegação e impressão |
| `src/etl.py` | Processamento e agregação dos microdados PRF |
| `src/visualizations.py` | Figuras vetoriais do PDF |
| `src/persist.py` | Banco SQLite derivado |
| `scripts/run_pipeline.py` | Orquestra a execução de todos os componentes |
| `scripts/refinar_artigo.py` | Renderiza `templates/article.html` em `docs/index.html` |

**Não edite `docs/index.html` diretamente**: o pipeline recria esse arquivo a partir do template. Imagens do protótipo de design não foram usadas como fonte de dados.

## Resultados dos arquivos PRF utilizados

| Ano | Sinistros | Mortes | Feridos | Sinistros com morte |
|---|---:|---:|---:|---:|
| 2023 | 67.766 | 5.627 | 78.463 | 4.858 |
| 2024 | 73.202 | 6.163 | 84.595 | 5.225 |
| 2025 | 72.529 | 6.043 | 83.550 | 5.210 |
| **Total** | **213.497** | **17.833** | **246.608** | **15.293** |

Os três ZIPs originais estão preservados em `data/raw/`; a auditoria de qualidade, a origem e os hashes SHA-256 ficam em `data/processed/auditoria.json`. **Sinistros com morte não equivalem à quantidade de mortes**: um registro pode envolver mais de uma vítima fatal. Contagens absolutas não medem risco ajustado pelo fluxo de tráfego.

Fonte: [portal oficial de dados abertos da PRF](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf) · [dicionário de dados](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dicionario-acidentes).

## Como imprimir ou salvar em PDF

No artigo, clique em **Imprimir / PDF** e selecione “Salvar como PDF”. Recomendações para Edge/Chrome: papel **A4**, escala **100%**, orientação **retrato**, gráficos de fundo ativados e cabeçalho/rodapé nativos desativados. O CSS publica figuras SVG vetoriais estáticas no lugar dos gráficos JavaScript. Uma exportação de referência está em `previews/Rodovias_em_Dados_2026_Artigo_Final_ABNT.pdf`.

## Publicação GitHub Pages

**Repositório identificado:** [igorbatistapdev/Rodovias-Em-Dados](https://github.com/igorbatistapdev/Rodovias-Em-Dados). Ele existe e estava vazio na preparação deste pacote, em 16/11/2026. O código-fonte deve ser enviado pela pasta raiz do projeto; o GitHub Pages deverá publicar o diretório `/docs` da branch `main`. O cabeçalho do artigo já aponta para o repositório correto.

**URL prevista do artigo após ativar Pages:** `https://igorbatistapdev.github.io/Rodovias-Em-Dados/`. Este endereço ainda precisa ser confirmado no painel **Settings → Pages**, pois o site não foi publicado nesta etapa.

Siga `GUIA_PUBLICACAO_GITHUB_PAGES.md` para os comandos de envio e o checklist de validação.

## Ciência aberta, limites e licenças

O projeto documenta princípios FAIR (Findable, Accessible, Interoperable, Reusable), processa e distribui agregados abertos em CSV e JSON, fornece scripts e testes e registra a proveniência dos arquivos. Código autoral: licença MIT. Consulte `LICENSE-CONTENT.md` para os termos de figuras/textos e a PRF para os dados originais.

**Limites:** o estudo é exploratório e descritivo. Não estabelece causalidade nem risco comparativo ajustado à exposição ao tráfego. A revisão bibliográfica e a conferência de links foram realizadas na edição final; ainda falta a publicação pública e a validação do ambiente Windows do autor. A validação em Windows e a publicação real no GitHub Pages não foram realizadas nesta sessão.

## Verificações da edição final

- Pipeline Python: executado com sucesso sobre os três arquivos originais.
- Testes automatizados: suíte revisada e execução registrada em `RELATORIO_QA.md`.
- Chromium: **1440, 768, 390 e 360 px**, sem rolagem horizontal ou erros de JS.
- Interações: séries anual/mensal, gravidade, ranking por rodovia e dias da semana.
- Impressão PDF: 9 páginas A4, figuras SVG, Abstract em página nova e referências em página própria.

Veja `RELATORIO_QA.md`, `CHANGELOG.md` e `DESIGN_SYSTEM_V5.md` para os detalhes técnicos e editoriais.


## Revisão final da edição 2026 (v5.1)

- **Cores científicas:** azul para evolução/horários, cobre para morte/gravidade, roxo para território, dourado e tons complementares nos tipos de sinistro. Verde permanece na identidade institucional.
- **ABNT:** referências revistas segundo NBR 6023:2025; sistema autor-data em conformidade com NBR 10520:2023 e links para páginas oficiais/versões abertas. Detalhes em `REFERENCIAS_E_ABNT.md`.
- **Pesquisa:** resumo/abstract com dados da extração, metodologias explícitas e trecho real do ETL no artigo; nenhuma inferência causal indevida.
- **PDF A4:** arquivo revisado em `previews/Rodovias_em_Dados_2026_Artigo_Final_ABNT.pdf`; navegação e interações ocultadas apenas na impressão.
- **Vídeo:** auditoria visual orientada pelas telas apresentadas no arquivo de referência; ver `AUDITORIA_FINAL_DO_VIDEO.md`.
- **Estado:** edição final local pronta para publicação, **ainda não publicada** no GitHub Pages. A nota final depende da rubrica e da avaliação do professor.
