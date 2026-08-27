#!/usr/bin/env bash
# Prova de que codigo nao entra sem fase de build, e de como se autoriza.
#
# Nao e bloqueio automatico: e recusa com o custo na tela, e passagem so com
# autorizacao deliberada que fica no historico do git para sempre.
set -u
KIT="${KIT:-/home/user/product-lifecycle-kit}"
ALVO="$1"
L=bin/lifecycle

titulo() { printf '\n----- %s -----\n' "$1"; }
mostra() { printf '$ %s\n' "$*"; "$@" 2>&1; printf 'EXIT: %d\n' "$?"; }

rm -rf "$ALVO"; mkdir -p "$ALVO/src"; cd "$ALVO" || exit 1
git init -q -b main .
git config user.name "Jonathan Camargo"
git config user.email "jonathan.camargo1@gmail.com"
printf 'print("v1")\n' > src/app.py
git add -A && git commit -q -m "projeto que ja existia"

titulo "1. Instalacao, tier 2"
"$KIT/install.sh" . --adapters none >/dev/null 2>&1
python3 - <<'PY'
import sys
sys.dont_write_bytecode = True  # nao sujar o alvo com __pycache__
sys.path.insert(0, "bin/lifecycle")
import _kitlib as kit
s = kit.read_state("."); s.update({"project": "prova-fase", "tier": 2})
kit.write_state(".", s)
PY
git add -A && git commit -q -m "instala o product-lifecycle-kit"
printf 'instalado, tier 2, nenhuma fase comecada\n'

titulo "2. O que falta, antes de qualquer coisa"
mostra python3 $L/plan

titulo "3. O agente tenta subir feature sem fase de build"
printf 'print("feature sem PRD, sem spec, sem review")\n' >> src/app.py
git add src/app.py
mostra git commit -m "adiciona feature de checkout"

titulo "4. O caminho recomendado funciona"
python3 $L/session-open --agent codex > /dev/null 2>&1
mostra python3 $L/new-artifact 01-contexto checkout "Contexto do checkout" --owner "Jonathan Camargo"

titulo "5. Mas na fase 01 codigo continua recusado"
mostra git commit -m "adiciona feature de checkout"

titulo "6. Com autorizacao explicita do humano, passa"
mostra git commit -m "corrige timeout do gateway

Sem-fase: hotfix de producao, autorizado por Jonathan Camargo"

titulo "7. A autorizacao vazia nao passa"
# So o arquivo de codigo em staging: com docs/ junto e a sessao aberta, quem
# recusaria primeiro seria o guard-commit, e a prova mostraria outra coisa.
printf 'print("mais uma")\n' >> src/app.py
git add src/app.py
mostra git commit -m "outra coisa

Sem-fase:"

titulo "8. A divida aparece em toda sessao, e o rastro e permanente"
mostra python3 $L/gate-check
mostra git log --grep '^Sem-fase:' --oneline
