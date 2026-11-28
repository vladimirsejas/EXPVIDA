# -*- coding: utf-8 -*-
"""ONDE esta a violencia (2000-2024) e relacao com a renda (IDHM_R) do territorio."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

K = 100000
REG = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}
AGR = ["agressao_arma_fogo", "agressao_arma_branca", "agressao_outros"]

cau = pd.read_csv("CAUSAS_MUNICIPIO.csv", sep=";", dtype={"municipio": str, "faixa": str})
pop = pd.read_csv("POP_MUNICIPIO.csv", sep=";", dtype={"municipio": str, "faixa": str})
mm = pd.read_csv("MUNICIPIO_MICRORREGIAO.csv", sep=";", dtype=str)
idh = pd.read_csv("IDHM_RE_POR_MICRORREGIAO.csv", sep=";", dtype={"microrregiao": str})
idh["ANO"] = idh["ANO"].astype(int)

periodos = list(dict.fromkeys(cau["periodo"]))
assert set(periodos) == set(pop["periodo"]), "periodos diferentes entre CAUSAS e POP"
ordem = {p: i for i, p in enumerate(periodos)}
ini = {p: int(p[:4]) for p in periodos}

# ---------- municipios ----------
mm = mm.drop_duplicates("municipio")
ign_mun = set(mm.loc[mm["municipio"].str.endswith("0000") | (mm["uf"] == "00"), "municipio"])
uf_of = dict(zip(mm["municipio"], mm["uf"]))
mic_of = dict(zip(mm["municipio"], mm["microrregiao"]))


def ignorado(m):
    return m.str.endswith("0000") | m.isin(ign_mun)


def prep(df):
    ig = ignorado(df["municipio"])
    # municipios fora do arquivo de microrregiao (criados depois): UF = 2 primeiros digitos do codigo
    df = df.assign(uf=df["municipio"].map(uf_of).fillna(df["municipio"].str[:2]))
    ig = ig | (df["uf"] == "00")
    return df[~ig].copy(), df[ig].copy()


cau_ok, cau_ign = prep(cau)
pop_ok, _ = prep(pop)
for d in (cau_ok, pop_ok):
    d["regiao"] = d["uf"].str[0].map(REG)
    d["microrregiao"] = d["municipio"].map(mic_of)
assert cau_ok["regiao"].notna().all() and pop_ok["regiao"].notna().all()


def grupo(c):
    if c in AGR:
        return "agressao"
    if c.startswith("transito_"):
        return "transito"
    if c.startswith("suicidio_"):
        return "suicidio"
    return "outra"


cau_ok["g"] = cau_ok["causa"].map(grupo)

M, J = 1, "15-29"
cj = cau_ok[(cau_ok["sexo"] == M) & (cau_ok["faixa"] == J)]
pj = pop_ok[(pop_ok["sexo"] == M) & (pop_ok["faixa"] == J)]


def taxas(keys, cj, pj):
    k = ["periodo"] + keys
    p = pj.groupby(k)["pessoas_ano"].sum().rename("pop")
    o = pd.DataFrame(index=p.index)
    o["ob_agressao"] = cj[cj["g"] == "agressao"].groupby(k)["obitos"].sum()
    o["ob_fogo"] = cj[cj["causa"] == "agressao_arma_fogo"].groupby(k)["obitos"].sum()
    o["ob_transito"] = cj[cj["g"] == "transito"].groupby(k)["obitos"].sum()
    o["ob_suicidio"] = cj[cj["g"] == "suicidio"].groupby(k)["obitos"].sum()
    o = o.fillna(0)
    o["pop"] = p
    return o.reset_index()


# ---------- Tabela 5: regioes ----------
t5 = taxas(["regiao"], cj, pj)
t5["taxa_agressao_100k"] = t5["ob_agressao"] / t5["pop"] * K
t5["taxa_arma_fogo_100k"] = t5["ob_fogo"] / t5["pop"] * K
t5["taxa_transito_100k"] = t5["ob_transito"] / t5["pop"] * K
t5["taxa_suicidio_100k"] = t5["ob_suicidio"] / t5["pop"] * K
t5["pct_homicidios_brasil"] = t5["ob_agressao"] / t5.groupby("periodo")["ob_agressao"].transform("sum") * 100
t5["_o"] = t5["periodo"].map(ordem)
t5["_r"] = t5["regiao"].map({v: i for i, v in enumerate(REG.values())})
t5 = t5.sort_values(["_o", "_r"]).drop(columns=["_o", "_r"])
t5 = t5[["periodo", "regiao", "taxa_agressao_100k", "taxa_arma_fogo_100k", "taxa_transito_100k",
         "taxa_suicidio_100k", "pct_homicidios_brasil", "ob_agressao", "pop"]]
t5 = t5.rename(columns={"ob_agressao": "obitos_agressao", "pop": "pessoas_ano"})

# ---------- Tabela 6: UF ----------
t6 = taxas(["uf"], cj, pj)
t6["taxa_agressao_100k"] = t6["ob_agressao"] / t6["pop"] * K
t6["ranking"] = t6.groupby("periodo")["taxa_agressao_100k"].rank(ascending=False, method="min").astype(int)
t6["_o"] = t6["periodo"].map(ordem)
t6 = t6.sort_values(["_o", "ranking"]).drop(columns="_o")
t6 = t6[["periodo", "uf", "taxa_agressao_100k", "ranking", "ob_agressao", "pop"]]
t6 = t6.rename(columns={"ob_agressao": "obitos_agressao", "pop": "pessoas_ano"})


# ---------- quintis de IDHM_R por ano ----------
def ano_idh(p):
    anos = sorted(idh["ANO"].unique())
    ok = [a for a in anos if a <= ini[p]]
    return max(ok) if ok else anos[0]


quint = {}
for a in sorted({ano_idh(p) for p in periodos}):
    d = idh[idh["ANO"] == a].sort_values("IDHM_R").reset_index(drop=True)
    cum = d["POP"].cumsum() / d["POP"].sum()
    d["quintil"] = np.clip(np.ceil(cum * 5 - 1e-12), 1, 5).astype(int)
    quint[a] = dict(zip(d["microrregiao"], d["quintil"]))


def com_quintil(df):
    out = []
    for p in periodos:
        d = df[df["periodo"] == p].copy()
        d["quintil_IDHM_R"] = d["microrregiao"].map(quint[ano_idh(p)])
        out.append(d)
    out = pd.concat(out)
    out = out[out["quintil_IDHM_R"].notna()].copy()
    out["quintil_IDHM_R"] = out["quintil_IDHM_R"].astype(int)
    return out


# ---------- Tabela 7 ----------
cq, pq = com_quintil(cj), com_quintil(pj)
t7 = taxas(["quintil_IDHM_R"], cq, pq)
t7["ano_idhm_usado"] = t7["periodo"].map(ano_idh)
t7["taxa_agressao_100k"] = t7["ob_agressao"] / t7["pop"] * K
t7["taxa_arma_fogo_100k"] = t7["ob_fogo"] / t7["pop"] * K
t7["_o"] = t7["periodo"].map(ordem)
t7 = t7.sort_values(["_o", "quintil_IDHM_R"]).drop(columns="_o")
t7 = t7[["periodo", "ano_idhm_usado", "quintil_IDHM_R", "taxa_agressao_100k", "taxa_arma_fogo_100k",
         "ob_agressao", "pop"]].rename(columns={"ob_agressao": "obitos_agressao", "pop": "pessoas_ano"})

# ---------- Tabela 8: idosos 60+ padronizado por idade ----------
IDO = ["60-69", "70-79", "80+"]
p_id = pop_ok[pop_ok["faixa"].isin(IDO)]
c_id = cau_ok[cau_ok["faixa"].isin(IDO)]
padrao = p_id[p_id["periodo"].str.startswith("2010-2014")].groupby("faixa")["pessoas_ano"].sum()
padrao = padrao / padrao.sum()
assert len(padrao) == 3
pk = com_quintil(p_id)
ck = com_quintil(c_id)
k = ["periodo", "sexo", "quintil_IDHM_R", "faixa"]
P = pk.groupby(k)["pessoas_ano"].sum().rename("pop")
O = ck.groupby(k)["obitos"].sum().rename("obitos")
t8 = pd.concat([P, O], axis=1).fillna({"obitos": 0}).reset_index()
t8["taxa_faixa"] = t8["obitos"] / t8["pop"] * K
t8["tw"] = t8["taxa_faixa"] * t8["faixa"].map(padrao)
g = t8.groupby(["periodo", "sexo", "quintil_IDHM_R"]).agg(
    taxa_padronizada_100k=("tw", "sum"), obitos=("obitos", "sum"), pessoas_ano=("pop", "sum")).reset_index()
g["sexo"] = g["sexo"].map({1: "masculino", 2: "feminino"})
g["_o"] = g["periodo"].map(ordem)
t8 = g.sort_values(["_o", "sexo", "quintil_IDHM_R"]).drop(columns="_o")

# ---------- testes ----------
tot_ign = int(cau_ign["obitos"].sum())
ign_agr = int(cau_ign[(cau_ign["sexo"] == M) & (cau_ign["faixa"] == J) & (cau_ign["causa"].isin(AGR))]["obitos"].sum())
print(f"Obitos ignorados excluidos (todas as causas/sexos/faixas): {tot_ign}; agressao homens 15-29: {ign_agr}")
for p in periodos:
    raw = cau[(cau["periodo"] == p) & (cau["sexo"] == M) & (cau["faixa"] == J) & cau["causa"].isin(AGR)]
    raw = raw[~ignorado(raw["municipio"])]
    nac = int(raw["obitos"].sum())
    reg = int(t5[t5["periodo"] == p]["obitos_agressao"].sum())
    assert nac == reg, f"{p}: soma regioes {reg} != nacional {nac}"
    print(f"  {p}: regioes={reg} nacional={nac} OK")
for p, s in t5.groupby("periodo")["pct_homicidios_brasil"].sum().items():
    assert abs(s - 100) <= 0.1, f"{p}: pct soma {s}"
for nome, t in [("t5", t5), ("t6", t6), ("t7", t7), ("t8", t8)]:
    tc = [c for c in t.columns if c.startswith("taxa")]
    v = t[tc].to_numpy(dtype=float)
    assert np.isfinite(v).all() and (v >= 0).all(), f"{nome}: taxa negativa/infinita"
assert len(t5) == 5 * len(periodos)

# ---------- saidas ----------
def salva(t, nome):
    t.to_csv(nome, sep=";", index=False, float_format="%.4f", encoding="utf-8")


salva(t5, "ONDE_TABELA5_REGIOES_V2.csv")
salva(t6, "ONDE_TABELA6_UF_V2.csv")
salva(t7, "ONDE_TABELA7_IDHM_HOMICIDIO_V2.csv")
salva(t8, "ONDE_TABELA8_IDOSOS_IDHM_V2.csv")

fig, ax = plt.subplots(figsize=(9, 5.5))
x = list(range(len(periodos)))
for r in REG.values():
    d = t5[t5["regiao"] == r].set_index("periodo").reindex(periodos)
    ax.plot(x, d["taxa_agressao_100k"], marker="o", label=r)
ax.set_xticks(x)
ax.set_xticklabels([p.replace(" pandemia", "") for p in periodos])
ax.set_xlabel("Periodo")
ax.set_ylabel("Agressoes por 100 mil homens 15-29")
ax.set_title("Taxa de agressao de homens 15-29 por grande regiao")
ax.grid(alpha=.3)
ax.legend(title="Regiao")
fig.tight_layout()
fig.savefig("ONDE_FIGURA4_REGIOES_V2.png", dpi=150)

print("TESTES OK: somas por regiao = total nacional; pct=100 (+-0,1); taxas finitas e >= 0")
