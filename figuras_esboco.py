"""
Projeto: Quando o territorio importa (estudo de divergencia territorial; pasta de pesquisa).
Esboco das tres figuras principais, so com resultados ja calculados e dados reais:
  A) tau por idade e sexo, 2015-2019 (DIFERENCAS_TAU_IDADES.csv, IC por blocos de UF)
  B) razao H2 (tau 15-29 / tau 30-59, homens) nos seis periodos (VALIDACAO_PERIODOS_BLOCOS.csv, IC por blocos de UF)
  C) efeito territorial estimado dos homens de 15-29 anos (razao de risco em relacao ao Brasil, 2015-2019),
     um ponto por microrregiao no centroide (nao e mapa de poligonos)
Grava FIGURAS_ESBOCO.png. Como usar: "python figuras_esboco.py".
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm

P = os.path.dirname(os.path.abspath(__file__))
AZ, LA = "#1f5fa8", "#d9772b"
fig, ax = plt.subplots(1, 3, figsize=(17, 5.2), gridspec_kw={"width_ratios": [1.15, 1, 1]})

# A
d = pd.read_csv(os.path.join(P, "DIFERENCAS_TAU_IDADES.csv"), sep=";")
x = np.arange(len(d))
for c, cor, nome in (("tau_H", AZ, "Homens"), ("tau_M", LA, "Mulheres")):
    ax[0].fill_between(x, d[c + "_ic_inf"], d[c + "_ic_sup"], color=cor, alpha=.18, lw=0)
    ax[0].plot(x, d[c], "-o", color=cor, ms=4, label=nome)
ax[0].set_xticks(x); ax[0].set_xticklabels(d["faixa"], rotation=60, fontsize=8)
ax[0].set_ylabel("τ (desvio-padrão entre microrregiões, escala log)"); ax[0].set_title("A. Desigualdade territorial por idade e sexo, 2015-2019")
ax[0].legend(frameon=False); ax[0].set_ylim(0)

# B
b = pd.read_csv(os.path.join(P, "VALIDACAO_PERIODOS_BLOCOS.csv"), sep=";")
b = b[b["esquema"].str.startswith("UF")].reset_index(drop=True)
y = b["H2_15-29_sobre_30-59"]
ax[1].errorbar(range(len(b)), y, yerr=[y - b["H2_15-29_sobre_30-59_ic_inf"], b["H2_15-29_sobre_30-59_ic_sup"] - y], fmt="o-", color=AZ, capsize=4)
ax[1].axhline(1, color="gray", ls="--", lw=1)
ax[1].set_xticks(range(len(b))); ax[1].set_xticklabels([p.replace(" pandemia", "\n(pandemia)") for p in b["periodo"]], fontsize=8)
ax[1].set_ylabel("τ(15-29) / τ(30-59), homens"); ax[1].set_title("B. A razão fica acima de 1 e cresce até 2015-2019")

# C
D, PY, cod = dm.carregar()
O, E = dm.esperados(D[("2015-2019", 1)], PY[("2015-2019", 1)], dm.BANDAS["15-29"])
a = dm.ajustar(O, E)
rr = np.exp(a["u"])
c = pd.read_csv(os.path.join(P, "MICRORREGIOES_CENTROIDES.csv"), sep=";")
c["microrregiao"] = c["microrregiao"].astype(str)
m = pd.DataFrame({"microrregiao": [str(k) for k in cod], "rr": rr}).merge(c, on="microrregiao", how="left").dropna()
sc = ax[2].scatter(m["lon"], m["lat"], c=np.log2(m["rr"]), cmap="RdBu_r", vmin=-1.5, vmax=1.5, s=14)
ax[2].set_aspect("equal"); ax[2].set_xticks([]); ax[2].set_yticks([])
cb = plt.colorbar(sc, ax=ax[2], shrink=.75, ticks=[-1, 0, 1]); cb.ax.set_yticklabels(["½×", "= Brasil", "2×"])
ax[2].set_title("C. Homens de 15-29 anos: risco relativo estimado\npor microrregião (esboço, centroides)")
for z in ax[:2]:
    z.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(P, "FIGURAS_ESBOCO.png"), dpi=140)
print("tau =", round(a["tau"], 3), "| microrregioes no mapa:", len(m), "| rr min/max:", round(m.rr.min(), 2), round(m.rr.max(), 2))
