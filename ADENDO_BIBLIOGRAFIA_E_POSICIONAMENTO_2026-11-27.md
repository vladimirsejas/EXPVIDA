# Atualização bibliográfica e posicionamento — busca de 27/11/2026
## EXPVIDA — complemento ao manuscrito principal

Esta atualização acrescenta estudos encontrados em uma busca adicional. Continua sendo uma revisão exploratória, não sistemática.

## 1. Martin e Camarda (2026): modelo recente de mortalidade em pequenas áreas

**Modeling smooth and localized mortality patterns across age, time, and space to uncover small-area inequalities.** *Journal of the Royal Statistical Society: Series A: Statistics in Society*. Publicado em 06/08/2026. DOI: https://doi.org/10.1093/jrsssa/qnag093.

O artigo apresenta um modelo que estima padrões de mortalidade por idade, espaço e tempo em pequenas populações, combinando componentes suaves e desvios locais. A aplicação utiliza mais de 4.800 pequenas áreas da Grande Londres, 2002–2024, e estima desigualdades etárias e espaciais, incluindo o período da COVID-19.

**Implicação para EXPVIDA:** o artigo é um precedente metodológico contemporâneo e muito próximo quanto ao problema estatístico: separar ruído de contagem de desigualdades locais em mortalidade por idade e tempo. A proposta brasileira não deve reivindicar novidade por usar Poisson, efeitos aleatórios ou análise de pequenas áreas em si. O diferencial possível está no contexto brasileiro, na série 2000–2024, no uso de microrregiões e na transparência da sensibilidade à qualidade do SIM. A comparação metodológica deve explicar por que o modelo Poisson-lognormal de um parâmetro τ é adequado à pergunta descritiva, reconhecendo que não modela suavidade etária/espacial/temporal com a flexibilidade do modelo de Martin e Camarda.

Fonte: https://academic.oup.com/jrsssa/advance-article/doi/10.1093/jrsssa/qnag093/8753126

## 2. Lima et al. (2024): estudo direto de qualidade do SIM em 558 microrregiões

**Analyzing regional patterns of mortality data quality and adult mortality for small areas in Brazil, 1980–2010.** *Demographic Research*, 51(44), 1411–1428. DOI: https://doi.org/10.4054/DemRes.2024.51.44.

O artigo estuda qualidade dos registros e mortalidade adulta em 558 microrregiões brasileiras, por sexo e ao longo de 1980–2010. Utiliza métodos de distribuição de óbitos e TOPALS, além de análise espacial. Encontra melhora da completude do registro, mas persistência de disparidades regionais e associação com desigualdade social.

**Implicação:** é um precedente essencial para a discussão de sub-registro. O EXPVIDA usa a mesma escala de 558 microrregiões e período posterior, e mede heterogeneidade residual de mortalidade, que pode refletir cobertura diferencial. O manuscrito deve dialogar diretamente com esse estudo e evitar tratar τ como mortalidade verdadeira sem qualificação.

Fonte: https://www.demographic-research.org/articles/volume/51/44/

## 3. Gonzaga et al. (2024): estimativas municipais e projeções

**Estimation and probabilistic projection of age- and sex-specific mortality rates across Brazilian municipalities between 2010 and 2030.** *Population Health Metrics* (2024). DOI: https://doi.org/10.1186/s12963-024-00329-x.

O trabalho estima taxas por idade e sexo para 5.565 municípios brasileiros, combinando TOPALS, modelos bayesianos e suavização espacial, e projeta mortalidade e expectativa de vida.

**Implicação:** reforça que a estimação de mortalidade em pequenas áreas brasileiras já possui literatura consolidada. A contribuição do EXPVIDA deve ser formulada em torno do estimando τ e da comparação da heterogeneidade por idade/sexo ao longo do tempo, e não como uma nova solução geral de estimação de mortalidade municipal.

Fonte: https://pubmed.ncbi.nlm.nih.gov/38802870/

## 4. Monteiro da Silva et al. (2026): decomposição do hiato urbano-rural

**The Emergence of an Urban Mortality Advantage in Brazil: An Assessment of Age and Causes-of-Death Contributions to the Urban–Rural Mortality Gap.** *Journal of Urban Health* (2026). DOI: https://doi.org/10.1007/s11524-026-01076-0.

Analisa expectativa de vida adulta de 20 a 85 anos, por sexo, idade e causa, nas cinco macrorregiões brasileiras, 2006–2023. Encontra mudança do hiato urbano-rural, com contribuição importante das causas externas entre homens de 20–39 anos.

**Implicação:** é um precedente próximo para a interpretação substantiva da desigualdade masculina jovem e para decomposição por causas. O EXPVIDA opera em microrregiões, com estimando diferente (heterogeneidade residual dos riscos), e não deve afirmar que descobriu a concentração de mortalidade masculina jovem ou a contribuição geral das causas externas.

Fonte: https://link.springer.com/article/10.1007/s11524-026-01076-0

## 5. Baptista, Queiroz e Pinheiro (2021): distribuição espacial das causas em pequenas áreas

**Regional Distribution of Causes of Death for Small Areas in Brazil, 1998–2017.** *Frontiers in Public Health*. DOI: https://doi.org/10.3389/fpubh.2021.601980.

O estudo analisa a distribuição espaço-temporal de grupos de causas de morte nas microrregiões brasileiras, por sexo, entre 1998 e 2017.

**Implicação:** a análise de causas em microrregiões também tem precedente. O EXPVIDA precisa distinguir a comparação de heterogeneidade τ causa-específica de uma decomposição aditiva da desigualdade geral, que não é válida.

Fonte: https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2021.601980/full

## 6. Posicionamento científico recomendado

A literatura agora identificada mostra que quatro blocos de pesquisa já existem:
1. estimação e suavização da mortalidade em pequenas áreas brasileiras;
2. análise espacial e temporal de causas de morte em microrregiões;
3. decomposição por idade e causa de diferenças regionais/urbano-rurais de expectativa de vida;
4. modelagem contemporânea de padrões suaves e localizados de mortalidade em pequenas áreas.

A contribuição mais defensável do manuscrito principal é:

> Quantificar, em uma série de seis períodos entre 2000 e 2024, como a heterogeneidade residual da mortalidade registrada varia por idade e sexo entre as 558 microrregiões brasileiras, usando um modelo Poisson-lognormal e inferência por blocos geográficos, e documentar como a dependência espacial e a qualidade do registro alteram a incerteza das comparações.

A novidade é incremental e específica: aplicação longitudinal e por idade/sexo de um estimando de heterogeneidade territorial residual, com atenção explícita à dependência espacial e à incerteza de registro. Não reivindicar pioneirismo em small-area estimation, análise espacial de mortalidade ou decomposição por causa.

## 7. Ajustes necessários no manuscrito

- Acrescentar Martin e Camarda (2026) à discussão metodológica.
- Acrescentar Lima et al. (2024) como precedente central sobre qualidade dos registros nas mesmas 558 microrregiões.
- Acrescentar Gonzaga et al. (2024) à discussão de estimação de mortalidade em pequenas áreas.
- Acrescentar Monteiro da Silva et al. (2026) à discussão de diferenças de mortalidade masculina jovem e causas externas.
- Moderar qualquer alegação de novidade do modelo.
- Explicitar que o τ do EXPVIDA é um parâmetro de dispersão dos efeitos territoriais sob o modelo especificado, e não uma medida universal de desigualdade geográfica.
