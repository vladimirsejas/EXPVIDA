# Quando o território importa: heterogeneidade territorial da mortalidade por idade e sexo no Brasil, 2000–2024
## Manuscrito de trabalho — versão 0.1, 27/11/2026

**Autores:** a definir  
**Afiliação:** a definir  
**Tipo de artigo:** pesquisa original, estudo ecológico de pequenas áreas  
**Status:** rascunho científico baseado nos resultados documentados no repositório. Não submeter antes da auditoria local, da revisão bibliográfica sistemática e da checagem final dos arquivos de análise.

---

## Resumo

**Objetivo:** Investigar como a heterogeneidade territorial da mortalidade varia com a idade e difere entre homens e mulheres nas microrregiões brasileiras, entre 2000 e 2024, com atenção às mudanças observadas durante e após a pandemia de COVID-19.

**Métodos:** Foram utilizados registros de óbitos do Sistema de Informações sobre Mortalidade (SIM/DATASUS) e estimativas populacionais por sexo e idade (POPSVS), agregados em 558 microrregiões. Os períodos analisados foram 2000–2004, 2005–2009, 2010–2014, 2015–2019, 2020–2021 e 2022–2024. Para cada sexo, idade e período, estimou-se um modelo Poisson-lognormal em que os óbitos observados são condicionados aos óbitos esperados pela taxa do restante do Brasil, excluída a própria microrregião. A heterogeneidade territorial foi quantificada pelo desvio-padrão dos efeitos aleatórios na escala logarítmica (τ). A dependência espacial foi considerada na inferência por bootstrap em blocos de unidades da Federação. A expectativa temporária de vida entre 0 e 80 anos (e0-80) foi utilizada em análises complementares.

**Resultados:** Em 2015–2019, a heterogeneidade territorial foi maior entre homens de 15–29 anos (τ=0,34; IC95% 0,32–0,36) do que entre mulheres da mesma idade (τ=0,15; IC95% 0,14–0,16). Entre os homens, a razão entre τ de 15–29 anos e 30–59 anos foi 2,46 (IC95% por blocos 1,83–3,06), mantendo-se acima de 1 nos seis períodos. A razão entre 15–29 e 1–14 anos foi 1,49 (1,20–1,84) em 2015–2019, mas não foi estatisticamente distinguível de 1 durante a pandemia e ficou no limite em 2022–2024. Os perfis etários de heterogeneidade diferiram entre os sexos nos seis períodos. Na pandemia, a heterogeneidade aumentou em várias faixas entre as mulheres e na infância entre os homens; em 2022–2024, retornou ao patamar anterior ou ficou abaixo dele em diversas idades.

**Conclusão:** A desigualdade territorial da mortalidade no Brasil não é uniforme ao longo do curso de vida nem entre os sexos. A concentração da heterogeneidade entre homens jovens é consistente, sobretudo em comparação com homens de 30–59 anos. Entretanto, τ também incorpora diferenças persistentes de cobertura e qualidade do registro e de denominadores; os resultados não devem ser interpretados como diferenças exclusivamente biológicas ou como efeitos causais de causas específicas.

**Palavras-chave:** mortalidade; desigualdades territoriais; pequenas áreas; diferenças por sexo; modelo Poisson-lognormal; Brasil.

---

## 1. Introdução

A mortalidade não se distribui de maneira homogênea no território. Diferenças regionais na estrutura etária, nas condições de vida, na exposição a riscos, na oferta de serviços e na qualidade dos sistemas de informação podem produzir padrões distintos de sobrevivência. No Brasil, a desigualdade regional da mortalidade e suas mudanças ao longo do tempo foram descritas em diferentes escalas, incluindo grandes regiões e unidades subnacionais.

Uma questão menos simples é identificar em que idades as diferenças territoriais se tornam mais pronunciadas e se esse padrão é semelhante entre homens e mulheres. Comparações de taxas observadas podem confundir heterogeneidade persistente com flutuação aleatória, especialmente em faixas etárias e territórios com poucos óbitos. Além disso, a dependência espacial entre áreas vizinhas torna inadequado tratar todas as unidades territoriais como observações independentes na inferência.

