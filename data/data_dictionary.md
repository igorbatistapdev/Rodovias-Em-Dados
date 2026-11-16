# Dicionário de dados — Rodovias em Dados

## Fonte e granularidade

Os conjuntos utilizados são os arquivos anuais de **acidentes agrupados por ocorrência** da PRF, extraídos do sistema BAT, cobrindo 2023, 2024 e 2025.

- Portal: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf
- Dicionário oficial: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dicionario-acidentes
- Granularidade: **cada linha do CSV corresponde a uma ocorrência**. A mesma ocorrência não deve ser multiplicada pelo número de pessoas envolvidas.
- Formato: CSV em ZIP, separador `;`, codificação Latin-1 e ponto decimal representado por vírgula em coordenadas.

## Variáveis utilizadas

| Campo original | Papel na análise | Tipo após ETL |
|---|---|---|
| `id` | Identificador da ocorrência e checagem de duplicidade | inteiro |
| `data_inversa` | Data do sinistro, base para séries temporal e mensal | data |
| `horario` | Horário informado no registro; validado para extrair a hora (0–23) | texto HH:MM ou HH:MM:SS |
| `dia_semana` | Dia informado na origem; comparação cruzada com a data quando necessário | texto |
| `uf` | Unidade federativa | texto |
| `br` | Número da rodovia federal | inteiro |
| `km` | Quilômetro de registro | numérico |
| `municipio` | Município informado | texto |
| `causa_acidente` | Principal causa registrada no BAT | categoria |
| `tipo_acidente` | Tipo da ocorrência | categoria |
| `classificacao_acidente` | Classificação de consequência reportada | categoria |
| `tipo_pista` | Característica viária (simples, dupla, múltipla) | categoria |
| `fase_dia` | Amanhecer, pleno dia, anoitecer ou noite | categoria |
| `condicao_metereologica` | Condição meteorológica informada | categoria |
| `mortos` | Número de pessoas mortas no registro | inteiro |
| `feridos` | Número de pessoas feridas no registro | inteiro |
| `latitude`, `longitude` | Coordenadas usadas somente para gerar células agregadas | decimal |

**Campos derivados:** `ano`, `mes`, `hora` (0–23; nulo quando o horário é inválido), `dia_num` (segunda=0 a domingo=6, calculado da data), `br_label`, `fatal` (ocorrência com pelo menos 1 morte), `localizacao_valida`, `lat_cell` e `lon_cell`.

## Agregados e artefatos da edição final

- `annual`, `monthly`: quantidades de sinistros, mortos, feridos e/ou ocorrências fatais por ano e mês.
- `hourly`, `weekday`: distribuição de 24 horas e 7 dias da semana, derivadas dos campos temporais. A distribuição horária exclui horários inválidos, que são auditados.
- `uf_annual`: sinistros, mortos e feridos por UF e ano.
- `top_municipalities_2025`: cidades de maior ocorrência em 2025, sempre identificadas junto com sua UF.
- `fatal_by_type_2025`: total e proporção de ocorrências fatais dentro de cada tipo de sinistro (mínimo de 100 registros).
- `eda_summary`: média, mediana, quartis e desvio-padrão populacional dos 36 totais mensais.
- `map_grid_2025`: células agregadas de 0,5 grau, sem coordenadas individuais.

**Arquivo compactado para reuso:** `data/processed/sinistros_diarios_uf_2023_2025.csv.gz` (uma linha por dia e UF; apenas contagens agregadas).


## Métricas

- **Sinistros:** número de IDs distintos depois de remover possíveis duplicatas e validar o ano.
- **Mortes/feridos:** soma dos campos de pessoas por ocorrência, não quantidade de acidentes fatais.
- **Ocorrências fatais:** número de sinistros cujo campo `mortos` é maior que zero.
- **Percentual de ocorrências fatais em grupo:** ocorrências fatais do grupo / total de ocorrências no grupo × 100. Trata-se de proporção interna, **não** risco por exposição ao tráfego.
- **Localização agregada:** coordenadas válidas podem ser auditadas como células de 0,5 grau, mas o artigo publicado não exibe mapas nem pontos individuais.

## Qualidade e limitações

O pipeline exporta `data/processed/auditoria.json` com totais por ano, duplicatas, datas inválidas, ausências e coordenadas fora de limites geográficos plausíveis para o Brasil. Também calcula os hashes SHA-256 dos ZIPs originais.

A análise não controla quilometragem percorrida, volume de veículos, extensão fiscalizada, qualidade da infraestrutura, tipo de veículo ou condições pessoais em todos os cruzamentos. Não inferir causalidade a partir de associações simples.

**Importante:** a PRF pode atualizar seus arquivos e anuários. Totais obtidos com uma extração em outro momento podem diferir ligeiramente dos aqui documentados.

## Uso responsável da localização

A edição final apresenta distribuição territorial somente por UF, município e rodovia em gráficos e tabelas. Coordenadas válidas são verificadas pelo ETL e podem ser mantidas como agregados de auditoria (`map_grid_2025`), mas não são representadas em mapas na interface. A comparação entre regiões permanece descritiva e não permite inferir risco por veículo-quilômetro.
