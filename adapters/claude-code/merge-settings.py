#!/usr/bin/env python3
"""Mescla os hooks do kit num .claude/settings.json existente.

Uso: _merge_settings.py <settings-do-kit> <settings-do-alvo>

Nunca remove hook do projeto. Nunca duplica hook do kit: um comando ja
presente no mesmo evento e deixado como esta.
"""
import json
import sys
from pathlib import Path


def comandos(entrada):
    return {h.get("command") for h in entrada.get("hooks", []) if isinstance(h, dict)}


def main():
    origem = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    destino_path = Path(sys.argv[2])
    try:
        destino = json.loads(destino_path.read_text(encoding="utf-8"))
    except OSError as erro:
        sys.stderr.write("merge-settings: nao consegui ler %s: %s\n"
                         % (destino_path, erro))
        return 1
    except ValueError as erro:
        # Sobrescrever aqui apagaria permissions, model e tudo mais que o
        # projeto tenha. Melhor parar e deixar a pessoa consertar o JSON.
        sys.stderr.write(
            "merge-settings: %s existe mas nao e JSON valido (%s).\n"
            "Nada foi alterado. Conserte o arquivo e rode install.sh de novo, "
            "ou adicione os hooks do kit a mao.\n" % (destino_path, erro))
        return 1
    if not isinstance(destino, dict):
        sys.stderr.write("merge-settings: %s nao contem um objeto JSON. "
                         "Nada foi alterado.\n" % destino_path)
        return 1

    alvo_hooks = destino.setdefault("hooks", {})
    for evento, entradas in origem.get("hooks", {}).items():
        existentes = alvo_hooks.setdefault(evento, [])
        ja_presentes = set()
        for entrada in existentes:
            if isinstance(entrada, dict):
                ja_presentes |= comandos(entrada)
        for entrada in entradas:
            if comandos(entrada) & ja_presentes:
                continue
            existentes.append(entrada)

    destino_path.write_text(json.dumps(destino, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
