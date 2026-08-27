"""Commit de codigo fora de uma fase de build.

Nao e bloqueio automatico: e recusa com o custo explicito, e passagem so com
autorizacao deliberada e permanente no historico (o trailer Sem-fase).
"""
import subprocess
import sys
import unittest

from kitfixture import DEFAULT_STATE, KIT_ROOT, KitTestCase

MSG_COMUM = "adiciona a feature de checkout\n"


class TestFaseParaCodigo(KitTestCase):
    def commit_msg(self, mensagem):
        alvo = self.root / "MSG"
        alvo.write_text(mensagem, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(KIT_ROOT / "git-hooks" / "commit-msg"), "MSG"],
            cwd=str(self.root), capture_output=True, text=True)

    def _stage(self, *paths):
        subprocess.run(["git", "add"] + list(paths), cwd=str(self.root),
                       capture_output=True)

    def _codigo(self):
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        self._stage("src/app.py")

    def _fase(self, slug, status="in_progress"):
        path = self.write_artifact("nucleo", slug, "artefato",
                                   inputs=["docs/_context/CONTEXT.md"])
        estado = dict(DEFAULT_STATE)
        estado["tier"] = 1
        estado["current_phase"] = slug
        estado["gates"] = {slug: {"status": status, "evidence": path,
                                  "by": None, "date": None}}
        self.write_state(estado)

    def test_recusa_codigo_sem_fase_de_build(self):
        self.git_init()
        self._codigo()
        result = self.commit_msg(MSG_COMUM)
        self.assertEqual(result.returncode, 1)
        saida = result.stdout + result.stderr
        self.assertIn("Sem-fase:", saida, "a saida precisa dizer como prosseguir")
        self.assertIn("13-build-log", saida, "precisa dizer qual fase falta")

    def test_a_recusa_explica_o_que_se_perde(self):
        self.git_init()
        self._codigo()
        saida = self.commit_msg(MSG_COMUM).stdout + self.commit_msg(MSG_COMUM).stderr
        for pista in ("spec", "review", "rastro"):
            self.assertIn(pista, saida.lower(),
                          "a recusa precisa nomear o custo, nao so proibir")

    def test_passa_com_a_fase_de_build_aberta(self):
        self.git_init()
        self._fase("13-build-log")
        self._codigo()
        self.assertEqual(self.commit_msg(MSG_COMUM).returncode, 0)

    def test_passa_nas_fases_seguintes_a_build(self):
        for slug in ("14-review", "17-ship"):
            with self.subTest(slug=slug):
                self.setUp()
                self.git_init()
                self._fase(slug)
                self._codigo()
                self.assertEqual(self.commit_msg(MSG_COMUM).returncode, 0)

    def test_recusa_em_fase_anterior_a_build(self):
        self.git_init()
        self._fase("01-contexto")
        self._codigo()
        self.assertEqual(self.commit_msg(MSG_COMUM).returncode, 1)

    def test_autorizacao_explicita_libera(self):
        self.git_init()
        self._codigo()
        mensagem = ("corrige o timeout do gateway\n\n"
                    "Sem-fase: hotfix de producao, autorizado por Jonathan\n")
        result = self.commit_msg(mensagem)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_autorizacao_exige_motivo(self):
        self.git_init()
        self._codigo()
        self.assertEqual(self.commit_msg("x\n\nSem-fase:\n").returncode, 1)

    def test_commit_so_de_docs_nao_e_afetado(self):
        self.git_init()
        self.write_artifact("nucleo", "01-contexto", "contexto")
        self._stage("docs")
        self.assertEqual(self.commit_msg(MSG_COMUM).returncode, 0)

    def test_o_proprio_kit_nao_conta_como_codigo(self):
        self.git_init()
        (self.root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
        self._stage("AGENTS.md")
        self.assertEqual(self.commit_msg(MSG_COMUM).returncode, 0)


class TestPh01(KitTestCase):
    def test_ph01_avisa_e_nao_derruba_o_exit_code(self):
        self.git_init()
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(self.root), capture_output=True)
        subprocess.run(["git", "commit", "-q", "--no-verify", "-m",
                        "feature\n\nSem-fase: autorizado por Jonathan"],
                       cwd=str(self.root), capture_output=True)
        result = self.run_script("gate-check")
        self.assertIn("PH-01", result.stdout)
        self.assertEqual(result.returncode, 0, "aviso nao derruba o exit code")

    def test_sem_commits_sem_fase_nao_avisa(self):
        self.git_init()
        result = self.run_script("gate-check")
        self.assertNotIn("PH-01", result.stdout)


if __name__ == "__main__":
    unittest.main()
