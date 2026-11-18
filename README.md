# Painel de PLs da ALRS

Painel de busca dos projetos de lei (PL) e de lei complementar (PLC) da Assembleia Legislativa do RS.

- Os dados vêm da pesquisa pública de proposições (ww4.al.rs.gov.br/legislativo).
- Todo dia o GitHub Actions executa `scripts/coletar.py`, atualiza `docs/data.json` e publica o painel no GitHub Pages.
- `docs/novos.json` lista os projetos detectados nos últimos 30 dias, com a data de detecção (`dt`).
- As áreas temáticas são definidas por palavras da ementa em `scripts/areas.py`.
- O partido segue a lista atual de deputados (`scripts/partidos.json`).

Para rodar uma coleta manual: aba **Actions**, fluxo **Atualizar painel**, botão **Run workflow**.
