"""Testes unitarios sinteticos de causas_tau_periodos.py."""
import os
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

import causas_tau
import causas_tau_periodos as novo
import divergencia_modelo as dm


class PoolSerial:
    """Substitui o Pool apenas nos testes para executar as mesmas funcoes em serie."""
    def __init__(self, processes=None, initializer=None, initargs=()):
        if initializer:
            initializer(*initargs)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    @staticmethod
    def map(func, iterable, chunksize=None):
        return [func(item) for item in iterable]


class TestCausasTauPeriodos(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data_dir = self.temp.name
        self.codigos = ["01001", "01002", "02001"]
        self.periodos = list(novo.PERIODOS)
        self.linhas_2015 = []
        self.linhas_outros = []

        self.D = {}
        self.PY = {}
        for periodo in self.periodos:
            for sexo in (1, 2):
                matriz = np.zeros((len(self.codigos), len(dm.IDADES)), dtype=float)
                for i, codigo in enumerate(self.codigos):
                    for j, idade in enumerate(dm.IDADES):
                        causas = [("agressoes", 10 + i + j % 3), ("infecciosas", 20 + i + j % 2)]
                        if periodo == "2020-2021 pandemia":
                            causas.append(("covid19", 5 + i))
                        for causa, obitos in causas:
                            linha = {
                                "microrregiao": codigo,
                                "sexo": sexo,
                                "idade_inicio": idade,
                                "causa": causa,
                                "obitos": obitos,
                            }
                            if periodo == "2015-2019":
                                self.linhas_2015.append(linha)
                            else:
                                linha["periodo"] = periodo
                                self.linhas_outros.append(linha)
                            matriz[i, j] += obitos
                self.D[(periodo, sexo)] = matriz
                self.PY[(periodo, sexo)] = np.full_like(matriz, 100000.0)

        pd.DataFrame(self.linhas_2015).to_csv(
            os.path.join(self.data_dir, novo.ARQUIVO_2015_2019), sep=";", index=False
        )
        pd.DataFrame(self.linhas_outros).to_csv(
            os.path.join(self.data_dir, novo.ARQUIVO_OUTROS), sep=";", index=False
        )

    def carregar_sintetico(self):
        return self.D, self.PY, self.codigos

    @staticmethod
    def ajustar_sintetico(obitos, esperados, inicio=None):
        obitos = np.asarray(obitos, dtype=float)
        esperados = np.asarray(esperados, dtype=float)
        tau = 0.05 + float(obitos.sum()) / (float(esperados.sum()) + 1.0) * 0.001
        return {
            "mu": 0.0,
            "tau": tau,
            "u": np.linspace(-0.1, 0.1, len(obitos)),
        }

    def test_leitura_une_os_dois_arquivos_nos_seis_periodos(self):
        dados = novo.ler_causas(self.data_dir)
        self.assertEqual(set(dados.periodo.unique()), set(self.periodos))
        self.assertEqual(len(dados), len(self.linhas_2015) + len(self.linhas_outros))
        self.assertEqual(
            int((dados.periodo == "2015-2019").sum()),
            len(self.linhas_2015),
        )

    def test_2015_2019_reproduz_resultados_do_script_original(self):
        dados = novo.ler_causas(self.data_dir)
        original = pd.DataFrame(self.linhas_2015)
        original.to_csv(
            os.path.join(self.data_dir, "CAUSAS_OBITOS_2015_2019.csv"),
            sep=";",
            index=False,
        )
        with patch.object(dm, "carregar", side_effect=self.carregar_sintetico), \
             patch.object(dm, "ajustar", side_effect=self.ajustar_sintetico), \
             patch.object(causas_tau, "P", self.data_dir), \
             patch.object(causas_tau, "B", 2), \
             patch.object(causas_tau, "MIN_OBITOS", 1), \
             patch.object(causas_tau, "Pool", PoolSerial):
            esperado, _ = novo.analisar_periodo(
                dados, "2015-2019", self.D, self.PY, self.codigos, B=2, min_obitos=1
            )
            causas_tau.main()
            produzido = pd.read_csv(
                os.path.join(self.data_dir, "CAUSAS_TAU.csv"), sep=";"
            )

        colunas = ["sexo", "causa", "faixa", "obitos", "tau", "ic_inf", "ic_sup"]
        a = esperado[colunas].sort_values(["sexo", "causa", "faixa"]).reset_index(drop=True)
        b = produzido[colunas].sort_values(["sexo", "causa", "faixa"]).reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b, check_dtype=False, rtol=1e-12, atol=1e-12)

    def test_covid19_aparece_apenas_no_periodo_com_obitos_covid(self):
        dados = novo.ler_causas(self.data_dir)
        self.assertEqual(set(dados.loc[dados.causa == "covid19", "periodo"].unique()),
                         {"2020-2021 pandemia"})
        with patch.object(dm, "carregar", side_effect=self.carregar_sintetico), \
             patch.object(dm, "ajustar", side_effect=self.ajustar_sintetico):
            tau, _ = novo.executar(
                self.data_dir,
                B=2,
                min_obitos=1,
                gravar=False,
            )
        covid = tau[tau.causa == "covid19"]
        self.assertFalse(covid.empty)
        self.assertEqual(set(covid.periodo.unique()), {"2020-2021 pandemia"})


if __name__ == "__main__":
    unittest.main()
