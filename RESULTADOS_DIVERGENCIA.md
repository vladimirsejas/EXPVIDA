# Em que idade o território faz diferença? Resultados da análise de divergência por idade

Projeto "Quando o território importa" (pasta C:\EXPVIDA). Documento de 24/11/2026, escrito depois que os quatro scripts desta etapa foram executados. Tudo o que está aqui saiu dos arquivos CSV que acompanham este documento; nada foi estimado à mão. Os resultados são ecológicos (descrevem microrregiões, não pessoas), descritivos e não provam causa.

## Em poucas linhas

Uma correção importante em relação à primeira versão deste documento: ela dizia que as três hipóteses estavam "sustentadas". Isso foi exagerado. A classificação revisada é a seguinte. A H2 (a desigualdade entre os homens é maior na idade adulta jovem) é estatisticamente significativa e robusta: sobrevive à correção para múltiplos testes e a três formas diferentes de agrupar as idades. A H3 (o padrão por idade difere entre os sexos) é estatisticamente significativa quanto à diferença dos perfis, mas a descrição do pico feminino na infância é só evidência parcial, porque falha em um dos seis períodos. A H1 (parte da desigualdade já existe no primeiro ano de vida) tem evidência parcial: o resultado estatístico é inequívoco, mas a medida inclui erros de registro e de população que estes dados não permitem separar, então ela não demonstra desigualdade "real" de mortalidade infantil. Os detalhes e os números estão na seção "As três hipóteses" e em REVISAO_TECNICA.md. Uma validação posterior (seção "Validação do modelo e correção dos intervalos") mostrou que as microrregiões vizinhas se parecem muito e que os intervalos originais eram estreitos demais; com intervalos corrigidos, H2 contra 30 a 59 anos continua significativa nos seis períodos, mas H2 contra 1 a 14 anos deixa de ser significativa na pandemia, e a forma dos picos de H3 só é segura a partir de 2005 (homens) e de 2010 (mulheres). Os valores-p da ordem de 10⁻⁵⁷ citados abaixo vêm do bootstrap sem blocos e não devem ser usados.

A proposta experimental da IDT (Idade de Divergência Territorial) funciona só para divergências fortes: é tardia e instável quando a diferença é modesta e não existe para a maioria das microrregiões. A IMD (Idade-Mediana da Diferença) foi construída como medida complementar, não como substituta: ela mede outra coisa (a idade em que se acumula metade da diferença em anos de vida, e não a idade em que a diferença começa) e a superioridade sobre a IDT não foi demonstrada.

## O que foi feito

Primeiro foi conferido o que já existia. As taxas por idade de BRASIL_taxas_por_idade.csv, passadas pela mesma tábua de vida de piloto_expectativa.py, reproduzem as expectativas de vida já publicadas (BRASIL_microrregioes.csv e BRASIL_ufs_e_brasil.csv) com diferença máxima de 0,00005 ano, e os óbitos e as pessoas-ano batem exatamente. Isso confirma fórmulas e denominadores. Um detalhe importante: as taxas por idade só foram gravadas para microrregião, UF e Brasil, não para município. Por isso toda esta análise é feita nas 558 microrregiões.

Depois foram escritos quatro scripts (todos rodam com "Run Python File", precisam de numpy, scipy e pandas, não baixam nada e não criam pastas):

1. `divergencia_territorial.py` mede a desigualdade entre microrregiões em cada idade, sexo e período.
2. `testes_hipoteses.py` testa H1, H2 e H3.
3. `idt_experimento.py` define a regra da IDT e a testa.
4. `imd_alternativa.py` propõe e testa a IMD. A biblioteca comum está em `divergencia_modelo.py` (não precisa ser aberta).

## A medida: como separar diferença sistemática de acaso

Com poucos óbitos, uma microrregião pode parecer pior ou melhor que o Brasil só por sorte. Para cada idade, o modelo calcula a razão de risco (RR) de cada microrregião, que é a taxa dela dividida pela taxa do resto do Brasil, e estima o quanto essas razões variam entre as microrregiões depois de descontar o acaso de Poisson. O resultado é o número tau (τ), o desvio-padrão do logaritmo da razão de risco sistemática. "Sistemática" quer dizer tudo o que se repete além do acaso: mortalidade de fato diferente, mas também erros de registro de óbitos e de estimativa da população, que o modelo não distingue. Quanto maior o τ, maior a desigualdade territorial naquela idade. Uma tradução prática: a razão esperada entre a microrregião do percentil 90 e a do percentil 10 é e elevado a 2,563 vezes τ (por exemplo, τ de 0,41 equivale a cerca de 2,9 vezes). O modelo foi testado antes de ser usado: em dados simulados com τ conhecido (0; 0,05; 0,2; 0,5) ele recuperou 0,001; 0,055; 0,194; 0,461.

Esta é uma correção importante do que já estava no BRASIL_RESUMO.md. A razão P90/P10 das taxas observadas mistura desigualdade sistemática com acaso, e como só entram microrregiões com pelo menos 20 óbitos na faixa, também seleciona as microrregiões de maior mortalidade nas idades com poucas mortes. O efeito é grande nas mulheres jovens: em 15 a 19 anos a razão observada é 1,91, mas a razão esperada sem o acaso é 1,65. A razão observada exagera a desigualdade das mulheres e diminui a distância para os homens.

## Onde a desigualdade territorial é maior (período 2015-2019, antes da pandemia)

| Faixa | Homens τ (IC 95%) | Mulheres τ (IC 95%) |
|---|---|---|
| 0 | 0,20 (0,18 a 0,22) | 0,19 (0,17 a 0,20) |
| 1 a 14 | 0,23 (0,20 a 0,26) | 0,24 (0,20 a 0,27) |
| 15 a 29 | 0,34 (0,32 a 0,36) | 0,15 (0,14 a 0,16) |
| 30 a 59 | 0,14 (0,13 a 0,15) | 0,13 (0,12 a 0,13) |
| 60 a 79 | 0,16 (0,15 a 0,17) | 0,14 (0,13 a 0,15) |
| 80 e mais | 0,12 (0,11 a 0,13) | 0,12 (0,11 a 0,14) |

