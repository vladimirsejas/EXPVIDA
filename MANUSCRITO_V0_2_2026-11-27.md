# Quando o território importa: decomposição da desigualdade territorial da mortalidade no Brasil por causas, sexo e período, 2000–2024
## Manuscrito de trabalho — versão 0.2, 27/11/2026

**Autores:** a definir  
**Afiliação:** a definir  
**Tipo de artigo:** pesquisa original, estudo ecológico de pequenas áreas  
**Status:** versão de trabalho atualizada com os resultados V2.

---

## Resumo

**Objetivo:** Decompor a heterogeneidade territorial da expectativa temporária de vida por causas, sexo e período no Brasil; avaliar a sensibilidade da contribuição de agressões à redistribuição de óbitos por intenção indeterminada; estimar τ de agressões por sexo e faixa etária; e descrever registros B34.2 com e sem U07.

**Métodos:** Foram utilizados registros de óbitos do SIM/DATASUS e estimativas populacionais POPSVS, agregados em microrregiões. A decomposição H10 empregou cenários contrafactuais de equalização das taxas locais para taxas nacionais e atribuição de contribuições pelo valor de Shapley. A sensibilidade redistribuiu frações 0,0, 0,5 e 1,0 dos óbitos por intenção indeterminada para agressões. A heterogeneidade territorial específica das agressões foi descrita por τ e IC95%, por sexo, faixa etária e período. Os registros B34.2 foram contabilizados com e sem U07.

**Resultados:** Na decomposição H10, a contribuição de agressões e intervenção legal entre homens variou de 18,37% a 46,67%; entre mulheres, variou de 1,29% a 2,77%. Em 2015–2019, a sensibilidade entre homens produziu contribuições de 46,67%, 47,94% e 49,21% nos cenários de fração 0,0, 0,5 e 1,0 (Tabelas 1 e 2; Figuras 1 e 2). Para homens de 15–29 anos, τ permaneceu entre 0,75 e 0,85 nos seis períodos, com intervalos sobrepostos, indicando estabilidade/persistência. Entre mulheres de 15–29 anos, τ foi menor em todos os períodos, entre 0,50 e 0,62 (Tabela 3; Figura 3). Os registros B34.2 com e sem U07 estão discriminados na Tabela 4.

**Conclusão:** A decomposição por causas revela contribuições distintas por sexo e período; τ de agressões aponta persistência da heterogeneidade territorial entre homens jovens e valores menores entre mulheres da mesma faixa. As estimativas para mulheres de 60 anos ou mais em períodos específicos são instáveis e não devem ser interpretadas.

**Palavras-chave:** mortalidade; desigualdades territoriais; pequenas áreas; causas de morte; diferenças por sexo; Brasil.

---

## 1. Introdução

A mortalidade não se distribui de maneira homogênea no território. Diferenças regionais na estrutura etária, nas condições de vida, na exposição a riscos, na oferta de serviços e na qualidade dos sistemas de informação podem produzir padrões distintos de sobrevivência. No Brasil, a desigualdade regional da mortalidade e suas mudanças ao longo do tempo foram descritas em diferentes escalas, incluindo grandes regiões e unidades subnacionais.

Uma questão menos simples é identificar em que idades as diferenças territoriais se tornam mais pronunciadas e se esse padrão é semelhante entre homens e mulheres. Comparações de taxas observadas podem confundir heterogeneidade persistente com flutuação aleatória, especialmente em faixas etárias e territórios com poucos óbitos. Além disso, a dependência espacial entre áreas vizinhas torna inadequado tratar todas as unidades territoriais como observações independentes na inferência.

Este estudo utiliza um modelo Poisson-lognormal para separar, sob hipóteses explícitas, a variação esperada pelo processo de contagem da heterogeneidade residual entre microrregiões. O parâmetro central, τ, representa o desvio-padrão dos efeitos territoriais na escala logarítmica. A medida não distingue mortalidade real de erros sistemáticos de registro ou de denominadores; representa, portanto, heterogeneidade territorial residual na mortalidade registrada.

O objetivo é decompor a heterogeneidade territorial da expectativa temporária de vida por grupos de causas, sexo e período; avaliar a sensibilidade da contribuição de agressões à redistribuição de óbitos por intenção indeterminada; estimar τ de agressões por sexo e faixa etária; e descrever registros B34.2 com e sem U07. As análises são descritivas e ecológicas, não relações causais individuais.


---

## 2. Métodos

### 2.1 Desenho e unidade de análise

