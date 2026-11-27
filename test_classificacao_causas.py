"""Testes unitarios da classificacao de causas do SIM no EXPVIDA.

Executar com: python -m unittest test_classificacao_causas
"""
import unittest

from causas_sim import grupo_causa
from causas_municipio import causa


class TestClassificacaoCausas(unittest.TestCase):
    def test_covid_confirmada_com_marcador_u071(self):
        self.assertEqual(grupo_causa(b"B342", [b"B342 U071"]), "covid19")

    def test_u071_direto(self):
        self.assertEqual(grupo_causa(b"U071"), "covid19")

    def test_covid_com_marcador_u072(self):
        self.assertEqual(grupo_causa(b"B342", [b"B342", b"U07.2"]), "covid19")

    def test_b342_sem_marcador_nao_e_rotulado_covid(self):
        self.assertEqual(grupo_causa(b"B342", [b"B342"]), "infecciosas")

    def test_marcador_covid_em_parte_ii_nao_substitui_causa_basica(self):
        self.assertEqual(grupo_causa(b"E119", [b"E119", b"U071"]), "endocrinas_nutricionais")

    def test_causa_municipal_b342_com_marcador(self):
        self.assertEqual(causa(b"B342", [b"B342 U07.1"]), "covid")

    def test_causa_municipal_u071_direto(self):
        self.assertEqual(causa(b"U071"), "covid")

    def test_causa_municipal_b342_sem_marcador(self):
        self.assertEqual(causa(b"B342", [b"B342"]), "infecciosas")

    def test_agressao(self):
        self.assertEqual(grupo_causa(b"X954"), "agressoes")

    def test_suicidio(self):
        self.assertEqual(grupo_causa(b"X700"), "suicidio")

    def test_transporte(self):
        self.assertEqual(grupo_causa(b"V892"), "transporte")

    def test_mal_definida(self):
        self.assertEqual(grupo_causa(b"R99"), "mal_definidas")

    def test_codigo_vazio(self):
        self.assertEqual(grupo_causa(b""), "sem_causa")


if __name__ == "__main__":
    unittest.main()
