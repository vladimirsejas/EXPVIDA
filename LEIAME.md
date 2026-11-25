# Quando o território importa: idade e desigualdade na sobrevivência no Brasil

Pasta do projeto: C:\EXPVIDA

## Pergunta central

Em que idade as desigualdades territoriais de sobrevivência aparecem no Brasil, e como elas diferem entre homens e mulheres?

## Origem

Projeto sugerido por um professor da Fatec Rio Claro: associar CEP e expectativa de vida usando dados públicos do SUS, para o Brasil inteiro, separando homens e mulheres. A pergunta acima é a forma geral dessa ideia. O inventário mostrou que os dados públicos não permitem chegar ao CEP nem ao bairro; o menor recorte confiável é o município.

## Dados (somente públicos e baixáveis)

- SIM (Sistema de Informações sobre Mortalidade), DATASUS: óbitos por residência, 2000 a 2024, arquivos DO<UF><ano>.dbc.
- Estimativas populacionais por município, sexo e idade (DATASUS, pasta IBGE/POPSVS), 2000 a 2024.
- Tabela CADMUN (DATASUS): nome, UF e microrregião do IBGE de cada município.

## Estado atual (24/11/2026)

- [x] Inventário do SIM do Acre: INVENTARIO_SIM_AC.md
- [x] Objetivos, hipóteses e desenho metodológico: DESENHO_METODOLOGICO.md
- [x] Piloto do Acre, série de 25 anos em seis janelas: PILOTO_AC_COMPARACAO_PERIODOS.md
- [x] Brasil inteiro, 27 UFs, 2000 a 2024, por município, microrregião, UF e Brasil, homens e mulheres: BRASIL_RESUMO.md e os CSV BRASIL_*
- [ ] Busca de literatura para saber o que já existe (obrigatória antes de qualquer afirmação de ineditismo)
- [ ] Testar formalmente as três hipóteses do desenho metodológico (até aqui só há descrição)
- [ ] Decidir se a microrregião do IBGE é o agrupamento final ou se se prefere região de saúde ou outro critério declarado antes da análise

## Como rodar de novo

Abrir brasil_expectativa.py no VS Code e clicar em "Run Python File". Leva cerca de 20 minutos, usa até 4 processos e uma pasta temporária do Windows (apagada ao final). Se parar no meio, rodar outra vez: continua de onde parou. O andamento aparece em BRASIL_PROGRESSO.txt.

## Arquivos gerados pelo Brasil

- BRASIL_RESUMO.md: leitura rápida (Brasil, UFs, desigualdade entre microrregiões, desigualdade por idade, óbitos excluídos, limites).
- BRASIL_municipios.csv, BRASIL_microrregioes.csv, BRASIL_ufs_e_brasil.csv: e0, e0-80, e15, e60, q0, q15-60, óbitos, pessoas-ano e intervalos de 95%, por período e sexo. Separador ponto e vírgula.
- BRASIL_taxas_por_idade.csv: óbitos e pessoas-ano por faixa etária (microrregião, UF e Brasil), base para qualquer cálculo de desigualdade por idade.

## O que o Brasil inteiro mostrou (descritivo, sem teste formal)

- Brasil, e0: homens 70,7 (2000-2004), 71,8, 72,1, 72,8 (2015-2019), 70,5 na pandemia (2020-2021) e 73,1 (2022-2024); mulheres 78,6, 79,6, 79,8, 80,2, 78,0 e 80,0. Valores da ordem esperada para o país, o que serve de checagem do método (a conferir com a tábua oficial do IBGE).
- A queda na pandemia foi de cerca de 2,3 anos em ambos os sexos no país, maior no Norte (Amazonas, Roraima, Amapá e Rondônia, mais de 4 anos) e menor em estados como Rio Grande do Sul e Rio Grande do Norte (cerca de 1,2).
- Entre microrregiões, a amplitude entre o percentil 10 e o 90 de e0-80 caiu nos homens de 5,1 anos (2000-2004) para 3,0 (2015-2019), subiu a 3,4 na pandemia e ficou em 2,9 em 2022-2024; nas mulheres foi de 2,8 para 1,6.
- Por idade, a razão entre a taxa do percentil 90 e a do 10 é a maior entre os homens de 15 a 19 anos (cerca de 3,0 em 2015-2019) e cai até cerca de 1,4 depois dos 80; nas mulheres o pico fica na infância (1 a 9 anos, cerca de 2,3) e vai a 1,4 depois dos 80. É um indício a favor da segunda e da terceira hipótese, que ainda precisam de teste formal. Nas faixas de 1 a 14 anos só entram microrregiões com ao menos 20 óbitos na faixa, que são poucas; ler com cautela.

## Decisões e cuidados (valem para todo o projeto)

- Períodos: 2000-2004, 2005-2009, 2010-2014, 2015-2019, 2020-2021 (pandemia, separada) e 2022-2024.
- Faixas de idade: 0, 1-4, 5-9, ..., 75-79 e 80 ou mais. Em município pequeno e em estado com sub-registro, e0 fica instável por causa da faixa de 80 ou mais (exemplos: Maranhão 87 anos para as mulheres em 2000-2004 e Amapá 87 em 2005-2009, que provavelmente são artefatos de sub-registro de óbitos idosos, não vida longa real). Por isso se usa e0-80 (anos vividos entre 0 e 80) para comparar territórios, além de q15-60.
- Unidade instável: menos de 100 óbitos no sexo e no período. Em 2015-2019, cerca de 3.100 municípios são instáveis para homens e 3.700 para mulheres; por isso o agrupamento em microrregiões (586 do IBGE, pelo CADMUN).
- Óbitos com sexo ou idade ignorados saem das tábuas e são contados no resumo. Óbitos de município não identificado (códigos como 120000) entram só no total da UF e do Brasil.
- Códigos de município: o SIM tem 6 ou 7 dígitos conforme o ano (usar os 6 primeiros) e a população tem 7 (cortar o último). Nos arquivos do SIM até 2017 os campos vêm com espaços sobrando ("1   " no sexo); o código descarta os espaços.
- A incerteza considera só os óbitos (Poisson); não inclui a incerteza da população estimada.
- O sub-registro de óbitos é maior no início dos anos 2000 e em locais pequenos e pobres, e tende a elevar a expectativa aparente; não foi corrigido.
- O descompactador dos .dbc (inventario_sim_ac.py) foi acelerado e validado por teste de ida e volta contra o antigo e contra o vetor de teste do zlib.

## Scripts (C:\EXPVIDA)

brasil_expectativa.py (Brasil inteiro), piloto_expectativa.py (funções de tábua de vida, usado pelo anterior), inventario_sim_ac.py (leitura dos .dbc), e os de apoio: conferir_acre_e_populacao.py, inspecionar_populacao.py, inspecionar_cadmun.py, procurar_tabelas_auxiliares.py, diagnostico_codigos.py, diagnostico_sexo.py.

## Arquivos antigos que podem ser apagados

PILOTO_AC_municipios.csv, PILOTO_AC_RESUMO.md, os PILOTO_AC_antes_*, PILOTO_AC_pandemia_* e PILOTO_AC_depois_* (primeira rodada do piloto, três períodos) e a pasta __pycache__. Não podem ser apagados daqui; podem ser apagados por você com segurança.

## Regras do projeto

- Trabalhar só com o que dá para baixar. Nada de dados inventados ou estimados sem fonte.
- Não afirmar ineditismo sem busca de literatura.
- Idade média ao morrer não é expectativa de vida.
- Associação não é causalidade; resultados por território são ecológicos, não individuais.
