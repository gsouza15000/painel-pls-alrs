#!/usr/bin/env bash
# Configura um servidor Ubuntu/Debian (de preferência com IP brasileiro) para coletar os PLs da ALRS todo dia.
# Uso, logado no servidor:  curl -fsSL https://raw.githubusercontent.com/gsouza15000/painel-pls-alrs/main/scripts/setup_vps.sh | bash
set -euo pipefail
REPO="gsouza15000/painel-pls-alrs"
DIR="$HOME/painel-pls-alrs"

echo "== 1/5 Instalando git e python =="
if command -v apt-get >/dev/null; then
  sudo apt-get update -qq && sudo apt-get install -y -qq git python3 cron curl tzdata
fi
sudo timedatectl set-timezone America/Sao_Paulo 2>/dev/null || true

echo "== 2/5 Testando acesso ao site da ALRS =="
if curl -sS -m 60 -o /dev/null -w "HTTP %{http_code}\n" "https://ww4.al.rs.gov.br/legislativo/pesquisa?siglaTipoProposicao=PL&anoProposicao=2026&pagina=1"; then
  echo "OK: o servidor consegue acessar a ALRS."
else
  echo "ERRO: este servidor também não alcança a ALRS (IP bloqueado). Use outro provedor/região e rode de novo."; exit 1
fi

echo "== 3/5 Chave SSH para enviar os dados ao GitHub =="
mkdir -p ~/.ssh && chmod 700 ~/.ssh
[ -f ~/.ssh/painel_alrs ] || ssh-keygen -t ed25519 -N "" -C "painel-alrs-vps" -f ~/.ssh/painel_alrs >/dev/null
grep -q "painel_alrs" ~/.ssh/config 2>/dev/null || cat >> ~/.ssh/config <<CFG
Host github-painel
  HostName github.com
  User git
  IdentityFile ~/.ssh/painel_alrs
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
CFG
echo
echo ">>> Copie a chave abaixo e cadastre em:"
echo ">>> https://github.com/$REPO/settings/keys/new  (marque 'Allow write access')"
echo
cat ~/.ssh/painel_alrs.pub
echo
read -r -p "Depois de cadastrar a chave, aperte ENTER para continuar... " _ </dev/tty

echo "== 4/5 Clonando e testando a coleta =="
[ -d "$DIR/.git" ] || git clone "git@github-painel:$REPO.git" "$DIR"
cd "$DIR"
git config user.name "painel-pls-alrs"
git config user.email "actions@users.noreply.github.com"
chmod +x scripts/atualizar_local.sh
./scripts/atualizar_local.sh

echo "== 5/5 Agendando todo dia às 07:00 (Brasília) =="
LINHA="0 7 * * * $DIR/scripts/atualizar_local.sh >> $HOME/painel.log 2>&1"
( crontab -l 2>/dev/null | grep -v atualizar_local.sh; echo "$LINHA" ) | crontab -
sudo systemctl enable --now cron 2>/dev/null || true
echo "Pronto. Log em ~/painel.log"
