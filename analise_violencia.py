"""
Projeto EXPVIDA (C:\\EXPVIDA) - a "onda" dos homicidios 2000-2024 por microrregiao.

Le VIOLENCIA_ANUAL_MUNICIPIO.csv, HOMICIDIO_OCORRENCIA_LOCAL.csv, POP_MUNICIPIO.csv,
MUNICIPIO_MICRORREGIAO.csv e idhm_municipios_RE.csv (todos na pasta do script, ou na pasta do argv[1]).
Grava:
  VIOLENCIA_MICRO_ANUAL.csv     taxa anual de homicidio por microrregiao (bruta e media movel de 3 anos)
  ONDA_DECOLAGEM_MICRO.csv      ano de "decolagem" de cada microrregiao
  ONDA_RESUMO.csv               decolagens por regiao x periodo e por quintil de IDHM-Renda 2000
  VIOLENCIA_REGIAO_ANUAL.csv    taxa anual por grande regiao (homicidio total, arma de fogo, homens 15-29)
  HOMICIDIO_LOCAL_REGIAO.csv    homicidios por local de ocorrencia (rua, casa, hospital) por regiao e ano
  ONDA_HOMICIDIOS.png           mapa do ano de decolagem + linhas por regiao
Areas descrevem lugares, nao pessoas.
"""
import os
import sys

import numpy as np
import pandas as pd

S = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
GEO = sys.argv[2] if len(sys.argv) > 2 else "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-100-mun.json"
HOMIC = ["agressao_arma_fogo", "agressao_arma_branca", "agressao_outros", "intervencao_legal"]
REG = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}
LIMIAR = 30.0   # homicidios por 100 mil (media movel de 3 anos)
PERSISTE = 3    # anos seguidos acima do limiar

PER = {"2000-2004": range(2000, 2005), "2005-2009": range(2005, 2010), "2010-2014": range(2010, 2015),
       "2015-2019": range(2015, 2020), "2020-2021 pandemia": range(2020, 2022), "2022-2024": range(2022, 2025)}


def ler(nome, **kw):
    return pd.read_csv(os.path.join(S, nome), sep=";", dtype={"municipio": str, "mun_residencia": str,
                                                              "mun_ocorrencia": str, "microrregiao": str}, **kw)


# ---------------------------------------------------------------- populacao anual por municipio
pop = ler("POP_MUNICIPIO.csv")
pop["ok"] = True
anos_pop = []
for per, anos in PER.items():
    p = pop[pop.periodo == per]
    tot = p.groupby("municipio").pessoas_ano.sum() / len(anos)
    jov = p[(p.sexo.astype(str) == "1") & (p.faixa == "15-29")].groupby("municipio").pessoas_ano.sum() / len(anos)
    for a in anos:
        anos_pop.append(pd.DataFrame({"ano": a, "pop": tot, "pop_h1529": jov}).reset_index())
popa = pd.concat(anos_pop).fillna(0)

mm = ler("MUNICIPIO_MICRORREGIAO.csv")
mm = mm[~mm.nome.str.contains("IGNORADO", na=False)]
mun2micro = dict(zip(mm.municipio, mm.microrregiao))

# ---------------------------------------------------------------- obitos
v = ler("VIOLENCIA_ANUAL_MUNICIPIO.csv")
v["sexo"] = v.sexo.astype(str)
h = v[v.causa.isin(HOMIC)]
hm = h.groupby(["ano", "municipio"]).obitos.sum().rename("homic")
af = h[h.causa == "agressao_arma_fogo"].groupby(["ano", "municipio"]).obitos.sum().rename("arma_fogo")
jv = h[(h.sexo == "1") & (h.faixa == "15-29")].groupby(["ano", "municipio"]).obitos.sum().rename("homic_h1529")
base = popa.merge(pd.concat([hm, af, jv], axis=1).reset_index(), on=["ano", "municipio"], how="left").fillna(0)
base["micro"] = base.municipio.map(mun2micro)
base["uf"] = base.municipio.str[:2]
base["regiao"] = base.municipio.str[0].map(REG)
base = base.dropna(subset=["micro", "regiao"])

# ---------------------------------------------------------------- regiao x ano
cols = ["pop", "pop_h1529", "homic", "arma_fogo", "homic_h1529"]
rg = base.groupby(["regiao", "ano"])[cols].sum().reset_index()
br = base.groupby("ano")[cols].sum().reset_index().assign(regiao="Brasil")
rg = pd.concat([rg, br])
rg["taxa_homic"] = rg.homic / rg["pop"] * 1e5
rg["taxa_arma_fogo"] = rg.arma_fogo / rg["pop"] * 1e5
rg["taxa_h1529"] = rg.homic_h1529 / rg.pop_h1529 * 1e5
rg.round(2).to_csv(os.path.join(S, "VIOLENCIA_REGIAO_ANUAL.csv"), sep=";", index=False)