Estudo ecológico de séries temporais agregadas, com unidade territorial principal definida pelas microrregiões do IBGE disponíveis na base analítica. Embora o CADMUN registre 586 códigos de microrregião, os arquivos de taxas e os modelos versionados utilizam 558 unidades. A razão dessa diferença deve ser reconciliada por código antes da submissão; até lá, o universo analítico é descrito como 558 microrregiões disponíveis na base.

As análises foram realizadas separadamente para homens e mulheres. Os períodos foram:
- 2000–2004;
- 2005–2009;
- 2010–2014;
- 2015–2019;
- 2020–2021 (pandemia);
- 2022–2024.

### 2.2 Fontes de dados

Os óbitos por residência foram obtidos do SIM/DATASUS, para 2000–2024. As exposições populacionais por município, sexo e idade foram obtidas das estimativas POPSVS do DATASUS. A associação entre município e microrregião foi feita com a tabela CADMUN.

Os dados foram agregados por sexo e por 18 grupos etários: 0, 1–4, 5–9, ..., 75–79 e 80 anos ou mais. Óbitos com sexo ou idade ignorados não foram imputados. Registros sem município identificável foram contabilizados separadamente nos totais de UF e Brasil, mas não atribuídos artificialmente a uma microrregião.

### 2.3 Tábuas de vida e medidas complementares

Foram construídas tábuas de vida abreviadas a partir das taxas centrais de mortalidade, calculadas como óbitos divididos por pessoas-ano. A expectativa temporária de vida entre 0 e 80 anos (e0-80) foi utilizada para comparar territórios, pois não depende da faixa aberta de 80 anos ou mais. A probabilidade de morrer entre 15 e 60 anos (q15-60) foi utilizada como medida complementar.

A faixa de idade zero utiliza população estimada como denominador. Não equivale à taxa de mortalidade infantil calculada com nascidos vivos; essa distinção é particularmente importante na interpretação de H1.

### 2.4 Modelo de heterogeneidade territorial

Para cada combinação de sexo, período e faixa etária, os óbitos observados na microrregião (i) foram modelados como:

[
D_i sim \operatorname{Poisson}\{E_i\exp(\mu+u_i)\},
\qquad u_i\sim N(0,\tau^2).
]

O valor (E_i) corresponde aos óbitos esperados se a microrregião apresentasse a taxa de mortalidade do restante do Brasil na mesma idade, sexo e período. A própria microrregião é excluída do cálculo da taxa de referência (leave-one-out). O parâmetro μ representa o nível médio comum e τ é o desvio-padrão dos efeitos territoriais na escala logarítmica.

Assim, τ quantifica a heterogeneidade residual entre microrregiões após considerar a variação Poisson. Sob a distribuição normal dos efeitos, a razão esperada entre os percentis 90 e 10 dos riscos territoriais é εxp(2,563τ). O parâmetro não representa uma medida pura de desigualdade da mortalidade real: inclui também diferenças persistentes na cobertura do SIM e erros dos denominadores populacionais.

A verossimilhança marginal foi aproximada por quadratura de Gauss-Hermite adaptativa, com 15 nós e otimização numérica. O modelo foi avaliado previamente por simulações com valores conhecidos de τ. Os intervalos de perfil de verossimilhança foram utilizados para estimativas pontuais de τ.

### 2.5 Dependência espacial e inferência

A validação espacial identificou autocorrelação dos efeitos territoriais e concentração de variação entre unidades da Federação. Por isso, as comparações entre faixas etárias e sexos foram avaliadas por bootstrap em blocos de UF, preservando os mesmos sorteios entre os grupos comparados. Foram utilizadas 300 replicações nos períodos, com semente fixa 20261124. A inferência por blocos produz intervalos mais amplos do que a reamostragem de microrregiões independentes.

O bootstrap por UF possui apenas 27 blocos e deve ser entendido como aproximação. As simulações de cobertura indicam que a inferência para uma população hipotética de áreas pode permanecer otimista sob dependência espacial forte ou desvios da normalidade. A interpretação principal é, portanto, referente às 558 microrregiões observadas, com generalização condicionada às hipóteses do modelo e do bootstrap.

### 2.6 Decomposição H10 da variância territorial por causas

A decomposição utiliza a variância territorial, com pesos iguais entre microrregiões, da expectativa temporária de vida entre 0 e 80 anos (e0-80). Para cada combinação de sexo e período, são construídos cenários contrafactuais nos quais as taxas locais de um ou mais grupos de causas são substituídas pela taxa nacional correspondente à mesma idade, sexo e período. A variância de e0-80 é recalculada em cada cenário.

