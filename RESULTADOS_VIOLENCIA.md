# EXPVIDA: a onda dos homicídios no Brasil, 2000-2024

Projeto EXPVIDA (pasta C:\EXPVIDA). Resultados preliminares de 27/11/2026, para discussão do autor. Fonte: SIM/DATASUS, com óbitos por residência de 2000 a 2024, e população POPSVS. Os homicídios incluem as agressões (CID-10 X85 a Y09) e a intervenção legal (Y35 e Y36). Os números descrevem lugares, não pessoas.

## O que os dados mostram

Em 2000, o Sudeste era a região mais violenta do país, com 32,7 homicídios por 100 mil habitantes, e o Nordeste tinha 18,1. Em 2017, o Nordeste chegou a 49,5 e o Norte a 48,2, enquanto o Sudeste já havia caído para 18,8. Em 2024, o Sudeste ficou em 11,5, o Nordeste em 33,3 e o Norte em 28,1. O pico do Sudeste ocorreu em 2002, o do Sul em 2009, o do Centro-Oeste em 2014 e os do Norte e do Nordeste em 2017. Essa sequência de picos é a "migração da violência" vista ano a ano.

Para enxergar o movimento no território, definimos o ano de "decolagem" de cada uma das 558 microrregiões. Ele é o primeiro ano em que a média móvel de três anos ficou acima de 30 homicídios por 100 mil habitantes, mantendo-se nesse patamar por pelo menos três anos seguidos. Das microrregiões do Sudeste, 23 já estavam acima desse patamar em 2000 e só uma decolou depois de 2014. No Nordeste aconteceu o contrário: 56 microrregiões decolaram entre 2008 e 2014 e outras 27 depois de 2015. No Norte, a maior parte das decolagens foi a mais tardia, depois de 2015. A mediana do ano de decolagem foi 2005,5 no Sul, 2008,5 no Sudeste, 2012 no Nordeste e no Centro-Oeste, e 2014 no Norte.

A onda também desceu na escala de renda. Separamos as microrregiões em cinco grupos de igual população pelo IDHM-Renda de 2000. Entre as que decolaram durante o período, a mediana do ano de decolagem foi 2006 no grupo mais rico e 2013 no grupo mais pobre. No grupo mais pobre, 88 microrregiões decolaram a partir de 2008. No grupo mais rico, apenas uma. Isso é coerente com a inversão do gradiente de renda já encontrada na análise municipal: a violência letal passou dos lugares mais ricos para os mais pobres.

Entre os jovens homens de 15 a 29 anos, a mudança é ainda mais forte. A taxa do Sudeste caiu de 135 para 43 por 100 mil entre 2000 e 2024. A do Nordeste subiu de 65 para 184 em 2018 e estava em 138 em 2024. A arma de fogo respondeu por 80% dos homicídios do Nordeste em 2017, a maior proporção entre as regiões.

Quanto ao local da morte, a via pública concentrou de 45% a 53% dos homicídios no Nordeste entre 2000 e 2015, a maior proporção do país, e caiu para 43,5% em 2024. Ao mesmo tempo, a parcela de mortes dentro de casa subiu em todas as regiões. No Sul, por exemplo, passou de 15,8% para 21,9%.

## Cuidado importante: homicídios escondidos

A queda nacional depois de 2018 precisa ser lida com cautela. As mortes violentas de intenção indeterminada, em que o sistema não sabe se houve agressão, acidente ou suicídio, subiram de cerca de 9.800 por ano até 2017 para 16.648 em 2019 e 17.207 em 2024. Parte da queda dos homicídios registrados pode ser, na verdade, homicídio classificado como indeterminado. O próximo passo é refazer as taxas somando uma parcela dessas mortes, como faz o Atlas da Violência, e ver se a onda e a inversão continuam.

## Limitações

A taxa usada é bruta, não padronizada por idade. Para comparar a tendência de uma mesma região isso pesa pouco, mas a comparação entre regiões com estruturas etárias diferentes pede padronização, que pode ser feita com os mesmos arquivos. O limiar de 30 por 100 mil é uma escolha. Convém testar 20 e 40 para ver se o desenho da onda se mantém. Os dados não dizem quem cometeu as mortes e não permitem atribuí-las a nenhuma facção. A ligação com a expansão de facções, como Comando Vermelho e PCC, é uma hipótese a ser discutida com a literatura e com fontes externas, como o Atlas da Violência e o Anuário do Fórum Brasileiro de Segurança Pública. O download do Sinesp falhou na rede do notebook (o site dados.mj.gov.br não respondeu) e será tentado de novo.

## Arquivos

Os arquivos estão na pasta C:\EXPVIDA: analise_violencia.py, ONDA_HOMICIDIOS.png, ONDA_DECOLAGEM_MICRO.csv, ONDA_RESUMO.csv, VIOLENCIA_REGIAO_ANUAL.csv, VIOLENCIA_MICRO_ANUAL.csv e HOMICIDIO_LOCAL_REGIAO.csv.
