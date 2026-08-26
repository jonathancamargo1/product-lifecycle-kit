"""guard-write e guard-commit: a mesma regra, em dois momentos."""
import datetime
import unittest

from kitfixture import DEFAULT_STATE, KitTestCase

HOJE = datetime.date.today().isoformat()

DECIDIDA = ("## D-0001 | %s | DECIDED | Liberar edicao\n"
            "Contexto: precisava mudar.\n"
            "Opcoes: A / B\n"
            "Recomendacao do agente: B, porque sim.\n"
            "Decisao: seguir com B.\n"
            "Decidido por: Jonathan Camargo em %s\n"
            "Afeta: %s\n")


class TestGuardWrite(KitTestCase):
    def guard(self, path):
        return self.run_script("guard-write", path)

    def _decide(self, path, status="DECIDED", data=HOJE):
        log = self.root / "docs" / "_context" / "decisions.log"
        texto = DECIDIDA % (data, data, path)
        if status != "DECIDED":
            texto = texto.replace("DECIDED", status)
        log.write_text(log.read_text(encoding="utf-8") + "\n" + texto, encoding="utf-8")

    def test_libera_path_nao_protegido(self):
        alvo = self.write_artifact("nucleo", "01-contexto", "contexto")
        self.assertEqual(self.guard(alvo).returncode, 0)

    def test_libera_arquivo_de_codigo_do_projeto(self):
        (self.root / "src").mkdir()
        (self.root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        self.assertEqual(self.guard("src/app.py").returncode, 0)

    def test_bloqueia_context_md(self):
        result = self.guard("docs/_context/CONTEXT.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Arquivo protegido", result.stdout + result.stderr)

    def test_bloqueia_process_inteiro(self):
        self.assertEqual(self.guard("docs/_process/gates.md").returncode, 2)
        self.assertEqual(
            self.guard("docs/_process/templates/05-prd.md").returncode, 2)

    def test_bloqueia_agents_md(self):
        self.assertEqual(self.guard("AGENTS.md").returncode, 2)

    def test_bloqueia_artefato_aprovado(self):
        alvo = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        self.assertEqual(self.guard(alvo).returncode, 2)

    def test_libera_artefato_em_draft(self):
        alvo = self.write_artifact("nucleo", "01-contexto", "contexto", status="draft")
        self.assertEqual(self.guard(alvo).returncode, 0)

    def test_bloqueia_adr_aceita(self):
        adr = self.root / "docs" / "_context" / "adr" / "0002-banco.md"
        adr.write_text("---\nstatus: accepted\n---\n\n# ADR\n", encoding="utf-8")
        self.assertEqual(self.guard("docs/_context/adr/0002-banco.md").returncode, 2)

    def test_libera_adr_proposta(self):
        adr = self.root / "docs" / "_context" / "adr" / "0002-banco.md"
        adr.write_text("---\nstatus: proposed\n---\n\n# ADR\n", encoding="utf-8")
        self.assertEqual(self.guard("docs/_context/adr/0002-banco.md").returncode, 0)

    def test_decisao_decidida_libera_o_path(self):
        self._decide("docs/_context/CONTEXT.md")
        self.assertEqual(self.guard("docs/_context/CONTEXT.md").returncode, 0)

    def test_decisao_pendente_nao_libera(self):
        self._decide("docs/_context/CONTEXT.md", status="PENDING")
        self.assertEqual(self.guard("docs/_context/CONTEXT.md").returncode, 2)

    def test_decisao_para_outro_path_nao_libera(self):
        self._decide("docs/_process/gates.md")
        self.assertEqual(self.guard("docs/_context/CONTEXT.md").returncode, 2)

    def test_decisao_anterior_a_modificacao_nao_libera(self):
        self._decide("docs/_context/CONTEXT.md", data="2000-01-01")
        self.assertEqual(self.guard("docs/_context/CONTEXT.md").returncode, 2)

    def test_arquivo_inexistente_e_liberado(self):
        self.assertEqual(self.guard("docs/areas/nova/01-contexto/x.md").returncode, 0)


class TestGuardCommit(KitTestCase):
    def guard(self):
        return self.run_script("guard-commit")

    def test_passa_sem_nada_em_staging(self):
        self.git_init()
        self.assertEqual(self.guard().returncode, 0)

    def test_passa_com_arquivo_novo_nao_protegido(self):
        self.git_init()
        self.write_artifact("nucleo", "01-contexto", "contexto")
        self._add()
        self.assertEqual(self.guard().returncode, 0)

    def test_bloqueia_edicao_de_artefato_aprovado(self):
        alvo = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        self.git_init()
        caminho = self.root / alvo
        caminho.write_text(caminho.read_text(encoding="utf-8") + "\nmudanca\n",
                           encoding="utf-8")
        self._add()
        result = self.guard()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Arquivo protegido", result.stdout + result.stderr)
        self.assertIn(alvo, result.stdout + result.stderr)

    def test_decisao_decidida_libera_o_commit(self):
        alvo = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        self.git_init()
        caminho = self.root / alvo
        caminho.write_text(caminho.read_text(encoding="utf-8") + "\nmudanca\n",
                           encoding="utf-8")
        log = self.root / "docs" / "_context" / "decisions.log"
        log.write_text(log.read_text(encoding="utf-8") + "\n" +
                       DECIDIDA % (HOJE, HOJE, alvo), encoding="utf-8")
        self._add()
        self.assertEqual(self.guard().returncode, 0)

    def test_permite_a_transicao_humana_para_approved(self):
        """Aprovar troca proposed por approved. O guard olha HEAD, nao staging."""
        alvo = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="proposed")
        self.git_init()
        caminho = self.root / alvo
        caminho.write_text(
            caminho.read_text(encoding="utf-8")
            .replace("status: proposed", "status: approved")
            .replace("approved_by: null", "approved_by: Jonathan Camargo")
            .replace("approved_at: null", "approved_at: 2026-08-26"),
            encoding="utf-8")
        self._add()
        self.assertEqual(self.guard().returncode, 0,
                         "aprovar um gate nao pode ser bloqueado pelo guard")

    def test_lista_todos_os_arquivos_bloqueados(self):
        self.git_init()
        ctx = self.root / "docs" / "_context" / "CONTEXT.md"
        ctx.write_text(ctx.read_text(encoding="utf-8") + "\nmudanca\n", encoding="utf-8")
        proc = self.root / "docs" / "_process" / "tiers.md"
        proc.write_text(proc.read_text(encoding="utf-8") + "\nmudanca\n",
                        encoding="utf-8")
        self._add()
        saida = self.guard().stdout + self.guard().stderr
        self.assertIn("docs/_context/CONTEXT.md", saida)
        self.assertIn("docs/_process/tiers.md", saida)

    def test_bloqueia_commit_de_docs_com_sessao_aberta(self):
        """Equivalente comum da garantia do hook Stop do Claude Code.

        Sem hook de runtime, nada impede o agente de parar no meio. O que
        impede o trabalho de entrar sem handoff e este guard.
        """
        self.git_init()
        estado = dict(DEFAULT_STATE)
        estado.update({"session_open": True, "session_counter": 1,
                       "session_agent": "codex"})
        self.write_state(estado)
        self.write_artifact("nucleo", "01-contexto", "contexto")
        self._add()
        result = self.guard()
        self.assertEqual(result.returncode, 1)
        saida = result.stdout + result.stderr
        self.assertIn("session-close", saida)

    def test_permite_commit_fora_de_docs_com_sessao_aberta(self):
        """Codigo do projeto nao e refem do protocolo de sessao."""
        self.git_init()
        estado = dict(DEFAULT_STATE)
        estado.update({"session_open": True, "session_counter": 1,
                       "session_agent": "codex"})
        self.write_state(estado)
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        import subprocess
        subprocess.run(["git", "add", "src/app.py"], cwd=str(self.root),
                       capture_output=True)
        self.assertEqual(self.guard().returncode, 0)

    def test_permite_commit_de_docs_com_sessao_fechada(self):
        self.git_init()
        self.write_artifact("nucleo", "01-contexto", "contexto")
        self._add()
        self.assertEqual(self.guard().returncode, 0)

    def _add(self):
        import subprocess
        subprocess.run(["git", "add", "-A"], cwd=str(self.root), capture_output=True)


if __name__ == "__main__":
    unittest.main()
