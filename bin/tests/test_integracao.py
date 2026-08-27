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


class TestManifestoNaoLiberaCustomizacao(unittest.TestCase):
    """O manifesto so pode listar o que o kit de fato entregou naquele path.

    Registrar o hash do kit para um arquivo que o projeto customizou daria ao
    guard-commit licenca para trocar a customizacao pela versao do kit sem
    decisao nenhuma, que e o oposto do que a protecao existe para fazer.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="plk-man-")
        self.root = Path(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, True)
        subprocess.run(["git", "init", "-q", "-b", "main", "."],
                       cwd=self.tmp, capture_output=True, text=True)
        self.instala()

    def instala(self, *extra):
        return subprocess.run(
            [str(KIT_ROOT / "install.sh"), str(self.root), "--adapters", "none"]
            + list(extra), capture_output=True, text=True)

    def manifesto(self):
        texto = (self.root / "docs" / ".kit-manifest").read_text(encoding="utf-8")
        return dict((l.split("  ", 1)[1], l.split("  ", 1)[0])
                    for l in texto.splitlines() if "  " in l)

    def soma_do_kit(self, rel):
        import hashlib
        return hashlib.sha256(
            (KIT_ROOT / rel).read_bytes()).hexdigest()

    def test_agents_customizado_nao_entra_no_manifesto_com_o_hash_do_kit(self):
        alvo = self.root / "AGENTS.md"
        alvo.write_text("# AGENTS do projeto\n\nregra nossa.\n", encoding="utf-8")
        saida = self.instala("--update")
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        entrada = self.manifesto().get("AGENTS.md")
        self.assertNotEqual(
            entrada, self.soma_do_kit("docs/AGENTS.md"),
            "manifesto liberou a troca do AGENTS.md customizado pelo do kit")

    def test_agents_intocado_continua_no_manifesto(self):
        saida = self.instala("--update")
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        self.assertEqual(self.manifesto().get("AGENTS.md"),
                         self.soma_do_kit("docs/AGENTS.md"))

    def test_processo_customizado_nao_entra_no_manifesto_com_o_hash_do_kit(self):
        alvo = self.root / "docs" / "_process" / "gates.md"
        alvo.write_text("# gates do projeto\n", encoding="utf-8")
        saida = self.instala("--update")
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        self.assertNotEqual(
            self.manifesto().get("docs/_process/gates.md"),
            self.soma_do_kit("docs/_process/gates.md"),
            "manifesto liberou a troca de um arquivo de processo customizado")
