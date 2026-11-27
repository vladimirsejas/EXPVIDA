# Complemento de busca — precedentes adicionais sobre pequenas áreas e variância da longevidade
**EXPVIDA | 27/11/2026 | revisão exploratória**

## 1. Gonzaga e Schmertmann (2016): TOPALS em pequenas áreas brasileiras

**Estimating age- and sex-specific mortality rates for small areas with TOPALS regression: an application to Brazil in 2010.** *Revista Brasileira de Estudos de População*, 33(3), 629–652. DOI: https://doi.org/10.20947/S0102-30982016c0009.

O estudo utiliza regressão Poisson combinada ao modelo relacional TOPALS para estimar taxas de mortalidade por idade e sexo em estados, mesorregiões, microrregiões e municípios brasileiros em 2010. Mostra diferenças nos padrões etários até entre áreas adjacentes e discute a instabilidade das taxas observadas em pequenas populações.

**Implicação:** o uso de Poisson em pequenas áreas brasileiras e a análise de diferenças nos padrões etários já têm precedente. O EXPVIDA deve enfatizar seu estimando de dispersão territorial residual (τ) e a série temporal, não a aplicação de Poisson em si.

Fonte: https://www.scielo.br/scielo.php?lng=en&pid=S0102-30982016000300629&script=sci_arttext&tlng=en

## 2. Seaman, Riffe e Caswell (2019): variância da idade à morte e heterogeneidade entre áreas

**Changing contribution of area-level deprivation to total variance in age at death: a population-based decomposition analysis.** *BMJ Open*, 9(3), e024952. DOI: https://doi.org/10.1136/bmjopen-2018-024952.

O artigo compara quintis de privação territorial na Escócia entre 1981 e 2011, por sexo, e separa variância entre grupos da variância individual dentro dos grupos. A contribuição da heterogeneidade entre áreas para a variância total da idade à morte aumentou, mas explicou no máximo 4% da variância total.

**Implicação:** reforça a necessidade de distinguir:
- variância da expectativa de vida entre microrregiões;
- variância da idade à morte entre indivíduos;
- heterogeneidade de risco entre microrregiões estimada por τ.

São estimandos diferentes. A proposta H10 de decompor a variância territorial de e0-80 não é equivalente à decomposição da variância individual da idade à morte.

Fonte: https://pubmed.ncbi.nlm.nih.gov/30928938/

## 3. Reforço da comparação metodológica

A literatura identificada agora inclui:
- TOPALS/Poisson em pequenas áreas brasileiras (Gonzaga & Schmertmann, 2016);
- desigualdade territorial de mortalidade e qualidade do registro em microrregiões (Lima et al., 2024);
- estimação e projeção municipal com TOPALS, modelos bayesianos e suavização espacial (Gonzaga et al., 2024);
- decomposição de variância da idade à morte por privação territorial (Seaman et al., 2019);
- decomposição da variância da expectativa de vida por idade e causa entre unidades territoriais (Vierboom et al., 2019);
- modelagem suave e localizada de mortalidade em pequenas áreas por idade, espaço e tempo (Martin & Camarda, 2026).

O manuscrito principal precisa declarar com precisão que seu foco é a dispersão dos efeitos territoriais dos riscos de mortalidade, estimada por τ, e não a variância individual da longevidade. Essa distinção é uma das formas mais claras de posicionar a contribuição.
