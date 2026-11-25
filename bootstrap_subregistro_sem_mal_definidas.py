"""Bootstrap pareado por blocos de UF para sensibilidade de sub-registro.
Projeto: Quando o territorio importa (EXPVIDA / C:\\EXPVIDA).

Compara homens de 30-59 anos em 2000-2004 (nove cenarios de cobertura,
sem causas mal definidas) com 2022-2024 (sem causas mal definidas).
Reamostra 27 UFs com reposicao, usa os mesmos sorteios nos dois periodos,
recalcula a referencia leave-one-out em cada replicacao e estima tau pelo
mesmo modelo Poisson-lognormal de divergencia_modelo.py.

Saidas:
- RESULTADO_FINAL_BOOTSTRAP_300.csv
- REPLICACOES_BOOTSTRAP_300.csv

Requer pandas, numpy, scipy e os CSVs fonte na mesma pasta.
"""
import numpy as np
import pandas as pd
import divergencia_modelo as dm

B = 300
SEED = 20261125
PERIODS = ["2000-2004", "2022-2024"]
COLS = dm.BANDAS["30-59"]

UF = [11,12,13,14,15,16,17,21,22,23,24,25,26,27,28,29,31,32,33,35,41,42,43,50,51,52,53]
COVERAGE = {
    "GGB 2000/2010": [.94,.93,.99,1.01,.79,.92,.99,.97,.98,.97,1.01,.98,1.00,1.00,1.01,1.00,1.00,1.09,1.00,1.01,1.04,1.00,1.02,1.09,1.00,.98,1.00],
    "SEG-adj 2000/2010": [.89,.86,.91,.87,.77,.82,.86,.78,.88,.87,.91,.91,.95,.95,.95,.91,.93,1.01,.96,1.00,.99,.94,.99,.98,.92,.90,1.00],
    "SEG-adj 1991/2000": [.98,1.08,.92,1.02,.84,.85,.70,.79,.85,.87,.91,.96,.96,.97,.94,.91,.94,.96,.97,.97,1.01,.96,.98,.99,.92,.89,1.07],
}


def cause_matrix(frame, codes, cause=None):
    """Matriz microrregiao x idade para homens; causa=None representa todas."""
    index = {code: i for i, code in enumerate(codes)}
    matrix = np.zeros((len(codes), len(dm.IDADES)), dtype=float)
    selected = frame[frame.sexo == 1] if cause is None else frame[(frame.sexo == 1) & (frame.causa == cause)]
    grouped = selected.groupby(["microrregiao", "idade_inicio"]).obitos.sum().reset_index()
    for micro, age, deaths in grouped.itertuples(index=False):
        i = index.get(str(micro))
        if i is not None:
            matrix[i, dm.IDADES.index(int(age))] += deaths
    return matrix


def estimate(matrix, person_years, initial=None):
    observed = matrix[:, COLS].sum(axis=1)
    expected = dm.esperados(matrix, person_years, COLS)[1]
    return dm.ajustar(observed, expected, inicio=initial)