Este estudo utiliza um modelo Poisson-lognormal para separar, sob hipóteses explícitas, a variação esperada pelo processo de contagem da heterogeneidade residual entre microrregiões. O parâmetro central, τ, representa o desvio-padrão dos efeitos territoriais na escala logarítmica. A medida não distingue mortalidade real de erros sistemáticos de registro ou de denominadores; representa, portanto, heterogeneidade territorial residual na mortalidade registrada.

O objetivo é descrever a evolução de τ por idade, sexo e período, com ênfase na idade adulta jovem, e avaliar se os perfis etários diferem entre homens e mulheres. A pandemia é tratada como período separado, evitando incorporá-la a uma janela ordinária de referência.

As hipóteses examinadas são:
- **H1:** parte da heterogeneidade territorial já está presente no primeiro ano de vida.
- **H2:** entre os homens, a heterogeneidade territorial é maior entre 15 e 29 anos do que nas faixas de 1–14 e 30–59 anos.
- **H3:** o perfil etário da heterogeneidade territorial difere entre homens e mulheres.

As hipóteses são avaliadas como afirmações descritivas e estatísticas sobre microrregiões, não como relações causais individuais.

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

### 2.6 Testes das hipóteses

As hipóteses foram avaliadas em seis faixas agrupadas: 0; 1–14; 15–29; 30–59; 60–79; 80 anos ou mais.

- **H1:** magnitude de τ na faixa zero e participação dessa faixa na variância territorial de e0-80, por decomposição de Arriaga. A interpretação é parcial porque o denominador de idade zero é população estimada e o registro de óbitos infantis pode variar territorialmente.
- **H2:** razões τ(15–29)/τ(1–14) e τ(15–29)/τ(30–59) entre homens, com intervalos do bootstrap pareado por blocos.
- **H3:** teste de Wald dos contrastes entre os perfis de log(τ) de homens e mulheres, com covariância estimada pelo bootstrap. A probabilidade de cada faixa ser o pico do perfil foi avaliada nos sorteios.

### 2.7 Ética e proteção de dados

O estudo utiliza dados secundários públicos agregados. Nenhum registro individual é armazenado nos resultados analíticos versionados. As conclusões são ecológicas e não devem ser interpretadas como associações individuais.

## 3. Resultados

### 3.1 Padrão etário e diferenças por sexo

Em 2015–2019, a heterogeneidade territorial entre homens foi maior na faixa de 15–29 anos (τ=0,34; IC95% 0,32–0,36). Nas mulheres, o maior valor entre as faixas agrupadas ocorreu em 1–14 anos (τ=0,24; IC95% 0,20–0,27), enquanto τ em 15–29 anos foi 0,15 (0,14–0,16).

Nas 18 faixas etárias individuais, o pico masculino ocorreu entre 15–19 anos (τ=0,41; IC95% 0,39–0,44). Entre as mulheres, o pico ocorreu entre 1–4 anos (τ=0,31; IC95% 0,28–0,34). A forma do pico feminino deve ser interpretada com cautela devido à instabilidade em algumas faixas infantis e à qualidade desigual dos registros.

### 3.2 Heterogeneidade entre homens jovens

Em 2015–2019, a razão entre τ dos homens de 15–29 anos e de 1–14 anos foi 1,49 (IC95% por blocos 1,20–1,84). A razão entre 15–29 e 30–59 anos foi 2,46 (1,83–3,06). A segunda comparação permaneceu estatisticamente acima de 1 em todos os seis períodos.

A comparação entre 15–29 e 1–14 anos foi mais frágil: não foi estatisticamente distinguível de 1 durante a pandemia (1,13; IC95% 0,88–1,42) e ficou no limite em 2022–2024 (1,29; 0,99–1,66).

### 3.3 Diferenças dos perfis entre os sexos

O teste de Wald rejeitou a hipótese de perfis paralelos entre homens e mulheres nos seis períodos. A evidência de pico masculino em 15–29 anos foi mais consistente a partir de 2005–2009. A evidência de pico feminino em 1–14 anos foi consistente a partir de 2010–2014; nos períodos anteriores, a faixa de pico foi menos estável.