Nas 18 faixas individuais o pico dos homens é 15 a 19 anos (τ 0,41, IC 0,39 a 0,44) e o das mulheres é 1 a 4 anos (τ 0,31, IC 0,28 a 0,34). A tabela completa, por sexo, período e faixa, está em DIVERGENCIA_POR_IDADE.csv, com intervalo de confiança, razão P90/P10 esperada e a observada no estilo do BRASIL_RESUMO.md para comparar.

Estabilidade: as diferenças estimadas de cada microrregião se repetem entre períodos. A correlação entre 2010-2014 e 2015-2019 nos homens é de 0,66 a 0,87 de 15 anos em diante, e nas mulheres de 0,35 a 0,86 (menor na idade adulta jovem, onde há poucos óbitos). Na infância ela fica entre 0,34 e 0,66 (DIVERGENCIA_ESTABILIDADE.csv).

## As três hipóteses

Os testes usam seis faixas agrupadas (0; 1 a 14; 15 a 29; 30 a 59; 60 a 79; 80 e mais) para dar mais óbitos a cada estimativa, e bootstrap de microrregiões (1000 repetições em 2015-2019, 300 nos demais períodos). Resultados em TESTES_HIPOTESES.csv. Foram feitos 30 testes (H1a, H2 e H3 por período); aplicando a correção de Holm com valores-p analíticos, os 30 continuam significativos a 5% quando se usam os intervalos sem blocos (TESTES_HIPOTESES_HOLM.csv); com intervalos por blocos de estados, ver a seção de validação, onde o H2 da pandemia contra 1 a 14 anos deixa de ser significativo. O mais frágil é o H2 da pandemia contra a faixa de 1 a 14 anos (p ajustado 0,041). Para não depender da escolha das faixas, H2 e H3 foram refeitos em 2015-2019 com dois outros agrupamentos (SENSIBILIDADE_FAIXAS.csv) e a conclusão se manteve.

| Hipótese | Classificação | Por quê |
|---|---|---|
| H2, a desigualdade dos homens é maior em 15 a 29 anos | Estatisticamente significativa e robusta | Razão 1,49 (IC por blocos 1,20 a 1,84) contra 1 a 14 anos e 2,46 (1,83 a 3,06) contra 30 a 59 em 2015-2019; contra 30 a 59 é significativa nos seis períodos; contra 1 a 14 é significativa até 2019, não na pandemia; robusta a outros agrupamentos de faixas, à retirada de qualquer microrregião ou estado e à t de Student |
| H3, o padrão por idade difere entre os sexos | Significativa quanto à diferença; parcial quanto à forma do pico feminino | Wald significativo nos seis períodos também com intervalos por blocos de estados (valores originais p de 10⁻²¹ a 10⁻⁵⁷, otimistas); pico masculino em 15 a 29 seguro a partir de 2005; pico feminino em 1 a 14 seguro só a partir de 2010 (em 2000-2004 aparece em 80 e mais) |
| H1, parte da desigualdade já existe no primeiro ano de vida | Evidência parcial | τ da faixa 0 maior que zero em todos os casos (trivial com tantos óbitos); participação na variância da e0-80 de 6,7% nos homens e 14,1% nas mulheres; mas inclui erros de registro e de população |

Tabela por período (cada célula com intervalo de confiança de 95%):

| periodo | H1a tau0 H | H1a tau0 M | H1b part, H | H1b part, M | H2 15-29/1-14 | H2 15-29/30-59 | H3 Wald (5 gl) | H3 p |
|---|---|---|---|---|---|---|---|---|
| 2000-2004 | 0,261 (0,245 a 0,276) | 0,258 (0,240 a 0,275) | 5,9% (4,4 a 7,2) | 16,7% (14,8 a 18,9) | 1,44 (1,29 a 1,63) | 1,23 (1,16 a 1,31) | 274,4 | 3,2e-57 |
| 2005-2009 | 0,215 (0,200 a 0,228) | 0,217 (0,200 a 0,230) | 4,7% (3,4 a 6,0) | 14,0% (12,0 a 16,1) | 1,35 (1,18 a 1,53) | 1,42 (1,31 a 1,55) | 182,3 | 1,7e-37 |
| 2010-2014 | 0,186 (0,171 a 0,199) | 0,180 (0,163 a 0,194) | 5,0% (3,7 a 6,6) | 10,7% (8,5 a 12,9) | 1,40 (1,25 a 1,57) | 1,87 (1,71 a 2,03) | 221,2 | 8,1e-46 |
| 2015-2019 | 0,201 (0,184 a 0,216) | 0,186 (0,167 a 0,204) | 6,7% (5,2 a 8,3) | 14,1% (11,5 a 16,8) | 1,49 (1,31 a 1,70) | 2,46 (2,25 a 2,70) | 212,2 | 6,9e-44 |
| 2020-2021 pandemia | 0,214 (0,194 a 0,233) | 0,209 (0,186 a 0,226) | 7,1% (5,6 a 8,5) | 8,1% (6,0 a 10,2) | 1,13 (1,01 a 1,28) | 2,45 (2,25 a 2,68) | 104,3 | 6,6e-21 |
| 2022-2024 | 0,192 (0,168 a 0,217) | 0,200 (0,180 a 0,223) | 9,6% (7,9 a 11,6) | 16,4% (13,1 a 19,2) | 1,29 (1,13 a 1,50) | 2,34 (2,14 a 2,54) | 105,5 | 3,7e-21 |

**H2.** Em 2015-2019 o τ dos homens em 15 a 29 anos é 1,49 vez o de 1 a 14 anos e 2,46 vezes o de 30 a 59 anos. O período mais fraco é a pandemia (1,13; IC 1,01 a 1,28). Limitação: o resultado é ecológico e de todas as causas somadas; não diz que causa produz a concentração nessa idade.

