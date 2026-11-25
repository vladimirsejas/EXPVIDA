# Brasil inteiro: expectativa de vida e mortalidade por idade, por sexo e território

Gerado por brasil_expectativa.py (projeto "Quando o território importa", pasta C:\EXPVIDA). Dados públicos do DATASUS: óbitos do SIM por residência, 2000 a 2024, e população do IBGE/POPSVS por município, sexo e idade. Tábuas de vida abreviadas por sexo, com óbitos e pessoas-ano somados em cada janela. Incerteza (IC 95%) por simulação de Poisson, considerando só os óbitos (a incerteza da população não entra). Resultados descritivos e ecológicos: descrevem territórios, não indivíduos, e não provam causa.

e0 = expectativa de vida ao nascer. e0-80 = anos vividos entre 0 e 80 anos (robusta quando há poucos óbitos). Unidade "instável" = menos de 100 óbitos naquele sexo e período.

## Brasil

| Período | Sexo | Óbitos | e0 (IC 95%) | e0-80 (IC 95%) | q15-60 | q0 por mil |
|---|---|---|---|---|---|---|
| 2000-2004 | homens | 2843728 | 70.7 (70.7 a 70.7) | 67.1 (67.1 a 67.1) | 0.212 | 19.7 |
| 2000-2004 | mulheres | 2048805 | 78.6 (78.6 a 78.6) | 72.4 (72.3 a 72.4) | 0.105 | 16.0 |
| 2005-2009 | homens | 3013546 | 71.8 (71.8 a 71.8) | 68.0 (68.0 a 68.0) | 0.199 | 16.5 |
| 2005-2009 | mulheres | 2232287 | 79.6 (79.5 a 79.6) | 73.0 (73.0 a 73.0) | 0.096 | 13.5 |
| 2010-2014 | homens | 3350580 | 72.1 (72.1 a 72.1) | 68.4 (68.3 a 68.4) | 0.194 | 14.3 |
| 2010-2014 | mulheres | 2554590 | 79.8 (79.7 a 79.8) | 73.4 (73.3 a 73.4) | 0.092 | 12.0 |
| 2015-2019 | homens | 3648001 | 72.8 (72.8 a 72.8) | 69.0 (69.0 a 69.0) | 0.181 | 13.1 |
| 2015-2019 | mulheres | 2888969 | 80.2 (80.2 a 80.2) | 73.7 (73.7 a 73.7) | 0.087 | 11.1 |
| 2020-2021 pandemia | homens | 1885841 | 70.5 (70.5 a 70.5) | 67.7 (67.7 a 67.7) | 0.214 | 12.3 |
| 2020-2021 pandemia | mulheres | 1498217 | 78.0 (77.9 a 78.0) | 72.6 (72.6 a 72.7) | 0.111 | 10.4 |
| 2022-2024 | homens | 2480187 | 73.1 (73.1 a 73.1) | 69.3 (69.3 a 69.3) | 0.175 | 13.2 |
| 2022-2024 | mulheres | 2054889 | 80.0 (80.0 a 80.0) | 73.7 (73.7 a 73.8) | 0.086 | 11.2 |

## e0 por UF e período

As duas últimas colunas são a diferença em anos de e0 em relação a 2015-2019 (pandemia e depois dela).

### Homens

