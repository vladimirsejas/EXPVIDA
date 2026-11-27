# Auditoria independente do EXPVIDA — ChatGPT
**Data:** 27/11/2026  
**Branch:** `auditoria-chatgpt-2026-11-27`  
**Base inspecionada:** branch `main`, commit `3c753c08070003c4bfcfabe0dce848b78a0a02ae`.

> **ERRATA IMPORTANTE (27/11/2026):** A seção 3 abaixo comparou indevidamente o bootstrap temporal por causas com um adendo referente a uma análise de sensibilidade diferente. A conclusão de divergência necessária entre código e método foi corrigida. Consulte `AUDITORIA_COMPLEMENTAR_IMPLEMENTACAO_2026-11-27.md`, que distingue os procedimentos e registra o achado concreto sobre a classificação de COVID-19.

## 1. Escopo e limite desta auditoria

Esta é uma auditoria documental e estática feita a partir dos arquivos versionados no GitHub. Foram lidos documentos metodológicos, relatórios de resultados e trechos dos scripts centrais. **Não executei os programas, não abri os arquivos locais de `C:\EXPVIDA` e não validei os CSV linha a linha em ambiente local.** Portanto, os pontos abaixo são achados de leitura de código/documentação e precisam ser confrontados por execução independente quando indicado.

Nenhum arquivo da `main` foi alterado. Este relatório foi criado em branch separada.

## 2. Diagnóstico executivo

O EXPVIDA já tem uma base de trabalho substancial: SIM/DATASUS e POPSVS, tábuas de vida, estimativas por sexo e território, modelo Poisson-lognormal para heterogeneidade territorial por idade, bootstrap espacial, análises de sensibilidade, estudos municipais e análises por causas.

O principal problema neste momento não é falta de resultados. É **garantir que cada resultado publicado corresponda exatamente ao estimando, ao código e ao procedimento inferencial descritos**. Há uma questão metodológica concreta no bootstrap por blocos dos scripts de causas que merece prioridade antes de qualquer conclusão temporal baseada nesses intervalos.

Também é necessário separar claramente três frentes que hoje aparecem próximas no repositório:
1. Estudo principal: desigualdade territorial de sobrevivência por idade e sexo.
2. Estudos complementares: causas de morte, violência e resultados municipais.
3. Nova pergunta explicativa: contribuição de grupos de causas para diferenças de sobrevivência entre territórios (H10, ainda a formalizar).

## 3. Achado prioritário: bootstrap por blocos nas análises de causas

### Evidência no código

Em `divergencia_modelo.py`, a função `esperados(D, PY, colunas)` calcula, para cada microrregião, os óbitos esperados usando a taxa do restante do Brasil, excluindo a própria microrregião (leave-one-out):

```python
taxa_ref = (d.sum(0, keepdims=True) - d) / (p.sum(0, keepdims=True) - p)
return d.sum(1), (p * taxa_ref).sum(1)
```

Em `causas_temporal.py` e `causas_temporal_3059.py`, as matrizes `OE` são calculadas uma vez antes do bootstrap. Em seguida, os scripts chamam `vt._rep_bloco`. Essa função, em `validacao_tau.py`, ajusta o modelo usando:

```python
a = dm.ajustar(O[sel], E[sel], ...)
```

Ou seja, a reamostragem seleciona as linhas observadas e os valores esperados já calculados; **não recalcula explicitamente a taxa de referência leave-one-out a cada replicação**.

### Por que isso importa

A documentação do adendo `ADENDO_ANALISE_FINAL_BOOTSTRAP_EXPVIDA.md` afirma que a referência leave-one-out foi recalculada dentro de cada replicação. O trecho de implementação compartilhado por `causas_temporal.py`/ `causas_temporal_3059.py` não demonstra esse recálculo. Há, portanto, uma divergência entre o procedimento descrito e o procedimento que o código aparenta executar.

Isso não prova, por si só, que os valores de τ estejam errados. Significa que os intervalos de bootstrap e as diferenças entre períodos precisam ser reavaliados com uma implementação que deixe explícito como os denominadores e as taxas de referência são recalculados sob a amostra de microrregiões reamostrada.

### Ação recomendada

