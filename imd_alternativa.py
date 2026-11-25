"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
IMD (Idade-Mediana da Diferenca): alternativa a IDT, que nao exige significancia faixa por faixa.
A IMD e uma proposta EXPERIMENTAL deste projeto, nao um indicador consolidado.

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva poucos minutos.
Precisa de numpy, scipy e pandas. Le so os CSV que ja estao na pasta; nao baixa nada, nao cria pastas.

POR QUE EXISTE: a IDT (idt_experimento.py) so existe onde ha 2 faixas consecutivas significativas, entao
falha em microrregioes pequenas e quando a diferenca e modesta (ela detecta tarde demais). A IMD usa a
decomposicao de Arriaga: a diferenca entre a e0-80 da microrregiao e a do Brasil (em anos) e repartida entre
as faixas de idade, e como cada faixa contribui com anos de vida, a soma e estavel mesmo com poucos obitos
por faixa.
REGRA: G = e0-80 da microrregiao menos e0-80 do Brasil. A IMD e a idade de inicio da primeira faixa em que a
contribuicao acumulada chega a metade de G ("metade da diferenca em anos de vida ja foi formada ate esta faixa").
Definida so quando G difere de zero (erro-padrao por bootstrap de Poisson, 200 sorteios; correcao FDR de 5% sobre as
558 microrregioes) e |G| >= 0,3 ano. Sem a correcao, cerca de 6% das microrregioes seriam "definidas" so por acaso.
Compara-se com a IDT: reprodutibilidade entre periodos, falsos positivos e recuperacao de diferenca conhecida.
Grava: IMD_POR_MICRORREGIAO.csv e IMD_AVALIACAO.csv (separador ponto e virgula).
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm
from idt_experimento import esperados_por_idade

SEMENTE = 20261124
R = 200                 # sorteios do bootstrap de Poisson
MIN_G = 0.3             # diferenca minima relevante de e0-80, em anos
PERIODOS_ANALISE = ["2010-2014", "2015-2019", "2022-2024"]
N_SIM, R_SIM = 20, 60


def imd_de(c, G):
    """Indice (0..16) da primeira faixa em que o acumulado chega a metade de G. c: [..., 18]; G: [...]."""
    with np.errstate(divide="ignore", invalid="ignore"):
        cum = np.cumsum(c, axis=-1) / G[..., None]
    ok = cum >= 0.5
    ok[..., -1] = True
    idx = np.argmax(ok, axis=-1).astype(float)
    return np.where(np.isfinite(G) & (G != 0), idx, np.nan)


def tabua_ref(d, py, sx):
    return dm.tabua_lx(d.sum(0), py.sum(0), sx)