# ---------------------------------------------------------------- microrregiao x ano
mi = base.groupby(["micro", "ano"])[cols].sum().reset_index()
mi = mi[mi["pop"] > 0].sort_values(["micro", "ano"])
mi["taxa"] = mi.homic / mi["pop"] * 1e5
roll = mi.groupby("micro")[["homic", "pop"]].rolling(3, center=True, min_periods=2).sum().reset_index(level=0, drop=True)
mi["taxa_mm3"] = roll.homic / roll["pop"] * 1e5
mi["regiao"] = mi.micro.str[0].map(REG)
mi.round(2).to_csv(os.path.join(S, "VIOLENCIA_MICRO_ANUAL.csv"), sep=";", index=False)


def decolagem(s):
    """s: serie taxa_mm3 indexada por ano. Retorna ano, ou 'ja_alta_2000', ou 'nunca'."""
    acima = (s >= LIMIAR).values
    anos = s.index.values
    if acima[:PERSISTE].all():
        return "ja_alta_2000"
    for i in range(1, len(acima) - PERSISTE + 1):
        if acima[i:i + PERSISTE].all():
            return int(anos[i])
    return "nunca"


dec = mi.groupby("micro").apply(lambda d: decolagem(d.set_index("ano").taxa_mm3)).rename("decolagem").reset_index()
ini = mi[mi.ano.between(2000, 2002)].groupby("micro")[["homic", "pop"]].sum()
fim = mi[mi.ano.between(2022, 2024)].groupby("micro")[["homic", "pop"]].sum()
dec["taxa_2000_2002"] = dec.micro.map(ini.homic / ini["pop"] * 1e5)
dec["taxa_2022_2024"] = dec.micro.map(fim.homic / fim["pop"] * 1e5)
dec["pico_ano"] = dec.micro.map(mi.loc[mi.groupby("micro").taxa_mm3.idxmax()].set_index("micro").ano)
dec["pico_taxa"] = dec.micro.map(mi.groupby("micro").taxa_mm3.max())
dec["regiao"] = dec.micro.str[0].map(REG)

# IDHM-Renda 2000 da microrregiao (media ponderada pela populacao)
idh = ler("idhm_municipios_RE.csv")
idh = idh[idh.ANO == 2000].copy()
idh["municipio"] = idh.Codmun7.astype(str).str[:6]
idh["micro"] = idh.municipio.map(mun2micro)
idh = idh.dropna(subset=["micro"])
idh["w"] = idh.IDHM_R * idh.POP
im = idh.groupby("micro")[["w", "POP"]].sum()
dec["idhm_r_2000"] = dec.micro.map(im.w / im.POP)
pm = mi[mi.ano == 2000].set_index("micro")["pop"]
dec["pop_2000"] = dec.micro.map(pm)
d2 = dec.dropna(subset=["idhm_r_2000"]).sort_values("idhm_r_2000")
cum = d2.pop_2000.cumsum() / d2.pop_2000.sum()
dec.loc[d2.index, "quintil_renda_2000"] = np.minimum(5, (cum * 5).apply(np.ceil)).astype(int)
dec.round(3).to_csv(os.path.join(S, "ONDA_DECOLAGEM_MICRO.csv"), sep=";", index=False)


def faixa(x):
    if x in ("ja_alta_2000", "nunca"):
        return x
    x = int(x)
    return "2001-2007" if x <= 2007 else ("2008-2014" if x <= 2014 else "2015-2024")


dec["onda"] = dec.decolagem.apply(faixa)
ordem = ["ja_alta_2000", "2001-2007", "2008-2014", "2015-2024", "nunca"]
r1 = pd.crosstab(dec.regiao, dec.onda).reindex(columns=ordem, fill_value=0)
r1.insert(0, "grupo", "regiao")
r2 = pd.crosstab(dec.quintil_renda_2000, dec.onda).reindex(columns=ordem, fill_value=0)
r2.index = ["quintil_%d" % i for i in r2.index]
r2.insert(0, "grupo", "quintil_IDHM_R_2000")
pd.concat([r1, r2]).to_csv(os.path.join(S, "ONDA_RESUMO.csv"), sep=";")

