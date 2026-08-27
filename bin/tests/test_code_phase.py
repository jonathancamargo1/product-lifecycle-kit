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


class TestBordas(KitTestCase):
    """Casos que a regra de fase para codigo nao pode quebrar."""

    def commit_msg(self, mensagem):
        (self.root / "MSG").write_text(mensagem, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(KIT_ROOT / "git-hooks" / "commit-msg"), "MSG"],
            cwd=str(self.root), capture_output=True, text=True)

    def _codigo(self, nome="src/app.py"):
        alvo = self.root / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", nome], cwd=str(self.root), capture_output=True)

    def test_kitlib_antigo_nao_derruba_o_hook(self):
        """Hook novo com _kitlib sem as funcoes novas degrada, nao explode."""
        self.git_init()
        # Usa o _kitlib da 1.0.0 de verdade, do historico do proprio kit, em vez
        # de recortar o atual: recorte por indice de string ja tinha comido
        # metade do modulo sem ninguem notar.
        antigo = subprocess.run(
            ["git", "show", "981d293:bin/_kitlib.py"], cwd=str(KIT_ROOT),
            capture_output=True, text=True)
        if antigo.returncode != 0:
            self.skipTest("historico do kit indisponivel para pegar a 1.0.0")
        lib = self.root / "bin" / "lifecycle" / "_kitlib.py"
        lib.write_text(antigo.stdout, encoding="utf-8")
        self.assertNotIn("def is_code_path", antigo.stdout,
                         "a 1.0.0 nao deveria ter a funcao nova")
        self._codigo()
        result = self.commit_msg("qualquer coisa\n")
        self.assertEqual(result.returncode, 0,
                         "hook explodiu com lib antiga:\n" + result.stderr)

    def test_trailer_dentro_do_diff_do_commit_v_nao_autoriza(self):
        """git commit -v anexa o diff. Um doc que cita o trailer nao autoriza."""
        self.git_init()
        self._codigo()
        mensagem = (
            "adiciona feature\n"
            "# Please enter the commit message for your changes.\n"
            "# ------------------------ >8 ------------------------\n"
            "diff --git a/README.md b/README.md\n"
            "+Sem-fase: <por que entra sem fase, e quem autorizou>\n")
        self.assertEqual(self.commit_msg(mensagem).returncode, 1,
                         "o diff anexado autorizou o commit")

    def test_linha_de_comentario_nao_autoriza(self):
        self.git_init()
        self._codigo()
        self.assertEqual(
            self.commit_msg("x\n\n# Sem-fase: isto e um comentario\n").returncode, 1)

    def test_cherry_pick_e_revert_nao_sao_barrados(self):
        """Movem commit que ja existe, nao estao autorando codigo novo."""
        for marca in ("CHERRY_PICK_HEAD", "REVERT_HEAD"):
            with self.subTest(marca=marca):
                self.setUp()
                self.git_init()
                self._codigo()
                (self.root / ".git" / marca).write_text("0" * 40 + "\n",
                                                        encoding="utf-8")
                self.assertEqual(self.commit_msg("move commit\n").returncode, 0)

    def test_rebase_em_andamento_nao_e_barrado(self):
        self.git_init()
        self._codigo()
        (self.root / ".git" / "rebase-merge").mkdir(parents=True, exist_ok=True)
        self.assertEqual(self.commit_msg("continua o rebase\n").returncode, 0)

    def test_merge_nao_e_barrado(self):
        """Merge nao esta autorando codigo novo, esta juntando o que ja existe."""
        self.git_init()
        self._codigo()
        (self.root / ".git" / "MERGE_HEAD").write_text("0" * 40 + "\n",
                                                       encoding="utf-8")
        self.assertEqual(self.commit_msg("Merge branch 'feature'\n").returncode, 0)

    def test_path_com_acento_nao_vira_codigo(self):
        self.git_init()
        alvo = self.root / "docs" / "decisao-nao-obvia.md"
        alvo.write_text("nota\n", encoding="utf-8")
        acentuado = self.root / "docs" / "decis\u00e3o.md"
        acentuado.write_text("nota\n", encoding="utf-8")
        subprocess.run(["git", "add", "docs"], cwd=str(self.root), capture_output=True)
        result = self.commit_msg("documenta a decisao\n")
        self.assertEqual(result.returncode, 0,
                         "path com acento foi tratado como codigo:\n" + result.stderr)

    def test_delecao_de_codigo_tambem_exige_fase(self):
        self.git_init()
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "velho.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(self.root), capture_output=True)
        subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "base"],
                       cwd=str(self.root), capture_output=True)
        subprocess.run(["git", "rm", "-q", "src/velho.py"], cwd=str(self.root),
                       capture_output=True)
        self.assertEqual(self.commit_msg("remove codigo morto\n").returncode, 1,
                         "apagar codigo do produto passou sem fase")

    def test_a_recusa_manda_rodar_plan_e_nao_um_comando_que_falha(self):
        self.git_init()
        self._codigo()
        saida = self.commit_msg("x\n").stderr
        self.assertIn("plan", saida)
        self.assertNotIn("new-artifact 13-build", saida,
                         "nao mande rodar um comando que o SQ-01 vai recusar")


