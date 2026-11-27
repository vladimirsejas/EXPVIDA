# Auditoria técnica do EXPVIDA

Projeto EXPVIDA, pasta `C:\EXPVIDA`, repositório `vladimirsejas/EXPVIDA`. Auditoria feita em 27/11/2026 pelo Claude (dados e execução), a pedido do Vladimir. É um diagnóstico de leitura: nenhum script de análise antigo foi reexecutado, nenhum arquivo foi apagado ou alterado e a branch `main` não foi tocada.

## 1. Como a auditoria foi feita

A pasta foi listada por completo. Os 44 scripts Python, os 19 documentos Markdown, os logs e as tabelas pequenas e médias foram copiados para leitura. As dependências (o que cada script lê, grava e baixa) foram extraídas automaticamente do código e conferidas à mão nos scripts centrais. Três conferências numéricas foram executadas sobre os arquivos existentes, descritas na seção 5. Não existem scripts em R nem arquivos Parquet no projeto.

## 2. Inventário

A pasta tem 1 subpasta de cache do Python (`__pycache__`, descartável), o `.git` e, na raiz, 44 scripts `.py`, 19 `.md`, 2 `.pdf`, 6 `.png`, 4 `.txt` de log e cerca de 85 `.csv`. Não há subpastas de dados.

O estado do git é o seguinte. A branch ativa é `analises-divergencia-territorial`, com quatro commits: `600b594` (piloto Acre e base Brasil), `4392075` (divergência territorial), `1b4b1a7` e `3c753c0` (onda dos homicídios, Censo 2022, CNES e municípios). O último commit também foi enviado para `origin/main`, por pedido do Vladimir em 27/11. A `main` local continua em `600b594`. Os quatro arquivos com mais de 90 MB estão fora do GitHub por `.gitignore`: `CAUSAS_MUNICIPIO.csv` (184 MB), `CAUSAS_RACA_ESCOLARIDADE.csv` (103 MB), `CENSO2022_SOCIO_MUNICIPIOS.csv` (678 MB) e `IBGE_SOCIOECONOMICO_MUNICIPIOS.csv` (248 MB).

Os scripts se dividem em seis famílias:

| Família | Scripts | Papel |
|---|---|---|
| Diagnóstico inicial (Acre) | `inventario_sim_ac.py`, `piloto_expectativa.py`, `conferir_acre_e_populacao.py`, `diagnostico_codigos.py`, `diagnostico_sexo.py`, `inspecionar_cadmun.py`, `inspecionar_populacao.py`, `procurar_tabelas_auxiliares.py` | ler o FTP do DATASUS, conferir campos e montar a tábua de vida |
| Base Brasil | `brasil_expectativa.py`, `tabela_municipio_microrregiao.py` | baixar SIM + POPSVS + CADMUN e gravar taxas por idade e expectativas de vida |
| Divergência (τ) | `divergencia_modelo.py` (biblioteca), `divergencia_territorial.py`, `testes_hipoteses.py`, `sensibilidade_faixas.py`, `validacao_tau.py`, `comparacao_sexos.py`, `pandemia_tau.py`, `tau_condicoes_de_vida.py`, `figuras_esboco.py` | modelo Poisson-lognormal, hipóteses H1–H3, validação |
| Indicadores de idade (descartados como tese) | `idt_experimento.py`, `imd_alternativa.py`, `imd_sem_ruido.py`, `arriaga_territorial.py` | IDT, IMD e Arriaga 2015–2019 |
| Causas | `causas_sim.py`, `causas_sim_periodos.py`, `causas_tau.py`, `causas_comparacao.py`, `causas_temporal.py`, `causas_temporal_3059.py`, `checa_registro_3059.py`, `sensibilidade_subregistro_3059.py`, `bootstrap_subregistro_*.py`, `causas_municipio.py`, `analise_municipios.py`, `mapas_municipios.py` | causas por microrregião e por município |
| Violência e socioeconomia | `baixar_violencia.py`, `analise_violencia.py`, `baixar_socioeconomicos.py`, `baixar_censo2022.py`, `resumir_censo2022.py`, `baixar_cnes.py`, `analise_socio.py` | onda dos homicídios, Censo 2022, CNES |

`publicar_github.py` só faz commit e push.

## 3. Achados principais

