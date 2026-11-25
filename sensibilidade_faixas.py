"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
SENSIBILIDADE DAS HIPOTESES H2 E H3 A OUTRAS DEFINICOES DE FAIXAS DE IDADE, E CORRECAO DE MULTIPLOS TESTES.

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva cerca de 4 minutos.
Precisa de numpy, scipy e pandas. Le so os CSV da pasta; nao baixa nada, nao cria pastas.

Por que existe: as faixas agrupadas de testes_hipoteses.py (0 | 1-14 | 15-29 | 30-59 | 60-79 | 80+) foram
escolhidas por mim antes de rodar, mas nao foram registradas em lugar nenhum como pre-especificacao, e uma
conclusao que depende de onde se cortam as idades e fragil. Aqui H2 e H3 sao refeitas, so em 2015-2019 (periodo
principal), com dois outros agrupamentos (bootstrap de 300 microrregioes, mesma semente), e o resultado e
comparado com o original.
  Agrupamento B: 0 | 1-9 | 10-24 | 25-44 | 45-64 | 65-79 | 80+      (H2: 10-24 contra 1-9 e contra 25-44)
  Agrupamento C: 0 | 1-14 | 15-24 | 25-34 | 35-59 | 60-79 | 80+     (H2: 15-24 contra 1-14 e contra 25-34)
