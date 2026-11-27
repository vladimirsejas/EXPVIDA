# H10 — especificação metodológica para decisão
**EXPVIDA — documento de trabalho, não é protocolo aprovado**  
**Data:** 27/11/2026  
**Branch:** `auditoria-chatgpt-2026-11-27`

## 1. Por que H10 precisa ser reformulada

A pergunta genérica “quais causas explicam diferenças territoriais de expectativa de vida?” já tem precedentes próximos e diretos. A revisão exploratória identificou:
- Calazans, Guimarães e Nepomuceno (2023), sobre contribuições de idade e causas para variação da esperança de vida e dispersão da idade à morte entre regiões brasileiras, 2008–2018.
- Monteiro da Silva et al. (2026), sobre contribuições de idade e causas para o hiato urbano-rural de mortalidade adulta no Brasil, 2006–2023.
- Baptista, Queiroz e Pinheiro (2021), sobre distribuição regional de grupos de causas em pequenas áreas brasileiras, 1998–2017.
- Um precedente internacional especialmente próximo: “Rising geographic inequality in mortality in the United States” (2019) apresenta, no apêndice, decomposição da mudança na variância da expectativa de vida entre 40 unidades espaciais, substituindo sequencialmente taxas nacionais por taxas locais para grupos idade-causa.
- A literatura de decomposição da variância da longevidade também inclui a decomposição S-A-T (spread, allocation, timing), que separa mecanismos pelos quais causas de morte alteram a variabilidade da idade à morte.

Portanto, não se deve alegar que o EXPVIDA inventa a decomposição territorial por causas, a análise de pequenas áreas ou a decomposição da variância da expectativa de vida.

A oportunidade do EXPVIDA pode estar em uma combinação mais específica: série temporal longa (2000–2024), escala de microrregiões brasileiras, tábuas temporárias de sobrevivência até 80 anos, comparação por sexo/idade, modelagem da heterogeneidade residual Poisson-lognormal e uma decomposição de contribuição por causa que trate explicitamente a dependência da ordem de substituição.

## 2. Pergunta de pesquisa candidata

**Entre as microrregiões brasileiras, quais grupos de causas de morte mais contribuem para a desigualdade territorial da sobrevivência até os 80 anos, e como essas contribuições mudaram entre 2000 e 2024, separadamente para homens e mulheres?**

A pergunta é sobre a distribuição territorial de uma medida de sobrevivência, não sobre “o que causa” a morte de indivíduos. O estudo permanece ecológico e descritivo-contrafactual.

## 3. Estimando primário proposto

Para cada período, sexo e microrregião (i), calcular a expectativa temporária de vida entre 0 e 80 anos, (e_{0-80,i}), a partir de uma tábua de múltiplos decrementos coerente com os grupos de causas.

O desfecho primário de desigualdade territorial será:

[
V = \operatorname{Var}_{i}(e_{0-80,i})
]

com cada microrregião recebendo o mesmo peso na variância principal. Essa escolha responde à desigualdade entre unidades territoriais, não à desigualdade entre indivíduos brasileiros. Uma análise secundária ponderada pela população poderá responder a outra pergunta e não deve substituir silenciosamente o estimando principal.

A escolha por (e_{0-80}) evita que a faixa aberta 80+ e a instabilidade da mortalidade em idades muito avançadas dominem as comparações. Não resolve, porém, o problema do denominador da idade zero nem o sub-registro.

## 4. Decomposição contrafactual proposta: Shapley da variância territorial

### 4.1 Construção dos riscos por causa

Para cada microrregião, sexo, período, idade e grupo de causa (c), calcular:

[
m_{ixc}=D_{ixc}/PY_{ix}
]

em que (D) é o número de óbitos atribuídos à causa e (PY) são pessoas-ano. Os grupos devem ser mutuamente exclusivos e exaustivos: a soma dos óbitos classificados por causa precisa reproduzir o total de óbitos usado na tábua, dentro de tolerâncias documentadas.

As taxas específicas por causa devem ser combinadas como riscos competitivos na construção da tábua. A soma dos riscos causa-específicos deve reproduzir o risco total sob a convenção de taxas escolhida. A conversão entre taxa central de mortalidade e probabilidade de morte precisa ser consistente com a convenção de tábua adotada; não se deve simplesmente somar probabilidades de morte independentes.

### 4.2 Cenários contrafactuais

