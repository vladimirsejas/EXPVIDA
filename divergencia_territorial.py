"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
DIVERGENCIA TERRITORIAL POR IDADE: em que idades as microrregioes se afastam da referencia nacional,
separado por sexo e periodo, com incerteza, estabilidade entre periodos e sensibilidade.

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva poucos minutos.
Precisa de numpy, scipy e pandas. Le so os CSV que ja estao na pasta; nao baixa nada, nao cria pastas.

O que faz (detalhes do modelo em divergencia_modelo.py):
  1. Para cada sexo, periodo e faixa de idade, estima tau = desvio-padrao, entre as 558 microrregioes, do
     log da razao de risco real (taxa da microrregiao / taxa do resto do Brasil), separando o acaso de
     Poisson da diferenca verdadeira. Da tambem o IC 95% de tau (verossimilhanca de perfil), o teste de
     tau = 0 e a razao P90/P10 esperada. Compara com a razao P90/P10 observada no estilo do BRASIL_RESUMO.
  2. Estabilidade: correlacao, entre periodos, das diferencas estimadas de cada microrregiao.
  3. Sensibilidade: (a) erro hipotetico na populacao estimada, (b) sem as microrregioes pequenas,
     (c) com a UF como unidade em vez da microrregiao.
Grava: DIVERGENCIA_POR_IDADE.csv, DIVERGENCIA_ESTABILIDADE.csv, DIVERGENCIA_SENSIBILIDADE.csv
(separador ponto e virgula, como os demais CSV do projeto).
"""
import math
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm

ERROS_POPULACAO = (0.02, 0.05)      # erro relativo hipotetico (desvio-padrao) da populacao estimada, por microrregiao
MIN_OBITOS_GRANDE = 500             # "microrregiao grande" na analise de sensibilidade (obitos no sexo e periodo)


def principal():
    D, PY, cod = dm.carregar()
    linhas, fits = [], {}
    for per in dm.PERIODOS:
        for sx in (1, 2):
            d, py = D[(per, sx)], PY[(per, sx)]
            obs = dm.p90_p10_observada(d, py)
            for j, rot in enumerate(dm.ROTULO):
                O, E = dm.esperados(d, py, [j])
                a = dm.ajustar(O, E)
                lo, hi = dm.intervalo_perfil(O, E, a)
                fits[(per, sx, j)] = a
                linhas.append({
                    "periodo": per, "sexo": dm.SEXOS[sx], "idade": rot, "microrregioes": a["n"],
                    "obitos": int(O.sum()), "tau": a["tau"], "tau_ic_inf": lo, "tau_ic_sup": hi,
                    "razao_p90_p10_esperada": math.exp(2 * dm.Z90 * a["tau"]),
                    "razao_p90_p10_observada_repo": obs[j][1], "microrregioes_com_20_obitos": obs[j][0],
                    "lrt_tau0": a["lrt"], "p_tau0": a["p"],
                })
        print("periodo pronto:", per, flush=True)
    tab = pd.DataFrame(linhas)
    tab.to_csv(os.path.join(dm.PASTA, "DIVERGENCIA_POR_IDADE.csv"), sep=";", index=False, float_format="%.5g")

    # ---- estabilidade entre periodos (correlacao das diferencas estimadas das microrregioes)
    pares = [("2010-2014", "2015-2019"), ("2015-2019", "2022-2024"), ("2000-2004", "2015-2019")]
    est = []
    for p1, p2 in pares:
        for sx in (1, 2):
            for j, rot in enumerate(dm.ROTULO):
                u1, u2 = fits[(p1, sx, j)]["u"], fits[(p2, sx, j)]["u"]
                m = ~np.isnan(u1) & ~np.isnan(u2)
                est.append({"periodo_1": p1, "periodo_2": p2, "sexo": dm.SEXOS[sx], "idade": rot,
                            "correlacao_pearson": float(np.corrcoef(u1[m], u2[m])[0, 1]),
                            "correlacao_spearman": float(pd.Series(u1[m]).corr(pd.Series(u2[m]), method="spearman"))})
    pd.DataFrame(est).to_csv(os.path.join(dm.PASTA, "DIVERGENCIA_ESTABILIDADE.csv"), sep=";", index=False,
                             float_format="%.4g")

    # ---- sensibilidade
    sens = []
    Du, PYu, cod_uf = dm.carregar("uf")
    for per in dm.PERIODOS:
        for sx in (1, 2):
            d, py = D[(per, sx)], PY[(per, sx)]
            grande = d.sum(1) >= MIN_OBITOS_GRANDE
            for j, rot in enumerate(dm.ROTULO):
                a = fits[(per, sx, j)]
                O, E = dm.esperados(d, py, [j])
                linha = {"periodo": per, "sexo": dm.SEXOS[sx], "idade": rot, "tau_base": a["tau"]}
                for s_pop in ERROS_POPULACAO:
                    linha["tau_se_erro_pop_%d_por_cento" % round(100 * s_pop)] = math.sqrt(max(a["tau"] ** 2 - s_pop ** 2, 0.0))
                ag = dm.ajustar(O[grande], E[grande])
                linha["tau_so_microrregioes_grandes"] = ag["tau"]
                linha["n_microrregioes_grandes"] = int(grande.sum())
                Ou, Eu = dm.esperados(Du[(per, sx)], PYu[(per, sx)], [j])
                au = dm.ajustar(Ou, Eu)
                linha["tau_unidade_uf"] = au["tau"]
                sens.append(linha)
    pd.DataFrame(sens).to_csv(os.path.join(dm.PASTA, "DIVERGENCIA_SENSIBILIDADE.csv"), sep=";", index=False,
                              float_format="%.5g")
    print("pronto: DIVERGENCIA_POR_IDADE.csv, DIVERGENCIA_ESTABILIDADE.csv, DIVERGENCIA_SENSIBILIDADE.csv")


if __name__ == "__main__":
    principal()
