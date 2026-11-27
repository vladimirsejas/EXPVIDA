"""Testes sintéticos do módulo H10; não usam microdados do SIM.

Executar: python -m unittest test_h10_shapley
"""
import unittest
import numpy as np

from h10_shapley import shapley_variance


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

    def test_shapley_closes(self):
        r = shapley_variance(self.deaths, self.py, 1, ["causa_variavel", "causa_constante"])
        self.assertAlmostEqual(r["closure_error"], 0.0, places=12)
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
