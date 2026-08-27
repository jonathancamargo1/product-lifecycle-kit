#!/usr/bin/env bash
# Prova do modo A: repositorio operado pelo Claude Code (--adapters claude-code)
set -u
KIT=/home/user/product-lifecycle-kit
ALVO="$1"
L=bin/lifecycle

titulo() { printf '\n----- %s -----\n' "$1"; }
mostra() { printf '$ %s\n' "$*"; "$@" 2>&1; printf 'EXIT: %d\n' "$?"; }

rm -rf "$ALVO"; mkdir -p "$ALVO"; cd "$ALVO" || exit 1
git init -q -b main .
git config user.name "Jonathan Camargo"
git config user.email "jonathan.camargo1@gmail.com"

titulo "1. Instalacao"
mostra "$KIT/install.sh" . --adapters claude-code

titulo "2. Git hooks instalados"
mostra ls -1 .git/hooks/pre-commit .git/hooks/commit-msg

# Estado inicial do projeto, feito por humano.
python3 - <<'PY'
import sys
sys.dont_write_bytecode = True  # nao sujar o alvo com __pycache__
sys.path.insert(0, "bin/lifecycle")
import _kitlib as kit
state = kit.read_state(".")
state.update({"project": "prova-a", "tier": 1,
              "next_action": "Escrever o contexto e o nao-escopo"})
kit.write_state(".", state)
PY
git add -A && git commit -q -m "instala o product-lifecycle-kit" && echo "commit inicial ok"

# helpers ------------------------------------------------------------------
propoe() {  # $1 = path do artefato, $2 = slug do gate
    python3 - "$1" "$2" <<'PY'
import sys
sys.dont_write_bytecode = True  # nao sujar o alvo com __pycache__
sys.path.insert(0, "bin/lifecycle")
import _kitlib as kit
from pathlib import Path
alvo, slug = sys.argv[1], sys.argv[2]
p = Path(alvo)
p.write_text(p.read_text(encoding="utf-8").replace("status: draft", "status: proposed", 1),
             encoding="utf-8")
state = kit.read_state(".")
state["gates"][slug]["status"] = "proposed"
kit.write_state(".", state)
print("artefato %s marcado proposed pelo agente" % alvo)
PY
}

aprova() {  # $1 = path do artefato, $2 = slug do gate. Papel humano.
    python3 - "$1" "$2" <<'PY'
import sys, datetime
sys.dont_write_bytecode = True  # nao sujar o alvo com __pycache__
sys.path.insert(0, "bin/lifecycle")
import _kitlib as kit
from pathlib import Path
alvo, slug = sys.argv[1], sys.argv[2]
hoje = datetime.date.today().isoformat()
p = Path(alvo)
texto = (p.read_text(encoding="utf-8")
         .replace("status: proposed", "status: approved", 1)
         .replace("approved_by: null", "approved_by: Jonathan Camargo", 1)
         .replace("approved_at: null", "approved_at: %s" % hoje, 1))
p.write_text(texto, encoding="utf-8")
state = kit.read_state(".")
state["gates"][slug].update({"status": "approved", "by": "Jonathan Camargo",
                             "date": hoje})
kit.write_state(".", state)
print("gate %s aprovado por Jonathan Camargo em %s" % (slug, hoje))
PY
    git add -A && git commit -q -m "humano aprova o gate $2" && echo "commit da aprovacao ok"
}

handoff() {  # $1 = texto do Fiz
    printf '## Fiz\n- %s\n\n## Falta\n- aprovar o gate\n\n## Cuidado com\n- nada pendente\n' "$1" > /tmp/handoff-a.md
    echo /tmp/handoff-a.md
}

# --------------------------------------------------------------- sessao 01
titulo "3. Sessao 01, fase 01-contexto"
mostra python3 $L/session-open --agent claude-code

titulo "3a. session-open recusa abrir com a sessao anterior aberta"
mostra python3 $L/session-open --agent claude-code

titulo "3b. session-close --check recusa enquanto a sessao esta aberta"
mostra python3 $L/session-close --check

titulo "3c. gate-check --phase 13-build ANTES de aprovar a fase 01"
mostra python3 $L/gate-check --phase 13-build

mostra python3 $L/new-artifact 01-contexto nucleo "Contexto do prova-a" --owner "Jonathan Camargo"
propoe docs/areas/nucleo/01-contexto/contexto-do-prova-a.md 01-contexto

titulo "3d. session-close com handoff"
mostra python3 $L/session-close --handoff "$(handoff 'escrevi o contexto e o nao-escopo')"

titulo "3e. session-close --check depois de fechar"
mostra python3 $L/session-close --check

titulo "4. Humano aprova o gate 01"
aprova docs/areas/nucleo/01-contexto/contexto-do-prova-a.md 01-contexto

titulo "4a. gate-check --phase 13-build DEPOIS de aprovar a fase 01"
mostra python3 $L/gate-check --phase 13-build

titulo "4b. guard-write num artefato aprovado"
mostra python3 $L/guard-write docs/areas/nucleo/01-contexto/contexto-do-prova-a.md

# --------------------------------------------------------------- sessoes 02 a 04
sessao() {  # $1 = fase, $2 = titulo, $3 = input, $4 = arquivo gerado, $5 = slug
    titulo "5. Sessao seguinte, fase $1"
    python3 $L/session-open --agent claude-code > /tmp/open.log 2>&1
    printf '$ python3 %s/session-open --agent claude-code\n[saida completa suprimida, ver sessao 01]\nEXIT: %d\n' "$L" "$?"
    mostra python3 $L/new-artifact "$1" nucleo "$2" --owner "Jonathan Camargo" --inputs "$3"
    propoe "$4" "$5"
    mostra python3 $L/session-close --handoff "$(handoff "executei a fase $1")"
    aprova "$4" "$5"
}

sessao 13-build "Build do prova-a" \
    docs/areas/nucleo/01-contexto/contexto-do-prova-a.md \
    docs/areas/nucleo/13-build-log/build-do-prova-a.md 13-build-log
sessao 14-review "Review do prova-a" \
    docs/areas/nucleo/13-build-log/build-do-prova-a.md \
    docs/areas/nucleo/14-review/review-do-prova-a.md 14-review
sessao 17-ship "Ship do prova-a" \
    docs/areas/nucleo/14-review/review-do-prova-a.md \
    docs/areas/nucleo/17-ship/ship-do-prova-a.md 17-ship

titulo "6. Estado final"
mostra python3 $L/gate-check
mostra sed -n '/```yaml/,/```/p' docs/STATE.md
mostra git log --oneline
