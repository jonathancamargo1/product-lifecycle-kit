"""Biblioteca compartilhada pelos scripts do product-lifecycle-kit.

Apenas biblioteca padrao do Python 3. Nenhuma dependencia externa, porque o
kit precisa rodar em qualquer repositorio, com qualquer runtime, sem instalar
nada.
"""
import datetime
import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

KIT_VERSION = "1.1.0"

PHASES = [
    "01-contexto", "02-discovery", "03-csd", "04-personas-jornada", "05-prd",
    "06-adr", "07-flows-ia", "08-wireframes", "09-usability", "10-ui",
    "11-spec", "12-backlog-handoff", "13-build-log", "14-review",
    "15-threat-review", "16-verify", "17-ship", "18-runbook", "19-medir",
    "20-retro",
]

TIER_PHASES = {
    1: ["01-contexto", "13-build-log", "14-review", "17-ship"],
    2: ["01-contexto", "02-discovery", "05-prd", "07-flows-ia", "08-wireframes",
        "11-spec", "12-backlog-handoff", "13-build-log", "14-review",
        "15-threat-review", "16-verify", "17-ship"],
    3: list(PHASES),
}

PHASES_SEM_INPUTS = ("01-contexto", "02-discovery")

ARTIFACT_STATUSES = ("draft", "review", "proposed", "approved", "superseded")
GATE_STATUSES = ("in_progress", "proposed", "approved", "superseded")
AGENT_TOKENS = ("agent", "codex", "claude", "ai", "bot")

REQUIRED_FRONTMATTER = ("phase", "area", "title", "status", "owner", "inputs",
                        "approved_by", "approved_at", "superseded_by")

STATE_KEYS = ["project", "tier", "current_phase", "current_area", "next_action",
              "blocked_by", "open_questions", "gates", "last_session",
              "session_counter", "session_open", "session_agent"]

STATE_COMMENTS = {
    "tier": "1 | 2 | 3",
    "next_action": "uma frase imperativa",
    "blocked_by": "slug de gate, id de decisao ou null",
    "open_questions": "{id, question, raised_at, answered}",
    "gates": "slug da fase: {status, evidence, by, date}",
    "last_session": "path do ultimo handoff",
    "session_open": "true entre session-open e session-close",
    "session_agent": "codex | claude-code | human",
}

DEFAULT_PROTECTED_GLOBS = ["docs/_context/CONTEXT.md", "docs/_process/**",
                           "AGENTS.md", "docs/AGENTS.md"]

SESSION_AGENTS = ("codex", "claude-code", "human")


# ---------------------------------------------------------------- YAML subset

def _strip_comment(text):
    out = []
    quote = None
    for i, char in enumerate(text):
        if quote:
            out.append(char)
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
            out.append(char)
        elif char == "#" and (i == 0 or text[i - 1] in " \t"):
            break
        else:
            out.append(char)
    return "".join(out).rstrip()


def _scalar_value(text):
    text = text.strip()
    if text in ("", "null", "~"):
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if text == "[]":
        return []
    if text == "{}":
        return {}
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_scalar_value(part) for part in inner.split(",")]
    try:
        return int(text)
    except ValueError:
        return text


def _looks_like_mapping(text):
    if ":" not in text:
        return False
    key = text.split(":", 1)[0]
    return bool(key) and " " not in key.strip()


def _items(text):
    result = []
    for raw in text.splitlines():
        content = _strip_comment(raw)
        if not content.strip():
            continue
        result.append((len(content) - len(content.lstrip()), content.strip()))
    return result


def _parse_nodes(items, idx, indent):
    if idx >= len(items):
        return None, idx
    if items[idx][1].startswith("- ") or items[idx][1] == "-":
        seq = []
        while idx < len(items):
            ind, content = items[idx]
            if ind != indent or not (content.startswith("- ") or content == "-"):
                break
            rest = content[1:].strip()
            if _looks_like_mapping(rest):
                sub = [(indent + 2, rest)]
                idx += 1
                while idx < len(items) and items[idx][0] > indent:
                    sub.append(items[idx])
                    idx += 1
                value, _ = _parse_nodes(sub, 0, indent + 2)
                seq.append(value)
            else:
                seq.append(_scalar_value(rest))
                idx += 1
        return seq, idx
    mapping = {}
    while idx < len(items):
        ind, content = items[idx]
        if ind != indent or ":" not in content:
            break
        key, _, rest = content.partition(":")
        key = key.strip()
        rest = rest.strip()
        idx += 1
        if rest == "":
            if idx < len(items) and items[idx][0] > indent:
                child_indent = items[idx][0]
                value, idx = _parse_nodes(items, idx, child_indent)
            else:
                value = None
            mapping[key] = value
        else:
            mapping[key] = _scalar_value(rest)
    return mapping, idx


