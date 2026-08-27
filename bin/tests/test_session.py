"""session-open, session-close e decide."""
import datetime
import unittest

from kitfixture import DEFAULT_STATE, KitTestCase

HANDOFF_OK = "## Fiz\n- escrevi o contexto\n\n## Falta\n- aprovar o gate\n\n## Cuidado com\n- nada\n"


class SessionBase(KitTestCase):
    def abre(self, agente="codex"):
        return self.run_script("session-open", "--agent", agente)

    def state_text(self):
        return (self.root / "docs" / "STATE.md").read_text(encoding="utf-8")

    def handoff(self, texto=HANDOFF_OK, nome="handoff.md"):
        path = self.root / nome
        path.write_text(texto, encoding="utf-8")
        return nome


class TestSessionOpen(SessionBase):
    def test_abre_e_marca_o_estado(self):
        result = self.abre()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        texto = self.state_text()
        self.assertIn("session_open: true", texto)
        self.assertIn("session_counter: 1", texto)
        self.assertIn("session_agent: codex", texto)

    def test_incrementa_o_contador_a_cada_sessao(self):
        self.abre()
        estado = dict(DEFAULT_STATE)
        estado.update({"session_counter": 1, "session_open": False})
        self.write_state(estado)
        self.abre("claude-code")
        self.assertIn("session_counter: 2", self.state_text())

    def test_recusa_abrir_com_sessao_anterior_aberta(self):
        self.abre()
        result = self.abre()
        self.assertEqual(result.returncode, 1)
        saida = result.stdout + result.stderr
        self.assertIn("session-close", saida)
        self.assertIn("session_counter: 1", self.state_text())

    def test_recusa_agente_desconhecido(self):
        result = self.abre("cursor")
        self.assertEqual(result.returncode, 1)
        self.assertIn("session_open: false", self.state_text())

    def test_imprime_os_arquivos_na_ordem_do_protocolo(self):
        estado = dict(DEFAULT_STATE)
        estado["current_phase"] = "05-prd"
        self.write_state(estado)
        saida = self.abre().stdout
        ordem = ["AGENTS.md", "docs/STATE.md", "docs/_context/CONTEXT.md",
                 "docs/_context/principles.md",
                 "docs/_process/templates/05-prd.md"]
        posicoes = [saida.find("=== %s" % nome) for nome in ordem]
        self.assertTrue(all(p >= 0 for p in posicoes),
                        "faltou arquivo na saida:\n%s" % saida)
        self.assertEqual(posicoes, sorted(posicoes), "ordem errada:\n%s" % saida)

    def test_imprime_o_ultimo_handoff_quando_existe(self):
        anterior = self.root / "docs" / "_handoffs" / "2026-08-25-sessao-01.md"
        anterior.write_text("## Fiz\n- coisa anterior\n", encoding="utf-8")
        estado = dict(DEFAULT_STATE)
        estado["last_session"] = "docs/_handoffs/2026-08-25-sessao-01.md"
        estado["session_counter"] = 1
        self.write_state(estado)
        saida = self.abre().stdout
        self.assertIn("coisa anterior", saida)

    def test_roda_gate_check_e_imprime_o_resultado(self):
        self.write_artifact("nucleo", "01-contexto", "contexto", status="pronto")
        saida = self.abre().stdout
        self.assertIn("[FM-02]", saida)