| UF | 2000-2004 | 2005-2009 | 2010-2014 | 2015-2019 | 2020-2021 pandemia | 2022-2024 | Δ pandemia | Δ 2022-24 |
|---|---|---|---|---|---|---|---|---|
| RO | 70.8 | 72.8 | 72.5 | 73.5 | 69.3 | 72.7 | -4.2 | -0.8 |
| AC | 72.6 | 72.9 | 72.6 | 72.2 | 69.2 | 73.6 | -3.0 | +1.4 |
| AM | 74.5 | 74.1 | 72.8 | 72.5 | 67.5 | 72.6 | -5.0 | +0.1 |
| RR | 73.9 | 74.1 | 73.5 | 72.0 | 67.4 | 72.4 | -4.6 | +0.4 |
| PA | 75.9 | 74.4 | 73.1 | 72.8 | 70.2 | 73.6 | -2.6 | +0.7 |
| AP | 73.2 | 75.4 | 73.3 | 71.9 | 67.2 | 71.0 | -4.6 | -0.9 |
| TO | 76.5 | 75.6 | 74.1 | 74.2 | 71.0 | 73.7 | -3.2 | -0.5 |
| MA | 79.7 | 77.5 | 75.3 | 74.2 | 71.2 | 73.7 | -3.0 | -0.5 |
| PI | 75.8 | 74.6 | 73.7 | 73.6 | 71.3 | 73.1 | -2.3 | -0.6 |
| CE | 74.1 | 74.0 | 72.8 | 72.6 | 70.2 | 73.1 | -2.4 | +0.6 |
| RN | 75.1 | 75.0 | 73.4 | 72.4 | 71.2 | 73.8 | -1.2 | +1.4 |
| PB | 73.8 | 73.2 | 71.9 | 72.6 | 70.8 | 72.8 | -1.8 | +0.2 |
| PE | 68.0 | 69.8 | 70.7 | 70.7 | 69.2 | 71.5 | -1.5 | +0.8 |
| AL | 70.2 | 70.3 | 69.2 | 70.5 | 68.9 | 71.0 | -1.5 | +0.6 |
| SE | 70.9 | 71.9 | 71.0 | 70.7 | 69.5 | 72.4 | -1.3 | +1.6 |
| BA | 74.3 | 74.1 | 72.8 | 72.5 | 70.3 | 72.0 | -2.2 | -0.5 |
| MG | 71.9 | 72.4 | 73.0 | 74.1 | 72.5 | 74.3 | -1.6 | +0.2 |
| ES | 69.6 | 70.8 | 71.9 | 73.4 | 71.2 | 73.7 | -2.2 | +0.3 |
| RJ | 67.4 | 69.0 | 70.4 | 71.0 | 68.5 | 72.3 | -2.5 | +1.3 |
| SP | 68.8 | 71.3 | 72.3 | 73.5 | 70.9 | 73.5 | -2.7 | -0.0 |
| PR | 69.8 | 70.7 | 71.5 | 73.1 | 70.4 | 73.0 | -2.7 | -0.1 |
| SC | 70.8 | 72.2 | 73.4 | 74.7 | 72.8 | 75.1 | -1.9 | +0.4 |
| RS | 69.6 | 70.9 | 71.8 | 72.8 | 71.6 | 73.3 | -1.2 | +0.5 |
| MS | 70.6 | 71.0 | 71.7 | 72.9 | 70.0 | 72.1 | -3.0 | -0.8 |
| MT | 71.0 | 71.9 | 71.8 | 72.9 | 69.1 | 72.4 | -3.8 | -0.5 |
| GO | 72.0 | 72.6 | 71.7 | 72.6 | 69.8 | 73.4 | -2.8 | +0.7 |
| DF | 71.9 | 73.3 | 74.0 | 75.8 | 72.3 | 76.2 | -3.5 | +0.4 |

### Mulheres

| UF | 2000-2004 | 2005-2009 | 2010-2014 | 2015-2019 | 2020-2021 pandemia | 2022-2024 | Δ pandemia | Δ 2022-24 |
|---|---|---|---|---|---|---|---|---|
| RO | 78.9 | 80.4 | 79.6 | 80.2 | 76.4 | 79.8 | -3.7 | -0.4 |
| AC | 79.3 | 80.0 | 79.8 | 79.3 | 76.3 | 79.5 | -3.0 | +0.3 |
| AM | 82.1 | 80.9 | 80.1 | 79.8 | 74.7 | 79.7 | -5.1 | -0.1 |
| RR | 81.1 | 81.0 | 81.1 | 79.0 | 74.2 | 78.8 | -4.8 | -0.1 |
| PA | 82.8 | 81.8 | 81.1 | 80.7 | 77.8 | 80.5 | -2.9 | -0.2 |
| AP | 82.7 | 87.1 | 81.8 | 80.2 | 75.7 | 79.2 | -4.5 | -1.1 |
| TO | 81.5 | 81.1 | 80.4 | 80.8 | 78.4 | 80.8 | -2.4 | +0.0 |
| MA | 87.4 | 85.6 | 83.8 | 82.1 | 79.4 | 81.0 | -2.6 | -1.0 |
| PI | 81.4 | 81.0 | 80.8 | 80.9 | 79.2 | 80.6 | -1.8 | -0.3 |
| CE | 80.6 | 81.1 | 81.2 | 80.7 | 78.6 | 80.9 | -2.1 | +0.3 |
| RN | 81.6 | 82.7 | 81.7 | 80.9 | 79.2 | 81.2 | -1.6 | +0.3 |
| PB | 80.1 | 80.6 | 80.0 | 80.2 | 78.7 | 80.3 | -1.5 | +0.1 |
| PE | 77.0 | 78.3 | 78.8 | 78.9 | 77.0 | 79.2 | -1.8 | +0.3 |
| AL | 77.7 | 79.0 | 78.5 | 78.1 | 76.4 | 78.2 | -1.7 | +0.1 |
| SE | 77.9 | 79.5 | 79.5 | 79.7 | 78.3 | 80.4 | -1.4 | +0.7 |
| BA | 81.6 | 82.0 | 81.4 | 81.3 | 79.3 | 80.5 | -2.0 | -0.8 |
| MG | 79.4 | 80.1 | 80.3 | 81.1 | 79.3 | 80.6 | -1.8 | -0.5 |
| ES | 78.7 | 79.7 | 80.7 | 81.5 | 78.9 | 81.0 | -2.6 | -0.5 |
| RJ | 76.7 | 77.9 | 78.2 | 78.6 | 75.8 | 78.8 | -2.8 | +0.2 |
| SP | 77.7 | 79.2 | 79.7 | 80.2 | 78.0 | 79.9 | -2.3 | -0.3 |
| PR | 77.3 | 78.5 | 79.1 | 80.2 | 78.0 | 80.0 | -2.2 | -0.2 |
| SC | 78.3 | 79.8 | 80.4 | 81.3 | 79.7 | 80.8 | -1.6 | -0.4 |
| RS | 77.7 | 78.8 | 79.3 | 80.0 | 78.5 | 79.6 | -1.5 | -0.3 |
| MS | 78.2 | 78.7 | 79.4 | 79.7 | 77.0 | 79.1 | -2.7 | -0.6 |
| MT | 78.8 | 79.5 | 79.2 | 80.1 | 76.5 | 79.7 | -3.5 | -0.4 |
| GO | 79.1 | 79.6 | 78.8 | 80.0 | 77.2 | 80.0 | -2.8 | -0.0 |
| DF | 79.6 | 80.6 | 81.3 | 82.7 | 80.2 | 83.0 | -2.6 | +0.3 |

