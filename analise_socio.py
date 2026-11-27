"""
Projeto EXPVIDA (C:\\EXPVIDA) - cruzamento da onda dos homicidios com Censo 2022, IDHM e cobertura da Saude da Familia.

Le CENSO2022_COMPACTO.csv, CENSO2022_DICIONARIO.csv, CNES_EQUIPES_MUNICIPIO.csv, POP_MUNICIPIO.csv, MUNICIPIO_MICRORREGIAO.csv,
ONDA_DECOLAGEM_MICRO.csv e VIOLENCIA_MICRO_ANUAL.csv (pasta do script ou argv[1]).
Grava:
  SOCIO_MUNICIPIOS_2022.csv    indicadores do Censo 2022 e cobertura ESF por municipio
  SOCIO_MICRO.csv              os mesmos indicadores por microrregiao + taxas de homicidio e decolagem
  SOCIO_GRADIENTES.csv         taxa de homicidio 2000-2002 e 2022-2024 por quinto de populacao de cada indicador
  SOCIO_CORRELACOES.csv        correlacao de Spearman entre indicadores e homicidio (microrregioes)
  GRADIENTES_CENSO2022.png
Areas descrevem lugares, nao pessoas (falacia ecologica).
"""
import os
import sys

import numpy as np
import pandas as pd

S = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
REG = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}


def ler(nome):
    return pd.read_csv(os.path.join(S, nome), sep=";", dtype={"municipio": str, "micro": str, "microrregiao": str,
                                                               "cod": str, "tabela": str, "tipo_eqp": str})


# ---------------------------------------------------------------- Censo 2022
c = ler("CENSO2022_COMPACTO.csv")
c["valor"] = pd.to_numeric(c.valor, errors="coerce")
c["municipio"] = c.municipio.str[:6]
w = c.pivot_table(index="municipio", columns="cod", values="valor", aggfunc="first")
dic = ler("CENSO2022_DICIONARIO.csv")


def cod(tabela, inicio, unidade, categoria):
    x = dic[(dic.tabela == tabela) & dic.variavel.str.startswith(inicio) & (dic.unidade == unidade)
            & (dic.categoria == categoria)]
    if len(x) != 1:
        raise RuntimeError("codigo nao encontrado: %s %s %s" % (tabela, inicio, categoria))
    return x.cod.iloc[0]


def col(*a, zero=False):
    v = w[cod(*a)]
    return v.fillna(0) if zero else v


ind = pd.DataFrame(index=w.index)
ind["renda_media_pc"] = col("10295", "Valor do rendimento nominal médio", "Reais", "Total | Total | Total")
ind["pct_ate_meio_sm"] = (col("10296", "Moradores", "Percentual", "Até 1/4 de salário mínimo | Total | Total", zero=True)
                          + col("10296", "Moradores", "Percentual", "Mais de 1/4 a 1/2 salário mínimo | Total | Total",
                                zero=True))
ind["pct_renda_outras_fontes"] = col("10297", "Participação percentual", "%", "Rendimento de outras fontes")
ind["alfabetizacao"] = col("9543", "Taxa de alfabetização", "%", "Total | Total | Total")
ind["pct_agua_rede"] = col("6803", "Domicílios", "Percentual", "Possui ligação à rede geral e a utiliza como forma principal", zero=True)
ind["pct_esgoto_rede"] = col("6805", "Domicílios", "Percentual", "Rede geral, rede pluvial ou fossa ligada à rede", zero=True)
ind["pct_lixo_coletado"] = col("6892", "Domicílios", "Percentual", "Coletado", zero=True)
ind["pct_sem_banheiro"] = col("6805", "Domicílios", "Percentual", "Não tinham banheiro nem sanitário", zero=True)

# ---------------------------------------------------------------- populacao e ESF
pop = ler("POP_MUNICIPIO.csv")
p22 = pop[pop.periodo == "2022-2024"].groupby("municipio").pessoas_ano.sum() / 3
p10 = pop[pop.periodo == "2010-2014"].groupby("municipio").pessoas_ano.sum() / 5
cn = ler("CNES_EQUIPES_MUNICIPIO.csv")
esf_antigo = {"01", "02", "03"}   # ESF, ESF com saude bucal M1 e M2 (codigos ate 2019)
esf_novo = {"70"}                 # eSF (codigo a partir de 2020)
cn = cn[cn.tipo_eqp.isin(esf_antigo | esf_novo)]
e = cn.groupby(["ano", "municipio"]).equipes.sum().unstack(0)
ind["pop_2022"] = p22
ind["cobertura_esf_2022"] = np.minimum(100, e.get(2022, pd.Series(dtype=float)).reindex(ind.index).fillna(0) * 3450 / p22 * 100)
ind["cobertura_esf_2010"] = np.minimum(100, e.get(2010, pd.Series(dtype=float)).reindex(ind.index).fillna(0) * 3450
                                       / p10.reindex(ind.index) * 100)
mm = ler("MUNICIPIO_MICRORREGIAO.csv")
ind["micro"] = ind.index.map(dict(zip(mm.municipio, mm.microrregiao)))
ind["regiao"] = ind.index.str[0].map(REG)
ind = ind.dropna(subset=["micro", "pop_2022"])
ind.round(2).to_csv(os.path.join(S, "SOCIO_MUNICIPIOS_2022.csv"), sep=";")

# ---------------------------------------------------------------- microrregiao (media ponderada pela populacao)
cols = ["renda_media_pc", "pct_ate_meio_sm", "pct_renda_outras_fontes", "alfabetizacao", "pct_agua_rede",
        "pct_esgoto_rede", "pct_lixo_coletado", "pct_sem_banheiro", "cobertura_esf_2022", "cobertura_esf_2010"]