As contribuições são atribuídas pelo valor de Shapley, calculado sobre todos os subconjuntos de grupos. A atribuição distribui simetricamente as interações e não depende de uma única ordem de substituição. A soma das contribuições corresponde à redução entre a variância observada e a variância com todos os grupos equalizados, salvo erro numérico. Contribuições positivas indicam redução da variância após equalização; contribuições negativas indicam aumento no cenário contrafactual. A variância observada é apresentada separadamente e não é contribuição percentual.

Os grupos são: agressões e intervenção legal; intenção indeterminada; suicídio; transporte; demais causas externas; COVID-19; infecciosas sem COVID-19; neoplasias; circulatórias; respiratórias; mal definidas e sem causa; e demais doenças. A decomposição utiliza os arquivos V2 e fração zero de redistribuição de intenção indeterminada, salvo na análise de sensibilidade.

### 2.7 Sensibilidade à intenção indeterminada

A sensibilidade foi avaliada para a contribuição de agressões e intervenção legal entre homens, redistribuindo fração 0,0, 0,5 ou 1,0 dos óbitos classificados como intenção indeterminada para esse grupo. São cenários explícitos, não uma afirmação de que todos os óbitos indeterminados sejam agressões.

### 2.8 Heterogeneidade territorial específica das agressões

A heterogeneidade territorial das agressões foi estimada pelo parâmetro τ para homens e mulheres, por período e faixa etária, com IC95%. A comparação temporal considera a sobreposição dos intervalos.

### 2.9 Registros B34.2 com e sem U07

A análise descritiva contabiliza, por ano, registros B34.2 com U07 e sem U07, conforme ARTIGO_TABELA4_COVID_V2.csv. As contagens não recebem interpretação causal ou validação clínica individual.
### 2.10 Ética e proteção de dados

O estudo utiliza dados secundários públicos agregados. Nenhum registro individual é armazenado nos resultados analíticos versionados. As conclusões são ecológicas e não devem ser interpretadas como associações individuais.


---

## 3. Resultados

### 3.1 Decomposição H10 por causa, sexo e período

A Tabela 1 apresenta as contribuições percentuais dos grupos de causas para a redução da variância territorial de e0-80, separadamente para homens e mulheres, nos seis períodos. As Figuras 1 e 2 apresentam a mesma decomposição em formato gráfico, respectivamente para homens e mulheres.

Entre homens, a contribuição de agressões e intervenção legal foi de 18,37%, 22,13%, 32,50%, 46,67%, 31,74%, 36,57%. Entre mulheres, os valores foram 2,72%, 2,77%, 2,73%, 2,43%, 1,29%, 1,92%. A contribuição de agressões foi maior entre homens em todos os períodos.

As contribuições circulatórias entre homens foram 30,01%, 24,52%, 21,13%, 15,27%, 10,78%, 14,19%; entre mulheres, 41,43%, 34,06%, 30,85%, 31,75%, 14,12%, 25,97%. A contribuição do grupo COVID-19 em 2020–2021 foi 22,67% entre homens e 42,05% entre mulheres. Esses valores são contribuições contrafactuais, não proporções de óbitos.

A linha “Variância observada” da Tabela 1 apresenta a variância territorial de e0-80 antes da equalização, e não contribuição percentual. Valores negativos indicam que a equalização daquele grupo aumentou a variância no cenário contrafactual.

**Tabela 1.** Contribuições percentuais H10 por grupo de causa, sexo e período. Valores positivos indicam redução da variância territorial após equalização; valores negativos indicam aumento. A variância observada é apresentada separadamente.

**Homens**

| Grupo de causa | 2000–2004 | 2005–2009 | 2010–2014 | 2015–2019 | 2020–2021 (pandemia) | 2022–2024 |
|---|---:|---:|---:|---:|---:|---:|
| Agressões e intervenção legal | 18,37 | 22,13 | 32,50 | 46,67 | 31,74 | 36,57 |
| Intenção indeterminada | 2,02 | 0,64 | 0,17 | 2,55 | 2,19 | 1,78 |
| Suicídio | 1,64 | 0,80 | -0,72 | -1,71 | -0,81 | -0,59 |
| Transporte | 7,62 | 7,13 | 6,14 | 5,86 | 5,93 | 11,91 |
| Demais causas externas | 4,00 | 2,02 | 2,10 | 0,65 | 2,48 | 3,13 |
| COVID-19 | 0,00 | 0,00 | 0,00 | 0,00 | 22,67 | 0,35 |
| Infecciosas sem COVID-19 | 5,66 | 5,02 | 5,27 | 4,82 | 4,74 | 4,09 |
| Neoplasias | 18,02 | 15,21 | 9,24 | 1,83 | 1,70 | 0,33 |
| Circulatórias | 30,01 | 24,52 | 21,13 | 15,27 | 10,78 | 14,19 |
| Respiratórias | 9,17 | 8,05 | 6,31 | 3,34 | 4,50 | 4,04 |
| Mal definidas e sem causa | -14,24 | -1,34 | 0,06 | 3,66 | 3,34 | 5,32 |
| Demais doenças | 17,72 | 15,83 | 17,80 | 17,06 | 10,75 | 18,88 |
| Variância observada | 3,86 | 2,40 | 1,62 | 1,41 | 1,58 | 1,14 |

