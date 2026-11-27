# Execução local de fechamento — EXPVIDA
**Instruções para Claude | 27/11/2026**
**Branch de referência:** `auditoria-chatgpt-2026-11-27`

Este arquivo consolida somente as ações que exigem o ambiente local e os arquivos SIM/POPSVS. Não é necessário repetir a auditoria documental já registrada.

## 1. Preparação segura

1. Confirmar que está no repositório `C:\EXPVIDA`.
2. Criar/usar branch local correspondente à branch remota `auditoria-chatgpt-2026-11-27`, sem alterar `main`.
3. Conferir que os scripts locais correspondem aos arquivos versionados nessa branch.
4. Não apagar bases, caches, CSVs antigos ou resultados anteriores.
5. Registrar Python, versões de bibliotecas, commit, data/hora e logs.

## 2. Testes unitários novos

Executar:

```powershell
python -m unittest -v test_classificacao_causas test_h10_shapley
```

Esperado:
- 16 testes de classificação de causas/COVID;
- 4 testes sintéticos de H10;
- nenhum acesso à internet ou microdados individuais para os testes.

Se houver falha, corrigir primeiro os testes ou o código; não executar extração completa com testes quebrados.

## 3. Extração de causas e classificação COVID

Executar na ordem:

```powershell
python tabela_municipio_microrregiao.py
python causas_sim.py
python causas_sim_periodos.py
```

A nova versão lê `CAUSABAS`, `LINHAA`, `LINHAB`, `LINHAC`, `LINHAD` e `LINHAII`.

Regra:
- U07.1/U07.2 como causa básica: `covid19`;
- B34.2 com marcador U07.1/U07.2 nas linhas da DO: `covid19`;
- B34.2 sem marcador: permanece em `infecciosas`;
- U07 presente com outra causa básica: não substitui a causa básica.

Os relatórios `CAUSAS_QUALIDADE.csv` e `CAUSAS_QUALIDADE_OUTROS.csv` agora devem conter:
- `b342_com_u07`;
- `b342_sem_u07`;
- `u07_basica`.

Conferir se os três campos aparecem por UF/ano, se há variação temporal plausível e se o número de marcadores é coerente com os campos preenchidos. Não rotular B34.2 isolado como COVID.

## 4. Extração municipal

Executar:

```powershell
python causas_municipio.py
```

A nova versão aplica a mesma regra de COVID e grava os três contadores adicionais em `CAUSAS_MUNICIPIO_QUALIDADE.csv`.

Não sobrescrever os CSVs antigos sem cópia/versionamento. Guardar os arquivos anteriores com sufixo `_classificacao_v1` ou preservá-los no histórico Git.

## 5. Fechamento das causas e H10

Executar primeiro um diagnóstico de fechamento entre:
- soma dos grupos causa-específicos;
- óbitos gerais de `BRASIL_taxas_por_idade.csv`;
- por microrregião, sexo, período e idade.

O adendo de fechamento documenta 37 óbitos de diferença na base antiga, todos em 2000–2004 na microrregião 43016 (22 homens, 15 mulheres), com efeito quase nulo em um teste específico de homens 30–59. Isso não autoriza ignorar a diferença na nova análise H10: identificar se a discrepância permanece após a nova extração e documentar sua origem.

Somente se o fechamento estiver exato, testar H10:

```powershell
python -c "from h10_shapley import run_h10; r=run_h10('.', '2015-2019', 1); print(r['variance_reduction'], r['contributions'], r['closure_error'], r['diagnostics'])"
python -c "from h10_shapley import run_h10; r=run_h10('.', '2015-2019', 2); print(r['variance_reduction'], r['contributions'], r['closure_error'], r['diagnostics'])"
```

O módulo calcula 2^12 cenários contrafactuais por sexo/período, com grupos mutuamente exclusivos e Shapley exato. A contribuição positiva indica redução da variância territorial de e0-80 ao equalizar aquele grupo à taxa nacional. Não chamar de efeito causal.

Não executar os 12 conjuntos sexo-período em lote antes de medir o tempo dos dois testes de 2015–2019. Se a execução for muito lenta, registrar o tempo e propor otimização sem alterar o estimando.

## 6. Reconciliação 558 versus 586

Gerar uma tabela por código com:
1. 586 códigos distintos de MICROCOD do CADMUN;
2. 558 códigos presentes nos centroides/painel analítico;
3. códigos presentes em óbitos e exposição por período/sexo;
4. códigos excluídos e motivo comprovado.

Não atribuir automaticamente os 28 códigos a microrregiões sem população, sem óbitos ou a códigos especiais. A diferença deve ser demonstrada por interseção de conjuntos e tabelas de frequência.

## 7. Reexecução de resultados dependentes de causas

Após validar a classificação:
- reexecutar `causas_tau.py`;
- reexecutar `causas_comparacao.py`;
- reexecutar `causas_temporal.py`;
- reexecutar `causas_temporal_3059.py`;
- reexecutar análises municipais que dependam de `CAUSAS_MUNICIPIO.csv`;
- comparar resultados antigos e novos, identificando especificamente o impacto da nova regra COVID.

Os resultados antigos devem ser preservados; novos arquivos devem ser identificados como versão pós-auditoria.

## 8. Critérios de conclusão

A tarefa local só estará fechada quando:
- os 20 testes unitários passarem;
- as extrações terminarem sem falhas;
- os contadores U07/B34.2 forem preenchidos e conferidos;
- o fechamento por causa for documentado;
- 558/586 for reconciliado por código;
- H10 tiver fechamento Shapley numérico próximo de zero, ou tiver sido formalmente bloqueada por falta de fechamento dos dados;
- os resultados de causas tiverem sido reexecutados e comparados;
- logs, parâmetros, semente e commit estiverem registrados.

## 9. Restrições

Não alterar `main`, não fazer deploy, não publicar, não excluir dados e não substituir resultados antigos. Fazer commit somente na branch de auditoria ou em branch derivada. Não declarar teste aprovado sem log real.
