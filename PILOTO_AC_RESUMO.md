# Piloto: AC, periodo 2022 a 2024

Gerado por piloto_expectativa.py. Tabuas de vida abreviadas por municipio e sexo, com obitos e pessoas-ano somados no periodo. Incerteza: 300 simulacoes, obitos tratados como contagens de Poisson (intervalo de 95%). Os numeros abaixo sao do piloto de teste do metodo; nao sao conclusoes.

## Obitos usados e excluidos

Obitos lidos no SIM: 12615. Excluidos e contados: sexo ignorado 19; idade ignorada 16; municipio de residencia fora da lista de municipios da populacao (inclui o codigo de municipio ignorado) 5.
Municipios na populacao: 22.

## Total do estado

| Sexo | Obitos | e0 (anos) | IC 95% | e60 | q15-60 | q0 (por mil) |
|---|---|---|---|---|---|---|
| homens | 7373 | 73.6 | 73.2 a 73.9 | 21.5 | 0.162 | 17.7 |
| mulheres | 5202 | 79.5 | 79.1 a 80.0 | 24.4 | 0.086 | 15.4 |

## Municipios (e0 por sexo, anos)

Marcados como instaveis os municipios com menos de 100 obitos no periodo e no sexo; para eles o intervalo e largo e a leitura deve ser cautelosa.

| Municipio | Homens e0 | IC 95% | Obitos | Mulheres e0 | IC 95% | Obitos | Instavel |
|---|---|---|---|---|---|---|---|
| 120001 | 78.0 | 74.9 a 81.7 | 113 | 83.9 | 80.1 a 91.2 | 63 | sim |
| 120005 | 74.0 | 69.5 a 82.0 | 68 | 74.4 | 70.2 a 80.7 | 63 | sim |
| 120010 | 71.9 | 70.1 a 73.8 | 277 | 77.4 | 75.4 a 80.0 | 182 | nao |
| 120013 | 79.0 | 76.4 a 83.3 | 95 | 84.8 | 79.3 a 108.7 | 67 | sim |
| 120017 | 76.0 | 72.8 a 81.0 | 93 | 81.4 | 76.9 a 93.1 | 61 | sim |
| 120020 | 73.2 | 72.2 a 74.3 | 804 | 80.4 | 79.2 a 81.6 | 536 | nao |
| 120025 | 73.9 | 71.6 a 76.7 | 181 | 76.8 | 74.9 a 79.6 | 132 | nao |
| 120030 | 74.9 | 72.9 a 76.8 | 274 | 81.0 | 78.4 a 84.5 | 186 | nao |
| 120032 | 90.4 | 81.0 a 150.0 | 32 | 90.5 | 81.8 a 142.5 | 29 | sim |
| 120033 | 77.7 | 74.9 a 82.0 | 136 | 80.0 | 77.3 a 84.2 | 106 | nao |
| 120034 | 75.4 | 72.3 a 82.4 | 89 | 79.1 | 75.4 a 88.3 | 58 | sim |
| 120035 | 79.4 | 76.5 a 84.3 | 80 | 88.1 | 82.5 a 105.7 | 44 | sim |
| 120038 | 75.9 | 73.8 a 78.8 | 160 | 82.0 | 79.4 a 87.3 | 99 | sim |
| 120039 | 79.1 | 75.1 a 87.8 | 53 | 84.1 | 78.3 a 108.4 | 38 | sim |
| 120040 | 72.2 | 71.7 a 72.6 | 3546 | 79.5 | 78.9 a 80.2 | 2576 | nao |
| 120042 | 77.2 | 74.4 a 82.0 | 100 | 85.2 | 80.8 a 96.5 | 53 | sim |
| 120043 | 70.9 | 65.5 a 85.2 | 61 | 69.2 | 64.3 a 80.1 | 70 | sim |
| 120045 | 77.0 | 74.3 a 80.9 | 196 | 80.0 | 77.3 a 83.5 | 148 | nao |
| 120050 | 75.0 | 73.2 a 76.8 | 350 | 79.3 | 77.3 a 81.7 | 242 | nao |
| 120060 | 73.2 | 71.5 a 75.1 | 355 | 78.4 | 76.5 a 80.6 | 235 | nao |
| 120070 | 74.5 | 72.4 a 77.3 | 168 | 81.0 | 78.6 a 86.1 | 107 | nao |
| 120080 | 77.6 | 74.6 a 81.6 | 142 | 79.1 | 76.6 a 82.6 | 107 | nao |

## Limites

- Ecologico: municipios, nao individuos. Associacao nao e causalidade.
- Subregistro de obitos nao e corrigido. Populacao: estimativas do Ministerio da Saude/IBGE.
- Para idade 0 e 1 a 4 anos, a distribuicao dos obitos dentro do grupo usa as formulas de Coale e Demeny (Preston, Heuveline e Guillot, 2001); nos demais grupos, o ponto medio.
- A simulacao considera apenas a incerteza dos obitos (Poisson), nao a da populacao estimada.