**Mulheres**

| Grupo de causa | 2000–2004 | 2005–2009 | 2010–2014 | 2015–2019 | 2020–2021 (pandemia) | 2022–2024 |
|---|---:|---:|---:|---:|---:|---:|
| Agressões e intervenção legal | 2,72 | 2,77 | 2,73 | 2,43 | 1,29 | 1,92 |
| Intenção indeterminada | 0,80 | 0,29 | 0,14 | 0,27 | 0,76 | 0,78 |
| Suicídio | 0,81 | 0,36 | 0,35 | 0,16 | 0,77 | 1,07 |
| Transporte | 3,54 | 3,29 | 3,25 | 1,89 | 1,53 | 3,62 |
| Demais causas externas | 2,07 | 1,22 | 1,60 | 1,50 | 1,06 | 2,34 |
| COVID-19 | 0,00 | 0,00 | 0,00 | 0,00 | 42,05 | 1,93 |
| Infecciosas sem COVID-19 | 4,79 | 5,81 | 6,19 | 7,24 | 4,60 | 5,81 |
| Neoplasias | 23,98 | 20,25 | 17,83 | 15,04 | 8,91 | 14,10 |
| Circulatórias | 41,43 | 34,06 | 30,85 | 31,75 | 14,12 | 25,97 |
| Respiratórias | 11,79 | 11,44 | 12,16 | 11,37 | 6,14 | 11,88 |
| Mal definidas e sem causa | -15,35 | -1,20 | 1,69 | 3,84 | 2,58 | 7,13 |
| Demais doenças | 23,42 | 21,71 | 23,20 | 24,50 | 16,20 | 23,47 |
| Variância observada | 1,03 | 0,72 | 0,49 | 0,36 | 0,72 | 0,36 |

**Figuras 1 e 2.** Decomposição H10 por grupo de causa e período: Figura 1, homens; Figura 2, mulheres.

### 3.2 Sensibilidade à redistribuição de intenção indeterminada

A Tabela 2 apresenta a contribuição de agressões e intervenção legal entre homens sob três cenários de redistribuição de óbitos por intenção indeterminada. Em todos os períodos, a contribuição aumentou conforme a fração redistribuída passou de 0,0 para 0,5 e 1,0. Em 2015–2019, os valores foram 46,67%, 47,94% e 49,21%, respectivamente. A análise é sensibilidade a hipóteses de classificação, não evidência de que todos os óbitos indeterminados sejam agressões.

**Tabela 2.** Sensibilidade da contribuição de agressões e intervenção legal entre homens à fração redistribuída.

| Período | Fração 0,0 | Fração 0,5 | Fração 1,0 |
|---|---:|---:|---:|
| 2000–2004 | 18,37% | 19,37% | 20,38% |
| 2005–2009 | 22,13% | 22,45% | 22,78% |
| 2010–2014 | 32,50% | 32,59% | 32,69% |
| 2015–2019 | 46,67% | 47,94% | 49,21% |
| 2020–2021 (pandemia) | 31,74% | 32,83% | 33,92% |
| 2022–2024 | 36,57% | 37,45% | 38,33% |

### 3.3 τ de agressões por sexo, faixa etária e período

A Tabela 3 apresenta τ e IC95% por período, sexo e faixa etária. Entre homens de 15–29 anos, τ permaneceu entre 0,75 e 0,85 nos seis períodos. Os intervalos de confiança se sobrepõem; o padrão deve ser descrito como **estabilidade/persistência da heterogeneidade territorial**, e não como queda ou aumento temporal.

Entre mulheres de 15–29 anos, τ foi menor que entre homens em todos os períodos, variando de 0,50 a 0,62. O contraste entre os sexos também aparece nas faixas de 15–19, 20–24 e 25–29 anos.

Para mulheres de 60 anos ou mais, os limites inferiores dos IC95% foram 0,02, 0,00 e 0,00 nos períodos 2010–2014, 2020–2021 e 2022–2024. Essas estimativas estão marcadas como instáveis, poucos óbitos, e não são interpretadas.

