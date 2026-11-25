"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
IDT (Idade de Divergencia Territorial): regra operacional, teste de viabilidade e de robustez.
A IDT e uma proposta EXPERIMENTAL deste projeto. Nao e um indicador consolidado nem se afirma inedita
(a busca de literatura esta registrada em RESULTADOS_DIVERGENCIA.md).

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva alguns minutos.
Precisa de numpy, scipy e pandas. Le so os CSV que ja estao na pasta; nao baixa nada, nao cria pastas.

REGRA OPERACIONAL (fixada antes de olhar os resultados por microrregiao)
  Para cada microrregiao, sexo e periodo, em cada uma das 18 faixas de idade:
    RR = obitos observados / obitos esperados com a taxa do resto do Brasil (padronizacao indireta);
    p exato de Poisson (bilateral);
    correcao de comparacoes multiplas: Benjamini-Hochberg (FDR 5%) sobre TODOS os testes
    (558 microrregioes x 18 faixas) de cada sexo e periodo.
  Faixa "divergente" = q < 0,05 E diferenca relevante (RR >= 1,2 para pior, ou RR <= 1/1,2 para melhor).
  Persistencia: pelo menos 2 faixas consecutivas divergentes no mesmo sentido.
  IDT = idade de inicio da primeira sequencia persistente. A IDT "adversa" usa RR >= 1,2; a "favoravel", RR <= 1/1,2.
  Sem sequencia persistente, a microrregiao fica SEM IDT (a medida nao e estimavel ali), e nao com IDT inventada.

O QUE ESTE SCRIPT AVALIA
  1. Poder: menor RR detectavel (poder 80%, alfa 0,001) por faixa de idade e tamanho da microrregiao.
  2. Falsos positivos: simulacao sem nenhuma divergencia (RR = 1 em tudo).
  3. Recuperacao: simulacao com divergencia conhecida (RR 1,4 e 1,2 a partir de 15, 40 ou 60 anos): quantas
     microrregioes sao detectadas e quao perto fica a IDT estimada da verdadeira.
  4. Reprodutibilidade nos dados reais entre periodos (2010-2014 x 2015-2019 e 2015-2019 x 2022-2024).
