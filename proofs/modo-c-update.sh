#!/usr/bin/env bash
# Prova do modo C: install.sh --update sobre o projeto prova-b ja instalado.
set -u
KIT=/home/user/product-lifecycle-kit
ALVO="$1"
NOVA="${2:-1.1.0}"

titulo() { printf '\n----- %s -----\n' "$1"; }
mostra() { printf '$ %s\n' "$*"; "$@" 2>&1; printf 'EXIT: %d\n' "$?"; }

impressao_digital() {
    # Soma de tudo que o --update tem proibido tocar.
    ( cd "$ALVO" && find docs/STATE.md docs/_handoffs docs/areas -type f \
        | sort | xargs sha256sum | sha256sum | cut -c1-64 )
}

titulo "1. Estado antes do update"
mostra cat "$ALVO/docs/KIT_VERSION"
ANTES="$(impressao_digital)"
printf 'impressao digital de STATE.md + _handoffs + areas: %s\n' "$ANTES"

titulo "2. Nova versao do kit"
printf '%s\n' "$NOVA" > "$KIT/VERSION"
python3 - "$KIT" "$NOVA" <<'PY'
import re, sys
from pathlib import Path
kit, nova = Path(sys.argv[1]), sys.argv[2]
lib = kit / "bin" / "_kitlib.py"
lib.write_text(re.sub(r'KIT_VERSION = "[^"]+"', 'KIT_VERSION = "%s"' % nova,
                      lib.read_text(encoding="utf-8"), count=1), encoding="utf-8")
changelog = kit / "CHANGELOG.md"
texto = changelog.read_text(encoding="utf-8")
entrada = """## %s

Versao usada para provar o fluxo `install.sh --update` (modo C do README).
Nenhuma mudanca de comportamento em relacao a 1.0.0: processo e scripts sao
reenviados ao alvo e `docs/KIT_VERSION` passa a 1.1.0, sem tocar em estado,
contexto, handoffs ou artefatos.

""" % nova
marcador = "## 1.0.0"
if ("## %s" % nova) not in texto:
    changelog.write_text(texto.replace(marcador, entrada + marcador, 1), encoding="utf-8")
print("VERSION agora e %s e o CHANGELOG.md ganhou a secao %s" % (nova, nova))
PY
mostra cat "$KIT/VERSION"

titulo "3. install.sh --update"
mostra "$KIT/install.sh" "$ALVO" --update

titulo "4. KIT_VERSION mudou"
mostra cat "$ALVO/docs/KIT_VERSION"

titulo "5. STATE.md, _handoffs e areas nao mudaram"
DEPOIS="$(impressao_digital)"
printf 'antes:  %s\n' "$ANTES"
printf 'depois: %s\n' "$DEPOIS"
if [ "$ANTES" = "$DEPOIS" ]; then
    printf 'IGUAIS. O update nao tocou em estado, handoffs nem artefatos.\n'
else
    printf 'DIFERENTES. O update tocou em algo que nao podia.\n'
    ( cd "$ALVO" && git status --short docs/STATE.md docs/_handoffs docs/areas )
fi

titulo "5a. git status do alvo depois do update"
mostra git -C "$ALVO" status --short

titulo "6. gate-check continua limpo depois do update"
mostra git -C "$ALVO" --no-pager log --oneline -1
( cd "$ALVO" && printf '$ python3 bin/lifecycle/gate-check\n' && python3 bin/lifecycle/gate-check 2>&1; printf 'EXIT: %d\n' "$?" )