**Tabela 3.** τ de agressões por período, sexo e faixa etária, com IC95%. τ e limites com duas casas decimais. *Estimativa instável, poucos óbitos.*

| Período | Sexo | Faixa | τ | IC95% |
|---|---|---:|---:|---:|
| 2000–2004 | Homens | 15-19 | 1,00 | 0,89–1,09 |
| 2000–2004 | Homens | 20-24 | 0,85 | 0,72–0,94 |
| 2000–2004 | Homens | 25-29 | 0,79 | 0,68–0,87 |
| 2000–2004 | Homens | 15-29 | 0,85 | 0,74–0,93 |
| 2000–2004 | Homens | 30-59 | 0,71 | 0,61–0,79 |
| 2000–2004 | Homens | 60+ | 0,61 | 0,51–0,69 |
| 2000–2004 | Mulheres | 15-19 | 0,70 | 0,60–0,78 |
| 2000–2004 | Mulheres | 20-24 | 0,59 | 0,48–0,66 |
| 2000–2004 | Mulheres | 25-29 | 0,54 | 0,45–0,61 |
| 2000–2004 | Mulheres | 15-29 | 0,62 | 0,52–0,72 |
| 2000–2004 | Mulheres | 30-59 | 0,56 | 0,47–0,68 |
| 2000–2004 | Mulheres | 60+ | 0,43 | 0,24–0,56 |
| 2005–2009 | Homens | 15-19 | 0,89 | 0,79–0,99 |
| 2005–2009 | Homens | 20-24 | 0,73 | 0,64–0,82 |
| 2005–2009 | Homens | 25-29 | 0,71 | 0,61–0,79 |
| 2005–2009 | Homens | 15-29 | 0,75 | 0,66–0,84 |
| 2005–2009 | Homens | 30-59 | 0,62 | 0,53–0,69 |
| 2005–2009 | Homens | 60+ | 0,56 | 0,49–0,61 |
| 2005–2009 | Mulheres | 15-19 | 0,59 | 0,47–0,72 |
| 2005–2009 | Mulheres | 20-24 | 0,56 | 0,43–0,65 |
| 2005–2009 | Mulheres | 25-29 | 0,48 | 0,37–0,56 |
| 2005–2009 | Mulheres | 15-29 | 0,53 | 0,45–0,61 |
| 2005–2009 | Mulheres | 30-59 | 0,44 | 0,36–0,54 |
| 2005–2009 | Mulheres | 60+ | 0,51 | 0,39–0,61 |
| 2010–2014 | Homens | 15-19 | 0,94 | 0,83–1,04 |
| 2010–2014 | Homens | 20-24 | 0,79 | 0,69–0,87 |
| 2010–2014 | Homens | 25-29 | 0,68 | 0,58–0,75 |
| 2010–2014 | Homens | 15-29 | 0,78 | 0,69–0,86 |
| 2010–2014 | Homens | 30-59 | 0,60 | 0,52–0,65 |
| 2010–2014 | Homens | 60+ | 0,52 | 0,43–0,58 |
| 2010–2014 | Mulheres | 15-19 | 0,61 | 0,52–0,70 |
| 2010–2014 | Mulheres | 20-24 | 0,50 | 0,42–0,56 |
| 2010–2014 | Mulheres | 25-29 | 0,44 | 0,36–0,50 |
| 2010–2014 | Mulheres | 15-29 | 0,50 | 0,42–0,57 |
| 2010–2014 | Mulheres | 30-59 | 0,40 | 0,34–0,45 |
| 2010–2014 | Mulheres | 60+ | 0,34 | 0,02–0,42* |
| 2015–2019 | Homens | 15-19 | 0,91 | 0,73–1,04 |
| 2015–2019 | Homens | 20-24 | 0,81 | 0,64–0,93 |
| 2015–2019 | Homens | 25-29 | 0,72 | 0,55–0,81 |
| 2015–2019 | Homens | 15-29 | 0,80 | 0,64–0,90 |
| 2015–2019 | Homens | 30-59 | 0,59 | 0,45–0,66 |
| 2015–2019 | Homens | 60+ | 0,53 | 0,40–0,61 |
| 2015–2019 | Mulheres | 15-19 | 0,60 | 0,47–0,68 |
| 2015–2019 | Mulheres | 20-24 | 0,51 | 0,36–0,59 |
| 2015–2019 | Mulheres | 25-29 | 0,42 | 0,29–0,49 |
| 2015–2019 | Mulheres | 15-29 | 0,50 | 0,41–0,55 |
| 2015–2019 | Mulheres | 30-59 | 0,38 | 0,29–0,44 |
| 2015–2019 | Mulheres | 60+ | 0,42 | 0,28–0,49 |
| 2020–2021 (pandemia) | Homens | 15-19 | 0,93 | 0,67–1,13 |
| 2020–2021 (pandemia) | Homens | 20-24 | 0,83 | 0,61–0,97 |
| 2020–2021 (pandemia) | Homens | 25-29 | 0,76 | 0,54–0,87 |
| 2020–2021 (pandemia) | Homens | 15-29 | 0,83 | 0,62–0,97 |
| 2020–2021 (pandemia) | Homens | 30-59 | 0,58 | 0,40–0,64 |
| 2020–2021 (pandemia) | Homens | 60+ | 0,57 | 0,40–0,66 |
| 2020–2021 (pandemia) | Mulheres | 15-19 | 0,75 | 0,51–0,92 |
| 2020–2021 (pandemia) | Mulheres | 20-24 | 0,58 | 0,39–0,65 |
| 2020–2021 (pandemia) | Mulheres | 25-29 | 0,52 | 0,32–0,62 |
| 2020–2021 (pandemia) | Mulheres | 15-29 | 0,57 | 0,42–0,66 |
| 2020–2021 (pandemia) | Mulheres | 30-59 | 0,44 | 0,29–0,50 |
| 2020–2021 (pandemia) | Mulheres | 60+ | 0,40 | 0,00–0,56* |
| 2022–2024 | Homens | 15-19 | 0,92 | 0,69–1,09 |
| 2022–2024 | Homens | 20-24 | 0,80 | 0,57–0,93 |
| 2022–2024 | Homens | 25-29 | 0,71 | 0,48–0,84 |
| 2022–2024 | Homens | 15-29 | 0,79 | 0,57–0,92 |
| 2022–2024 | Homens | 30-59 | 0,56 | 0,40–0,64 |
| 2022–2024 | Homens | 60+ | 0,54 | 0,39–0,62 |
| 2022–2024 | Mulheres | 15-19 | 0,76 | 0,58–0,88 |
| 2022–2024 | Mulheres | 20-24 | 0,60 | 0,43–0,71 |
| 2022–2024 | Mulheres | 25-29 | 0,52 | 0,35–0,61 |
| 2022–2024 | Mulheres | 15-29 | 0,57 | 0,42–0,66 |
| 2022–2024 | Mulheres | 30-59 | 0,41 | 0,28–0,48 |
| 2022–2024 | Mulheres | 60+ | 0,47 | 0,00–0,59* |

