"""Modo reverso: gate por fase suspenso, confirmacao em bloco.

O que estes testes protegem nao e a mecanica, e a distincao que a justifica.
Confirmar em bloco muda a granularidade da deliberacao, nao a natureza dela:
continua sendo ato humano, e a reconstrucao so vale se apontar para o que a
sustenta.
"""
import subprocess
import sys
import unittest

from kitfixture import BIN, DEFAULT_STATE, KitTestCase, dump_frontmatter


class ReversoBase(KitTestCase):
    def rodar(self, script, *args):
        return subprocess.run(
            [sys.executable, str(BIN / script)] + [str(a) for a in args],
            cwd=str(self.root), capture_output=True, text=True)

    def artefato(self, slug, nome, ponteiros=None, status="proposed",
                 inputs=None):
        campos = {"phase": slug, "area": "nucleo", "title": nome,
                  "status": status, "owner": "Jonathan Camargo",
                  "inputs": list(inputs or []),
                  "approved_by": None, "approved_at": None,
                  "superseded_by": None}
        if ponteiros is not None:
            campos["reconstructed_from"] = ponteiros
        caminho = self.root / "docs" / "areas" / "nucleo" / slug / ("%s.md" % nome)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(dump_frontmatter(campos) + "\n# %s\n" % nome,
                           encoding="utf-8")
        return "docs/areas/nucleo/%s/%s.md" % (slug, nome)


class TestConfirmImport(ReversoBase):
    def montar(self, ponteiros=("src/app.py",), respondida=True):
        rel = self.artefato("01-contexto", "contexto",
                            list(ponteiros) if ponteiros is not None else None)
        state = dict(DEFAULT_STATE)
        state.update({
            "import_mode": "reverse",
            "open_questions": [{"id": "Q1", "question": "O que nao sera feito?",
                                "raised_at": "2026-08-27",
                                "answered": ("Nada de multi-tenant."
                                             if respondida else None)}],
            "gates": {"01-contexto": {"status": "proposed", "evidence": rel,
                                      "by": None, "date": None}},
        })
        self.write_state(state)
        return rel

    def test_confirma_em_bloco_e_baixa_o_import_mode(self):
        self.montar()
        saida = self.rodar("confirm-import", "--by", "Jonathan Camargo")
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        gate = self.read_state()["gates"]["01-contexto"]
        self.assertEqual(gate["status"], "approved")
        self.assertEqual(gate["by"], "Jonathan Camargo")
        self.assertEqual(gate["method"], "reverse-batch")
        self.assertIsNone(self.read_state().get("import_mode"))

    def test_o_artefato_tambem_e_marcado(self):
        rel = self.montar()
        self.rodar("confirm-import", "--by", "Jonathan Camargo")
        texto = (self.root / rel).read_text(encoding="utf-8")
        self.assertIn("status: approved", texto)
        self.assertIn("approved_by: Jonathan Camargo", texto)

    def test_recusa_assinatura_de_agente(self):
        self.montar()
        for nome in ("Claude Code", "codex", "algum BOT", "ai assistant"):
            saida = self.rodar("confirm-import", "--by", nome)
            self.assertNotEqual(saida.returncode, 0,
                                "aceitou %r como quem confirma" % nome)
            self.assertIn("principio 4", saida.stderr)
            self.assertEqual(
                self.read_state()["gates"]["01-contexto"]["status"], "proposed")

    def test_recusa_reconstrucao_sem_ponteiro(self):
        self.montar(ponteiros=None)
        saida = self.rodar("confirm-import", "--by", "Jonathan Camargo")
        self.assertEqual(saida.returncode, 1)
        self.assertIn("reconstructed_from", saida.stdout)
        self.assertEqual(self.read_state()["gates"]["01-contexto"]["status"],
                         "proposed", "confirmou apesar de recusar")

    def test_recusa_pergunta_em_aberto(self):
        self.montar(respondida=False)
        saida = self.rodar("confirm-import", "--by", "Jonathan Camargo")
        self.assertEqual(saida.returncode, 1)
        self.assertIn("Q1", saida.stdout)

    def test_recusa_fora_do_modo_reverso(self):
        self.montar()
        state = self.read_state()
        state["import_mode"] = None
        self.write_state(state)
        saida = self.rodar("confirm-import", "--by", "Jonathan Camargo")
        self.assertNotEqual(saida.returncode, 0)
        self.assertIn("import_mode", saida.stderr)

    def test_dry_run_nao_escreve(self):
        self.montar()
        saida = self.rodar("confirm-import", "--dry-run")
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        self.assertEqual(self.read_state()["gates"]["01-contexto"]["status"],
                         "proposed")

    def test_sem_by_nao_confirma(self):
        self.montar()
        saida = self.rodar("confirm-import")
        self.assertNotEqual(saida.returncode, 0)
        self.assertEqual(self.read_state()["gates"]["01-contexto"]["status"],
                         "proposed")


