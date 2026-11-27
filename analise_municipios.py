"""Projeto EXPVIDA (C:\\EXPVIDA) - analise por MUNICIPIO a partir de CAUSAS_MUNICIPIO.csv e POP_MUNICIPIO.csv.
Razao padronizada (indireta, por faixa x sexo, referencia Brasil no mesmo periodo) suavizada por Bayes empirico
(Poisson-gama, metodo dos momentos de Marshall). Periodo principal: 2015-2019 + 2022-2024 (sem a pandemia).
"""
import sys
import numpy as np
import pandas as pd

import os
D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[2] if len(sys.argv) > 2 else D

c = pd.read_csv(f"{D}/CAUSAS_MUNICIPIO.csv", sep=";", dtype={"municipio": str})
p = pd.read_csv(f"{D}/POP_MUNICIPIO.csv", sep=";", dtype={"municipio": str})
mm = pd.read_csv(f"{D}/MUNICIPIO_MICRORREGIAO.csv", sep=";", dtype=str, encoding="utf-8-sig")
idh = pd.read_csv(f"{D}/idhm_municipios_RE.csv", sep=";")
idh = idh[idh.ANO == 2010].copy()
idh["municipio"] = idh.Codmun7.astype(str).str[:6]

IND = {
    "homicidio": ["agressao_arma_fogo", "agressao_arma_branca", "agressao_outros", "intervencao_legal"],
    "homicidio_arma_fogo": ["agressao_arma_fogo"],
    "intervencao_legal": ["intervencao_legal"],
    "indeterminada": ["indeterminada_arma_fogo", "indeterminada_outros"],
    "transito": ["transito_pedestre", "transito_ciclista", "transito_moto", "transito_automovel", "transito_pesado", "transito_outros"],
    "transito_moto": ["transito_moto"],
    "transito_pedestre": ["transito_pedestre"],
    "transito_automovel": ["transito_automovel"],
    "suicidio": ["suicidio_enforcamento", "suicidio_arma_fogo", "suicidio_envenenamento", "suicidio_outros"],
    "suicidio_arma_fogo": ["suicidio_arma_fogo"],
    "suicidio_envenenamento": ["suicidio_envenenamento"],
    "suicidio_enforcamento": ["suicidio_enforcamento"],
    "mal_definidas": ["mal_definidas"],
}
# idosos 60+: total e causas sensiveis a atencao primaria (proxy, nao medida de eficiencia)
IDOSOS = ["60-69", "70-79", "80+"]
IND_IDOSO = {
    "idosos_total": None,
    "idosos_aps": ["hipertensivas", "diabetes", "pneumonia_influenza", "cerebrovasculares"],
    "idosos_mal_definidas": ["mal_definidas"],
    "idosos_demencias": ["demencias"],
}
RECENTE = ["2015-2019", "2022-2024"]
ANTIGO = ["2000-2004", "2005-2009"]


def razao(periodos, causas, faixas=None, sexo=None):
    cc = c[c.periodo.isin(periodos)]
    pp = p[p.periodo.isin(periodos)]
    if causas is not None:
        cc = cc[cc.causa.isin(causas)]
    if faixas is not None:
        cc, pp = cc[cc.faixa.isin(faixas)], pp[pp.faixa.isin(faixas)]
    if sexo is not None:
        cc, pp = cc[cc.sexo == sexo], pp[pp.sexo == sexo]
    o = cc.groupby(["periodo", "municipio", "sexo", "faixa"]).obitos.sum()
    n = pp.groupby(["periodo", "municipio", "sexo", "faixa"]).pessoas_ano.sum()
    t = pd.concat([o, n], axis=1).fillna(0)
    t = t[t.pessoas_ano > 0]
    ref = t.groupby(level=["periodo", "sexo", "faixa"]).sum()
    taxa_ref = (ref.obitos / ref.pessoas_ano).rename("tr")
    t = t.join(taxa_ref, on=["periodo", "sexo", "faixa"])
    t["esp"] = t.pessoas_ano * t.tr
    m = t.groupby(level="municipio")[["obitos", "esp", "pessoas_ano"]].sum()
    m = m[m.esp > 0]
    # taxa bruta de referencia por 100 mil (padronizada para a estrutura Brasil)
    taxa_br = ref.obitos.sum() / ref.pessoas_ano.sum() * 1e5
    # Bayes empirico (Marshall) sobre a razao O/E
    r = m.obitos / m.esp
    mu = m.obitos.sum() / m.esp.sum()
    s2 = (m.esp * (r - mu) ** 2).sum() / m.esp.sum() - mu / m.esp.mean()
    s2 = max(s2, 1e-9)
    w = s2 / (s2 + mu / m.esp)
    m["razao_bruta"] = r
    m["razao_eb"] = w * r + (1 - w) * mu
    m["taxa_eb_100mil"] = m.razao_eb * taxa_br
    m["taxa_br_100mil"] = taxa_br
    return m


resultados = {}
for nome, causas in IND.items():
    resultados[nome] = razao(RECENTE, causas)
resultados["homicidio_homens_15_29"] = razao(RECENTE, IND["homicidio"], ["15-29"], 1)
resultados["transito_moto_homens_15_29"] = razao(RECENTE, IND["transito_moto"], ["15-29"], 1)
resultados["suicidio_homens"] = razao(RECENTE, IND["suicidio"], None, 1)
for nome, causas in IND_IDOSO.items():
    resultados[nome] = razao(RECENTE, causas, IDOSOS)
