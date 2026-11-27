# Os dados do EXPVIDA permitem a H10?

Projeto EXPVIDA (`C:\EXPVIDA`). A H10 pergunta quais grupos de causas de morte explicam as diferenças de sobrevivência entre territórios. Este documento só verifica se os dados permitem essa análise. A decomposição em si não foi executada. O método (contrafactual, Shapley ou outro) será definido pelo ChatGPT e aprovado pelo Vladimir.

## Resposta curta

Sim, nas 558 microrregiões, por sexo, em 18 faixas de idade e 6 períodos, para 17 grandes grupos de causas. Os óbitos por causa somam exatamente o total usado nas tábuas de vida, então dá para montar tábuas por microrregião, sexo e idade com a mortalidade repartida por causa. Há quatro limitações que precisam ser resolvidas ou declaradas antes: a COVID está dentro de "infecciosas", a motocicleta não está separada no arquivo de idades de 5 anos, os grupos violentos têm muitas células pequenas e a idade 0 usa população estimada.

## As dez perguntas

**1. Quais grupos de causas existem?** Há dois arquivos. Por microrregião e idade de 5 anos (`CAUSAS_OBITOS_2015_2019.csv` e `CAUSAS_OBITOS_OUTROS_PERIODOS.csv`) existem 17 grupos: agressões, intervenção legal, suicídio, transporte, intenção indeterminada, acidentes outros, externas outras, infecciosas, neoplasias, circulatórias, respiratórias, endócrinas e nutricionais, digestivas, perinatais, congênitas, mal definidas e outras doenças. Por município e 7 faixas largas (`CAUSAS_MUNICIPIO.csv`, só no notebook por ter 184 MB) existem 39 causas detalhadas, entre elas motocicleta, pedestre, automóvel, arma de fogo, isquêmicas, cerebrovasculares, hipertensivas, diabetes, demências, pneumonia e câncer.

**2. Quais códigos podem ser agrupados com consistência?** Todos vêm da causa básica (`CAUSABAS`) em CID-10, de 2000 a 2024, sem troca de classificação no período. Os grupos são mutuamente exclusivos e cobrem todos os óbitos (o grupo "sem_causa" ficou vazio). Os sete grupos propostos para a H10 podem ser montados assim: homicídios = agressões + intervenção legal; motociclistas = V20–V29 (só no arquivo municipal); outras causas externas = transporte sem moto + suicídio + acidentes + externas outras + indeterminadas; cardiovasculares = circulatórias (I00–I99); câncer = neoplasias (C00–D48); mal definidas = R00–R99; demais causas = o restante. Recomendo manter as mortes de intenção indeterminada como grupo separado, e não dentro de "outras externas", por causa do problema descoberto em São Paulo e Minas (`RESULTADOS_BLINDAGEM.md`).

**3. Quais faixas etárias têm dados suficientes?** Para circulatórias, neoplasias e respiratórias, praticamente nenhuma combinação de microrregião, sexo e período tem menos de 10 óbitos. Para agressões, 22% das combinações têm menos de 10 óbitos (somando todas as idades). Para suicídio são 31%, para intenção indeterminada 51% e para intervenção legal 96%. Por idade de 5 anos, as células ficam muito menores. A decomposição por grupo violento vai precisar de faixas largas (por exemplo 15–29 e 30–59), de suavização ou de modelagem, e não de taxas brutas célula a célula.

**4. Quais períodos podem ser comparados?** Os seis períodos (2000–2004, 2005–2009, 2010–2014, 2015–2019, 2020–2021 e 2022–2024) têm a mesma estrutura. A comparação de 2020–2021 só é limpa se a COVID for separada (pergunta 8).

**5. Dá para montar tábuas de vida por território, sexo, idade e causa?** Sim. `BRASIL_taxas_por_idade.csv` traz óbitos e pessoas-ano por microrregião, sexo, 18 faixas e período. O teste desta auditoria mostrou que a soma dos óbitos por causa é igual ao total desse arquivo em todas as células de 2005 a 2024. Em 2000–2004 há uma diferença de 37 óbitos em 14 células, sem efeito prático. A tábua já existe em `divergencia_modelo.py` (`tabua_lx`, `tabua_vec`, `e0_80`) e a decomposição de Arriaga por idade também (`arriaga_e0_80`, `arriaga_vec`). Falta só repartir cada faixa por causa.

**6. Quais denominadores existem?** As pessoas-ano do POPSVS por município, sexo e idade, para cada período (`POP_MUNICIPIO.csv` em 7 faixas e `BRASIL_taxas_por_idade.csv` em 18 faixas). Não há nascidos vivos (SINASC).

**7. Qual é a cobertura territorial?** São 558 microrregiões reais em todos os arquivos. Os óbitos com município ignorado (códigos terminados em `000`) ficam fora, e são poucos: de 4.260 óbitos com idade ignorada em 2000 a 1.546 em 2024, e de 953 com sexo ignorado a 511.

**8. Quais grupos têm problema de classificação?** Há quatro. A COVID está somada em "infecciosas" (o SIM grava B34.2 e o script procurava U07), e separar exige ler de novo o SIM. As mortes de intenção indeterminada cresceram muito no Sudeste e passaram dos homicídios em São Paulo em 2022–2024. As mal definidas caem muito ao longo do tempo (cerca de 132 mil por ano em 2000–2004 e 74 mil em 2022–2024) e variam entre territórios, o que mistura melhora real da informação com mudança de mortalidade. E a variável "transporte" inclui também acidentes aquáticos e aéreos (V90–V99), o que deve ser declarado.

**9. O que impediria uma decomposição contrafactual?** Nada impede tecnicamente, mas há quatro cuidados. O ruído de Poisson nos grupos raros pode inflar a "contribuição" de causas violentas em microrregiões pequenas, se não houver modelagem. Os grupos de má qualidade (mal definidas e indeterminadas) podem ser artefatos: uma parte da "contribuição" deles é na verdade outra causa mal registrada. A faixa aberta 80+ só permite a e0-80 (anos vividos até os 80), não a e0 completa. E a mistura da COVID com infecciosas distorce 2020–2021.

**10. Quais scripts podem ser reaproveitados?** `divergencia_modelo.py` (tábua, e0-80, Arriaga e o modelo de τ), `arriaga_territorial.py` (já faz Arriaga por idade de cada microrregião contra o Brasil, só sem causa), `causas_tau.py` e `causas_temporal.py` (já leem os dois arquivos de causas e juntam os períodos) e `validacao_tau.py` (bootstrap por blocos de UF para os intervalos).

## O que falta preparar antes da H10

Na ordem: separar a COVID (B34.2) e, se possível, guardar a causa com 4 caracteres, o que exige baixar o SIM de novo; gerar o arquivo de causas por microrregião e idade de 5 anos com a motocicleta separada, aproveitando a mesma leitura; e decidir com o ChatGPT o tratamento das mal definidas e das indeterminadas (manter como grupo próprio, redistribuir ou fazer os dois como sensibilidade). Nenhuma dessas etapas precisa do SINASC, que só é necessário para a idade 0.

A H10 não deve confundir a participação de uma causa no total de óbitos com a contribuição dela para a diferença de sobrevivência. Exemplo: as circulatórias são o maior grupo de óbitos, mas podem explicar pouca diferença entre territórios se a taxa delas for parecida em todo lugar.