class TestSessionClose(SessionBase):
    def _abre_sessao(self):
        self.git_init()
        self.abre()

    def test_check_recusa_com_sessao_aberta(self):
        self._abre_sessao()
        result = self.run_script("session-close", "--check")
        self.assertEqual(result.returncode, 1)
        self.assertTrue((result.stdout + result.stderr).strip())

    def test_check_passa_com_sessao_fechada(self):
        self.git_init()
        result = self.run_script("session-close", "--check")
        self.assertEqual(result.returncode, 0)

    def test_recusa_fechar_sem_sessao_aberta(self):
        self.git_init()
        nome = self.handoff()
        result = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(result.returncode, 1)

    def test_fecha_move_o_handoff_e_commita(self):
        self._abre_sessao()
        nome = self.handoff()
        result = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        hoje = datetime.date.today().isoformat()
        destino = self.root / "docs" / "_handoffs" / ("%s-sessao-01.md" % hoje)
        self.assertTrue(destino.exists(), "handoff nao foi movido")
        self.assertFalse((self.root / nome).exists(), "origem nao foi removida")
        texto = self.state_text()
        self.assertIn("session_open: false", texto)
        self.assertIn(destino.relative_to(self.root).as_posix(), texto)
        log = self._git("log", "-1", "--pretty=%s").stdout.strip()
        self.assertTrue(log.startswith("sessao 01:"), "mensagem de commit: %r" % log)

    def test_recusa_handoff_sem_as_tres_secoes(self):
        self._abre_sessao()
        nome = self.handoff("## Fiz\n- so isso\n")
        result = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Cuidado com", result.stdout + result.stderr)

    def test_recusa_handoff_longo_demais(self):
        self._abre_sessao()
        corpo = "## Fiz\n" + "".join("- linha %d\n" % i for i in range(20))
        corpo += "\n## Falta\n- x\n\n## Cuidado com\n- y\n"
        nome = self.handoff(corpo)
        result = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(result.returncode, 1)
        self.assertIn("15", result.stdout + result.stderr)

    def test_nao_commita_com_gate_check_falhando(self):
        self._abre_sessao()
        self.write_artifact("nucleo", "01-contexto", "contexto", status="pronto")
        nome = self.handoff()
        result = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(result.returncode, 1)
        log = self._git("log", "-1", "--pretty=%s").stdout.strip()
        self.assertEqual(log, "inicial", "nao podia ter commitado")


