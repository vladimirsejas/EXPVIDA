"""
Projeto: Quando o territorio importa (estudo de divergencia territorial; pasta de pesquisa, nao e o EXPVIDA principal).
VALIDACAO DO MODELO DE TAU. Roda uma etapa por vez:  python validacao_tau.py <etapa>
  moran      autocorrelacao espacial dos efeitos territoriais estimados, contra a distribuicao esperada sem
             dependencia espacial (simulada, ja considerando o encolhimento do modelo)
  blocos     bootstrap em blocos geograficos (por UF e por agrupamentos espaciais) para H2 e H3
  simulacao  cobertura dos intervalos do tau com efeitos espacialmente correlacionados e nao normais
  tstudent   modelo alternativo com efeitos de cauda pesada (t de Student)
  influencia retirar uma microrregiao (ou uma UF) por vez
Precisa de numpy, scipy e pandas; usa MICRORREGIOES_VIZINHAS.csv e MICRORREGIOES_CENTROIDES.csv (feitos a partir do
mapa dos municipios e da tabela CADMUN). Semente fixa 20261124.
"""
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd
from scipy import optimize, stats
from scipy.cluster.vq import kmeans2
from scipy.special import gammaln, logsumexp

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm

SEMENTE = 20261124
PER = "2015-2019"
NB = list(dm.BANDAS.keys())


def saida(nome, df):
    df.to_csv(os.path.join(dm.PASTA, nome), sep=";", index=False, float_format="%.5g")


def dados():
    D, PY, cod = dm.carregar()
    OE = {(sx, b): dm.esperados(D[(PER, sx)], PY[(PER, sx)], cols) for sx in (1, 2) for b, cols in dm.BANDAS.items()}
    return D, PY, cod, OE


def vizinhanca(cod):
    pos = {c: i for i, c in enumerate(cod)}
    n = len(cod)
    W = np.zeros((n, n))
    v = pd.read_csv(os.path.join(dm.PASTA, "MICRORREGIOES_VIZINHAS.csv"), sep=";", dtype=str)
    for a, b in zip(v.microrregiao_a, v.microrregiao_b):
        W[pos[a], pos[b]] = W[pos[b], pos[a]] = 1
    cen = pd.read_csv(os.path.join(dm.PASTA, "MICRORREGIOES_CENTROIDES.csv"), sep=";", dtype={"microrregiao": str})
    xy = cen.set_index("microrregiao").loc[cod][["lon", "lat"]].to_numpy()
    for i in np.where(W.sum(1) == 0)[0]:          # ilhas: ligar a mais proxima
        d = np.hypot(*(xy - xy[i]).T)
        d[i] = np.inf
        j = int(np.argmin(d))
        W[i, j] = W[j, i] = 1
    return W, xy


def moran(z, Wrs):
    z = z - z.mean()
    return float(z @ Wrs @ z / (z @ z))


def r2_uf(z, uf_idx, n_uf):
    z = z - z.mean()
    soma = np.bincount(uf_idx, weights=z, minlength=n_uf)
    cont = np.bincount(uf_idx, minlength=n_uf)
    return float(np.sum(soma[cont > 0] ** 2 / cont[cont > 0]) / np.sum(z ** 2))


# ---------------------------------------------------------------- etapa 1: Moran
def _sim_moran(args):
    O_E, mu, tau, sem, Wrs, uf_idx, n_uf = args
    E = O_E
    rng = np.random.default_rng(sem)
    u = rng.normal(0, tau, len(E))
    O = rng.poisson(E * np.exp(mu + u)).astype(float)
    a = dm.ajustar(O, E, inicio=(mu, math.log(tau)))
    return moran(a["u"], Wrs), r2_uf(a["u"], uf_idx, n_uf), a["tau"]


def etapa_moran():
    D, PY, cod, OE = dados()
    W, _ = vizinhanca(cod)
    Wrs = W / W.sum(1, keepdims=True)
    ufs = sorted({c[:2] for c in cod})
    uf_idx = np.array([ufs.index(c[:2]) for c in cod])
    linhas = []
    with Pool(2) as pool:
        for (sx, b), (O, E) in OE.items():
            a = dm.ajustar(O, E)
            I0, R0 = moran(a["u"], Wrs), r2_uf(a["u"], uf_idx, len(ufs))
            args = [(E, a["mu"], a["tau"], SEMENTE + k, Wrs, uf_idx, len(ufs)) for k in range(300)]
            res = np.array(pool.map(_sim_moran, args))
            linhas.append({"sexo": dm.SEXOS[sx], "faixa": b, "tau": a["tau"], "moran_observado": I0,
                           "moran_nulo_media": res[:, 0].mean(), "moran_nulo_dp": res[:, 0].std(ddof=1),
                           "p_moran": float((1 + np.sum(res[:, 0] >= I0)) / 301),
                           "r2_entre_UFs_observado": R0, "r2_entre_UFs_nulo_media": res[:, 1].mean(),
                           "p_r2_uf": float((1 + np.sum(res[:, 1] >= R0)) / 301)})
            print("moran", sx, b, "I=%.3f nulo=%.3f" % (I0, res[:, 0].mean()), flush=True)
    saida("VALIDACAO_MORAN.csv", pd.DataFrame(linhas))


