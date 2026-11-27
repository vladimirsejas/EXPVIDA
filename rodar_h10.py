r"""Projeto EXPVIDA (C:\EXPVIDA). Abra no VS Code e clique em Run Python File."""
import csv
from pathlib import Path

from h10_shapley import run_h10


DATA_DIR = Path(r"C:\EXPVIDA")
PERIODOS = (
    "2000-2004",
    "2005-2009",
    "2010-2014",
    "2015-2019",
    "2020-2021 pandemia",
    "2022-2024",
)
SEXOS = (1, 2)
FRACOES = (0.0, 0.5, 1.0)
RESULTADOS = DATA_DIR / "H10_RESULTADOS_V2.csv"
DIAGNOSTICOS = DATA_DIR / "H10_DIAGNOSTICOS_V2.csv"

COLUNAS_RESULTADOS = (
    "periodo",
    "sexo",
    "fracao_indeterminada",
    "grupo",
    "contribuicao",
    "percentual_da_reducao",
    "variancia_observada",
    "variancia_todas_equalizadas",
)
COLUNAS_DIAGNOSTICOS = (
    "periodo",
    "sexo",
    "fracao_indeterminada",
    "territories",
    "cause_deaths",
    "all_cause_deaths",
    "net_difference",
    "cells_with_difference",
    "max_abs_cell_difference",
)


def principal():
    rodadas = len(PERIODOS) * len(SEXOS) * len(FRACOES)
    concluidas = 0
    with RESULTADOS.open("w", encoding="utf-8", newline="") as arquivo_resultados, DIAGNOSTICOS.open(
        "w", encoding="utf-8", newline=""
    ) as arquivo_diagnosticos:
        escritor_resultados = csv.DictWriter(
            arquivo_resultados, fieldnames=COLUNAS_RESULTADOS, delimiter=";"
        )
        escritor_diagnosticos = csv.DictWriter(
            arquivo_diagnosticos, fieldnames=COLUNAS_DIAGNOSTICOS, delimiter=";"
        )
        escritor_resultados.writeheader()
        escritor_diagnosticos.writeheader()

        for periodo in PERIODOS:
            for sexo in SEXOS:
                for fracao in FRACOES:
                    resultado = run_h10(
                        data_dir=DATA_DIR,
                        period=periodo,
                        sex=sexo,
                        strict_closure=False,
                        agrupamento="violencia_detalhada",
                        versao_causas="v2",
                        idade_inicial=1,
                        fracao_indeterminada_agressao=fracao,
                    )
                    variancia_reducao = resultado["variance_reduction"]
                    for grupo, contribuicao in zip(
                        resultado["group_names"], resultado["contributions"]
                    ):
                        percentual = (
                            float(contribuicao) / variancia_reducao * 100.0
                            if variancia_reducao != 0
                            else 0.0
                        )
                        escritor_resultados.writerow(
                            {
                                "periodo": periodo,
                                "sexo": sexo,
                                "fracao_indeterminada": fracao,
                                "grupo": grupo,
                                "contribuicao": float(contribuicao),
                                "percentual_da_reducao": percentual,
                                "variancia_observada": resultado["variance_observed"],
                                "variancia_todas_equalizadas": resultado[
                                    "variance_all_causes_equalized"
                                ],
                            }
                        )
                    escritor_diagnosticos.writerow(
                        {
                            "periodo": periodo,
                            "sexo": sexo,
                            "fracao_indeterminada": fracao,
                            **resultado["diagnostics"],
                        }
                    )
                    arquivo_resultados.flush()
                    arquivo_diagnosticos.flush()
                    concluidas += 1
                    print(
                        f"[{concluidas}/{rodadas}] {periodo} sexo={sexo} "
                        f"fracao_indeterminada={fracao} concluida",
                        flush=True,
                    )


if __name__ == "__main__":
    principal()
