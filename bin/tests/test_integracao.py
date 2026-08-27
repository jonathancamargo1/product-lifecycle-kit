"""Ciclo real, com os git hooks instalados de verdade.

Os outros testes chamam os scripts direto. Este instala o kit num repositorio
temporario com install.sh, o que poe pre-commit e commit-msg no lugar, e faz
commits de verdade. E a unica camada que exercita os hooks pelo caminho que o
projeto alvo usa.
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from kitfixture import KIT_ROOT


class TestCicloComHooks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="plk-int-")
        self.root = Path(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.root / "src").mkdir()
        (self.root / "src" / "app.py").write_text("print(1)\n", encoding="utf-8")
        self.git("init", "-q", "-b", "main", ".")
        self.git("config", "user.name", "Jonathan Camargo")
        self.git("config", "user.email", "j@x")
        self.git("add", "-A")
        self.git("commit", "-q", "--no-verify", "-m", "projeto que ja existia")
        subprocess.run([str(KIT_ROOT / "install.sh"), str(self.root),
                        "--adapters", "none"], capture_output=True, text=True)

    def git(self, *args):
        return subprocess.run(["git"] + list(args), cwd=str(self.root),
                              capture_output=True, text=True)

    def lifecycle(self, script, *args):
        import sys
        return subprocess.run(
            [sys.executable, str(self.root / "bin" / "lifecycle" / script)]
            + [str(a) for a in args],
            cwd=str(self.root), capture_output=True, text=True)

    def tier(self, valor):
        import sys
        sys.path.insert(0, str(self.root / "bin" / "lifecycle"))
        import importlib
        import _kitlib
        importlib.reload(_kitlib)
        s = _kitlib.read_state(self.root)
        s.update({"project": "integracao", "tier": valor})
        _kitlib.write_state(self.root, s)

    def test_hooks_ficam_instalados_e_executaveis(self):
        for nome in ("pre-commit", "commit-msg"):
            alvo = self.root / ".git" / "hooks" / nome
            self.assertTrue(alvo.exists(), "%s nao foi instalado" % nome)
            self.assertTrue(os.access(alvo, os.X_OK), "%s nao e executavel" % nome)

    def test_commit_da_instalacao_passa_pelos_hooks(self):
        self.tier(1)
        self.git("add", "-A")
        resultado = self.git("commit", "-m", "instala o product-lifecycle-kit")
        self.assertEqual(resultado.returncode, 0,
                         resultado.stdout + resultado.stderr)

    def test_hook_recusa_codigo_sem_fase_e_aceita_com_autorizacao(self):
        self.tier(1)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "instala o product-lifecycle-kit")
        (self.root / "src" / "app.py").write_text("print(2)\n", encoding="utf-8")
        self.git("add", "src/app.py")
        recusa = self.git("commit", "-m", "muda o app")
        self.assertNotEqual(recusa.returncode, 0, "o hook deixou passar")
        self.assertIn("Sem-fase", recusa.stdout + recusa.stderr)
        self.assertNotIn("Traceback", recusa.stdout + recusa.stderr)
        ok = self.git("commit", "-m",
                      "muda o app\n\nSem-fase: hotfix, autorizado por Jonathan")
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)

    def test_nenhum_pycache_versionado_depois_do_ciclo(self):
        self.tier(1)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "instala o product-lifecycle-kit")
        self.lifecycle("session-open", "--agent", "codex")
        self.lifecycle("new-artifact", "01", "nucleo", "Contexto",
                       "--owner", "Jonathan Camargo")
        handoff = self.root / "h.md"
        handoff.write_text("## Fiz\n- x\n\n## Falta\n- y\n\n## Cuidado com\n- z\n",
                           encoding="utf-8")
        fechou = self.lifecycle("session-close", "--handoff", "h.md")
        self.assertEqual(fechou.returncode, 0, fechou.stdout + fechou.stderr)
        rastreados = self.git("ls-files").stdout
        self.assertNotIn("__pycache__", rastreados)
        self.assertNotIn(".pyc", rastreados)


if __name__ == "__main__":
    unittest.main()
