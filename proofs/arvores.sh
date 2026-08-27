#!/bin/sh
# Gera as tres arvores da secao "Estrutura" do README.
#
# Uso: proofs/arvores.sh <alvo-adapters-all> <alvo-modo-a> [saida]
#
# As tres tem formatos diferentes de proposito, e o build-readme.py conta com
# isso: a do kit e uma arvore indentada de git ls-files, a do alvo recem
# instalado e uma lista plana sem ./ na frente, e a do modo A e a saida crua
# de find, com a linha de comando ecoada em cima.
set -eu
KIT="${KIT:-/home/user/product-lifecycle-kit}"
ALVO_ALL="${1:?uso: arvores.sh <alvo-adapters-all> <alvo-modo-a> [saida]}"
ALVO_A="${2:?uso: arvores.sh <alvo-adapters-all> <alvo-modo-a> [saida]}"
SAIDA="${3:-$KIT/proofs/out}"
mkdir -p "$SAIDA"

{ printf '$ git ls-files\n'
  git -C "$KIT" ls-files | python3 -c '
import sys
visto = set()
for linha in sys.stdin.read().splitlines():
    partes = linha.split("/")
    for i, parte in enumerate(partes):
        prefixo = "/".join(partes[:i + 1])
        if prefixo in visto:
            continue
        visto.add(prefixo)
        barra = "/" if i < len(partes) - 1 else ""
        print("%s%s%s" % ("  " * i, parte, barra))
'; } > "$SAIDA/arvore-kit.out"

( cd "$ALVO_ALL" && find . -path ./.git -prune -o -print ) \
    | sed -e 's|^\./||' -e '/^\.$/d' | sort > "$SAIDA/arvore-all.txt"

{ printf '$ find . | sort\n'
  ( cd "$ALVO_A" && find . -path ./.git -prune -o -print | sort ); } \
    > "$SAIDA/arvore-alvo.out"

printf 'arvores geradas em %s\n' "$SAIDA"
