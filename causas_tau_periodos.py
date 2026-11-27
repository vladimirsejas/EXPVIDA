"""Projeto EXPVIDA (C:\EXPVIDA). Abra no VS Code e clique em Run Python File.

Estima tau por causa, sexo, faixa etaria e periodo. Reutiliza a matriz de causas e
as rotinas do modelo/bootstrap ja existentes em causas_tau.py e validacao_tau.py.
Nao baixa dados nem altera arquivos de entrada.
"""
import os
import numpy as np
import pandas as pd

import causas_tau as ct
import divergencia_modelo as dm
import validacao_tau as vt

P = os.path.dirname(os.path.abspath(__file__))

PERIODOS = [
    "2000-2004",
    "2005-2009",
    "2010-2014",
    "2015-2019",
    "2020-2021 pandemia",
    "2022-2024",
]
B = 300
MIN_OBITOS = 300

ARQUIVO_2015_2019 = "CAUSAS_OBITOS_2015_2019_V2.csv"
ARQUIVO_OUTROS = "CAUSAS_OBITOS_OUTROS_PERIODOS_V2.csv"


def ler_causas(data_dir=P):
    """Une os dois arquivos V2 e associa 2015-2019 ao primeiro."""
    primeiro = pd.read_csv(
        os.path.join(data_dir, ARQUIVO_2015_2019),
        sep=";",
        dtype={"microrregiao": str},
    )
    if "periodo" in primeiro.columns:
        primeiro = primeiro.drop(columns=["periodo"])
    primeiro.insert(0, "periodo", "2015-2019")
    outros = pd.read_csv(
        os.path.join(data_dir, ARQUIVO_OUTROS),
        sep=";",
        dtype={"microrregiao": str},
    )
    obrigatorias = {"periodo", "microrregiao", "sexo", "idade_inicio", "causa", "obitos"}
    for nome, quadro in (("2015-2019", primeiro), ("outros periodos", outros)):
        faltam = obrigatorias - set(quadro.columns)
        if faltam:
            raise ValueError(f"Colunas ausentes em {nome}: {sorted(faltam)}")
    dados = pd.concat([primeiro, outros], ignore_index=True)
    desconhecidos = sorted(set(dados["periodo"].dropna()) - set(PERIODOS))
    if desconhecidos:
        raise ValueError(f"Periodos fora da especificacao: {desconhecidos}")
    dados["sexo"] = pd.to_numeric(dados["sexo"], errors="raise").astype(int)
    dados["idade_inicio"] = pd.to_numeric(dados["idade_inicio"], errors="raise").astype(int)
    dados["obitos"] = pd.to_numeric(dados["obitos"], errors="raise")
    return dados


def selecionar_blocos_uf(codigos):
    """Reproduz a definicao dos blocos de UF usada em causas_tau.py."""
    uf = np.array([str(c)[:2] for c in codigos])
    return [np.where(uf == u)[0] for u in sorted(set(uf))]


def analisar_periodo(df, periodo, D, PY, codigos, B=B, min_obitos=MIN_OBITOS):
    """Executa a mesma estimacao e bootstrap de causas_tau.py para um periodo."""
    parte = df[df.periodo == periodo]
    if parte.empty:
        raise ValueError(f"Nao ha registros de causas para o periodo {periodo}")

    observadas = {}
    OE, info = {}, {}
    causas = sorted(parte.causa.unique())
    for sx in (1, 2):
        total = ct.matriz_causa(parte, codigos, sx, None)
        referencia = D[(periodo, sx)]
        observadas[sx] = {
            "sexo": dm.SEXOS[sx],
            "obitos_expvida": float(referencia.sum()),
            "obitos_causas": float(total.sum()),
            "diferenca": float(total.sum() - referencia.sum()),
            "microrregioes_com_diferenca": int((np.abs(total - referencia).sum(1) > 0).sum()),
            "maior_diferenca_absoluta": float(np.abs(total - referencia).max()),
        }

        for causa in causas + ["todas"]:
            M = ct.matriz_causa(parte, codigos, sx, None if causa == "todas" else causa)
            for faixa in ct.GRUPOS_IDADE:
                colunas = ct.FAIXAS[faixa]
                nobs = float(M[:, colunas].sum())
                if nobs >= min_obitos:
                    chave = (sx, causa, faixa)
                    OE[chave] = dm.esperados(M, PY[(periodo, sx)], colunas)
                    info[chave] = nobs

    if not OE:
        return pd.DataFrame(columns=["periodo", "sexo", "causa", "faixa", "obitos", "tau", "ic_inf", "ic_sup"]), observadas

    estimativas = {
        chave: (lambda ajuste: (ajuste["mu"], ajuste["tau"], ajuste["u"]))(
            dm.ajustar(*valores)
        )
        for chave, valores in OE.items()
    }
    blocos = selecionar_blocos_uf(codigos)
    rng = np.random.default_rng(vt.SEMENTE)
    selecoes = [
        np.concatenate([blocos[i] for i in rng.integers(0, len(blocos), len(blocos))])
        for _ in range(B)
    ]
    pontos = {chave: (valor[0], valor[1]) for chave, valor in estimativas.items()}
    vt._init(OE)
    replicacoes = [vt._rep_bloco((selecao, pontos)) for selecao in selecoes]

    saida = []
    for chave in OE:
        valores = np.array([rep[chave] for rep in replicacoes], dtype=float)
        inferior, superior = np.percentile(valores, [2.5, 97.5])
        sx, causa, faixa = chave
        saida.append({
            "periodo": periodo,
            "sexo": dm.SEXOS[sx],
            "causa": causa,
            "faixa": faixa,
            "obitos": int(info[chave]),
            "tau": estimativas[chave][1],
            "ic_inf": inferior,
            "ic_sup": superior,
        })
    return pd.DataFrame(saida), observadas


def executar(data_dir=P, periodos=None, B=None, min_obitos=None, gravar=True):
    """Executa somente os periodos selecionados; parametros menores permitem teste rapido."""
    dados = ler_causas(data_dir)
    D, PY, codigos = dm.carregar()
    periodos = PERIODOS if periodos is None else list(periodos)
    B = globals()["B"] if B is None else int(B)
    min_obitos = MIN_OBITOS if min_obitos is None else int(min_obitos)

    resultados, conferencias = [], []
    for periodo in periodos:
        if periodo not in PERIODOS:
            raise ValueError(f"Periodo desconhecido: {periodo}")
        estimativas, conferencia = analisar_periodo(
            dados, periodo, D, PY, codigos, B=B, min_obitos=min_obitos
        )
        resultados.append(estimativas)
        for sx in (1, 2):
            linha = dict(periodo=periodo, **conferencia[sx])
            conferencias.append(linha)

    tabela_tau = pd.concat(resultados, ignore_index=True) if resultados else pd.DataFrame(
        columns=["periodo", "sexo", "causa", "faixa", "obitos", "tau", "ic_inf", "ic_sup"]
    )
    tabela_conferencia = pd.DataFrame(conferencias)
    if gravar:
        tabela_tau.to_csv(os.path.join(data_dir, "CAUSAS_TAU_PERIODOS_V2.csv"), sep=";", index=False)
        tabela_conferencia.to_csv(
            os.path.join(data_dir, "CAUSAS_CONFERENCIA_PERIODOS_V2.csv"), sep=";", index=False
        )
    return tabela_tau, tabela_conferencia


def main():
    tabela, _ = executar()
    print("Pronto:", len(tabela), "estimativas de tau nos seis periodos.")


if __name__ == "__main__":
    main()
