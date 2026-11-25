"""
Projeto: Quando o territorio importa (clone de pesquisa; nao altera nenhum arquivo existente).
Decomposicao de Arriaga territorial: em que idades a diferenca de e0-80 de cada microrregiao para o Brasil se concentra,
usando os efeitos SUAVIZADOS do modelo Poisson-lognormal (sem o acaso de Poisson).
Para cada sexo e idade a: taxa_i(a) = taxa do resto do Brasil(a) * exp(mu + u_i), com (mu, tau, u) do modelo ajustado a idade a.
Grava ARRIAGA_TERRITORIAL.csv (por faixa) e ARRIAGA_TERRITORIAL_IDADES.csv (por idade). Periodo: 2015-2019.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm

PER = sys.argv[1] if len(sys.argv) > 1 else "2015-2019"
D, PY, cod = dm.carregar()
NG = len(dm.IDADES)
lin_idade, lin_banda = [], []
for sx in (1, 2):
    d, py = D[(PER, sx)], PY[(PER, sx)]
    ref = dm.tabua_lx(d.sum(0), py.sum(0), sx)
    ref2 = (ref[0], ref[1])
    taxa = np.zeros_like(d)
    taus = np.zeros(NG)
    for j in range(NG):
        obs, E = dm.esperados(d, py, [j])
        aj = dm.ajustar(obs, E)
        taus[j] = aj["tau"]
        u = np.nan_to_num(aj["u"])
        taxa_ref = (d[:, j].sum() - d[:, j]) / (py[:, j].sum() - py[:, j])
        taxa[:, j] = taxa_ref * np.exp(aj["mu"] + u)
    l, L = dm.tabua_vec(taxa * py, py, sx)
    c = dm.arriaga_vec(ref2, l, L)
    e0_ref = dm.e0_80(ref[0], ref[1])
    e0_i = L[:, :-1].sum(1) / l[:, 0]
    G = e0_i - e0_ref
    soma = c.sum(1)
    print(PER, dm.SEXOS[sx], "e0-80 Brasil %.2f" % e0_ref, "| max |soma contribuicoes - diferenca| = %.2e" % np.nanmax(np.abs(soma - G)),
          "| DP de e0-80 entre microrregioes %.2f ano | n nan %d" % (np.nanstd(G), int(np.isnan(G).sum())))
    for j in range(NG):
        lin_idade.append({"periodo": PER, "sexo": dm.SEXOS[sx], "idade": dm.ROTULO[j], "tau": taus[j],
                          "dp_contribuicao_anos": np.nanstd(c[:, j]), "contrib_abs_media_anos": np.nanmean(np.abs(c[:, j])),
                          "obitos_total": d[:, j].sum()})
    tot = np.nansum([np.nanmean(np.abs(c[:, j])) for j in range(NG - 1)])
    for nome, idx in dm.BANDAS.items():
        idx2 = [j for j in idx if j < NG - 1]
        if not idx2:
            continue
        cb = c[:, idx2].sum(1)
        lin_banda.append({"periodo": PER, "sexo": dm.SEXOS[sx], "banda": nome,
                          "tau_medio_das_idades": float(np.mean(taus[idx])),
                          "dp_contribuicao_anos": float(np.nanstd(cb)),
                          "contrib_abs_media_anos": float(np.nanmean(np.abs(cb))),
                          "parte_da_variancia_de_e0": float(np.nansum(np.nanvar(cb) * 0 + np.nanmean((cb - np.nanmean(cb)) * (G - np.nanmean(G)))) / np.nanvar(G)),
                          "obitos_total": float(d[:, idx].sum())})
a = pd.DataFrame(lin_idade)
b = pd.DataFrame(lin_banda)
a.to_csv(os.path.join(dm.PASTA, "ARRIAGA_TERRITORIAL_IDADES.csv"), sep=";", index=False)
b.to_csv(os.path.join(dm.PASTA, "ARRIAGA_TERRITORIAL.csv"), sep=";", index=False)
pd.set_option("display.width", 200)
print(b.round(3).to_string())