def estimar(d, py, sx, ref, rng, reps):
    """Devolve G, indice da IMD, definida (bool), ic inf/sup de G e da IMD. d, py: [n,18]."""
    l, L = dm.tabua_vec(d, py, sx)
    c = dm.arriaga_vec(ref, l, L)
    G = c.sum(1)
    sim = rng.poisson(np.repeat(d[:, None, :], reps, axis=1)).astype(float)
    ls, Ls = dm.tabua_vec(sim, py[:, None, :], sx)
    cs = dm.arriaga_vec(ref, ls, Ls)
    Gs = cs.sum(-1)
    g_inf, g_sup = np.nanpercentile(Gs, 2.5, axis=1), np.nanpercentile(Gs, 97.5, axis=1)
    # significancia de G com correcao de comparacoes multiplas (FDR de Benjamini-Hochberg sobre as microrregioes)
    dp = np.nanstd(Gs, axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = 2 * stats.norm.sf(np.abs(G) / dp)
    p = np.where(np.isfinite(p), p, 1.0)
    p = np.where(dp == 0, np.where(G == 0, 1.0, 0.0), p)
    q = stats.false_discovery_control(p, method="bh")
    definida = (q < 0.05) & (np.abs(G) >= MIN_G) & np.isfinite(G)
    ims = imd_de(cs, Gs)
    ims_sinal = np.where(np.sign(Gs) == np.sign(G)[:, None], ims, np.nan)
    with np.errstate(all="ignore"):
        i_inf, i_sup = np.nanpercentile(ims_sinal, 2.5, axis=1), np.nanpercentile(ims_sinal, 97.5, axis=1)
    return G, imd_de(c, G), definida, g_inf, g_sup, i_inf, i_sup


def idade(ix):
    return np.where(np.isfinite(ix), np.array(dm.IDADES + [np.nan])[np.nan_to_num(ix, nan=18).astype(int)], np.nan)


def principal():
    D, PY, cod = dm.carregar()
    rng = np.random.default_rng(SEMENTE)
    nomes = pd.read_csv(os.path.join(dm.PASTA, "BRASIL_microrregioes.csv"), sep=";", dtype={"codigo": str},
                        usecols=["codigo", "nome", "uf"]).drop_duplicates("codigo").set_index("codigo")
    aval, tabela, guarda = [], [], {}

    def reg(secao, periodo, sexo, medida, valor):
        aval.append({"secao": secao, "periodo": periodo, "sexo": sexo, "medida": medida, "valor": valor})

    for per in PERIODOS_ANALISE:
        for sx in (1, 2):
            d, py = D[(per, sx)], PY[(per, sx)]
            ref = tabua_ref(d, py, sx)
            G, ix, defin, gi, gs_, ii, isup = estimar(d, py, sx, ref, rng, R)
            ages = idade(ix)
            guarda[(per, sx)] = (np.where(defin, ix, np.nan), G, defin)
            for i, c in enumerate(cod):
                tabela.append({"periodo": per, "sexo": dm.SEXOS[sx], "codigo": c, "nome": nomes.loc[c, "nome"],
                               "uf": nomes.loc[c, "uf"], "obitos": int(d[i].sum()), "diferenca_e0_80_anos": G[i],
                               "g_ic_inf": gi[i], "g_ic_sup": gs_[i], "definida": int(defin[i]),
                               "imd": ages[i] if defin[i] else np.nan,
                               "imd_ic_inf": idade(np.array([ii[i]]))[0] if defin[i] else np.nan,
                               "imd_ic_sup": idade(np.array([isup[i]]))[0] if defin[i] else np.nan})
            reg("real", per, dm.SEXOS[sx], "microrregioes_com_IMD_definida", int(defin.sum()))
            reg("real", per, dm.SEXOS[sx], "pior_que_o_Brasil", int((defin & (G < 0)).sum()))
            reg("real", per, dm.SEXOS[sx], "melhor_que_o_Brasil", int((defin & (G > 0)).sum()))
            for a in dm.IDADES[:-1]:
                reg("real_distribuicao_IMD_pior", per, dm.SEXOS[sx], "idade_%d" % a, int((defin & (G < 0) & (ages == a)).sum()))
            print("real:", per, dm.SEXOS[sx], flush=True)
    pd.DataFrame(tabela).to_csv(os.path.join(dm.PASTA, "IMD_POR_MICRORREGIAO.csv"), sep=";", index=False,
                                float_format="%.5g")

    # ---- reprodutibilidade
    for p1, p2 in (("2010-2014", "2015-2019"), ("2015-2019", "2022-2024")):
        for sx in (1, 2):
            a1, G1, d1 = guarda[(p1, sx)]
            a2, G2, d2 = guarda[(p2, sx)]
            ambos = d1 & d2
            nome = "%s x %s" % (p1, p2)
            reg("reprodutibilidade", nome, dm.SEXOS[sx], "microrregioes_com_IMD_nos_dois_periodos", int(ambos.sum()))
            reg("reprodutibilidade", nome, dm.SEXOS[sx], "pct_das_com_IMD_no_1o_periodo_que_tem_no_2o",
                float(100 * ambos.sum() / max(1, d1.sum())))
            po1, po2 = d1.mean(), d2.mean()
            esp = po1 * po2 + (1 - po1) * (1 - po2)
            reg("reprodutibilidade", nome, dm.SEXOS[sx], "kappa_de_Cohen_ter_ou_nao_IMD", float(((d1 == d2).mean() - esp) / (1 - esp)))
            reg("reprodutibilidade", nome, dm.SEXOS[sx], "correlacao_de_Spearman_da_diferenca_G_entre_periodos",
                float(stats.spearmanr(G1[~np.isnan(G1) & ~np.isnan(G2)], G2[~np.isnan(G1) & ~np.isnan(G2)])[0]))
            if ambos.sum() >= 5:
                reg("reprodutibilidade", nome, dm.SEXOS[sx], "correlacao_de_Spearman_da_IMD_entre_periodos",
                    float(stats.spearmanr(a1[ambos], a2[ambos])[0]))
                reg("reprodutibilidade", nome, dm.SEXOS[sx], "pct_com_IMD_igual_ou_vizinha_(ate_1_faixa)",
                    float(100 * (np.abs(a1[ambos] - a2[ambos]) <= 1).mean()))
                reg("reprodutibilidade", nome, dm.SEXOS[sx], "pct_com_IMD_exatamente_igual", float(100 * (a1[ambos] == a2[ambos]).mean()))

    # ---- falsos positivos e recuperacao (2015-2019)
    for sx in (1, 2):
        d, py = D[("2015-2019", sx)], PY[("2015-2019", sx)]
        ref = tabua_ref(d, py, sx)
        E = esperados_por_idade(d, py)
        # nulo: mortalidade igual a do resto do Brasil
        fp = []
        for _ in range(N_SIM):
            _, _, defin, *_ = estimar(rng.poisson(E).astype(float), py, sx, ref, rng, R_SIM)
            fp.append(int(defin.sum()))
        reg("falso_positivo", "2015-2019", dm.SEXOS[sx], "media_de_microrregioes_com_IMD_sem_diferenca_real", float(np.mean(fp)))
        tam = E.sum(1)
        terco = np.digitize(tam, np.quantile(tam, [1 / 3, 2 / 3]))
        for rr_v in (1.4, 1.2):
            for idade_v in (15, 40, 60):
                fator = np.ones(len(dm.IDADES))
                fator[dm.IDADES.index(idade_v):] = rr_v
                D_ver = E * fator[None, :]
                l, L = dm.tabua_vec(D_ver, py, sx)
                c = dm.arriaga_vec(ref, l, L)
                G_ver = c.sum(1)
                ix_ver = imd_de(c, G_ver)
                valido = np.abs(G_ver) >= MIN_G
                erros, detect = [], []
                for _ in range(N_SIM):
                    G, ix, defin, *_ = estimar(rng.poisson(D_ver).astype(float), py, sx, ref, rng, R_SIM)
                    detect.append(defin & valido)
                    erros.append(np.where(defin & valido, np.array(dm.IDADES + [np.nan])[np.nan_to_num(ix, nan=18).astype(int)]
                                          - np.array(dm.IDADES + [np.nan])[np.nan_to_num(ix_ver, nan=18).astype(int)], np.nan))
                detect, erros = np.array(detect), np.array(erros)
                for t, rot in ((0, "pequenas"), (1, "medias"), (2, "grandes")):
                    m = (terco == t) & valido
                    if m.sum() == 0:
                        continue
                    sub_d, sub_e = detect[:, m], erros[:, m]
                    reg("recuperacao", "2015-2019", dm.SEXOS[sx],
                        "pct_detectadas_RR%.1f_a_partir_de_%d_anos_microrregioes_%s" % (rr_v, idade_v, rot), float(100 * sub_d.mean()))
                    if sub_d.any():
                        reg("recuperacao", "2015-2019", dm.SEXOS[sx],
                            "mediana_do_erro_em_anos_RR%.1f_a_partir_de_%d_microrregioes_%s" % (rr_v, idade_v, rot),
                            float(np.nanmedian(sub_e)))
                        reg("recuperacao", "2015-2019", dm.SEXOS[sx],
                            "pct_com_erro_ate_5_anos_entre_detectadas_RR%.1f_a_partir_de_%d_microrregioes_%s" % (rr_v, idade_v, rot),
                            float(100 * np.nanmean(np.abs(sub_e[sub_d]) <= 5)))
        print("simulacoes:", dm.SEXOS[sx], flush=True)
    pd.DataFrame(aval).to_csv(os.path.join(dm.PASTA, "IMD_AVALIACAO.csv"), sep=";", index=False, float_format="%.5g")
    print("pronto: IMD_POR_MICRORREGIAO.csv, IMD_AVALIACAO.csv")


if __name__ == "__main__":
    principal()
