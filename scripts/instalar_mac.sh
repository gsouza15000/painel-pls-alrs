#!/usr/bin/env bash
# Instala no Mac um agendamento (launchd) que roda a coleta ao ligar/logar e a cada 4 horas
# enquanto o Mac estiver ligado. Se ficou desligado, recupera na próxima vez que ligar.
# Uso (dentro da pasta do repositório clonado):  ./scripts/instalar_mac.sh
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
ROT="com.gsouza.painel-pls-alrs"
PLIST="$HOME/Library/LaunchAgents/$ROT.plist"
LOG="$HOME/Library/Logs/painel-pls-alrs.log"

chmod +x "$RAIZ/scripts/atualizar_local.sh"
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$ROT</string>
  <key>ProgramArguments</key><array>
    <string>/bin/bash</string><string>-c</string>
    <string>sleep 45; "$RAIZ/scripts/atualizar_local.sh"</string>
  </array>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>StartInterval</key><integer>14400</integer>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict></plist>
PL

launchctl bootout "gui/$(id -u)/$ROT" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Instalado. Log: $LOG"
echo "Para remover: launchctl bootout gui/$(id -u)/$ROT && rm \"$PLIST\""
