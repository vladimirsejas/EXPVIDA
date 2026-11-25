# Adendo técnico — fechamento da análise de sub-registro
## Projeto “Quando o território importa” — EXPVIDA

**Data da execução:** 25/11/2026  
**Análise:** homens, 30–59 anos; 2000–2004 versus 2022–2024; exclusão de causas mal definidas; correção determinística de cobertura no período inicial; bootstrap pareado por blocos de UF.

## 1. Objetivo

Verificar se a diferença de heterogeneidade territorial entre 2000–2004 e 2022–2024 permanece após excluir causas mal definidas nos dois períodos e corrigir os óbitos do período inicial sob nove cenários de cobertura.

## 2. Dados e preparação

Foram utilizados `CAUSAS_OBITOS_2015_2019.csv`, `CAUSAS_OBITOS_OUTROS_PERIODOS.csv`, `BRASIL_taxas_por_idade.csv`, `divergencia_modelo(1).py` e as definições de cobertura registradas em `sensibilidade_subregistro_3059(1).py`.

Para cada período, sexo e microrregião, a matriz sem causas mal definidas foi construída como:

`óbitos sem mal definidas = óbitos de todas as causas − óbitos da categoria mal_definidas`.

A análise de comparação foi restrita a homens de 30–59 anos, utilizando os denominadores POPSVS originais, mantidos fixos.

## 3. Cenários de correção

A cobertura estadual foi limitada superiormente a 1 e o déficit publicado foi multiplicado por k:

`c_ajustada = 1 − k × (1 − min(1, c_publicada))`.

Os óbitos do período 2000–2004 foram divididos pela cobertura ajustada. Foram avaliados nove cenários: GGB 2000/2010 (k=1, 2, 3), SEG-adj 2000/2010 (k=1, 2, 3) e SEG-adj 1991/2000 (k=1, 2, 3). O período 2022–2024 não recebeu correção de cobertura.

## 4. Método do bootstrap

- 27 UFs utilizadas como blocos de reamostragem.
- 300 replicações, com reposição de UFs.
- Mesmos sorteios de UFs utilizados nos dois períodos, produzindo diferenças pareadas.
- A referência leave-one-out foi recalculada dentro de cada replicação a partir das microrregiões selecionadas.
- O modelo Poisson-lognormal e o estimador de τ foram os mesmos do arquivo `divergencia_modelo(1).py`.
- Os intervalos foram calculados pelos percentis 2,5 e 97,5 da distribuição bootstrap.
- Não houve falhas de estimação nas 300 replicações para nenhum dos dez conjuntos de estimativas (nove cenários de 2000–2004 e a referência de 2022–2024).

A inferência é condicional às coberturas fixadas. O procedimento não propaga a incerteza dos estudos de cobertura nem corrige heterogeneidade de cobertura dentro de cada UF.

## 5. Resultados

τ de referência em 2022–2024, sem causas mal definidas: **0,133975**; IC bootstrap 95%: **0,113759–0,149792**.

| Cenário | τ 2000–04 | τ 2022–24 | Diferença | IC 95% da diferença |
|---|---:|---:|---:|---:|
| GGB 2000/2010 k1 | 0,347249 | 0,133975 | 0,213274 | 0,148089–0,267578 |
| GGB 2000/2010 k2 | 0,338600 | 0,133975 | 0,204625 | 0,142952–0,258760 |
| GGB 2000/2010 k3 | 0,347302 | 0,133975 | 0,213327 | 0,141202–0,276008 |
| SEG-adj 2000/2010 k1 | 0,321037 | 0,133975 | 0,187062 | 0,130030–0,235078 |
| SEG-adj 2000/2010 k2 | 0,285922 | 0,133975 | 0,151947 | 0,100558–0,200393 |
| SEG-adj 2000/2010 k3 | 0,288051 | 0,133975 | 0,154076 | 0,091814–0,215180 |
| SEG-adj 1991/2000 k1 | 0,330265 | 0,133975 | 0,196290 | 0,132835–0,244873 |
| SEG-adj 1991/2000 k2 | 0,310573 | 0,133975 | 0,176598 | 0,120615–0,227854 |
| SEG-adj 1991/2000 k3 | 0,371902 | 0,133975 | 0,237927 | 0,110074–0,402735 |

**Resultado:** os nove intervalos de confiança pareados da diferença permanecem inteiramente acima de zero. O limite inferior mais próximo de zero é 0,091814 (SEG-adj 2000/2010 k3). Portanto, dentro dos cenários avaliados e condicionados às coberturas fixas, a maior heterogeneidade territorial em 2000–2004 persiste após a exclusão de causas mal definidas e a correção determinística de cobertura.

