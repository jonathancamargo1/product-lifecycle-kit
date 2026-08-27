#!/usr/bin/env bash
# Prova de que install.sh encadeia hook de git existente e mescla um
# .claude/settings.json que ja tem hooks do projeto, sem remover nada.
set -u
KIT="${KIT:-/home/user/product-lifecycle-kit}"
ALVO="$1"
mostra() { printf '$ %s\n' "$*"; "$@" 2>&1; printf 'EXIT: %d\n' "$?"; }

rm -rf "$ALVO"; mkdir -p "$ALVO"; cd "$ALVO" || exit 1
git init -q -b main .
git config user.name "Jonathan Camargo"
git config user.email "jonathan.camargo1@gmail.com"

printf -- '----- 1. O projeto ja tem um pre-commit proprio e hooks proprios -----\n'
cat > .git/hooks/pre-commit <<'HOOK'
#!/bin/sh
echo "HOOK ANTERIOR DO PROJETO RODOU"
exit 0
HOOK
chmod +x .git/hooks/pre-commit
mkdir -p .claude
cat > .claude/settings.json <<'JSON'
{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "meu-hook-do-projeto.sh"}]}]}}
JSON
mostra cat .git/hooks/pre-commit

printf -- '\n----- 2. Instalacao -----\n'
"$KIT/install.sh" . --adapters all 2>&1 | grep -i "encadeado\|mesclad\|preservad\|gate-check"

printf -- '\n----- 3. O hook do projeto foi preservado, nao sobrescrito -----\n'
mostra cat .git/hooks/pre-commit.local

printf -- '\n----- 4. settings.json: o hook do projeto continua la -----\n'
printf '$ python3 lista os hooks de .claude/settings.json\n'
python3 -c "
import json
d = json.load(open('.claude/settings.json'))
for evento, entradas in d['hooks'].items():
    for e in entradas:
        for h in e.get('hooks', []):
            print('%-14s %s' % (evento, h['command']))"

printf -- '\n----- 5. Num commit real, os dois rodam, o do projeto primeiro -----\n'
echo teste > a.txt
git add a.txt
mostra git commit -m "primeiro commit"
