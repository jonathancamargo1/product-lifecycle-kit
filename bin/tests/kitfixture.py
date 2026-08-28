"""Fixtures compartilhadas pelos testes do kit.

O emissor de YAML aqui e independente do parser de bin/_kitlib.py de
proposito: se o parser quebrar, os testes precisam falhar, e nao concordar
com o proprio bug.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[2]
BIN = KIT_ROOT / "bin"

DEFAULT_STATE = {
    "project": "fixture",
    "tier": 1,
    "import_mode": None,
    "current_phase": None,
    "current_area": None,
    "next_action": None,
    "blocked_by": None,
    "open_questions": [],
    "gates": {},
    "last_session": None,
    "session_counter": 0,
    "session_open": False,
    "session_agent": None,
}

STATE_ORDER = list(DEFAULT_STATE.keys())


def _scalar(value):
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


def dump_state(state):
    lines = []
    for key in STATE_ORDER:
        value = state.get(key)
        if key == "open_questions":
            if not value:
                lines.append("open_questions: []")
                continue
            lines.append("open_questions:")
            for item in value:
                lines.append("  - id: %s" % _scalar(item.get("id")))
                for sub in ("question", "raised_at", "answered"):
                    lines.append("    %s: %s" % (sub, _scalar(item.get(sub))))
        elif key == "gates":
            if not value:
                lines.append("gates: {}")
                continue
            lines.append("gates:")
            for slug, gate in value.items():
                lines.append("  %s:" % slug)
                for sub in ("status", "evidence", "by", "date"):
                    lines.append("    %s: %s" % (sub, _scalar(gate.get(sub))))
                if gate.get("method"):
                    lines.append("    method: %s" % _scalar(gate["method"]))
        else:
            lines.append("%s: %s" % (key, _scalar(value)))
    return "# STATE\n\n```yaml\n" + "\n".join(lines) + "\n```\n"


def dump_frontmatter(fields):
    order = ["phase", "area", "title", "status", "owner", "inputs",
             "approved_by", "approved_at", "superseded_by"]
    lines = ["---"]
    for key in order:
        if key not in fields:
            continue
        value = fields[key]
        if key == "inputs":
            if not value:
                lines.append("inputs: []")
            else:
                lines.append("inputs:")
                for item in value:
                    lines.append("  - %s" % item)
        else:
            lines.append("%s: %s" % (key, _scalar(value)))
    for key, value in fields.items():
        if key not in order:
            if isinstance(value, list):
                if not value:
                    lines.append("%s: []" % key)
                else:
                    lines.append("%s:" % key)
                    lines.extend("  - %s" % item for item in value)
            else:
                lines.append("%s: %s" % (key, _scalar(value)))
    lines.append("---")
    return "\n".join(lines) + "\n"


class KitTestCase(unittest.TestCase):
    """Monta um projeto alvo minimo num diretorio temporario."""

    maxDiff = None

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="plk-test-")
        self.root = Path(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.make_project()

    def make_project(self, state=None):
        root = self.root
        (root / "docs" / "_process" / "templates").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "_context" / "adr").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "_handoffs").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "areas").mkdir(parents=True, exist_ok=True)
        (root / "bin" / "lifecycle").mkdir(parents=True, exist_ok=True)

        shutil.rmtree(root / "docs" / "_process", ignore_errors=True)
        shutil.copytree(KIT_ROOT / "docs" / "_process", root / "docs" / "_process")
        shutil.copy2(KIT_ROOT / "docs" / "_context" / "CONTEXT.md",
                     root / "docs" / "_context" / "CONTEXT.md")
        shutil.copy2(KIT_ROOT / "docs" / "_context" / "principles.md",
                     root / "docs" / "_context" / "principles.md")
        shutil.copy2(KIT_ROOT / "docs" / "_context" / "decisions.log",
                     root / "docs" / "_context" / "decisions.log")
        shutil.copy2(KIT_ROOT / "docs" / "AGENTS.md", root / "AGENTS.md")
        (root / "docs" / "KIT_VERSION").write_text(
            (KIT_ROOT / "VERSION").read_text().strip() + "\n", encoding="utf-8")

        for script in ("gate-check", "new-artifact", "session-open", "session-close",
                       "guard-write", "guard-commit", "decide", "plan",
                       "confirm-import", "_kitlib.py"):
            src = BIN / script
            if src.exists():
                dst = root / "bin" / "lifecycle" / script
                shutil.copy2(src, dst)
                dst.chmod(0o755)

        self.write_state(state or dict(DEFAULT_STATE))

    def write_state(self, state):
        (self.root / "docs" / "STATE.md").write_text(dump_state(state), encoding="utf-8")

    def read_state(self):
        """Le o STATE.md pelo parser do kit, que e o que os scripts usam."""
        sys.path.insert(0, str(BIN))
        try:
            import importlib
            import _kitlib
            importlib.reload(_kitlib)
            return _kitlib.read_state(self.root)
        finally:
            sys.path.remove(str(BIN))

    def raw_state(self, text):
        (self.root / "docs" / "STATE.md").write_text(text, encoding="utf-8")

    def write_artifact(self, area, phase, name, **fields):
        base = {
            "phase": phase,
            "area": area,
            "title": name,
            "status": "draft",
            "owner": "Jonathan Camargo",
            "inputs": [],
            "approved_by": None,
            "approved_at": None,
            "superseded_by": None,
        }
        base.update(fields)
        path = self.root / "docs" / "areas" / area / phase / (name + ".md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dump_frontmatter(base) + "\n# %s\n\ncorpo\n" % name,
                        encoding="utf-8")
        return path.relative_to(self.root).as_posix()

    def write_area_readme(self, area):
        path = self.root / "docs" / "areas" / area / "README.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Area: %s\n\n| Tier | 1 |\n" % area, encoding="utf-8")
        return path

    def run_script(self, script, *args, cwd=None, stdin=None):
        return subprocess.run(
            [sys.executable, str(BIN / script)] + [str(a) for a in args],
            cwd=str(cwd or self.root), capture_output=True, text=True, input=stdin)

    def git_init(self, commit=True):
        env = {"GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "f@x",
               "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "f@x"}
        os.environ.update(env)
        self._git("init", "-q", "-b", "main")
        self._git("config", "user.name", "Fixture")
        self._git("config", "user.email", "f@x")
        if commit:
            self.git_commit("inicial")

    def git_commit(self, message):
        self._git("add", "-A")
        return subprocess.run(["git", "commit", "-q", "--no-verify", "-m", message],
                              cwd=str(self.root), capture_output=True, text=True)

    def _git(self, *args):
        return subprocess.run(["git"] + list(args), cwd=str(self.root),
                              capture_output=True, text=True)

    def codes(self, result):
        found = set()
        for line in (result.stdout + result.stderr).splitlines():
            line = line.strip()
            if line.startswith("["):
                found.add(line[1:line.index("]")])
        return found

    def assertCode(self, result, code):
        self.assertIn(code, self.codes(result),
                      "esperava %s. saida:\n%s\n%s" % (code, result.stdout, result.stderr))

    def assertNoCode(self, result, code):
        self.assertNotIn(code, self.codes(result),
                         "nao esperava %s. saida:\n%s\n%s" % (code, result.stdout, result.stderr))