Claude deve verificar localmente qual versão de `validacao_tau.py` foi realmente usada para gerar cada CSV e se existe outra implementação de bootstrap. Depois, comparar o código executado com os arquivos versionados. Se o procedimento for o mesmo, produzir uma versão de bootstrap em que cada réplica:
1. reamostre as UFs como blocos;
2. reconstrua as matrizes de óbitos e pessoas-ano da amostra;
3. recalcule as taxas de referência leave-one-out para a réplica;
4. ajuste o modelo e guarde τ;
5. registre falhas e tamanho efetivo da amostra.

Não reutilizar os intervalos antigos como se fossem os novos. Manter os resultados antigos e produzir arquivos com nomes/versionamento distintos.

## 4. Interpretação de τ: cuidado conceitual confirmado

O próprio código e a documentação definem τ como o desvio-padrão dos efeitos territoriais sistemáticos na escala log, após separar a variação Poisson, sob um modelo Poisson-lognormal.

A medida é estimada para um conjunto de causas/idade/sexo, mas **τ não é aditivo por causa**. A análise por causa pode comparar heterogeneidades e correlações dos efeitos territoriais; não pode afirmar que a soma dos τ por causa explica o τ da mortalidade geral.

Consequência para H10: não usar uma soma ou subtração simples de τ causa-específico como “percentual explicado” da desigualdade de sobrevivência. H10 precisa de outro estimando, preferencialmente uma decomposição contrafactual da diferença de expectativa de vida/sobrevivência entre dois grupos territoriais, substituindo padrões de mortalidade por grupos de causas e tratando a ordem de substituição. Uma decomposição Shapley pode ser avaliada para repartir a diferença contrafactual entre grupos de causas, desde que o estimando e os cenários sejam definidos antes da execução.

## 5. Distinção necessária entre as medidas já existentes

- `e0`: expectativa de vida ao nascer da tábua de vida.
- `e0-80`: expectativa temporária de vida entre 0 e 80 anos, adotada como medida mais estável em áreas pequenas.
- `q15-60`: probabilidade de morrer entre 15 e 60 anos.
- `τ`: heterogeneidade territorial residual entre microrregiões na escala log de risco, por idade/sexo/período.
- `IMD`: idade em que o acumulado da contribuição de Arriaga alcança metade da diferença total em anos de vida; não é a idade de início da divergência.
- `IDT`: regra operacional para detectar a idade de início de uma sequência de diferenças de risco.

Essas medidas respondem a perguntas diferentes. Não intercambiar os termos “desigualdade de sobrevivência”, “heterogeneidade de mortalidade”, “idade de início” e “idade em que metade da diferença se acumulou”.

## 6. Pontos documentais e de dados que precisam de fechamento

### 6.1 Universo territorial: 558 versus 586

O LEIAME e os scripts centrais usam 558 microrregiões disponíveis na base analítica, enquanto outros registros/relatórios mencionam 586 microrregiões do CADMUN/IBGE. O relatório técnico também descreve 558 unidades em alguns testes. A diferença pode decorrer de ausência de unidades sem população/óbitos, códigos inválidos, exclusões ou versões distintas da divisão territorial. Não escolher uma explicação sem conferência.

**Solicitação a Claude:** produzir tabela de reconciliação com: total no CADMUN, total no CSV de população/taxas, total efetivamente modelado, códigos ausentes em cada lado, UFs correspondentes e motivo documentado de cada exclusão.

### 6.2 Idade zero

Os documentos reconhecem que o denominador de idade zero é população estimada, não nascidos vivos. Portanto, as conclusões da faixa 0 e a hipótese H1 precisam ser apresentadas com essa limitação. Para uma análise infantil mais apropriada, avaliar SINASC/nascidos vivos e compatibilidade territorial/temporal, sem misturar denominadores diferentes sem explicação.

### 6.3 Sub-registro e qualidade do SIM

O τ pode incorporar heterogeneidade de cobertura e de qualidade do registro, além da variação real da mortalidade. A queda de τ entre períodos não pode ser interpretada automaticamente como convergência real. Os cenários determinísticos de cobertura descritos no adendo são análises condicionais; não propagam a incerteza das estimativas de cobertura e aplicam valores estaduais uniformemente às microrregiões.

### 6.4 COVID-19

A documentação de resultados municipais informa que B34.2 foi tratado dentro de infecciosas e reconhece a necessidade de verificar os códigos U07.1/U07.2 e campos da declaração. A classificação final deve ser auditada no script de extração e no dicionário de causas, não corrigida apenas no texto.

