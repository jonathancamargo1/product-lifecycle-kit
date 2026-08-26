#!/usr/bin/env bash
# Criterio de aceite: install.sh --adapters none num repositorio vazio.
set -u
KIT=/home/user/product-lifecycle-kit
ALVO="$1"
mostra() { printf '$ %s\n' "$*"; "$@" 2>&1; printf 'EXIT: %d\n' "$?"; }

rm -rf "$ALVO"; mkdir -p "$ALVO"; cd "$ALVO" || exit 1
git init -q -b main .
git config user.name "Jonathan Camargo"
git config user.email "jonathan.camargo1@gmail.com"

mostra "$KIT/install.sh" . --adapters none

printf '\n----- os dois git hooks estao instalados e executaveis -----\n'
mostra ls -l .git/hooks/pre-commit .git/hooks/commit-msg

printf '\n----- nenhum arquivo de adaptador foi instalado -----\n'
mostra ls -a .

printf '\n----- gate-check no alvo -----\n'
mostra python3 bin/lifecycle/gate-check
