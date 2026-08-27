#!/usr/bin/env bash
# Prova do modo C: install.sh --update sobre um projeto ja instalado.
#
# A nova versao do kit e montada numa COPIA temporaria, nunca no kit real. Uma
# prova que suja o repositorio que ela mesma testa nao e reproduzivel: os
# outros modos passariam a rodar numa versao diferente da que esta colada no
# README.
set -u
KIT="${KIT:-/home/user/product-lifecycle-kit}"
ALVO="$1"
NOVA="${2:-1.1.0}"

titulo() { printf '\n----- %s -----\n' "$1"; }
mostra() { printf '$ %s\n' "$*"; "$@" 2>&1; printf 'EXIT: %d\n' "$?"; }

impressao_digital() {
    ( cd "$ALVO" && find docs/STATE.md docs/_handoffs docs/areas -type f \
        | sort | xargs sha256sum | sha256sum | cut -c1-64 )
}

titulo "1. Estado antes do update"
mostra cat "$ALVO/docs/KIT_VERSION"
ANTES="$(impressao_digital)"
printf 'impressao digital de STATE.md + _handoffs + areas: %s\n' "$ANTES"

titulo "2. Nova versao do kit, montada numa copia temporaria"
COPIA="$(mktemp -d)"
trap 'rm -rf "$COPIA"' EXIT
tar -C "$KIT" --exclude=.git --exclude=__pycache__ -cf - . | tar -C "$COPIA" -xf -
printf '%s\n' "$NOVA" > "$COPIA/VERSION"
python3 - "$COPIA" "$NOVA" <<'PY'
import re, sys
from pathlib import Path
copia, nova = Path(sys.argv[1]), sys.argv[2]
lib = copia / "bin" / "_kitlib.py"
lib.write_text(re.sub(r'KIT_VERSION = "[^"]+"', 'KIT_VERSION = "%s"' % nova,
                      lib.read_text(encoding="utf-8"), count=1), encoding="utf-8")
changelog = copia / "CHANGELOG.md"
texto = changelog.read_text(encoding="utf-8")
entrada = """## %s

Versao usada para provar o fluxo `install.sh --update` (modo C do README).
Nenhuma mudanca de comportamento em relacao a versao anterior: processo e
scripts sao reenviados ao alvo e `docs/KIT_VERSION` sobe, sem tocar em estado,
contexto, handoffs ou artefatos.

""" % nova
# A entrada precisa entrar em cima de tudo: o install.sh mostra a primeira
# secao "## " do CHANGELOG, entao um marcador de versao fixo colocaria a
# entrada nova embaixo da anterior e a prova mostraria o changelog errado.
corte = texto.find("\n## ")
if ("## %s" % nova) not in texto and corte != -1:
    changelog.write_text(texto[:corte + 1] + entrada + texto[corte + 1:],
                         encoding="utf-8")
print("copia do kit montada na versao %s. O kit real segue intocado." % nova)
PY
printf '$ cat <copia>/VERSION\n'; cat "$COPIA/VERSION"
printf '$ cat %s/VERSION   (o kit real)\n' "$KIT"; cat "$KIT/VERSION"

titulo "3. install.sh --update, rodado a partir da copia"
printf '$ <copia>/install.sh %s --update\n' "$ALVO"
"$COPIA/install.sh" "$ALVO" --update 2>&1
printf 'EXIT: %d\n' "$?"

titulo "4. KIT_VERSION do alvo mudou"
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

titulo "6. O kit real continua na versao de antes"
mostra git -C "$KIT" status --short VERSION CHANGELOG.md bin/_kitlib.py

titulo "7. gate-check continua limpo depois do update"
( cd "$ALVO" && printf '$ python3 bin/lifecycle/gate-check\n' && python3 bin/lifecycle/gate-check 2>&1; printf 'EXIT: %d\n' "$?" )
