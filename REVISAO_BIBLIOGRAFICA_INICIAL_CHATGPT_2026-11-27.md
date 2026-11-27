# Complemento bibliográfico inicial — EXPVIDA
**Data da busca:** 27/11/2026  
**Status:** busca exploratória, não sistemática. Não usar como declaração de ineditismo.

## 1. Resultado principal: há precedentes muito próximos

### Calazans, Guimarães e Nepomuceno (2023)
**“Diferenciais regionais da mortalidade no Brasil: contribuição dos grupos etários e de causas de óbito sobre a variação da esperança de vida e da dispersão da idade à morte entre 2008 e 2018.”** Revista Brasileira de Estudos de População, 40. DOI: https://doi.org/10.20947/S0102-3098a0244

O artigo analisa Brasil e grandes regiões, a contribuição dos grupos de causas para mudanças na esperança de vida e na dispersão da idade à morte entre 2008 e 2018. Usa oito grupos de causas e taxas específicas por idade; o estudo declara usar taxas de mortalidade do IBGE corrigidas por problemas de registro e óbitos por causa básica do SIM. Os autores encontram aumento dos diferenciais regionais de esperança de vida, diferenças quase constantes na dispersão da idade à morte e contribuições distintas das causas por região.

**Implicação:** a pergunta ampla “quais causas contribuem para diferenças regionais de esperança de vida e dispersão da idade à morte no Brasil?” já foi estudada. H10 não pode ser apresentada como inédita nessa formulação geral.

Fonte consultada: https://www.scielo.br/j/rbepop/a/whYGB9rjGDJBrr6LZy64ymD/?format=html

### Monteiro da Silva et al. (2026)
**“The Emergence of an Urban Mortality Advantage in Brazil: An Assessment of Age and Causes-of-Death Contributions to the Urban–Rural Mortality Gap.”** Journal of Urban Health, publicado em 23/04/2026. DOI: https://doi.org/10.1007/s11524-026-01076-0

O artigo estuda diferenças urbano-rurais de expectativa de vida adulta (20–85 anos) nas cinco macrorregiões, de 2006 a 2023, por sexo, idade e causa. Decompõe a mudança do hiato urbano-rural por idade, causa e tipo de área. Usa SIM, censos e ajustes de completude; exclui idades abaixo de 20 e limita a análise até 85 anos, entre outros motivos ligados à qualidade dos registros.

**Implicação:** a decomposição de diferenças de sobrevivência por idade e causa no Brasil também tem trabalho muito recente. O diferencial potencial do EXPVIDA não é simplesmente aplicar uma decomposição por causas, mas investigar a heterogeneidade entre muitas unidades territoriais pequenas, em vez de apenas macrorregiões ou contraste urbano-rural, e testar se grupos de causas estão associados à distribuição territorial da sobrevivência.

Fonte consultada: https://link.springer.com/article/10.1007/s11524-026-01076-0

### Baptista, Queiroz e Pinheiro (2021)
**“Regional Distribution of Causes of Death for Small Areas in Brazil, 1998–2017.”** Frontiers in Public Health. DOI: https://doi.org/10.3389/fpubh.2021.601980

Analisa padrões espaço-temporais de grupos de causas e sexo em pequenas áreas/microrregiões brasileiras, usando SIM/DATASUS, 1998–2017. Trabalha com taxas padronizadas e visualização composicional de três grupos principais.

**Implicação:** a escala de pequenas áreas e a distribuição espacial de causas já foram abordadas. O diferencial do EXPVIDA precisa ser claramente o estimando de heterogeneidade da sobrevivência, a modelagem do componente Poisson e/ou uma decomposição contrafactual bem definida — não apenas mapear causas por microrregião.

Fonte consultada: https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2021.601980/full

### Borges (2017)
**“Health transition in Brazil: regional variations and divergence/convergence in mortality.”** Cadernos de Saúde Pública. DOI: https://doi.org/10.1590/0102-311X00080316

Analisa a transição da saúde e a divergência/convergência regional da mortalidade, considerando contribuições de grupos etários e causas para variações na esperança de vida.

Fonte consultada: https://pubmed.ncbi.nlm.nih.gov/28832781/

## 2. O que isso muda na formulação de H10

A formulação ampla — “quanto das diferenças territoriais de expectativa de vida é explicado pelas causas de morte?” — está próxima de literatura existente. É uma pergunta válida, mas não sustenta, sozinha, uma alegação de novidade.

Uma formulação potencialmente mais específica para o EXPVIDA seria:

> Entre microrregiões brasileiras, como a heterogeneidade territorial da sobrevivência por idade e sexo se relaciona aos padrões de mortalidade por grandes grupos de causas, e em que medida diferenças contrafactuais nesses padrões alteram a distribuição territorial de e0-80?

Essa formulação ainda precisa ser avaliada. Há uma distinção metodológica decisiva:
- Decompor um hiato de esperança de vida entre dois grupos de territórios é um problema.
- Explicar a variância/heterogeneidade entre centenas de microrregiões é outro problema.
- Decompor τ diretamente por causa não é válido por adição simples, conforme já reconhecido no projeto.

A estratégia mais prudente é não assumir que Shapley resolve automaticamente o problema. Primeiro definir o objeto a decompor: diferença entre dois territórios representativos, diferença entre quantis da distribuição territorial, variância de e0-80, ou outro funcional. Depois verificar se a decomposição contrafactual respeita a estrutura de riscos competitivos e mantém taxas coerentes.

## 3. Próximas buscas necessárias

A revisão ainda não é sistemática. Próximas etapas:
1. Pesquisar artigos sobre decomposition of life expectancy differences by cause of death, small areas, subnational mortality, spatial heterogeneity e Brazil.
2. Procurar estudos que decomponham variância ou dispersão entre áreas, não apenas diferenças entre duas regiões.
3. Identificar estudos que utilizem modelos hierárquicos/Poisson-lognormal para heterogeneidade territorial de mortalidade causa-específica.
4. Verificar artigos internacionais em que Shapley ou decomposição contrafactual seja aplicada a desigualdade territorial de sobrevivência.
5. Ler texto integral e suplemento dos estudos mais próximos, especialmente os de 2023 e 2026.

## 4. Conclusão provisória

Há precedentes diretos para decomposição por idade e causa das diferenças regionais de esperança de vida no Brasil, inclusive um estudo de 2023 e outro muito recente de 2026. Há também precedentes de análise causa-específica em pequenas áreas. O caminho científico do EXPVIDA deve, portanto, ser mais estreito e preciso: avaliar se a modelagem da heterogeneidade entre microrregiões e sua relação com os padrões causa-específicos acrescenta algo além das decomposições regionais já publicadas. Nenhuma alegação de ineditismo está autorizada nesta fase.
