"""Um caso que passa e um que falha para cada codigo de gate-check."""
import unittest

from kitfixture import DEFAULT_STATE, KitTestCase, dump_frontmatter


class GateCheckBase(KitTestCase):
    def check(self, *args):
        return self.run_script("gate-check", *args)


class TestFrontmatter(GateCheckBase):
    def test_fm01_passa_com_frontmatter_valido(self):
        self.write_artifact("nucleo", "01-contexto", "contexto")
        self.assertNoCode(self.check(), "FM-01")

    def test_fm01_falha_sem_frontmatter(self):
        path = self.root / "docs" / "areas" / "nucleo" / "01-contexto" / "solto.md"
        path.parent.mkdir(parents=True)
        path.write_text("# sem frontmatter\n", encoding="utf-8")
        result = self.check()
        self.assertCode(result, "FM-01")
        self.assertEqual(result.returncode, 1)

    def test_fm01_ignora_readme_de_area(self):
        self.write_artifact("nucleo", "01-contexto", "contexto")
        self.write_area_readme("nucleo")
        self.assertNoCode(self.check(), "FM-01")

    def test_fm02_passa_com_status_do_enum(self):
        self.write_artifact("nucleo", "01-contexto", "contexto", status="review")
        self.assertNoCode(self.check(), "FM-02")

    def test_fm02_falha_com_status_fora_do_enum(self):
        self.write_artifact("nucleo", "01-contexto", "contexto", status="pronto")
        self.assertCode(self.check(), "FM-02")

    def test_fm02_falha_com_campo_obrigatorio_ausente(self):
        path = self.root / "docs" / "areas" / "nucleo" / "01-contexto" / "x.md"
        path.parent.mkdir(parents=True)
        path.write_text(dump_frontmatter({
            "phase": "01-contexto", "area": "nucleo", "title": "x",
            "status": "draft", "inputs": []}) + "\ncorpo\n", encoding="utf-8")
        self.assertCode(self.check(), "FM-02")

    def test_fm03_passa_com_aprovacao_completa(self):
        self.write_artifact("nucleo", "01-contexto", "contexto", status="approved",
                            approved_by="Jonathan Camargo", approved_at="2026-08-26")
        self.assertNoCode(self.check(), "FM-03")

    def test_fm03_falha_com_approved_sem_data(self):
        self.write_artifact("nucleo", "01-contexto", "contexto", status="approved",
                            approved_by="Jonathan Camargo")
        self.assertCode(self.check(), "FM-03")

    def test_fm04_passa_com_aprovador_humano(self):
        self.write_artifact("nucleo", "01-contexto", "contexto", status="approved",
                            approved_by="Jonathan Camargo", approved_at="2026-08-26")
        self.assertNoCode(self.check(), "FM-04")

    def test_fm04_falha_com_aprovador_agente(self):
        for nome in ("Claude Code", "codex", "AI assistant", "some-BOT", "agent"):
            with self.subTest(nome=nome):
                self.write_artifact("nucleo", "01-contexto", "contexto",
                                    status="approved", approved_by=nome,
                                    approved_at="2026-08-26")
                self.assertCode(self.check(), "FM-04")

    def test_fm05_passa_com_superseded_by(self):
        novo = self.write_artifact("nucleo", "01-contexto", "novo")
        self.write_artifact("nucleo", "01-contexto", "velho", status="superseded",
                            superseded_by=novo)
        self.assertNoCode(self.check(), "FM-05")

    def test_fm05_falha_sem_superseded_by(self):
        self.write_artifact("nucleo", "01-contexto", "velho", status="superseded")
        self.assertCode(self.check(), "FM-05")