**H3.** O teste de Wald de perfis paralelos (5 graus de liberdade, covariância por bootstrap) rejeita o paralelismo nos seis períodos. O pico dos homens fica em 15 a 29 anos em todos eles. O pico das mulheres fica em 1 a 14 anos de 2005-2009 em diante; em 2000-2004 apareceu em 80 e mais, época em que o sub-registro de óbitos idosos é mais provável. Por isso o que está demonstrado é que os perfis diferem, e o formato "pico feminino na infância" é só parcialmente sustentado. Nos sorteios do bootstrap, os picos coincidiram em no máximo 2% das vezes.

**H1.** Em 2015-2019 o τ da faixa 0 é cerca de 0,20 nos homens e 0,19 nas mulheres (razão P90/P10 esperada de 1,6 a 1,7). A participação do primeiro ano na variância entre microrregiões da e0-80 é de 6,7% nos homens (IC 5,2 a 8,3%) e 14,1% nas mulheres (IC 11,5 a 16,8%); entre os seis períodos varia de 4,7% a 9,6% nos homens e de 8,1% a 16,7% nas mulheres. É uma parte, não a maior: nos homens, 15 a 29 anos e 30 a 59 anos respondem por cerca de 37% e 39%. Por que é só parcial: o denominador do primeiro ano é a população estimada de 0 ano, não os nascidos vivos, e o sub-registro de óbitos infantis varia entre regiões; ambos inflam o τ da faixa 0 sem serem desigualdade de mortalidade. Para demonstrar H1 seria preciso refazer a faixa 0 com nascidos vivos (SINASC) e correção de sub-registro.

## Validação do modelo e correção dos intervalos (25/11/2026)

Esta seção corrige a anterior onde ela era otimista. A pergunta foi: os intervalos e valores-p dos testes continuam válidos quando se leva em conta que microrregiões vizinhas se parecem? Os programas são `validacao_tau.py` (cinco etapas) e `comparacao_sexos.py`; os resultados estão em VALIDACAO_*.csv e DIFERENCAS_TAU_*.csv. O mapa dos municípios veio de um repositório público do GitHub e a ligação município-microrregião, da tabela CADMUN do DATASUS (a mesma do EXPVIDA).

**Dependência espacial: é forte.** O índice de Moran dos efeitos territoriais estimados fica entre 0,33 e 0,65 nas 12 combinações de sexo e faixa, contra cerca de zero esperado sem dependência (valor-p 0,003, o mínimo possível com 300 simulações). Os estados explicam de 26% a 57% da variação entre microrregiões, contra uns 5% esperados por acaso. O bootstrap anterior, que sorteava microrregiões soltas, tratava vizinhas como independentes.

**Efeito nos intervalos.** Sorteando blocos geográficos inteiros (27 estados, ou 20 ou 60 agrupamentos espaciais), os intervalos ficam de 1,7 a 2,6 vezes mais largos. Em 2015-2019, a razão de H2 contra 30-59 anos passa de 2,46 (2,25 a 2,70) para 2,46 (1,83 a 3,06), e contra 1-14 anos de 1,49 (1,31 a 1,70) para 1,49 (1,20 a 1,84). O Wald de H3 cai de 206 para 92 a 114, e os valores-p de 10⁻⁵⁷ para ordens de 10⁻¹⁸ ou maiores. Valores-p extremos não devem ser reportados; basta "p < 0,001".

**Simulações com verdade conhecida** (efeitos normais, t de 3 graus de liberdade e assimétricos; dependência espacial nula ou forte; τ verdadeiro de 0,05, 0,15 e 0,30; óbitos esperados reais de homens em 15-29 e 30-59; 150 repetições cada). O estimador de τ é pouco enviesado: de −7% a +4% em todos os cenários. A cobertura do intervalo de 95% do modelo para o τ populacional é de 94% a 99% com efeitos normais e independentes, mas cai para 47% a 73% com dependência espacial forte, 40% a 62% com efeitos não normais e 23% a 65% com os dois problemas. Já a cobertura do desvio-padrão realizado nas próprias 558 microrregiões ficou entre 79% e 100%. Em palavras: para descrever as 558 microrregiões observadas, os intervalos antigos eram razoáveis; para generalizar além delas (por exemplo, afirmar que o padrão persiste), eles eram otimistas, e os intervalos por blocos são os adequados.

**Distribuição dos efeitos.** Com a t de Student (3, 5 e 10 graus de liberdade), τ muda pouco: para 10 graus de liberdade a diferença é de no máximo 0,012. Em algumas faixas a t ajusta melhor que a normal (por exemplo, homens de 30-59 e mulheres de 80 e mais), mas na faixa principal, homens de 15-29, a normal ajusta melhor (log-verossimilhança 6 a 27 pontos acima da t). As razões de H2 ficam entre 1,46 e 1,63 (contra 1-14) e entre 2,37 e 2,65 (contra 30-59), próximas de 1,49 e 2,46.

**Influência.** Retirar qualquer microrregião muda a razão de H2 de 1,49 para entre 1,48 e 1,54 e a de 2,46 para entre 2,45 e 2,50. Retirar um estado inteiro, de cada vez: a razão contra 30-59 fica entre 2,14 (sem São Paulo) e 2,58; a razão contra 1-14, entre 1,41 e 1,57; o pico dos homens permanece em 15-29 e o das mulheres em 1-14 em todos os 27 casos.

**Todos os períodos, com intervalos por blocos de estados** (300 sorteios):

| Período | H2: 15-29 / 1-14 (IC 95%) | H2: 15-29 / 30-59 (IC 95%) | H3 Wald (5 gl) | Prob. do pico dos homens ser 15-29 | Prob. do pico das mulheres ser 1-14 |
|---|---|---|---|---|---|
| 2000-2004 | 1,44 (1,20 a 1,71) | 1,23 (1,10 a 1,41) | 71,5 | 68% | 0% |
| 2005-2009 | 1,35 (1,11 a 1,79) | 1,42 (1,26 a 1,62) | 63,9 | 92% | 47% |
| 2010-2014 | 1,40 (1,22 a 1,78) | 1,87 (1,56 a 2,25) | 170,9 | 100% | 89% |
| 2015-2019 | 1,49 (1,20 a 1,84) | 2,46 (1,83 a 3,06) | 96,8 | 100% | 100% |
| 2020-2021 pandemia | 1,13 (0,88 a 1,42) | 2,45 (1,78 a 3,09) | 39,6 | 86% | 100% |
| 2022-2024 | 1,29 (0,99 a 1,66) | 2,34 (1,73 a 2,84) | 45,8 | 97% | 98% |