def parse_yaml(text):
    """Parser do subconjunto de YAML que o kit usa. Erros viram ValueError."""
    items = _items(text)
    if not items:
        return {}
    value, _ = _parse_nodes(items, 0, items[0][0])
    if not isinstance(value, dict):
        raise ValueError("esperava um mapeamento no topo")
    return value


def emit_scalar(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if text == "" or text != text.strip():
        return '"%s"' % text
    if text in ("null", "true", "false") or ": " in text or text.startswith("#"):
        return '"%s"' % text
    return text


# ------------------------------------------------------------------- caminhos

def repo_root(start=None):
    current = Path(start or os.getcwd()).resolve()
    for candidate in [current] + list(current.parents):
        if (candidate / "docs" / "STATE.md").exists():
            return candidate
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=str(current),
                         capture_output=True, text=True)
    if top.returncode == 0 and top.stdout.strip():
        return Path(top.stdout.strip())
    return current


def relative(root, path):
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = (Path(os.getcwd()) / candidate)
    try:
        return candidate.resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


# --------------------------------------------------------------- frontmatter

def read_frontmatter(path):
    """Retorna (campos, primeira_linha_do_bloco) ou (None, motivo)."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as erro:
        return None, "arquivo ilegivel: %s" % erro
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "frontmatter ausente: o arquivo nao comeca com ---"
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            bloco = "\n".join(lines[1:index])
            try:
                fields = parse_yaml(bloco)
            except ValueError as erro:
                return None, "frontmatter nao parseavel: %s" % erro
            return fields, 2
    return None, "frontmatter nao fechado: falta o --- final"


def frontmatter_line(path, key):
    """Numero da linha de um campo do frontmatter, para o relatorio."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return 1
    for number, line in enumerate(lines[:60], start=1):
        if line.strip() == "---" and number > 1:
            break
        if line.startswith(key + ":"):
            return number
    return 1


# --------------------------------------------------------------------- STATE

def state_path(root):
    return Path(root) / "docs" / "STATE.md"


def _fence_bounds(lines):
    inicio = None
    for index, line in enumerate(lines):
        if line.strip().startswith("```") and inicio is None:
            inicio = index
            continue
        if inicio is not None and line.strip() == "```":
            return inicio, index
    return None, None


def read_state(root):
    path = state_path(root)
    if not path.exists():
        raise ValueError("docs/STATE.md nao existe")
    lines = path.read_text(encoding="utf-8").splitlines()
    inicio, fim = _fence_bounds(lines)
    if inicio is None:
        raise ValueError("docs/STATE.md nao tem bloco de codigo com o YAML")
    try:
        state = parse_yaml("\n".join(lines[inicio + 1:fim]))
    except ValueError as erro:
        raise ValueError("YAML de docs/STATE.md nao parseavel: %s" % erro)
    if state.get("open_questions") is None:
        state["open_questions"] = []
    if state.get("gates") is None:
        state["gates"] = {}
    return state


def dump_state_body(state):
    linhas = []
    for key in STATE_KEYS:
        value = state.get(key)
        comentario = STATE_COMMENTS.get(key)
        if key == "open_questions":
            if not value:
                linhas.append(_com("open_questions: []", comentario))
                continue
            linhas.append(_com("open_questions:", comentario))
            for item in value:
                linhas.append("  - id: %s" % emit_scalar(item.get("id")))
                for sub in ("question", "raised_at", "answered"):
                    linhas.append("    %s: %s" % (sub, emit_scalar(item.get(sub))))
        elif key == "gates":
            if not value:
                linhas.append(_com("gates: {}", comentario))
                continue
            linhas.append(_com("gates:", comentario))
            for slug in sorted(value):
                gate = value[slug] or {}
                linhas.append("  %s:" % slug)
                for sub in ("status", "evidence", "by", "date"):
                    linhas.append("    %s: %s" % (sub, emit_scalar(gate.get(sub))))
        else:
            linhas.append(_com("%s: %s" % (key, emit_scalar(value)), comentario))
    return "\n".join(linhas)


def _com(texto, comentario):
    if not comentario:
        return texto
    return "%-29s # %s" % (texto, comentario)


