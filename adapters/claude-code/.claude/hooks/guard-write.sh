#!/bin/sh
# Encanamento, nao logica: extrai tool_input.file_path do evento PreToolUse e
# entrega ao guard-write. Toda a regra esta em bin/lifecycle/guard-write.
# Exit 2 bloqueia a ferramenta.
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] || exit 0

CAMINHO=$(python3 -c 'import json,sys
try:
    dados = json.load(sys.stdin)
except Exception:
    sys.exit(0)
print(dados.get("tool_input", {}).get("file_path", ""))')

[ -n "$CAMINHO" ] || exit 0
python3 "$ROOT/bin/lifecycle/guard-write" "$CAMINHO"
exit $?