*Nota: *estimativa instável, poucos óbitos* nas mulheres de 60 anos ou mais nos períodos 2010–2014, 2020–2021 e 2022–2024; não interpretar.*

**Figura 3.** τ de agressões entre homens de 15–29 anos nos seis períodos, com intervalos de confiança.

### 3.4 Registros B34.2 com e sem U07

A Tabela 4 apresenta as contagens anuais de registros B34.2 com U07 e sem U07. A distribuição é distinta entre os anos, com maior contagem de B34.2 com U07 em 2021 e redução nos anos seguintes. Há registros B34.2 sem U07 em todos os anos apresentados. Essas contagens descrevem o arquivo utilizado e não devem ser confundidas com estimativas de mortalidade ou validação clínica individual.

**Tabela 4.** Registros B34.2 com e sem U07 por ano.

| Ano | B34.2 com U07 | B34.2 sem U07 |
|---:|---:|---:|
| 2020 | 195.034 | 17.583 |
| 2021 | 424.245 | 29 |
| 2022 | 65.715 | 16 |
| 2023 | 10.266 | 2 |
| 2024 | 5.598 | 2 |

---

## 4. Discussão

Os resultados combinam perspectivas complementares: decomposição da variância territorial de e0-80 por grupos de causas, sensibilidade à redistribuição de intenção indeterminada, heterogeneidade territorial específica das agressões por sexo e idade e contagens de registros B34.2 com e sem U07. Os estimandos são distintos. As contribuições H10 são resultados de cenários contrafactuais; τ mede dispersão territorial na escala logarítmica; a Tabela 4 apresenta contagens de registros. Não são medidas intercambiáveis.

A decomposição H10 indica que a contribuição de agressões e intervenção legal para a redução da variância territorial foi maior entre homens do que entre mulheres em todos os períodos. A decomposição não demonstra que a causa isoladamente produza a desigualdade observada: o valor de Shapley distribui a redução contrafactual da variância entre grupos, incluindo interações.