Leitura. H2 contra 30-59 anos é significativa nos seis períodos (limite inferior de 1,10 a 1,83). H2 contra 1-14 anos é significativa de 2000-2004 a 2015-2019 (limite inferior de 1,11 a 1,22), não é significativa na pandemia (IC 0,88 a 1,42) e fica no limite em 2022-2024 (IC 0,99 a 1,66). H3 rejeita o paralelismo dos perfis em todos os períodos (Wald de 40 a 171). A forma dos picos é menos firme: o pico masculino em 15-29 é seguro (86% a 100%) a partir de 2005-2009 e tem só 67% em 2000-2004; o pico feminino em 1-14 é seguro a partir de 2010-2014 (89% a 100%) e tem só 48% em 2005-2009.

**Diferenças absolutas e comparação entre os sexos** (intervalos por blocos de estados; DIFERENCAS_TAU_FAIXAS.csv, DIFERENCAS_TAU_IDADES.csv e FIGURA_TAU_IDADE_SEXO.png). Nos homens, em 2015-2019, τ(15-29) − τ(1-14) = 0,11 (IC 0,05 a 0,16) e τ(15-29) − τ(30-59) = 0,20 (0,13 a 0,25). A razão P90/P10 esperada dos homens em 15-29 é 2,41, contra 1,43 em 30-59 e 1,81 em 1-14; nas mulheres de 15-29 é 1,47. A diferença homens menos mulheres no τ é significativa em 15-29 anos nos seis períodos (de 0,13 a 0,19) e é maior aos 15 a 19 anos (0,22; IC 0,15 a 0,27). Dos 15 aos 44 anos os homens têm τ maior; dos 45 aos 79 e aos 80 e mais, os dois sexos são praticamente iguais. O excesso feminino na infância é pequeno: aos 1 a 4 anos, 0,31 nas mulheres e 0,27 nos homens (diferença −0,04; IC −0,08 a −0,01), e na faixa de 1 a 14 anos a diferença é significativa em um período só (2005-2009).

**Limitações que continuam abertas.** O bootstrap por estados tem poucos blocos (27) e é uma aproximação; os cenários de simulação cobrem uma estrutura espacial (autorregressiva com ρ = 0,9) e dois tipos de desvio da normalidade; a medida continua incluindo erros de registro de óbitos e de população; a pandemia tem poucos óbitos por faixa; e H1 não foi alterada por esta validação.

## Análise secundária da pandemia (25/11/2026)

Pergunta: a diferença sistemática entre microrregiões (τ) mudou em 2020-2021 e em 2022-2024 em relação a 2015-2019? O programa é `pandemia_tau.py` e o resultado está em PANDEMIA_MUDANCA_TAU.csv. Os intervalos vêm do bootstrap por blocos de estados, sorteando os mesmos estados em todos os períodos, de modo que a diferença entre períodos tem intervalo próprio (300 sorteios). São 72 comparações com 95% cada, então uma ou outra pode sair "significativa" por acaso; vale apenas o que é grande e coerente.

**Em 2020-2021 (pandemia).** Nos homens, o único aumento claro é na infância (1 a 14 anos): τ sobe de 0,21 para cerca de 0,27, uma razão de 1,25 (IC 1,16 a 1,40). Nas outras faixas masculinas não há mudança distinguível de zero. Nas mulheres o aumento é amplo: de 1,10 a 1,27 vezes em todas as faixas até 79 anos (1 a 14 anos: 1,27, IC 1,08 a 1,43; 30 a 59: 1,19, IC 1,08 a 1,32); só aos 80 e mais não há mudança. Consequência: a diferença homens menos mulheres diminui em 15 a 29 anos (−0,04; IC −0,07 a −0,01) e em 30 a 59 anos (−0,03; IC −0,05 a −0,02). Em palavras: na pandemia a desigualdade territorial das mulheres adultas se aproximou da dos homens. A razão H2 contra a infância cai (−0,35; IC −0,53 a −0,24), porque a infância subiu, não porque os 15 a 29 anos tenham caído; contra 30 a 59 anos não há mudança clara.

**Em 2022-2024.** A desigualdade territorial volta ao nível anterior ou abaixo dele. Nos homens, τ é menor em 15 a 29 anos (razão 0,90; IC 0,81 a 0,97) e em 60 a 79 (0,84; IC 0,79 a 0,89); nas mulheres, em 60 a 79 (0,88) e em 80 e mais (0,83). A infância volta ao patamar de 2015-2019 nos dois sexos. A diferença homens menos mulheres em 15 a 29 anos continua menor (−0,04; IC −0,07 a −0,02).

**O que isto sustenta e o que não sustenta.** Está demonstrado que o perfil de τ por idade mudou na pandemia, de forma diferente nos dois sexos, e que o pico masculino em 15 a 29 anos não desapareceu (H2 contra 30 a 59 anos não muda). Não está demonstrado por que τ mudou: o modelo mede a variação sistemática entre microrregiões, que inclui a covid-19, mas também mudanças de registro, de acesso a serviços e de estimativa de população; τ não se decompõe em parcelas somáveis. Os intervalos da infância são largos porque há poucos óbitos por microrregião. Separar o efeito da covid-19 exigiria a causa básica do óbito (CID-10), que é uma etapa posterior.

## Narrativa científica proposta e esboço das figuras (25/11/2026)

**A mensagem central, no que os dados sustentam.** Em 2015-2019, a diferença sistemática entre microrregiões na mortalidade é maior nos homens de 15 a 29 anos (τ cerca de 0,34; no máximo 0,41 aos 15 a 19) do que em qualquer outra idade ou nas mulheres da mesma idade (cerca de 0,15 a 0,20). Em outras palavras, uma microrregião de risco alto (percentil 90) tem cerca de 2,4 vezes a mortalidade de uma de risco baixo (percentil 10) entre homens jovens, contra cerca de 1,4 vezes entre 30 e 59 anos. Depois dos 45 anos os dois sexos são praticamente iguais. Esse resultado resiste à correção para dependência espacial, a outros agrupamentos de idade, à retirada de qualquer estado ou microrregião e a efeitos não normais.