class TestGateCheckReverso(ReversoBase):
    def montar(self, ponteiros, method="reverse-batch", import_mode=None,
               slugs=("01-contexto",)):
        gates = {}
        for slug in slugs:
            rel = self.artefato(slug, "art-" + slug, ponteiros, status="approved")
            gate = {"status": "approved", "evidence": rel,
                    "by": "Jonathan Camargo", "date": "2026-08-27"}
            if method:
                gate["method"] = method
            gates[slug] = gate
        state = dict(DEFAULT_STATE)
        state.update({"gates": gates, "import_mode": import_mode})
        self.write_state(state)

    def test_rv01_acusa_bloco_sem_ponteiro(self):
        self.montar(None)
        saida = self.rodar("gate-check")
        self.assertEqual(saida.returncode, 1, saida.stdout)
        self.assertIn("RV-01", saida.stdout)

    def test_bloco_com_ponteiro_passa(self):
        self.montar(["src/app.py"])
        self.assertNotIn("RV-01", self.rodar("gate-check").stdout)

    def test_gate_normal_nao_exige_ponteiro(self):
        """Sem method reverse-batch, RV-01 nao tem nada a dizer."""
        self.montar(None, method=None)
        self.assertNotIn("RV-01", self.rodar("gate-check").stdout)

    def test_rv02_avisa_marcador_esquecido(self):
        self.montar(["src/app.py"], import_mode="reverse",
                    slugs=("01-contexto", "13-build-log", "14-review", "17-ship"))
        self.assertIn("RV-02", self.rodar("gate-check").stdout)

    def test_rv02_calado_com_fase_pendente(self):
        """Importacao em andamento nao e marcador esquecido."""
        self.montar(["src/app.py"], import_mode="reverse")
        self.assertNotIn("RV-02", self.rodar("gate-check").stdout)


class TestPlanReverso(ReversoBase):
    def test_painel_abre_pela_duvida(self):
        com = self.artefato("01-contexto", "contexto", ["src/app.py"])
        sem = self.artefato("13-build-log", "build", None)
        state = dict(DEFAULT_STATE)
        state.update({
            "import_mode": "reverse",
            "current_area": "nucleo",
            "open_questions": [{"id": "Q1", "question": "O que nao sera feito?",
                                "raised_at": "2026-08-27", "answered": None}],
            "gates": {
                "01-contexto": {"status": "proposed", "evidence": com,
                                "by": None, "date": None},
                "13-build-log": {"status": "proposed", "evidence": sem,
                                 "by": None, "date": None}},
        })
        self.write_state(state)
        saida = self.rodar("plan")
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        texto = saida.stdout
        self.assertIn("Modo reverso", texto)
        # A duvida vem antes dos documentos: vinte documentos em ordem numa
        # sessao so e a receita da leitura diagonal.
        self.assertLess(texto.index("Q1"), texto.index("sem ponteiro"))
        self.assertIn("confirm-import", texto)

    def test_separa_por_forca_de_evidencia(self):
        com = self.artefato("01-contexto", "contexto", ["src/app.py", "README.md"])
        sem = self.artefato("13-build-log", "build", None)
        state = dict(DEFAULT_STATE)
        state.update({
            "import_mode": "reverse",
            "gates": {
                "01-contexto": {"status": "proposed", "evidence": com,
                                "by": None, "date": None},
                "13-build-log": {"status": "proposed", "evidence": sem,
                                 "by": None, "date": None}},
        })
        self.write_state(state)
        texto = self.rodar("plan").stdout
        self.assertIn("2 ponteiro(s)", texto)
        self.assertIn("sem ponteiro de evidencia (1)", texto)

    def test_fora_do_modo_reverso_o_plan_nao_muda(self):
        self.write_state(dict(DEFAULT_STATE))
        self.assertNotIn("Modo reverso", self.rodar("plan").stdout)


class TestCompatibilidadeComProjetoAntigo(ReversoBase):
    """import_mode nasceu na 1.2.0, e o --update nao toca em docs/STATE.md.

    Um projeto instalado antes dela nao tem a chave. Se ST-01 cobrasse o campo,
    todo commit desse projeto morreria depois de atualizar o kit, que e
    exatamente o modo de falha que este teste existe para impedir.
    """

    def test_state_sem_import_mode_nao_quebra(self):
        self.write_state(dict(DEFAULT_STATE))
        caminho = self.root / "docs" / "STATE.md"
        texto = "\n".join(l for l in caminho.read_text(encoding="utf-8").splitlines()
                          if not l.startswith("import_mode:"))
        caminho.write_text(texto + "\n", encoding="utf-8")
        self.assertNotIn("import_mode", caminho.read_text(encoding="utf-8"))

        saida = self.rodar("gate-check")
        self.assertEqual(saida.returncode, 0,
                         "projeto sem o campo novo parou de commitar: " + saida.stdout)
        self.assertNotIn("ST-01", saida.stdout)

    def test_ausente_vale_como_modo_normal(self):
        self.write_state(dict(DEFAULT_STATE))
        caminho = self.root / "docs" / "STATE.md"
        texto = "\n".join(l for l in caminho.read_text(encoding="utf-8").splitlines()
                          if not l.startswith("import_mode:"))
        caminho.write_text(texto + "\n", encoding="utf-8")
        self.assertNotIn("Modo reverso", self.rodar("plan").stdout)
        self.assertNotEqual(self.rodar("confirm-import", "--by", "Jonathan Camargo")
                            .returncode, 0)


