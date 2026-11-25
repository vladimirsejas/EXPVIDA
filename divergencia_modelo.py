"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
MODELO DE DIVERGENCIA TERRITORIAL POR IDADE (biblioteca usada pelos tres scripts de analise).

Este arquivo nao precisa ser aberto nem executado: ele so guarda as funcoes. Quem roda e:
  divergencia_territorial.py   (divergencia por idade, sexo e periodo; estabilidade; sensibilidade)
  testes_hipoteses.py          (H1, H2 e H3)
  idt_experimento.py           (regra operacional da IDT, falsos positivos e recuperacao)

Precisa de numpy, scipy e pandas. Le apenas os CSV que ja estao na pasta (nao baixa nada).

IDEIA CENTRAL
  Para cada microrregiao i, sexo, periodo e idade a, a razao de risco e
      RR(i,a) = (obitos / pessoas-ano da microrregiao) / (taxa do resto do Brasil na mesma idade)
  O "resto do Brasil" exclui a propria microrregiao (referencia leave-one-out).
  Com poucos obitos, o RR observado varia so por acaso. Para separar acaso de diferenca real usa-se um
  modelo Poisson-lognormal:
      obitos(i) ~ Poisson( E(i) * exp(mu + u(i)) ),   u(i) ~ Normal(0, tau^2)
  onde E(i) = obitos esperados se a microrregiao tivesse a taxa do resto do Brasil.
  tau e o desvio-padrao, entre microrregioes, do log da razao de risco REAL (sem o acaso de Poisson):
  e a medida de desigualdade territorial. A razao esperada entre o percentil 90 e o 10 e exp(2,563 * tau).
  A integral e feita por quadratura de Gauss-Hermite adaptativa (a mesma ideia dos pacotes de modelos mistos).