## Desigualdade entre microrregiões (sem peso por população)

Cada linha resume a distribuição de e0 e e0-80 entre as microrregiões do IBGE com ao menos 100 óbitos no sexo e no período. P10, P50 e P90 são os percentis 10, 50 e 90; a amplitude é P90 menos P10, em anos.

| Período | Sexo | Microrregiões | e0-80 P10 | P50 | P90 | amplitude | e0 P10 | P50 | P90 | amplitude |
|---|---|---|---|---|---|---|---|---|---|---|
| 2000-2004 | homens | 557 | 66.0 | 68.3 | 71.1 | 5.1 | 68.9 | 72.5 | 79.6 | 10.7 |
| 2000-2004 | mulheres | 554 | 71.3 | 72.7 | 74.1 | 2.8 | 76.4 | 79.3 | 85.7 | 9.3 |
| 2005-2009 | homens | 557 | 66.9 | 68.7 | 70.9 | 4.0 | 70.1 | 72.8 | 78.5 | 8.3 |
| 2005-2009 | mulheres | 555 | 72.1 | 73.2 | 74.4 | 2.3 | 77.8 | 80.2 | 84.7 | 6.9 |
| 2010-2014 | homens | 557 | 67.2 | 68.9 | 70.4 | 3.1 | 70.6 | 73.0 | 76.5 | 5.9 |
| 2010-2014 | mulheres | 556 | 72.6 | 73.5 | 74.4 | 1.8 | 78.1 | 80.2 | 83.6 | 5.5 |
| 2015-2019 | homens | 557 | 67.6 | 69.3 | 70.7 | 3.0 | 71.2 | 73.5 | 75.8 | 4.6 |
| 2015-2019 | mulheres | 556 | 72.9 | 73.8 | 74.6 | 1.6 | 78.5 | 80.4 | 82.7 | 4.2 |
| 2020-2021 pandemia | homens | 557 | 66.3 | 68.0 | 69.7 | 3.4 | 68.9 | 71.2 | 73.9 | 5.1 |
| 2020-2021 pandemia | mulheres | 554 | 71.8 | 72.8 | 73.8 | 2.1 | 76.3 | 78.4 | 80.8 | 4.5 |
| 2022-2024 | homens | 557 | 67.7 | 69.2 | 70.6 | 2.9 | 71.3 | 73.2 | 75.3 | 3.9 |
| 2022-2024 | mulheres | 556 | 72.8 | 73.7 | 74.4 | 1.6 | 78.2 | 80.1 | 81.8 | 3.6 |

## Extremos entre microrregiões em 2015-2019 (e0-80)

### Homens

