"""Decomposição Shapley da variância territorial de e0-80 por grupos de causas.

Módulo de pesquisa para EXPVIDA. Não é executado automaticamente.
Entrada: óbitos [microrregião, idade, grupo de causa] e pessoas-ano [microrregião, idade].
Estimando: variância (ddof=0, pesos iguais por microrregião) da expectativa temporária de vida 0-80.
Contrafactual: para cada subconjunto S, substituir as taxas locais das causas em S pela taxa nacional
da mesma idade/sexo/período; manter as demais taxas locais.
Contribuições positivas indicam redução da variância após equalizar a causa.
A soma Shapley fecha exatamente V(vazio)-V(todas), salvo erro numérico.

Antes de usar com dados reais, resolver o fechamento das causas e a discrepância 558/586.
"""
from __future__ import annotations

from math import factorial
from pathlib import Path
import numpy as np
import pandas as pd

import divergencia_modelo as dm

# Os grupos são mutuamente exclusivos. As categorias externas originais são agregadas.
CAUSE_GROUP = {
    "agressoes": "causas_externas",
    "intervencao_legal": "causas_externas",
    "suicidio": "causas_externas",
    "transporte": "causas_externas",
    "intencao_indeterminada": "causas_externas",
    "acidentes_outros": "causas_externas",
    "externas_outras": "causas_externas",
    "covid19": "covid19",
    "infecciosas": "infecciosas_sem_covid",
    "neoplasias": "neoplasias",
    "endocrinas_nutricionais": "endocrinas_nutricionais",
    "circulatorias": "circulatorias",
    "respiratorias": "respiratorias",
    "digestivas": "digestivas",
    "perinatais": "perinatais_congenitas",
    "congenitas": "perinatais_congenitas",
    "mal_definidas": "mal_definidas",
    "outras_doencas": "outras_doencas",
    "sem_causa": "sem_causa",
}
CAUSE_GROUPS = tuple(dict.fromkeys(CAUSE_GROUP.values()))
AGE_WIDTHS = np.array([1, 4] + [5] * 15 + [None], dtype=object)


def _life_e0_80(mortality_rates, sex):
    """Calcula e0-80 a partir de taxas centrais de mortalidade por idade."""
    m = np.asarray(mortality_rates, dtype=float)
    if m.ndim != 2 or m.shape[1] != 17:
        raise ValueError("A tábua requer taxas para 17 grupos etários (0 a 75-79)")
    m0 = m[:, 0]
    if sex == 1:
        a0 = np.where(m0 >= 0.107, 0.330, 0.045 + 2.684 * m0)
        a1 = np.where(m0 >= 0.107, 1.352, 1.651 - 2.816 * m0)
    elif sex == 2:
        a0 = np.where(m0 >= 0.107, 0.350, 0.053 + 2.800 * m0)
        a1 = np.where(m0 >= 0.107, 1.361, 1.522 - 1.518 * m0)
    else:
        raise ValueError("sex deve ser 1 (homens) ou 2 (mulheres)")

    q = np.empty((m.shape[0], 17), dtype=float)
    q[:, 0] = np.minimum(1.0, m[:, 0] / (1.0 + (1.0 - a0) * m[:, 0]))
    q[:, 1] = np.minimum(1.0, 4.0 * m[:, 1] / (1.0 + (4.0 - a1) * m[:, 1]))
    q[:, 2:] = np.minimum(1.0, 5.0 * m[:, 2:17] / (1.0 + 2.5 * m[:, 2:17]))

    l = np.ones((m.shape[0], 18), dtype=float)
    for j in range(1, 18):
        l[:, j] = l[:, j - 1] * (1.0 - q[:, j - 1])

    L = np.empty((m.shape[0], 17), dtype=float)
    L[:, 0] = l[:, 1] + a0 * (l[:, 0] - l[:, 1])
    L[:, 1] = 4.0 * l[:, 2] + a1 * (l[:, 1] - l[:, 2])
    for j in range(2, 17):
        L[:, j] = 5.0 * l[:, j + 1] + 2.5 * (l[:, j] - l[:, j + 1])
    return L.sum(axis=1)


def variance_e0_80(deaths_by_cause, person_years, sex, national_rates, equalized_mask=0):
    """Variância territorial sob um cenário; bit=1 equaliza o grupo correspondente."""
    d = np.asarray(deaths_by_cause, dtype=float)
    py = np.asarray(person_years, dtype=float)
    if d.ndim != 3 or py.shape != d.shape[:2]:
        raise ValueError("Dimensões esperadas: óbitos [território, idade, causa], pessoas-ano [território, idade]")
    if np.any(py[:, :17] <= 0):
        raise ValueError("Pessoas-ano ausentes ou não positivas em alguma idade 0-79")
    local_rates = d / py[:, :, None]
    rates = local_rates.copy()
    for j in range(d.shape[2]):
        if equalized_mask & (1 << j):
            rates[:, :, j] = national_rates[None, :, j]
    total_rates = rates.sum(axis=2)
    # A tábua e0-80 usa os grupos 0 a 75-79; a idade 80+ não entra no cálculo.
    e = _life_e0_80(total_rates[:, :17], sex)
    return float(np.var(e, ddof=0)), e