A análise de sensibilidade mostra que a contribuição atribuída a agressões depende da fração de óbitos por intenção indeterminada redistribuída. Isso reforça a necessidade de explicitar as hipóteses de classificação. A análise não identifica a causa verdadeira de cada óbito.

Entre homens de 15–29 anos, os valores de τ permanecem no intervalo observado nos seis períodos e os intervalos de confiança se sobrepõem. A formulação apropriada é estabilidade/persistência da heterogeneidade territorial. Entre mulheres da mesma faixa, τ é menor em todos os períodos. As estimativas para mulheres de 60 anos ou mais em três períodos foram assinaladas como instáveis, poucos óbitos, e não sustentam interpretação substantiva.

A contagem de registros B34.2 com e sem U07 descreve a distribuição dos códigos no arquivo analisado. Não permite, isoladamente, inferir sub-registro, erro de classificação ou validade clínica.

### 4.1 Leituras substantivas possíveis — decisão do autor

**[ESCOLHA DO AUTOR] (A) Persistência da desigualdade territorial dos homicídios de homens jovens por 25 anos.** Uma leitura possível é enfatizar a persistência da heterogeneidade territorial das agressões entre homens jovens ao longo dos seis períodos que cobrem 2000–2024. A sobreposição dos intervalos de confiança de τ para homens de 15–29 anos sustenta uma interpretação de estabilidade/persistência, sem evidência suficiente para descrever queda ou aumento. Essa leitura coloca no centro a continuidade temporal da desigualdade territorial associada aos homicídios de homens jovens.

**[ESCOLHA DO AUTOR] (B) Contraste persistente entre homens e mulheres.** Outra leitura possível é destacar que τ de agressões entre mulheres de 15–29 anos é menor que entre homens em todos os períodos, enquanto a decomposição H10 também mostra contribuição de agressões e intervenção legal maior entre homens. Essa leitura enfatiza o contraste persistente entre os sexos, articulando dois estimandos diferentes sem confundi-los: contribuição contrafactual H10 e heterogeneidade territorial τ.

As duas leituras são compatíveis com os resultados apresentados, mas organizam a contribuição científica de maneiras distintas. A escolha do eixo narrativo principal deve ser feita pelo autor.

### 4.2 Relação com a literatura

Estudos anteriores documentaram diferenciais regionais de mortalidade no Brasil e contribuições de idade e causas para diferenças na esperança de vida. Calazans, Guimarães e Nepomuceno (2023) examinaram diferenças regionais de esperança de vida e dispersão da idade à morte, incluindo contribuições por grupos de causas. Borges (2017) analisou a transição da saúde e a divergência/convergência regional da mortalidade. Lima et al. (2024) avaliaram a qualidade dos registros e a mortalidade adulta nas microrregiões brasileiras entre 1980 e 2010. Gonzaga et al. (2024) estimaram e projetaram taxas por idade e sexo em municípios brasileiros. Martin e Camarda (2026) propuseram um modelo que combina padrões suaves e desvios locais em idade, espaço e tempo para estimar mortalidade em pequenas áreas.

A decomposição da variância territorial por causas possui precedentes metodológicos. Vierboom, Preston e Hendi (2019) analisaram desigualdade geográfica da mortalidade e decompuseram mudanças na variância da expectativa de vida por idade e causa, substituindo taxas locais por taxas nacionais. A contribuição específica desta análise deve ser posicionada na aplicação longitudinal às microrregiões brasileiras, na atribuição de Shapley para tratar simetricamente interações entre grupos e na apresentação conjunta — sem confusão entre estimandos — da decomposição H10 e da heterogeneidade territorial τ por sexo e idade. A novidade deve ser sustentada por comparação metodológica e bibliográfica, não presumida.

### 4.3 Limitações

Primeiro, τ não separa heterogeneidade real da mortalidade de heterogeneidade de cobertura do SIM e de erros nos denominadores.

Segundo, a decomposição H10 depende da classificação dos grupos de causas e dos cenários contrafactuais de equalização. Contribuições negativas não significam proteção causal; indicam que a equalização do grupo aumentou a variância no cenário definido.

Terceiro, a análise de sensibilidade redistribui frações predeterminadas dos óbitos por intenção indeterminada. Os cenários não identificam a causa verdadeira dos registros e não substituem investigação individual ou validação externa.

Quarto, a inferência espacial por bootstrap utiliza unidades da Federação como blocos. O número limitado de blocos restringe a precisão e a generalização.

Quinto, as estimativas de τ para mulheres de 60 anos ou mais em 2010–2014, 2020–2021 e 2022–2024 são instáveis, poucos óbitos, e não devem ser interpretadas.

