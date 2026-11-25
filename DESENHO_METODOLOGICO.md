# Desenho metodológico

Projeto: Quando o território importa: idade e desigualdade na sobrevivência no Brasil. Pasta: C:\EXPVIDA. Versão atualizada em 24/11/2026, após o piloto e a primeira execução para o Brasil inteiro.

## Objetivo

O objetivo geral é descrever em que idades as desigualdades territoriais de sobrevivência aparecem no Brasil e como elas diferem entre homens e mulheres, usando exclusivamente dados públicos do SUS e do IBGE. Os objetivos específicos são estimar, por município e por sexo, a expectativa de vida ao nascer e em idades selecionadas, medir o tamanho da diferença entre territórios em cada idade e mostrar, com intervalos de incerteza, onde a diferença é maior que o acaso.

## Pergunta e hipóteses

A pergunta central é a do LEIAME. Formulam-se três hipóteses, todas a serem testadas e nenhuma tratada como resultado. A primeira é que parte da desigualdade territorial já está presente no primeiro ano de vida. A segunda é que a desigualdade entre territórios cresce na idade adulta jovem entre os homens, faixa em que pesam as mortes por causas externas. A terceira é que o padrão por idade da desigualdade territorial difere entre homens e mulheres, isto é, as idades em que a diferença entre territórios é maior não são as mesmas nos dois sexos. Se os dados não sustentarem uma hipótese, isso será relatado como resultado.

## Dados

Usam-se os óbitos do SIM (DATASUS), por residência, de 2000 a 2024, com sexo, idade e município de residência, as estimativas populacionais por município, sexo e idade (DATASUS, POPSVS), também de 2000 a 2024, e a tabela CADMUN, que associa cada município à sua microrregião do IBGE. O inventário do SIM do Acre mostrou que o município de residência está preenchido em todos os óbitos e que não há coluna de CEP; o código de bairro existe apenas de 2000 a 2010, de forma irregular. Por isso a unidade territorial do estudo é o município e, para os pequenos, a microrregião; o nível de CEP ou bairro fica fora do escopo.

## Método

Para cada território e sexo constroem-se tábuas de vida abreviadas, com faixas de idade 0, 1 a 4, 5 a 9 e assim por diante até 80 ou mais, a partir das taxas de mortalidade (óbitos divididos pelas pessoas-ano). Os óbitos e as populações são somados em seis janelas: 2000-2004, 2005-2009, 2010-2014, 2015-2019, 2020-2021 (pandemia, tratada à parte e não usada como referência) e 2022-2024. Além da expectativa de vida ao nascer, calcula-se a expectativa até os 80 anos (e0-80, anos vividos entre 0 e 80), que não depende da faixa aberta de 80 ou mais e por isso é a medida de comparação entre territórios pequenos, e a probabilidade de morrer entre 15 e 60 anos. A incerteza vem de simulação de Poisson dos óbitos. Territórios com menos de 100 óbitos no sexo e no período são marcados como instáveis; municípios pequenos são agrupados na microrregião do IBGE, critério fixado antes da execução nacional. A desigualdade é descrita pelos percentis 10, 50 e 90 entre microrregiões e pela razão entre o percentil 90 e o 10 das taxas, em cada idade, só entre microrregiões com ao menos 20 óbitos na faixa. Óbitos com sexo ou idade ignorados são contados e relatados, sem imputação; óbitos sem município identificado entram apenas nos totais de UF e Brasil. Idade média ao morrer não é usada como se fosse expectativa de vida.

## Piloto e execução nacional

O piloto no Acre, de 2000 a 2024, testou o código, a tábua de vida, a escolha de e0-80 e a correção dos códigos de município de 7 dígitos. Em seguida o mesmo método foi executado para as 27 UFs, com resultado descritivo em BRASIL_RESUMO.md. Os testes formais das hipóteses e a busca de literatura são os passos seguintes.

## Limites

Os resultados por território são ecológicos e não descrevem indivíduos. Associação não é causalidade. O subregistro de óbitos, mais provável em municípios pequenos e em regiões com menor cobertura, pode afetar as estimativas, e não será corrigido sem fonte pública que o permita. Nenhum ineditismo é afirmado antes de uma busca de literatura.
