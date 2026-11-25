"""
Projeto: Quando o territorio importa (estudo 2, causas de morte; pasta de pesquisa, separado do EXPVIDA principal).
Evolucao de tau das agressoes e da mortalidade geral nos seis periodos (homens; faixas 15-29 e 15-19), com IC 95% por
bootstrap em BLOCOS DE UF (300 sorteios; os MESMOS estados em todos os periodos e grupos, o que da intervalo proprio as
diferencas entre periodos). Usa CAUSAS_OBITOS_2015_2019.csv e CAUSAS_OBITOS_OUTROS_PERIODOS.csv (causas_sim.py e causas_sim_periodos.py).
Grupos: agressoes; violencia_ampliada (agressoes + intencao indeterminada + intervencao legal); transporte; suicidio; externas_total;
nao_externas; mal_definidas (indicador de qualidade do registro); todas.
Grava CAUSAS_TEMPORAL.csv (uma linha por periodo, faixa e grupo: obitos, participacao nos obitos, tau, IC, diferenca em relacao a
2000-2004 com IC, correlacao dos efeitos com os da mortalidade geral) e CAUSAS_TEMPORAL_3059_CONF.csv.
Como usar: "python causas_temporal.py".
"""
import os, sys
from multiprocessing import Pool
import numpy as np, pandas as pd
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm
import validacao_tau as vt
import causas_tau as ct
import causas_comparacao as cc

B = 300
FX = {"30-59": [7, 8, 9, 10, 11, 12]}
GRUPOS = ["circulatorias", "neoplasias", "infecciosas", "respiratorias", "digestivas", "endocrinas_nutricionais", "agressoes", "transporte", "suicidio", "externas_total", "nao_externas", "mal_definidas", "todas"]
BASE = "2000-2004"


def main():
    a = pd.read_csv(os.path.join(ct.P, "CAUSAS_OBITOS_2015_2019.csv"), sep=";", dtype={"microrregiao": str}); a.insert(0, "periodo", "2015-2019")
    b = pd.read_csv(os.path.join(ct.P, "CAUSAS_OBITOS_OUTROS_PERIODOS.csv"), sep=";", dtype={"microrregiao": str})
    df = pd.concat([a, b], ignore_index=True)
    D, PY, cod = dm.carregar()
    conf, OE, nob, M15 = [], {}, {}, {}
    for per in dm.PERIODOS:
        d = df[df.periodo == per]
        tot = cc.matriz(d, cod, 1, "todas")
        conf.append(dict(periodo=per, obitos_expvida=D[(per, 1)].sum(), obitos_causas=tot.sum(), diferenca=tot.sum() - D[(per, 1)].sum(),
                         maior_dif_microrregiao_idade=np.abs(tot - D[(per, 1)]).max()))
        for g in GRUPOS:
            M = cc.matriz(d, cod, 1, g)
            for fx, cols in FX.items():
                OE[(per, fx, g)] = dm.esperados(M, PY[(per, 1)], cols)
                nob[(per, fx, g)] = (M[:, cols].sum(), int((M[:, cols].sum(1) == 0).sum()), tot[:, cols].sum())
    pd.DataFrame(conf).to_csv(os.path.join(ct.P, "CAUSAS_TEMPORAL_3059_CONF.csv"), sep=";", index=False)
    print(pd.DataFrame(conf).to_string(index=False))
    pt = {k: (lambda r: (r["mu"], r["tau"], r["u"]))(dm.ajustar(*v)) for k, v in OE.items()}
    uf = np.array([c[:2] for c in cod])
    blocos = [np.where(uf == u)[0] for u in sorted(set(uf))]
    rng = np.random.default_rng(vt.SEMENTE)
    sels = [np.concatenate([blocos[e] for e in rng.integers(0, len(blocos), len(blocos))]) for _ in range(B)]
    with Pool(2, initializer=vt._init, initargs=(OE,)) as pool:
        res = pool.map(vt._rep_bloco, [(s, {k: (v[0], v[1]) for k, v in pt.items()}) for s in sels], chunksize=10)
    bt = {k: np.array([r[k] for r in res]) for k in OE}
    linhas = []
    for per in dm.PERIODOS:
        for fx in FX:
            for g in GRUPOS:
                k = (per, fx, g); k0 = (BASE, fx, g)
                lo, hi = np.percentile(bt[k], [2.5, 97.5])
                dl, dh = np.percentile(bt[k] - bt[k0], [2.5, 97.5]) if per != BASE else (np.nan, np.nan)
                kt = (per, fx, "todas")
                u1, u2 = pt[kt][2], pt[k][2]
                ok = np.isfinite(u1) & np.isfinite(u2)
                linhas.append(dict(periodo=per, faixa=fx, grupo=g, obitos=int(nob[k][0]), participacao_nos_obitos=nob[k][0] / nob[k][2],
                                   microrregioes_sem_obito=nob[k][1], tau=pt[k][1], ic_inf=lo, ic_sup=hi,
                                   dif_vs_2000_2004=pt[k][1] - pt[k0][1] if per != BASE else np.nan, dif_ic_inf=dl, dif_ic_sup=dh,
                                   corr_efeitos_com_geral=float(np.corrcoef(u1[ok], u2[ok])[0, 1]) if g != "todas" else np.nan))
    t = pd.DataFrame(linhas)
    # razao tau agressoes / tau geral e diferenca, com IC
    extra = []
    for per in dm.PERIODOS:
        for fx in FX:
            for g in ("agressoes",):
                r = bt[(per, fx, g)] / bt[(per, fx, "todas")]
                d = bt[(per, fx, g)] - bt[(per, fx, "todas")]
                est = pt[(per, fx, g)][1] / pt[(per, fx, "todas")][1]
                extra.append(dict(periodo=per, faixa=fx, grupo=g + " / todas (razao de tau)", obitos=np.nan, tau=est, ic_inf=np.percentile(r, 2.5), ic_sup=np.percentile(r, 97.5)))
                extra.append(dict(periodo=per, faixa=fx, grupo=g + " menos todas (diferenca de tau)", obitos=np.nan, tau=pt[(per, fx, g)][1] - pt[(per, fx, "todas")][1], ic_inf=np.percentile(d, 2.5), ic_sup=np.percentile(d, 97.5)))
    pd.concat([t, pd.DataFrame(extra)], ignore_index=True).to_csv(os.path.join(ct.P, "CAUSAS_TEMPORAL_3059.csv"), sep=";", index=False)
    print("pronto")


if __name__ == "__main__":
    main()
