# Auditoria complementar de implementação — EXPVIDA
**27/11/2026 | Branch de auditoria ChatGPT**  
**Escopo:** leitura estática de scripts, resultados CSV versionados e documentação. Nenhuma execução local foi realizada.

## 1. Correção de uma afirmação da auditoria anterior

A primeira auditoria apontou divergência entre o bootstrap de `causas_temporal.py` e um adendo que descrevia recálculo leave-one-out em cada réplica. Essa comparação misturou procedimentos distintos.

A leitura conjunta dos arquivos mostra:
- `causas_temporal.py` e `causas_temporal_3059.py` calculam `O,E` antes das réplicas e reamostram pares fixos.
- `ADENDO_FINAL_FECHAMENTO_EXPVIDA.md` também declara explicitamente pares `O,E` fixos para o bootstrap da análise principal de sub-registro.
- `ADENDO_ANALISE_FINAL_BOOTSTRAP_EXPVIDA.md` descreve outro procedimento, com recálculo leave-one-out dentro das réplicas, referente à análise de sensibilidade sem causas mal definidas.

Portanto, não está demonstrado que `causas_temporal.py` contradiga o adendo do bootstrap principal. O bootstrap de pares fixos é uma escolha condicional: a incerteza dos valores esperados/referência nacional não é reestimada em cada réplica. Isso deve ser explicado como condicionamento do procedimento, não chamado automaticamente de erro de implementação.

**Errata:** a conclusão anterior de que o código de análise temporal por causas necessariamente diverge da descrição do bootstrap principal foi forte demais. O achado correto é que existem estratégias diferentes entre análises e que cada resultado precisa estar ligado ao seu script e ao seu estimando exatos.

## 2. Achado concreto: classificação de COVID-19 pela causa básica

### O que o script fazia

Em `causas_sim.py`, a função `grupo_causa` classificava códigos A00-B99 como `infecciosas`. A extração lia `CAUSABAS`, mas não consultava `LINHAA`, `LINHAB`, `LINHAC`, `LINHAD` ou `LINHAII`.

O inventário de campos do próprio repositório mostra que esses campos estão disponíveis no SIM ao longo de 2000–2024. Eles registram os códigos CID-10 informados nas linhas da Declaração de Óbito.

### Por que isso importa

A orientação do Ministério da Saúde descreve a codificação brasileira de COVID-19 como B34.2 combinado com o marcador U07.1 (vírus identificado) ou U07.2 (vírus não identificado/critério clínico-epidemiológico). B34.2 isolado é “infecção por coronavírus de localização não especificada”; não deve ser automaticamente interpretado como COVID-19.

Fontes oficiais:
- Ministério da Saúde, orientações de codificação das causas de morte relacionadas à COVID-19: https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/c/covid-19/publicacoes-tecnicas/recomendacoes/orientacoes-para-codificacao-das-causas-de-morte
- Quadro-síntese dos códigos de emergência: https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/c/covid-19/publicacoes-tecnicas/guias-e-planos/orientacoes-para-a-codificacao-dos-demais-codigos-de-emergencia-relacionados-a-covid-19.pdf

A afirmação em `RESULTADOS_MUNICIPIOS.md` de que B34.2 é “a COVID-19” simplifica excessivamente a codificação. A agregação atual pode misturar B34.2 com marcador COVID e B34.2 sem marcador. Como a análise usa apenas causa básica, também não deve contar COVID mencionada apenas como causa contribuinte na Parte II como causa básica.

### Alteração preparada nesta branch

Foi atualizada a cópia de trabalho de `causas_sim.py` para:
1. ler também LINHAA-D e LINHAII;
2. classificar como `covid19` apenas quando a causa básica é B34.2 e há marcador U07.1/U07.2 nas linhas da DO;
3. manter B34.2 sem marcador em `infecciosas`;
4. não trocar a causa básica por COVID quando U07 aparece apenas com outra causa básica;
5. usar diretório de cache versionado para evitar reutilizar agregações antigas sem marcador.

Também foi atualizada a cópia de trabalho de `causas_sim_periodos.py` para usar cache versionado, e criado `test_classificacao_causas.py` com nove testes unitários.

**Limite importante:** esses testes foram escritos, mas não executados neste ambiente. A extração completa dos arquivos SIM deve ser reexecutada localmente por Claude para gerar novas tabelas. Os CSV atuais e os resultados que deles dependem continuam sendo os resultados da classificação anterior até que a reextração seja validada.

## 3. Dependência de reprodutibilidade identificada

`causas_sim.py` exige `MUNICIPIO_MICRORREGIAO.csv`. Esse arquivo não está versionado na árvore atual do repositório, mas existe `tabela_municipio_microrregiao.py`, que o baixa do CADMUN e o gera localmente. A sequência reprodutível precisa estar explícita:
1. executar `tabela_municipio_microrregiao.py`;
2. conferir total de códigos de município, microrregiões e municípios ignorados;
3. executar `causas_sim.py` e `causas_sim_periodos.py`;
4. conferir fechamento por sexo, idade e período.