# ---------------------------------------------------------------- etapa 2: bootstrap em blocos
def _rep_bloco(args):
    sel, pt = args
    out = {}
    for k, (O, E) in OE_G.items():
        a = dm.ajustar(O[sel], E[sel], inicio=(pt[k][0], math.log(pt[k][1])))
        out[k] = a["tau"]
    return out


OE_G = None


def _init(oe):
    global OE_G
    OE_G = oe


def estatisticas(t):
    """t: dict (sx,b)->tau. Devolve vetor de quantidades de interesse."""
    q = {"tau_H_" + b: t[(1, b)] for b in NB}
    q.update({"tau_M_" + b: t[(2, b)] for b in NB})
    q["H2_15-29_sobre_1-14"] = t[(1, "15-29")] / t[(1, "1-14")]
    q["H2_15-29_sobre_30-59"] = t[(1, "15-29")] / t[(1, "30-59")]
    for b in NB:
        q["difLog_HM_" + b] = math.log(t[(1, b)]) - math.log(t[(2, b)])
    return q


def etapa_blocos():
    D, PY, cod, OE = dados()
    n = len(cod)
    W, xy = vizinhanca(cod)
    pt = {k: (lambda a: (a["mu"], a["tau"]))(dm.ajustar(*v)) for k, v in OE.items()}
    est0 = estatisticas({k: v[1] for k, v in pt.items()})
    esquemas = {}
    uf = np.array([c[:2] for c in cod])
    esquemas["UF (27 blocos)"] = [np.where(uf == u)[0] for u in sorted(set(uf))]
    for kk in (20, 60):
        _, lab = kmeans2((xy - xy.mean(0)) / xy.std(0), kk, minit="++", seed=SEMENTE)
        esquemas["agrupamentos espaciais (%d blocos)" % kk] = [np.where(lab == l)[0] for l in sorted(set(lab)) if (lab == l).any()]
    esquemas["independente (microrregiao)"] = [np.array([i]) for i in range(n)]
    B = 400
    linhas, wald_l = [], []
    with Pool(2, initializer=_init, initargs=(OE,)) as pool:
        for nome, blocos in esquemas.items():
            rng = np.random.default_rng(SEMENTE)
            sels = []
            for _ in range(B):
                if nome.startswith("independente"):
                    sels.append(rng.integers(0, n, n))
                else:
                    esc = rng.integers(0, len(blocos), len(blocos))
                    sels.append(np.concatenate([blocos[e] for e in esc]))
            res = pool.map(_rep_bloco, [(s, pt) for s in sels], chunksize=10)
            Q = pd.DataFrame([estatisticas(r) for r in res])
            for q, v0 in est0.items():
                lo, hi = np.percentile(Q[q], [2.5, 97.5])
                linhas.append({"esquema": nome, "quantidade": q, "estimativa": v0, "ic_inf": lo, "ic_sup": hi,
                               "largura": hi - lo})
            # H2: p unilateral (log da razao, aproximacao normal) e teste de Wald (H3)
            for q in ("H2_15-29_sobre_1-14", "H2_15-29_sobre_30-59"):
                sd = np.log(Q[q]).std(ddof=1)
                wald_l.append({"esquema": nome, "teste": q, "estatistica": math.log(est0[q]) / sd,
                               "p": float(stats.norm.sf(math.log(est0[q]) / sd))})
            cols = ["difLog_HM_" + b for b in NB]
            d_est = np.array([est0[c] for c in cols])
            C = np.zeros((5, 6))
            for i in range(5):
                C[i, 0], C[i, i + 1] = -1.0, 1.0
            S = np.cov((Q[cols].to_numpy() @ C.T).T)
            w = float((C @ d_est) @ np.linalg.solve(S, C @ d_est))
            wald_l.append({"esquema": nome, "teste": "H3 Wald (5 gl)", "estatistica": w, "p": float(stats.chi2.sf(w, 5))})
            pico_m = Q[["tau_H_" + b for b in NB]].to_numpy().argmax(1)
            pico_f = Q[["tau_M_" + b for b in NB]].to_numpy().argmax(1)
            wald_l.append({"esquema": nome, "teste": "prob. pico masculino em 15-29", "estatistica": float((pico_m == 2).mean()),
                           "p": float("nan")})
            wald_l.append({"esquema": nome, "teste": "prob. picos coincidirem", "estatistica": float((pico_m == pico_f).mean()),
                           "p": float("nan")})
            print("blocos", nome, flush=True)
    saida("VALIDACAO_BLOCOS_IC.csv", pd.DataFrame(linhas))
    saida("VALIDACAO_BLOCOS_TESTES.csv", pd.DataFrame(wald_l))