Para cada subconjunto (S) de grupos de causas, construir uma matriz contrafactual na qual:
- para causas em (S), cada microrregião recebe a taxa de referência nacional da mesma idade, sexo e período;
- para causas fora de (S), preserva sua própria taxa observada/suavizada;
- denominadores, faixa etária, período, sexo e conjunto territorial permanecem fixos.

Calcular (e_{0-80,i}(S)) em cada cenário e:

[
V(S)=\operatorname{Var}_{i}(e_{0-80,i}(S)).
]

Interpretação: (V(\varnothing)) é a variância territorial observada; (V(C)), com todas as causas substituídas pela referência nacional, é a variância residual que permanece depois dessa equalização contrafactual. A diferença (V(\varnothing)-V(C)) é a parcela da variância removida por esse conjunto de equalizações, não uma fração causal da desigualdade real.

### 4.3 Atribuição Shapley

Para cada causa (c), calcular a contribuição média marginal sobre todas as ordens possíveis de substituição:

[
\phi_c=\sum_{S\subseteq C\setminus\{c\}}
\frac{|S|!(K-|S|-1)!}{K!}
[V(S)-V(S\cup\{c\})].
]

Com essa convenção, contribuições positivas indicam que equalizar a causa tende a reduzir a variância; contribuições negativas indicam que a equalização tende a aumentá-la. A soma das contribuições Shapley é exatamente (V(\varnothing)-V(C)), por construção.

Isso resolve a dependência da ordem presente em substituições sequenciais simples. **Não transforma a decomposição em causal.** A atribuição depende dos grupos escolhidos, da referência nacional, da qualidade dos dados e do contrafactual de equalização.

### 4.4 Número de grupos e custo computacional

Com (K) grupos, a decomposição exata requer (2^K) cenários distintos de (V(S)), não necessariamente todas as (K!) permutações separadamente. Para 7–9 grupos, isso é computacionalmente plausível se a construção das tábuas for vetorizada. Se houver mais grupos, avaliar aproximação por amostragem de permutações, com erro Monte Carlo documentado.

## 5. Hipótese H10 candidata

**H10:** A contribuição dos grupos de causas para a variância territorial de (e_{0-80}) não é homogênea: causas externas e causas crônicas apresentam contribuições territoriais distintas, e a composição dessas contribuições varia entre homens e mulheres e ao longo do período 2000–2024.

Esta hipótese ainda é ampla. Antes de testá-la, é necessário definir:
- grupos de causas e classificação CID-10;
- se a pandemia 2020–2021 será analisada separadamente;
- quais períodos terão estimativas comparáveis;
- qual conjunto de microrregiões será mantido constante;
- qual será a hipótese primária e quais análises serão secundárias;
- qual será a regra para causas mal definidas e códigos residuais.

Não formular uma hipótese direcional específica para homicídios, transporte ou doenças crônicas sem análise exploratória documentada e justificativa prévia.

## 6. Como τ entra — e como não entra

O τ do modelo Poisson-lognormal mede a dispersão dos efeitos territoriais na escala log do risco, após o componente Poisson, para uma combinação de causa, sexo, idade e período. É um estimando distinto da variância de (e_{0-80}).

Regras:
1. Não somar τ causa-específicos.
2. Não dividir τ de uma causa pelo τ geral e chamar isso de “percentual explicado”.
3. Não interpretar correlação entre efeitos territoriais causa-específicos e efeito geral como decomposição.
4. Usar τ como análise paralela de heterogeneidade dos riscos causa-específicos, não como substituto da decomposição Shapley da variância de sobrevivência.
5. Se houver interesse em explicar a própria distribuição de τ, será necessário outro estimando e outro método; a decomposição acima não responde a essa pergunta.

## 7. Questões críticas antes da implementação

### 7.1 Sub-registro e qualidade do SIM
A cobertura varia por território, tempo, idade e causa. A equalização de taxas não corrige sub-registro. Apresentar análises de sensibilidade com e sem causas mal definidas, e cenários de cobertura apenas quando a fonte e a incerteza estiverem documentadas. O resultado deve ser descrito como condicionado à qualidade dos registros disponíveis.

### 7.2 Idade zero
A base usa população estimada como exposição na idade zero; para mortalidade infantil, nascidos vivos do SINASC seriam um denominador epidemiológico mais apropriado. A decomposição primária deve ser repetida como sensibilidade excluindo a idade zero ou usando uma especificação compatível com nascidos vivos, se houver cobertura e compatibilidade adequadas.

### 7.3 Causas mal definidas
Devem permanecer como grupo explícito no cenário principal, pois são parte do processo de registro e sua distribuição espacial afeta os resultados. Sensibilidade: excluir/reclassificar com regras justificadas. Não redistribuir proporcionalmente sem método validado.