A diferença entre os sexos concentrou-se na idade adulta jovem: em 2015–2019, a diferença de τ entre homens e mulheres foi maior entre 15–19 anos (0,22; IC95% 0,15–0,27). Dos 15 aos 44 anos, os homens apresentaram maior heterogeneidade territorial; em idades posteriores, os valores foram mais próximos.

### 3.4 Mudanças durante e após a pandemia

Em 2020–2021, a heterogeneidade territorial aumentou entre as mulheres em várias faixas até 79 anos, aproximadamente 10% a 27%, e entre os homens na faixa de 1–14 anos, cerca de 25%. A diferença entre os sexos em 15–29 anos diminuiu durante a pandemia.

Em 2022–2024, a heterogeneidade retornou ao nível pré-pandêmico ou ficou abaixo dele em diversas faixas. Entre os homens, τ diminuiu em 15–29 anos (razão 0,90; IC95% 0,81–0,97) e em 60–79 anos (0,84; 0,79–0,89). Entre as mulheres, diminuiu em 60–79 anos (aproximadamente 0,88) e em 80 anos ou mais (aproximadamente 0,83).

Essas mudanças descrevem a heterogeneidade territorial da mortalidade registrada; não isolam o efeito causal da COVID-19, de alterações na cobertura do SIM ou de mudanças nos denominadores.

### 3.5 H1: primeiro ano de vida

Em 2015–2019, τ na faixa zero foi 0,201 nos homens (IC95% 0,184–0,216) e 0,186 nas mulheres (0,167–0,204). A contribuição do primeiro ano para a variância territorial de e0-80 foi 6,7% nos homens (5,2%–8,3%) e 14,1% nas mulheres (11,5%–16,8%).

Esses resultados indicam que a faixa zero participa da heterogeneidade observada, mas não demonstram desigualdade real de mortalidade infantil independente de erros de registro e de denominador. A hipótese permanece parcialmente sustentada.

## 4. Discussão

O principal resultado é a concentração da heterogeneidade territorial da mortalidade masculina na idade adulta jovem. Em 2015–2019, o τ dos homens de 15–29 anos foi mais que o dobro daquele observado entre 30–59 anos. A diferença foi consistente nos seis períodos, inclusive durante a pandemia. Isso indica que a desigualdade territorial da mortalidade não é uma característica constante ao longo do curso de vida.

O resultado não identifica, por si só, a causa dessa concentração. A idade adulta jovem masculina inclui causas externas relevantes, mas o modelo principal utiliza mortalidade por todas as causas. Atribuir o padrão a homicídios, acidentes ou suicídios exigiria análises causa-específicas adicionais, com classificação e qualidade dos registros verificadas.

A dependência espacial alterou substancialmente a incerteza. Os intervalos por blocos de UF foram de 1,7 a 2,6 vezes mais largos do que os intervalos anteriores baseados em microrregiões independentes. Essa diferença demonstra a importância de considerar a estrutura geográfica ao comparar pequenas áreas.

A pandemia produziu alterações diferentes por sexo e idade. O aumento da heterogeneidade em diversas faixas femininas e na infância masculina sugere que a distribuição territorial da mortalidade registrada se alterou de forma desigual. Contudo, τ agrega diferenças de mortalidade, registro e exposição populacional. Atribuir as mudanças à pandemia como mecanismo causal exige desenho e dados adicionais.

### 4.1 Relação com a literatura

Estudos anteriores já documentaram diferenciais regionais de mortalidade no Brasil e contribuições de idade e causas para diferenças na esperança de vida. Calazans, Guimarães e Nepomuceno (2023) examinaram diferenças regionais de esperança de vida e dispersão da idade à morte, incluindo contribuições por grupos de causas. Borges (2017) analisou a transição da saúde e a divergência/convergência regional da mortalidade.

