# Mapa do fluxo de dados do EXPVIDA

Projeto EXPVIDA (`C:\EXPVIDA`). As setas indicam "é lido por". Todos os arquivos ficam na raiz da pasta. Os dados brutos ficam num cache temporário e são apagados depois de cada execução.

## Fontes externas

| Fonte | Endereço | Quem baixa |
|---|---|---|
| SIM, óbitos por UF e ano (`DO<UF><ano>.dbc`), causa básica, por residência | FTP `ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/DORES` | `brasil_expectativa.py`, `causas_sim.py`, `causas_sim_periodos.py`, `causas_municipio.py`, `baixar_violencia.py` |
| POPSVS, população por município, sexo e idade (`POPSBR<aa>.zip`) | FTP `.../IBGE/POPSVS` | `brasil_expectativa.py`, `causas_municipio.py` |
| CADMUN, município → microrregião | FTP `.../SIM/CID10/TABELAS/CADMUN.DBF` | `brasil_expectativa.py`, `tabela_municipio_microrregiao.py` |
| Censo 2022 e catálogo de agregados | API SIDRA `apisidra.ibge.gov.br` e `servicodados.ibge.gov.br` | `baixar_socioeconomicos.py`, `baixar_censo2022.py` |
| CNES, equipes (EP) | FTP do DATASUS (CNES) | `baixar_cnes.py` |
| IDHM 2000/2010 | não documentado (provavelmente Atlas Brasil) | nenhum script |
| Contorno dos municípios | `raw.githubusercontent.com/tbrugz/geodata-br` | `analise_violencia.py`, `mapas_municipios.py` |

## Fluxo

```
FTP DATASUS (SIM + POPSVS + CADMUN)
 └─ brasil_expectativa.py ──► BRASIL_taxas_por_idade.csv  (558 micro × 18 idades × sexo × 6 períodos: óbitos, pessoas-ano)
                          ──► BRASIL_municipios.csv, BRASIL_microrregioes.csv, BRASIL_ufs_e_brasil.csv (e0, e0-80, q15-60, IC)
                          ──► BRASIL_RESUMO.md
     BRASIL_taxas_por_idade.csv
      └─ divergencia_modelo.py (biblioteca: τ Poisson-lognormal, tábua de vida, Arriaga)
          ├─ divergencia_territorial.py ──► DIVERGENCIA_POR_IDADE / _ESTABILIDADE / _SENSIBILIDADE.csv
          ├─ testes_hipoteses.py ──► TESTES_HIPOTESES*.csv, TESTES_H1_PARTICIPACAO_E0_80.csv
          ├─ sensibilidade_faixas.py ──► SENSIBILIDADE_FAIXAS.csv
          ├─ validacao_tau.py ──► VALIDACAO_*.csv, MICRORREGIOES_CENTROIDES.csv, MICRORREGIOES_VIZINHAS.csv
          ├─ comparacao_sexos.py ──► DIFERENCAS_TAU_*.csv, FIGURA_TAU_IDADE_SEXO.png
          ├─ pandemia_tau.py ──► PANDEMIA_MUDANCA_TAU.csv
          ├─ tau_condicoes_de_vida.py (+ IDHM_RE_POR_MICRORREGIAO.csv) ──► TAU_COM_E_SEM_CONDICOES_DE_VIDA.csv
          ├─ arriaga_territorial.py ──► ARRIAGA_TERRITORIAL*.csv (2015-2019)
          ├─ idt_experimento.py ──► IDT_*.csv ; imd_alternativa.py ──► IMD_*.csv ; imd_sem_ruido.py ──► IMD_SEM_RUIDO.csv
          └─ figuras_esboco.py ──► FIGURAS_ESBOCO.png
     (sem script) ──► ARRIAGA_2000-2004.csv … ARRIAGA_2022-2024.csv

FTP DATASUS (SIM)
 ├─ causas_sim.py ──► CAUSAS_OBITOS_2015_2019.csv, CAUSAS_QUALIDADE.csv   (micro × idade de 5 anos × 17 grupos)
 └─ causas_sim_periodos.py ──► CAUSAS_OBITOS_OUTROS_PERIODOS.csv, CAUSAS_QUALIDADE_OUTROS.csv
     └─ causas_tau.py ──► CAUSAS_TAU.csv, CAUSAS_CONFERENCIA.csv, CAUSAS_CORRELACAO_EFEITOS.csv
     └─ causas_comparacao.py ──► CAUSAS_COMPARACAO*.csv
     └─ causas_temporal.py / causas_temporal_3059.py ──► CAUSAS_TEMPORAL*.csv
     └─ checa_registro_3059.py, sensibilidade_subregistro_3059.py, bootstrap_subregistro_*.py ──► SENSIBILIDADE_SUBREGISTRO_3059.md, REPLICACOES_*, RESULTADO_*

FTP DATASUS (SIM + POPSVS)
 └─ causas_municipio.py ──► CAUSAS_MUNICIPIO.csv (município × 7 faixas × 39 causas), POP_MUNICIPIO.csv,
                            CAUSAS_RACA_ESCOLARIDADE.csv, CAUSAS_MUNICIPIO_QUALIDADE.csv
     └─ analise_municipios.py (+ idhm_municipios_RE.csv) ──► MUNICIPIOS_INDICADORES.csv, GRADIENTE_RENDA_MUNICIPAL.csv,
                            CAPITAIS_INTERIOR_REGIOES.csv, PERSISTENCIA_MUNICIPAL.csv, RANKING_MUNICIPIOS_100MIL.csv,
                            PERFIL_RACA_ESCOLARIDADE_2015_2024.csv ──► RESULTADOS_MUNICIPIOS.md/.pdf
     └─ mapas_municipios.py ──► MAPA_MUNICIPIOS_4_CAUSAS.png, GRADIENTE_RENDA_ANTES_DEPOIS.png

FTP DATASUS (SIM anual)
 └─ baixar_violencia.py ──► VIOLENCIA_ANUAL_MUNICIPIO.csv (ano × município × sexo × 7 faixas × 16 causas externas),
                            HOMICIDIO_OCORRENCIA_LOCAL.csv (LOCOCOR), VIOLENCIA_LOG.txt
     └─ analise_violencia.py (+ POP_MUNICIPIO, MUNICIPIO_MICRORREGIAO, idhm_municipios_RE) ──► VIOLENCIA_REGIAO_ANUAL.csv,
                            VIOLENCIA_MICRO_ANUAL.csv, ONDA_DECOLAGEM_MICRO.csv, ONDA_RESUMO.csv, HOMICIDIO_LOCAL_REGIAO.csv,
                            ONDA_HOMICIDIOS.png ──► RESULTADOS_VIOLENCIA.md/.pdf
     └─ blindagem_violencia.py [novo, ainda fora da pasta] ──► BLINDAGEM_*.csv ──► RESULTADOS_BLINDAGEM.md

API IBGE
 ├─ baixar_socioeconomicos.py ──► IBGE_SOCIOECONOMICO_MUNICIPIOS.csv, IBGE_CATALOGO_CENSO2022.csv
 └─ baixar_censo2022.py ──► CENSO2022_SOCIO_MUNICIPIOS.csv ──► resumir_censo2022.py ──► CENSO2022_COMPACTO.csv, CENSO2022_DICIONARIO.csv
FTP CNES
 └─ baixar_cnes.py ──► CNES_EQUIPES_MUNICIPIO.csv, CNES_LOG.txt
     CENSO2022_COMPACTO + CNES + ONDA_DECOLAGEM_MICRO + VIOLENCIA_MICRO_ANUAL
      └─ analise_socio.py ──► SOCIO_MUNICIPIOS_2022.csv, SOCIO_MICRO.csv, SOCIO_GRADIENTES.csv, SOCIO_CORRELACOES.csv, GRADIENTES_CENSO2022.png
```