def write_state(root, state):
    path = state_path(root)
    lines = path.read_text(encoding="utf-8").splitlines()
    inicio, fim = _fence_bounds(lines)
    if inicio is None:
        raise ValueError("docs/STATE.md nao tem bloco de codigo com o YAML")
    novo = lines[:inicio + 1] + dump_state_body(state).splitlines() + lines[fim:]
    path.write_text("\n".join(novo) + "\n", encoding="utf-8")


# --------------------------------------------------------------------- fases

def resolve_phase(prefix):
    if prefix in PHASES:
        return prefix
    matches = [slug for slug in PHASES if slug.startswith(prefix)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ValueError("fase desconhecida: %s" % prefix)
    raise ValueError("prefixo ambiguo %r, resolve para: %s"
                     % (prefix, ", ".join(matches)))


def required_phases(tier):
    try:
        return TIER_PHASES[int(tier)]
    except (KeyError, TypeError, ValueError):
        return None


def phase_number(slug):
    return int(slug.split("-", 1)[0])


# ---------------------------------------------------------- paths protegidos

def protected_globs(root):
    path = Path(root) / "docs" / "_process" / "protected-paths.md"
    if not path.exists():
        return list(DEFAULT_PROTECTED_GLOBS)
    linhas = path.read_text(encoding="utf-8").splitlines()
    dentro = False
    padroes = []
    for linha in linhas:
        if linha.strip().startswith("```"):
            if not dentro and "protected-globs" in linha:
                dentro = True
                continue
            if dentro:
                break
            continue
        if dentro:
            texto = linha.strip()
            if texto and not texto.startswith("#"):
                padroes.append(texto)
    return padroes or list(DEFAULT_PROTECTED_GLOBS)


def glob_matches(pattern, rel_path):
    if pattern.endswith("/**"):
        base = pattern[:-3]
        return rel_path == base or rel_path.startswith(base + "/")
    return fnmatch.fnmatch(rel_path, pattern)


def protection_reason(root, rel_path, content_reader=None):
    """Por que o path e protegido, ou None se nao for.

    content_reader devolve o texto ja registrado do arquivo (disco para
    guard-write, HEAD para guard-commit) ou None se ele nao existe ainda.
    """
    if content_reader is None:
        content_reader = lambda rel: _read_disk(root, rel)
    texto = content_reader(rel_path)
    if texto is None:
        # Nada registrado ainda. Criar arquivo novo nunca destroi decisao.
        return None
    for pattern in protected_globs(root):
        if glob_matches(pattern, rel_path):
            return "padrao protegido %s" % pattern
    fields = _frontmatter_from_text(texto)
    if fields is None:
        return None
    status = fields.get("status")
    if rel_path.startswith("docs/_context/adr/") and status == "accepted":
        return "ADR aceita"
    if rel_path.startswith("docs/areas/") and status == "approved":
        return "artefato aprovado"
    return None


def blocking_reason(root, rel_path, content_reader=None):
    """Motivo para recusar a escrita, ou None se liberado.

    Junta as duas metades da regra: o path e protegido, e nenhuma decisao
    DECIDED o liberou em data igual ou posterior a ultima modificacao.
    """
    motivo = protection_reason(root, rel_path, content_reader=content_reader)
    if motivo is None:
        return None
    if decision_releases(root, rel_path, last_modified(root, rel_path)):
        return None
    return motivo


def _read_disk(root, rel_path):
    path = Path(root) / rel_path
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _frontmatter_from_text(texto):
    lines = texto.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            try:
                return parse_yaml("\n".join(lines[1:index]))
            except ValueError:
                return None
    return None


# ------------------------------------------------------- painel de area

PANEL_HEADER = "| Gate | Entregavel | Status | Evidencia | Aprovado por | Data |"


def area_of(rel_path):
    partes = rel_path.split("/")
    if len(partes) > 2 and partes[0] == "docs" and partes[1] == "areas":
        return partes[2]
    return None


def refresh_area_panels(root, state):
    """Regera o painel de gates de cada area a partir de STATE.md.

    O painel e vista derivada, nunca fonte. Status continua vivendo em dois
    lugares apenas (principio 8): o frontmatter do artefato e STATE.md. Esta
    funcao existe para que a terceira copia nunca possa divergir: ela e
    reescrita inteira a cada new-artifact e a cada session-close.
    """
    gates = state.get("gates") or {}
    obrigatorias = required_phases(state.get("tier"))
    por_area = {}
    for slug, gate in gates.items():
        gate = gate or {}
        if obrigatorias is not None and slug not in obrigatorias:
            continue
        area = area_of(str(gate.get("evidence") or ""))
        if area:
            por_area.setdefault(area, []).append((slug, gate))

    base = Path(root) / "docs" / "areas"
    if not base.exists():
        return
    for area in sorted(p.name for p in base.iterdir() if p.is_dir()):
        readme = base / area / "README.md"
        if not readme.exists():
            continue
        linhas = readme.read_text(encoding="utf-8").splitlines()
        inicio = None
        for index, linha in enumerate(linhas):
            if linha.replace(" ", "").startswith("|Gate|Entregavel|"):
                inicio = index
                break
        if inicio is None:
            continue
        fim = inicio + 1
        while fim < len(linhas) and linhas[fim].startswith("|"):
            fim += 1
        novas = [PANEL_HEADER, "|---|---|---|---|---|---|"]
        for slug, gate in sorted(por_area.get(area, [])):
            evidencia = str(gate.get("evidence") or "")
            fields, _ = read_frontmatter(Path(root) / evidencia)
            titulo = (fields or {}).get("title") or ""
            novas.append("| %s | %s | %s | %s | %s | %s |" % (
                slug, titulo, gate.get("status") or "",
                evidencia, gate.get("by") or "", gate.get("date") or ""))
        linhas[inicio:fim] = novas

        entradas = por_area.get(area, [])
        if obrigatorias is not None:
            faltam = [s for s in obrigatorias
                      if (gates.get(s) or {}).get("status") != "approved"]
            geral = "em andamento" if faltam else "concluida"
        else:
            geral = "em andamento"
        for index, linha in enumerate(linhas):
            if linha.replace(" ", "").startswith("|Statusgeral|"):
                linhas[index] = "| Status geral | %s |" % geral
                break
        readme.write_text("\n".join(linhas) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ decisoes

def decisions_path(root):
    return Path(root) / "docs" / "_context" / "decisions.log"


def parse_decisions(root):
    path = decisions_path(root)
    if not path.exists():
        return []
    entradas = []
    atual = None
    dentro_de_fence = False
    for numero, linha in enumerate(path.read_text(encoding="utf-8").splitlines(),
                                   start=1):
        if linha.strip().startswith("```"):
            dentro_de_fence = not dentro_de_fence
            continue
        if dentro_de_fence:
            continue
        if linha.startswith("## "):
            partes = [p.strip() for p in linha[3:].split("|")]
            if len(partes) >= 4:
                atual = {"id": partes[0], "date": partes[1], "status": partes[2],
                         "title": "|".join(partes[3:]), "line": numero,
                         "afeta": [], "fields": {}}
                entradas.append(atual)
            else:
                atual = None
            continue
        if atual is None or ":" not in linha:
            continue
        chave, _, valor = linha.partition(":")
        chave = chave.strip()
        valor = valor.strip()
        atual["fields"][chave] = valor
        if chave.lower() == "afeta":
            atual["afeta"] = [p.strip() for p in valor.split(",") if p.strip()]
    return entradas


def next_decision_id(root):
    maior = 0
    for entrada in parse_decisions(root):
        match = re.match(r"D-(\d+)", entrada["id"])
        if match:
            maior = max(maior, int(match.group(1)))
    return "D-%04d" % (maior + 1)


def decision_releases(root, rel_path, modificado_em):
    """True se alguma decisao DECIDED libera rel_path na data certa."""
    for entrada in parse_decisions(root):
        if entrada["status"].upper() != "DECIDED":
            continue
        if rel_path not in entrada["afeta"]:
            continue
        if not modificado_em or entrada["date"] >= modificado_em:
            return True
    return False


# ----------------------------------------------------------------------- git

def git(root, *args):
    return subprocess.run(["git"] + list(args), cwd=str(root),
                          capture_output=True, text=True)


def last_modified(root, rel_path):
    """Data da ultima modificacao registrada, YYYY-MM-DD."""
    resultado = git(root, "log", "-1", "--format=%cs", "--", rel_path)
    if resultado.returncode == 0 and resultado.stdout.strip():
        return resultado.stdout.strip()
    path = Path(root) / rel_path
    if path.exists():
        return datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()
    return None


def head_content(root, rel_path):
    resultado = git(root, "show", "HEAD:%s" % rel_path)
    if resultado.returncode != 0:
        return None
    return resultado.stdout


def staged_files(root):
    resultado = git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMRT")
    if resultado.returncode != 0:
        return []
    return [linha.strip() for linha in resultado.stdout.splitlines() if linha.strip()]


def today():
    return datetime.date.today().isoformat()


def die(mensagem, code=1):
    sys.stderr.write(mensagem.rstrip() + "\n")
    raise SystemExit(code)