class TestInputs(GateCheckBase):
    def test_in01_passa_com_input_existente(self):
        base = self.write_artifact("nucleo", "01-contexto", "contexto")
        self.write_artifact("nucleo", "13-build-log", "build", inputs=[base])
        self.assertNoCode(self.check(), "IN-01")

    def test_in01_falha_com_input_inexistente(self):
        self.write_artifact("nucleo", "13-build-log", "build",
                            inputs=["docs/areas/nucleo/01-contexto/nao-existe.md"])
        result = self.check()
        self.assertCode(result, "IN-01")
        self.assertEqual(result.returncode, 1)

    def test_in02_passa_com_input_mais_velho(self):
        base = self.write_artifact("nucleo", "01-contexto", "contexto")
        self.git_init()
        self.write_artifact("nucleo", "13-build-log", "build", inputs=[base],
                            status="approved", approved_by="Jonathan Camargo",
                            approved_at="2999-01-01")
        self.git_commit("segundo")
        self.assertNoCode(self.check(), "IN-02")

    def test_in02_avisa_com_input_modificado_depois(self):
        base = self.write_artifact("nucleo", "01-contexto", "contexto")
        self.write_artifact("nucleo", "13-build-log", "build", inputs=[base],
                            status="approved", approved_by="Jonathan Camargo",
                            approved_at="2000-01-01")
        self.git_init()
        result = self.check()
        self.assertCode(result, "IN-02")
        self.assertIn("STALE", result.stdout)
        self.assertEqual(result.returncode, 0, "aviso nao pode derrubar o exit code")

    def test_in03_passa_com_inputs_vazios_na_fase_01(self):
        self.write_artifact("nucleo", "01-contexto", "contexto", inputs=[])
        self.assertNoCode(self.check(), "IN-03")

    def test_in03_falha_com_inputs_vazios_fora_das_fases_01_e_02(self):
        self.write_artifact("nucleo", "13-build-log", "build", inputs=[])
        self.assertCode(self.check(), "IN-03")