**Um ponto que corrige uma leitura comum.** Esse padrão não é estável no tempo. A razão τ(15-29)/τ(30-59) dos homens cresceu de 1,23 em 2000-2004 para 1,42, 1,87 e 2,46 em 2015-2019 (Figura B), e ficou em 2,45 e 2,34 depois. O que aparece em todos os períodos é a direção (razão acima de 1); a magnitude é recente. Correção posterior (estudo de causas): esse crescimento da razão não vem de um aumento da desigualdade nos homens de 15 a 29 anos, cujo τ ficou entre 0,27 e 0,34 nos seis períodos com intervalos que se sobrepõem. Vem da queda do τ dos homens de 30 a 59 anos, de 0,25 em 2000-2004 para 0,14 em 2015-2019 e 0,13 em 2022-2024, com intervalos que deixam de se sobrepor. A narrativa deve dizer que a desigualdade territorial dos homens jovens se manteve enquanto a dos homens adultos diminuiu, e não que a dos jovens cresceu.

**O que a narrativa não pode afirmar.** Que as diferenças regionais brasileiras "são produzidas no início da vida adulta": τ mede dispersão entre territórios na escala logarítmica em cada idade, não a origem das diferenças na esperança de vida. Nem que a causa seja violência: o modelo usa todas as causas juntas. A discussão pode e deve mencionar que homicídios, acidentes de transporte e outras causas externas são candidatos plausíveis, porque a literatura brasileira os associa à mortalidade de homens jovens, mas isso é hipótese ainda não testada com estes dados (as referências citadas por outros colegas não foram conferidas por mim na fonte). Testá-la exige a causa básica do óbito, o estudo seguinte.

**H1 passa a ser exploratória.** Dos três resultados, H1 (parte da desigualdade já existe no primeiro ano de vida) é a mais frágil, porque a medida da faixa 0 inclui erro de população e sub-registro de óbitos infantis. No manuscrito ela deve aparecer como análise exploratória, não como hipótese principal; só passaria a principal com nascidos vivos (SINASC) e correção de sub-registro. A classificação anterior ("evidência parcial") fica mantida; muda apenas o lugar dela no texto.

**A pandemia como suplemento.** A análise de 2020-2021 e 2022-2024 amplia a história (o perfil mudou, de forma diferente nos dois sexos), mas não sustenta a mensagem central. No manuscrito, vai como seção curta de robustez, com a tabela completa em material suplementar.

**Figuras principais** (esboço em FIGURAS_ESBOCO.png, feito por `figuras_esboco.py` com resultados já calculados). A: τ por idade e sexo em 2015-2019, com intervalos por blocos de estados. B: razão τ(15-29)/τ(30-59) nos seis períodos. C: risco relativo estimado de cada microrregião para homens de 15 a 29 anos, em relação ao Brasil (de 0,47 a 2,45 vezes). Na C, os pontos são centroides, não polígonos; o padrão visível é de risco menor no Sudeste e no Sul e maior no litoral do Nordeste e em partes do Norte. Esse padrão descreve onde o excesso está estimado; não o explica. Para a versão do manuscrito, a C deve ser refeita com os polígonos das microrregiões, que o mapa municipal já permite.

## A IDT: viável só em parte

**Regra (fixada antes de olhar os resultados por microrregião).** Em cada faixa de idade, compara-se o número de óbitos observado com o esperado pela taxa do resto do Brasil, com teste exato de Poisson, corrigido para comparações múltiplas pelo método de Benjamini-Hochberg (taxa de falsas descobertas de 5%, sobre todos os 558 x 18 testes de cada sexo e período). Uma faixa é "divergente" se passa no teste e a diferença é relevante (RR de pelo menos 1,2 para pior, ou no máximo 1/1,2 para melhor). A IDT é a idade em que começa a primeira sequência de pelo menos 2 faixas consecutivas divergentes no mesmo sentido. Sem sequência, a microrregião fica sem IDT, em vez de receber uma idade inventada.

**O que se verificou** (IDT_AVALIACAO.csv e IDT_POR_MICRORREGIAO.csv):

Poder. A menor razão de risco que uma microrregião mediana consegue detectar (poder de 80%, nível 0,001) é 1,15 aos 80 anos ou mais e 1,24 a 1,37 entre 60 e 79 anos, mas sobe para 1,5 a 1,6 aos 15 a 44 anos nos homens, 2,4 a 2,8 nas mulheres de 15 a 29 anos e chega a 3 ou mais nas faixas de 1 a 14 anos (4,2 nos homens e 5,2 nas mulheres em 5 a 9 anos). Em idades jovens, para a maioria das microrregiões, só divergências enormes são detectáveis.

Falsos positivos. Em 200 simulações sem nenhuma divergência real, nenhuma microrregião recebeu IDT.

Recuperação de divergência conhecida (simulações de RR 1,4 e 1,2 a partir de 15, 40 ou 60 anos). Com RR 1,4, a regra detecta 97% a 100% das microrregiões nos homens e 91% a 100% nas mulheres, e nos homens o erro mediano da idade estimada é de 0 a 5 anos. Nas mulheres ele é de 0 a 5 anos nas microrregiões grandes, mas chega a 20 anos de atraso nas médias e 35 nas pequenas. Com RR 1,2 a detecção cai para 27% a 94% e a IDT sai tardia (erro mediano de 5 a 40 anos nos homens e de 5 a 50 nas mulheres).

Dados reais. Em 2015-2019, 178 das 558 microrregiões (32%) têm IDT adversa nos homens e 72 (13%) nas mulheres. Nos homens, o início mais frequente é aos 15 anos (48 microrregiões), depois 25 anos (22), 0 ano (21) e 30 anos (21). Entre períodos (2010-2014 contra 2015-2019 e 2015-2019 contra 2022-2024), a correlação de Spearman da IDT nas microrregiões que a têm nos dois períodos é de 0,72 a 0,80, mas só 30% a 37% têm exatamente a mesma faixa de início e 46% a 69% a mesma ou a vizinha.

