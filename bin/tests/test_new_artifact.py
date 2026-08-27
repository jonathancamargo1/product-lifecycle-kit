"""new-artifact: cria o artefato, a area e a linha do gate."""
import unittest

from kitfixture import DEFAULT_STATE, KitTestCase


class TestNewArtifact(KitTestCase):
    def novo(self, *args):
        return self.run_script("new-artifact", *args)

    def test_cria_artefato_com_frontmatter_preenchido(self):
        result = self.novo("01-contexto", "onboarding", "Contexto de Onboarding",
                           "--owner", "Jonathan Camargo")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        alvo = (self.root / "docs" / "areas" / "onboarding" / "01-contexto"
                / "contexto-de-onboarding.md")
        self.assertTrue(alvo.exists(), result.stdout + result.stderr)
        texto = alvo.read_text(encoding="utf-8")
        self.assertIn("phase: 01-contexto", texto)
        self.assertIn("area: onboarding", texto)
        self.assertIn("title: Contexto de Onboarding", texto)
        self.assertIn("owner: Jonathan Camargo", texto)
        self.assertIn("status: draft", texto)
        frontmatter = texto.split("---")[1]
        self.assertNotIn("PREENCHER", frontmatter,
                         "o frontmatter nao pode sair com placeholder")

    def test_cria_o_readme_da_area(self):
        self.novo("01-contexto", "onboarding", "Contexto", "--owner", "Jonathan Camargo")
        readme = self.root / "docs" / "areas" / "onboarding" / "README.md"
        self.assertTrue(readme.exists())
        texto = readme.read_text(encoding="utf-8")
        self.assertIn("onboarding", texto)
        self.assertNotIn("PREENCHER-AREA", texto)

    def test_nao_sobrescreve_readme_existente(self):
        self.write_area_readme("onboarding")
        self.novo("01-contexto", "onboarding", "Contexto", "--owner", "Jonathan Camargo")
        texto = (self.root / "docs" / "areas" / "onboarding" / "README.md").read_text(
            encoding="utf-8")
        self.assertIn("| Tier | 1 |", texto)

    def test_registra_o_gate_em_progresso(self):
        self.novo("01-contexto", "onboarding", "Contexto", "--owner", "Jonathan Camargo")
        texto = (self.root / "docs" / "STATE.md").read_text(encoding="utf-8")
        self.assertIn("01-contexto:", texto)
        self.assertIn("status: in_progress", texto)
        self.assertIn("current_phase: 01-contexto", texto)
        self.assertIn("current_area: onboarding", texto)

    def test_aceita_prefixo_de_slug(self):
        self.assertEqual(
            self.novo("01", "onboarding", "Contexto", "--owner", "Ana Souza").returncode,
            0)

    def test_recusa_prefixo_ambiguo(self):
        result = self.novo("1", "onboarding", "Contexto", "--owner", "Ana Souza")
        self.assertEqual(result.returncode, 1)
        self.assertIn("ambiguo", (result.stdout + result.stderr).lower())

    def test_recusa_quando_gate_check_da_fase_falha(self):
        result = self.novo("13-build", "onboarding", "Build", "--owner", "Ana Souza",
                           "--inputs", "docs/_context/CONTEXT.md")
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.root / "docs" / "areas" / "onboarding").exists(),
                         "nao pode criar a area se o gate anterior nao passou")

    def test_exige_inputs_fora_das_fases_01_e_02(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        estado = dict(DEFAULT_STATE)
        estado["gates"] = {"01-contexto": {"status": "approved", "evidence": path,
                                           "by": "Jonathan Camargo",
                                           "date": "2026-08-26"}}
        self.write_state(estado)
        semarg = self.novo("13-build", "nucleo", "Build", "--owner", "Ana Souza")
        self.assertEqual(semarg.returncode, 1)
        self.assertIn("inputs", (semarg.stdout + semarg.stderr).lower())
        comarg = self.novo("13-build", "nucleo", "Build", "--owner", "Ana Souza",
                           "--inputs", path)
        self.assertEqual(comarg.returncode, 0, comarg.stdout + comarg.stderr)
        texto = (self.root / "docs" / "areas" / "nucleo" / "13-build-log"
                 / "build.md").read_text(encoding="utf-8")
        self.assertIn("- " + path, texto)

    def test_recusa_input_inexistente(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        estado = dict(DEFAULT_STATE)
        estado["gates"] = {"01-contexto": {"status": "approved", "evidence": path,
                                           "by": "Jonathan Camargo",
                                           "date": "2026-08-26"}}
        self.write_state(estado)
        result = self.novo("13-build", "nucleo", "Build", "--owner", "Ana Souza",
                           "--inputs", "docs/areas/nucleo/nao-existe.md")
        self.assertEqual(result.returncode, 1)

    def test_recusa_owner_que_parece_agente(self):
        result = self.novo("01-contexto", "onboarding", "Contexto",
                           "--owner", "Claude Code")
        self.assertEqual(result.returncode, 1)

    def _gate_aprovado(self):
        path = self.write_artifact("nucleo", "01-contexto", "contexto",
                                   status="approved", approved_by="Jonathan Camargo",
                                   approved_at="2026-08-26")
        estado = dict(DEFAULT_STATE)
        estado["gates"] = {"01-contexto": {"status": "approved", "evidence": path,
                                           "by": "Jonathan Camargo",
                                           "date": "2026-08-26"}}
        self.write_state(estado)
        return path

    def test_recusa_segundo_artefato_num_gate_aprovado(self):
        """Um comando de agente nao pode reverter aprovacao humana."""
        self._gate_aprovado()
        result = self.novo("01-contexto", "nucleo", "Segundo contexto",
                           "--owner", "Ana Souza")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        saida = (result.stdout + result.stderr).lower()
        self.assertIn("supersede", saida)
        texto = (self.root / "docs" / "STATE.md").read_text(encoding="utf-8")
        self.assertIn("by: Jonathan Camargo", texto,
                      "a aprovacao humana foi destruida")

    def test_supersede_marca_o_anterior_e_registra_o_link(self):
        anterior = self._gate_aprovado()
        result = self.novo("01-contexto", "nucleo", "Segundo contexto",
                           "--owner", "Ana Souza", "--supersede")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        velho = (self.root / anterior).read_text(encoding="utf-8")
        self.assertIn("status: superseded", velho)
        self.assertIn("superseded_by: docs/areas/nucleo/01-contexto/"
                      "segundo-contexto.md", velho)
        self.assertEqual(self.run_script("gate-check").returncode, 0)

    def test_supersede_sem_gate_anterior_e_recusado(self):
        result = self.novo("01-contexto", "nucleo", "Contexto",
                           "--owner", "Ana Souza", "--supersede")
        self.assertEqual(result.returncode, 1)

    def test_o_resultado_passa_no_gate_check(self):
        self.novo("01-contexto", "onboarding", "Contexto", "--owner", "Jonathan Camargo")
        result = self.run_script("gate-check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