### 6.5 Mortalidade infantil e denominador

A tábua geral usa população de idade zero. Para mortalidade infantil, o denominador epidemiológico usual é nascidos vivos. Não interpretar q0 ou τ da faixa 0 como equivalente direto a uma taxa infantil calculada com SINASC.

### 6.6 Taxas municipais e suavização

O relatório municipal descreve uma razão observado/esperado com suavização Bayes empírica. Isso não deve ser chamado simplesmente de taxa diretamente padronizada. O artigo precisa descrever com precisão o estimador, o padrão de referência e a unidade de exposição.

## 7. Achados sobre a organização científica

O LEIAME atualizado em 24/11 registra como pendências a busca sistemática de literatura, os testes formais das hipóteses e a decisão sobre a unidade territorial. Outros documentos posteriores já relatam testes de H1–H3 e uma busca inicial de literatura. A documentação deve ser consolidada para não manter checklists desatualizados.

A revisão técnica faz uma correção importante: H1 tem evidência parcial; H2 é sustentada pelos testes apresentados; H3 é significativa para a diferença entre perfis, mas a interpretação do pico feminino deve permanecer qualificada. A afirmação genérica de que “as três hipóteses foram confirmadas” não é defensável.

A busca bibliográfica descrita é explicitamente inicial/não sistemática. Não afirmar ineditismo. A contribuição do trabalho deve ser formulada em termos de aplicação, operacionalização, comparação territorial/etária e reprodutibilidade até que uma busca sistemática seja concluída.

## 8. Proposta de formalização de H10 — ainda sem executar

**Pergunta candidata:** quanto da diferença de sobrevivência/expectativa de vida entre grupos de territórios pode ser atribuído, em sentido contrafactual, aos diferentes padrões de mortalidade por grandes grupos de causas?

Antes de programar, fixar:
1. Qual é o contraste territorial: quantis de e0-80, grupos de τ, regiões ou outro contraste definido a priori?
2. Qual é o desfecho: diferença de e0, e0-80, q15-60 ou sobrevivência até uma idade específica?
3. Qual é a população-alvo: homens, mulheres ou análises separadas?
4. Quais períodos serão comparados, evitando misturar pandemia com períodos ordinários?
5. Quais grupos de causas são mutuamente exclusivos e exaustivos, incluindo mal definidas e códigos residuais?
6. Como tratar diferenças de cobertura/qualidade do SIM e incerteza dos denominadores?
7. Qual é o contrafactual: substituir as taxas por causa do grupo A pelas do grupo B, mantendo as demais causas e a estrutura de exposição coerentes?
8. Como repartir interações/ordem de substituição: avaliar Shapley sobre todas as ordens ou um desenho contrafactual alternativo.

**Regra:** não iniciar a execução de H10 até que o contraste, os grupos de causas, o contrafactual e a incerteza estejam aprovados.

## 9. Plano de trabalho dividido

### ChatGPT — GitHub, método e revisão independente
- Manter esta auditoria e atualizar achados com base em código/relatórios versionados.
- Revisar scripts e documentação, apontando divergências entre método descrito e implementado.
- Formalizar H10 e desenhar a estratégia de literatura.
- Revisar resultados que Claude devolver, sem alegar execução local.
- Preparar texto científico e limitações depois da validação.

### Claude — ambiente local e dados
- Confirmar versão exata dos scripts executados e correspondência com o GitHub.
- Reconciliar 558/586.
- Verificar a divergência de bootstrap destacada na seção 3.
- Conferir extração/classificação de causas, COVID, idade zero e cobertura.
- Entregar tabelas de conferência e logs reprodutíveis.

## 10. Arquivos/artefatos que devem ser preservados

Não sobrescrever resultados existentes. Novas execuções devem gerar arquivos com sufixo/versionamento próprio, registrar commit de origem, parâmetros, semente, número de replicações, tempo, falhas e versão dos scripts. Não apagar CSVs ou bases intermediárias até que a reconciliação seja concluída.

---
**Conclusão desta etapa:** o projeto tem material analítico relevante, mas o ponto de maior prioridade é conferir a implementação do bootstrap por blocos nas análises de causas, porque o código visível não corresponde claramente à descrição de recálculo leave-one-out por réplica. A auditoria é preliminar e documental; depende da conferência local de Claude antes de qualquer correção ou conclusão nova.