## Fase inicial (Acre), já superada

`inventario_sim_ac.py`, `piloto_expectativa.py`, `conferir_acre_e_populacao.py`, `diagnostico_codigos.py`, `diagnostico_sexo.py`, `inspecionar_cadmun.py`, `inspecionar_populacao.py` e `procurar_tabelas_auxiliares.py` geraram os `PILOTO_AC_*`, `INVENTARIO_SIM_AC.md`, `DIAGNOSTICO_*.md`, `CADMUN_ESTRUTURA.md`, `POPULACAO_ESTRUTURA.md`, `TABELAS_AUXILIARES.md` e `CONFERENCIA_ACRE_POPULACAO.md`. `piloto_expectativa.py` e `inventario_sim_ac.py` continuam importantes porque são importados pelos scripts da base Brasil (tábua de vida e leitura do `.dbc`).

## Dependências entre scripts (importações)

`inventario_sim_ac.py` e `piloto_expectativa.py` → `brasil_expectativa.py` → `causas_sim.py`, `causas_municipio.py`, `baixar_violencia.py`, `baixar_socioeconomicos.py`. `causas_municipio.py` → `baixar_violencia.py`. `baixar_socioeconomicos.py` → `baixar_censo2022.py`, `baixar_cnes.py`. `divergencia_modelo.py` → todos os scripts de τ, causas e Arriaga. `validacao_tau.py` → `causas_*`, `comparacao_sexos.py`, `pandemia_tau.py`. `idt_experimento.py` → `imd_*`. Mudar `divergencia_modelo.py`, `brasil_expectativa.py` ou `piloto_expectativa.py` afeta quase tudo.
