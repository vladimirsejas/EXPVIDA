# Sensibilidade do tau (homens, 30-59 anos) ao sub-registro de óbitos

Script: sensibilidade_subregistro_3059.py (ambiente de pesquisa; EXPVIDA original intacto).

Cobertura por UF, homens (Queiroz et al., Rev Bras Epidemiol 2017; 20(S1):21-33, Tabela 1). Óbitos corrigidos = óbitos / cobertura da UF (valores acima de 1 limitados a 1). O fator k multiplica o déficit publicado (1 - cobertura). Todas as microrregiões herdam a cobertura da sua UF.

tau 2022-2024 sem correção: 0,131 (com todos os óbitos). tau 2000-2004 sem correção: 0,250 (com todos os óbitos); 0,362 se forem excluídos os óbitos mal definidos.

| Cenário (2000-2004) | tau corrigido |
|---|---|
| Sem correção | 0,250 |
| GGB 2000/2010, k=1 / 2 / 3 | 0,239 / 0,239 / 0,268 |
| SEG-adj 2000/2010, k=1 / 2 / 3 | 0,215 / 0,201 / 0,254 |
| SEG-adj 1991/2000, k=1 / 2 / 3 | 0,221 / 0,216 / 0,319 |

2005-2009 com SEG-adj 2000/2010: 0,168 (k=1), 0,177 (k=2), 0,259 (k=3); sem correção 0,193.

Leitura: nos cenários baseados nos valores publicados (k=1 e k=2), o tau inicial cai para 0,20-0,24; a redução até 0,131 permanece de 35% a 45%. Com k=3 a correção passa do ponto e o tau volta a subir (o cenário deixa de ser plausível).

Limites: cobertura só por UF; não captura diferenças entre microrregiões dentro da UF; os valores são médias do período 2000/2010; não há correção para 2015-2024 (SIM em torno de 98% em 2015-16 segundo Costa et al. 2020).
