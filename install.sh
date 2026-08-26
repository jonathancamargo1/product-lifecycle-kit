#!/usr/bin/env bash
# product-lifecycle-kit: instala ou atualiza o kit num repositorio alvo.
#
# Uso:
#   install.sh <caminho-do-repo-alvo> [--adapters claude-code,codex|all|none]
#              [--update]
set -u

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ALVO=""
ADAPTERS="all"
UPDATE=0
PULADOS=()
REAPROVEITADOS=()
REVISAR=()

erro() { printf 'install.sh: %s\n' "$1" >&2; exit 1; }
info() { printf '%s\n' "$1"; }

while [ $# -gt 0 ]; do
    case "$1" in
        --adapters) ADAPTERS="${2:-}"; shift 2 ;;
        --adapters=*) ADAPTERS="${1#*=}"; shift ;;
        --update) UPDATE=1; shift ;;
        -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
        -*) erro "opcao desconhecida: $1" ;;
        *) ALVO="$1"; shift ;;
    esac
done

[ -n "$ALVO" ] || erro "informe o caminho do repositorio alvo."
[ -d "$ALVO" ] || erro "diretorio nao existe: $ALVO"
ALVO="$(cd "$ALVO" && pwd)"
[ -d "$ALVO/.git" ] || erro "$ALVO nao e um repositorio git. Rode git init antes."
[ "$ALVO" != "$KIT_DIR" ] || erro "o alvo nao pode ser o proprio kit."

VERSAO="$(cat "$KIT_DIR/VERSION")"
MANIFESTO="$ALVO/docs/.kit-manifest"

# ---------------------------------------------------------------- utilitarios

soma() { python3 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }

manifesto_registrado() {
    # $1 = path relativo. Imprime a soma gravada na instalacao anterior.
    [ -f "$MANIFESTO" ] || return 1
    python3 - "$MANIFESTO" "$1" <<'PY'
import sys
alvo = sys.argv[2]
for linha in open(sys.argv[1], encoding="utf-8"):
    partes = linha.split(None, 1)
    if len(partes) == 2 and partes[1].strip() == alvo:
        print(partes[0])
        break
PY
}

customizado() {
    # 0 se o arquivo do alvo foi editado depois da instalacao anterior.
    local rel="$1" destino="$ALVO/$1"
    [ -f "$destino" ] || return 1
    local gravada; gravada="$(manifesto_registrado "$rel" || true)"
    [ -n "$gravada" ] || return 0
    [ "$gravada" != "$(soma "$destino")" ]
}

copia() {
    # copia $1 (absoluto no kit) para $2 (relativo no alvo).
    local origem="$1" rel="$2" destino="$ALVO/$2"
    mkdir -p "$(dirname "$destino")"
    if [ -e "$destino" ] && [ "$UPDATE" -eq 0 ]; then
        PULADOS+=("$rel")
        return 0
    fi
    cp "$origem" "$destino"
    printf '%s  %s\n' "$(soma "$destino")" "$rel" >> "$MANIFESTO.novo"
}

copia_atualizavel() {
    # no --update, respeita customizacao do projeto.
    local origem="$1" rel="$2" destino="$ALVO/$2"
    if [ "$UPDATE" -eq 1 ] && customizado "$rel"; then
        REVISAR+=("$rel")
        [ -f "$destino" ] && printf '%s  %s\n' "$(soma "$destino")" "$rel" >> "$MANIFESTO.novo"
        return 0
    fi
    mkdir -p "$(dirname "$destino")"
    if [ -e "$destino" ] && [ "$UPDATE" -eq 0 ]; then
        PULADOS+=("$rel")
        [ -f "$destino" ] && printf '%s  %s\n' "$(soma "$destino")" "$rel" >> "$MANIFESTO.novo"
        return 0
    fi
    cp "$origem" "$destino"
    printf '%s  %s\n' "$(soma "$destino")" "$rel" >> "$MANIFESTO.novo"
}

