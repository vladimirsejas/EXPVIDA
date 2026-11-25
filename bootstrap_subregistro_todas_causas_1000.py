"""Bootstrap pareado por blocos de UF (2.000 replicacoes) para todas as causas.
EXPVIDA / Quando o territorio importa.

Analise principal: homens, 30-59 anos; 2000-2004 corrigido por nove cenarios
versus 2022-2024 sem correcao. Todas as causas permanecem incluidas.

Para manter consistencia com a estrategia de pares fixos usada nas analises
anteriores (validacao_tau.py, conforme auditoria independente), O e E sao
calculados na amostra completa antes do bootstrap. Os pares (O_i,E_i) sao
reamostrados em blocos de UF; a referencia leave-one-out nao e recalculada
sobre copias duplicadas durante as replicacoes.

A incerteza das coberturas nao e propagada; os resultados sao condicionais
às coberturas e aos denominadores POPSVS fixados.
"""
import numpy as np
import pandas as pd
import divergencia_modelo as dm

B = 1000
SEED = 20261125
PERIOD_OLD = "2000-2004"
PERIOD_NEW = "2022-2024"
SEX = 1
COLS = dm.BANDAS["30-59"]
UF = [11,12,13,14,15,16,17,21,22,23,24,25,26,27,28,29,31,32,33,35,41,42,43,50,51,52,53]
COVERAGE = {
    "GGB 2000/2010": [.94,.93,.99,1.01,.79,.92,.99,.97,.98,.97,1.01,.98,1.00,1.00,1.01,1.00,1.00,1.09,1.00,1.01,1.04,1.00,1.02,1.09,1.00,.98,1.00],
    "SEG-adj 2000/2010": [.89,.86,.91,.87,.77,.82,.86,.78,.88,.87,.91,.91,.95,.95,.95,.91,.93,1.01,.96,1.00,.99,.94,.99,.98,.92,.90,1.00],
    "SEG-adj 1991/2000": [.98,1.08,.92,1.02,.84,.85,.70,.79,.85,.87,.91,.96,.96,.97,.94,.91,.94,.96,.97,.97,1.01,.96,.98,.99,.92,.89,1.07],
}

def get_oe(D, PY):
    O, E = dm.esperados(D, PY, COLS)
    return O, E

def fit(O, E, start=None):
    return dm.ajustar(O, E, inicio=start)

def main():
    D, PY, codes = dm.carregar()
    D_old = D[(PERIOD_OLD, SEX)].copy()
    PY_old = PY[(PERIOD_OLD, SEX)].copy()
    D_new = D[(PERIOD_NEW, SEX)].copy()
    PY_new = PY[(PERIOD_NEW, SEX)].copy()

    micro_uf = np.array([int(str(c)[:2]) for c in codes])
    uf_index = np.array([UF.index(u) for u in micro_uf])
    unique_ufs = sorted(set(micro_uf))
    blocks = [np.where(micro_uf == uf)[0] for uf in unique_ufs]
    if len(blocks) != 27:
        raise RuntimeError(f"Esperadas 27 UFs; encontradas {len(blocks)}")

    # Periodo recente: todas as causas, pares fixos na amostra completa.
    O_new, E_new = get_oe(D_new, PY_new)
    point_new = fit(O_new, E_new)

    scenarios = []
    for method, vals in COVERAGE.items():
        vals = np.minimum(1.0, np.asarray(vals, dtype=float))
        for k in (1,2,3):
            cov = (1 - k * (1 - vals))[uf_index]
            if np.any(cov <= 0):
                raise RuntimeError(f"Cobertura nao positiva: {method}, k={k}")
            D_corr = D_old / cov[:, None]
            O_old, E_old = get_oe(D_corr, PY_old)
            point = fit(O_old, E_old)
            scenarios.append({"cenario": f"{method} k{k}", "coverage": cov,
                              "O": O_old, "E": E_old, "point": point})

    rng = np.random.default_rng(SEED)
    raw = {"tau_2022_2024": np.full(B, np.nan)}
    for s in scenarios:
        raw[s["cenario"]] = np.full(B, np.nan)
    failures = {k: 0 for k in raw}

    starts = {"tau_2022_2024": (point_new["mu"], np.log(point_new["tau"]))}
    for s in scenarios:
        starts[s["cenario"]] = (s["point"]["mu"], np.log(s["point"]["tau"]))

    for b in range(B):
        draw = rng.integers(0, len(blocks), len(blocks))
        sel = np.concatenate([blocks[j] for j in draw])
        try:
            raw["tau_2022_2024"][b] = fit(O_new[sel], E_new[sel], starts["tau_2022_2024"])["tau"]
        except Exception:
            failures["tau_2022_2024"] += 1
        for s in scenarios:
            name = s["cenario"]
            try:
                raw[name][b] = fit(s["O"][sel], s["E"][sel], starts[name])["tau"]
            except Exception:
                failures[name] += 1
        if (b+1) % 100 == 0:
            print(f"Replicacao {b+1}/{B}", flush=True)

    raw_df = pd.DataFrame(raw)
    raw_df.insert(0, "replicacao", np.arange(1, B+1))
    raw_df.to_csv("REPLICACOES_BOOTSTRAP_TODAS_CAUSAS_1000.csv", index=False)

    newv = raw_df["tau_2022_2024"].to_numpy()
    rows=[]
    for s in scenarios:
        name=s["cenario"]
        oldv=raw_df[name].to_numpy()
        ok=np.isfinite(oldv)&np.isfinite(newv)
        diff=oldv[ok]-newv[ok]
        rows.append({
            "cenario":name,
            "tau_2000_04_pontual":s["point"]["tau"],
            "tau_2022_24_pontual":point_new["tau"],
            "diferenca_pontual":s["point"]["tau"]-point_new["tau"],
            "ic95_tau_2000_04_inf":np.percentile(oldv[np.isfinite(oldv)],2.5),
            "ic95_tau_2000_04_sup":np.percentile(oldv[np.isfinite(oldv)],97.5),
            "ic95_tau_2022_24_inf":np.percentile(newv[np.isfinite(newv)],2.5),
            "ic95_tau_2022_24_sup":np.percentile(newv[np.isfinite(newv)],97.5),
            "ic95_diferenca_inf":np.percentile(diff,2.5),
            "ic95_diferenca_sup":np.percentile(diff,97.5),
            "replicacoes_validas":int(ok.sum()),
            "falhas_2000_04":failures[name],
            "falhas_2022_24":failures["tau_2022_2024"],
            "metodo_referencia":"pares O/E fixos calculados na amostra completa; bootstrap pareado por UF",
        })
    result=pd.DataFrame(rows)
    result.to_csv("RESULTADO_BOOTSTRAP_TODAS_CAUSAS_1000.csv",index=False)
    print("\nEstimativa recente:",point_new["tau"])
    print(result.to_string(index=False))
    print("\nFalhas:",failures)

if __name__=="__main__":
    main()