class TestConfirmImportAtomico(ReversoBase):
    """Confirmar vinte fases e uma operacao so, nao vinte."""

    def montar_dois(self):
        bom = self.artefato("01-contexto", "contexto", ["src/app.py"])
        # IN-03: fora de 01 e 02, inputs vazio e erro. No modo reverso a
        # reconstrucao encadeia igual, senao o gate-check recusa.
        ruim = self.artefato("13-build-log", "build", ["src/app.py"],
                             inputs=[bom])
        state = dict(DEFAULT_STATE)
        state.update({
            "import_mode": "reverse",
            "gates": {
                "01-contexto": {"status": "proposed", "evidence": bom,
                                "by": None, "date": None},
                "13-build-log": {"status": "proposed", "evidence": ruim,
                                 "by": None, "date": None}},
        })
        self.write_state(state)
        return bom, ruim

    def test_planejamento_nao_escreve_antes_de_conferir_tudo(self):
        """texto_aprovado calcula sem gravar: e o que impede o estado pela metade.

        O ramo de rollback em si nao da para exercitar aqui, porque o container
        roda como root e permissao de arquivo nao injeta falha de escrita.
        Fica sem cobertura, e isso esta dito no PR em vez de disfarcado.
        """
        bom, ruim = self.montar_dois()
        antes = [(self.root / rel).read_text(encoding="utf-8")
                 for rel in (bom, ruim)]
        saida = self.rodar("confirm-import", "--dry-run")
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        depois = [(self.root / rel).read_text(encoding="utf-8")
                  for rel in (bom, ruim)]
        self.assertEqual(antes, depois, "dry-run tocou nos artefatos")

    def test_gate_check_sujo_bloqueia_a_confirmacao(self):
        bom, _ = self.montar_dois()
        # evidence apontando para path inexistente: ST-03.
        state = self.read_state()
        state["gates"]["13-build-log"]["evidence"] = "docs/areas/nucleo/nao-existe.md"
        self.write_state(state)
        saida = self.rodar("confirm-import", "--by", "Jonathan Camargo")
        self.assertEqual(saida.returncode, 1)
        self.assertIn("gate-check", saida.stdout)
        self.assertIn("status: proposed", (self.root / bom).read_text(encoding="utf-8"))


class TestSequenciamentoSuspenso(ReversoBase):
    """SQ-01 nao vale no modo reverso: a fase anterior ainda esta proposed.

    A fixture nasce com current_phase None e nenhum teste de modo reverso
    passava --phase. Com em_andamento vazio, check_sequence retornava antes
    de olhar os gates, e o modo reverso passou na suite sem nunca ter sido
    exercitado contra o SQ-01. Num projeto de verdade, com a segunda fase
    reconstruida e a primeira ainda proposta -- o estado normal do modo
    reverso --, new-artifact e session-close chamam gate-check e reprovam.
    """

    def montar(self, import_mode="reverse"):
        gates = {}
        for slug in ("01-contexto", "02-discovery"):
            rel = self.artefato(slug, "art-" + slug, ["src/app.py"])
            gates[slug] = {"status": "proposed", "evidence": rel,
                           "by": None, "date": None}
        state = dict(DEFAULT_STATE)
        state.update({"tier": 3, "import_mode": import_mode, "gates": gates})
        self.write_state(state)
        return state

    def test_fase_alvo_nao_e_cobrada(self):
        """O caso que new-artifact exercita: gate-check --phase antes de criar."""
        self.montar()
        saida = self.rodar("gate-check", "--phase", "03-csd")
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        self.assertNotIn("SQ-01", saida.stdout)

    def test_current_phase_nao_e_cobrada(self):
        """O caso que session-close exercita: gate-check sem --phase."""
        state = self.montar()
        state["current_phase"] = "02-discovery"
        self.write_state(state)
        saida = self.rodar("gate-check")
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        self.assertNotIn("SQ-01", saida.stdout)

    def test_fora_do_modo_reverso_continua_cobrando(self):
        """Suspender no reverso nao pode ter desligado o sequenciamento normal."""
        self.montar(import_mode=None)
        saida = self.rodar("gate-check", "--phase", "03-csd")
        self.assertEqual(saida.returncode, 1, saida.stdout)
        self.assertIn("SQ-01", saida.stdout)