instala_hook() {
    local nome="$1" origem="$KIT_DIR/git-hooks/$1" destino="$ALVO/.git/hooks/$1"
    mkdir -p "$ALVO/.git/hooks"
    if [ -f "$destino" ] && ! grep -q "product-lifecycle-kit" "$destino" 2>/dev/null; then
        mv "$destino" "$destino.local"
        chmod +x "$destino.local"
        info "  hook $nome existente preservado em $nome.local e encadeado"
    fi
    cp "$origem" "$destino"
    chmod +x "$destino"
}

# --------------------------------------------------------------------- inicio

mkdir -p "$ALVO/docs"
: > "$MANIFESTO.novo"

if [ "$UPDATE" -eq 1 ]; then
    info "Atualizando o kit em $ALVO para a versao $VERSAO."
    [ -f "$ALVO/docs/KIT_VERSION" ] && info "Versao anterior: $(cat "$ALVO/docs/KIT_VERSION")"
else
    info "Instalando o product-lifecycle-kit $VERSAO em $ALVO."
fi

# 1. processo (sempre substituido no update, exceto templates customizados)
while IFS= read -r origem; do
    rel="docs/_process/${origem#"$KIT_DIR/docs/_process/"}"
    copia_atualizavel "$origem" "$rel"
done < <(find "$KIT_DIR/docs/_process" -type f -name '*.md' | sort)

# 2. contexto, estado e AGENTS.md: nunca tocados no update
if [ "$UPDATE" -eq 0 ]; then
    while IFS= read -r origem; do
        rel="docs/_context/${origem#"$KIT_DIR/docs/_context/"}"
        case "$rel" in */.gitkeep) continue ;; esac
        copia "$origem" "$rel"
    done < <(find "$KIT_DIR/docs/_context" -type f | sort)
    copia "$KIT_DIR/docs/STATE.md" "docs/STATE.md"
    copia "$KIT_DIR/docs/AGENTS.md" "AGENTS.md"
    mkdir -p "$ALVO/docs/_handoffs" "$ALVO/docs/areas"
else
    for rel in docs/STATE.md AGENTS.md; do
        [ -f "$ALVO/$rel" ] && printf '%s  %s\n' "$(soma "$ALVO/$rel")" "$rel" >> "$MANIFESTO.novo"
    done
fi

# 3. scripts, sem os testes do kit
for script in gate-check new-artifact session-open session-close guard-write \
              guard-commit decide _kitlib.py; do
    rel="bin/lifecycle/$script"
    if [ "$UPDATE" -eq 1 ]; then
        mkdir -p "$ALVO/bin/lifecycle"
        cp "$KIT_DIR/bin/$script" "$ALVO/$rel"
        printf '%s  %s\n' "$(soma "$ALVO/$rel")" "$rel" >> "$MANIFESTO.novo"
    else
        copia "$KIT_DIR/bin/$script" "$rel"
    fi
    [ "$script" = "_kitlib.py" ] || chmod +x "$ALVO/$rel" 2>/dev/null || true
done

# 4. git hooks: sempre reinstalados, sempre encadeando
instala_hook pre-commit
instala_hook commit-msg

# 5. adaptadores
instala_adaptador_claude() {
    copia_atualizavel "$KIT_DIR/adapters/claude-code/CLAUDE.md" "CLAUDE.md"
    while IFS= read -r origem; do
        rel=".claude/${origem#"$KIT_DIR/adapters/claude-code/.claude/"}"
        if [ "$rel" = ".claude/settings.json" ] && [ -f "$ALVO/$rel" ]; then
            python3 "$KIT_DIR/adapters/claude-code/merge-settings.py" "$origem" "$ALVO/$rel" \
                && info "  .claude/settings.json existente teve os hooks mesclados"
            printf '%s  %s\n' "$(soma "$ALVO/$rel")" "$rel" >> "$MANIFESTO.novo"
            continue
        fi
        copia_atualizavel "$origem" "$rel"
    done < <(find "$KIT_DIR/adapters/claude-code/.claude" -type f | sort)
    chmod +x "$ALVO/.claude/hooks/"*.sh 2>/dev/null || true
}

