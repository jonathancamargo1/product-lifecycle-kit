#!/usr/bin/env bash
# Varredura de caracteres proibidos e limites de tamanho.
#
# Nota: este script nunca escreve o travessao longo literalmente. Ele monta o
# caractere a partir do codepoint U+2014. Se o escrevesse, o proprio arquivo
# passaria a ser uma ocorrencia, e a varredura acusaria a si mesma.
KIT="${KIT:-/home/user/product-lifecycle-kit}"
cd "$KIT" || exit 1

TRAVESSAO=$(python3 -c 'print(chr(0x2014), end="")')

# proofs/out guarda as saidas desta propria varredura: incluir seria o grep
# lendo o que ele mesmo acabou de escrever.
printf '$ grep -rn --exclude-dir=.git --exclude-dir=out -e "<U+2014>" .\n'
grep -rn --exclude-dir=.git --exclude-dir=out --exclude-dir=__pycache__ \
    -e "$TRAVESSAO" .
printf 'EXIT: %d\n' "$?"

printf '\n$ python3 varredura de codepoints em todos os arquivos versionados\n'
python3 - <<'PY'
import subprocess
from pathlib import Path
raiz = Path(__file__).resolve().parent if "__file__" in dir() else Path.cwd()
raiz = Path.cwd()
TRAVESSAO = chr(0x2014)
arquivos = subprocess.run(["git", "ls-files"], cwd=raiz, capture_output=True,
                          text=True).stdout.split()
suspeitos = []
verificados = 0
for nome in arquivos:
    try:
        texto = (raiz / nome).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    verificados += 1
    for numero, linha in enumerate(texto.splitlines(), start=1):
        for char in linha:
            ponto = ord(char)
            if char == TRAVESSAO:
                suspeitos.append((nome, numero, "travessao U+2014"))
            elif (0x1F000 <= ponto <= 0x1FAFF or 0x2600 <= ponto <= 0x27BF
                  or ponto in (0xFE0F, 0x2764, 0x2B50) or 0x1F1E6 <= ponto <= 0x1F1FF):
                suspeitos.append((nome, numero, "emoji U+%04X" % ponto))
print("arquivos versionados verificados: %d" % verificados)
print("ocorrencias de travessao U+2014 ou emoji: %d" % len(suspeitos))
for item in suspeitos[:20]:
    print("  %s:%d %s" % item)
PY
printf 'EXIT: %d\n' "$?"

printf '\n$ limites de tamanho\n'
python3 - <<'PY'
from pathlib import Path
raiz = Path.cwd()
templates = sorted((raiz / "docs/_process/templates").glob("*.md"))
maior = max(len(t.read_text(encoding="utf-8").splitlines()) for t in templates)
print("templates: %d arquivos, maior tem %d linhas, limite 80"
      % (len(templates), maior))
print("docs/AGENTS.md: %d linhas, limite 60"
      % len((raiz / "docs/AGENTS.md").read_text(encoding="utf-8").splitlines()))
print("adapters/claude-code/CLAUDE.md: %d linhas, exigido 2"
      % len((raiz / "adapters/claude-code/CLAUDE.md").read_text(encoding="utf-8").splitlines()))
PY

printf '\n$ pastas vazias fora dos .gitkeep\n'
VAZIAS=$(find . -type d -empty -not -path './.git/*' -not -path './*__pycache__*')
if [ -z "$VAZIAS" ]; then
    printf 'nenhuma\n'
else
    printf '%s\n' "$VAZIAS"
fi
