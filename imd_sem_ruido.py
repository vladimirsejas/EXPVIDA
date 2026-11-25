"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
Verificacao: a IMD NAO e a idade de inicio da divergencia.
Para cada idade de inicio (15, 40, 60) e cada RR (1,4 e 1,2), cria-se uma divergencia conhecida (mortalidade esperada
multiplicada por RR a partir daquela idade), SEM ruido de Poisson, e calcula-se a IMD exata (a que a regra daria se nao
houvesse acaso). Grava IMD_SEM_RUIDO.csv (mediana e quartis entre as microrregioes com |G| >= 0,3 ano).
Como usar: "Run Python File". Precisa de numpy e pandas; nao baixa nada, nao cria pastas. Leva poucos segundos.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergencia_modelo as dm
from idt_experimento import esperados_por_idade
from imd_alternativa import imd_de, tabua_ref, MIN_G

D, PY, cod = dm.carregar()
linhas = []
for sx in (1, 2):
    d, py = D[("2015-2019", sx)], PY[("2015-2019", sx)]
    ref = tabua_ref(d, py, sx)
    E = esperados_por_idade(d, py)
    for rr in (1.4, 1.2):
        for inicio in (15, 40, 60):
            f = np.ones(len(dm.IDADES))
            f[dm.IDADES.index(inicio):] = rr
            l, L = dm.tabua_vec(E * f[None, :], py, sx)
            c = dm.arriaga_vec(ref, l, L)
            G = c.sum(1)
            ix = imd_de(c, G)
            ok = np.abs(G) >= MIN_G
            idades = np.array(dm.IDADES + [np.nan])[np.nan_to_num(ix, nan=18).astype(int)][ok]
            linhas.append({"sexo": dm.SEXOS[sx], "rr": rr, "inicio_da_divergencia": inicio, "n_microrregioes": int(ok.sum()),
                           "imd_sem_ruido_mediana": np.median(idades), "imd_q25": np.percentile(idades, 25),
                           "imd_q75": np.percentile(idades, 75)})
pd.DataFrame(linhas).to_csv(os.path.join(dm.PASTA, "IMD_SEM_RUIDO.csv"), sep=";", index=False)
print(pd.DataFrame(linhas).to_string())