Tambem aplica a correcao de Holm (controle do erro de tipo I familiar) aos 30 valores p de TESTES_HIPOTESES.csv
(H1a, H2 e H3 em seis periodos), com valores p analiticos ou normais, e nao os do bootstrap, que tem resolucao de 1/B.
Grava: SENSIBILIDADE_FAIXAS.csv e TESTES_HIPOTESES_HOLM.csv (separador ponto e virgula).
"""
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm

SEMENTE = 20261124
B = 300
PERIODO = "2015-2019"
CONJUNTOS = {
    "B": ({"0": [0], "1-9": [1, 2], "10-24": [3, 4, 5], "25-44": [6, 7, 8, 9], "45-64": [10, 11, 12, 13],
           "65-79": [14, 15, 16], "80+": [17]}, "10-24", "1-9", "25-44"),
    "C": ({"0": [0], "1-14": [1, 2, 3], "15-24": [4, 5], "25-34": [6, 7], "35-59": [8, 9, 10, 11, 12],
           "60-79": [13, 14, 15, 16], "80+": [17]}, "15-24", "1-14", "25-34"),
}


def ic(v):
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def principal():
    D, PY, cod = dm.carregar()
    n = len(cod)
    linhas = []
    for nome, (bandas, jovem, antes, depois) in CONJUNTOS.items():
        rng = np.random.default_rng(SEMENTE)
        nomes = list(bandas.keys())
        OE = {(sx, b): dm.esperados(D[(PERIODO, sx)], PY[(PERIODO, sx)], cols) for sx in (1, 2) for b, cols in bandas.items()}
        pt = {k: dm.ajustar(*v) for k, v in OE.items()}
        boot = {k: np.zeros(B) for k in OE}
        for r in range(B):
            sel = rng.integers(0, n, n)
            for k, (O, E) in OE.items():
                boot[k][r] = dm.ajustar(O[sel], E[sel], inicio=(pt[k]["mu"], math.log(pt[k]["tau"])))["tau"]
        for sx in (1, 2):
            for b in nomes:
                lo, hi = ic(boot[(sx, b)])
                linhas.append({"agrupamento": nome, "hipotese": "tau_por_faixa", "sexo": dm.SEXOS[sx], "descricao": b,
                               "estimativa": pt[(sx, b)]["tau"], "ic_inf": lo, "ic_sup": hi, "p": float("nan")})
        for ref in (antes, depois):
            razao = boot[(1, jovem)] / boot[(1, ref)]
            lo, hi = ic(razao)
            linhas.append({"agrupamento": nome, "hipotese": "H2", "sexo": "homens",
                           "descricao": "tau(%s)/tau(%s)" % (jovem, ref),
                           "estimativa": pt[(1, jovem)]["tau"] / pt[(1, ref)]["tau"], "ic_inf": lo, "ic_sup": hi,
                           "p": float(min(1.0, 2 * min((razao <= 1).mean(), (razao >= 1).mean())))})
        L = np.array([[math.log(boot[(1, b)][r]) - math.log(boot[(2, b)][r]) for b in nomes] for r in range(B)])
        d_est = np.array([math.log(pt[(1, b)]["tau"]) - math.log(pt[(2, b)]["tau"]) for b in nomes])
        C = np.zeros((len(nomes) - 1, len(nomes)))
        for i in range(len(nomes) - 1):
            C[i, 0], C[i, i + 1] = -1.0, 1.0
        cest = C @ d_est
        S = np.cov((L @ C.T).T)
        wald = float(cest @ np.linalg.solve(S, cest))
        pm = nomes[int(np.argmax([pt[(1, b)]["tau"] for b in nomes]))]
        pf = nomes[int(np.argmax([pt[(2, b)]["tau"] for b in nomes]))]
        linhas.append({"agrupamento": nome, "hipotese": "H3", "sexo": "homens vs mulheres",
                       "descricao": "Wald paralelismo (%d gl) = %.1f; pico homens=%s; pico mulheres=%s" % (len(cest), wald, pm, pf),
                       "estimativa": wald, "ic_inf": float("nan"), "ic_sup": float("nan"),
                       "p": float(stats.chi2.sf(wald, len(cest)))})
        print("agrupamento pronto:", nome, flush=True)
    pd.DataFrame(linhas).to_csv(os.path.join(dm.PASTA, "SENSIBILIDADE_FAIXAS.csv"), sep=";", index=False, float_format="%.5g")

    # ---- Holm sobre todos os testes com valor p de TESTES_HIPOTESES.csv (30 testes: 6 periodos x 5)
    # Valores p usados: H1a = razao de verossimilhanca (analitico); H3 = Wald (analitico); H2 = aproximacao normal do
    # logaritmo da razao, com erro-padrao tirado da largura do IC de bootstrap (o p do bootstrap com 300 repeticoes
    # nao passa de 1/300 e tornaria a correcao artificialmente rigida). Valores abaixo de 1e-300 sao tratados como 1e-300.
    t = pd.read_csv(os.path.join(dm.PASTA, "TESTES_HIPOTESES.csv"), sep=";")
    t = t[t.hipotese.isin(["H1a", "H2", "H3"])].copy()
    pv = []
    for _, r in t.iterrows():
        if r.hipotese == "H2":
            dp = (math.log(r.ic_sup) - math.log(r.ic_inf)) / (2 * 1.959964)
            pv.append(float(2 * stats.norm.sf(abs(math.log(r.estimativa)) / dp)))
        else:
            pv.append(float(r.p))
    t["p_usado"] = np.maximum(np.array(pv), 1e-300)
    ordem = np.argsort(t.p_usado.to_numpy())
    m = len(t)
    aj = np.empty(m)
    maximo = 0.0
    for rank, i in enumerate(ordem):
        maximo = max(maximo, min(1.0, (m - rank) * t.p_usado.to_numpy()[i]))
        aj[i] = maximo
    t["p_holm"] = aj
    t["sobrevive_a_holm_5pct"] = (t.p_holm < 0.05).astype(int)
    t.drop(columns=["estatistica", "p"]).to_csv(os.path.join(dm.PASTA, "TESTES_HIPOTESES_HOLM.csv"), sep=";", index=False,
                                                float_format="%.5g")
    print("pronto: SENSIBILIDADE_FAIXAS.csv, TESTES_HIPOTESES_HOLM.csv")


if __name__ == "__main__":
    principal()