class TestHandoffNoDestino(SessionBase):
    """O handoff escrito direto no destino nao pode ser apagado.

    AGENTS.md manda escrever o handoff num arquivo. Nada impede o agente de
    escolher o proprio nome que o script geraria. Se origem e destino forem o
    mesmo arquivo, mover nao pode significar destruir.
    """

    def test_handoff_escrito_no_destino_sobrevive(self):
        self.git_init()
        self.abre()
        import datetime
        nome = "docs/_handoffs/%s-sessao-01.md" % datetime.date.today().isoformat()
        destino = self.root / nome
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(HANDOFF_OK, encoding="utf-8")
        result = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(destino.exists(), "o handoff foi apagado")
        self.assertIn("escrevi o contexto", destino.read_text(encoding="utf-8"))

    def test_st04_falha_com_last_session_inexistente(self):
        estado = dict(DEFAULT_STATE)
        estado["last_session"] = "docs/_handoffs/2026-01-01-sessao-99.md"
        self.write_state(estado)
        result = self.run_script("gate-check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("ST-04", result.stdout)

    def test_st04_passa_com_last_session_existente(self):
        alvo = self.root / "docs" / "_handoffs" / "2026-01-01-sessao-01.md"
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(HANDOFF_OK, encoding="utf-8")
        estado = dict(DEFAULT_STATE)
        estado["last_session"] = "docs/_handoffs/2026-01-01-sessao-01.md"
        self.write_state(estado)
        result = self.run_script("gate-check")
        self.assertNotIn("ST-04", result.stdout)
        self.assertEqual(result.returncode, 0)


class TestFalhaRecuperavel(SessionBase):
    """gate-check falhando nao pode deixar a sessao num beco sem saida."""

    def test_gate_check_falhando_deixa_a_sessao_retomavel(self):
        self.git_init()
        self.abre()
        self.write_artifact("nucleo", "01-contexto", "contexto", status="invalido")
        nome = self.handoff()
        result = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(result.returncode, 1)

        texto = self.state_text()
        self.assertIn("session_open: true", texto,
                      "a sessao ficou fechada apesar da falha")
        self.assertIn("last_session: null", texto,
                      "last_session avancou apesar da falha")
        self.assertTrue((self.root / nome).exists(),
                        "o handoff foi consumido apesar da falha")

        # corrigido o erro, o mesmo comando conclui
        (self.root / "docs" / "areas" / "nucleo" / "01-contexto"
         / "contexto.md").unlink()
        segunda = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(segunda.returncode, 0, segunda.stdout + segunda.stderr)
        self.assertIn("session_open: false", self.state_text())


class TestSessionCloseComCodigoEmStaging(SessionBase):
    """A regra de fase para codigo nao pode estragar o session-close."""

    def test_codigo_em_staging_nao_estraga_o_commit_da_sessao(self):
        self.git_init()
        self.abre()
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        import subprocess
        subprocess.run(["git", "add", "src/app.py"], cwd=str(self.root),
                       capture_output=True)
        nome = self.handoff()
        result = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("session_open: false", self.state_text())
        log = self._git("log", "-1", "--pretty=%s").stdout.strip()
        self.assertTrue(log.startswith("sessao 01:"), "commit da sessao: %r" % log)

    def test_falha_no_commit_devolve_a_sessao(self):
        """Se o commit falhar, a sessao volta a estar aberta e recuperavel."""
        self.git_init()
        self.abre()
        nome = self.handoff()
        # impede o commit sem impedir o gate-check
        (self.root / ".git" / "hooks").mkdir(parents=True, exist_ok=True)
        hook = self.root / ".git" / "hooks" / "commit-msg"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        result = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(result.returncode, 1)
        self.assertIn("session_open: true", self.state_text(),
                      "a sessao ficou fechada apesar de o commit ter falhado")
        self.assertTrue((self.root / nome).exists(),
                        "o handoff foi consumido apesar da falha")


class TestCommitDaSessaoPegaTudo(SessionBase):
    def test_handoff_e_artefato_novos_entram_no_commit(self):
        """Arquivo novo sob docs/ precisa entrar: commit com pathspec sozinho
        ignora untracked, e o handoff nasce untracked sempre."""
        import subprocess
        self.git_init()
        self.abre()
        alvo = self.write_artifact("nucleo", "01-contexto", "contexto")
        nome = self.handoff()
        result = self.run_script("session-close", "--handoff", nome)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        rastreados = self._git("ls-files").stdout
        self.assertIn("docs/_handoffs/", rastreados, "handoff ficou de fora")
        self.assertIn(alvo, rastreados, "artefato ficou de fora")
        sobrou = self._git("status", "--short").stdout
        self.assertNotIn("??", sobrou, "sobrou arquivo nao rastreado: %s" % sobrou)

    def test_staging_do_agente_fora_de_docs_e_preservado(self):
        import subprocess
        self.git_init()
        self.abre()
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/app.py"], cwd=str(self.root),
                       capture_output=True)
        self.write_artifact("nucleo", "01-contexto", "contexto")
        nome = self.handoff()
        self.assertEqual(
            self.run_script("session-close", "--handoff", nome).returncode, 0)
        staged = self._git("diff", "--cached", "--name-only").stdout
        self.assertIn("src/app.py", staged,
                      "o session-close mexeu no staging do agente")


class TestDecide(SessionBase):
    def test_cria_entrada_pendente_e_bloqueia_o_estado(self):
        result = self.run_script(
            "decide", "--titulo", "Qual regra de cobranca",
            "--contexto", "duas leituras possiveis",
            "--opcoes", "A cobrar no ato / B cobrar no fim",
            "--recomendacao", "B, porque combina com o contrato",
            "--afeta", "docs/_context/CONTEXT.md")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        log = (self.root / "docs" / "_context" / "decisions.log").read_text(
            encoding="utf-8")
        self.assertIn("| PENDING | Qual regra de cobranca", log)
        self.assertIn("Afeta: docs/_context/CONTEXT.md", log)
        self.assertIn("blocked_by: D-0001", self.state_text())
        self.assertIn("session-close", result.stdout)

    def test_numera_em_sequencia(self):
        for i in range(2):
            self.run_script("decide", "--titulo", "Decisao %d" % i,
                            "--afeta", "docs/_context/CONTEXT.md")
        log = (self.root / "docs" / "_context" / "decisions.log").read_text(
            encoding="utf-8")
        self.assertIn("## D-0001", log)
        self.assertIn("## D-0002", log)

    def test_a_entrada_criada_nao_derruba_o_gate_check(self):
        self.run_script("decide", "--titulo", "Uma duvida",
                        "--afeta", "docs/_context/CONTEXT.md")
        result = self.run_script("gate-check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exige_afeta(self):
        result = self.run_script("decide", "--titulo", "Sem afeta")
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
