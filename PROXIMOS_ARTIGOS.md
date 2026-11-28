# EXPVIDA — Ideias para os próximos artigos

Registro de 28/11/2026. A escolha do próximo artigo é do autor do projeto; este arquivo apenas guarda as opções levantadas.

## Situação do artigo 1

O artigo "Da geografia da violência à geografia da desigualdade: homicídios e expectativa de vida nos territórios brasileiros, 2000–2024" está finalizado por enquanto (versão 0.3, ramo chatgpt-manuscrito-v03). Não acrescentar novas hipóteses nem novos modelos a ele.

Pendências antes de submeter: revisão final de consistência de números, referências e interpretação; conferir DOI e autores da referência 5 (Soares Filho et al., Ciência & Saúde Coletiva, 2020).

Mensagem central do artigo 1: a desigualdade territorial caiu porque as doenças convergiram, não porque a violência convergiu.

## Visão de conjunto

A grande riqueza do EXPVIDA talvez não esteja em descobrir qual região tem mais mortes, mas em compreender como a desigualdade de sobrevivência se organiza, persiste e se transforma dentro do território brasileiro. É uma agenda científica, não apenas um artigo.

## Candidata 1 — Persistência e mobilidade territorial

Pergunta: as microrregiões que estavam piores em 2000 continuam piores em 2024, ou algumas conseguiram sair do fundo da distribuição?
Por que importa: a variância pode cair enquanto os mesmos territórios continuam nas posições desfavoráveis; a variância sozinha não mostra isso.
Base: e0–80 por microrregião (558) nos seis períodos de 2000–2004 a 2022–2024.

## Candidata 2 — Convergência por idade

Pergunta: a desigualdade territorial diminuiu igualmente entre crianças, jovens, adultos e idosos? Em que fase da vida ela resistiu?
Por que importa: a medida agregada e0–80 pode esconder diferenças entre as idades.
Cuidado: o resultado de idosos por IDHM foi excluído do artigo 1 por suspeita de sub-registro.

## Candidata 3 — Entre regiões e dentro das regiões

Pergunta: quanto da desigualdade de expectativa de vida está entre as cinco grandes regiões e quanto está dentro delas?
Resultados PRELIMINARES (homens; calculados fora do repositório, ainda sem script que os reproduza): a parcela da variância que está entre regiões foi de 18,3%, 5,4%, 5,5%, 23,5%, 17,4% e 28,8% nos seis períodos. A variância absoluta entre regiões subiu de 0,08 (2010–2014) para 0,37 (2022–2024). A maior parte da desigualdade continua dentro das regiões, mas as regiões voltaram a se afastar depois de 2010.
e0–80 dos homens em 2022–2024: Nordeste 68,44; Sudeste 69,74; Sul 69,99.
Diálogo com a literatura: a decomposição da variância entre e dentro de regiões mede algo diferente da comparação de médias entre regiões (por exemplo, Calazans). Os dois resultados podem coexistir; não afirmar contradição nem correção sem comparar medidas, períodos e unidades de análise.
Próximo passo técnico previsto: script entre_dentro_regioes.py gerando V03_TABELA_ENTRE_DENTRO.csv, em ramo próprio a partir do main.

## Candidata 4 — Trânsito

Observação: a participação do trânsito na desigualdade dos homens passou de 5,9% (2015–2019) para 11,9% (2022–2024).
Separar três perguntas antes de interpretar: (a) a mortalidade por transporte aumentou? (b) a contribuição absoluta do transporte para a desigualdade aumentou? (c) a participação subiu apenas porque outras causas caíram mais?
Hipótese a testar: motocicletas no interior do Norte e do Nordeste.

## Candidata 5 — Transição epidemiológica territorial

Pergunta: as microrregiões estão se aproximando também na composição das causas de morte, e não só em quanto sobrevivem?
Cuidado: separar mudança no perfil epidemiológico de mudança na estrutura etária.

## Outras ideias anotadas

Capital versus interior.

## Ordens possíveis (decisão do autor)

Ordem A (começa pelo que já tem resultado): entre e dentro das regiões; persistência; idade; trânsito.
Ordem B (começa pela pergunta mais forte): persistência e mobilidade como artigo 2; convergência por região, idade e causa como artigo 3.

## Regras de escrita mantidas para todos os artigos

Usar "até onde sabemos", nunca "inédito". Usar "maior componente isolado", nunca "principal motor". Facções criminosas: no máximo uma frase, como hipótese. A contribuição é estatística e descritiva, não causal. Não inventar referências. Conferir todo número contra as tabelas do repositório antes de entrar em manuscrito.