"""
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import optimize, stats
from scipy.special import gammaln, logsumexp

sys.dont_write_bytecode = True

PASTA = os.path.dirname(os.path.abspath(__file__))
IDADES = [0, 1] + list(range(5, 85, 5))                      # inicio de cada faixa (18 faixas)
ROTULO = ["0", "1-4"] + ["%d-%d" % (a, a + 4) for a in range(5, 80, 5)] + ["80+"]
PERIODOS = ["2000-2004", "2005-2009", "2010-2014", "2015-2019", "2020-2021 pandemia", "2022-2024"]
SEXOS = {1: "homens", 2: "mulheres"}
# faixas agrupadas (indices em IDADES): usadas nos testes das hipoteses
BANDAS = {"0": [0], "1-14": [1, 2, 3], "15-29": [4, 5, 6], "30-59": [7, 8, 9, 10, 11, 12],
          "60-79": [13, 14, 15, 16], "80+": [17]}
Z90 = stats.norm.ppf(0.9)                                    # 1,2816
TAU_MIN, TAU_MAX = 1e-3, 3.0
_X, _W = np.polynomial.hermite.hermgauss(15)
_LOGW = np.log(_W)


# ------------------------------------------------------------------ dados
def carregar(nivel="microrregiao"):
    """Devolve D e PY: dicionarios {(periodo, sexo): matriz [territorio, 18 idades]} e a lista de codigos.
    nivel: "microrregiao" (558) ou "uf" (27)."""
    t = pd.read_csv(os.path.join(PASTA, "BRASIL_taxas_por_idade.csv"), sep=";", dtype={"codigo": str})
    t = t[t.nivel == nivel]
    codigos = sorted(t.codigo.unique())
    D, PY = {}, {}
    for (per, sx), g in t.groupby(["periodo", "sexo"]):
        d = g.pivot(index="codigo", columns="idade_inicio", values="obitos").reindex(index=codigos, columns=IDADES)
        p = g.pivot(index="codigo", columns="idade_inicio", values="pessoas_ano").reindex(index=codigos, columns=IDADES)
        D[(per, int(sx))] = d.to_numpy(dtype=float)
        PY[(per, int(sx))] = p.to_numpy(dtype=float)
    return D, PY, codigos


def esperados(D, PY, colunas=None):
    """Obitos observados e esperados por microrregiao para um conjunto de idades (padronizacao indireta).
    Referencia: taxa do resto do Brasil (soma das demais microrregioes) em cada idade."""
    cols = list(range(len(IDADES))) if colunas is None else list(colunas)
    d, p = D[:, cols], PY[:, cols]
    taxa_ref = (d.sum(0, keepdims=True) - d) / (p.sum(0, keepdims=True) - p)
    return d.sum(1), (p * taxa_ref).sum(1)


# ------------------------------------------------------------------ modelo Poisson-lognormal
def _modo(D, logE, mu, tau):
    u = np.zeros_like(D)
    prec = 1.0 / tau ** 2
    for _ in range(25):
        lam = np.exp(logE + mu + u)
        passo = (D - lam - u * prec) / (-lam - prec)
        passo = np.clip(passo, -1.0, 1.0)
        u = u - passo
        if np.max(np.abs(passo)) < 1e-9:
            break
    lam = np.exp(logE + mu + u)
    return u, 1.0 / np.sqrt(lam + prec)


def loglik(mu, tau, D, logE, devolver_u=False):
    u, s = _modo(D, logE, mu, tau)
    uk = u[:, None] + math.sqrt(2.0) * s[:, None] * _X[None, :]
    eta = logE[:, None] + mu + uk
    termo = (_LOGW[None, :] + _X[None, :] ** 2 + D[:, None] * eta - np.exp(eta) - gammaln(D + 1)[:, None]
             - 0.5 * (uk / tau) ** 2 - math.log(tau) - 0.5 * math.log(2 * math.pi))
    ll = float(np.sum(np.log(math.sqrt(2.0) * s) + logsumexp(termo, axis=1)))
    return (ll, u) if devolver_u else ll


def loglik_nulo(D, E):
    mu = math.log(D.sum() / E.sum())
    return float(np.sum(D * (np.log(E) + mu) - E * math.exp(mu) - gammaln(D + 1))), mu


def ajustar(D, E, inicio=None):
    """Maxima verossimilhanca de (mu, tau). Devolve dict com mu, tau, ll, lrt, p, u (moda por microrregiao)."""
    ok = E > 0
    D, E = D[ok], E[ok]
    logE = np.log(E)
    ll0, mu0 = loglik_nulo(D, E)

    def f(theta):
        return -loglik(theta[0], math.exp(theta[1]), D, logE)

    melhor = None
    pontos = [inicio] if inicio is not None else [(mu0, math.log(0.1)), (mu0, math.log(0.02)), (mu0, math.log(0.4))]
    for ini in pontos:
        r = optimize.minimize(f, np.array(ini, dtype=float), method="L-BFGS-B",
                              bounds=[(-2.0, 2.0), (math.log(TAU_MIN), math.log(TAU_MAX))])
        if melhor is None or r.fun < melhor.fun:
            melhor = r
    mu, tau = float(melhor.x[0]), math.exp(float(melhor.x[1]))
    ll, u = loglik(mu, tau, D, logE, devolver_u=True)
    lrt = max(0.0, 2.0 * (ll - ll0))
    uu = np.full(len(ok), np.nan)
    uu[ok] = u
    return {"mu": mu, "tau": tau, "ll": ll, "ll0": ll0, "lrt": lrt,
            "p": 0.5 * stats.chi2.sf(lrt, 1) if lrt > 0 else 1.0, "u": uu, "n": int(ok.sum())}


def intervalo_perfil(D, E, aj, nivel=0.95):
    """IC por verossimilhanca de perfil para tau (raiz de ll_max - ll_perfil = corte, nos dois lados).
    Limite inferior 0 quando o perfil nao exclui tau muito pequeno; limite superior nan se passar do teto."""
    ok = E > 0
    D, E = D[ok], E[ok]
    logE = np.log(E)
    corte = stats.chi2.ppf(nivel, 1) / 2.0

    def perfil(tau):
        r = optimize.minimize_scalar(lambda m: -loglik(m, tau, D, logE),
                                     bounds=(aj["mu"] - 0.6, aj["mu"] + 0.6), method="bounded",
                                     options={"xatol": 1e-6})
        return -r.fun

    def f(ltau):
        return aj["ll"] - perfil(math.exp(ltau)) - corte

    lt = math.log(aj["tau"])
    lo_lim, hi_lim = math.log(TAU_MIN), math.log(TAU_MAX)
    if lt <= lo_lim + 1e-6:
        inf = 0.0
    elif f(lo_lim) < 0:
        inf = 0.0
    else:
        inf = math.exp(optimize.brentq(f, lo_lim, lt, xtol=1e-4))
    if lt >= hi_lim - 1e-6 or f(hi_lim) < 0:
        sup = float("nan")
    else:
        sup = math.exp(optimize.brentq(f, lt, hi_lim, xtol=1e-4))
    return inf, sup


# ------------------------------------------------------------------ razao P90/P10 no estilo do BRASIL_RESUMO
def p90_p10_observada(D, PY, min_obitos=20):
    """Reproduz o criterio do repositorio: taxas observadas, so microrregioes com >= min_obitos na faixa."""
    r = []
    for j in range(D.shape[1]):
        m = D[:, j] >= min_obitos
        t = D[m, j] / PY[m, j]
        r.append((int(m.sum()), float(np.percentile(t, 90) / np.percentile(t, 10)) if m.sum() >= 20 else float("nan")))
    return r


# ------------------------------------------------------------------ tabua de vida (mesma formula do piloto_expectativa.py)
_INI = IDADES
_LARG = [1, 4] + [5] * 15 + [None]


def tabua_lx(D, PY, sexo):
    """Devolve (l, L, a) da tabua abreviada, ou None se nao for calculavel. Igual a piloto_expectativa.tabua."""
    NG = len(_INI)
    if np.any(PY <= 0) or D[-1] <= 0:
        return None
    m = D / PY
    a = np.zeros(NG)
    m0 = m[0]
    if sexo == 1:
        a[0] = 0.330 if m0 >= 0.107 else 0.045 + 2.684 * m0
        a[1] = 1.352 if m0 >= 0.107 else 1.651 - 2.816 * m0
    else:
        a[0] = 0.350 if m0 >= 0.107 else 0.053 + 2.800 * m0
        a[1] = 1.361 if m0 >= 0.107 else 1.522 - 1.518 * m0
    for i in range(2, NG - 1):
        a[i] = _LARG[i] / 2.0
    q = np.ones(NG)
    for i in range(NG - 1):
        n = _LARG[i]
        q[i] = min(1.0, n * m[i] / (1.0 + (n - a[i]) * m[i]))
    l = np.ones(NG)
    for i in range(1, NG):
        l[i] = l[i - 1] * (1.0 - q[i - 1])
    L = np.zeros(NG)
    for i in range(NG - 1):
        L[i] = _LARG[i] * l[i + 1] + a[i] * (l[i] - l[i + 1])
    L[-1] = l[-1] / m[-1]
    return l, L, a


def e0_80(l, L):
    return float(L[:-1].sum() / l[0])


def arriaga_e0_80(t1, t2):
    """Decomposicao de Arriaga da diferenca e0-80(2) - e0-80(1) por faixa de idade (18 valores; a faixa 80+ vale 0).
    A soma das contribuicoes e exatamente a diferenca de e0-80."""
    l1, L1, _ = t1
    l2, L2, _ = t2
    NG = len(l1)
    T2 = np.zeros(NG + 1)
    for i in range(NG - 2, -1, -1):
        T2[i] = T2[i + 1] + L2[i]
    c = np.zeros(NG)
    for i in range(NG - 1):
        direto = (l1[i] / l1[0]) * (L2[i] / l2[i] - L1[i] / l1[i])
        indireto = (T2[i + 1] / l1[0]) * (l1[i] / l2[i] - l1[i + 1] / l2[i + 1]) if i + 1 < NG - 1 else 0.0
        c[i] = direto + indireto
    return c


# ------------------------------------------------------------------ versao vetorizada (muitas tabuas de uma vez)
_LARG_VEC = np.array([1, 4] + [5] * 15 + [0], dtype=float)


def tabua_vec(D, PY, sexo):
    """Igual a tabua_lx, para arrays [..., 18]. Onde nao calculavel (obitos 80+ = 0) devolve nan."""
    m = D / PY
    NG = len(_INI)
    a = np.zeros(m.shape)
    m0 = m[..., 0]
    if sexo == 1:
        a[..., 0] = np.where(m0 >= 0.107, 0.330, 0.045 + 2.684 * m0)
        a[..., 1] = np.where(m0 >= 0.107, 1.352, 1.651 - 2.816 * m0)
    else:
        a[..., 0] = np.where(m0 >= 0.107, 0.350, 0.053 + 2.800 * m0)
        a[..., 1] = np.where(m0 >= 0.107, 1.361, 1.522 - 1.518 * m0)
    a[..., 2:NG - 1] = _LARG_VEC[2:NG - 1] / 2.0
    q = np.ones(m.shape)
    n = _LARG_VEC[:NG - 1]
    q[..., :NG - 1] = np.minimum(1.0, n * m[..., :NG - 1] / (1.0 + (n - a[..., :NG - 1]) * m[..., :NG - 1]))
    l = np.ones(m.shape)
    l[..., 1:] = np.cumprod(1.0 - q[..., :NG - 1], axis=-1)
    L = np.zeros(m.shape)
    L[..., :NG - 1] = n * l[..., 1:] + a[..., :NG - 1] * (l[..., :NG - 1] - l[..., 1:])
    with np.errstate(divide="ignore", invalid="ignore"):
        L[..., NG - 1] = np.where(m[..., NG - 1] > 0, l[..., NG - 1] / m[..., NG - 1], np.nan)
    return l, L


def arriaga_vec(ref, l2, L2):
    """ref = (l1, L1) com forma [18]; l2, L2 com forma [..., 18]. Devolve contribuicoes [..., 18] (80+ = 0)."""
    l1, L1 = ref[0], ref[1]
    NG = len(_INI)
    T2 = np.zeros(l2.shape[:-1] + (NG + 1,))
    for i in range(NG - 2, -1, -1):
        T2[..., i] = T2[..., i + 1] + L2[..., i]
    c = np.zeros(l2.shape)
    for i in range(NG - 1):
        direto = (l1[i] / l1[0]) * (L2[..., i] / l2[..., i] - L1[i] / l1[i])
        indireto = (T2[..., i + 1] / l1[0]) * (l1[i] / l2[..., i] - l1[i + 1] / l2[..., i + 1]) if i + 1 < NG - 1 else 0.0
        c[..., i] = direto + indireto
    return c
