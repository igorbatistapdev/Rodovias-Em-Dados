# Rodovias em Dados v5.1 — Publicação no GitHub pelo VS Code

**Repositório público existente (confirmado em 16/11/2026):** https://github.com/igorbatistapdev/Rodovias-Em-Dados

**Importante:** o repositório foi encontrado vazio nesta verificação. O ZIP contém o projeto **completo** pronto para enviar, mas **nenhum `git push` foi realizado**.

## 1. Abrir o projeto

Extraia o arquivo ZIP em uma pasta local. Abra o **Visual Studio Code → Arquivo → Abrir Pasta** e selecione a pasta `rodovias-em-dados` (aquela que contém `README.md`, `docs/`, `src/`, etc.). Abra o terminal integrado (PowerShell).

Para visualizar o site antes de enviar, na raiz do projeto:

```powershell
python -m http.server 8000 -d docs
```

Abra `http://localhost:8000` em seu navegador. O terminal fica ocupado enquanto o servidor estiver ativo; use `Ctrl+C` para interromper ou abra outro terminal no VS Code.

## 2. Enviar ao repositório já existente

Verifique se o Git está instalado:

```powershell
git --version
```

Em seguida, **a partir da pasta raiz** (e não dentro de `docs`), execute:

```powershell
git init
git branch -M main
git add .
git status
git commit -m "Publica Rodovias em Dados v5.1"
git remote add origin https://github.com/igorbatistapdev/Rodovias-Em-Dados.git
git push -u origin main
```

A primeira autenticação no GitHub pode abrir o navegador ou solicitar credenciais. Se o Git disser que seu nome ou e-mail não estão configurados, use `git config --global user.name "SEU NOME"` e `git config --global user.email "SEU EMAIL VINCULADO AO GIT"` e repita o commit. **Não envie senhas nem tokens no chat.**

Se aparecer `error: remote origin already exists`, **não repita `git remote add`**. Execute `git remote -v` para conferir o remoto e, se ele apontar para o local errado, use `git remote set-url origin https://github.com/igorbatistapdev/Rodovias-Em-Dados.git`.

> Atenção: se o repositório remoto deixou de estar vazio ou contém commits de outras pessoas, não use `--force`. Avalie as mudanças do remoto antes de enviar.

## 3. Ativar o GitHub Pages

Depois que os arquivos aparecerem no repositório, acesse **Settings → Pages → Build and deployment**:

1. Source: **Deploy from a branch**;
2. Branch: `main`;
3. Folder: `/docs`;
4. Clique em **Save**.

URL esperada **somente após a ativação bem-sucedida**: https://igorbatistapdev.github.io/Rodovias-Em-Dados/. Confirme a URL mostrada pelo GitHub, especialmente a capitalização do nome do repositório.

A pasta `docs/` contém um arquivo `.nojekyll`, para evitar processamento Jekyll sobre os recursos estáticos.

## 4. Conferência após publicação

- Abrir a página inicial no endereço público;
- Conferir CSS, favicon, gráficos e tabelas, inclusive em tela pequena;
- Alternar controles dos gráficos e exportar CSV;
- Revisar as URLs das referências;
- Usar o botão **Imprimir / PDF** no Edge ou Chrome;
- Verificar o link **Repositório GitHub** no cabeçalho;
- Conferir `README.md`, `CITATION.cff`, origem dos dados e testes Python.

## 5. Manutenção

Mude conteúdos e textos no arquivo `templates/article.html`, não só em `docs/index.html`. Depois de alterar o template, regenere a página com `python scripts/refinar_artigo.py` (requer as dependências instaladas). Para atualizar o site, faça novo `git add .`, `git commit` e `git push`. GitHub Pages atualizará a página a partir da pasta `/docs`.

**Python 3.13:** necessário para executar o pipeline completo com as versões de dependência fixadas; o site HTML já gerado funciona sem instalar Pandas.
