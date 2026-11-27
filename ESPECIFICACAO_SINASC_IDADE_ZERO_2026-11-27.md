# Especificação — SINASC e denominador da idade zero
**EXPVIDA | 27/11/2026**  
**Status:** especificação para execução local por Claude. Nenhuma extração ou análise com dados reais foi executada nesta etapa.

## 1. Objetivo

Substituir, para a faixa de idade zero, a exposição baseada na população estimada por um denominador de nascidos vivos do SINASC. A finalidade é aproximar a construção da tábua de uma medida demográfica/epidemiológica apropriada para mortalidade infantil e reduzir a dependência da estimativa de população com menos de um ano.

O cálculo deve ser feito separadamente por microrregião, sexo e período. Não alterar a definição das demais 17 faixas etárias.

## 2. Arquivos do FTP do DATASUS

Para cada ano de 2000 a 2024, baixar os arquivos definitivos de nascidos vivos por UF de residência da mãe:

- **Servidor:** `ftp.datasus.gov.br`
- **Diretório:** `/dissemin/publicos/SINASC/1996_/Dados/DNRES/`
- **Padrão do nome:** `DN<UF><AAAA>.dbc`
- **Exemplos:** `DNAC2000.dbc`, `DNSP2015.dbc`, `DNRS2024.dbc`.
- **URL-base:** `ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Dados/DNRES/`

A extração nacional requer, em princípio, os 27 arquivos estaduais de cada ano (25 anos × 27 UFs). O arquivo representa nascimentos segundo a UF de residência da mãe, e não segundo o município onde ocorreu o parto. Não usar os arquivos de `PRELIM` junto com os definitivos na análise principal. Se algum arquivo definitivo estiver ausente, registrar UF, ano, caminho consultado e data da consulta; não substituir silenciosamente por preliminar nem assumir zero nascimentos.

A documentação técnica do conjunto SINASC identifica o diretório `1996_/Dados/DNRES`, o padrão `DN + UF + ano` e a convenção de residência materna. O dicionário consultado identifica `DTNASC`, `CODMUNRES` e `SEXO`. Fontes: documentação do conjunto SINASC e estrutura disponibilizada pelo DATASUS, com referência de diretório também no catálogo de fontes do CONASS.

## 3. Variáveis mínimas e filtros

Ler os arquivos DBC e conferir, ano a ano, a presença e o formato das seguintes colunas:

| Campo | Uso |
|---|---|
| `CODMUNRES` | Código IBGE de seis dígitos do município de residência da mãe. É a variável territorial do denominador. |
| `DTNASC` | Data de nascimento da criança. Usar para conferir/derivar o ano de nascimento e validar o arquivo anual. |
| `SEXO` | Sexo do recém-nascido: em regra, 1 masculino, 2 feminino; códigos ignorados devem ficar fora dos denominadores por sexo e ser contabilizados à parte. |

O nome físico do campo de data é `DTNASC`; o formato pode variar entre versões do layout. Conferir o layout de cada ano e converter datas sem assumir um único formato para todos os anos. O arquivo anual já é particionado pelo ano do nascimento, mas a data deve ser validada e usada para identificar registros fora do ano nominal, se existirem.

Não usar `CODMUNNASC` para o agrupamento territorial: ele identifica o município de ocorrência do nascimento. O denominador do EXPVIDA é por residência da mãe, portanto a chave correta é `CODMUNRES`.

## 4. Agregação nas 558 microrregiões

Usar a mesma tabela município–microrregião já adotada pelo projeto, sem criar uma geografia alternativa:

1. Gerar ou conferir `MUNICIPIO_MICRORREGIAO.csv` executando o script existente `tabela_municipio_microrregiao.py`. Ele baixa a tabela CADMUN e produz os campos `municipio`, `nome`, `uf` e `microrregiao`.
2. Normalizar `CODMUNRES` e `municipio` para strings de seis dígitos, preservando zeros à esquerda.
3. Fazer junção exata por município de residência da mãe.
4. Agregar a contagem de nascidos vivos por `microrregiao`, `sexo` e `ano`.
5. Conferir quantos registros ficaram sem correspondência no CADMUN. Não atribuir município desconhecido a uma microrregião por aproximação.
6. Somar as contagens anuais nos mesmos seis períodos do EXPVIDA:

| Período | Anos incluídos |
|---|---|
| 2000–2004 | 2000, 2001, 2002, 2003, 2004 |
| 2005–2009 | 2005, 2006, 2007, 2008, 2009 |
| 2010–2014 | 2010, 2011, 2012, 2013, 2014 |
| 2015–2019 | 2015, 2016, 2017, 2018, 2019 |
| 2020–2021 | 2020, 2021 |
| 2022–2024 | 2022, 2023, 2024 |

O resultado mínimo esperado é uma tabela com uma linha por `microrregiao × periodo × sexo`, com número de nascidos vivos, número de arquivos/anos efetivamente cobertos, registros sem município associado e nascimentos com sexo ignorado.

O painel principal utiliza 558 microrregiões. Se a tabela CADMUN retornar 586 códigos, não reduzir ou expandir o universo por suposição: usar o conjunto de 558 códigos da base analítica, registrar os códigos de nascimentos que não se associam ao painel e manter a reconciliação 558/586 como diagnóstico separado.