# ---------------------------------------------------------------- etapa 3: simulacao de cobertura
def _sar(Wrs, phi):
    n = Wrs.shape[0]
    M = np.linalg.inv(np.eye(n) - phi * Wrs)
    esc = math.sqrt(np.mean(np.sum(M ** 2, axis=1)))
    return M / esc


def _inov(rng, dist, n):
    if dist == "normal":
        return rng.normal(size=n)
    if dist == "t3":
        return rng.standard_t(3, n) / math.sqrt(3)
    z = rng.normal(size=n)                                  # assimetrica (lognormal centrada)
    m, v = math.exp(0.5 * 0.8 ** 2), (math.exp(0.8 ** 2) - 1) * math.exp(0.8 ** 2)
    return (np.exp(0.8 * z) - m) / math.sqrt(v)


def _rep_sim(args):
    E, tau, dist, M, sem = args
    rng = np.random.default_rng(sem)
    u = tau * (M @ _inov(rng, dist, len(E)))
    O = rng.poisson(E * np.exp(u)).astype(float)
    a = dm.ajustar(O, E)
    inf, sup = dm.intervalo_perfil(O, E, a)
    sup = float("inf") if math.isnan(sup) else sup
    return a["tau"], inf, sup, float(np.std(u, ddof=1))


def etapa_simulacao():
    D, PY, cod, OE = dados()
    W, _ = vizinhanca(cod)
    Wrs = W / W.sum(1, keepdims=True)
    linhas = []
    R = 150
    with Pool(2) as pool:
        for faixa in ("15-29", "30-59"):
            E = OE[(1, faixa)][1]
            for phi in (0.0, 0.9):
                M = _sar(Wrs, phi) if phi > 0 else np.eye(len(E))
                for dist in ("normal", "t3", "assimetrica"):
                    for tau in (0.05, 0.15, 0.30):
                        args = [(E, tau, dist, M, SEMENTE + 1000 * r + int(tau * 100)) for r in range(R)]
                        res = np.array(pool.map(_rep_sim, args, chunksize=5))
                        cob = float(np.mean((res[:, 1] <= tau) & (tau <= res[:, 2])))
                        cob_emp = float(np.mean((res[:, 1] <= res[:, 3]) & (res[:, 3] <= res[:, 2])))
                        linhas.append({"faixa_E_real": faixa, "dependencia_espacial_phi": phi, "efeitos": dist,
                                       "tau_verdadeiro": tau, "tau_estimado_medio": res[:, 0].mean(),
                                       "vies_relativo_pct": 100 * (res[:, 0].mean() / tau - 1),
                                       "cobertura_ic95_do_tau": cob, "cobertura_do_dp_realizado": cob_emp,
                                       "repeticoes": R})
                        print("sim", faixa, phi, dist, tau, "cob=%.2f" % cob, flush=True)
    saida("VALIDACAO_SIMULACAO.csv", pd.DataFrame(linhas))


# ---------------------------------------------------------------- etapa 4: efeitos com cauda pesada (t de Student)
_X, _W = np.polynomial.hermite.hermgauss(21)
_LW = np.log(_W)


def _logt(u, s, nu):
    z = u / s
    return (gammaln((nu + 1) / 2) - gammaln(nu / 2) - 0.5 * math.log(nu * math.pi) - (nu + 1) / 2 * np.log1p(z * z / nu)
            - math.log(s))


