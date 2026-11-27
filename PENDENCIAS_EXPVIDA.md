# Pendências do EXPVIDA

Projeto EXPVIDA (`C:\EXPVIDA`). Resultado da auditoria técnica de 27/11/2026. A decisão sobre cada pendência é do Vladimir.

## Bloqueadores (impedem a H10 ou um artigo defensável)

**1. A COVID-19 está misturada com as infecciosas.** O código procura `U07`, mas o SIM grava `B34.2`. Em 2020–2021, "infecciosas" sobe para 376.864 óbitos por ano. Correção: baixar o SIM de novo guardando a causa com 4 caracteres, separando `B34.2` (e `U07.1`/`U07.2`, se aparecerem). Também é possível consultar as linhas da declaração, se o ChatGPT achar necessário para o método.

**2. A idade 0 sem nascidos vivos.** O denominador é a população estimada de 0 ano do POPSVS. Correção: baixar o SINASC por município de residência e ano (2000–2024) e refazer a idade 0 com nascidos vivos, separando neonatal e pós-neonatal. Bloqueia qualquer conclusão sobre a H1 (idade 0), mas não a H10 em e0-80 nem a H2.

**3. Os dados brutos não ficam guardados.** Os scripts apagam o cache do SIM e do POPSVS. Isso não impede o trabalho, mas impede a reprodução fiel se o DATASUS mudar os arquivos. Correção possível: guardar uma vez os `.dbc` usados num local fora do projeto, com a data da cópia, se houver espaço em disco. Sem espaço, registrar pelo menos a data de cada download e o tamanho dos arquivos baixados.

## Importantes

**4. Medidas de natureza diferente no projeto.** O τ usa a razão de risco por idade (taxa específica da microrregião contra o resto do Brasil, com o acaso de Poisson descontado por modelo). A e0, a e0-80 e a q15-60 vêm de tábuas de vida. `analise_municipios.py` usa a razão padronizada indireta suavizada por Bayes empírico. `analise_violencia.py` usa a taxa bruta. `blindagem_violencia.py` usa a taxa padronizada direta (padrão Brasil 2010–2014). Dentro de cada família, a comparação é direta. Entre famílias, não: uma taxa bruta de homicídio e uma razão padronizada suavizada não podem ser colocadas na mesma tabela. A onda dos homicídios deve passar a ser apresentada com a taxa padronizada; a blindagem mostrou que as conclusões se mantêm.

**5. As mortes de intenção indeterminada.** No Sudeste passaram de 26,5 para 92,3 por 100 homicídios entre 2000–02 e 2022–24, e em São Paulo de 30,2 para 166,5. Todos os artigos de violência e a H10 precisam de cenários de sensibilidade. Já existe o de 0/50/100% (`blindagem_violencia.py`). Falta o cenário proporcional por sexo, idade e região.

**6. Arquivos sem script.** `ARRIAGA_2000-2004.csv` até `ARRIAGA_2022-2024.csv` não têm script na pasta. Ou se encontra o código que os gerou, ou eles não devem ser usados em artigo.

**7. Origem do IDHM não documentada.** `idhm_municipios_RE.csv` e `IDHM_RE_POR_MICRORREGIAO.csv` não têm script nem fonte escrita. Registrar de onde vieram (provavelmente o Atlas do Desenvolvimento Humano no Brasil, PNUD/IPEA/FJP) e o cálculo da média por microrregião (ponderada pela população, nos scripts novos).

**8. A motocicleta não está no arquivo de 18 idades.** Ela só aparece em `CAUSAS_MUNICIPIO.csv` (7 faixas). Para a H10 com motocicleta separada, é preciso refazer o arquivo de causas por microrregião.

**9. LEIAME.md desatualizado.** Diz "586 microrregiões" e não descreve as análises de violência, Censo 2022, CNES e municípios. O número correto é 558 (586 inclui 27 códigos "ignorado" e o código legado `52998`).

## Secundários

**10.** `bootstrap_subregistro_sem_mal_definidas.py` grava com caminho relativo e só funciona se for executado de dentro da pasta. **11.** Os mapas baixam o contorno dos municípios de um repositório externo (tbrugz/geodata-br); seria melhor fixar a versão. **12.** "Transporte" inclui acidentes aquáticos e aéreos (V90–V99); declarar no método. **13.** Confirmar no DATASUS se os dados de 2024 do SIM já são definitivos. **14.** A `main` local está em `600b594`, enquanto `origin/main` recebeu o commit `3c753c0`; atualizar a `main` local quando for conveniente. **15.** A busca do Sinesp falhou (DNS do dados.mj.gov.br, `VIOLENCIA_LOG.txt`); não é necessária agora. **16.** A pasta `__pycache__` pode ser ignorada.

## O que foi executado nesta auditoria

Listagem completa da pasta (`device_list_dir`); cópia para leitura de 44 scripts, 19 documentos, logs e 9 tabelas; extração automática das leituras e gravações de cada script; leitura manual de `brasil_expectativa.py`, `divergencia_modelo.py`, `causas_municipio.py`, `causas_sim.py`, `baixar_violencia.py` e `analise_municipios.py`; conferência das unidades territoriais; conferência da soma dos óbitos por causa contra `BRASIL_taxas_por_idade.csv`; contagem das categorias de `CAUSAS_MUNICIPIO.csv`. Os scripts de análise antigos **não foram reexecutados**, então nenhum resultado antigo foi declarado como reproduzido. O único script executado foi o novo `blindagem_violencia.py`, numa cópia dos dados. Ele leva cerca de 5 segundos.

## O que não pôde ser reproduzido

`ARRIAGA_2000-2004.csv` a `ARRIAGA_2022-2024.csv` (sem script) e a origem do IDHM. Todo o resto tem script, mas as etapas de download só podem ser refeitas baixando os dados de novo do DATASUS e do IBGE.

## Sugestão de ordem

Primeiro, uma única nova leitura do SIM 2000–2024 que resolve juntos os itens 1 e 8: causa com 4 caracteres, COVID separada, motocicleta separada e as mesmas 18 idades por microrregião. Depois, o SINASC (item 2), as correções de documentação (itens 6, 7 e 9) e, aprovado o método pelo ChatGPT e pelo Vladimir, a H10.
