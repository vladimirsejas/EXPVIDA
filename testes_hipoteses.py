"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
TESTES FORMAIS DAS TRES HIPOTESES do DESENHO_METODOLOGICO.md.

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva cerca de 5 a 10 minutos.
Precisa de numpy, scipy e pandas. Le so os CSV que ja estao na pasta; nao baixa nada, nao cria pastas.

Medida de desigualdade: tau = desvio-padrao, entre as 558 microrregioes, do log da razao de risco real
(taxa da microrregiao / taxa do resto do Brasil, ja padronizada por idade dentro da faixa), estimado por
modelo Poisson-lognormal que separa o acaso do Poisson da diferenca verdadeira (ver divergencia_modelo.py).
As idades sao agrupadas em seis faixas para dar mais obitos a cada estimativa:
0 | 1-14 | 15-29 | 30-59 | 60-79 | 80+.

Hipoteses (como escritas no desenho metodologico) e como cada uma e testada:
  H1  Parte da desigualdade territorial ja esta presente no primeiro ano de vida.
      (a) tau da faixa 0 maior que zero (teste de razao de verossimilhanca, p com mistura 0,5*qui-quadrado);
      (b) participacao da faixa 0 na variancia entre microrregioes da expectativa de vida e0-80
          (decomposicao de Arriaga + decomposicao da covariancia), com IC por bootstrap de microrregioes.
      Sustentada se (a) vale em todos os periodos e sexos e (b) tem IC 95% acima de zero.
  H2  A desigualdade cresce na idade adulta jovem entre os homens.
      Compara tau dos homens em 15-29 com tau em 1-14 (antes) e em 30-59 (depois). Sustentada se as duas
      razoes tem IC 95% (bootstrap de microrregioes) acima de 1.
  H3  O padrao por idade difere entre homens e mulheres.
      Teste de Wald, com covariancia por bootstrap pareado, de que a diferenca entre sexos em log(tau) e
      a mesma nas seis faixas (perfis paralelos). Tambem: faixa de maior tau em cada sexo e a probabilidade,
      no bootstrap, de coincidirem. Sustentada se p < 0,05.
O bootstrap sorteia microrregioes com reposicao (as mesmas nos dois sexos e em todas as faixas), 1000 vezes
em 2015-2019 (periodo principal, antes da pandemia) e 300 nos demais. Semente fixa.

Grava: TESTES_HIPOTESES_TAU_FAIXAS.csv, TESTES_HIPOTESES.csv e TESTES_H1_PARTICIPACAO_E0_80.csv.
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
B_PRINCIPAL, B_OUTROS = 1000, 300
PERIODO_PRINCIPAL = "2015-2019"
MIN_OBITOS_E0 = 500          # microrregioes com ao menos isso de obitos no sexo e periodo entram na decomposicao de e0-80
NOMES_BANDAS = list(dm.BANDAS.keys())


def ic(v, nivel=0.95):
    a = (1 - nivel) / 2
    return float(np.nanpercentile(v, 100 * a)), float(np.nanpercentile(v, 100 * (1 - a)))


def participacao_e0_80(D, PY, sx, periodo):
    """Participacao de cada idade na variancia entre microrregioes de e0-80 (exata: cov(c_a, soma)/var(soma))."""
    d, py = D[(periodo, sx)], PY[(periodo, sx)]
    tb = dm.tabua_lx(d.sum(0), py.sum(0), sx)
    contrib, gaps, idx = [], [], []
    for i in range(d.shape[0]):
        if d[i].sum() < MIN_OBITOS_E0:
            continue
        ti = dm.tabua_lx(d[i], py[i], sx)
        if ti is None:
            continue
        c = dm.arriaga_e0_80(tb, ti)
        contrib.append(c)
        idx.append(i)
    return np.array(contrib), np.array(idx)


def participacoes(contrib):
    soma = contrib.sum(1)
    v = soma.var(ddof=1)
    return np.array([np.cov(contrib[:, a], soma, ddof=1)[0, 1] / v for a in range(contrib.shape[1])])


def agrupar_part(p):
    return {nome: float(p[cols].sum()) for nome, cols in dm.BANDAS.items()}