Não se trata de arquivo perdido se a etapa geradora for executada, mas a documentação de reprodução deve informar essa pré-condição.

## 4. Resultados causa-específicos: interpretação que precisa de contenção

A leitura de `CAUSAS_COMPARACAO.csv` mostra, para homens de 15–29 anos em 2015–2019:
- agressões: τ = 0,802; IC 95% 0,636–0,900;
- transporte: τ = 0,397; IC 95% 0,345–0,449;
- suicídio: τ = 0,416; IC 95% 0,352–0,476;
- intenção indeterminada: τ = 0,939; IC 95% 0,764–1,108; 80 microrregiões sem óbitos;
- intervenção legal: τ = 1,714; IC 95% 1,392–1,937; 344 microrregiões sem óbitos;
- todas as causas: τ = 0,343; IC 95% 0,275–0,383.

Isso não autoriza dizer que a intervenção legal é “a causa mais desigual” no mesmo sentido das demais: 344 de 558 microrregiões não têm óbitos nesse grupo, e a estimativa é dominada por uma distribuição extremamente esparsa. Deve ser descrita como padrão de registro extremamente concentrado, com forte ressalva de baixa ocorrência/zero estrutural. A intenção indeterminada também tem 80 microrregiões sem óbitos.

Além disso, `τ` causa-específico não é uma contribuição aditiva para o τ geral. Os próprios scripts documentam essa limitação. Razões e diferenças de τ podem ser apresentadas como comparações de heterogeneidade, não como percentuais explicados.

## 5. O que a análise temporal efetivamente cobre

`causas_temporal.py` estima homens de 15–29 e 15–19 anos; `causas_temporal_3059.py` estima homens de 30–59. Não são análises temporais completas por sexo e faixa etária para todas as causas.

Os intervalos são construídos com 300 reamostragens em blocos de UF, usando os mesmos sorteios entre períodos/grupos e pares `O,E` fixos. A documentação científica deve dizer que a incerteza da referência leave-one-out não é reestimada dentro dessas réplicas. Se a pergunta científica exigir incorporar a estimação da referência, será necessária uma análise de sensibilidade específica, com regra de tratamento para microrregiões repetidas na amostra bootstrap.

O período pandêmico é um período separado, mas a classificação COVID precisa ser reavaliada antes de interpretar a categoria infecciosas ou comparar sua evolução.

## 6. A discrepância 558/586

O repositório documenta 586 códigos distintos de `MICROCOD` no CADMUN e 558 unidades no painel analítico, centroides e scripts. A diferença não pode ser atribuída com segurança apenas à ausência de população, ausência de óbitos ou códigos especiais sem uma reconciliação código a código.

A auditoria definitiva deve gerar três conjuntos e suas diferenças:
- códigos distintos `MICROCOD` no CADMUN, excluindo e incluindo explicitamente situações especiais;
- códigos presentes em `BRASIL_taxas_por_idade.csv` e no painel de população;
- códigos efetivamente usados nos modelos, após filtros de dados e regras de exclusão.

A árvore pública contém `MICRORREGIOES_CENTROIDES.csv` e `MICRORREGIOES_VIZINHAS.csv` com 558 unidades. O arquivo `MUNICIPIO_MICRORREGIAO.csv` é gerado localmente pelo script de tabela. Não inventar a explicação dos 28 códigos faltantes antes de Claude executar a reconciliação.

## 7. Prioridades objetivas para o fechamento

1. Claude executar os nove testes de `test_classificacao_causas.py`.
2. Reextrair dados de causas com a nova regra de marcador COVID.
3. Confirmar se o marcador U07.1/U07.2 está efetivamente armazenado nos campos LINHAA-D/LINHAII para os anos relevantes; reportar cobertura dos campos e frequência de B34.2 com/sem marcador.
4. Recalcular `CAUSAS_TAU.csv`, `CAUSAS_COMPARACAO.csv`, `CAUSAS_TEMPORAL.csv`, `CAUSAS_TEMPORAL_3059.csv` e relatórios derivados somente após validar a nova extração.
5. Reconciliar 558/586 por código.
6. Atualizar `RESULTADOS_MUNICIPIOS.md` para retirar a equivalência simplista B34.2 = COVID.
7. Preservar os CSVs anteriores com sufixo `_v1` ou em commit histórico; não sobrescrever sem rastreabilidade.

## 8. Estado da auditoria

A análise documental do código de causas encontrou um ponto concreto e corrigível na classificação de COVID-19, com implementação e testes preparados na branch. O achado anterior sobre incompatibilidade entre bootstrap temporal e adendo principal foi corrigido nesta nota. Permanecem dependentes de execução local: testes, reextração SIM, fechamento dos grupos de causa e reconciliação territorial. Nenhum resultado novo foi apresentado como executado.
