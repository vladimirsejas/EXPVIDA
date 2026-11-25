# EXPVIDA — Adendo final de fechamento da análise de sub-registro

## Escopo

Esta etapa foi realizada para resolver a lacuna apontada na auditoria independente: o bootstrap anterior cobria a variante sem causas mal definidas, enquanto a medida principal do artigo utiliza todas as causas. O presente adendo documenta o bootstrap da análise principal, sem causas removidas.

**População analisada:** homens de 30–59 anos, 558 microrregiões.

**Comparação:** 2000–2004 com correção determinística de cobertura em nove cenários versus 2022–2024 sem correção. Todas as causas de morte são mantidas nos dois períodos.

## Método

- Reamostragem em blocos das 27 UFs, com reposição.
- 1.000 replicações pareadas.
- Os mesmos sorteios de UFs são utilizados nos dois períodos e em todos os cenários.
- Em cada cenário, os pares de óbitos observados e esperados (O, E) são calculados na amostra completa antes da reamostragem e mantidos fixos durante o bootstrap. Essa escolha segue a estratégia de pares fixos utilizada nas análises anteriores de H2/H3 e evita recalcular a referência leave-one-out sobre microrregiões duplicadas na amostra bootstrap.
- A diferença é calculada dentro de cada replicação: τ(2000–04 corrigido) − τ(2022–24).
- Intervalos de 95% obtidos pelos percentis 2,5 e 97,5 da distribuição bootstrap pareada.
- Não houve falhas de estimação: 1.000 replicações válidas em cada cenário.

A cobertura estadual é aplicada uniformemente às microrregiões de cada UF. A incerteza das estimativas de cobertura não é propagada; portanto, a inferência é condicional aos valores de cobertura e aos denominadores POPSVS fixados.

## Resultados

| Cenário | τ 2000–04 | τ 2022–24 | Diferença | IC 95% da diferença |
|---|---:|---:|---:|---:|
| GGB 2000/2010 k1 | 0,238629 | 0,131165 | 0,107465 | 0,063435–0,147979 |
| GGB 2000/2010 k2 | 0,239032 | 0,131165 | 0,107867 | 0,061932–0,150695 |
| GGB 2000/2010 k3 | 0,268240 | 0,131165 | 0,137076 | 0,061031–0,211483 |
| SEG-adj 2000/2010 k1 | 0,215078 | 0,131165 | 0,083914 | 0,047466–0,123262 |
| SEG-adj 2000/2010 k2 | 0,200952 | 0,131165 | 0,069788 | 0,034754–0,110507 |
| SEG-adj 2000/2010 k3 | 0,254272 | 0,131165 | 0,123107 | 0,048627–0,190261 |
| SEG-adj 1991/2000 k1 | 0,221181 | 0,131165 | 0,090017 | 0,050257–0,129794 |
| SEG-adj 1991/2000 k2 | 0,216084 | 0,131165 | 0,084920 | 0,044539–0,128149 |
| SEG-adj 1991/2000 k3 | 0,318806 | 0,131165 | 0,187641 | 0,065634–0,356445 |

**Resultado:** os nove intervalos de 95% da diferença permanecem acima de zero. O limite inferior mais próximo de zero é 0,034754 (SEG-adj 2000/2010, k2). Não houve falhas de estimação.

## Interpretação

Na medida principal do artigo — todas as causas — a heterogeneidade territorial estimada para homens de 30–59 anos em 2000–2004 permanece maior que em 2022–2024 nos nove cenários de correção avaliados. A diferença pontual varia de aproximadamente 0,070 a 0,188, e os intervalos bootstrap de 95% não incluem zero.

A conclusão deve ser formulada como evidência de robustez nos cenários determinísticos examinados, não como prova de convergência real da mortalidade. A análise não separa integralmente convergência real de melhoria da cobertura do SIM e não incorpora a incerteza das estimativas de cobertura.

## Relação com a análise sem causas mal definidas

O bootstrap anterior com 300 replicações, para a variante sem causas mal definidas, permanece como análise de sensibilidade. Ele não deve ser usado como intervalo da medida principal. A análise principal está agora coberta pelo bootstrap de 1.000 replicações documentado neste adendo.

## Discrepância de 37 óbitos

A auditoria independente identificou 37 óbitos adicionais na base por causas em relação à base geral, todos em 2000–2004 e na microrregião 43016: 22 homens e 15 mulheres. A reestimação informada pela auditoria para homens de 30–59 anos resultou em τ = 0,249837 na base por causas e τ = 0,249840 na base geral, diferença de aproximadamente 0,000003. O efeito é negligenciável para o resultado analisado. A origem exata dos registros não foi confirmada; recomenda-se apenas documentar a discrepância em nota metodológica, sem excluir ou redistribuir registros.

## Consistência de versão dos arquivos anteriores

A auditoria identificou que o CSV anterior de resultados (bootstrap sem causas mal definidas) tinha uma coluna `falhas`, enquanto a versão atual do script registrava `falhas_2000_04` e `falhas_2022_24`. Os valores numéricos coincidiam, mas os arquivos eram de versões diferentes. O presente resultado principal foi gerado em arquivo próprio e possui as colunas de falhas separadas.

## Conclusão operacional

A lacuna que impedia o fechamento — ausência de bootstrap para a medida principal com todas as causas — foi resolvida. A análise principal e a sensibilidade sem causas mal definidas ficam claramente separadas. Não se recomenda abrir novas hipóteses ou modelos para esta questão. O resultado está pronto para ser incorporado ao manuscrito, com as limitações acima explicitadas.
