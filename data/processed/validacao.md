# Validação dos registros PRF — extração do projeto

## Resultado do pipeline

| Ano | Linhas lidas | Linhas após validação | Duplicações por ID | Datas inválidas | Coordenadas fora do intervalo | Classificação ausente |
|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 67.766 | 67.766 | 0 | 0 | 0 | 1 |
| 2024 | 73.202 | 73.202 | 0 | 0 | 0 | 1 |
| 2025 | 72.529 | 72.529 | 0 | 0 | 0 | 1 |

- Critério geográfico preliminar: latitude entre -35 e 6, longitude entre -74 e -32. A aprovação nesse filtro não comprova precisão cartográfica ou correspondência com a malha rodoviária.
- Identificador de ocorrência `id` sem duplicações nos ZIPs analisados.
- Datas pertencentes ao ano do arquivo correspondente.
- Campo `classificacao_acidente`: um valor ausente em cada ano; a métrica de ocorrência fatal foi definida pelo campo numérico `mortos > 0`.
- Os arquivos de origem foram preservados sem alterações; seus hashes estão em `auditoria.json`.
- Os resultados são reprodutíveis com `python scripts/run_pipeline.py`.

## Comparação com documentos oficiais

A PRF atualiza suas bases ao longo do tempo. As contagens acima refletem os arquivos ZIP preservados no projeto, extraídos em novembro de 2026. Publicações jornalísticas ou anuários podem apresentar pequenas diferenças quando se baseiam em extrações anteriores. Este estudo **não mistura** os dados de diferentes versões em uma mesma série; todos os indicadores principais vêm dos três ZIPs analisados.

## Cuidados para interpretação

- A soma de mortos representa pessoas falecidas, não necessariamente sinistros fatais (que podem ter mais de uma morte).
- A proporção de sinistros com pelo menos uma morte é calculada **dentro de cada categoria** e não é uma medida de risco por viagem ou quilometragem percorrida.
- Não há ajuste por exposição de tráfego nem controle de confundidores.
- O artigo não publica mapas nem localizações individuais; a informação territorial aparece como agregados por UF, município e rodovia.
- Resultados são descritivos e não demonstram causalidade.