class TestState(GateCheckBase):
    def test_st01_passa_com_state_completo(self):
        self.assertNoCode(self.check(), "ST-01")

    def test_st01_falha_com_campo_ausente(self):
        self.raw_state("# STATE\n\n```yaml\nproject: x\ntier: 1\n```\n")
        result = self.check()
        self.assertCode(result, "ST-01")
        self.assertEqual(result.returncode, 1)

    def test_st01_falha_sem_bloco_yaml(self):
        self.raw_state("# STATE\n\nsem bloco\n")
        self.assertCode(self.check(), "ST-01")

    def test_st02_passa_com_status_concordando(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="proposed")
        state = dict(DEFAULT_STATE)
        state["gates"] = {"01-contexto": {"status": "proposed", "evidence": path,
                                          "by": None, "date": None}}
        self.write_state(state)
        self.assertNoCode(self.check(), "ST-02")

    def test_st02_passa_com_in_progress_e_artefato_draft(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto", status="draft")
        state = dict(DEFAULT_STATE)
        state["gates"] = {"01-contexto": {"status": "in_progress", "evidence": path,
                                          "by": None, "date": None}}
        self.write_state(state)
        self.assertNoCode(self.check(), "ST-02")

    def test_st02_falha_com_status_divergente(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="proposed")
        state = dict(DEFAULT_STATE)
        state["gates"] = {"01-contexto": {"status": "approved", "evidence": path,
                                          "by": "Jonathan Camargo",
                                          "date": "2026-08-26"}}
        self.write_state(state)
        result = self.check()
        self.assertCode(result, "ST-02")
        self.assertEqual(result.returncode, 1)

    def test_st03_passa_com_evidencia_existente(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto")
        state = dict(DEFAULT_STATE)
        state["gates"] = {"01-contexto": {"status": "in_progress", "evidence": path,
                                          "by": None, "date": None}}
        self.write_state(state)
        self.assertNoCode(self.check(), "ST-03")

    def test_st03_falha_com_evidencia_inexistente(self):
        state = dict(DEFAULT_STATE)
        state["gates"] = {"01-contexto": {"status": "proposed",
                                          "evidence": "docs/areas/x/y.md",
                                          "by": None, "date": None}}
        self.write_state(state)
        self.assertCode(self.check(), "ST-03")


class TestSequencia(GateCheckBase):
    def _aprova(self, state, slug, path):
        state.setdefault("gates", {})[slug] = {
            "status": "approved", "evidence": path,
            "by": "Jonathan Camargo", "date": "2026-08-26"}

    def test_sq01_passa_com_gate_anterior_aprovado(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        build = self.write_artifact("nucleo", "13-build-log", "build", inputs=[path])
        state = dict(DEFAULT_STATE)
        state["gates"] = {}
        self._aprova(state, "01-contexto", path)
        state["gates"]["13-build-log"] = {"status": "in_progress", "evidence": build,
                                          "by": None, "date": None}
        state["current_phase"] = "13-build-log"
        state["current_area"] = "nucleo"
        self.write_state(state)
        self.assertNoCode(self.check(), "SQ-01")

    def test_sq01_falha_com_gate_anterior_nao_aprovado(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="proposed")
        build = self.write_artifact("nucleo", "13-build-log", "build", inputs=[path])
        state = dict(DEFAULT_STATE)
        state["gates"] = {
            "01-contexto": {"status": "proposed", "evidence": path,
                            "by": None, "date": None},
            "13-build-log": {"status": "in_progress", "evidence": build,
                             "by": None, "date": None}}
        state["current_phase"] = "13-build-log"
        state["current_area"] = "nucleo"
        self.write_state(state)
        result = self.check()
        self.assertCode(result, "SQ-01")
        self.assertEqual(result.returncode, 1)

    def test_sq01_ignora_fase_nao_obrigatoria_do_tier(self):
        """Tier 1 nao exige a fase 05, entao ela nao bloqueia a 13."""
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        build = self.write_artifact("nucleo", "13-build-log", "build", inputs=[path])
        state = dict(DEFAULT_STATE)
        state["gates"] = {}
        self._aprova(state, "01-contexto", path)
        state["gates"]["13-build-log"] = {"status": "in_progress", "evidence": build,
                                          "by": None, "date": None}
        state["current_phase"] = "13-build-log"
        self.write_state(state)
        self.assertNoCode(self.check(), "SQ-01")

    def test_sq01_nao_trava_segunda_area_na_mesma_fase(self):
        """Regressao: gates sao chaveados so pela fase (Q2).

        Quando a area B comeca a fase 01, ela sobrescreve o gate 01 que era da
        area A. Se SQ-01 varresse todo gate aberto, o gate 13 da area A, ainda
        em andamento, passaria a exigir um 01 que agora esta in_progress, e o
        projeto travaria: nem commit, nem session-close.
        """
        ctx = self.write_artifact("areaA", "01-contexto", "contexto-a",
                                  status="approved", approved_by="Jonathan Camargo",
                                  approved_at="2026-08-26")
        build = self.write_artifact("areaA", "13-build-log", "build-a",
                                    inputs=[ctx])
        novo_ctx = self.write_artifact("areaB", "01-contexto", "contexto-b")
        estado = dict(DEFAULT_STATE)
        estado["current_phase"] = "01-contexto"
        estado["current_area"] = "areaB"
        estado["gates"] = {
            "01-contexto": {"status": "in_progress", "evidence": novo_ctx,
                            "by": None, "date": None},
            "13-build-log": {"status": "in_progress", "evidence": build,
                             "by": None, "date": None}}
        self.write_state(estado)
        result = self.check()
        self.assertNoCode(result, "SQ-01")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_phase_nao_duplica_ocorrencia_de_sq01(self):
        """--phase nao pode reportar a mesma fase duas vezes."""
        ctx = self.write_artifact("nucleo", "01-contexto", "contexto",
                                  status="proposed")
        estado = dict(DEFAULT_STATE)
        estado["current_phase"] = "13-build-log"
        estado["gates"] = {"01-contexto": {"status": "proposed", "evidence": ctx,
                                           "by": None, "date": None}}
        self.write_state(estado)
        linhas = [l for l in self.check("--phase", "13-build").stdout.splitlines()
                  if l.startswith("[SQ-01]")]
        self.assertEqual(len(linhas), 1, "esperava uma ocorrencia, veio %d:\n%s"
                         % (len(linhas), "\n".join(linhas)))

    def test_phase_recusa_iniciar_sem_gate_anterior(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="proposed")
        state = dict(DEFAULT_STATE)
        state["gates"] = {"01-contexto": {"status": "proposed", "evidence": path,
                                          "by": None, "date": None}}
        self.write_state(state)
        result = self.check("--phase", "13-build")
        self.assertEqual(result.returncode, 1)
        self.assertCode(result, "SQ-01")

    def test_phase_permite_iniciar_com_gate_anterior_aprovado(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        state = dict(DEFAULT_STATE)
        state["gates"] = {"01-contexto": {"status": "approved", "evidence": path,
                                          "by": "Jonathan Camargo",
                                          "date": "2026-08-26"}}
        self.write_state(state)
        result = self.check("--phase", "13-build")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_phase_recusa_prefixo_ambiguo(self):
        result = self.check("--phase", "1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("ambiguo", (result.stdout + result.stderr).lower())


class TestTierDeclarado(GateCheckBase):
    """Sem tier, SQ-01 nao tem o que verificar e o sequenciamento some.

    Esse era o furo: o kit instala com tier null, entao um projeto onde
    ninguem preencheu o tier rodava com a trava desligada, e o gate-check
    dizia que estava tudo certo.
    """

    def _com_gate(self, tier):
        path = self.write_artifact("nucleo", "13-build-log", "build",
                                   inputs=["docs/_context/CONTEXT.md"])
        estado = dict(DEFAULT_STATE)
        estado["tier"] = tier
        estado["gates"] = {"13-build-log": {"status": "in_progress",
                                            "evidence": path, "by": None,
                                            "date": None}}
        self.write_state(estado)

    def test_st05_falha_com_tier_null_e_gate_registrado(self):
        self._com_gate(None)
        result = self.check()
        self.assertCode(result, "ST-05")
        self.assertEqual(result.returncode, 1)

    def test_st05_falha_com_tier_fora_do_enum(self):
        self._com_gate(9)
        self.assertCode(self.check(), "ST-05")

    def test_st05_falha_com_tier_booleano(self):
        """int(True) e 1: sem guarda, tier: true rodaria como tier 1."""
        for valor in (True, False):
            with self.subTest(valor=valor):
                self._com_gate(valor)
                self.assertCode(self.check(), "ST-05")

    def test_st05_passa_com_tier_declarado(self):
        self._com_gate(1)
        self.assertNoCode(self.check(), "ST-05")

    def test_st05_nao_incomoda_projeto_recem_instalado(self):
        """install.sh termina com gate-check. Projeto vazio nao pode acusar."""
        estado = dict(DEFAULT_STATE)
        estado["tier"] = None
        self.write_state(estado)
        result = self.check()
        self.assertNoCode(result, "ST-05")
        self.assertEqual(result.returncode, 0)

    def test_st05_pega_artefato_em_disco_com_state_intocado(self):
        """Modo reverso: backfill escreve artefatos antes de mexer no STATE.md."""
        self.write_artifact("nucleo", "01-contexto", "contexto")
        estado = dict(DEFAULT_STATE)
        estado["tier"] = None
        self.write_state(estado)
        result = self.check()
        self.assertCode(result, "ST-05")
        self.assertEqual(result.returncode, 1)

    def test_st05_falha_com_current_phase_e_sem_tier(self):
        estado = dict(DEFAULT_STATE)
        estado["tier"] = None
        estado["current_phase"] = "01-contexto"
        self.write_state(estado)
        self.assertCode(self.check(), "ST-05")


class TestDecisoes(GateCheckBase):
    def _log(self, texto):
        (self.root / "docs" / "_context" / "decisions.log").write_text(
            texto, encoding="utf-8")

    PENDENTE = ("## D-0001 | 2026-08-26 | PENDING | Nome da regra\n"
                "Contexto: precisa de humano.\n"
                "Opcoes: A / B\n"
                "Recomendacao do agente: B, porque sim.\n"
                "Decisao:\n"
                "Decidido por:\n"
                "Afeta: docs/_context/CONTEXT.md\n")

    def test_dc01_passa_com_blocked_by_correspondente(self):
        self._log(self.PENDENTE)
        state = dict(DEFAULT_STATE)
        state["blocked_by"] = "D-0001"
        self.write_state(state)
        self.assertNoCode(self.check(), "DC-01")

    def test_dc01_falha_com_pendente_sem_blocked_by(self):
        self._log(self.PENDENTE)
        result = self.check()
        self.assertCode(result, "DC-01")
        self.assertEqual(result.returncode, 1)

    def test_dc01_ignora_entrada_decidida(self):
        self._log(self.PENDENTE.replace("PENDING", "DECIDED"))
        self.assertNoCode(self.check(), "DC-01")


class TestVocabulario(GateCheckBase):
    def _proibe(self, *termos):
        path = self.root / "docs" / "_context" / "CONTEXT.md"
        corpo = path.read_text(encoding="utf-8")
        corpo += "\n## Termos proibidos\n\n"
        for termo in termos:
            corpo += "- %s: motivo qualquer\n" % termo
        path.write_text(corpo, encoding="utf-8")

    def test_vc01_passa_sem_termo_proibido_no_codigo(self):
        self._proibe("usuario premium")
        (self.root / "src").mkdir()
        (self.root / "src" / "app.py").write_text("assinante = 1\n", encoding="utf-8")
        self.assertNoCode(self.check(), "VC-01")

    def test_vc01_falha_com_termo_proibido_no_codigo(self):
        self._proibe("usuario premium")
        (self.root / "src").mkdir()
        (self.root / "src" / "app.py").write_text(
            "# o usuario Premium tem desconto\n", encoding="utf-8")
        result = self.check()
        self.assertCode(result, "VC-01")
        self.assertEqual(result.returncode, 1)

    def test_vc01_nao_varre_a_propria_lista(self):
        self._proibe("usuario premium")
        self.assertNoCode(self.check(), "VC-01")

    def test_vc01_exige_limite_de_palavra(self):
        self._proibe("id")
        (self.root / "src").mkdir()
        (self.root / "src" / "app.py").write_text("valido = 1\n", encoding="utf-8")
        self.assertNoCode(self.check(), "VC-01")


class TestEstrutura(GateCheckBase):
    def test_dr01_passa_sem_pasta_vazia(self):
        self.write_artifact("nucleo", "01-contexto", "contexto")
        self.assertNoCode(self.check(), "DR-01")

    def test_dr01_avisa_com_pasta_vazia(self):
        (self.root / "docs" / "areas" / "orfa").mkdir(parents=True)
        result = self.check()
        self.assertCode(result, "DR-01")
        self.assertEqual(result.returncode, 0, "aviso nao pode derrubar o exit code")

    def test_kv01_passa_com_versao_compativel(self):
        self.assertNoCode(self.check(), "KV-01")

    def test_kv01_avisa_com_major_incompativel(self):
        (self.root / "docs" / "KIT_VERSION").write_text("99.0.0\n", encoding="utf-8")
        result = self.check()
        self.assertCode(result, "KV-01")
        self.assertEqual(result.returncode, 0)

    def test_kv01_avisa_sem_arquivo(self):
        (self.root / "docs" / "KIT_VERSION").unlink()
        self.assertCode(self.check(), "KV-01")


class TestSaida(GateCheckBase):
    def test_projeto_limpo_sai_zero(self):
        self.write_artifact("nucleo", "01-contexto", "contexto")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_formato_da_linha_de_relatorio(self):
        self.write_artifact("nucleo", "01-contexto", "contexto", status="pronto")
        linhas = [l for l in self.check().stdout.splitlines() if l.startswith("[FM-02]")]
        self.assertTrue(linhas, "esperava uma linha FM-02")
        self.assertRegex(linhas[0], r"^\[FM-02\] \S+:\d+ .+")

    def test_json_lista_ocorrencias(self):
        import json
        self.write_artifact("nucleo", "01-contexto", "contexto", status="pronto")
        result = self.check("--json")
        dados = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertIn("findings", dados)
        self.assertIn("FM-02", [f["code"] for f in dados["findings"]])
        self.assertEqual(dados["exit_code"], 1)
        for chave in ("file", "line", "message", "severity"):
            self.assertIn(chave, dados["findings"][0])


if __name__ == "__main__":
    unittest.main()
