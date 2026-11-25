# Piloto: AC, periodo "pandemia" (2020, 2021)

Gerado por piloto_expectativa.py. Tabuas de vida abreviadas por municipio e sexo, com obitos e pessoas-ano somados no periodo. Incerteza: 300 simulacoes, obitos tratados como contagens de Poisson (intervalo de 95%). Os numeros abaixo sao do piloto de teste do metodo; nao sao conclusoes.

## Obitos usados e excluidos

Obitos lidos no SIM: 10356. Excluidos e contados: sexo ignorado 29; idade ignorada 18; municipio de residencia fora da lista de municipios da populacao (inclui o codigo de municipio ignorado) 5.
Municipios na populacao: 22.

## Total do estado

e0 = expectativa de vida ao nascer. e0-80 = anos vividos entre 0 e 80 anos (medida mais robusta em municipios pequenos, pois nao depende da faixa de 80 anos e mais). q15-60 = probabilidade de morrer entre 15 e 60 anos. q0 = mortalidade no primeiro ano, por mil.

| Sexo | Obitos | e0 (IC 95%) | e0-80 (IC 95%) | e60 | q15-60 | q0 |
|---|---|---|---|---|---|---|
| homens | 6206 | 69.2 (68.8 a 69.5) | 66.8 (66.5 a 67.1) | 18.1 | 0.215 | 19.2 |
| mulheres | 4098 | 76.3 (75.8 a 76.8) | 71.4 (71.1 a 71.7) | 22.2 | 0.127 | 13.6 |

## Municipios

Instavel = menos de 100 obitos no periodo em algum dos sexos. Veja tambem a largura do intervalo: intervalo largo significa numero pouco confiavel, mesmo acima desse limite.

| Municipio | H e0-80 (IC) | H obitos | M e0-80 (IC) | M obitos | H e0 (IC) | M e0 (IC) | Instavel |
|---|---|---|---|---|---|---|---|
| Acrelandia (120001) | 68.3 (66.1 a 70.6) | 107 | 73.2 (71.6 a 74.9) | 56 | 71.7 (68.8 a 75.6) | 77.8 (75.0 a 83.5) | sim |
| Assis Brasil (120005) | 65.9 (63.0 a 68.6) | 66 | 68.6 (65.1 a 71.5) | 44 | 67.2 (64.3 a 70.7) | 72.2 (68.4 a 79.1) | sim |
| Brasileia (120010) | 66.6 (64.6 a 68.2) | 202 | 71.8 (70.4 a 73.0) | 126 | 69.8 (67.3 a 72.3) | 76.1 (74.1 a 79.1) | nao |
| Bujari (120013) | 67.7 (65.1 a 70.3) | 92 | 74.1 (72.2 a 76.0) | 34 | 71.2 (68.1 a 75.2) | 88.7 (79.6 a 131.3) | sim |
| Capixaba (120017) | 70.4 (68.1 a 72.8) | 66 | 72.6 (70.0 a 75.0) | 38 | 74.2 (71.1 a 79.2) | 80.2 (75.3 a 96.6) | sim |
| Cruzeiro do Sul (120020) | 68.6 (67.7 a 69.6) | 575 | 72.5 (71.8 a 73.3) | 397 | 71.3 (70.1 a 72.5) | 77.9 (76.6 a 79.6) | nao |
| Epitaciolandia (120025) | 67.7 (65.8 a 69.9) | 139 | 71.8 (69.9 a 73.6) | 82 | 70.5 (68.2 a 73.4) | 77.1 (74.2 a 81.5) | sim |
| Feijo (120030) | 67.8 (66.1 a 69.4) | 206 | 70.6 (69.0 a 71.9) | 145 | 72.1 (69.7 a 75.4) | 79.1 (75.5 a 84.7) | nao |
| Jordao (120032) | 73.5 (71.0 a 76.4) | 19 | 78.0 (76.7 a 79.2) | 8 | 93.2 (78.5 a 122.6) | 119.9 (88.5 a 121.7) | sim |
| Manoel Urbano (120033) | 70.2 (68.3 a 72.1) | 91 | 72.0 (70.0 a 73.8) | 77 | 77.5 (73.7 a 85.3) | 77.4 (74.2 a 82.4) | sim |
| Marechal Thaumaturgo (120034) | 66.5 (63.7 a 69.5) | 83 | 69.5 (66.8 a 72.3) | 42 | 68.5 (65.2 a 72.2) | 101.6 (75.7 a 121.6) | sim |
| Mancio Lima (120035) | 72.1 (70.0 a 74.2) | 55 | 74.2 (72.1 a 76.1) | 36 | 77.1 (73.4 a 84.4) | 84.4 (78.7 a 110.4) | sim |
| Placido de Castro (120038) | 68.7 (66.6 a 70.7) | 119 | 72.9 (71.3 a 74.7) | 71 | 73.3 (70.5 a 77.7) | 80.5 (77.0 a 87.2) | sim |
| Porto Walter (120039) | 72.9 (70.4 a 75.4) | 29 | 74.4 (71.4 a 77.0) | 19 | 97.6 (80.9 a 131.1) | 91.5 (79.5 a 133.5) | sim |
| Rio Branco (120040) | 65.2 (64.7 a 65.7) | 3213 | 70.9 (70.5 a 71.3) | 2253 | 66.9 (66.3 a 67.4) | 74.9 (74.3 a 75.5) | nao |
| Rodrigues Alves (120042) | 69.6 (67.5 a 72.0) | 77 | 73.9 (71.9 a 75.8) | 51 | 73.9 (70.7 a 80.4) | 78.2 (75.1 a 83.1) | sim |
| Santa Rosa do Purus (120043) | 65.9 (61.6 a 70.1) | 38 | 66.3 (62.5 a 69.9) | 30 | 71.2 (64.1 a 86.8) | 98.9 (71.2 a 113.8) | sim |
| Senador Guiomard (120045) | 67.3 (65.5 a 69.0) | 185 | 71.2 (69.3 a 73.0) | 112 | 70.1 (68.0 a 72.7) | 77.8 (74.5 a 82.4) | nao |
| Sena Madureira (120050) | 68.7 (67.4 a 70.0) | 280 | 72.0 (70.8 a 73.2) | 182 | 71.5 (69.9 a 73.4) | 76.9 (74.9 a 79.2) | nao |
| Tarauaca (120060) | 67.1 (65.5 a 68.5) | 286 | 72.4 (71.1 a 73.7) | 148 | 69.4 (67.5 a 71.3) | 78.4 (76.1 a 81.9) | nao |
| Xapuri (120070) | 68.2 (65.8 a 70.4) | 126 | 73.9 (72.3 a 75.4) | 68 | 71.6 (68.7 a 74.7) | 80.8 (77.7 a 86.8) | sim |
| Porto Acre (120080) | 66.4 (64.2 a 68.5) | 152 | 70.5 (68.4 a 72.4) | 79 | 69.3 (66.7 a 72.3) | 79.4 (75.1 a 91.0) | sim |

## Limites

- Ecologico: municipios, nao individuos. Associacao nao e causalidade.
- Subregistro de obitos nao e corrigido. Populacao: estimativas do Ministerio da Saude/IBGE.
- Para idade 0 e 1 a 4 anos, a distribuicao dos obitos dentro do grupo usa as formulas de Coale e Demeny (Preston, Heuveline e Guillot, 2001); nos demais grupos, o ponto medio.
- A simulacao considera apenas a incerteza dos obitos (Poisson), nao a da populacao estimada.