Sexto, as contagens B34.2 com e sem U07 são descritivas. Sem validação adicional, não permitem concluir sobre erro, sub-registro ou diagnóstico clínico.

Sétimo, a unidade territorial disponível é a microrregião. Os resultados não podem ser interpretados como desigualdades entre bairros, CEPs ou indivíduos.

---

## 5. Conclusão

A decomposição H10 mostrou contribuições distintas dos grupos de causas para a redução contrafactual da variância territorial de e0-80, com contribuição de agressões e intervenção legal maior entre homens do que entre mulheres nos períodos analisados. A análise de sensibilidade demonstrou que a contribuição atribuída a agressões aumenta conforme cresce a fração de óbitos por intenção indeterminada redistribuída para esse grupo.

Na análise específica de agressões, τ entre homens de 15–29 anos apresentou estabilidade/persistência nos seis períodos, com intervalos de confiança sobrepostos. Entre mulheres da mesma faixa, τ foi menor em todos os períodos. As estimativas para mulheres de 60 anos ou mais assinaladas na Tabela 3 são instáveis, poucos óbitos, e não sustentam interpretação.

As contagens B34.2 com e sem U07 descrevem a distribuição dos registros, mas não permitem inferências clínicas ou causais isoladas. Os resultados devem ser interpretados respeitando as diferenças entre decomposição contrafactual, heterogeneidade residual e contagem de registros.

---

## Referências

1. Calazans, J. A., Guimarães, R. M., & Nepomuceno, M. R. (2023). Diferenciais regionais da mortalidade no Brasil: contribuição dos grupos etários e de causas de óbito sobre a variação da esperança de vida e da dispersão da idade à morte entre 2008 e 2018. *Revista Brasileira de Estudos de População*, 40. https://doi.org/10.20947/S0102-3098a0244
2. Borges, G. M. (2017). Health transition in Brazil: regional variations and divergence/convergence in mortality. *Cadernos de Saúde Pública*. https://doi.org/10.1590/0102-311X00080316
3. Lima, E. E. C., et al. (2024). Analyzing regional patterns of mortality data quality and adult mortality for small areas in Brazil, 1980–2010. *Demographic Research*, 51(44). https://doi.org/10.4054/DemRes.2024.51.44
4. Vierboom, Y. C., Preston, S. H., & Hendi, A. S. (2019). Rising geographic inequality in mortality in the United States. *SSM - Population Health*, 9, 100478. https://doi.org/10.1016/j.ssmph.2019.100478
5. Nau, C., & Firebaugh, G. (2012). A new method for determining why length of life is more unequal in some populations than in others. *Demography*, 49(4), 1207–1230. https://doi.org/10.1007/s13524-012-0133-9
6. Gonzaga, M. R., & Schmertmann, C. P. (2016). Estimating age- and sex-specific mortality rates for small areas with TOPALS regression: an application to Brazil in 2010. *Revista Brasileira de Estudos de População*, 33(3), 629–652. https://doi.org/10.20947/S0102-30982016c0009
7. Martin, J., & Camarda, C. G. (2026). Modeling smooth and localized mortality patterns across age, time, and space to uncover small-area inequalities. *Journal of the Royal Statistical Society: Series A*. https://doi.org/10.1093/jrsssa/qnag093
8. Gonzaga, M. R., et al. (2024). Estimation and probabilistic projection of age- and sex-specific mortality rates across Brazilian municipalities between 2010 and 2030. *Population Health Metrics*. https://doi.org/10.1186/s12963-024-00329-x
9. Seaman, R., Riffe, T., & Caswell, H. (2019). Changing contribution of area-level deprivation to total variance in age at death: a population-based decomposition analysis. *BMJ Open*, 9(3), e024952. https://doi.org/10.1136/bmjopen-2018-024952
10. Monteiro da Silva, et al. (2026). The Emergence of an Urban Mortality Advantage in Brazil: An Assessment of Age and Causes-of-Death Contributions to the Urban–Rural Mortality Gap. *Journal of Urban Health*. https://doi.org/10.1007/s11524-026-01076-0

## Pendências editoriais antes de submissão

- Conferir a reconciliação 558/586.
- Conferir e congelar os scripts e versões que geraram cada tabela.
- Atualizar a revisão bibliográfica com busca sistemática e leitura integral dos trabalhos mais próximos.
- Recalcular/confirmar todos os intervalos finais a partir da versão congelada do código.
- Decidir se a análise de causas será um segundo artigo ou uma análise secundária; não misturar τ causa-específico com decomposição de sobrevivência.
- Inserir autoria, afiliação, financiamento, contribuições, disponibilidade de dados/código e declaração ética conforme as regras do periódico escolhido.