resultados["homicidio_2000_2009"] = razao(ANTIGO, IND["homicidio"])
resultados["suicidio_2000_2009"] = razao(ANTIGO, IND["suicidio"])
resultados["transito_2000_2009"] = razao(ANTIGO, IND["transito"])
resultados["idosos_aps_2000_2009"] = razao(ANTIGO, IND_IDOSO["idosos_aps"], IDOSOS)

# tabela larga por municipio
base = mm.rename(columns={"nome": "nome_municipio"})[["municipio", "nome_municipio", "uf", "microrregiao"]].drop_duplicates("municipio")
pop = p[p.periodo.isin(RECENTE)].groupby("municipio").pessoas_ano.sum() / 8
larga = base.set_index("municipio").join(pop.rename("pop_media"))
for nome, m in resultados.items():
    larga = larga.join(m[["obitos", "taxa_eb_100mil", "razao_eb"]].add_prefix(nome + "__"))
larga = larga.join(idh.set_index("municipio")[["IDHM_R", "IDHM_E"]])
larga = larga[larga.pop_media.notna()]
larga.to_csv(f"{OUT}/MUNICIPIOS_INDICADORES.csv", sep=";", float_format="%.4g")

# gradiente por quintil de renda municipal (IDHM-R 2010), quintis ponderados por populacao
g = larga[larga.IDHM_R.notna()].sort_values("IDHM_R").copy()
g["acum"] = g.pop_media.cumsum() / g.pop_media.sum()
g["quintil"] = np.minimum((g.acum * 5).apply(np.ceil), 5).astype(int)
linhas = []
for nome, m in resultados.items():
    j = m.join(g[["quintil"]], how="inner")
    q = j.groupby("quintil")[["obitos", "esp"]].sum()
    taxa_br = m.taxa_br_100mil.iloc[0]
    for qq, row in q.iterrows():
        linhas.append([nome, qq, int(row.obitos), row.obitos / row.esp, row.obitos / row.esp * taxa_br])
grad = pd.DataFrame(linhas, columns=["indicador", "quintil_renda", "obitos", "razao_padronizada", "taxa_padronizada_100mil"])
grad.to_csv(f"{OUT}/GRADIENTE_RENDA_MUNICIPAL.csv", sep=";", index=False, float_format="%.4g")

# grupos de territorio: capitais x interior por grande regiao, e destaque SP capital x interior do Nordeste
CAP = {"110020", "120040", "130260", "140010", "150140", "160030", "172100", "211130", "221100", "230440", "240810",
       "250750", "261160", "270430", "280030", "292740", "310620", "320530", "330455", "355030", "410690", "420540",
       "431490", "500270", "510340", "520870", "530010"}
REG = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}
larga2 = larga.reset_index().rename(columns={"index": "municipio"})
larga2["grupo"] = larga2.municipio.str[0].map(REG) + np.where(larga2.municipio.isin(CAP), " capitais", " interior")
grp = larga2.set_index("municipio")["grupo"]
linhas = []
for nome, m in resultados.items():
    j = m.join(grp, how="inner")
    q = j.groupby("grupo")[["obitos", "esp"]].sum()
    taxa_br = m.taxa_br_100mil.iloc[0]
    for gg, row in q.iterrows():
        linhas.append([nome, gg, int(row.obitos), row.obitos / row.esp, row.obitos / row.esp * taxa_br])
grupos = pd.DataFrame(linhas, columns=["indicador", "grupo", "obitos", "razao_padronizada", "taxa_padronizada_100mil"])
grupos.to_csv(f"{OUT}/CAPITAIS_INTERIOR_REGIOES.csv", sep=";", index=False, float_format="%.4g")

# persistencia: correlacao de Spearman entre 2000-2009 e 2015-2024 (municipios com 20 mil hab ou mais)
pers = []
for atual, antigo in [("homicidio", "homicidio_2000_2009"), ("suicidio", "suicidio_2000_2009"),
                      ("transito", "transito_2000_2009"), ("idosos_aps", "idosos_aps_2000_2009")]:
    j = larga[larga.pop_media >= 20000][[atual + "__razao_eb", antigo + "__razao_eb"]].dropna()
    pers.append([atual, len(j), j.corr(method="spearman").iloc[0, 1]])
pd.DataFrame(pers, columns=["indicador", "municipios", "spearman_2000_09_vs_2015_24"]).to_csv(
    f"{OUT}/PERSISTENCIA_MUNICIPAL.csv", sep=";", index=False, float_format="%.3f")

# rankings: municipios com 100 mil habitantes ou mais (taxa suavizada)
rk = []
for nome in ["homicidio", "homicidio_arma_fogo", "homicidio_homens_15_29", "intervencao_legal", "transito", "transito_moto",
             "transito_pedestre", "suicidio", "suicidio_arma_fogo", "suicidio_envenenamento", "idosos_aps", "idosos_mal_definidas"]:
    j = larga[larga.pop_media >= 100000].sort_values(nome + "__taxa_eb_100mil", ascending=False)
    for pos, (mun, row) in enumerate(j.head(15).iterrows(), 1):
        rk.append([nome, pos, mun, row.nome_municipio, row.uf, int(row.pop_media), int(row[nome + "__obitos"]),
                   row[nome + "__taxa_eb_100mil"], row[nome + "__razao_eb"]])
pd.DataFrame(rk, columns=["indicador", "posicao", "municipio", "nome", "uf", "pop_media", "obitos_8anos",
                          "taxa_padronizada_suavizada_100mil", "razao_vs_brasil"]).to_csv(
    f"{OUT}/RANKING_MUNICIPIOS_100MIL.csv", sep=";", index=False, float_format="%.3g")
print("ok")
