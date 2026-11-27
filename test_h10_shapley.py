"""Testes sintéticos do módulo H10; não usam microdados do SIM.

Executar: python -m unittest test_h10_shapley
"""
import unittest
import numpy as np
import pandas as pd

from h10_shapley import (
    CAUSE_GROUP,
    CAUSE_GROUPINGS,
    CAUSE_GROUPS_BY_NAME,
    agrupar_categorias_causa,
    arquivos_causas,
    shapley_variance,
)


class TestH10Shapley(unittest.TestCase):
    def setUp(self):
        n_territories, n_ages = 4, 18
        py = np.full((n_territories, n_ages), 100000.0)
        deaths = np.zeros((n_territories, n_ages, 2), dtype=float)
        multipliers = [0.5, 0.8, 1.2, 1.5]
        for i, mult in enumerate(multipliers):
            rates_a = np.full(n_ages, 0.0002)
            rates_a[4:13] *= mult
            rates_b = np.full(n_ages, 0.0001)
            deaths[i, :, 0] = np.round(rates_a * py[i])
            deaths[i, :, 1] = np.round(rates_b * py[i])
        self.deaths = deaths
        self.py = py

    def test_versoes_de_arquivos_de_causas(self):
        self.assertEqual(
            arquivos_causas("v1"),
            ("CAUSAS_OBITOS_2015_2019.csv", "CAUSAS_OBITOS_OUTROS_PERIODOS.csv"),
        )
        self.assertEqual(
            arquivos_causas("v2"),
            ("CAUSAS_OBITOS_2015_2019_V2.csv", "CAUSAS_OBITOS_OUTROS_PERIODOS_V2.csv"),
        )
        with self.assertRaises(ValueError):
            arquivos_causas("v3")

    def test_agrupamentos_preservam_categorias_obitos_e_fechamento(self):
        categorias = list(next(iter(CAUSE_GROUPINGS.values())))
        self.assertEqual(len(categorias), 19)
        self.assertEqual(CAUSE_GROUPINGS["atual"], CAUSE_GROUP)
        self.assertEqual(len(CAUSE_GROUPS_BY_NAME["violencia_detalhada"]), 12)
        esperado_detalhado = {
            "agressoes_intervencao_legal": {"agressoes", "intervencao_legal"},
            "intencao_indeterminada": {"intencao_indeterminada"},
            "suicidio": {"suicidio"},
            "transporte": {"transporte"},
            "externas_demais": {"acidentes_outros", "externas_outras"},
            "covid19": {"covid19"},
            "infecciosas_sem_covid": {"infecciosas"},
            "neoplasias": {"neoplasias"},
            "circulatorias": {"circulatorias"},
            "respiratorias": {"respiratorias"},
            "mal_definidas_sem_causa": {"mal_definidas", "sem_causa"},
            "demais_doencas": {
                "endocrinas_nutricionais", "digestivas", "perinatais", "congenitas", "outras_doencas"
            },
        }
        agrupamento_detalhado = CAUSE_GROUPINGS["violencia_detalhada"]
        self.assertEqual(
            {grupo: {causa for causa, alvo in agrupamento_detalhado.items() if alvo == grupo}
             for grupo in CAUSE_GROUPS_BY_NAME["violencia_detalhada"]},
            esperado_detalhado,
        )
        for nome, mapping in CAUSE_GROUPINGS.items():
            with self.subTest(agrupamento=nome):
                self.assertEqual(set(mapping), set(categorias))
                self.assertEqual(len(mapping), len(categorias))

                linhas = []
                for territorio in range(4):
                    for idade in range(18):
                        for j, categoria in enumerate(categorias):
                            linhas.append({
                                "microrregiao": str(territorio),
                                "idade_inicio": idade,
                                "causa": categoria,
                                "obitos": 1 + territorio * (j + 1) + idade % 3,
                            })
                original = pd.DataFrame(linhas)
                agrupado = agrupar_categorias_causa(original, nome)
                self.assertEqual(float(agrupado.obitos.sum()), float(original.obitos.sum()))

                grupos = CAUSE_GROUPS_BY_NAME[nome]
                group_idx = {grupo: i for i, grupo in enumerate(grupos)}
                deaths = np.zeros((4, 18, len(grupos)), dtype=float)
                for row in agrupado.itertuples(index=False):
                    deaths[int(row.microrregiao), int(row.idade_inicio), group_idx[row.grupo_h10]] = row.obitos
                resultado = shapley_variance(deaths, self.py, 1, list(grupos))
                self.assertAlmostEqual(
                    float(resultado["contributions"].sum()),
                    resultado["variance_observed"] - resultado["variance_all_causes_equalized"],
                    places=12,
                )

    def test_shapley_closes(self):
        r = shapley_variance(self.deaths, self.py, 1, ["causa_variavel", "causa_constante"])
        self.assertAlmostEqual(r["closure_error"], 0.0, places=12)
        # Evita regressão que divide taxas por pessoas-ano uma segunda vez.
        self.assertGreater(r["variance_observed"], 1e-10)
        self.assertAlmostEqual(
            r["variance_reduction"],
            r["contributions"].sum(),
            places=12,
        )

    def test_variable_cause_gets_positive_contribution(self):
        r = shapley_variance(self.deaths, self.py, 1, ["causa_variavel", "causa_constante"])
        self.assertGreater(r["contributions"][0], 0.0)
        self.assertAlmostEqual(r["contributions"][1], 0.0, places=12)

    def test_group_order_only_reorders_contributions(self):
        a = shapley_variance(self.deaths, self.py, 1, ["A", "B"])
        b = shapley_variance(self.deaths[:, :, ::-1], self.py, 1, ["B", "A"])
        self.assertAlmostEqual(a["variance_observed"], b["variance_observed"], places=12)
        self.assertAlmostEqual(a["variance_reduction"], b["variance_reduction"], places=12)
        self.assertAlmostEqual(a["contributions"][0], b["contributions"][1], places=12)
        self.assertAlmostEqual(a["contributions"][1], b["contributions"][0], places=12)

    def test_rejects_wrong_age_count(self):
        with self.assertRaises(ValueError):
            shapley_variance(self.deaths[:, :17, :], self.py[:, :17], 1)


if __name__ == "__main__":
    unittest.main()
