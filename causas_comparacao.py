"""
Projeto: Quando o territorio importa (estudo 2, causas de morte; pasta de pesquisa, separado do EXPVIDA principal).
Comparacao dirigida de tau entre grupos de causa e a mortalidade geral, com IC 95% por bootstrap em BLOCOS DE UF
(300 sorteios, os MESMOS estados em todos os grupos, o que da intervalo proprio as diferencas) e estabilidade por
retirada de cada UF (27 reajustes). Grupos agregados (somas de grupos mutuamente exclusivos de causas_sim.py):
  violencia_ampliada = agressoes + intencao_indeterminada + intervencao_legal   (essas tres se confundem no registro)
  externas_total     = todas as causas externas (V01-Y98)
  nao_externas       = todas as demais
Grava CAUSAS_COMPARACAO.csv. Como usar: "python causas_comparacao.py". Semente fixa.
"""
import os, sys
from multiprocessing import Pool
import numpy as np, pandas as pd
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm
import validacao_tau as vt
import causas_tau as ct

B = 300
EXT = ["agressoes", "intervencao_legal", "suicidio", "transporte", "intencao_indeterminada", "acidentes_outros", "externas_outras"]
VIOL = ["agressoes", "intencao_indeterminada", "intervencao_legal"]
CELULAS = {("homens", "15-29"): ["agressoes", "transporte", "suicidio", "acidentes_outros", "intencao_indeterminada", "intervencao_legal",
                                  "violencia_ampliada", "externas_total", "nao_externas", "todas"],
           ("homens", "15-19"): ["agressoes", "transporte", "suicidio", "violencia_ampliada", "externas_total", "nao_externas", "todas"],
           ("mulheres", "1-14"): ["infecciosas", "endocrinas_nutricionais", "respiratorias", "congenitas", "mal_definidas", "perinatais", "transporte",
                                  "acidentes_outros", "externas_total", "nao_externas", "todas"],
           ("mulheres", "1-4"): ["infecciosas", "endocrinas_nutricionais", "respiratorias", "congenitas", "mal_definidas", "transporte",
                                 "acidentes_outros", "externas_total", "nao_externas", "todas"],
           ("homens", "1-14"): ["infecciosas", "endocrinas_nutricionais", "respiratorias", "congenitas", "mal_definidas", "transporte",
                                "acidentes_outros", "externas_total", "nao_externas", "todas"]}
FX = {"1-14": [1, 2, 3], "1-4": [1], "15-19": [4], "15-29": [4, 5, 6]}


def matriz(df, cod, sx, g):
    if g == "todas":
        return ct.matriz_causa(df, cod, sx, None)
    if g == "violencia_ampliada":
        return sum(ct.matriz_causa(df, cod, sx, c) for c in VIOL)
    if g == "externas_total":
        return sum(ct.matriz_causa(df, cod, sx, c) for c in EXT)
    if g == "nao_externas":
        return ct.matriz_causa(df, cod, sx, None) - matriz(df, cod, sx, "externas_total")
    return ct.matriz_causa(df, cod, sx, g)


def main():
    df = pd.read_csv(os.path.join(ct.P, "CAUSAS_OBITOS_2015_2019.csv"), sep=";", dtype={"microrregiao": str})
    D, PY, cod = dm.carregar()
    sxn = {"homens": 1, "mulheres": 2}
    OE, nob = {}, {}
    for (sx, fx), gs in CELULAS.items():
        for g in gs:
            M = matriz(df, cod, sxn[sx], g)
            OE[(sx, fx, g)] = dm.esperados(M, PY[(ct.PER, sxn[sx])], FX[fx])
            nob[(sx, fx, g)] = (M[:, FX[fx]].sum(), int((M[:, FX[fx]].sum(1) == 0).sum()))
    pt = {k: (lambda a: (a["mu"], a["tau"]))(dm.ajustar(*v)) for k, v in OE.items()}
    uf = np.array([c[:2] for c in cod])
    ufs = sorted(set(uf))
    blocos = [np.where(uf == u)[0] for u in ufs]
    rng = np.random.default_rng(vt.SEMENTE)
    sels = [np.concatenate([blocos[e] for e in rng.integers(0, len(blocos), len(blocos))]) for _ in range(B)]
    loo = [np.where(uf != u)[0] for u in ufs]
    with Pool(2, initializer=vt._init, initargs=(OE,)) as pool:
        res = pool.map(vt._rep_bloco, [(s, pt) for s in sels], chunksize=10)
        rl = pool.map(vt._rep_bloco, [(s, pt) for s in loo], chunksize=3)
    bt = {k: np.array([r[k] for r in res]) for k in OE}
    lt = {k: np.array([r[k] for r in rl]) for k in OE}
    linhas = []
    for (sx, fx), gs in CELULAS.items():
        for g in gs:
            k = (sx, fx, g)
            lo, hi = np.percentile(bt[k], [2.5, 97.5])
            kt = (sx, fx, "todas")
            d = bt[k] - bt[kt]
            dl, dh = np.percentile(d, [2.5, 97.5])
            linhas.append(dict(sexo=sx, faixa=fx, grupo=g, obitos=int(nob[k][0]), microrregioes_sem_obito=nob[k][1], tau=pt[k][1], ic_inf=lo, ic_sup=hi,
                               dif_vs_todas=pt[k][1] - pt[kt][1], dif_ic_inf=dl, dif_ic_sup=dh,
                               tau_sem_cada_UF_min=lt[k].min(), tau_sem_cada_UF_max=lt[k].max(), tau_no_limite_inferior=int(pt[k][1] < 0.01)))
    out = pd.DataFrame(linhas)
    out.to_csv(os.path.join(ct.P, "CAUSAS_COMPARACAO.csv"), sep=";", index=False)
    # diferencas entre grupos de causa externa
    dif = []
    for (sx, fx), gs in CELULAS.items():
        for a, b in (("agressoes", "transporte"), ("agressoes", "suicidio"), ("violencia_ampliada", "transporte"), ("transporte", "suicidio"), ("violencia_ampliada", "suicidio")):
            if a in gs and b in gs:
                d = bt[(sx, fx, a)] - bt[(sx, fx, b)]
                est = pt[(sx, fx, a)][1] - pt[(sx, fx, b)][1]
                lo, hi = np.percentile(d, [2.5, 97.5])
                dif.append(dict(sexo=sx, faixa=fx, grupo=a + " menos " + b, estimativa=est, ic_inf=lo, ic_sup=hi))
    pd.DataFrame(dif).to_csv(os.path.join(ct.P, "CAUSAS_COMPARACAO_EXTERNAS.csv"), sep=";", index=False)
    print("pronto")


if __name__ == "__main__":
    main()
