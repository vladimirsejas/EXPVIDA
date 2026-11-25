# Comparacao entre periodos: AC

Gerado por piloto_expectativa.py. Tabuas de vida abreviadas por municipio e sexo; obitos e pessoas-ano somados em cada janela. Incerteza (IC 95%) por simulacao de Poisson com 300 repeticoes, considerando so os obitos. Numeros do piloto de teste do metodo, nao conclusoes.

e0 = expectativa de vida ao nascer. e0-80 = anos vividos entre 0 e 80 anos (robusta em municipio pequeno). q15-60 = probabilidade de morrer entre 15 e 60 anos. q0 = mortalidade no primeiro ano, por mil.

## Total do estado

| Periodo | Sexo | Obitos | e0 (IC 95%) | e0-80 (IC 95%) | q15-60 | q0 |
|---|---|---|---|---|---|---|
| 2000-2004 | homens | 7947 | 72.6 (72.3 a 73.1) | 67.8 (67.5 a 68.0) | 0.192 | 22.1 |
| 2000-2004 | mulheres | 4775 | 79.3 (78.7 a 79.8) | 72.4 (72.2 a 72.6) | 0.106 | 15.5 |
| 2005-2009 | homens | 8743 | 72.9 (72.6 a 73.3) | 68.5 (68.3 a 68.8) | 0.178 | 20.0 |
| 2005-2009 | mulheres | 5348 | 80.0 (79.6 a 80.6) | 72.6 (72.4 a 72.8) | 0.101 | 15.9 |
| 2010-2014 | homens | 9987 | 72.7 (72.3 a 73.0) | 68.7 (68.5 a 68.9) | 0.181 | 17.1 |
| 2010-2014 | mulheres | 6232 | 79.8 (79.4 a 80.3) | 72.9 (72.7 a 73.0) | 0.095 | 15.3 |
| 2015-2019 | homens | 11827 | 72.2 (71.9 a 72.5) | 68.4 (68.2 a 68.6) | 0.186 | 16.9 |
| 2015-2019 | mulheres | 7413 | 79.3 (78.9 a 79.6) | 73.1 (73.0 a 73.3) | 0.091 | 13.5 |
| 2020-2021 pandemia | homens | 6206 | 69.2 (68.8 a 69.5) | 66.8 (66.5 a 67.1) | 0.215 | 19.2 |
| 2020-2021 pandemia | mulheres | 4098 | 76.3 (75.8 a 76.8) | 71.4 (71.1 a 71.7) | 0.127 | 13.6 |
| 2022-2024 | homens | 7373 | 73.6 (73.2 a 73.9) | 69.4 (69.1 a 69.6) | 0.162 | 17.7 |
| 2022-2024 | mulheres | 5202 | 79.5 (79.1 a 80.0) | 73.2 (73.0 a 73.4) | 0.086 | 15.4 |

## Anos vividos entre 0 e 80 (e0-80), por municipio e periodo

Asterisco: menos de 100 obitos naquele sexo e periodo; leitura com cautela. Os intervalos de cada numero estao no CSV.

### Homens

| Municipio | 2000-2004 | 2005-2009 | 2010-2014 | 2015-2019 | 2020-2021 pandemia | 2022-2024 |
|---|---|---|---|---|---|---|
| Acrelandia (120001) | 71.2* | 70.8 | 70.3 | 71.0 | 68.3 | 71.4 |
| Assis Brasil (120005) | 70.4* | 69.9* | 68.7* | 66.3 | 65.9* | 68.0* |
| Brasileia (120010) | 68.8 | 69.5 | 70.1 | 68.4 | 66.6 | 68.3 |
| Bujari (120013) | 74.3* | 74.9* | 70.7* | 69.0 | 67.7* | 72.2* |
| Capixaba (120017) | 73.8* | 70.1* | 69.8 | 68.0 | 70.4* | 70.1* |
| Cruzeiro do Sul (120020) | 67.7 | 68.2 | 69.1 | 68.6 | 68.6 | 69.6 |
| Epitaciolandia (120025) | 68.7 | 70.7 | 71.1 | 70.5 | 67.7 | 69.3 |
| Feijo (120030) | 70.5 | 69.8 | 68.8 | 68.8 | 67.8 | 69.4 |
| Jordao (120032) | 76.7* | 70.9* | 70.1* | 72.8* | 73.5* | 73.6* |
| Manoel Urbano (120033) | 74.2* | 72.4 | 71.0 | 69.2 | 70.2* | 70.7 |
| Marechal Thaumaturgo (120034) | 73.7* | 69.8* | 68.0 | 68.3 | 66.5* | 69.8* |
| Mancio Lima (120035) | 76.5* | 72.4* | 71.7 | 73.1 | 72.1* | 72.9* |
| Placido de Castro (120038) | 71.4 | 69.8 | 70.5 | 70.2 | 68.7 | 71.5 |
| Porto Walter (120039) | 74.1* | 68.9* | 69.5* | 72.3* | 72.9* | 72.8* |
| Rio Branco (120040) | 65.0 | 66.9 | 67.8 | 67.4 | 65.2 | 68.7 |
| Rodrigues Alves (120042) | 74.1* | 72.7* | 72.2 | 71.2 | 69.6* | 71.2 |
| Santa Rosa do Purus (120043) | 75.8* | 63.8* | 66.8* | 67.3* | 65.9* | 65.4* |
| Senador Guiomard (120045) | 71.1 | 71.4 | 69.0 | 69.0 | 67.3 | 70.1 |
| Sena Madureira (120050) | 70.0 | 71.2 | 68.9 | 70.2 | 68.7 | 69.9 |
| Tarauaca (120060) | 66.6 | 68.9 | 69.2 | 68.5 | 67.1 | 68.8 |
| Xapuri (120070) | 70.7 | 71.1 | 69.9 | 70.4 | 68.2 | 70.6 |
| Porto Acre (120080) | 73.4* | 71.2 | 70.3 | 68.2 | 66.4 | 71.4 |

