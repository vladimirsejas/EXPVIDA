# Atualização da revisão bibliográfica — precedentes metodológicos diretos
**EXPVIDA | 27/11/2026 | Busca exploratória**

Esta nota complementa `REVISAO_BIBLIOGRAFICA_INICIAL_CHATGPT_2026-11-27.md`. A busca adicional encontrou um precedente ainda mais próximo da proposta de decompor a variância territorial da expectativa de vida.

## 1. Vierboom, Preston e Hendi (2019)

**Rising geographic inequality in mortality in the United States.** *SSM - Population Health*, 9, 100478. DOI: https://doi.org/10.1016/j.ssmph.2019.100478.

O artigo analisa desigualdade espacial em mortalidade e expectativa de vida em 40 unidades dos Estados Unidos, de 1990 a 2016. O apêndice apresenta uma decomposição da mudança da variância da expectativa de vida entre 2000 e 2016 por idade e causa de morte. O procedimento substitui sequencialmente as taxas locais de cada combinação idade-causa pela taxa nacional e recalcula a variância territorial.

Grupos incluídos no apêndice: câncer de pulmão/doenças respiratórias, circulatórias, Alzheimer/mentais/neuro, outras causas externas, drogas/álcool/suicídio, homicídio, cânceres rastreáveis, HIV/AIDS e demais causas. O artigo reporta contribuições por idade-causa para homens e mulheres.

**Consequência para o EXPVIDA:** a ideia de decompor a variância territorial da expectativa de vida por idade e causa já tem precedente direto. Não é defensável apresentar a decomposição Shapley proposta como invenção do princípio de decompor a variância por causas. A contribuição potencial teria de estar na extensão ao contexto brasileiro, escala e painel territorial, série temporal, tratamento explícito da dependência da ordem, validação e qualidade do SIM — e mesmo isso só após comparação sistemática.

Fonte principal: https://pmc.ncbi.nlm.nih.gov/articles/PMC6804490/  
Registro PubMed: https://pubmed.ncbi.nlm.nih.gov/31649997/

## 2. Nau e Firebaugh (2012)

**A New Method for Determining Why Length of Life is More Unequal in Some Populations Than in Others.** *Demography*, 49(4), 1207–1230. DOI: https://doi.org/10.1007/s13524-012-0133-9.

Apresenta a decomposição S-A-T (spread, allocation, timing) da variância da idade à morte por causa. Compara Estados Unidos e Suécia e mostra que a distribuição etária das mortes por causa, a alocação de mortes entre causas e o momento médio das mortes são mecanismos distintos.

O artigo discute limitações importantes: causas competem entre si; a independência entre causas é uma suposição problemática; resultados dependem do agrupamento das causas; e métodos sequenciais de substituição podem depender da ordem e do grupo de referência.

**Consequência:** EXPVIDA deve distinguir a variância territorial da expectativa de vida entre microrregiões da variância individual da idade à morte. São objetos diferentes. S-A-T não é sinônimo da proposta Shapley sobre variância entre microrregiões.

Fonte principal: https://pmc.ncbi.nlm.nih.gov/articles/PMC4104684/  
Registro PubMed: https://pubmed.ncbi.nlm.nih.gov/23011942/

## 3. GBD 2021 (publicado em 2024)

**Global burden of 288 causes of death and life expectancy decomposition in 204 countries and territories and 811 subnational locations, 1990–2021.** *The Lancet*, 403 (2024). 

O estudo apresenta decomposição de expectativa de vida por idade e causa em escala global, nacional e subnacional, usando 288 causas e 811 localidades subnacionais. Demonstra que a decomposição por causa/idade em múltiplas escalas é uma linha de pesquisa consolidada, embora a metodologia de estimação e os dados sejam distintos do SIM/POPSVS do EXPVIDA.

Fonte: https://pmc.ncbi.nlm.nih.gov/articles/PMC11126520/

## 4. Ajuste obrigatório na proposta H10

A proposta Shapley continua metodologicamente interessante para reduzir a dependência da ordem de substituição, mas **não deve ser vendida como novidade isolada**. O artigo de Vierboom et al. já faz substituição sequencial de taxas locais por taxas nacionais e recalcula a variância territorial. Shapley seria uma escolha de atribuição simétrica para repartir interações entre causas, não uma nova pergunta substantiva por si só.

A comparação formal deverá responder:
1. O que exatamente Vierboom et al. medem e qual é o seu algoritmo de substituição?
2. O que difere entre variância de e0 ao nascer, variância de e0-80 e outros indicadores?
3. A proposta brasileira agrega microrregiões e painel temporal comparável ou apenas replica o procedimento em mais unidades?
4. O tratamento da ordem via Shapley muda materialmente a interpretação e melhora a propriedade de fechamento?
5. A qualidade e a completude do SIM permitem uma decomposição por causa confiável em todos os períodos?
6. O modelo Poisson-lognormal de τ responde a uma pergunta distinta e pode ser integrado como análise complementar sem confundir estimandos?

## 5. Recomendação de posicionamento

A pergunta de pesquisa mais promissora talvez não seja “quais causas explicam a variância territorial da expectativa de vida?”, pois há precedente direto. Uma formulação mais forte deve combinar:
- dinâmica temporal da desigualdade territorial por idade e sexo;
- decomposição por causa com ordem tratada explicitamente;
- avaliação da robustez a sub-registro e causas mal definidas;
- comparação entre variância de sobrevivência e heterogeneidade residual dos riscos (τ), mantendo os estimandos separados.

A novidade deve ser sustentada por comparação metodológica e bibliográfica, não presumida pela escala maior do banco de dados.