def principal():
    D, PY, cod = dm.carregar()
    rng = np.random.default_rng(SEMENTE)
    n = len(cod)
    linhas_tau, linhas_teste, linhas_h1 = [], [], []

    for per in dm.PERIODOS:
        B = B_PRINCIPAL if per == PERIODO_PRINCIPAL else B_OUTROS
        OE = {(sx, b): dm.esperados(D[(per, sx)], PY[(per, sx)], cols)
              for sx in (1, 2) for b, cols in dm.BANDAS.items()}
        pt = {k: dm.ajustar(*v) for k, v in OE.items()}
        # ---- bootstrap pareado de microrregioes
        boot = {k: np.zeros(B) for k in OE}
        pico_m = np.zeros(B, dtype=int)
        pico_f = np.zeros(B, dtype=int)
        for r in range(B):
            sel = rng.integers(0, n, n)
            for k, (O, E) in OE.items():
                a = dm.ajustar(O[sel], E[sel], inicio=(pt[k]["mu"], math.log(pt[k]["tau"])))
                boot[k][r] = a["tau"]
            pico_m[r] = int(np.argmax([boot[(1, b)][r] for b in NOMES_BANDAS]))
            pico_f[r] = int(np.argmax([boot[(2, b)][r] for b in NOMES_BANDAS]))
        # ---- tau por faixa
        for (sx, b), a in pt.items():
            lo, hi = ic(boot[(sx, b)])
            linhas_tau.append({"periodo": per, "sexo": dm.SEXOS[sx], "faixa": b, "obitos": int(OE[(sx, b)][0].sum()),
                               "tau": a["tau"], "tau_ic_inf_bootstrap": lo, "tau_ic_sup_bootstrap": hi,
                               "lrt_tau0": a["lrt"], "p_tau0": a["p"], "razao_p90_p10_esperada": math.exp(2 * dm.Z90 * a["tau"])})
        # ---- H1 (a): tau da faixa 0 > 0
        for sx in (1, 2):
            a = pt[(sx, "0")]
            linhas_teste.append({"periodo": per, "hipotese": "H1a", "sexo": dm.SEXOS[sx],
                                 "descricao": "tau da faixa 0 maior que zero (razao de verossimilhanca)",
                                 "estatistica": a["lrt"], "estimativa": a["tau"], "ic_inf": ic(boot[(sx, "0")])[0],
                                 "ic_sup": ic(boot[(sx, "0")])[1], "p": a["p"], "sustentada": int(a["p"] < 0.05)})
        # ---- H1 (b): participacao da faixa 0 na variancia de e0-80
        for sx in (1, 2):
            contrib, idx = participacao_e0_80(D, PY, sx, per)
            part = agrupar_part(participacoes(contrib))
            bt = {b: [] for b in NOMES_BANDAS}
            for r in range(B):
                s2 = rng.integers(0, len(idx), len(idx))
                pb = agrupar_part(participacoes(contrib[s2]))
                for b in NOMES_BANDAS:
                    bt[b].append(pb[b])
            for b in NOMES_BANDAS:
                lo, hi = ic(bt[b])
                linhas_h1.append({"periodo": per, "sexo": dm.SEXOS[sx], "faixa": b, "microrregioes": len(idx),
                                  "participacao_na_variancia_e0_80": part[b], "ic_inf": lo, "ic_sup": hi})
            lo, hi = ic(bt["0"])
            linhas_teste.append({"periodo": per, "hipotese": "H1b", "sexo": dm.SEXOS[sx],
                                 "descricao": "participacao da faixa 0 na variancia entre microrregioes de e0-80 (IC acima de zero)",
                                 "estatistica": float("nan"), "estimativa": part["0"], "ic_inf": lo, "ic_sup": hi,
                                 "p": float("nan"), "sustentada": int(lo > 0)})
        # ---- H2: homens, 15-29 contra 1-14 e contra 30-59
        for ref in ("1-14", "30-59"):
            razao = boot[(1, "15-29")] / boot[(1, ref)]
            est = pt[(1, "15-29")]["tau"] / pt[(1, ref)]["tau"]
            lo, hi = ic(razao)
            p = float(min(1.0, 2 * min((razao <= 1).mean(), (razao >= 1).mean())))
            linhas_teste.append({"periodo": per, "hipotese": "H2", "sexo": "homens",
                                 "descricao": "razao tau(15-29) / tau(%s) maior que 1" % ref, "estatistica": float("nan"),
                                 "estimativa": est, "ic_inf": lo, "ic_sup": hi, "p": p, "sustentada": int(lo > 1)})
        # ---- H3: perfis paralelos entre os sexos
        L = np.array([[math.log(boot[(1, b)][r]) - math.log(boot[(2, b)][r]) for b in NOMES_BANDAS] for r in range(B)])
        d_est = np.array([math.log(pt[(1, b)]["tau"]) - math.log(pt[(2, b)]["tau"]) for b in NOMES_BANDAS])
        C = np.zeros((len(NOMES_BANDAS) - 1, len(NOMES_BANDAS)))
        for i in range(len(NOMES_BANDAS) - 1):
            C[i, 0], C[i, i + 1] = -1.0, 1.0
        cest = C @ d_est
        S = np.cov((L @ C.T).T)
        wald = float(cest @ np.linalg.solve(S, cest))
        p3 = float(stats.chi2.sf(wald, len(cest)))
        pm = NOMES_BANDAS[int(np.argmax([pt[(1, b)]["tau"] for b in NOMES_BANDAS]))]
        pf = NOMES_BANDAS[int(np.argmax([pt[(2, b)]["tau"] for b in NOMES_BANDAS]))]
        coincide = float((pico_m == pico_f).mean())
        linhas_teste.append({"periodo": per, "hipotese": "H3", "sexo": "homens vs mulheres",
                             "descricao": "perfis de log(tau) paralelos entre os sexos (Wald, %d gl); pico homens=%s, pico mulheres=%s; "
                                          "prob. no bootstrap de o pico coincidir=%.3f" % (len(cest), pm, pf, coincide),
                             "estatistica": wald, "estimativa": float("nan"), "ic_inf": float("nan"),
                             "ic_sup": float("nan"), "p": p3, "sustentada": int(p3 < 0.05)})
        print("periodo pronto:", per, "(bootstrap %d)" % B, flush=True)

    pd.DataFrame(linhas_tau).to_csv(os.path.join(dm.PASTA, "TESTES_HIPOTESES_TAU_FAIXAS.csv"), sep=";", index=False,
                                    float_format="%.5g")
    pd.DataFrame(linhas_teste).to_csv(os.path.join(dm.PASTA, "TESTES_HIPOTESES.csv"), sep=";", index=False,
                                      float_format="%.5g")
    pd.DataFrame(linhas_h1).to_csv(os.path.join(dm.PASTA, "TESTES_H1_PARTICIPACAO_E0_80.csv"), sep=";", index=False,
                                   float_format="%.5g")
    print("pronto: TESTES_HIPOTESES.csv, TESTES_HIPOTESES_TAU_FAIXAS.csv, TESTES_H1_PARTICIPACAO_E0_80.csv")


if __name__ == "__main__":
    principal()
