#!/usr/bin/env bash
# Prova do modo B: repositorio operado pelo Codex (--adapters codex).
# Nenhum hook de runtime. Tudo que segura o processo aqui e git hook e script.
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

titulo "1. Instalacao sem nenhum hook de runtime"
mostra "$KIT/install.sh" . --adapters codex

titulo "2. Nenhum artefato de runtime de agente foi instalado"
mostra ls -a .
printf '$ ls .git/hooks/pre-commit .git/hooks/commit-msg\n'
ls .git/hooks/pre-commit .git/hooks/commit-msg 2>&1
printf 'EXIT: %d\n' "$?"

python3 - <<'PY'
import sys
sys.path.insert(0, "bin/lifecycle")
import _kitlib as kit
state = kit.read_state(".")
state.update({"project": "prova-b", "tier": 1,
              "next_action": "Escrever o contexto e o nao-escopo"})
kit.write_state(".", state)
PY
git add -A && git commit -q -m "instala o product-lifecycle-kit" && echo "commit inicial ok"

propoe() {
    python3 - "$1" "$2" <<'PY'
import sys
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

aprova() {
    python3 - "$1" "$2" <<'PY'
import sys, datetime
sys.path.insert(0, "bin/lifecycle")
import _kitlib as kit
from pathlib import Path
alvo, slug = sys.argv[1], sys.argv[2]
hoje = datetime.date.today().isoformat()
p = Path(alvo)
p.write_text((p.read_text(encoding="utf-8")
              .replace("status: proposed", "status: approved", 1)
              .replace("approved_by: null", "approved_by: Jonathan Camargo", 1)
              .replace("approved_at: null", "approved_at: %s" % hoje, 1)),
             encoding="utf-8")
state = kit.read_state(".")
state["gates"][slug].update({"status": "approved", "by": "Jonathan Camargo",
                             "date": hoje})
kit.write_state(".", state)
print("gate %s aprovado por Jonathan Camargo em %s" % (slug, hoje))
PY
    git add -A && git commit -q -m "humano aprova o gate $2" && echo "commit da aprovacao ok"
}

handoff() {
    printf '## Fiz\n- %s\n\n## Falta\n- aprovar o gate\n\n## Cuidado com\n- nada pendente\n' "$1" > /tmp/handoff-b.md
    echo /tmp/handoff-b.md
}

titulo "3. Sessao 01, fase 01-contexto, invocando os scripts direto"
printf '$ python3 %s/session-open --agent codex\n' "$L"
python3 $L/session-open --agent codex > /tmp/open-b.log 2>&1
printf '[cabecalho de AGENTS.md, STATE.md, CONTEXT.md e principles.md suprimido aqui, %d linhas]\n' "$(wc -l < /tmp/open-b.log)"
tail -4 /tmp/open-b.log
printf 'EXIT: 0\n'

mostra python3 $L/new-artifact 01-contexto nucleo "Contexto do prova-b" --owner "Jonathan Camargo"
propoe docs/areas/nucleo/01-contexto/contexto-do-prova-b.md 01-contexto
mostra python3 $L/session-close --handoff "$(handoff 'escrevi o contexto e o nao-escopo')"
aprova docs/areas/nucleo/01-contexto/contexto-do-prova-b.md 01-contexto

sessao() {
    titulo "4. Sessao seguinte, fase $1"
    python3 $L/session-open --agent codex > /tmp/open-b.log 2>&1
    printf '$ python3 %s/session-open --agent codex\nEXIT: %d\n' "$L" "$?"
    mostra python3 $L/new-artifact "$1" nucleo "$2" --owner "Jonathan Camargo" --inputs "$3"
    propoe "$4" "$5"
    mostra python3 $L/session-close --handoff "$(handoff "executei a fase $1")"
    aprova "$4" "$5"
}

sessao 13-build "Build do prova-b" \
    docs/areas/nucleo/01-contexto/contexto-do-prova-b.md \
    docs/areas/nucleo/13-build-log/build-do-prova-b.md 13-build-log
sessao 14-review "Review do prova-b" \
    docs/areas/nucleo/13-build-log/build-do-prova-b.md \
    docs/areas/nucleo/14-review/review-do-prova-b.md 14-review
sessao 17-ship "Ship do prova-b" \
    docs/areas/nucleo/14-review/review-do-prova-b.md \
    docs/areas/nucleo/17-ship/ship-do-prova-b.md 17-ship

# ---------------------------------------------------------------------------
# O que so o modo B pode provar: sem hook de escrita, quem segura e o git.
# ---------------------------------------------------------------------------
ARTEFATO=docs/areas/nucleo/01-contexto/contexto-do-prova-b.md

titulo "5. Edicao num artefato aprovado. Nada impede a escrita no disco."
printf 'Uma linha que um agente sem hook de runtime conseguiu escrever.\n' >> $ARTEFATO
mostra git add "$ARTEFATO"

titulo "5a. git commit e abortado pelo pre-commit, com a saida de guard-commit"
mostra git commit -m "altera um artefato aprovado sem decisao"

titulo "5b. o artefato aprovado continua intocado no repositorio"
mostra git log --oneline -1 -- "$ARTEFATO"

titulo "6. Entrada DECIDED em decisions.log liberando o mesmo path"
python3 - "$ARTEFATO" <<'PY'
import sys, datetime
from pathlib import Path
alvo = sys.argv[1]
hoje = datetime.date.today().isoformat()
log = Path("docs/_context/decisions.log")
log.write_text(log.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + (
    "## D-0001 | %s | DECIDED | Corrigir o nao-escopo do contexto aprovado\n"
    "Contexto: o nao-escopo saiu incompleto e ja esta aprovado.\n"
    "Opcoes: A reabrir o gate / B corrigir o artefato aprovado\n"
    "Recomendacao do agente: B, porque a correcao nao muda a decisao.\n"
    "Decisao: seguir com B.\n"
    "Decidido por: Jonathan Camargo em %s\n"
    "Afeta: %s\n") % (hoje, hoje, alvo), encoding="utf-8")
print("decisao D-0001 registrada como DECIDED, Afeta: %s" % alvo)
PY
mostra git add -A

titulo "6a. o mesmo commit agora passa"
mostra git commit -m "corrige o artefato aprovado sob a decisao D-0001"

titulo "7. commit-msg recusa sessao 99 quando o session_counter e 4"
printf '$ grep session_counter docs/STATE.md\n'
grep session_counter docs/STATE.md
printf 'nota.txt\n' > nota.txt
git add nota.txt
mostra git commit -m "sessao 99: 17-ship resumo mentiroso"

titulo "7a. a mesma mudanca passa com uma mensagem que nao e de sessao"
mostra git commit -m "adiciona uma nota solta"

titulo "8. Estado final"
mostra python3 $L/gate-check
mostra git log --oneline