## 5. Numerador de óbitos infantis

O numerador deve vir do SIM, por município de residência da criança, sexo e ano do óbito, usando os registros com idade ao morrer inferior a um ano. O campo de residência do SIM é `CODMUNRES`; a idade deve ser interpretada conforme o formato SIM (minutos, horas, dias, meses ou anos), sem confundir o código de idade com idade em anos inteiros.

Agregação:
- filtrar óbitos com idade menor que um ano;
- agrupar por município de residência, sexo e ano do óbito;
- associar o município à mesma tabela CADMUN;
- agregar em microrregião e nos seis períodos;
- conferir sexo ignorado, idade ignorada e município sem correspondência.

A correspondência de residência entre SINASC e SIM é conceitualmente: residência da mãe no nascimento para o denominador e residência registrada para a criança no óbito para o numerador. A diferença entre essas residências é um risco de classificação territorial, não algo que se resolva trocando o município de ocorrência pelo de residência.

## 6. Fórmula: nascidos vivos → q0 → m0

Para cada microrregião (i), sexo (s) e período (p), definir:

[
q_{0,isp}^{(NV)} = rac{D_{0,isp}}{NV_{isp}}
]

em que (D_0) é o número de óbitos de menores de um ano no período e (NV) é o total de nascidos vivos no mesmo período. Se a taxa for armazenada por mil, primeiro dividir por 1.000. O valor usado como probabilidade é a razão sem multiplicador por mil.

**Não usar essa razão diretamente como (m_0).** A função `_life_e0_80` de `h10_shapley.py` recebe taxas centrais (m), não probabilidades (q). Ela converte (m_0) em (q_0) pela fórmula:

[
q_0 = rac{m_0}{1+(1-a_0)m_0}
]

Logo, para manter exatamente a convenção da função, é necessário inverter a expressão:

[
m_0 = rac{q_0}{1-(1-a_0)m_0^{,0}q_0}
]

Na expressão acima, (a_0) depende do próprio (m_0), de acordo com a regra Coale–Demeny implementada no código. Portanto, a inversão correta é resolvida por ramo, usando as mesmas constantes e o mesmo ponto de corte da função:

### Homens (`sex == 1` em `_life_e0_80`)

- Se (m_0 < 0{,}107), a função usa (a_0=0{,}045+2{,}684m_0). Substituindo e resolvendo a equação quadrática, com (q=q_0^{(NV)}):

[
2{,}684q,m_0^2 + [1-0{,}955q]m_0-q=0
]

A raiz não negativa é:

[
m_0 = rac{-[1-0{,}955q]+sqrt{[1-0{,}955q]^2+4(2{,}684)q^2}}{2(2{,}684)q}
]

e deve satisfazer (m_0<0{,}107).

- Se (m_0geq0{,}107), a função usa (a_0=0{,}330), portanto:

[
m_0=rac{q}{1-0{,}670q}
]

e o resultado deve satisfazer (m_0geq0{,}107).

### Mulheres (`sex == 2` em `_life_e0_80`)

- Se (m_0<0{,}107), a função usa (a_0=0{,}053+2{,}800m_0):

[
2{,}800q,m_0^2 + [1-0{,}947q]m_0-q=0
]

A raiz não negativa é:

[
m_0 = rac{-[1-0{,}947q]+sqrt{[1-0{,}947q]^2+4(2{,}800)q^2}}{2(2{,}800)q}
]

e deve satisfazer (m_0<0{,}107).

- Se (m_0geq0{,}107), a função usa (a_0=0{,}350):

[
m_0=rac{q}{1-0{,}650q}
]

e o resultado deve satisfazer (m_0geq0{,}107).

Para (q=0), definir (m_0=0). Para (q>0), calcular os candidatos dos ramos e aceitar somente o que satisfizer a condição do próprio ramo. Se nenhum candidato for consistente, interromper a construção daquela célula e registrar o caso; não escolher o ramo por aproximação. Verificar também (0leq q<1), (m_0geq0) e ausência de denominador nulo.

**Correção importante da notação:** a expressão de inversão geral, quando (a_0) já é conhecido, é (m_0=q_0/[1-(1-a_0)q_0]). Como no EXPVIDA (a_0) é função de (m_0), as fórmulas quadráticas acima são a forma operacional exata para o ramo de baixa mortalidade; o ramo alto é a inversão direta.

### Integração com a tábua

- Construir a matriz de taxas centrais de mortalidade com (m_0) obtido acima na primeira coluna.
- Manter as demais colunas de (m) como estão, calculadas a partir de óbitos/pessoas-ano do POPSVS.
- Passar a matriz de 17 faixas (0 a 75–79) e o sexo para `_life_e0_80(mortality_rates, sex)`.
- Não incluir 80+ na soma de (e_{0-80}), pois a função explicitamente usa as faixas 0 a 75–79.
- A função calcula (q_0) novamente a partir de (m_0). Isso é intencional: a inversão acima garante que o (q_0) reconstruído pela função seja o valor calculado com nascidos vivos, salvo tolerância numérica.