**Conclusão.** A IDT é uma regra com falso positivo controlado e válida, sem falsos positivos, mas só como medida para divergências fortes e persistentes. Não é um indicador universal: não existe para a maioria das microrregiões e, quando a diferença é modesta, aponta idades tardias. Não deve ser apresentada como indicador consolidado.

## A alternativa: IMD (Idade-Mediana da Diferença)

A IMD parte da decomposição de Arriaga, que reparte a diferença entre a e0-80 da microrregião e a do Brasil (em anos de vida) entre as faixas de idade. A IMD é a idade de início da primeira faixa em que o acumulado chega à metade da diferença total, ou seja, "metade da diferença em anos de vida já foi formada até esta idade". Como cada faixa contribui com anos de vida, a soma é estável mesmo com poucos óbitos por faixa. Ela só é definida quando a diferença total é significativa (erro-padrão por bootstrap de Poisson, com correção FDR de 5% sobre as 558 microrregiões) e tem pelo menos 0,3 ano. A primeira versão sem essa correção marcava cerca de 6% das microrregiões por acaso; a versão final marca em média 0,2 a 0,25 microrregião em 558 num cenário sem diferença real (IMD_AVALIACAO.csv e IMD_POR_MICRORREGIAO.csv, com intervalo de confiança de cada IMD).

Em 2015-2019 a IMD é definida em 387 microrregiões nos homens (69%; 139 piores e 248 melhores que o Brasil) e em 287 nas mulheres (51%; 129 piores e 158 melhores). Na simulação, com RR 1,4 ela é definida em 85% a 100% das microrregiões nos homens e 81% a 100% nas mulheres, e em 95% a 100% dos casos definidos o valor fica a até 5 anos do valor que a IMD teria sem ruído (esse é o critério de erro: é a estabilidade da medida, não a idade em que a divergência começa). Com RR 1,2 a detecção vai de 32% a 100% nos homens e de 26% a 100% nas mulheres, conforme o tamanho da microrregião e a idade de início (é pior quando a diferença começa aos 60 anos), e o valor fica a até 5 anos do valor sem ruído em 74% a 100% dos casos definidos. Entre períodos, a correlação de Spearman da IMD é 0,69 a 0,78 e a da diferença total G é de 0,77 a 0,82. Mas a idade em si continua incerta: só 66% a 70% das IMD repetem a mesma faixa ou a vizinha entre períodos. O kappa de ter ou não IMD é baixo (0,25 a 0,44), porque há muitos casos próximos do limite de significância.

Em resumo: a IMD é uma medida complementar à IDT, não uma versão melhor dela. Ela mede outra coisa: a idade em que se acumula metade da diferença em anos de vida, e não a idade em que a diferença começa. Na simulação, uma divergência que começa aos 15, 40 ou 60 anos resulta em IMD de cerca de 50, 60 e 65 nos homens (55, 60 e 65 nas mulheres), mesmo sem ruído algum; logo a IMD não estima a idade de início. Com RR 1,4 a IDT detecta mais microrregiões que a IMD (97% a 100% contra 85% a 100% nos homens; 91% a 100% contra 81% a 100% nas mulheres); com RR 1,2, microrregiões pequenas e diferença a partir dos 15 ou 40 anos, a IMD detecta mais (por exemplo 98% contra 66% nos homens aos 15 anos). Na reprodutibilidade entre períodos a IMD não é melhor que a IDT: correlação de Spearman de 0,69 a 0,78 contra 0,72 a 0,80, e kappa de ter ou não a medida de 0,25 a 0,44 contra 0,52 a 0,65. A parte favorável à IMD é só que a mesma faixa ou a vizinha se repete em 66% a 70% dos casos, contra 46% a 69% da IDT. A vantagem demonstrada da IMD é ser definida para mais microrregiões sob divergências modestas, com controle de falsos positivos; a reprodutibilidade é moderada e comparável à da IDT. A idade exata de uma microrregião individual tem incerteza de cerca de uma faixa (5 anos) em um terço dos casos. Serve para descrever padrões e comparar grupos de microrregiões, não para afirmar uma idade precisa de uma microrregião específica. As microrregiões "melhores que o Brasil" são em média menores que as "piores" (mediana de óbitos de homens em 2015-2019: 3.353 contra 5.219; mulheres: 2.593 contra 3.530). Sub-registro de óbitos infla a expectativa de vida, mas estes dados não permitem dizer se isso explica o grupo; a localização (interior ou capital) não foi verificada. Não leia esse grupo como "vida longa comprovada".

Exemplos (homens, 2015-2019, maiores diferenças para pior): Laranjeiras (SE), Itabaiana (SE), Itaguaí (RJ), Própria (SE) e Bonito (PE), com IMD entre 25 e 45 anos. Isto diz em que idade a diferença se forma, não por quê. Com estes dados (todas as causas somadas) não é possível atribuir causa.

## Confiabilidade

Sub-registro de óbitos. Não pode ser corrigido com os dados do projeto. Um sinal de alerta é que o τ nas idades de 45 anos em diante era muito maior em 2000-2004 (nos homens, de 0,25 a 0,31) do que em 2015-2019 (de 0,12 a 0,16) e em 2022-2024 (de 0,11 a 0,15). A queda é compatível com melhora da cobertura do registro e também com convergência real, e estes dados não separam as duas coisas. Para comparações no tempo, 2000-2009 deve ser lido com mais cuidado que 2010 em diante.

Incerteza da população estimada. Não existe nos arquivos. Como teste de sensibilidade, supôs-se um erro relativo hipotético de 2% e de 5% na população de cada microrregião. Em 2015-2019, um erro de 5% reduz o τ em cerca de 0,01 no máximo (por exemplo, de 0,123 para 0,112 aos 80 anos ou mais nos homens). Os intervalos de confiança do modelo continuam considerando só o acaso dos óbitos.

Microrregiões pequenas. Excluí-las (ficando só as com pelo menos 500 óbitos no sexo e no período) não muda o τ de forma perceptível em 2015-2019, então a desigualdade medida não vem das menores.

