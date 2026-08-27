#!/bin/sh
# Encanamento, nao logica: chama session-close --check e traduz o resultado
# para o protocolo de hook. Exit 2 impede o encerramento.
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] || exit 0

ENTRADA=$(cat)
ATIVO=$(printf '%s' "$ENTRADA" | python3 -c 'import json,sys
try:
    dados = json.load(sys.stdin)
except Exception:
    print("false"); sys.exit(0)
print("true" if dados.get("stop_hook_active") else "false")')

# Ja bloqueamos uma vez nesta parada. Bloquear de novo viraria laco.
[ "$ATIVO" = "true" ] && exit 0

MOTIVO=$(python3 "$ROOT/bin/lifecycle/session-close" --check 2>&1)
if [ $? -eq 0 ]; then
    exit 0
fi
# O nucleo devolve o motivo em linguagem neutra. Traduzir para o comando
# deste runtime e trabalho do adaptador, nao do nucleo.
printf '%s\nExecute /session-close.\n' "$MOTIVO" >&2
exit 2
