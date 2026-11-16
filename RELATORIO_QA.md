# Relatório final de qualidade | Rodovias em Dados v5.1

**Data:** 12/11/2026 · **Ambiente local:** Python 3.13.5 / Linux; Chromium headless; testes de interface via HTML/CSS/JS incorporados em documento de verificação por restrições de navegação da sandbox.

## Inspeções executadas

- **Pipeline completo:** `python scripts/run_pipeline.py`, sem erros de execução.
- **Testes automatizados:** `python -m pytest -q`, **23 aprovados**. Inclusos ETL, regressões, design, referências/âncoras, imagens locais, versão e cores.
- **Dados:** 213.497 sinistros, 17.833 mortes, 246.608 feridos e 15.293 ocorrências com pelo menos uma morte. Valores derivados dos ZIPs originais, sem alteração.
- **Interface:** telas desktop 1440 px, tablet 768 px, mobile 390 e 360 px; sem rolagem horizontal do documento e sem erros de JavaScript.
- **Interações:** 36 pontos da visualização mensal, alternância de indicador para mortes, 7 categorias de dia da semana, 7 causas e 9 rodovias; testadas em Chromium.
- **Paleta:** sinistros azul, mortes cobre, feridos dourado, ranking territorial roxo, tipos de sinistro com diferentes tons moderados. As figuras vetoriais de impressão usam a mesma direção cromática.
- **PDF:** 9 páginas A4, texto selecionável, Abstract iniciando na página 2, figuras SVG, referências na última página e URLs clicáveis.
- **Normas acadêmicas:** NBR 6023:2025 para referências e NBR 10520:2023 para citações autor-data; texto, método, conclusão e fontes conforme a estrutura HTML determinada pelo professor.
- **Vídeo:** conferido visualmente em dez pontos, de 0 a 45 segundos. Ver `AUDITORIA_FINAL_DO_VIDEO.md`.

## Evidências de transparência

- Os sete URLs das referências foram identificados e consultados por navegação pública, conforme `REFERENCIAS_E_ABNT.md`. Isto não substitui testar cada um na rede do usuário.
- A rede do ambiente Python não permite acesso HTTP externo direto; nenhum relatório foi fabricado de respostas HTTP 200.
- O arquivo PDF exportado é uma referência da aparência local e pode variar conforme fontes/escala do Edge ou Chrome do usuário.
- Não foi realizada validação no Windows do usuário nem publicação no GitHub Pages; são tarefas posteriores explicitamente acordadas.

## Pendências legítimas antes da apresentação

1. Publicar repositório público e habilitar GitHub Pages em `/docs`, substituir o link de perfil pelo URL real do projeto quando disponível.
2. Verificar na rede do usuário os URLs externos das referências, pois serviços de terceiros podem alterar endereços/bloquear acesso.
3. Revisão humana do professor quanto a eventuais exigências adicionais de formatação/ênfase ou autoria de artigo.
4. Executar instalação e pipeline no Windows com Python 3.13.

**Conclusão:** edição final local preparada e testada; qualidade técnica elevada, mas nota 10 não é garantida nem pode ser declarada antes da avaliação do professor e do requisito de publicação pública.