def _loglik_t(mu, s, nu, D, logE):
    u = np.zeros_like(D)
    for _ in range(60):
        eta = logE + mu + u
        lam = np.exp(eta)
        z2 = (u / s) ** 2
        g1 = D - lam - (nu + 1) * u / (nu * s * s + u * u)
        g2 = -lam - (nu + 1) * (nu * s * s - u * u) / (nu * s * s + u * u) ** 2
        g2 = np.minimum(g2, -1e-6 - lam)                 # curvatura negativa garantida
        passo = np.clip(g1 / g2, -1.0, 1.0)
        u = u - passo
        if np.max(np.abs(passo)) < 1e-9:
            break
    lam = np.exp(logE + mu + u)
    g2 = np.minimum(-lam - (nu + 1) * (nu * s * s - u * u) / (nu * s * s + u * u) ** 2, -1e-6 - lam)
    sd = 1 / np.sqrt(-g2)
    uk = u[:, None] + math.sqrt(2) * sd[:, None] * _X[None, :]
    eta = logE[:, None] + mu + uk
    termo = (_LW[None, :] + _X[None, :] ** 2 + D[:, None] * eta - np.exp(eta) - gammaln(D + 1)[:, None]
             + _logt(uk, s, nu))
    return float(np.sum(np.log(math.sqrt(2) * sd) + logsumexp(termo, axis=1)))


def ajustar_t(O, E, nu, mu0, tau0):
    logE = np.log(E)
    s0 = tau0 * math.sqrt((nu - 2) / nu)
    r = optimize.minimize(lambda th: -_loglik_t(th[0], math.exp(th[1]), nu, O, logE), np.array([mu0, math.log(s0)]),
                          method="L-BFGS-B", bounds=[(-2, 2), (math.log(1e-3), math.log(3))])
    mu, s = float(r.x[0]), math.exp(float(r.x[1]))
    return mu, s * math.sqrt(nu / (nu - 2)), -float(r.fun)


def etapa_tstudent():
    D, PY, cod, OE = dados()
    linhas = []
    for (sx, b), (O, E) in OE.items():
        a = dm.ajustar(O, E)
        linha = {"sexo": dm.SEXOS[sx], "faixa": b, "tau_normal": a["tau"], "loglik_normal": a["ll"]}
        for nu in (3, 5, 10):
            mu, sdt, ll = ajustar_t(O, E, nu, a["mu"], a["tau"])
            linha["dp_t_nu%d" % nu] = sdt
            linha["dif_loglik_t_nu%d_menos_normal" % nu] = ll - a["ll"]
        linhas.append(linha)
        print("t", sx, b, flush=True)
    df = pd.DataFrame(linhas)
    saida("VALIDACAO_T_STUDENT.csv", df)


# ---------------------------------------------------------------- etapa 5: influencia
def etapa_influencia():
    D, PY, cod, OE = dados()
    n = len(cod)
    pt = {k: dm.ajustar(*v) for k, v in OE.items()}

    def tau_sem(idx):
        m = np.ones(n, bool)
        m[idx] = False
        return {k: dm.ajustar(O[m], E[m], inicio=(pt[k]["mu"], math.log(pt[k]["tau"])))["tau"] for k, (O, E) in OE.items()
                if k[0] == 1 and k[1] in ("1-14", "15-29", "30-59")}
    base1, base2 = pt[(1, "15-29")]["tau"] / pt[(1, "1-14")]["tau"], pt[(1, "15-29")]["tau"] / pt[(1, "30-59")]["tau"]
    lin = []
    for i in range(n):
        t = tau_sem([i])
        lin.append({"microrregiao": cod[i], "r1": t[(1, "15-29")] / t[(1, "1-14")], "r2": t[(1, "15-29")] / t[(1, "30-59")],
                    "tau_H_15-29": t[(1, "15-29")]})
        if i % 100 == 0:
            print("infl", i, flush=True)
    df = pd.DataFrame(lin)
    df["d_r1"], df["d_r2"] = df.r1 - base1, df.r2 - base2
    saida("VALIDACAO_INFLUENCIA_MICRORREGIAO.csv", df.reindex(df.d_r1.abs().sort_values(ascending=False).index).head(30))
    resumo = {"razao_1_base": base1, "razao_1_minimo": df.r1.min(), "razao_1_maximo": df.r1.max(),
              "razao_2_base": base2, "razao_2_minimo": df.r2.min(), "razao_2_maximo": df.r2.max()}
    ufs = sorted({c[:2] for c in cod})
    luf = []
    for u in ufs:
        idx = [i for i, c in enumerate(cod) if c[:2] == u]
        m = np.ones(n, bool)
        m[idx] = False
        tt = {k: dm.ajustar(O[m], E[m], inicio=(pt[k]["mu"], math.log(pt[k]["tau"])))["tau"] for k, (O, E) in OE.items()}
        pm = NB[int(np.argmax([tt[(1, b)] for b in NB]))]
        pf = NB[int(np.argmax([tt[(2, b)] for b in NB]))]
        luf.append({"UF_retirada": u, "microrregioes_retiradas": len(idx), "razao_15-29_sobre_1-14": tt[(1, "15-29")] / tt[(1, "1-14")],
                    "razao_15-29_sobre_30-59": tt[(1, "15-29")] / tt[(1, "30-59")], "pico_homens": pm, "pico_mulheres": pf,
                    "tau_H_15-29": tt[(1, "15-29")], "tau_M_1-14": tt[(2, "1-14")], "tau_M_15-29": tt[(2, "15-29")]})
        print("uf", u, flush=True)
    saida("VALIDACAO_INFLUENCIA_UF.csv", pd.DataFrame(luf))
    saida("VALIDACAO_INFLUENCIA_RESUMO.csv", pd.DataFrame([resumo]))


