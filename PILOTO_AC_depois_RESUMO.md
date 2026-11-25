# Piloto: AC, periodo "depois" (2022, 2023, 2024)

Gerado por piloto_expectativa.py. Tabuas de vida abreviadas por municipio e sexo, com obitos e pessoas-ano somados no periodo. Incerteza: 300 simulacoes, obitos tratados como contagens de Poisson (intervalo de 95%). Os numeros abaixo sao do piloto de teste do metodo; nao sao conclusoes.

## Obitos usados e excluidos

Obitos lidos no SIM: 12615. Excluidos e contados: sexo ignorado 19; idade ignorada 16; municipio de residencia fora da lista de municipios da populacao (inclui o codigo de municipio ignorado) 5.
Municipios na populacao: 22.

## Total do estado

e0 = expectativa de vida ao nascer. e0-80 = anos vividos entre 0 e 80 anos (medida mais robusta em municipios pequenos, pois nao depende da faixa de 80 anos e mais). q15-60 = probabilidade de morrer entre 15 e 60 anos. q0 = mortalidade no primeiro ano, por mil.

| Sexo | Obitos | e0 (IC 95%) | e0-80 (IC 95%) | e60 | q15-60 | q0 |
|---|---|---|---|---|---|---|
| homens | 7373 | 73.6 (73.2 a 73.9) | 69.4 (69.1 a 69.6) | 21.5 | 0.162 | 17.7 |
| mulheres | 5202 | 79.5 (79.1 a 80.0) | 73.2 (73.0 a 73.4) | 24.4 | 0.086 | 15.4 |

## Municipios

Instavel = menos de 100 obitos no periodo em algum dos sexos. Veja tambem a largura do intervalo: intervalo largo significa numero pouco confiavel, mesmo acima desse limite.

| Municipio | H e0-80 (IC) | H obitos | M e0-80 (IC) | M obitos | H e0 (IC) | M e0 (IC) | Instavel |
|---|---|---|---|---|---|---|---|
| Acrelandia (120001) | 71.4 (69.9 a 73.0) | 113 | 74.5 (73.1 a 76.0) | 63 | 78.0 (74.9 a 81.7) | 83.9 (80.1 a 91.2) | sim |
| Assis Brasil (120005) | 68.0 (65.1 a 70.9) | 68 | 69.3 (66.2 a 72.1) | 63 | 74.0 (69.5 a 82.0) | 74.4 (70.2 a 80.7) | sim |
| Brasileia (120010) | 68.3 (66.8 a 69.7) | 277 | 72.1 (70.9 a 73.4) | 182 | 71.9 (70.1 a 73.8) | 77.4 (75.4 a 80.0) | nao |
| Bujari (120013) | 72.2 (70.5 a 73.7) | 95 | 73.0 (71.3 a 74.7) | 67 | 79.0 (76.4 a 83.3) | 84.8 (79.3 a 108.7) | sim |
| Capixaba (120017) | 70.1 (68.0 a 72.1) | 93 | 72.5 (70.7 a 74.2) | 61 | 76.0 (72.8 a 81.0) | 81.4 (76.9 a 93.1) | sim |
| Cruzeiro do Sul (120020) | 69.6 (68.9 a 70.2) | 804 | 73.9 (73.3 a 74.4) | 536 | 73.2 (72.2 a 74.3) | 80.4 (79.2 a 81.6) | nao |
| Epitaciolandia (120025) | 69.3 (67.8 a 70.8) | 181 | 72.8 (71.4 a 74.3) | 132 | 73.9 (71.6 a 76.7) | 76.8 (74.9 a 79.6) | nao |
| Feijo (120030) | 69.4 (68.1 a 70.7) | 274 | 73.0 (71.8 a 74.1) | 186 | 74.9 (72.9 a 76.8) | 81.0 (78.4 a 84.5) | nao |
| Jordao (120032) | 73.6 (71.3 a 75.8) | 32 | 74.0 (71.6 a 76.4) | 29 | 90.4 (81.0 a 150.0) | 90.5 (81.8 a 142.5) | sim |
| Manoel Urbano (120033) | 70.7 (69.0 a 72.3) | 136 | 73.5 (72.0 a 74.8) | 106 | 77.7 (74.9 a 82.0) | 80.0 (77.3 a 84.2) | nao |
| Marechal Thaumaturgo (120034) | 69.8 (67.7 a 71.9) | 89 | 71.7 (69.4 a 74.0) | 58 | 75.4 (72.3 a 82.4) | 79.1 (75.4 a 88.3) | sim |
| Mancio Lima (120035) | 72.9 (70.9 a 74.6) | 80 | 75.7 (74.3 a 77.2) | 44 | 79.4 (76.5 a 84.3) | 88.1 (82.5 a 105.7) | sim |
| Placido de Castro (120038) | 71.5 (69.9 a 73.0) | 160 | 74.2 (73.0 a 75.4) | 99 | 75.9 (73.8 a 78.8) | 82.0 (79.4 a 87.3) | sim |
| Porto Walter (120039) | 72.8 (70.8 a 74.6) | 53 | 73.4 (71.8 a 75.4) | 38 | 79.1 (75.1 a 87.8) | 84.1 (78.3 a 108.4) | sim |
| Rio Branco (120040) | 68.7 (68.3 a 69.1) | 3546 | 73.5 (73.2 a 73.9) | 2576 | 72.2 (71.7 a 72.6) | 79.5 (78.9 a 80.2) | nao |
| Rodrigues Alves (120042) | 71.2 (69.5 a 72.9) | 100 | 75.2 (73.8 a 76.6) | 53 | 77.2 (74.4 a 82.0) | 85.2 (80.8 a 96.5) | sim |
| Santa Rosa do Purus (120043) | 65.4 (62.2 a 68.8) | 61 | 63.0 (59.6 a 66.2) | 70 | 70.9 (65.5 a 85.2) | 69.2 (64.3 a 80.1) | sim |
| Senador Guiomard (120045) | 70.1 (68.6 a 71.5) | 196 | 73.2 (71.7 a 74.4) | 148 | 77.0 (74.3 a 80.9) | 80.0 (77.3 a 83.5) | nao |
| Sena Madureira (120050) | 69.9 (68.8 a 70.9) | 350 | 72.6 (71.5 a 73.6) | 242 | 75.0 (73.2 a 76.8) | 79.3 (77.3 a 81.7) | nao |
| Tarauaca (120060) | 68.8 (67.8 a 70.1) | 355 | 72.9 (71.8 a 74.0) | 235 | 73.2 (71.5 a 75.1) | 78.4 (76.5 a 80.6) | nao |
| Xapuri (120070) | 70.6 (69.1 a 72.2) | 168 | 73.7 (72.3 a 74.8) | 107 | 74.5 (72.4 a 77.3) | 81.0 (78.6 a 86.1) | nao |
| Porto Acre (120080) | 71.4 (69.5 a 72.8) | 142 | 72.9 (71.4 a 74.5) | 107 | 77.6 (74.6 a 81.6) | 79.1 (76.6 a 82.6) | nao |

## Limites

- Ecologico: municipios, nao individuos. Associacao nao e causalidade.
- Subregistro de obitos nao e corrigido. Populacao: estimativas do Ministerio da Saude/IBGE.
- Para idade 0 e 1 a 4 anos, a distribuicao dos obitos dentro do grupo usa as formulas de Coale e Demeny (Preston, Heuveline e Guillot, 2001); nos demais grupos, o ponto medio.
- A simulacao considera apenas a incerteza dos obitos (Poisson), nao a da populacao estimada.