Escala. Usando a UF como unidade em vez da microrregião, o τ cai (homens aos 15 a 19 anos: 0,29 na UF contra 0,41 na microrregião). Parte da desigualdade fica escondida dentro das UFs. Isto importa para a decisão ainda pendente sobre a unidade territorial final. Município não pôde ser analisado por idade porque as taxas por idade não foram gravadas por município. Os valores completos estão em DIVERGENCIA_SENSIBILIDADE.csv.

Tau de 2015-2019 em cada cenário (H = homens, M = mulheres; "pop" é o erro hipotético de população; "só grandes" exclui microrregiões com menos de 500 óbitos; UF usa a UF como unidade):

| idade | tau H | pop 2%% H | pop 5%% H | so grandes H | UF H | tau M | pop 2%% M | pop 5%% M | so grandes M | UF M |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0,201 | 0,200 | 0,194 | 0,200 | 0,176 | 0,186 | 0,185 | 0,179 | 0,181 | 0,166 |
| 1-4 | 0,267 | 0,266 | 0,262 | 0,267 | 0,241 | 0,310 | 0,309 | 0,306 | 0,302 | 0,242 |
| 5-9 | 0,241 | 0,240 | 0,235 | 0,240 | 0,228 | 0,231 | 0,230 | 0,225 | 0,230 | 0,187 |
| 10-14 | 0,228 | 0,227 | 0,222 | 0,228 | 0,178 | 0,182 | 0,181 | 0,175 | 0,177 | 0,163 |
| 15-19 | 0,410 | 0,410 | 0,407 | 0,410 | 0,292 | 0,195 | 0,194 | 0,188 | 0,186 | 0,155 |
| 20-24 | 0,354 | 0,354 | 0,351 | 0,355 | 0,282 | 0,146 | 0,145 | 0,138 | 0,145 | 0,114 |
| 25-29 | 0,314 | 0,313 | 0,310 | 0,312 | 0,261 | 0,157 | 0,156 | 0,149 | 0,157 | 0,131 |
| 30-34 | 0,251 | 0,250 | 0,246 | 0,252 | 0,208 | 0,143 | 0,141 | 0,134 | 0,143 | 0,115 |
| 35-39 | 0,210 | 0,210 | 0,204 | 0,210 | 0,156 | 0,141 | 0,140 | 0,132 | 0,141 | 0,101 |
| 40-44 | 0,168 | 0,167 | 0,161 | 0,168 | 0,130 | 0,125 | 0,123 | 0,115 | 0,125 | 0,090 |
| 45-49 | 0,144 | 0,143 | 0,135 | 0,144 | 0,099 | 0,137 | 0,135 | 0,127 | 0,137 | 0,090 |
| 50-54 | 0,134 | 0,133 | 0,125 | 0,134 | 0,090 | 0,130 | 0,129 | 0,120 | 0,130 | 0,093 |
| 55-59 | 0,141 | 0,139 | 0,132 | 0,140 | 0,091 | 0,136 | 0,134 | 0,126 | 0,136 | 0,100 |
| 60-64 | 0,151 | 0,149 | 0,142 | 0,150 | 0,099 | 0,149 | 0,147 | 0,140 | 0,148 | 0,096 |
| 65-69 | 0,154 | 0,153 | 0,146 | 0,153 | 0,093 | 0,147 | 0,145 | 0,138 | 0,146 | 0,092 |
| 70-74 | 0,161 | 0,160 | 0,153 | 0,161 | 0,096 | 0,144 | 0,143 | 0,135 | 0,144 | 0,091 |
| 75-79 | 0,159 | 0,157 | 0,150 | 0,158 | 0,090 | 0,136 | 0,135 | 0,127 | 0,136 | 0,076 |
| 80+ | 0,123 | 0,121 | 0,113 | 0,122 | 0,073 | 0,122 | 0,121 | 0,112 | 0,121 | 0,076 |

H2 e H3 com outros agrupamentos de faixas, 2015-2019 (SENSIBILIDADE_FAIXAS.csv):

| agrupamento | teste | estimativa (IC 95%) |
|---|---|---|
| B | H2 tau(10-24)/tau(1-9) | 1,41 (1,22 a 1,61) |
| B | H2 tau(10-24)/tau(25-44) | 1,64 (1,53 a 1,73) |
| B | H3 Wald paralelismo (6 gl) = 221,5; pico homens=10-24; pico mulheres=1-9 | Wald 221,5, p = 5,0e-45 |
| C | H2 tau(15-24)/tau(1-14) | 1,61 (1,40 a 1,81) |
| C | H2 tau(15-24)/tau(25-34) | 1,35 (1,27 a 1,41) |
| C | H3 Wald paralelismo (6 gl) = 215,1; pico homens=15-24; pico mulheres=1-14 | Wald 215,1, p = 1,2e-43 |

População de idade 0 e sub-registro infantil. O denominador do primeiro ano é a população estimada de 0 ano, não os nascidos vivos, e o sub-registro de óbitos infantis varia entre regiões. Ambos podem inflar o τ da faixa 0 e a participação dele na H1.

Pandemia. Em 2020-2021, o τ de 5 a 14 anos nas mulheres sobe (por exemplo 0,32 em 5 a 9 anos contra 0,23 em 2015-2019), mas são poucos óbitos por faixa; ler com cautela.

## O que a literatura já tinha (busca inicial, não sistemática)

Foram feitas sete buscas em inglês e português. O objetivo era saber o que já existe, e não afirmar ineditismo.

Estimar mortalidade por idade e sexo em pequenas áreas do Brasil, incluindo os 5.565 municípios, e lidar com ruído e sub-registro, já foi feito: Gonzaga e colegas (2024, Population Health Metrics) estimam taxas por idade e sexo para os municípios e projetam até 2030; Schmertmann e Gonzaga (2018, Demography) usam um modelo bayesiano com priors de cobertura de registro de óbitos e concluem que, na comparação entre áreas pequenas, o ruído muitas vezes domina o sinal, exatamente o problema que o τ aqui tenta separar. A mortalidade adulta em áreas pequenas do Brasil foi estudada por Lima e colegas (2020, Genus; e Demographic Research, vol. 51, art. 44).

