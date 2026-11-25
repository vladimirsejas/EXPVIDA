"""
Projeto: Quando o territorio importa (estudo de divergencia territorial; pasta de pesquisa).
Analise secundaria da pandemia: mudanca de tau por faixa e sexo em 2020-2021 e 2022-2024 em relacao a 2015-2019,
com bootstrap em BLOCOS DE UF (27 estados), usando OS MESMOS estados sorteados em todos os periodos
(assim a diferenca entre periodos tem intervalo proprio). Tambem a mudanca na razao H2 e na diferenca homens-mulheres.
Grava PANDEMIA_MUDANCA_TAU.csv. Como usar: "python pandemia_tau.py". Semente fixa.
"""
import math, os, sys
from multiprocessing import Pool
import numpy as np, pandas as pd
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm
import validacao_tau as vt

B = 300
BASE, ALVOS = "2015-2019", ["2020-2021 pandemia", "2022-2024"]


def main():
    D, PY, cod = dm.carregar()
    uf = np.array([c[:2] for c in cod])
    blocos = [np.where(uf == u)[0] for u in sorted(set(uf))]
    pers = [BASE] + ALVOS
    OE = {(p, sx, b): dm.esperados(D[(p, sx)], PY[(p, sx)], cols) for p in pers for sx in (1, 2) for b, cols in dm.BANDAS.items()}
    pt = {k: (lambda a: (a["mu"], a["tau"]))(dm.ajustar(*v)) for k, v in OE.items()}
    rng = np.random.default_rng(vt.SEMENTE)
    sels = [np.concatenate([blocos[e] for e in rng.integers(0, len(blocos), len(blocos))]) for _ in range(B)]
    with Pool(2, initializer=vt._init, initargs=(OE,)) as pool:
        res = pool.map(vt._rep_bloco, [(s, pt) for s in sels], chunksize=10)
    bt = {k: np.array([r[k] for r in res]) for k in OE}
    est = {k: v[1] for k, v in pt.items()}
    linhas = []

    def add(per, medida, sexo, faixa, f):
        e = f(est)
        v = np.array([f({k: bt[k][i] for k in OE}) for i in range(B)])
        lo, hi = np.percentile(v, [2.5, 97.5])
        linhas.append(dict(periodo=per, medida=medida, sexo=sexo, faixa=faixa, estimativa=e, ic_inf=lo, ic_sup=hi))

    nome = {1: "homens", 2: "mulheres"}
    for a in ALVOS:
        for sx in (1, 2):
            for b in vt.NB:
                add(a, "razao_tau_vs_2015-19", nome[sx], b, lambda t, a=a, sx=sx, b=b: t[(a, sx, b)] / t[(BASE, sx, b)])
                add(a, "dif_tau_vs_2015-19", nome[sx], b, lambda t, a=a, sx=sx, b=b: t[(a, sx, b)] - t[(BASE, sx, b)])
        for c in ("1-14", "30-59"):
            add(a, "mudanca_H2_15-29_sobre_" + c, "homens", "", lambda t, a=a, c=c: t[(a, 1, "15-29")] / t[(a, 1, c)] - t[(BASE, 1, "15-29")] / t[(BASE, 1, c)])
        for b in vt.NB:
            add(a, "mudanca_dif_HM", "homens-mulheres", b, lambda t, a=a, b=b: (t[(a, 1, b)] - t[(a, 2, b)]) - (t[(BASE, 1, b)] - t[(BASE, 2, b)]))
    vt.saida("PANDEMIA_MUDANCA_TAU.csv", pd.DataFrame(linhas))


if __name__ == "__main__":
    main()