# ---------------------------------------------------------------- local de ocorrencia
oc = ler("HOMICIDIO_OCORRENCIA_LOCAL.csv")
oc["regiao"] = oc.mun_residencia.str[0].map(REG)
oc = oc.dropna(subset=["regiao"])
lo = oc.pivot_table(index=["regiao", "ano"], columns="local", values="obitos", aggfunc="sum", fill_value=0)
lo["total"] = lo.sum(axis=1)
for c in ["via_publica", "domicilio", "hospital"]:
    if c in lo:
        lo["pct_" + c] = (lo[c] / lo.total * 100).round(1)
lo.reset_index().to_csv(os.path.join(S, "HOMICIDIO_LOCAL_REGIAO.csv"), sep=";", index=False)

# ---------------------------------------------------------------- figura
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

TXT, TXT2 = "#1f1f1f", "#5c5c5c"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "text.color": TXT})
g = gpd.read_file(GEO)
g["municipio"] = g["id"].astype(str).str[:6]
g["micro"] = g.municipio.map(mun2micro)
g = g.dropna(subset=["micro"]).to_crs(5880)
g["geometry"] = g.geometry.make_valid()
gm = g.dissolve(by="micro").reset_index().merge(dec[["micro", "onda"]], on="micro", how="left")
uf = g.dissolve(by=g.municipio.str[:2])

cores = {"ja_alta_2000": "#7a1414", "2001-2007": "#b02a2b", "2008-2014": "#eb6263", "2015-2024": "#f6c1c1",
         "nunca": "#efefef"}
rot = {"ja_alta_2000": "já acima de %d em 2000" % LIMIAR, "2001-2007": "decolou em 2001-2007",
       "2008-2014": "decolou em 2008-2014", "2015-2024": "decolou em 2015-2024", "nunca": "nunca passou de %d" % LIMIAR}
fig = plt.figure(figsize=(13, 6.6))
ax = fig.add_axes([0.0, 0.08, 0.52, 0.80])
gm.plot(color=gm.onda.map(cores).fillna("#d9d9d9"), ax=ax, linewidth=0)
uf.boundary.plot(ax=ax, color="white", linewidth=0.6)
ax.set_axis_off()
ax.set_title("Ano em que a microrregião passou a ter %d+ homicídios por 100 mil" % LIMIAR, loc="left", fontsize=10.5)
ax.legend(handles=[Patch(facecolor=cores[k], edgecolor="#bdbdbd", linewidth=0.5, label=rot[k]) for k in ordem],
          loc="lower left", frameon=False, fontsize=8.5)

ax2 = fig.add_axes([0.58, 0.14, 0.38, 0.72])
cr = {"Nordeste": "#b02a2b", "Norte": "#eb6263", "Centro-Oeste": "#9e9e9e", "Sudeste": "#1757ac", "Sul": "#519ced",
      "Brasil": "#1f1f1f"}
for nome, cor in cr.items():
    s = rg[rg.regiao == nome].sort_values("ano")
    ax2.plot(s.ano, s.taxa_homic, color=cor, linewidth=2.4 if nome == "Brasil" else 2,
             linestyle=(0, (4, 2)) if nome == "Brasil" else "-")
    dy = {"Brasil": 6, "Centro-Oeste": -5}.get(nome, 0)
    ax2.annotate(nome, (s.ano.iloc[-1], s.taxa_homic.iloc[-1]), xytext=(6, dy), textcoords="offset points",
                 va="center", fontsize=9, color=TXT)
ax2.set_xlim(1999.5, 2028)
ax2.set_ylim(bottom=0)
ax2.set_title("Homicídios por 100 mil habitantes, por grande região", loc="left", fontsize=10.5)
for sp in ("top", "right"):
    ax2.spines[sp].set_visible(False)
ax2.grid(axis="y", color="#ececec", linewidth=0.8)
fig.suptitle("A onda dos homicídios no Brasil, 2000-2024", x=0.01, ha="left", y=0.985, fontsize=13)
fig.text(0.01, 0.012, "Fonte: SIM/DATASUS (agressões X85-Y09 e intervenção legal Y35-Y36, por residência) e POPSVS. "
         "\nDecolagem: média móvel de 3 anos acima de %d por %d anos seguidos. Áreas descrevem lugares, não pessoas. "
         "Elaboração: projeto EXPVIDA." % (LIMIAR, PERSISTE), fontsize=8, color=TXT2)
fig.savefig(os.path.join(S, "ONDA_HOMICIDIOS.png"), dpi=150)

print(pd.concat([r1, r2]).to_string())
print(rg[rg.ano.isin([2000, 2007, 2012, 2017, 2024])].pivot(index="regiao", columns="ano", values="taxa_homic").round(1))
print("ok")
