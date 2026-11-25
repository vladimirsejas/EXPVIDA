"""
Projeto: Quando o territorio importa (estudo de divergencia territorial; pasta de pesquisa).
Diferencas absolutas de tau e comparacao homens x mulheres, com intervalos pelo bootstrap em BLOCOS DE UF
(27 blocos; sorteia estados inteiros, respeitando a dependencia espacial mostrada em VALIDACAO_MORAN.csv).
Grava:
  DIFERENCAS_TAU_FAIXAS.csv   por periodo: tau de cada faixa e sexo, diferenca absoluta entre faixas (homens), razao P90/P10
                              esperada, e diferenca homens - mulheres em cada faixa, com IC 95% por blocos
  DIFERENCAS_TAU_IDADES.csv   o mesmo em 18 faixas de idade individuais, 2015-2019
  FIGURA_TAU_IDADE_SEXO.png   perfil de tau por idade e sexo (2015-2019, valores reais, IC por blocos)
Como usar: "python comparacao_sexos.py". Leva cerca de 10 minutos. Semente fixa 20261124.
"""
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm
import validacao_tau as vt

B = 300
SEMENTE = vt.SEMENTE


def boot(OE, blocos, n, pool):
    pt = {k: (lambda a: (a["mu"], a["tau"]))(dm.ajustar(*v)) for k, v in OE.items()}
    rng = np.random.default_rng(SEMENTE)
    sels = []
    for _ in range(B):
        esc = rng.integers(0, len(blocos), len(blocos))
        sels.append(np.concatenate([blocos[e] for e in esc]))
    res = pool.map(vt._rep_bloco, [(s, pt) for s in sels], chunksize=10)
    return {k: v[1] for k, v in pt.items()}, {k: np.array([r[k] for r in res]) for k in OE}


def ic(v):
    return tuple(np.percentile(v, [2.5, 97.5]))


def p90p10(t):
    return math.exp(2 * dm.Z90 * t)


def principal():
    D, PY, cod = dm.carregar()
    n = len(cod)
    uf = np.array([c[:2] for c in cod])
    blocos = [np.where(uf == u)[0] for u in sorted(set(uf))]
    faixas, idades = [], []
    for per in dm.PERIODOS:
        OE = {(sx, b): dm.esperados(D[(per, sx)], PY[(per, sx)], cols) for sx in (1, 2) for b, cols in dm.BANDAS.items()}
        with Pool(2, initializer=vt._init, initargs=(OE,)) as pool:
            pt, bt = boot(OE, blocos, n, pool)
        for sx in (1, 2):
            for b in vt.NB:
                lo, hi = ic(bt[(sx, b)])
                faixas.append({"periodo": per, "medida": "tau", "sexo": dm.SEXOS[sx], "faixa": b, "estimativa": pt[(sx, b)],
                               "ic_inf": lo, "ic_sup": hi})
                faixas.append({"periodo": per, "medida": "razao_P90_P10_esperada", "sexo": dm.SEXOS[sx], "faixa": b,
                               "estimativa": p90p10(pt[(sx, b)]), "ic_inf": p90p10(lo), "ic_sup": p90p10(hi)})
        for ref in ("1-14", "30-59", "60-79"):
            d = bt[(1, "15-29")] - bt[(1, ref)]
            lo, hi = ic(d)
            faixas.append({"periodo": per, "medida": "dif_absoluta_tau_(15-29)_menos_(%s)" % ref, "sexo": "homens", "faixa": "15-29",
                           "estimativa": pt[(1, "15-29")] - pt[(1, ref)], "ic_inf": lo, "ic_sup": hi})
        for b in vt.NB:
            d = bt[(1, b)] - bt[(2, b)]
            lo, hi = ic(d)
            faixas.append({"periodo": per, "medida": "dif_tau_homens_menos_mulheres", "sexo": "H-M", "faixa": b,
                           "estimativa": pt[(1, b)] - pt[(2, b)], "ic_inf": lo, "ic_sup": hi})
            r = bt[(1, b)] / bt[(2, b)]
            lo, hi = ic(r)
            faixas.append({"periodo": per, "medida": "razao_tau_homens_sobre_mulheres", "sexo": "H/M", "faixa": b,
                           "estimativa": pt[(1, b)] / pt[(2, b)], "ic_inf": lo, "ic_sup": hi})
        print("faixas", per, flush=True)
    pd.DataFrame(faixas).to_csv(os.path.join(dm.PASTA, "DIFERENCAS_TAU_FAIXAS.csv"), sep=";", index=False, float_format="%.5g")

    # ---- 18 idades individuais, 2015-2019
    per = vt.PER
    OE = {(sx, j): dm.esperados(D[(per, sx)], PY[(per, sx)], [j]) for sx in (1, 2) for j in range(len(dm.IDADES))}
    with Pool(2, initializer=vt._init, initargs=(OE,)) as pool:
        pt, bt = boot(OE, blocos, n, pool)
    for j, rot in enumerate(dm.ROTULO):
        r = {"faixa": rot}
        for sx, ab in ((1, "H"), (2, "M")):
            lo, hi = ic(bt[(sx, j)])
            r["tau_" + ab], r["tau_%s_ic_inf" % ab], r["tau_%s_ic_sup" % ab] = pt[(sx, j)], lo, hi
        d = bt[(1, j)] - bt[(2, j)]
        lo, hi = ic(d)
        r["dif_H_menos_M"], r["dif_ic_inf"], r["dif_ic_sup"] = pt[(1, j)] - pt[(2, j)], lo, hi
        r["dif_exclui_zero"] = int(lo > 0 or hi < 0)
        idades.append(r)
    di = pd.DataFrame(idades)
    di.to_csv(os.path.join(dm.PASTA, "DIFERENCAS_TAU_IDADES.csv"), sep=";", index=False, float_format="%.5g")
    print("idades prontas", flush=True)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    x = np.arange(len(di))
    for ab, nome, cor in (("H", "Homens", "#1f5aa6"), ("M", "Mulheres", "#c4501b")):
        ax.fill_between(x, di["tau_%s_ic_inf" % ab], di["tau_%s_ic_sup" % ab], color=cor, alpha=0.18, linewidth=0)
        ax.plot(x, di["tau_" + ab], color=cor, marker="o", markersize=4, linewidth=1.8, label=nome)
    ax.set_xticks(x)
    ax.set_xticklabels(di["faixa"], rotation=45, ha="right", fontsize=8)
    ax.set_xlabel("Faixa de idade (anos)")
    ax.set_ylabel("τ (desigualdade entre microrregiões)")
    ax.set_title("Desigualdade territorial da mortalidade por idade e sexo, Brasil, 2015-2019", fontsize=10)
    ax.text(0.99, 0.02, "Faixa sombreada: IC 95% por bootstrap de estados (27 blocos). Fonte: SIM e POPSVS, 558 microrregiões.",
            transform=ax.transAxes, ha="right", fontsize=6.5, color="#555555")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(dm.PASTA, "FIGURA_TAU_IDADE_SEXO.png"))
    print("pronto")


if __name__ == "__main__":
    principal()
