#!/usr/bin/env bash
# Roda a coleta no seu computador (IP brasileiro) e envia os dados ao GitHub.
# O GitHub Actions publica o painel automaticamente quando docs/ muda.
set -euo pipefail
cd "$(dirname "$0")/.."
git pull --ff-only
python3 scripts/coletar.py
git add docs scripts/partidos.json
if git diff --cached --quiet; then
  echo "sem mudanças"
else
  git commit -m "Atualiza dados ($(date -u +%F))"
  git push
fi