def media_pond(d):
    out = {}
    for k in cols:
        ok = d[k].notna()
        out[k] = np.average(d.loc[ok, k], weights=d.loc[ok, "pop_2022"]) if ok.any() else np.nan
    out["pop_2022"] = d.pop_2022.sum()
    return pd.Series(out)


mi = ind.groupby("micro").apply(media_pond)
dec = ler("ONDA_DECOLAGEM_MICRO.csv").set_index("micro")
mi = mi.join(dec[["decolagem", "taxa_2000_2002", "taxa_2022_2024", "pico_ano", "pico_taxa", "idhm_r_2000", "regiao"]])
mi["variacao_taxa"] = mi.taxa_2022_2024 - mi.taxa_2000_2002
mi.round(3).to_csv(os.path.join(S, "SOCIO_MICRO.csv"), sep=";")

# ---------------------------------------------------------------- gradientes por quintos de populacao
rot = {"pct_ate_meio_sm": "Moradores com renda per capita de até 1/2 salário mínimo (%)",
       "alfabetizacao": "Taxa de alfabetização 15+ (%)",
       "pct_esgoto_rede": "Domicílios com esgoto ligado à rede (%)",
       "cobertura_esf_2022": "Cobertura estimada da Saúde da Família (%)",
       "renda_media_pc": "Renda domiciliar per capita média (R$)",
       "pct_renda_outras_fontes": "Parte da renda vinda de fontes que não o trabalho (%)"}
vi = ler("VIOLENCIA_MICRO_ANUAL.csv").set_index("micro")
linhas = []
for k in rot:
    d = mi.dropna(subset=[k]).sort_values(k)
    q = np.minimum(5, np.ceil(d.pop_2022.cumsum() / d.pop_2022.sum() * 5)).astype(int)
    d = d.assign(q=q.values)
    for qq, g in d.groupby("q"):
        v = vi.loc[vi.index.isin(g.index)]
        for per, (a0, a1) in {"2000-2002": (2000, 2002), "2022-2024": (2022, 2024)}.items():
            s = v[v.ano.between(a0, a1)]
            linhas.append([k, qq, per, g[k].min(), g[k].max(), s.homic.sum() / s["pop"].sum() * 1e5])
gr = pd.DataFrame(linhas, columns=["indicador", "quinto", "periodo", "min", "max", "taxa_homic_100mil"])
gr.round(2).to_csv(os.path.join(S, "SOCIO_GRADIENTES.csv"), sep=";", index=False)

# ---------------------------------------------------------------- correlacoes
cor = []
for k in cols + ["idhm_r_2000"]:
    for alvo in ["taxa_2000_2002", "taxa_2022_2024", "variacao_taxa"]:
        d = mi[[k, alvo]].dropna()
        cor.append([k, alvo, len(d), d[k].rank().corr(d[alvo].rank())])
co = pd.DataFrame(cor, columns=["indicador", "desfecho", "n_micro", "spearman"])
co.round(3).to_csv(os.path.join(S, "SOCIO_CORRELACOES.csv"), sep=";", index=False)

# ---------------------------------------------------------------- figura
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TXT, TXT2 = "#1f1f1f", "#5c5c5c"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "text.color": TXT})
paineis = [("pct_ate_meio_sm", "Pobreza: renda de até 1/2 salário mínimo", "menos\npobres", "mais\npobres"),
           ("pct_esgoto_rede", "Esgoto ligado à rede", "menos\nesgoto", "mais\nesgoto"),
           ("alfabetizacao", "Alfabetização", "menos\nalfabet.", "mais\nalfabet.")]
fig, axs = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True)
for ax, (k, tit, e1, e5) in zip(axs, paineis):
    for per, cor_, nome in [("2000-2002", "#9dc8f7", "2000-2002"), ("2022-2024", "#b02a2b", "2022-2024")]:
        s = gr[(gr.indicador == k) & (gr.periodo == per)].sort_values("quinto")
        ax.plot(s.quinto, s.taxa_homic_100mil, color=cor_, linewidth=2, marker="o", markersize=8,
                markeredgecolor="white", markeredgewidth=2)
        ax.annotate(nome, (5, s.taxa_homic_100mil.iloc[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=9, color=TXT)
    ax.set_title(tit, loc="left", fontsize=11)
    ax.set_xticks([1, 2, 3, 4, 5], ["1\n" + e1, "2", "3", "4", "5\n" + e5])
    ax.set_xlim(0.7, 6.2)
    ax.set_ylim(0, gr[gr.indicador.isin([x[0] for x in paineis])].taxa_homic_100mil.max() * 1.1)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color="#ececec", linewidth=0.8)
axs[0].set_ylabel("Homicídios por 100 mil habitantes")
fig.suptitle("Homicídios nas microrregiões agrupadas em quintos da população por indicadores do Censo 2022",
             x=0.01, ha="left", fontsize=12)
fig.text(0.01, -0.03, "Fonte: SIM/DATASUS, POPSVS e IBGE, Censo Demográfico 2022 (tabelas 10296, 6805 e 9543). "
         "Cada ponto reúne cerca de 1/5 da população. Áreas descrevem lugares, não pessoas. Elaboração: projeto EXPVIDA.",
         fontsize=8.5, color=TXT2)
fig.tight_layout()
fig.savefig(os.path.join(S, "GRADIENTES_CENSO2022.png"), dpi=150, bbox_inches="tight")

print(gr.pivot_table(index=["indicador", "quinto"], columns="periodo", values="taxa_homic_100mil").round(1).to_string())
print(co[co.desfecho != "taxa_2000_2002"].round(2).to_string(index=False))
print(ind[cols].describe().round(1).to_string())
print("ok")