O cenário SEG-adj 1991/2000 k3 apresenta intervalo particularmente amplo (0,110–0,403), indicando maior instabilidade desse cenário agressivo. Ele não altera a direção da diferença, mas deve ser descrito com cautela.

## 6. Interpretação permitida

Formulação recomendada:

> Em homens de 30–59 anos, a heterogeneidade territorial estimada em 2000–2004 permaneceu superior à de 2022–2024 após a exclusão dos óbitos por causas mal definidas e sob nove cenários determinísticos de correção do sub-registro. Em bootstrap pareado por blocos das 27 unidades da Federação, com 300 replicações, os intervalos de 95% para a diferença de τ permaneceram acima de zero em todos os cenários. Esses resultados demonstram robustez da diferença às sensibilidades avaliadas, mas não permitem separar integralmente convergência real da mortalidade de mudanças na cobertura dos registros, uma vez que a incerteza das coberturas não foi propagada e a cobertura estadual foi aplicada uniformemente às microrregiões.

Não afirmar que o bootstrap elimina o viés de cobertura ou que demonstra causalmente uma convergência real da mortalidade.

## 7. Auditoria da discrepância entre a base por causas e a base geral

A conferência anterior de `CAUSAS_TEMPORAL_3059_CONF.csv` comparava apenas homens (sexo=1), daí a diferença de **22 óbitos** registrada para 2000–2004.

A conferência ampliada por sexo e idade mostrou:

- Homens: base por causas excede a base geral em **22 óbitos**.
- Mulheres: base por causas excede a base geral em **15 óbitos**.
- Total combinado: **37 óbitos**.
- Todos os desvios identificados estão na microrregião de código **43016** (RS).
- Nos homens, os desvios estão distribuídos por dez grupos de idade; o maior é de seis óbitos na faixa 80+.
- Nas mulheres, os desvios estão em quatro grupos etários; o maior é de dez óbitos na faixa 80+.

A diferença é residual em relação ao volume nacional, mas sua concentração em uma única microrregião indica que não deve ser descrita apenas como discrepância aleatória difusa. A hipótese operacional mais plausível a investigar é uma diferença de universo/atribuição municipal entre a agregação da base geral (que usa municípios presentes no universo POPSVS) e a agregação da base por causas (que usa o mapa município–microrregião). Os arquivos agregados disponíveis não identificam quais registros ou municípios geraram os 37 óbitos adicionais; portanto, a origem exata permanece não resolvida.

Recomendação: documentar a discrepância e, antes da submissão, conferir os municípios de código 43016 presentes no mapa e no universo POPSVS, se os arquivos municipais/qualidade correspondentes estiverem disponíveis. Não excluir ou redistribuir os 37 óbitos sem rastreabilidade.

## 8. Arquivos produzidos

- `bootstrap_subregistro_sem_mal_definidas.py`: script reproduzível da análise completa.
- `RESULTADO_FINAL_BOOTSTRAP_300.csv`: tabela final dos nove cenários e respectivos intervalos.
- `REPLICACOES_BOOTSTRAP_300.csv`: valores de τ em cada replicação, para todos os cenários e para 2022–2024.

## 9. Limitações remanescentes

1. A incerteza das estimativas de cobertura não foi propagada.
2. A cobertura estadual foi aplicada uniformemente às microrregiões de cada UF.
3. As estimativas de cobertura não correspondem perfeitamente a cada período e grupo etário.
4. Os denominadores POPSVS foram mantidos fixos.
5. O ajuste determinístico pode produzir óbitos fracionários; a inferência bootstrap é condicional a essas matrizes corrigidas.
6. A discrepância de 37 óbitos na microrregião 43016 ainda não tem origem documentalmente identificada.

## 10. Conclusão técnica

A etapa inferencial pendente foi executada: bootstrap pareado por blocos de UF com 300 replicações, sem falhas de estimação. Os nove intervalos de confiança da diferença entre 2000–2004 corrigido e 2022–2024, ambos sem causas mal definidas, ficaram acima de zero. A diferença temporal é, portanto, robusta aos nove cenários determinísticos de cobertura avaliados, sob as hipóteses explicitadas.

A única pendência de auditoria identificada nesta etapa é rastrear a origem dos 37 óbitos adicionais da base por causas na microrregião 43016 em 2000–2004. Essa discrepância é pequena, mas concentrada e deve ser documentada.
