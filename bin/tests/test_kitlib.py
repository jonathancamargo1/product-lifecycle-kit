"""Round-trip do subconjunto de YAML usado por STATE.md e frontmatter."""
import unittest

from kitfixture import KIT_ROOT

import importlib.util
_spec = importlib.util.spec_from_file_location("_kitlib", KIT_ROOT / "bin" / "_kitlib.py")
kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit)


class TestRoundTrip(unittest.TestCase):
    def _volta(self, valor):
        corpo = kit.dump_state_body({"next_action": valor, "open_questions": [],
                                     "gates": {}})
        return kit.parse_yaml(corpo)["next_action"]

    def test_texto_simples(self):
        self.assertEqual(self._volta("Escrever o nao-escopo"),
                         "Escrever o nao-escopo")

    def test_valor_com_cerquilha_sobrevive(self):
        """'#' no meio do texto nao pode virar comentario no round-trip."""
        for valor in ("Corrigir o bug #42 do checkout",
                      "#42 primeiro",
                      "ticket#7 sem espaco"):
            with self.subTest(valor=valor):
                self.assertEqual(self._volta(valor), valor)

    def test_valor_com_dois_pontos(self):
        self.assertEqual(self._volta("Decidir: cobrar no ato ou no fim"),
                         "Decidir: cobrar no ato ou no fim")

    def test_comentario_de_verdade_continua_sendo_cortado(self):
        lido = kit.parse_yaml("tier: 1                       # 1 | 2 | 3\n")
        self.assertEqual(lido["tier"], 1)


if __name__ == "__main__":
    unittest.main()