**Atenção à natureza da razão:** (D_0/NV) calculado com óbitos ocorridos no ano/período e nascimentos do mesmo ano/período é uma taxa de período convencional, não uma probabilidade de coorte observada acompanhando cada nascimento por 12 meses. O documento deve chamar o valor de (q_0) de aproximação de período usada para compatibilizar a tábua, e não de risco individual/coorte exato.

## 7. Riscos e controles obrigatórios

1. **Sub-registro de nascimentos:** cobertura do SINASC pode variar por UF, município e ano, especialmente nos primeiros anos. A falta de registros reduz artificialmente o denominador e pode elevar a razão de mortalidade.
2. **Sub-registro de óbitos infantis:** o numerador também pode estar incompleto e a qualidade do SIM pode variar no território e no tempo. SINASC não corrige sub-registro do SIM.
3. **Mudança de município de residência:** a mãe pode mudar de município entre o nascimento e o óbito; o SIM pode registrar residência diferente da residência materna do SINASC. O vínculo territorial é ecológico e não acompanha individualmente a criança.
4. **Óbitos no ano seguinte ao nascimento:** uma criança nascida no fim de um ano pode morrer antes de completar um ano no ano seguinte. Por isso, óbitos do período não correspondem exatamente aos nascimentos do mesmo período. Uma análise de coorte exigiria vinculação individual protegida ou reconstrução por coorte de nascimento, não disponível nesta especificação.
5. **Arquivo ausente:** arquivo estadual/ano ausente não equivale a zero nascimentos. Registrar e bloquear o período afetado ou obter a versão definitiva correta.
6. **Mudança de layout:** os campos podem ganhar colunas ou mudar representação. Conferir o layout por ano; não presumir formato fixo de `DTNASC` nem codificação invariável de sexo sem validação.
7. **Municípios sem correspondência:** não imputar microrregião por UF, nome aproximado ou município de ocorrência. Guardar a contagem não vinculada e investigar.
8. **Sexo ignorado:** não distribuir nascimentos de sexo ignorado proporcionalmente entre homens e mulheres. Relatar separadamente.
9. **Painel territorial:** não confundir os 586 códigos da tabela CADMUN com as 558 unidades efetivamente usadas no painel. A compatibilidade deve ser demonstrada por código.
10. **Taxa acima de um:** se (D_0/NVgeq1), tratar como falha de cobertura, agregação ou correspondência e não truncar para 1 sem investigação.

## 8. Teste de validação com valores oficiais publicados

Claude deve fazer uma validação nacional e por UF para o ano de 2023, usando os mesmos critérios de residência, idade inferior a um ano e nascidos vivos.

**Referência externa conferida:** a tabela da Fundação Amazônia de Amparo a Estudos e Pesquisas (FAPESPA), *Taxa de Mortalidade Infantil, segundo Brasil, Grandes Regiões e Unidades da Federação, 2019–2023*, apresenta os valores de 2023 marcados com asterisco (preliminares), calculados com fonte SIM/SINASC do Ministério da Saúde:
- Brasil: **12,62 óbitos por mil nascidos vivos**;
- São Paulo: **11,37 por mil**;
- Acre: **17,03 por mil**;
- Roraima: **23,85 por mil**.

Fonte aberta e conferida: https://fapespa.pa.gov.br/sistemas/pcn2024/tabelas/4-saude/1-taxa-de-mortalidade-infantil-2019-2023.htm. O asterisco de 2023 indica dado preliminar na tabela. Os números são referência de conferência, não resultados do EXPVIDA.

**Procedimento do teste:**
1. Somar os óbitos de menores de um ano e nascidos vivos por residência para Brasil, SP e AC em 2023.
2. Calcular (1000	imes D_0/NV).
3. Comparar com os quatro valores acima, registrando diferença absoluta e relativa.
4. Antes de interpretar divergência, confirmar versão definitiva/preliminar, data de extração, critério de residência, sexo incluído, idade e cobertura de todos os arquivos.
5. Não exigir igualdade perfeita se as versões de dados ou a data de consolidação forem diferentes; exigir que a diferença seja explicada e reproduzível.

Como controle adicional de coerência, conferir que a soma das 27 UFs fecha com o Brasil, que as somas municipais fecham com as microrregiões e que as somas dos seis períodos fecham com 2000–2024, descontados apenas arquivos efetivamente ausentes e registros sem município/sexo válido.

## 9. Arquivos que Claude deve produzir localmente

A execução local deve gerar, no mínimo:
- tabela anual de nascidos vivos por município, sexo e ano;
- tabela de nascidos vivos por microrregião, sexo e período;
- relatório de arquivos ausentes, layouts, datas inválidas, municípios não vinculados e sexo ignorado;
- tabela de óbitos infantis por microrregião, sexo e período;
- tabela final com (D_0), (NV), (q_0), (m_0) e indicador de ramo da fórmula;
- relatório de validação Brasil/UF 2023 contra a tabela FAPESPA.

**Não executar nem apresentar resultados nesta etapa documental.** A implementação, a extração e a validação ficam com Claude no computador local de Vladimir.