instala_adaptador_codex() {
    copia_atualizavel "$KIT_DIR/adapters/codex/README.md" "docs/codex-adapter.md"
}

case "$ADAPTERS" in
    all) ESCOLHIDOS="claude-code codex" ;;
    none|"") ESCOLHIDOS="" ;;
    *) ESCOLHIDOS="$(printf '%s' "$ADAPTERS" | tr ',' ' ')" ;;
esac

for adaptador in $ESCOLHIDOS; do
    case "$adaptador" in
        claude-code)
            if [ "$UPDATE" -eq 1 ] && [ ! -f "$ALVO/CLAUDE.md" ]; then
                info "  adaptador claude-code nao estava instalado, pulando"
            else
                info "Adaptador claude-code."
                instala_adaptador_claude
            fi ;;
        codex)
            if [ "$UPDATE" -eq 1 ] && [ ! -f "$ALVO/docs/codex-adapter.md" ]; then
                info "  adaptador codex nao estava instalado, pulando"
            else
                info "Adaptador codex."
                instala_adaptador_codex
            fi ;;
        *) erro "adaptador desconhecido: $adaptador" ;;
    esac
done

# 6. kit anterior em docs/templates
if [ -d "$ALVO/docs/templates" ]; then
    info "Kit anterior encontrado em docs/templates."
    while IFS= read -r antigo; do
        nome="$(basename "$antigo")"
        if [ -f "$KIT_DIR/docs/_process/templates/$nome" ]; then
            REAPROVEITADOS+=("$nome")
            cp "$antigo" "$ALVO/docs/_process/templates/$nome"
        else
            REAPROVEITADOS+=("$nome (sem equivalente, movido)")
            cp "$antigo" "$ALVO/docs/_process/templates/$nome"
        fi
    done < <(find "$ALVO/docs/templates" -maxdepth 1 -type f -name '*.md' | sort)
    info "  templates reaproveitados no lugar dos novos, um conjunto so:"
    for item in "${REAPROVEITADOS[@]:-}"; do [ -n "$item" ] && info "    $item"; done
    info "  ATENCAO: os templates reaproveitados sao os seus, nao os do kit."
    info "  Eles nao foram validados contra a estrutura nova (Gate de saida,"
    info "  Anti-padroes, Modo reverso). Confira um a um antes de usar."
    info "  docs/templates preservado. Remova quando conferir a migracao."
fi

# 7. versao
printf '%s\n' "$VERSAO" > "$ALVO/docs/KIT_VERSION"
printf '%s  %s\n' "$(soma "$ALVO/docs/KIT_VERSION")" "docs/KIT_VERSION" >> "$MANIFESTO.novo"
mv "$MANIFESTO.novo" "$MANIFESTO"

# 8. relatorio
if [ "${#PULADOS[@]}" -gt 0 ]; then
    info ""
    info "Arquivos que ja existiam e foram preservados:"
    for item in "${PULADOS[@]}"; do info "  $item"; done
fi
if [ "${#REVISAR[@]}" -gt 0 ]; then
    info ""
    info "Customizados pelo projeto, nao substituidos. Revise a mao:"
    for item in "${REVISAR[@]}"; do info "  $item"; done
fi
if [ "$UPDATE" -eq 1 ] && [ -f "$KIT_DIR/CHANGELOG.md" ]; then
    info ""
    info "Mudancas desta versao (CHANGELOG.md):"
    awk '/^## /{n++} n==1' "$KIT_DIR/CHANGELOG.md" | sed 's/^/  /'
fi

info ""
info "docs/KIT_VERSION: $VERSAO"
info "Rodando gate-check no alvo."
info ""
( cd "$ALVO" && python3 bin/lifecycle/gate-check )
CODIGO=$?
info ""
if [ $CODIGO -eq 0 ]; then
    info "Instalacao concluida. gate-check saiu com 0."
else
    info "Instalacao concluida, mas gate-check saiu com $CODIGO. Veja acima."
fi
exit $CODIGO