A contribuição específica deste trabalho é a mensuração da heterogeneidade residual por idade e sexo em 558 microrregiões, com modelo Poisson-lognormal e inferência espacial por blocos. Essa contribuição deve ser apresentada como extensão de escala e de estimando, não como a primeira análise de desigualdade territorial ou de decomposição por causas no Brasil. A busca bibliográfica ainda precisa ser sistematizada.

### 4.2 Limitações

Primeiro, τ não separa heterogeneidade real da mortalidade de heterogeneidade de cobertura do SIM e de erros nos denominadores. O sub-registro foi mais intenso em períodos antigos e em áreas com menor qualidade de registro.

Segundo, a idade zero utiliza população estimada, não nascidos vivos. Assim, os resultados de H1 não equivalem a uma análise epidemiológica de mortalidade infantil baseada no SINASC.

Terceiro, a dependência espacial foi tratada por bootstrap em 27 blocos de UF. Embora mais adequado que reamostrar microrregiões isoladamente, esse número reduzido de conglomerados limita a precisão da inferência.

Quarto, a unidade territorial disponível é a microrregião. Os resultados não podem ser interpretados como desigualdades entre bairros, CEPs ou indivíduos.

Quinto, o modelo principal considera todas as causas em conjunto. Não identifica os mecanismos etiológicos ou sociais que produzem a heterogeneidade observada.

Sexto, a discrepância entre os 586 códigos de microrregião do CADMUN e as 558 unidades analíticas precisa ser documentada por código antes da versão final.

## 5. Conclusão

A heterogeneidade territorial da mortalidade no Brasil varia substancialmente por idade e sexo. Entre homens, a idade adulta jovem apresenta a maior heterogeneidade territorial, e a diferença em relação à faixa de 30–59 anos permanece nos seis períodos analisados. Os perfis de heterogeneidade também diferem entre os sexos, com mudanças importantes durante a pandemia.

A interpretação deve permanecer restrita à mortalidade registrada e à heterogeneidade residual estimada pelo modelo. A medida inclui diferenças de qualidade dos registros e dos denominadores, e não identifica causas específicas. O estudo oferece uma descrição comparável da dimensão etária e territorial da desigualdade, com inferência que considera a dependência espacial.

---

## Referências bibliográficas iniciais

1. Calazans, J. A., Guimarães, R. M., & Nepomuceno, M. R. (2023). Diferenciais regionais da mortalidade no Brasil: contribuição dos grupos etários e de causas de óbito sobre a variação da esperança de vida e da dispersão da idade à morte entre 2008 e 2018. *Revista Brasileira de Estudos de População*, 40. https://doi.org/10.20947/S0102-3098a0244
2. Borges, G. M. (2017). Health transition in Brazil: regional variations and divergence/convergence in mortality. *Cadernos de Saúde Pública*. https://doi.org/10.1590/0102-311X00080316
3. Lima, E. E. C., et al. (2024). Analyzing regional patterns of mortality data quality and adult mortality for small areas in Brazil, 1980–2010. *Demographic Research*, 51(44). https://doi.org/10.4054/DemRes.2024.51.44
4. Vierboom, Y. C., Preston, S. H., & Hendi, A. S. (2019). Rising geographic inequality in mortality in the United States. *SSM - Population Health*, 9, 100478. https://doi.org/10.1016/j.ssmph.2019.100478
5. Nau, C., & Firebaugh, G. (2012). A new method for determining why length of life is more unequal in some populations than in others. *Demography*, 49(4), 1207–1230. https://doi.org/10.1007/s13524-012-0133-9

## Pendências editoriais antes de submissão

- Conferir a reconciliação 558/586.
- Conferir e congelar os scripts e versões que geraram cada tabela.
- Atualizar a revisão bibliográfica com busca sistemática e leitura integral dos trabalhos mais próximos.
- Recalcular/confirmar todos os intervalos finais a partir da versão congelada do código.
- Decidir se a análise de causas será um segundo artigo ou uma análise secundária; não misturar τ causa-específico com decomposição de sobrevivência.
- Inserir autoria, afiliação, financiamento, contribuições, disponibilidade de dados/código e declaração ética conforme as regras do periódico escolhido.