def shapley_variance(deaths_by_cause, person_years, sex, group_names=None, max_groups=16):
    """Calcula Shapley exato sobre todos os 2^K cenários."""
    d = np.asarray(deaths_by_cause, dtype=float)
    py = np.asarray(person_years, dtype=float)
    if d.ndim != 3 or py.shape != d.shape[:2]:
        raise ValueError("Dimensões inválidas")
    n, ages, k = d.shape
    if ages != 18:
        raise ValueError("EXPVIDA requer 18 grupos etários (0, 1-4, ..., 80+)")
    if k > max_groups:
        raise ValueError(f"{k} grupos excedem o limite exato configurado ({max_groups})")
    if np.any(d < 0) or np.any(py <= 0):
        raise ValueError("Óbitos devem ser não negativos e pessoas-ano positivas")
    if group_names is None:
        group_names = [f"causa_{j+1}" for j in range(k)]
    if len(group_names) != k:
        raise ValueError("group_names precisa ter um nome por grupo")

    national_rates = d.sum(axis=0) / py.sum(axis=0)[:, None]
    local_rates = d / py[:, :, None]
    base_total_rates = local_rates.sum(axis=2)
    delta_rates = (national_rates[None, :, :] - local_rates).reshape(-1, k)
    n_masks = 1 << k
    values = np.empty(n_masks, dtype=float)
    for mask in range(n_masks):
        bits = np.fromiter(((mask >> j) & 1 for j in range(k)), dtype=float, count=k)
        total_rates = base_total_rates + (delta_rates @ bits).reshape(n, ages)
        e = _life_e0_80(total_rates[:, :17], sex)
        values[mask] = np.var(e, ddof=0)

    base, fully_equalized = values[0], values[-1]
    contributions = np.zeros(k, dtype=float)
    denom = factorial(k)
    for j in range(k):
        bit = 1 << j
        for mask in range(n_masks):
            if mask & bit:
                continue
            size = int(mask.bit_count())
            weight = factorial(size) * factorial(k - size - 1) / denom
            contributions[j] += weight * (values[mask] - values[mask | bit])

    total_change = base - fully_equalized
    closure_error = float(contributions.sum() - total_change)
    return {
        "group_names": list(group_names),
        "variance_observed": float(base),
        "variance_all_causes_equalized": float(fully_equalized),
        "variance_reduction": float(total_change),
        "contributions": contributions,
        "closure_error": closure_error,
        "scenario_variances": values,
    }


def load_period_sex(data_dir, period, sex):
    """Carrega dados versionados do EXPVIDA e prepara tensor de causas e exposição."""
    data_dir = Path(data_dir)
    d1 = pd.read_csv(data_dir / "CAUSAS_OBITOS_2015_2019.csv", sep=";", dtype={"microrregiao": str})
    d1.insert(0, "periodo", "2015-2019")
    d2 = pd.read_csv(data_dir / "CAUSAS_OBITOS_OUTROS_PERIODOS.csv", sep=";", dtype={"microrregiao": str})
    causes = pd.concat([d1, d2], ignore_index=True)
    D, PY, codes = dm.carregar()
    if (period, sex) not in D:
        raise ValueError(f"Período/sexo não encontrado na base geral: {period}, {sex}")
    py = PY[(period, sex)]
    deaths = np.zeros((len(codes), len(dm.IDADES), len(CAUSE_GROUPS)), dtype=float)
    code_idx = {str(code): i for i, code in enumerate(codes)}
    age_idx = {int(age): i for i, age in enumerate(dm.IDADES)}
    group_idx = {name: i for i, name in enumerate(CAUSE_GROUPS)}
    part = causes[(causes.periodo == period) & (causes.sexo.astype(int) == int(sex))].copy()
    unknown = sorted(set(part.causa) - set(CAUSE_GROUP))
    if unknown:
        raise ValueError(f"Categorias de causa sem mapeamento: {unknown}")
    part["grupo_h10"] = part.causa.map(CAUSE_GROUP)
    agg = part.groupby(["microrregiao", "idade_inicio", "grupo_h10"], as_index=False).obitos.sum()
    for row in agg.itertuples(index=False):
        i = code_idx.get(str(row.microrregiao))
        a = age_idx.get(int(row.idade_inicio))
        if i is not None and a is not None:
            deaths[i, a, group_idx[row.grupo_h10]] += float(row.obitos)

    all_cause = D[(period, sex)]
    difference = deaths.sum(axis=2) - all_cause
    diagnostics = {
        "territories": len(codes),
        "cause_deaths": float(deaths.sum()),
        "all_cause_deaths": float(all_cause.sum()),
        "net_difference": float(difference.sum()),
        "cells_with_difference": int(np.count_nonzero(np.abs(difference) > 0)),
        "max_abs_cell_difference": float(np.max(np.abs(difference))),
    }
    return deaths, py, list(CAUSE_GROUPS), diagnostics


def run_h10(data_dir, period, sex, strict_closure=True):
    deaths, py, groups, diagnostics = load_period_sex(data_dir, period, sex)
    if strict_closure and diagnostics["cells_with_difference"] > 0:
        raise ValueError(
            "As causas não fecham com a base geral. Resolver diferenças antes de estimar H10: "
            + str(diagnostics)
        )
    result = shapley_variance(deaths, py, sex, groups)
    result["diagnostics"] = diagnostics
    return result
