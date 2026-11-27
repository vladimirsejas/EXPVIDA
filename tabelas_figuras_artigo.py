r"""Projeto EXPVIDA (C:\EXPVIDA). Abra no VS Code e clique em Run Python File."""
from itertools import product
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PASTA = Path(__file__).resolve().parent
PERIODOS = [
    "2000-2004",
    "2005-2009",
    "2010-2014",
    "2015-2019",
    "2020-2021 pandemia",
    "2022-2024",
]
SEXOS = [(1, "homens"), (2, "mulheres")]
FRACOES = [0.0, 0.5, 1.0]
FAIXAS_TAU = ["15-19", "20-24", "25-29", "15-29", "30-59", "60+"]
GRUPOS = [
    "agressoes_intervencao_legal",
    "intencao_indeterminada",
    "suicidio",
    "transporte",
    "externas_demais",
    "covid19",
    "infecciosas_sem_covid",
    "neoplasias",
    "circulatorias",
    "respiratorias",
    "mal_definidas_sem_causa",
    "demais_doencas",
]
ROTULOS_GRUPOS = {
    "agressoes_intervencao_legal": "Agressões e intervenção legal",
    "intencao_indeterminada": "Intenção indeterminada",
    "suicidio": "Suicídio",
    "transporte": "Transporte",
    "externas_demais": "Demais causas externas",
    "covid19": "COVID-19",
    "infecciosas_sem_covid": "Infecciosas sem COVID-19",
    "neoplasias": "Neoplasias",
    "circulatorias": "Circulatórias",
    "respiratorias": "Respiratórias",
    "mal_definidas_sem_causa": "Mal definidas e sem causa",
    "demais_doencas": "Demais doenças",
}
ROTULOS_PERIODOS = {
    "2000-2004": "2000–2004",
    "2005-2009": "2005–2009",
    "2010-2014": "2010–2014",
    "2015-2019": "2015–2019",
    "2020-2021 pandemia": "2020–2021\npandemia",
    "2022-2024": "2022–2024",
}


def criar_tabela_h10(h10):
    base = h10[h10.fracao_indeterminada == 0.0]
    linhas = []
    for sexo, rotulo_sexo in SEXOS:
        parte = base[base.sexo == sexo]
        tabela = parte.pivot_table(
            index="grupo", columns="periodo", values="percentual_da_reducao", aggfunc="first"
        ).reindex(index=GRUPOS, columns=PERIODOS)
        variancias = parte.groupby("periodo").variancia_observada.first()
        for grupo in GRUPOS:
            linhas.append(
                {"sexo": rotulo_sexo, "grupo": ROTULOS_GRUPOS[grupo], **tabela.loc[grupo].to_dict()}
            )
        linhas.append(
            {
                "sexo": rotulo_sexo,
                "grupo": "Variância observada",
                **{periodo: variancias.get(periodo, np.nan) for periodo in PERIODOS},
            }
        )
    return pd.DataFrame(linhas, columns=["sexo", "grupo", *PERIODOS])


def criar_tabela_sensibilidade(h10):
    parte = h10[
        (h10.sexo == 1) & (h10.grupo == "agressoes_intervencao_legal")
    ]
    tabela = parte.pivot_table(
        index="periodo", columns="fracao_indeterminada", values="percentual_da_reducao", aggfunc="first"
    ).reindex(index=PERIODOS, columns=FRACOES)
    tabela.columns = [f"fracao_{fracao:.1f}" for fracao in FRACOES]
    tabela.index.name = "periodo"
    return tabela.reset_index()


def criar_tabela_tau(tau):
    parte = tau[(tau.causa == "agressoes") & tau.faixa.isin(FAIXAS_TAU)]
    combinacoes = pd.DataFrame(
        product(PERIODOS, [rotulo for _, rotulo in SEXOS], FAIXAS_TAU),
        columns=["periodo", "sexo", "faixa"],
    )
    return combinacoes.merge(
        parte[["periodo", "sexo", "faixa", "tau", "ic_inf", "ic_sup"]],
        on=["periodo", "sexo", "faixa"],
        how="left",
        validate="one_to_one",
    )