| Posição | Microrregião | UF | e0-80 | Óbitos |
|---|---|---|---|---|
| menores | Microrregião de Laranjeiras | SE | 65.0 | 1651 |
| menores | Microrregião de Itabaiana | SE | 65.8 | 3499 |
| menores | Microrregião de Itaguai | RJ | 65.9 | 5625 |
| menores | Microrregião de Propria | SE | 66.0 | 1868 |
| menores | Microrregião de Bonito | PE | 66.0 | 5297 |
| maiores | Microrregião de Muana | PA | 72.0 | 1649 |
| maiores | Microrregião de Breves | PA | 72.1 | 1980 |
| maiores | Microrregião de Concordia | SC | 72.1 | 2536 |
| maiores | Microrregião de Portel | PA | 72.3 | 1156 |
| maiores | Microrregião de Maraa | AM | 74.2 | 141 |

### Mulheres

| Posição | Microrregião | UF | e0-80 | Óbitos |
|---|---|---|---|---|
| menores | Microrregião de Itaguai | RJ | 71.4 | 4176 |
| menores | Microrregião de Caracarai | RR | 71.9 | 385 |
| menores | Microrregião de Atalaia | AL | 72.0 | 3717 |
| menores | Microrregião de Laranjeiras | SE | 72.1 | 1186 |
| menores | Microrregião de Escada | PE | 72.1 | 7838 |
| maiores | Microrregião de Santa Luzia | PB | 75.3 | 548 |
| maiores | Microrregião de Santa Maria Da Vitoria | BA | 75.3 | 1872 |
| maiores | Microrregião de Concordia | SC | 75.4 | 2058 |
| maiores | Microrregião de Livramento De Nossa Senhora | BA | 75.7 | 1273 |
| maiores | Microrregião de Sananduva | RS | 75.8 | 1060 |

## Desigualdade por idade entre microrregiões

Taxa de mortalidade por mil pessoas em cada faixa etária, entre microrregiões com ao menos 20 óbitos na faixa. A razão é P90 dividido por P10: quantas vezes a taxa do território no 90º percentil supera a do 10º. Isto responde onde, na vida, a desigualdade territorial é maior, e se a pandemia a alterou por idade.

### Homens

| Idade | Microrregiões (2015-2019) | Taxa P10 (2015-2019) | P50 | P90 | Razão P90/P10 2015-2019 | 2020-2021 pandemia | 2022-2024 |
|---|---|---|---|---|---|---|---|
| 0 | 528 | 9.84 | 12.90 | 17.54 | 1.78 | 1.89 | 1.78 |
| 1-4 | 213 | 0.42 | 0.57 | 0.85 | 2.04 | 2.90 | 2.15 |
| 5-9 | 111 | 0.18 | 0.28 | 0.39 | 2.22 | 1.76 | 2.38 |
| 10-14 | 197 | 0.26 | 0.41 | 0.55 | 2.08 | 2.55 | 2.31 |
| 15-19 | 499 | 0.96 | 1.60 | 2.87 | 3.00 | 2.98 | 2.62 |
| 20-24 | 533 | 1.44 | 2.33 | 3.78 | 2.62 | 2.71 | 2.59 |
| 25-29 | 532 | 1.53 | 2.47 | 3.67 | 2.40 | 2.28 | 2.25 |
| 30-34 | 542 | 1.79 | 2.70 | 3.66 | 2.04 | 1.97 | 1.95 |
| 35-39 | 545 | 2.28 | 3.09 | 4.05 | 1.78 | 1.72 | 1.83 |
| 40-44 | 550 | 3.04 | 3.92 | 5.04 | 1.66 | 1.60 | 1.65 |
| 45-49 | 550 | 4.24 | 5.23 | 6.47 | 1.53 | 1.56 | 1.58 |
| 50-54 | 554 | 5.87 | 7.46 | 8.82 | 1.50 | 1.54 | 1.47 |
| 55-59 | 554 | 8.14 | 10.26 | 12.31 | 1.51 | 1.60 | 1.44 |
| 60-64 | 555 | 11.63 | 15.11 | 17.87 | 1.54 | 1.64 | 1.50 |
| 65-69 | 554 | 16.99 | 21.81 | 26.39 | 1.55 | 1.64 | 1.52 |
| 70-74 | 554 | 24.83 | 32.25 | 38.79 | 1.56 | 1.64 | 1.46 |
| 75-79 | 554 | 38.58 | 49.64 | 59.85 | 1.55 | 1.60 | 1.51 |
| 80+ | 557 | 87.88 | 108.30 | 123.69 | 1.41 | 1.39 | 1.38 |

### Mulheres