**Os dados brutos não estão guardados.** Todos os scripts que baixam o SIM e o POPSVS usam um cache temporário do Windows (`%TEMP%\expvida_cache` e similares), e `brasil_expectativa.py` apaga esse cache ao terminar (`APAGAR_CACHE = True`). Não existe nenhum `.dbc` ou `.dbf` na pasta. As fontes originais são o FTP do DATASUS (`ftp.datasus.gov.br`, SIM `DO<UF><ano>.dbc`, POPSVS `POPSBR<aa>.zip`, CADMUN `SIM/CID10/TABELAS/CADMUN.DBF`), a API SIDRA do IBGE e os arquivos do CNES. Para reproduzir do zero é preciso baixar tudo de novo (cerca de 21 minutos para a base Brasil, segundo `BRASIL_PROGRESSO.txt`). A pasta guarda só contagens agregadas, o que protege a privacidade, mas a reprodução depende de o DATASUS manter os mesmos arquivos.

**558 e 586 microrregiões: o número certo é 558.** A tabela CADMUN do DATASUS tem 586 códigos de microrregião distintos. Desses, 27 são códigos "IGNORADO" (um por UF terminado em `000` e o `00000`) e 1 é o código `52998`, que agrupa municípios antigos de Goiás transferidos para o Tocantins (nomes "TRANSF. P/TO"). Sobram 558 microrregiões reais do IBGE, que são as usadas em todas as análises: `BRASIL_taxas_por_idade.csv`, τ, causas, violência e Censo têm exatamente 558. A frase do `LEIAME.md` ("586 do IBGE, pelo CADMUN") está desatualizada e deve dizer 558. Os óbitos com município ignorado (códigos `xx000`) aparecem nos arquivos de causas, mas ficam fora das 558.

**A categoria "covid" está vazia.** `causas_municipio.py` procura `U07` na causa básica, mas o SIM grava a COVID-19 como `B34.2`. Por isso a categoria "covid" não aparece em nenhuma linha, e as mortes por COVID foram somadas em "infecciosas": a média anual de óbitos infecciosos passa de cerca de 45 mil (2000–2004) para 376.864 em 2020–2021. Os arquivos guardam só a letra e os dois primeiros dígitos (B34), então separar o B34.2 exige ler de novo o SIM.

**Só a causa básica é lida.** Todos os scripts usam o campo `CAUSABAS`. As linhas da declaração (`LINHAA` a `LINHAD`, `LINHAII`) e a causa original não são consultadas. Isso é o padrão em demografia, mas deve ser declarado, e uma auditoria de COVID em causas múltiplas não é possível com os arquivos atuais.

**A idade 0 usa população estimada, não nascidos vivos.** O denominador do primeiro ano de vida é a população de 0 ano do POPSVS. Não há nenhuma leitura do SINASC (`procurar_tabelas_auxiliares.py` só listou a pasta de tabelas do SINASC). Também não há separação entre mortalidade neonatal e pós-neonatal.

**Há medidas de natureza diferente convivendo no projeto.** O detalhamento está em `PENDENCIAS_EXPVIDA.md`, item 4.

## 4. Resultados existentes e reprodutibilidade

"Reprodutível" significa aqui que o script que gera o resultado existe na pasta e lê só arquivos que também estão na pasta. Nenhum foi reexecutado nesta auditoria, exceto a blindagem da violência (seção 5).