def criar_tabela_covid(qualidade):
    parte = qualidade[pd.to_numeric(qualidade.ano, errors="raise").between(2020, 2024)].copy()
    parte["ano"] = pd.to_numeric(parte.ano, errors="raise").astype(int)
    for coluna in ("b342_com_u07", "b342_sem_u07"):
        parte[coluna] = pd.to_numeric(parte[coluna], errors="raise")
    somas = parte.groupby("ano")[["b342_com_u07", "b342_sem_u07"]].sum()
    anos = pd.Index(range(2020, 2025), name="ano")
    return somas.reindex(anos, fill_value=0).reset_index()


def criar_figura_h10(h10, sexo, nome_saida, titulo):
    parte = h10[(h10.sexo == sexo) & (h10.fracao_indeterminada == 0.0)]
    tabela = parte.pivot_table(
        index="periodo", columns="grupo", values="percentual_da_reducao", aggfunc="first"
    ).reindex(index=PERIODOS, columns=GRUPOS).fillna(0.0)

    cores = plt.get_cmap("tab20")(np.linspace(0, 1, len(GRUPOS)))
    fig, ax = plt.subplots(figsize=(12, 7))
    base = np.zeros(len(PERIODOS), dtype=float)
    x = np.arange(len(PERIODOS))
    for grupo, cor in zip(GRUPOS, cores):
        valores = tabela[grupo].to_numpy(dtype=float)
        ax.bar(x, valores, bottom=base, color=cor, label=ROTULOS_GRUPOS[grupo])
        base += valores
    ax.set_xticks(x, [ROTULOS_PERIODOS[p] for p in PERIODOS])
    ax.set_xlabel("Período")
    ax.set_ylabel("Contribuição para a desigualdade territorial (%)")
    ax.set_title(titulo)
    ax.legend(title="Grupo de causa", loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8)
    fig.tight_layout(rect=(0, 0, 0.79, 1))
    fig.savefig(PASTA / nome_saida, dpi=300, bbox_inches="tight")
    plt.close(fig)


def criar_figura_tau(tau):
    parte = tau[
        (tau.causa == "agressoes") & (tau.sexo == "homens") & (tau.faixa == "15-29")
    ].set_index("periodo").reindex(PERIODOS)
    x = np.arange(len(PERIODOS))
    valores = parte.tau.to_numpy(dtype=float)
    inferior = parte.ic_inf.to_numpy(dtype=float)
    superior = parte.ic_sup.to_numpy(dtype=float)
    validos = np.isfinite(valores) & np.isfinite(inferior)
    erro_inferior = np.maximum(0.0, valores[validos] - inferior[validos])
    erro_superior = np.where(
        np.isfinite(superior[validos]),
        np.maximum(0.0, superior[validos] - valores[validos]),
        0.0,
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(
        x[validos],
        valores[validos],
        yerr=np.vstack([erro_inferior, erro_superior]),
        fmt="o-",
        capsize=4,
        color="#245c8a",
    )
    ax.set_xticks(x, [ROTULOS_PERIODOS[p] for p in PERIODOS])
    ax.set_xlabel("Período")
    ax.set_ylabel("Tau de agressões")
    ax.set_title("Homens — 15 a 29 anos")
    fig.tight_layout()
    fig.savefig(PASTA / "ARTIGO_FIGURA3_TAU_HOMICIDIO_V2.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def principal():
    h10 = pd.read_csv(PASTA / "H10_RESULTADOS_V2.csv", sep=";")
    tau = pd.read_csv(PASTA / "CAUSAS_TAU_PERIODOS_V2.csv", sep=";")
    qualidade = pd.read_csv(PASTA / "CAUSAS_QUALIDADE_OUTROS_V2.csv", sep=";")

    criar_tabela_h10(h10).to_csv(PASTA / "ARTIGO_TABELA1_H10_V2.csv", sep=";", index=False)
    criar_tabela_sensibilidade(h10).to_csv(
        PASTA / "ARTIGO_TABELA2_SENSIBILIDADE_V2.csv", sep=";", index=False
    )
    criar_tabela_tau(tau).to_csv(
        PASTA / "ARTIGO_TABELA3_TAU_HOMICIDIO_V2.csv", sep=";", index=False
    )
    criar_tabela_covid(qualidade).to_csv(
        PASTA / "ARTIGO_TABELA4_COVID_V2.csv", sep=";", index=False
    )
    criar_figura_h10(h10, 1, "ARTIGO_FIGURA1_H10_HOMENS_V2.png", "Homens")
    criar_figura_h10(h10, 2, "ARTIGO_FIGURA2_H10_MULHERES_V2.png", "Mulheres")
    criar_figura_tau(tau)


if __name__ == "__main__":
    principal()