Grava: IDT_POR_MICRORREGIAO.csv e IDT_AVALIACAO.csv (separador ponto e virgula).
"""
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm

SEMENTE = 20261124
Q = 0.05                      # FDR
RR_MIN = 1.2                  # diferenca minima relevante (pior: >= 1,2; melhor: <= 1/1,2)
CONSEC = 2                    # faixas consecutivas exigidas
PERIODOS_ANALISE = ["2010-2014", "2015-2019", "2022-2024"]
N_SIM = 200


def esperados_por_idade(d, py):
    """Matriz de esperados [microrregiao, idade] com taxa do resto do Brasil (leave-one-out)."""
    ref = (d.sum(0, keepdims=True) - d) / (py.sum(0, keepdims=True) - py)
    return py * ref


def p_poisson(O, E):
    sup = stats.poisson.sf(O - 1, E)       # P(X >= O)
    inf = stats.poisson.cdf(O, E)          # P(X <= O)
    return np.minimum(1.0, 2.0 * np.minimum(sup, inf))


def divergentes(O, E):
    """Devolve (adversa, favoravel), matrizes booleanas [microrregiao, idade]."""
    p = p_poisson(O, E)
    q = stats.false_discovery_control(p.ravel(), method="bh").reshape(p.shape)
    rr = O / E
    return (q < Q) & (rr >= RR_MIN), (q < Q) & (rr <= 1.0 / RR_MIN)


def idt(flags):
    """Primeira idade de uma sequencia de CONSEC faixas consecutivas True; nan se nao houver."""
    saida = np.full(flags.shape[0], np.nan)
    for i in range(flags.shape[0]):
        f = flags[i]
        for j in range(len(f) - CONSEC + 1):
            if f[j:j + CONSEC].all():
                saida[i] = dm.IDADES[j]
                break
    return saida


def indice_faixa(idades):
    return np.array([dm.IDADES.index(int(a)) if a == a else -1 for a in idades])


def principal():
    D, PY, cod = dm.carregar()
    rng = np.random.default_rng(SEMENTE)
    nomes = pd.read_csv(os.path.join(dm.PASTA, "BRASIL_microrregioes.csv"), sep=";", dtype={"codigo": str},
                        usecols=["codigo", "nome", "uf"]).drop_duplicates("codigo").set_index("codigo")
    avaliacao = []

    def reg(secao, periodo, sexo, medida, valor, detalhe=""):
        avaliacao.append({"secao": secao, "periodo": periodo, "sexo": sexo, "medida": medida, "valor": valor,
                          "detalhe": detalhe})

    # ---------------- IDT nos dados reais
    por_micro, tabela = {}, []
    for per in PERIODOS_ANALISE:
        for sx in (1, 2):
            d, py = D[(per, sx)], PY[(per, sx)]
            E = esperados_por_idade(d, py)
            adv, fav = divergentes(d, E)
            ia, ifv = idt(adv), idt(fav)
            por_micro[(per, sx)] = (ia, ifv)
            for i, c in enumerate(cod):
                tabela.append({"periodo": per, "sexo": dm.SEXOS[sx], "codigo": c, "nome": nomes.loc[c, "nome"],
                               "uf": nomes.loc[c, "uf"], "obitos": int(d[i].sum()), "idt_adversa": ia[i],
                               "idt_favoravel": ifv[i], "faixas_adversas": int(adv[i].sum()),
                               "faixas_favoraveis": int(fav[i].sum())})
            reg("real", per, dm.SEXOS[sx], "microrregioes_com_IDT_adversa", int(np.isfinite(ia).sum()), "de %d" % len(cod))
            reg("real", per, dm.SEXOS[sx], "microrregioes_com_IDT_favoravel", int(np.isfinite(ifv).sum()), "de %d" % len(cod))
            if np.isfinite(ia).any():
                for a in dm.IDADES:
                    reg("real_distribuicao_IDT_adversa", per, dm.SEXOS[sx], "idade_%d" % a, int((ia == a).sum()))
    pd.DataFrame(tabela).to_csv(os.path.join(dm.PASTA, "IDT_POR_MICRORREGIAO.csv"), sep=";", index=False)

    # ---------------- 1. poder
    for sx in (1, 2):
        d, py = D[("2015-2019", sx)], PY[("2015-2019", sx)]
        E = esperados_por_idade(d, py)
        mdrr = np.exp((stats.norm.ppf(1 - 0.001 / 2) + stats.norm.ppf(0.8)) / np.sqrt(E))
        for j, rot in enumerate(dm.ROTULO):
            reg("poder", "2015-2019", dm.SEXOS[sx], "mediana_do_menor_RR_detectavel_idade_%s" % rot, float(np.median(mdrr[:, j])))
            reg("poder", "2015-2019", dm.SEXOS[sx], "pct_microrregioes_que_detectam_RR_1_2_idade_%s" % rot,
                float(100 * (mdrr[:, j] <= 1.2).mean()))
            reg("poder", "2015-2019", dm.SEXOS[sx], "pct_microrregioes_que_detectam_RR_1_5_idade_%s" % rot,
                float(100 * (mdrr[:, j] <= 1.5).mean()))

    # ---------------- 2. falsos positivos (sem divergencia alguma)
    for sx in (1, 2):
        d, py = D[("2015-2019", sx)], PY[("2015-2019", sx)]
        E = esperados_por_idade(d, py)
        com_idt = []
        for _ in range(N_SIM):
            O = rng.poisson(E).astype(float)
            adv, fav = divergentes(O, E)
            com_idt.append(int(np.isfinite(idt(adv)).sum() + np.isfinite(idt(fav)).sum()))
        com_idt = np.array(com_idt)
        reg("falso_positivo", "2015-2019", dm.SEXOS[sx], "media_de_microrregioes_com_IDT_sem_divergencia_real",
            float(com_idt.mean()), "em %d simulacoes de %d microrregioes" % (N_SIM, len(cod)))
        reg("falso_positivo", "2015-2019", dm.SEXOS[sx], "pct_simulacoes_com_alguma_IDT", float(100 * (com_idt > 0).mean()))

    # ---------------- 3. recuperacao de divergencia conhecida
    for sx in (1, 2):
        d, py = D[("2015-2019", sx)], PY[("2015-2019", sx)]
        E = esperados_por_idade(d, py)
        tam = E.sum(1)
        terco = np.digitize(tam, np.quantile(tam, [1 / 3, 2 / 3]))      # 0 = pequenas, 2 = grandes
        for rr_v in (1.4, 1.2):
            for idade_v in (15, 40, 60):
                j0 = dm.IDADES.index(idade_v)
                fator = np.ones(len(dm.IDADES))
                fator[j0:] = rr_v
                est_todas = []
                for _ in range(N_SIM // 4):
                    O = rng.poisson(E * fator[None, :]).astype(float)
                    adv, _ = divergentes(O, E * 1.0)
                    est_todas.append(idt(adv))
                est = np.array(est_todas)                              # [sim, microrregiao]
                for t, rot in ((0, "pequenas"), (1, "medias"), (2, "grandes")):
                    sub = est[:, terco == t]
                    detect = np.isfinite(sub)
                    reg("recuperacao", "2015-2019", dm.SEXOS[sx],
                        "pct_detectadas_RR%.1f_a_partir_de_%d_anos_microrregioes_%s" % (rr_v, idade_v, rot),
                        float(100 * detect.mean()))
                    if detect.any():
                        erro = (sub[detect] - idade_v)
                        reg("recuperacao", "2015-2019", dm.SEXOS[sx],
                            "mediana_do_erro_em_anos_RR%.1f_a_partir_de_%d_microrregioes_%s" % (rr_v, idade_v, rot),
                            float(np.median(erro)))
                        reg("recuperacao", "2015-2019", dm.SEXOS[sx],
                            "pct_com_erro_ate_5_anos_entre_detectadas_RR%.1f_a_partir_de_%d_microrregioes_%s" % (rr_v, idade_v, rot),
                            float(100 * (np.abs(erro) <= 5).mean()))

    # ---------------- 4. reprodutibilidade entre periodos nos dados reais
    for p1, p2 in (("2010-2014", "2015-2019"), ("2015-2019", "2022-2024")):
        for sx in (1, 2):
            a1, a2 = por_micro[(p1, sx)][0], por_micro[(p2, sx)][0]
            t1, t2 = np.isfinite(a1), np.isfinite(a2)
            ambos = t1 & t2
            nome = "%s x %s" % (p1, p2)
            reg("reprodutibilidade", nome, dm.SEXOS[sx], "microrregioes_com_IDT_nos_dois_periodos", int(ambos.sum()))
            reg("reprodutibilidade", nome, dm.SEXOS[sx], "pct_das_com_IDT_no_1o_periodo_que_tem_IDT_no_2o",
                float(100 * ambos.sum() / max(1, t1.sum())))
            po = t1.mean(), t2.mean()
            pc = (t1 & t2).mean()
            esperado = po[0] * po[1] + (1 - po[0]) * (1 - po[1])
            obs = (t1 == t2).mean()
            reg("reprodutibilidade", nome, dm.SEXOS[sx], "kappa_de_Cohen_ter_ou_nao_IDT",
                float((obs - esperado) / (1 - esperado)) if esperado < 1 else float("nan"))
            if ambos.sum() >= 5:
                i1, i2 = indice_faixa(a1[ambos]), indice_faixa(a2[ambos])
                reg("reprodutibilidade", nome, dm.SEXOS[sx], "correlacao_de_Spearman_da_IDT_entre_periodos",
                    float(stats.spearmanr(i1, i2)[0]))
                reg("reprodutibilidade", nome, dm.SEXOS[sx], "pct_com_IDT_igual_ou_vizinha_(ate_1_faixa)",
                    float(100 * (np.abs(i1 - i2) <= 1).mean()))
                reg("reprodutibilidade", nome, dm.SEXOS[sx], "pct_com_IDT_exatamente_igual", float(100 * (i1 == i2).mean()))

    pd.DataFrame(avaliacao).to_csv(os.path.join(dm.PASTA, "IDT_AVALIACAO.csv"), sep=";", index=False, float_format="%.5g")
    print("pronto: IDT_POR_MICRORREGIAO.csv, IDT_AVALIACAO.csv")


if __name__ == "__main__":
    principal()
