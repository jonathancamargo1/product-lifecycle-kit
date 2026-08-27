"""plan: o que falta para fechar o tier, e qual e a proxima acao."""
import unittest

from kitfixture import DEFAULT_STATE, KitTestCase


class TestPlan(KitTestCase):
    def plan(self, *args):
        return self.run_script("plan", *args)

    def test_lista_todas_as_fases_obrigatorias_do_tier(self):
        estado = dict(DEFAULT_STATE)
        estado["tier"] = 1
        self.write_state(estado)
        saida = self.plan().stdout
        for slug in ("01-contexto", "13-build-log", "14-review", "17-ship"):
            self.assertIn(slug, saida)

    def test_nao_lista_fase_fora_do_tier(self):
        estado = dict(DEFAULT_STATE)
        estado["tier"] = 1
        self.write_state(estado)
        saida = self.plan().stdout
        self.assertNotIn("05-prd", saida)
        self.assertNotIn("20-retro", saida)

    def test_marca_pendente_o_que_nao_existe(self):
        estado = dict(DEFAULT_STATE)
        estado["tier"] = 1
        self.write_state(estado)
        saida = self.plan().stdout
        self.assertIn("pendente", saida)
        self.assertIn("4 de 4", saida)

    def test_conta_o_que_ja_foi_aprovado(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        estado = dict(DEFAULT_STATE)
        estado["tier"] = 1
        estado["gates"] = {"01-contexto": {"status": "approved", "evidence": path,
                                           "by": "Jonathan Camargo",
                                           "date": "2026-08-26"}}
        self.write_state(estado)
        saida = self.plan().stdout
        self.assertIn("approved", saida)
        self.assertIn("3 de 4", saida)

    def test_aponta_a_proxima_fase(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        estado = dict(DEFAULT_STATE)
        estado["tier"] = 1
        estado["gates"] = {"01-contexto": {"status": "approved", "evidence": path,
                                           "by": "Jonathan Camargo",
                                           "date": "2026-08-26"}}
        self.write_state(estado)
        saida = self.plan().stdout
        self.assertIn("Proxima acao", saida)
        self.assertIn("13-build-log", saida.split("Proxima acao")[1])
        self.assertIn("new-artifact", saida)

    def test_diz_quando_o_tier_esta_completo(self):
        estado = dict(DEFAULT_STATE)
        estado["tier"] = 1
        estado["gates"] = {}
        for slug in ("01-contexto", "13-build-log", "14-review", "17-ship"):
            path = self.write_artifact("nucleo", slug, slug, status="approved",
                                       approved_by="Jonathan Camargo",
                                       approved_at="2026-08-26",
                                       inputs=["docs/_context/CONTEXT.md"])
            estado["gates"][slug] = {"status": "approved", "evidence": path,
                                     "by": "Jonathan Camargo", "date": "2026-08-26"}
        self.write_state(estado)
        saida = self.plan().stdout
        self.assertIn("0 de 4", saida)
        self.assertNotIn("pendente", saida)

    def test_recusa_sem_tier_declarado(self):
        estado = dict(DEFAULT_STATE)
        estado["tier"] = None
        self.write_state(estado)
        result = self.plan()
        self.assertEqual(result.returncode, 1)
        self.assertIn("tier", (result.stdout + result.stderr).lower())

    def test_json_lista_as_fases(self):
        import json
        estado = dict(DEFAULT_STATE)
        estado["tier"] = 1
        self.write_state(estado)
        dados = json.loads(self.plan("--json").stdout)
        self.assertEqual(dados["tier"], 1)
        self.assertEqual(len(dados["fases"]), 4)
        self.assertEqual(dados["faltam"], 4)
        self.assertEqual(dados["fases"][0]["slug"], "01-contexto")
        self.assertEqual(dados["fases"][0]["status"], "pendente")


if __name__ == "__main__":
    unittest.main()