class TestNaoCodigo(KitTestCase):
    def commit_msg(self, mensagem):
        (self.root / "MSG").write_text(mensagem, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(KIT_ROOT / "git-hooks" / "commit-msg"), "MSG"],
            cwd=str(self.root), capture_output=True, text=True)

    def test_primeiro_commit_do_repositorio_nao_e_barrado(self):
        """A instalacao manda commitar tudo. Nao pode ser recusada."""
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(self.root),
                       capture_output=True)
        subprocess.run(["git", "config", "user.name", "J"], cwd=str(self.root),
                       capture_output=True)
        subprocess.run(["git", "config", "user.email", "j@x"], cwd=str(self.root),
                       capture_output=True)
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(self.root), capture_output=True)
        result = self.commit_msg("instala o product-lifecycle-kit\n")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_documento_na_raiz_nao_e_codigo(self):
        self.git_init()
        for nome in ("README.md", "LICENSE", "CONTRIBUTING.md", "CHANGELOG.md"):
            (self.root / nome).write_text("texto\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(self.root), capture_output=True)
        result = self.commit_msg("atualiza a documentacao\n")
        self.assertEqual(result.returncode, 0, result.stderr)


class TestHigieneDoHook(KitTestCase):
    def commit_msg(self, mensagem):
        (self.root / "MSG").write_text(mensagem, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(KIT_ROOT / "git-hooks" / "commit-msg"), "MSG"],
            cwd=str(self.root), capture_output=True, text=True)

    def test_hook_nao_escreve_pycache_no_projeto(self):
        """__pycache__ versionado no alvo mata o pre-commit depois."""
        self.git_init()
        import shutil
        shutil.rmtree(self.root / "bin" / "lifecycle" / "__pycache__",
                      ignore_errors=True)
        self.commit_msg("qualquer coisa\n")
        self.assertFalse((self.root / "bin" / "lifecycle" / "__pycache__").exists(),
                         "o hook deixou __pycache__ no projeto alvo")

    def test_placeholder_da_propria_recusa_nao_autoriza(self):
        """Copiar a linha sugerida nao e autorizacao de humano."""
        self.git_init()
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/app.py"], cwd=str(self.root),
                       capture_output=True)
        mensagem = ("adiciona feature\n\n"
                    "Sem-fase: <por que entra sem fase, e quem autorizou>\n")
        self.assertEqual(self.commit_msg(mensagem).returncode, 1,
                         "o placeholder da propria mensagem autorizou o commit")


class TestArquivoBinarioEmStaging(KitTestCase):
    def test_guard_commit_sobrevive_a_arquivo_binario(self):
        """Um .pyc em staging nao pode derrubar o guard com UnicodeDecodeError."""
        self.git_init()
        alvo = self.root / "bin" / "lifecycle" / "bin.pyc"
        alvo.write_bytes(b"\xa7\x00\x01binario")
        subprocess.run(["git", "add", "-f", "bin/lifecycle/bin.pyc"],
                       cwd=str(self.root), capture_output=True)
        subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "bin"],
                       cwd=str(self.root), capture_output=True)
        alvo.write_bytes(b"\xa7\x00\x02outro")
        subprocess.run(["git", "add", "-f", "bin/lifecycle/bin.pyc"],
                       cwd=str(self.root), capture_output=True)
        result = self.run_script("guard-commit")
        self.assertNotIn("Traceback", result.stderr, result.stderr[-400:])
        self.assertIn(result.returncode, (0, 1))


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
