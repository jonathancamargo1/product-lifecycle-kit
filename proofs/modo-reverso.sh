#!/usr/bin/env bash
# Prova do modo reverso: gate por fase suspenso, confirmacao em bloco.
#
# O que a prova mede: que a confirmacao em bloco continua sendo ato humano, que
# ela recusa reconstrucao sem ponteiro de evidencia e pergunta em aberto, e que
# a procedencia fica gravada para separar o que foi vivido do que foi
# reconstruido.
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
printf 'def cobranca():\n    return "pix"\n' > src/cobranca.py
printf '# Servico de cobranca\n\nAceita pix. Boleto ficou de fora.\n' > README.md
git add -A && git commit -q -m "projeto que ja existia, sem processo nenhum"

titulo "1. Instalacao em modo reverso"
printf '$ install.sh . --reverso --adapters none\n'
"$KIT/install.sh" . --reverso --adapters none 2>&1 | grep -iE "reverso|concluida"
mostra grep -n "import_mode" docs/STATE.md

titulo "2. O agente reconstroi o que ja existe, e deixa em proposed"
python3 - <<'PY'
import sys
sys.dont_write_bytecode = True  # nao sujar o alvo com __pycache__
sys.path.insert(0, "bin/lifecycle")
import _kitlib as kit
s = kit.read_state(".")
s.update({"project": "cobranca", "tier": 1, "current_area": "nucleo",
          "open_questions": [{"id": "Q1",
                              "question": "Boleto ficou de fora por decisao ou por falta de tempo?",
                              "raised_at": "2026-08-28", "answered": None}]})
kit.write_state(".", s)
PY
mostra python3 $L/new-artifact 01-contexto nucleo "Contexto reconstruido" --owner "Jonathan Camargo"
python3 - <<'PY'
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, "bin/lifecycle")
import _kitlib as kit
from pathlib import Path
art = Path("docs/areas/nucleo/01-contexto/contexto-reconstruido.md")
art.write_text(art.read_text(encoding="utf-8")
               .replace("status: draft", "status: proposed")
               .replace("reconstructed_from: []",
                        "reconstructed_from:\n  - src/cobranca.py\n  - README.md"),
               encoding="utf-8")
s = kit.read_state(".")
s["gates"]["01-contexto"]["status"] = "proposed"
kit.write_state(".", s)
PY
printf '$ frontmatter do artefato reconstruido\n'
sed -n '1,12p' docs/areas/nucleo/01-contexto/contexto-reconstruido.md

titulo "3. plan abre pela duvida, nao pelos documentos"
mostra python3 $L/plan

titulo "4. Confirmacao recusada: pergunta em aberto"
mostra python3 $L/confirm-import --by "Jonathan Camargo"

titulo "5. Humano responde a pergunta na sessao de confirmacao"
python3 - <<'PY'
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, "bin/lifecycle")
import _kitlib as kit
s = kit.read_state(".")
s["open_questions"][0]["answered"] = "Decisao: boleto fora do escopo. Jonathan, 2026-08-28."
kit.write_state(".", s)
PY
printf 'Q1 respondida.\n'

titulo "6. Agente tentando confirmar: recusado"
mostra python3 $L/confirm-import --by "Claude Code"

titulo "7. Humano confirmando em bloco"
mostra python3 $L/confirm-import --by "Jonathan Camargo"

titulo "8. Procedencia gravada, e o marcador caiu sozinho"
printf '$ gates e import_mode em docs/STATE.md\n'
sed -n '/^gates:/,/^last_session/p' docs/STATE.md
grep -n "import_mode" docs/STATE.md

titulo "9. Reconstrucao sem ponteiro seria recusada pelo gate-check"
python3 - <<'PY'
import sys
from pathlib import Path
art = Path("docs/areas/nucleo/01-contexto/contexto-reconstruido.md")
linhas = [l for l in art.read_text(encoding="utf-8").splitlines()
          if not l.startswith("reconstructed_from:")
          and not l.startswith("  - src/cobranca.py")
          and not l.startswith("  - README.md")]
art.write_text("\n".join(linhas) + "\n", encoding="utf-8")
PY
mostra python3 $L/gate-check

titulo "10. Com o ponteiro de volta, limpo"
python3 - <<'PY'
from pathlib import Path
art = Path("docs/areas/nucleo/01-contexto/contexto-reconstruido.md")
t = art.read_text(encoding="utf-8").replace(
    "superseded_by: null",
    "superseded_by: null\nreconstructed_from:\n  - src/cobranca.py\n  - README.md")
art.write_text(t, encoding="utf-8")
PY
mostra python3 $L/gate-check