def main():
    a = pd.read_csv("CAUSAS_OBITOS_2015_2019.csv", sep=";", dtype={"microrregiao": str})
    a.insert(0, "periodo", "2015-2019")
    b = pd.read_csv("CAUSAS_OBITOS_OUTROS_PERIODOS.csv", sep=";", dtype={"microrregiao": str})
    causes = pd.concat([a, b], ignore_index=True)

    _, population, codes = dm.carregar()
    matrices = {}
    for period in PERIODS:
        subset = causes[causes.periodo == period]
        matrices[period] = cause_matrix(subset, codes) - cause_matrix(subset, codes, "mal_definidas")

    micro_uf = np.array([code[:2] for code in codes])
    blocks = [np.where(micro_uf == uf)[0] for uf in sorted(set(micro_uf))]
    if len(blocks) != 27:
        raise ValueError(f"Esperadas 27 UFs; encontradas {len(blocks)}")
    uf_index = np.array([UF.index(int(code[:2])) for code in codes])

    scenarios = []
    for method, values in COVERAGE.items():
        values = np.minimum(1.0, np.asarray(values, dtype=float))
        for k in (1, 2, 3):
            adjusted = (1 - k * (1 - values))[uf_index]
            if np.any(adjusted <= 0):
                raise ValueError(f"Cobertura ajustada não positiva: {method}, k={k}")
            scenarios.append((f"{method} k{k}", adjusted))

    # Estimativas pontuais da amostra completa.
    point = {}
    for name, coverage in scenarios:
        corrected = matrices["2000-2004"] / coverage[:, None]
        point[name] = estimate(corrected, population[("2000-2004", 1)])
    point["2022-2024"] = estimate(matrices["2022-2024"], population[("2022-2024", 1)])

    # Sorteios pareados: mesmos blocos de UF para os dois períodos.
    rng = np.random.default_rng(SEED)
    selections = [
        np.concatenate([blocks[j] for j in rng.integers(0, len(blocks), len(blocks))])
        for _ in range(B)
    ]
    bootstrap = {name: [] for name, _ in scenarios}
    bootstrap["2022-2024"] = []
    failures = {name: 0 for name in bootstrap}

    for replicate, selection in enumerate(selections, start=1):
        recent = matrices["2022-2024"][selection]
        recent_py = population[("2022-2024", 1)][selection]
        try:
            fit = estimate(recent, recent_py,
                           (point["2022-2024"]["mu"], np.log(point["2022-2024"]["tau"])))
            bootstrap["2022-2024"].append(fit["tau"])
        except Exception:
            failures["2022-2024"] += 1
            bootstrap["2022-2024"].append(np.nan)

        for name, coverage in scenarios:
            corrected = matrices["2000-2004"][selection] / coverage[selection, None]
            py = population[("2000-2004", 1)][selection]
            try:
                fit = estimate(corrected, py,
                               (point[name]["mu"], np.log(point[name]["tau"])))
                bootstrap[name].append(fit["tau"])
            except Exception:
                failures[name] += 1
                bootstrap[name].append(np.nan)
        if replicate % 25 == 0:
            print(f"Replicação {replicate}/{B}", flush=True)

    raw = pd.DataFrame(bootstrap)
    raw.to_csv("REPLICACOES_BOOTSTRAP_300.csv", index=False)

    recent_values = raw["2022-2024"].to_numpy()
    rows = []
    for name, _ in scenarios:
        old_values = raw[name].to_numpy()
        valid = np.isfinite(old_values) & np.isfinite(recent_values)
        difference = old_values[valid] - recent_values[valid]
        rows.append({
            "cenario": name,
            "tau_2000_04": point[name]["tau"],
            "tau_2022_24": point["2022-2024"]["tau"],
            "diferenca_tau": point[name]["tau"] - point["2022-2024"]["tau"],
            "ic95_tau_2000_04_inf": np.nanpercentile(old_values, 2.5),
            "ic95_tau_2000_04_sup": np.nanpercentile(old_values, 97.5),
            "ic95_tau_2022_24_inf": np.nanpercentile(recent_values, 2.5),
            "ic95_tau_2022_24_sup": np.nanpercentile(recent_values, 97.5),
            "ic95_diferenca_inf": np.percentile(difference, 2.5),
            "ic95_diferenca_sup": np.percentile(difference, 97.5),
            "replicacoes_validas": int(valid.sum()),
            "falhas_2000_04": failures[name],
            "falhas_2022_24": failures["2022-2024"],
        })
    summary = pd.DataFrame(rows)
    summary.to_csv("RESULTADO_FINAL_BOOTSTRAP_300.csv", index=False)
    print(summary.to_string(index=False))
    print("Falhas:", failures)


if __name__ == "__main__":
    main()