### 7.4 COVID-19
Auditar B34.2, U07.1 e U07.2, incluindo campos de causa básica e associadas, conforme os arquivos e a codificação efetivamente usada. COVID não pode ficar parcialmente dentro de infecciosas e parcialmente fora sem documentação.

### 7.5 Microrregiões
Resolver a discrepância 558/586 e definir se a análise usará painel territorial constante ou universo variável. Para comparabilidade temporal, a opção preferível é um painel fixo de códigos válidos em todos os períodos, com exclusões justificadas e análise de sensibilidade.

### 7.6 Incerteza
A incerteza deve, idealmente, propagar óbitos, estimativas populacionais e cobertura do SIM. O bootstrap deve preservar dependência espacial e parear as mesmas unidades/sorteios entre cenários e períodos. Não basta reamostrar τ já calculado se o estimando contrafactual depende da construção das taxas e tábuas em cada réplica.

## 8. Plano mínimo de validação

1. Teste de fechamento: soma dos grupos de causas = total de óbitos, por microrregião, sexo, idade e período.
2. Teste de fechamento da tábua: riscos causa-específicos reproduzem o total all-cause dentro da tolerância definida.
3. Teste de Shapley: soma de φ_c = V(∅) − V(C), com erro numérico próximo de zero.
4. Teste de invariância: permutar a ordem de cálculo não altera os valores exatos de Shapley.
5. Teste de simulação: dados artificiais com uma causa territorialmente desigual conhecida devem recuperar contribuição predominante dessa causa.
6. Teste de sensibilidade: grupos mais agregados/desagregados, causas mal definidas, painel territorial, idade zero e pandemia.
7. Bootstrap por blocos de UF ou blocos espaciais, com reconstrução integral dos cenários contrafactuais dentro de cada réplica.

## 9. Critério de decisão: avançar ou abandonar H10

**Avançar** somente se:
- a classificação de causas for mutuamente exclusiva e exaustiva;
- as diferenças de cobertura e qualidade forem mensuráveis o bastante para análise de sensibilidade;
- a tábua por causas for matematicamente coerente;
- o método fechar numericamente;
- a contribuição Shapley acrescentar uma resposta distinta das decomposições publicadas.

**Reformular ou abandonar** se o resultado depender excessivamente de causas mal definidas/sub-registro, se a base por causas não fechar, se a unidade territorial não for comparável, ou se a contribuição proposta apenas reproduzir resultados já publicados sem ganho metodológico substantivo.

## 10. Literatura-base para a decisão

1. Calazans, Guimarães & Nepomuceno (2023), diferenciais regionais da mortalidade brasileira e contribuição de idade/causas à esperança de vida e dispersão da idade à morte. DOI: https://doi.org/10.20947/S0102-3098a0244.
2. Monteiro da Silva et al. (2026), hiato urbano-rural de mortalidade adulta no Brasil, com decomposição por idade e causa. DOI: https://doi.org/10.1007/s11524-026-01076-0.
3. Baptista, Queiroz & Pinheiro (2021), distribuição regional de causas de morte em pequenas áreas brasileiras. DOI: https://doi.org/10.3389/fpubh.2021.601980.
4. “Rising geographic inequality in mortality in the United States” (2019), que inclui decomposição da variância da expectativa de vida entre 40 unidades espaciais por grupos idade-causa: https://pmc.ncbi.nlm.nih.gov/articles/PMC6804490/.
5. “A New Method for Determining Why Length of Life is More Unequal in Some Populations Than in Others” (2012), decomposição S-A-T da variância da longevidade por spread, allocation e timing: https://pmc.ncbi.nlm.nih.gov/articles/PMC4104684/.
6. GBD 2021, decomposição da expectativa de vida por causa e idade em países e 811 unidades subnacionais: https://pmc.ncbi.nlm.nih.gov/articles/PMC11126520/.

## 11. Decisão recomendada nesta fase

Não executar H10 ainda. Primeiro Claude deve fechar a auditoria do universo territorial, dos grupos de causas, da discrepância entre bases e do bootstrap existente. Em paralelo, o EXPVIDA deve decidir se a contribuição científica central será:
- a decomposição Shapley da variância territorial de (e_{0-80}), ou
- a modelagem da evolução temporal de τ causa-específico.

As duas podem coexistir como análises complementares, mas não devem ser fundidas num único indicador ou numa narrativa de “percentual explicado”.
