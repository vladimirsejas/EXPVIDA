# Piloto: AC, periodo "antes" (2017, 2018, 2019)

Gerado por piloto_expectativa.py. Tabuas de vida abreviadas por municipio e sexo, com obitos e pessoas-ano somados no periodo. Incerteza: 300 simulacoes, obitos tratados como contagens de Poisson (intervalo de 95%). Os numeros abaixo sao do piloto de teste do metodo; nao sao conclusoes.

## Obitos usados e excluidos

Obitos lidos no SIM: 12024. Excluidos e contados: sexo ignorado 17; idade ignorada 21; municipio de residencia fora da lista de municipios da populacao (inclui o codigo de municipio ignorado) 6.
Municipios na populacao: 22.

## Total do estado

e0 = expectativa de vida ao nascer. e0-80 = anos vividos entre 0 e 80 anos (medida mais robusta em municipios pequenos, pois nao depende da faixa de 80 anos e mais). q15-60 = probabilidade de morrer entre 15 e 60 anos. q0 = mortalidade no primeiro ano, por mil.

| Sexo | Obitos | e0 (IC 95%) | e0-80 (IC 95%) | e60 | q15-60 | q0 |
|---|---|---|---|---|---|---|
| homens | 7355 | 72.0 (71.7 a 72.4) | 68.2 (67.9 a 68.4) | 20.9 | 0.187 | 17.4 |
| mulheres | 4625 | 79.2 (78.7 a 79.6) | 73.1 (72.9 a 73.3) | 24.2 | 0.094 | 12.7 |

## Municipios

Instavel = menos de 100 obitos no periodo em algum dos sexos. Veja tambem a largura do intervalo: intervalo largo significa numero pouco confiavel, mesmo acima desse limite.

| Municipio | H e0-80 (IC) | H obitos | M e0-80 (IC) | M obitos | H e0 (IC) | M e0 (IC) | Instavel |
|---|---|---|---|---|---|---|---|
| Acrelandia (120001) | 71.6 (69.6 a 73.4) | 103 | 73.8 (72.2 a 75.4) | 63 | 77.0 (74.5 a 81.0) | 80.5 (77.4 a 86.7) | sim |
| Assis Brasil (120005) | 66.6 (63.7 a 69.5) | 80 | 73.5 (70.9 a 75.6) | 34 | 68.5 (65.0 a 72.0) | 81.5 (76.0 a 94.4) | sim |
| Brasileia (120010) | 68.3 (66.8 a 69.6) | 245 | 72.5 (71.4 a 73.7) | 162 | 72.3 (70.4 a 74.4) | 76.7 (75.1 a 79.0) | nao |
| Bujari (120013) | 70.2 (68.2 a 72.4) | 83 | 74.4 (72.7 a 76.0) | 47 | 81.5 (75.9 a 95.5) | 82.2 (78.0 a 92.0) | sim |
| Capixaba (120017) | 68.1 (65.7 a 70.4) | 100 | 74.7 (72.9 a 76.5) | 38 | 72.1 (68.8 a 76.8) | 85.6 (79.8 a 103.0) | sim |
| Cruzeiro do Sul (120020) | 68.2 (67.4 a 68.9) | 787 | 73.5 (72.8 a 74.0) | 487 | 72.1 (70.9 a 73.2) | 79.9 (78.7 a 81.5) | nao |
| Epitaciolandia (120025) | 70.8 (69.1 a 72.3) | 140 | 73.5 (72.1 a 74.8) | 92 | 76.0 (73.4 a 79.7) | 80.0 (76.9 a 84.7) | sim |
| Feijo (120030) | 68.4 (67.2 a 69.5) | 297 | 72.8 (71.7 a 73.9) | 167 | 72.2 (70.5 a 74.2) | 82.3 (79.2 a 87.0) | nao |
| Jordao (120032) | 73.2 (70.7 a 76.0) | 26 | 73.3 (70.7 a 76.0) | 22 | 93.4 (81.2 a 146.5) | 108.3 (80.9 a 120.6) | sim |
| Manoel Urbano (120033) | 68.9 (67.2 a 70.5) | 145 | 72.0 (70.4 a 73.5) | 92 | 73.6 (71.0 a 77.0) | 81.0 (77.4 a 89.5) | sim |
| Marechal Thaumaturgo (120034) | 68.0 (65.6 a 70.4) | 83 | 72.9 (70.9 a 75.3) | 54 | 74.4 (70.1 a 83.7) | 77.0 (73.8 a 81.0) | sim |
| Mancio Lima (120035) | 74.2 (72.5 a 75.7) | 55 | 74.2 (72.5 a 76.2) | 55 | 87.9 (82.1 a 106.8) | 81.0 (77.9 a 88.7) | sim |
| Placido de Castro (120038) | 69.8 (67.8 a 71.5) | 159 | 74.7 (73.5 a 76.2) | 78 | 74.5 (72.2 a 77.8) | 83.5 (80.1 a 89.3) | sim |
| Porto Walter (120039) | 72.0 (69.6 a 74.7) | 46 | 73.2 (70.9 a 75.7) | 35 | 83.0 (76.4 a 108.5) | 82.5 (77.3 a 106.8) | sim |
| Rio Branco (120040) | 67.1 (66.7 a 67.5) | 3655 | 73.1 (72.8 a 73.4) | 2358 | 70.1 (69.6 a 70.6) | 78.7 (78.1 a 79.3) | nao |
| Rodrigues Alves (120042) | 70.1 (68.3 a 71.9) | 98 | 73.0 (71.3 a 74.8) | 55 | 76.6 (73.4 a 82.2) | 88.9 (81.4 a 125.2) | sim |
| Santa Rosa do Purus (120043) | 66.5 (62.5 a 70.5) | 43 | 72.2 (68.8 a 75.5) | 24 | 78.5 (68.5 a 99.6) | 99.5 (80.7 a 140.8) | sim |
| Senador Guiomard (120045) | 68.7 (67.2 a 70.4) | 232 | 74.0 (72.9 a 75.1) | 135 | 72.1 (70.1 a 74.3) | 79.4 (77.1 a 82.1) | nao |
| Sena Madureira (120050) | 70.0 (69.0 a 71.1) | 331 | 73.0 (71.9 a 74.0) | 225 | 74.4 (72.7 a 76.6) | 78.7 (76.9 a 81.2) | nao |
| Tarauaca (120060) | 68.5 (67.4 a 69.7) | 328 | 72.0 (71.1 a 73.3) | 218 | 72.8 (70.8 a 75.1) | 78.5 (76.5 a 81.8) | nao |
| Xapuri (120070) | 71.1 (69.7 a 72.3) | 148 | 73.7 (72.4 a 75.1) | 112 | 75.4 (73.4 a 77.9) | 78.2 (76.1 a 81.0) | nao |
| Porto Acre (120080) | 68.1 (66.4 a 69.8) | 171 | 73.9 (72.4 a 75.4) | 72 | 73.4 (70.6 a 76.5) | 83.9 (80.4 a 91.6) | sim |

## Limites

- Ecologico: municipios, nao individuos. Associacao nao e causalidade.
- Subregistro de obitos nao e corrigido. Populacao: estimativas do Ministerio da Saude/IBGE.
- Para idade 0 e 1 a 4 anos, a distribuicao dos obitos dentro do grupo usa as formulas de Coale e Demeny (Preston, Heuveline e Guillot, 2001); nos demais grupos, o ponto medio.
- A simulacao considera apenas a incerteza dos obitos (Poisson), nao a da populacao estimada.
