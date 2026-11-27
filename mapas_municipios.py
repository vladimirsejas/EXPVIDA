"""Projeto EXPVIDA - mapas municipais (razao suavizada vs Brasil) e grafico da inversao do gradiente de renda."""
import sys
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
import pandas as pd

import os
GEO = sys.argv[1] if len(sys.argv) > 1 else "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-100-mun.json"
S = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
TXT, TXT2 = "#1f1f1f", "#5c5c5c"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "text.color": TXT})

g = gpd.read_file(GEO)
g["municipio"] = g["id"].astype(str).str[:6]
ind = pd.read_csv(f"{S}/MUNICIPIOS_INDICADORES.csv", sep=";", dtype={"municipio": str})
g = g.merge(ind, on="municipio", how="left").to_crs(5880)
g["geometry"] = g.geometry.make_valid()
uf = g.dissolve(by=g.municipio.str[:2])

cores = ["#1757ac", "#519ced", "#b6d5f8", "#efefef", "#f6c1c1", "#eb6263", "#b02a2b"]
limites = [0, 0.5, 0.7, 0.9, 1.1, 1.5, 2.0, 99]
rotulos = ["menos da metade", "0,5 a 0,7", "0,7 a 0,9", "parecido com o Brasil (0,9 a 1,1)", "1,1 a 1,5", "1,5 a 2,0",
           "mais do dobro"]
cmap, norm = ListedColormap(cores), BoundaryNorm(limites, len(cores))

paineis = [("homicidio__razao_eb", "Homicídios (agressões + intervenção legal)"),
           ("transito_moto__razao_eb", "Mortes de motociclistas"),
           ("suicidio__razao_eb", "Suicídios"),
           ("idosos_aps__razao_eb", "Idosos 60+: hipertensão, diabetes, AVC e pneumonia")]
fig, axs = plt.subplots(2, 2, figsize=(12, 12.6))
for ax, (col, tit) in zip(axs.flat, paineis):
    g.plot(column=col, cmap=cmap, norm=norm, ax=ax, linewidth=0, missing_kwds={"color": "#d9d9d9"})
    uf.boundary.plot(ax=ax, color="white", linewidth=0.5)
    ax.set_title(tit, fontsize=11, loc="left", color=TXT)
    ax.set_axis_off()
fig.legend(handles=[Patch(facecolor=c, edgecolor="#bdbdbd", linewidth=0.5, label=l) for c, l in zip(cores, rotulos)],
           loc="lower center", ncol=4, frameon=False, fontsize=9,
           title="Taxa do município em relação ao Brasil (padronizada por idade e sexo, suavizada)")
fig.suptitle("Onde se morre mais do que a média brasileira, por município, 2015-2019 e 2022-2024",
             fontsize=13, x=0.02, ha="left", y=0.993)
fig.text(0.02, 0.962, "Fonte: SIM/DATASUS e população POPSVS. Áreas descrevem municípios, não pessoas. "
         "Cinza: sem dado. Elaboração: projeto EXPVIDA.", fontsize=8.5, color=TXT2)
fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.08, wspace=0.02, hspace=0.06)
fig.savefig(f"{S}/MAPA_MUNICIPIOS_4_CAUSAS.png", dpi=150)

# inversao do gradiente de renda (quintis de IDHM-Renda 2010)
gr = pd.read_csv(f"{S}/GRADIENTE_RENDA_MUNICIPAL.csv", sep=";")
fig, axs = plt.subplots(1, 3, figsize=(13, 4.4), sharey=True)
pares = [("homicidio", "Homicídios"), ("transito", "Trânsito"), ("idosos_aps", "Idosos: causas sensíveis à atenção primária")]
for ax, (k, tit) in zip(axs, pares):
    for per, nome, cor in [("_2000_2009", "2000-2009", "#9dc8f7"), ("", "2015-2024", "#1757ac")]:
        s = gr[gr.indicador == k + per].sort_values("quintil_renda")
        ax.plot(s.quintil_renda, s.razao_padronizada, color=cor, linewidth=2, marker="o", markersize=8,
                markeredgecolor="white", markeredgewidth=2, label=nome)
        ax.annotate(nome, (5, s.razao_padronizada.iloc[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=9, color=TXT)
    ax.axhline(1, color="#9e9e9e", linewidth=1, linestyle=(0, (3, 3)))
    ax.set_title(tit, loc="left", fontsize=11)
    ax.set_xticks([1, 2, 3, 4, 5], ["1\nmais pobres", "2", "3", "4", "5\nmais ricos"])
    ax.set_xlim(0.7, 6.0)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color="#ececec", linewidth=0.8)
axs[0].set_ylabel("Razão em relação ao Brasil (1 = média)")
axs[0].legend(frameon=False, loc="upper left")
fig.suptitle("Municípios agrupados em quintos da população pelo IDHM-Renda 2010", x=0.01, ha="left", fontsize=12)
fig.text(0.01, -0.02, "Fonte: SIM/DATASUS, POPSVS e Atlas do Desenvolvimento Humano. 2015-2024 sem os anos de pandemia. "
         "Nos municípios pobres, o sub-registro de 2000-2009 puxa a razão para baixo.", fontsize=8.5, color=TXT2)
fig.tight_layout()
fig.savefig(f"{S}/GRADIENTE_RENDA_ANTES_DEPOIS.png", dpi=150, bbox_inches="tight")
print("ok")
