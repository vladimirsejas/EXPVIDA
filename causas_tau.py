"""
Projeto: Quando o territorio importa (estudo 2, causas de morte; pasta de pesquisa, separado do EXPVIDA principal).
Usa CAUSAS_OBITOS_2015_2019.csv (gerado por causas_sim.py) e os denominadores/obitos totais de BRASIL_taxas_por_idade.csv.
1) Conferencia: a soma dos grupos de causa reproduz os obitos totais do EXPVIDA em cada microrregiao, sexo e idade?
2) Para cada sexo, faixa de idade e grupo de causa: tau (mesmo modelo Poisson-lognormal da mortalidade geral, referencia = resto do
   Brasil na mesma causa e idade), IC 95% por bootstrap em BLOCOS DE UF (300 sorteios) e numero de obitos.
   So se estima tau quando ha pelo menos MIN_OBITOS obitos no Brasil naquela combinacao.
3) Correlacao entre os efeitos territoriais estimados (modas) da mortalidade geral e de cada causa, por sexo e faixa
   (descritiva; tau NAO se decompoe em soma de causas).
Grava CAUSAS_CONFERENCIA.csv, CAUSAS_TAU.csv e CAUSAS_CORRELACAO_EFEITOS.csv. Semente fixa.
Como usar: "python causas_tau.py". Leva alguns minutos.
"""
import os, sys
from multiprocessing import Pool
import numpy as np, pandas as pd
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm
import validacao_tau as vt

P = os.path.dirname(os.path.abspath(__file__))
PER = "2015-2019"
B = 300
MIN_OBITOS = 300
FAIXAS = dict(dm.BANDAS)
FAIXAS.update({"15-19": [4], "20-24": [5], "25-29": [6], "1-4": [1], "5-14": [2, 3], "60+": [13, 14, 15, 16, 17]})
GRUPOS_IDADE = ["0", "1-4", "5-14", "15-19", "20-24", "25-29", "15-29", "30-59", "60+"]


def matriz_causa(df, cod, sx, causa):
    idx = {c: i for i, c in enumerate(cod)}
    M = np.zeros((len(cod), len(dm.IDADES)))
    g = df[(df.sexo == sx) & (df.causa == causa)] if causa is not None else df[df.sexo == sx]
    for mic, ida, n in g.groupby(["microrregiao", "idade_inicio"]).obitos.sum().reset_index().itertuples(index=False):
        i = idx.get(str(mic))
        if i is not None:
            M[i, dm.IDADES.index(int(ida))] += n
    return M


def main():
    df = pd.read_csv(os.path.join(P, "CAUSAS_OBITOS_2015_2019.csv"), sep=";", dtype={"microrregiao": str})
    D, PY, cod = dm.carregar()
    # 1) conferencia
    linhas = []
    for sx in (1, 2):
        tot = matriz_causa(df, cod, sx, None)
        ref = D[(PER, sx)]
        linhas.append(dict(sexo=dm.SEXOS[sx], obitos_expvida=ref.sum(), obitos_causas=tot.sum(),
                           diferenca=tot.sum() - ref.sum(), microrregioes_com_diferenca=int((np.abs(tot - ref).sum(1) > 0).sum()),
                           maior_diferenca_absoluta=np.abs(tot - ref).max()))
    pd.DataFrame(linhas).to_csv(os.path.join(P, "CAUSAS_CONFERENCIA.csv"), sep=";", index=False)
    print(pd.DataFrame(linhas).to_string(index=False))
    # 2) tau por causa
    causas = [c for c in sorted(df.causa.unique())]
    OE, info, matrizes = {}, {}, {}
    for sx in (1, 2):
        for c in causas + ["todas"]:
            M = matriz_causa(df, cod, sx, None if c == "todas" else c)
            matrizes[(sx, c)] = M
            for fx in GRUPOS_IDADE:
                cols = FAIXAS[fx]
                nobs = M[:, cols].sum()
                if nobs >= MIN_OBITOS:
                    OE[(sx, c, fx)] = dm.esperados(M, PY[(PER, sx)], cols)
                    info[(sx, c, fx)] = nobs
    pt = {k: (lambda a: (a["mu"], a["tau"], a["u"]))(dm.ajustar(*v)) for k, v in OE.items()}
    uf = np.array([c[:2] for c in cod])
    blocos = [np.where(uf == u)[0] for u in sorted(set(uf))]
    rng = np.random.default_rng(vt.SEMENTE)
    sels = [np.concatenate([blocos[e] for e in rng.integers(0, len(blocos), len(blocos))]) for _ in range(B)]
    pt2 = {k: (v[0], v[1]) for k, v in pt.items()}
    with Pool(2, initializer=vt._init, initargs=(OE,)) as pool:
        res = pool.map(vt._rep_bloco, [(s, pt2) for s in sels], chunksize=10)
    out = []
    for k in OE:
        v = np.array([r[k] for r in res])
        lo, hi = np.percentile(v, [2.5, 97.5])
        out.append(dict(sexo=dm.SEXOS[k[0]], causa=k[1], faixa=k[2], obitos=int(info[k]), tau=pt[k][1], ic_inf=lo, ic_sup=hi))
    t = pd.DataFrame(out)
    t.to_csv(os.path.join(P, "CAUSAS_TAU.csv"), sep=";", index=False)
    # 3) correlacao de efeitos com a mortalidade geral
    cor = []
    for k in OE:
        if k[1] == "todas":
            continue
        kt = (k[0], "todas", k[2])
        if kt in pt:
            u1, u2 = pt[kt][2], pt[k][2]
            ok = np.isfinite(u1) & np.isfinite(u2)
            cor.append(dict(sexo=dm.SEXOS[k[0]], causa=k[1], faixa=k[2], corr_efeitos_com_geral=float(np.corrcoef(u1[ok], u2[ok])[0, 1])))
    pd.DataFrame(cor).to_csv(os.path.join(P, "CAUSAS_CORRELACAO_EFEITOS.csv"), sep=";", index=False)
    print("Pronto:", len(t), "estimativas de tau.")


if __name__ == "__main__":
    main()