### Mulheres

| Municipio | 2000-2004 | 2005-2009 | 2010-2014 | 2015-2019 | 2020-2021 pandemia | 2022-2024 |
|---|---|---|---|---|---|---|
| Acrelandia (120001) | 74.5* | 73.0* | 74.9* | 74.6* | 73.2* | 74.5* |
| Assis Brasil (120005) | 77.3* | 73.6* | 72.6* | 72.1* | 68.6* | 69.3* |
| Brasileia (120010) | 73.3 | 72.3 | 71.9 | 72.2 | 71.8 | 72.1 |
| Bujari (120013) | 77.7* | 75.7* | 73.9* | 74.2* | 74.1* | 73.0* |
| Capixaba (120017) | 76.0* | 74.8* | 72.7* | 74.2* | 72.6* | 72.5* |
| Cruzeiro do Sul (120020) | 72.5 | 73.8 | 73.2 | 73.6 | 72.5 | 73.9 |
| Epitaciolandia (120025) | 72.7* | 72.9 | 74.0 | 74.0 | 71.8* | 72.8 |
| Feijo (120030) | 73.6 | 73.8 | 73.4 | 72.5 | 70.6 | 73.0 |
| Jordao (120032) | 79.1* | 74.2* | 71.6* | 73.5* | 78.0* | 74.0* |
| Manoel Urbano (120033) | 75.9* | 74.2* | 72.9 | 72.9 | 72.0* | 73.5 |
| Marechal Thaumaturgo (120034) | 76.0* | 71.0* | 75.0* | 72.9* | 69.5* | 71.7* |
| Mancio Lima (120035) | 76.2* | 75.8* | 74.2* | 74.6* | 74.2* | 75.7* |
| Placido de Castro (120038) | 73.3* | 72.6 | 73.9 | 73.8 | 72.9* | 74.2* |
| Porto Walter (120039) | 75.1* | 73.3* | 75.2* | 73.0* | 74.4* | 73.4* |
| Rio Branco (120040) | 71.1 | 72.0 | 72.7 | 73.2 | 70.9 | 73.5 |
| Rodrigues Alves (120042) | 77.3* | 74.2* | 74.9* | 73.2* | 73.9* | 75.2* |
| Santa Rosa do Purus (120043) | 78.7* | 67.7* | 69.7* | 70.4* | 66.3* | 63.0* |
| Senador Guiomard (120045) | 73.8 | 73.1 | 73.5 | 73.9 | 71.2 | 73.2 |
| Sena Madureira (120050) | 73.2 | 74.3 | 73.1 | 73.4 | 72.0 | 72.6 |
| Tarauaca (120060) | 71.8 | 71.8 | 72.5 | 71.7 | 72.4 | 72.9 |
| Xapuri (120070) | 71.7 | 72.8 | 72.5 | 73.8 | 73.9* | 73.7 |
| Porto Acre (120080) | 75.4* | 73.5* | 72.5 | 73.6 | 70.5* | 72.9 |

## Obitos excluidos por periodo

| Periodo | Lidos | Sexo ignorado | Idade ignorada | Municipio fora da lista |
|---|---|---|---|---|
| 2000-2004 | 12755 | 8 | 7 | 18 |
| 2005-2009 | 14119 | 8 | 9 | 11 |
| 2010-2014 | 16253 | 9 | 15 | 10 |
| 2015-2019 | 19304 | 21 | 35 | 8 |
| 2020-2021 pandemia | 10356 | 29 | 18 | 5 |
| 2022-2024 | 12615 | 19 | 16 | 5 |

## Limites

- Ecologico: municipios, nao individuos. Associacao nao e causalidade.
- Subregistro de obitos nao e corrigido; ele tende a ser maior nos primeiros anos da serie (anos 2000) e em municipios pequenos, o que pode subestimar a mortalidade e superestimar a expectativa de vida.
- Populacao: estimativas do Ministerio da Saude/IBGE, que mudam a cada revisao e nao entram na incerteza.
- Para idade 0 e 1 a 4 anos, a distribuicao dos obitos dentro do grupo usa as formulas de Coale e Demeny (Preston, Heuveline e Guillot, 2001); nos demais grupos, o ponto medio.