# ---------------------------------------------------------------- etapa 6: todos os periodos, com blocos
def etapa_periodos():
    D, PY, cod = dm.carregar()
    n = len(cod)
    W, xy = vizinhanca(cod)
    uf = np.array([c[:2] for c in cod])
    _, lab = kmeans2((xy - xy.mean(0)) / xy.std(0), 20, minit="++", seed=SEMENTE)
    esquemas = {"UF (27 blocos)": [np.where(uf == u)[0] for u in sorted(set(uf))],
                "agrupamentos espaciais (20 blocos)": [np.where(lab == l)[0] for l in sorted(set(lab)) if (lab == l).any()]}
    B = 300
    linhas = []
    for per in dm.PERIODOS:
        OE = {(sx, b): dm.esperados(D[(per, sx)], PY[(per, sx)], cols) for sx in (1, 2) for b, cols in dm.BANDAS.items()}
        pt = {k: (lambda a: (a["mu"], a["tau"]))(dm.ajustar(*v)) for k, v in OE.items()}
        est0 = estatisticas({k: v[1] for k, v in pt.items()})
        with Pool(2, initializer=_init, initargs=(OE,)) as pool:
            for nome, blocos in esquemas.items():
                rng = np.random.default_rng(SEMENTE)
                sels = []
                for _ in range(B):
                    esc = rng.integers(0, len(blocos), len(blocos))
                    sels.append(np.concatenate([blocos[e] for e in esc]))
                res = pool.map(_rep_bloco, [(s, pt) for s in sels], chunksize=10)
                Q = pd.DataFrame([estatisticas(r) for r in res])
                linha = {"periodo": per, "esquema": nome}
                for q in ("H2_15-29_sobre_1-14", "H2_15-29_sobre_30-59"):
                    lo, hi = np.percentile(Q[q], [2.5, 97.5])
                    sd = np.log(Q[q]).std(ddof=1)
                    linha[q] = est0[q]; linha[q + "_ic_inf"] = lo; linha[q + "_ic_sup"] = hi
                    linha[q + "_p_unilateral"] = float(stats.norm.sf(math.log(est0[q]) / sd))
                cols = ["difLog_HM_" + b for b in NB]
                d_est = np.array([est0[c] for c in cols])
                C = np.zeros((5, 6))
                for i in range(5):
                    C[i, 0], C[i, i + 1] = -1.0, 1.0
                S = np.cov((Q[cols].to_numpy() @ C.T).T)
                w = float((C @ d_est) @ np.linalg.solve(S, C @ d_est))
                linha["H3_wald"], linha["H3_p"] = w, float(stats.chi2.sf(w, 5))
                pm = Q[["tau_H_" + b for b in NB]].to_numpy().argmax(1)
                pf = Q[["tau_M_" + b for b in NB]].to_numpy().argmax(1)
                linha["prob_pico_H_em_15-29"] = float((pm == 2).mean())
                linha["prob_pico_M_em_1-14"] = float((pf == 1).mean())
                linhas.append(linha)
                print("periodos", per, nome, flush=True)
    saida("VALIDACAO_PERIODOS_BLOCOS.csv", pd.DataFrame(linhas))


ETAPAS = {"periodos": etapa_periodos, "moran": etapa_moran, "blocos": etapa_blocos, "simulacao": etapa_simulacao, "tstudent": etapa_tstudent,
          "influencia": etapa_influencia}

if __name__ == "__main__":
    ETAPAS[sys.argv[1]]()
