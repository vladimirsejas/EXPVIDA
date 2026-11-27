"""Testes unitarios da classificacao de causas do SIM no EXPVIDA.

Executar com: python -m unittest test_classificacao_causas
"""
import unittest
import struct

from causas_sim import contar as contar_sim, grupo_causa
from causas_municipio import causa, contar as contar_municipio


def dbf_sintetico(campos, registros):
    """Monta um DBF dBase III pequeno em memória para os testes."""
    descritores = bytearray()
    tamanho_registro = 1
    for nome, largura in campos:
        descritor = bytearray(32)
        descritor[:len(nome)] = nome.encode("ascii")
        descritor[11] = ord("C")
        descritor[16] = largura
        descritores.extend(descritor)
        tamanho_registro += largura
    tamanho_cabecalho = 32 + len(descritores) + 1
    cabecalho = bytearray(32)
    cabecalho[0] = 3
    cabecalho[4:8] = struct.pack("<I", len(registros))
    cabecalho[8:10] = struct.pack("<H", tamanho_cabecalho)
    cabecalho[10:12] = struct.pack("<H", tamanho_registro)
    saida = cabecalho + descritores + b"\x0d"
    for registro in registros:
        saida.extend(b" ")
        for (nome, largura), valor in zip(campos, registro):
            saida.extend(valor.encode("ascii").ljust(largura)[:largura])
    return bytes(saida) + b"\x1a"


class TestClassificacaoCausas(unittest.TestCase):
    def test_contar_sem_colunas_de_linhas(self):
        campos = [("SEXO", 1), ("IDADE", 3), ("CODMUNRES", 6), ("CAUSABAS", 4)]
        dbf = dbf_sintetico(campos, [
            ("1", "400", "123456", "B342"),
            ("2", "400", "123456", "U071"),
        ])

        resultado_sim = contar_sim(dbf, {"123456": "micro"})
        self.assertEqual(resultado_sim["cont"][("micro", "1", 0, "infecciosas")], 1)
        self.assertEqual(resultado_sim["cont"][("micro", "2", 0, "covid19")], 1)
        self.assertEqual(resultado_sim["q"]["sem_colunas_linhas"], 2)
        self.assertEqual(resultado_sim["q"]["b342_sem_u07"], 1)
        self.assertEqual(resultado_sim["q"]["total"], 2)

        resultado_municipio = contar_municipio(dbf)
        self.assertEqual(resultado_municipio["cont"][("123456", "1", 0, "infecciosas")], 1)
        self.assertEqual(resultado_municipio["cont"][("123456", "2", 0, "covid")], 1)
        self.assertEqual(resultado_municipio["q"]["sem_colunas_linhas"], 2)
        self.assertEqual(resultado_municipio["q"]["b342_sem_u07"], 1)

    def test_covid_confirmada_com_marcador_u071(self):
        self.assertEqual(grupo_causa(b"B342", [b"B342 U071"]), "covid19")

    def test_cache_boolean_covid(self):
        self.assertEqual(grupo_causa(b"B342", True), "covid19")
        self.assertEqual(grupo_causa(b"B342", False), "infecciosas")

    def test_u071_direto(self):
        self.assertEqual(grupo_causa(b"U071"), "covid19")

    def test_covid_com_marcador_u072(self):
        self.assertEqual(grupo_causa(b"B342", [b"B342", b"U07.2"]), "covid19")

    def test_u073_nao_e_classificado_como_covid(self):
        self.assertNotEqual(grupo_causa(b"U07.3"), "covid19")
        self.assertNotEqual(causa(b"U07.3"), "covid")

    def test_b342_sem_marcador_nao_e_rotulado_covid(self):
        self.assertEqual(grupo_causa(b"B342", [b"B342"]), "infecciosas")

    def test_marcador_covid_em_parte_ii_nao_substitui_causa_basica(self):
        self.assertEqual(grupo_causa(b"E119", [b"E119", b"U071"]), "endocrinas_nutricionais")

    def test_causa_municipal_b342_com_marcador(self):
        self.assertEqual(causa(b"B342", [b"B342 U07.1"]), "covid")

    def test_cache_boolean_covid_municipal(self):
        self.assertEqual(causa(b"B342", True), "covid")
        self.assertEqual(causa(b"B342", False), "infecciosas")

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
