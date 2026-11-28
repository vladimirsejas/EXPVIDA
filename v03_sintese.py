# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

h = pd.read_csv("H10_RESULTADOS_V2.csv", sep=";")
h = h[h["fracao_indeterminada"] == 0].copy()
periodos = list(dict.fromkeys(h["periodo"]))

# ---------- figura ----------
GR = [("Agressões e intervenção legal", ["agressoes_intervencao_legal"], "#8B0000"),
      ("Doenças circulatórias", ["circulatorias"], "#4C78A8"),
      ("Neoplasias", ["neoplasias"], "#F2A541"),
      ("Doenças respiratórias", ["respiratorias"], "#72B7B2"),
      ("Demais doenças", ["demais_doencas"], "#B79BD0"),
      ("Transporte", ["transporte"], "#54A24B"),
      ("COVID-19", ["covid19"], "#E377C2"),
      ("Outras causas", ["intencao_indeterminada", "suicidio", "externas_demais", "infecciosas_sem_covid"], "#C9B458")]
MAL = "mal_definidas_sem_causa"
usados = {g for _, gs, _ in GR for g in gs} | {MAL}
assert usados == set(h["grupo"]), "grupos nao cobertos"

plt.rcParams.update({"font.size": 12})
fig, axs = plt.subplots(1, 2, figsize=(15, 7), sharey=True)
x = np.arange(len(periodos))
rot = [p.replace(" pandemia", "\n(pandemia)") for p in periodos]
for ax, (sx, nome) in zip(axs, [(1, "Homens"), (2, "Mulheres")]):
    d = h[h["sexo"] == sx]
    base = np.zeros(len(periodos))
    for lab, gs, cor in GR:
        v = d[d["grupo"].isin(gs)].groupby("periodo")["contribuicao"].sum().reindex(periodos).fillna(0).to_numpy()
        ax.bar(x, v, bottom=base, color=cor, label=lab, width=0.7, edgecolor="white", linewidth=.5)
        base += v
    m = d[d["grupo"] == MAL].set_index("periodo")["contribuicao"].reindex(periodos).fillna(0).to_numpy()
    ax.bar(x, m, color="#D0D0D0", hatch="///", edgecolor="#555555", width=0.7, label="Mal definidas e sem causa")
    vo = d.groupby("periodo")["variancia_observada"].first().reindex(periodos).to_numpy()
    ax.plot(x, vo, "o", color="black", markersize=8, linestyle="none", label="Variância observada total", zorder=5)
    ax.axhline(0, color="black", linewidth=.8)
    ax.set_xticks(x)
    ax.set_xticklabels(rot, fontsize=10)
    ax.set_xlabel("Período")
    ax.set_title(nome, fontsize=15)
    ax.grid(axis="y", alpha=.3)
axs[0].set_ylabel("Contribuição para a variância territorial")
hd, lb = axs[0].get_legend_handles_labels()
fig.legend(hd, lb, loc="lower center", ncol=5, frameon=False, fontsize=11)
fig.suptitle("Contribuição dos grupos de causa para a variância territorial da expectativa de vida", fontsize=15)
fig.tight_layout(rect=(0, 0.12, 1, 0.95))
fig.savefig("V03_FIGURA_SINTESE.png", dpi=300)

# ---------- tabela queda ----------
P0, P1, P2 = "2000-2004", "2015-2019", "2022-2024"
w = h.pivot_table(index=["sexo", "grupo"], columns="periodo", values="contribuicao").reset_index()
tot = h.groupby(["sexo", "periodo"])["contribuicao"].sum().unstack()
rows = []
for sx in (1, 2):
    sub = w[w["sexo"] == sx].copy()
    for alvo, col in ((P1, "pct_queda_2000_2015"), (P2, "pct_queda_2000_2022")):
        queda_total = sub[P0].sum() - sub[alvo].sum()
        sub[col] = (sub[P0] - sub[alvo]) / queda_total * 100
        assert abs(sub[col].sum() - 100) <= 0.5, (sx, alvo, sub[col].sum())
    rows.append(sub)
t = pd.concat(rows)
t["sexo"] = t["sexo"].map({1: "homens", 2: "mulheres"})
t = t[["sexo", "grupo", P0, P1, P2, "pct_queda_2000_2015", "pct_queda_2000_2022"]]
t = t.rename(columns={P0: "contrib_2000-2004", P1: "contrib_2015-2019", P2: "contrib_2022-2024"})
t.to_csv("V03_TABELA_QUEDA.csv", sep=";", index=False, float_format="%.4f", encoding="utf-8")
print("ASSERT OK: porcentagens da queda somam 100 (+-0,5) por sexo e intervalo")

# ---------- mal definidas ----------
mm = pd.read_csv("MUNICIPIO_MICRORREGIAO.csv", sep=";", dtype=str).drop_duplicates("municipio")
ign = set(mm.loc[mm["municipio"].str.endswith("0000") | (mm["uf"] == "00"), "municipio"])
uf_of = dict(zip(mm["municipio"], mm["uf"]))
c = pd.read_csv("CAUSAS_MUNICIPIO.csv", sep=";", dtype={"municipio": str, "faixa": str})
c = c[~(c["municipio"].str.endswith("0000") | c["municipio"].isin(ign))].copy()
c["uf"] = c["municipio"].map(uf_of).fillna(c["municipio"].str[:2])
c = c[c["uf"] != "00"]
REG = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}
c["regiao"] = c["uf"].str[0].map(REG)
assert c["regiao"].notna().all()
c["md"] = c["causa"].isin(["mal_definidas", "sem_causa"])
g = c.groupby(["periodo", "regiao"]).apply(
    lambda d: pd.Series({"obitos_mal_definidos": d.loc[d["md"], "obitos"].sum(), "obitos_total": d["obitos"].sum()}),
    include_groups=False).reset_index()
g["pct_mal_definidas"] = g["obitos_mal_definidos"] / g["obitos_total"] * 100
po = {p: i for i, p in enumerate(periodos)}
g["_o"] = g["periodo"].map(po); g["_r"] = g["regiao"].map({v: i for i, v in enumerate(REG.values())})
g = g.sort_values(["_o", "_r"]).drop(columns=["_o", "_r"])
g.to_csv("V03_TABELA_MAL_DEFINIDAS.csv", sep=";", index=False, float_format="%.4f", encoding="utf-8")