| Idade | Microrregiões (2015-2019) | Taxa P10 (2015-2019) | P50 | P90 | Razão P90/P10 2015-2019 | 2020-2021 pandemia | 2022-2024 |
|---|---|---|---|---|---|---|---|
| 0 | 523 | 8.37 | 10.96 | 14.22 | 1.70 | 1.90 | 1.82 |
| 1-4 | 172 | 0.35 | 0.50 | 0.80 | 2.29 | 2.77 | 2.49 |
| 5-9 | 76 | 0.15 | 0.22 | 0.33 | 2.27 | 3.33 | 1.98 |
| 10-14 | 107 | 0.20 | 0.26 | 0.35 | 1.81 | 2.62 | 2.25 |
| 15-19 | 233 | 0.34 | 0.47 | 0.65 | 1.91 | 2.15 | 1.74 |
| 20-24 | 286 | 0.43 | 0.57 | 0.75 | 1.73 | 1.85 | 1.79 |
| 25-29 | 328 | 0.52 | 0.68 | 0.89 | 1.72 | 1.90 | 1.85 |
| 30-34 | 405 | 0.71 | 0.91 | 1.19 | 1.68 | 1.79 | 1.74 |
| 35-39 | 467 | 1.03 | 1.30 | 1.70 | 1.66 | 1.74 | 1.69 |
| 40-44 | 492 | 1.47 | 1.85 | 2.31 | 1.57 | 1.65 | 1.60 |
| 45-49 | 518 | 2.14 | 2.68 | 3.41 | 1.59 | 1.71 | 1.61 |
| 50-54 | 533 | 3.09 | 3.92 | 4.74 | 1.53 | 1.63 | 1.55 |
| 55-59 | 549 | 4.58 | 5.70 | 6.99 | 1.53 | 1.72 | 1.57 |
| 60-64 | 551 | 6.75 | 8.70 | 10.77 | 1.59 | 1.66 | 1.51 |
| 65-69 | 553 | 10.65 | 13.73 | 16.55 | 1.55 | 1.68 | 1.53 |
| 70-74 | 552 | 17.45 | 21.35 | 25.93 | 1.49 | 1.60 | 1.46 |
| 75-79 | 554 | 28.12 | 34.89 | 41.73 | 1.48 | 1.57 | 1.44 |
| 80+ | 555 | 76.72 | 91.95 | 104.22 | 1.36 | 1.36 | 1.32 |

## Óbitos lidos e excluídos por período

Óbitos com sexo ou idade ignorados saem de todas as tábuas. Óbitos com município de residência não identificado (por exemplo, código terminado em 0000) ficam fora dos municípios e das microrregiões, mas entram nos totais da UF e do Brasil.

| Período | Lidos | Sexo ignorado | Idade ignorada | Município não identificado |
|---|---|---|---|---|
| 2000-2004 | 4917398 | 3885 | 20980 | 17463 |
| 2005-2009 | 5266437 | 2380 | 18224 | 9819 |
| 2010-2014 | 5926124 | 2868 | 18086 | 9558 |
| 2015-2019 | 6553132 | 3072 | 13090 | 7303 |
| 2020-2021 pandemia | 3389473 | 1313 | 4102 | 2486 |
| 2022-2024 | 4541891 | 1663 | 5152 | 3645 |

## Municípios instáveis

| Período | Sexo | Municípios | Instáveis (menos de 100 óbitos) |
|---|---|---|---|
| 2000-2004 | homens | 5570 | 2041 |
| 2000-2004 | mulheres | 5570 | 2747 |
| 2005-2009 | homens | 5570 | 1809 |
| 2005-2009 | mulheres | 5570 | 2583 |
| 2010-2014 | homens | 5570 | 1547 |
| 2010-2014 | mulheres | 5570 | 2299 |
| 2015-2019 | homens | 5570 | 1339 |
| 2015-2019 | mulheres | 5570 | 1994 |
| 2020-2021 pandemia | homens | 5570 | 2708 |
| 2020-2021 pandemia | mulheres | 5570 | 3349 |
| 2022-2024 | homens | 5570 | 1992 |
| 2022-2024 | mulheres | 5570 | 2660 |

## Limites

O sub-registro de óbitos e a qualidade da causa e da idade foram maiores no início dos anos 2000 e em municípios pequenos e pobres, o que tende a elevar a expectativa de vida aparente desses lugares; este é um limite dos dados, não corrigido aqui. As populações do IBGE (POPSVS) são estimativas que foram revisadas com os censos, e o ajuste de períodos distintos pode mudar tendências. A incerteza mostrada vem só da variação aleatória dos óbitos. Microrregião é a divisão do IBGE vigente na tabela CADMUN do DATASUS. A idade média ao morrer não é expectativa de vida, e as comparações entre territórios são ecológicas: mostram associação entre lugares, nunca causa para pessoas. A associação com o CEP, pedida pelo professor, ainda não foi feita: aqui o menor recorte é o município.