A decomposição por idade e causa das diferenças regionais já foi aplicada ao Brasil: Calazans, Guimarães e Nepomuceno (2023, Revista Brasileira de Estudos de População), para as grandes regiões entre 2008 e 2018; Laurenti (2013, Cadernos de Saúde Pública) para estados. O método de Arriaga (1984) é padrão.

O padrão por idade e sexo encontrado aqui tem antecedentes: um estudo de províncias italianas (2002-2019, extensão espacial do modelo Lee-Carter) encontra que as diferenças geográficas se ampliam entre os homens na idade adulta jovem e nas mulheres em idades mais altas; um estudo das regiões da China (2007) mostra que os contrastes espaciais são maiores nas idades jovens e que idade e área não são independentes; um estudo da Alemanha usa decomposição por idade para a convergência entre estados.

Então a conclusão honesta é que os ingredientes existem na literatura (estimação em pequenas áreas, decomposição por idade, padrões por sexo). Nesta busca curta não apareceu um trabalho que combine, para microrregiões brasileiras e só com dados públicos do SIM e do POPSVS, um desvio-padrão entre territórios por idade e sexo com o acaso descontado, testes formais de hipóteses sobre o padrão por idade e uma medida como a IMD. Mas isso não é evidência de ineditismo, porque a busca foi curta e não sistemática. Antes de afirmar qualquer novidade em artigo, é preciso uma busca sistemática (PubMed, SciELO, Scopus ou Web of Science, e Google Acadêmico) com os termos: mortalidade por idade, desigualdade territorial ou regional, áreas pequenas, microrregiões, decomposição de Arriaga, heterogeneidade entre áreas, Brasil, e a leitura dos textos completos dos trabalhos acima. A contribuição defensável por enquanto é a descrição e os testes aplicados a uma base pública reproduzível, e não a invenção do método.

Referências (para consulta):
- Gonzaga MR, Queiroz BL, Freire FHMA e outros. Estimation and probabilistic projection of age- and sex-specific mortality rates across Brazilian municipalities between 2010 and 2030. Population Health Metrics 2024; 22:9. https://doi.org/10.1186/s12963-024-00329-x
- Schmertmann CP, Gonzaga MR. Bayesian estimation of age-specific mortality and life expectancy for small areas with defective vital records. Demography 2018. https://link.springer.com/doi/10.1007/s13524-018-0695-2
- Lima E, Queiroz BL, Freire F, Gonzaga M. Temporal and spatial trends of adult mortality in small areas of Brazil, 1980-2010. Genus 2020; 76:36. https://doi.org/10.1186/s41118-020-00105-3
- Lima E, Queiroz BL, Freire F, Gonzaga M. Analyzing regional patterns of mortality data quality and adult mortality for small areas in Brazil, 1980-2010. Demographic Research, vol. 51, art. 44. https://demographic-research.org/volumes/vol51/44/51-44.pdf
- Calazans JA, Guimarães R, Nepomuceno MR. Diferenciais regionais da mortalidade no Brasil: contribuição dos grupos etários e de causas de óbito (2008-2018). Revista Brasileira de Estudos de População 2023. https://rebep.org.br/revista/article/download/2210/1228
- Laurenti R. Decomposição da diferença da expectativa de vida de Minas Gerais em relação ao Rio de Janeiro e São Paulo. Cadernos de Saúde Pública 2013; 29(6):1131-1140. https://scielosp.org/pdf/csp/2013.v29n6/1131-1140/pt
- Geographical inequalities in mortality by age and gender in Italy, 2002-2019: insights from a spatial extension of the Lee-Carter model. arXiv:2510.06210. https://arxiv.org/abs/2510.06210
- A model for spatial variations in life expectancy; mortality in Chinese regions in 2000. International Journal of Health Geographics 2007; 6:16. https://pmc.ncbi.nlm.nih.gov/articles/PMC1876206
- Declining regional disparities in mortality in the context of persisting large inequalities in economic conditions: the case of Germany. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7266541/
- Arriaga EE. Measuring and explaining the change in life expectancies. Demography 1984; 21(1):83-96.

## O que ainda falta

Uma busca de literatura sistemática (acima). Decidir se a microrregião do IBGE é o agrupamento final, ou se se prefere região de saúde ou outro critério declarado antes da análise; a comparação com a UF mostra que a escolha importa. Refazer a análise por município só se o brasil_expectativa.py passar a gravar as taxas por idade por município. E, se a análise for para artigo, definir como tratar o sub-registro, por exemplo com estimativas públicas de cobertura do registro de óbitos como no trabalho de Schmertmann e Gonzaga.

## Arquivos desta etapa

Scripts: validacao_tau.py, comparacao_sexos.py, pandemia_tau.py, figuras_esboco.py, tabela_municipio_microrregiao.py, imd_sem_ruido.py (prova de que a IMD não é a idade de início; grava IMD_SEM_RUIDO.csv), divergencia_modelo.py, divergencia_territorial.py, testes_hipoteses.py, idt_experimento.py, imd_alternativa.py, sensibilidade_faixas.py. Resultados: DIVERGENCIA_POR_IDADE.csv, DIVERGENCIA_ESTABILIDADE.csv, DIVERGENCIA_SENSIBILIDADE.csv, TESTES_HIPOTESES.csv, TESTES_HIPOTESES_TAU_FAIXAS.csv, TESTES_H1_PARTICIPACAO_E0_80.csv, TESTES_HIPOTESES_HOLM.csv, SENSIBILIDADE_FAIXAS.csv, IDT_POR_MICRORREGIAO.csv, IDT_AVALIACAO.csv, IMD_POR_MICRORREGIAO.csv, IMD_AVALIACAO.csv. Os resultados anteriores não foram alterados. Todos os sorteios usam a semente fixa 20261124 e dão o mesmo resultado a cada execução. Tempos aproximados: divergencia_territorial.py cerca de 1 minuto, testes_hipoteses.py cerca de 10 minutos, idt_experimento.py cerca de 15 segundos, imd_alternativa.py cerca de 40 segundos.
