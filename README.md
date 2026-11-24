# Painel de PLs da ALRS

Painel de busca dos projetos de lei (PL) e de lei complementar (PLC) da Assembleia Legislativa do RS.

- Os dados vêm da pesquisa pública de proposições (ww4.al.rs.gov.br/legislativo).
- A coleta (`scripts/coletar.py`) roda no computador do mantenedor via `scripts/atualizar_local.sh` (o site da ALRS bloqueia os servidores do GitHub); o push em `docs/` dispara a publicação no GitHub Pages.
- `docs/novos.json` lista os projetos detectados nos últimos 30 dias, com a data de detecção (`dt`).
- As áreas temáticas são definidas por palavras da ementa em `scripts/areas.py`.
- O partido segue a lista atual de deputados (`scripts/partidos.json`).

Agendamento local (Linux/Mac): `crontab -e` e `0 7 * * * /caminho/painel-pls-alrs/scripts/atualizar_local.sh >> /tmp/painel.log 2>&1`.