| Resultado | Script | Arquivos | Situação |
|---|---|---|---|
| Expectativa de vida, e0-80, q15-60 por município, microrregião, UF | `brasil_expectativa.py` | `BRASIL_*.csv`, `BRASIL_RESUMO.md` | script existe; depende de novo download |
| τ por idade, sexo e período | `divergencia_territorial.py` + `divergencia_modelo.py` | `DIVERGENCIA_*.csv` | reprodutível com os CSV da pasta |
| H1–H3 e correção de Holm | `testes_hipoteses.py`, `sensibilidade_faixas.py` | `TESTES_*.csv`, `SENSIBILIDADE_FAIXAS.csv` | reprodutível |
| Validação (blocos de UF, Moran, simulação, influência) | `validacao_tau.py` | `VALIDACAO_*.csv`, `MICRORREGIOES_*.csv` | reprodutível |
| Diferença entre sexos | `comparacao_sexos.py` | `DIFERENCAS_TAU_*.csv`, `FIGURA_TAU_IDADE_SEXO.png` | reprodutível |
| Pandemia | `pandemia_tau.py` | `PANDEMIA_MUDANCA_TAU.csv` | reprodutível |
| τ com e sem condições de vida | `tau_condicoes_de_vida.py` | `TAU_COM_E_SEM_CONDICOES_DE_VIDA.csv` | lê `IDHM_RE_POR_MICRORREGIAO.csv`, cuja origem não tem script |
| IDT e IMD | `idt_experimento.py`, `imd_alternativa.py`, `imd_sem_ruido.py` | `IDT_*.csv`, `IMD_*.csv` | reprodutível (linha descartada como tese) |
| Arriaga territorial 2015–2019 | `arriaga_territorial.py` | `ARRIAGA_TERRITORIAL*.csv` | reprodutível |
| Arriaga por período | nenhum script encontrado | `ARRIAGA_2000-2004.csv` … `ARRIAGA_2022-2024.csv` | **órfão: não reprodutível** |
| Causas por microrregião | `causas_sim.py`, `causas_sim_periodos.py` | `CAUSAS_OBITOS_*.csv`, `CAUSAS_QUALIDADE*.csv` | depende de novo download |
| τ por causa, comparação e tempo | `causas_tau.py`, `causas_comparacao.py`, `causas_temporal*.py` | `CAUSAS_TAU.csv` etc. | reprodutível |
| Sub-registro 30–59 e bootstrap | `sensibilidade_subregistro_3059.py`, `bootstrap_*.py`, `checa_registro_3059.py` | `REPLICACOES_*`, `RESULTADO_*`, `SENSIBILIDADE_SUBREGISTRO_3059.md` | reprodutível; um bootstrap grava com caminho relativo (só funciona rodando de dentro da pasta) |
| Causas por município | `causas_municipio.py` | `CAUSAS_MUNICIPIO*.csv`, `POP_MUNICIPIO.csv`, `CAUSAS_RACA_ESCOLARIDADE.csv` | depende de novo download |
| Indicadores municipais, motociclistas, idosos | `analise_municipios.py`, `mapas_municipios.py` | `MUNICIPIOS_INDICADORES.csv`, `RANKING_*`, `PERSISTENCIA_*`, `CAPITAIS_*`, `GRADIENTE_RENDA_*`, `PERFIL_*`, mapas | reprodutível; mapas baixam o contorno dos municípios do GitHub (tbrugz/geodata-br) |
| Onda dos homicídios | `baixar_violencia.py`, `analise_violencia.py` | `VIOLENCIA_*.csv`, `ONDA_*.csv`, `HOMICIDIO_*.csv` | baixa: depende de download; análise: reprodutível |
| Censo 2022 e CNES | `baixar_censo2022.py`, `resumir_censo2022.py`, `baixar_cnes.py`, `analise_socio.py` | `CENSO2022_*`, `CNES_*`, `SOCIO_*` | baixas dependem da API do IBGE e do FTP do CNES; análise reprodutível |
| IDHM municipal | nenhum script | `idhm_municipios_RE.csv`, `IDHM_RE_POR_MICRORREGIAO.csv` | **origem não documentada** (colunas ANO, Codmun7, IDHM_R, IDHM_E, POP; tudo indica o Atlas do Desenvolvimento Humano) |

## 5. Testes executados nesta auditoria

Primeiro teste: consistência entre o arquivo de causas por microrregião e o arquivo de óbitos totais. Somando `CAUSAS_OBITOS_2015_2019.csv` e `CAUSAS_OBITOS_OUTROS_PERIODOS.csv` por microrregião, sexo, idade e período (sem os códigos ignorados), o total bate exatamente com `BRASIL_taxas_por_idade.csv` em cinco dos seis períodos. Em 2000–2004 sobram 37 óbitos em 14 células, muito provavelmente do código legado `52998`. Isso confirma que os dois arquivos podem ser usados juntos numa decomposição por causa.

Segundo teste: verificação da COVID. Contagem das categorias de `CAUSAS_MUNICIPIO.csv`: a categoria "covid" não existe, e "infecciosas" sobe para 376.864 óbitos por ano em 2020–2021.

Terceiro teste: contagem das unidades territoriais em `MUNICIPIO_MICRORREGIAO.csv`, `BRASIL_taxas_por_idade.csv`, `VIOLENCIA_MICRO_ANUAL.csv` e `SOCIO_MICRO.csv` (resultado na seção 3).

Também foi executado, antes desta auditoria e fora do notebook, o script novo `blindagem_violencia.py` (padronização etária, cenários de 0/50/100% de mortes indeterminadas e limiares de 20/30/40). Ele leu cópias idênticas dos CSV da pasta e está descrito em `RESULTADOS_BLINDAGEM.md`. Ainda não foi copiado para `C:\EXPVIDA`.

## 6. Diagnóstico em uma frase

O EXPVIDA tem uma base sólida e coerente nas 558 microrregiões, com o núcleo de τ reprodutível a partir dos CSV da pasta. Os pontos fracos são o download refeito a cada vez (sem dados brutos guardados), a COVID misturada às infecciosas, a idade 0 sem SINASC, dois arquivos de origem não documentada e um conjunto de arquivos Arriaga sem script.
