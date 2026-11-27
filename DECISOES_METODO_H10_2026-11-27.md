# H10 — decisões metodológicas para aprovação

**EXPVIDA | 27/11/2026 | Documento para decisão de Vladimir**  
**Status: proposta; nenhuma análise com dados reais foi executada nesta etapa.**

## O que a H10 pretende medir

A H10 pergunta: **quanto cada grupo de causas de morte contribui para a desigualdade territorial da esperança de vida dos 0 aos 80 anos entre as 558 microrregiões brasileiras?**

Em termos simples: calculamos a esperança de vida de cada microrregião. Depois imaginamos um exercício: e se, para uma causa específica, todas as microrregiões tivessem a mesma taxa de mortalidade nacional daquela idade, sexo e período? Recalculamos a esperança de vida e observamos quanto a diferença entre microrregiões diminuiria ou aumentaria.

O método Shapley repete esse exercício considerando todas as combinações de causas. Assim, a contribuição de cada grupo é calculada pela média de sua contribuição marginal em diferentes ordens de substituição. Isso evita escolher uma única ordem arbitrária. **Não é uma prova de que a causa produz causalmente a desigualdade**: é uma decomposição contrafactual, condicionada à referência, aos grupos e à qualidade dos registros.

O resultado principal será a variância entre microrregiões de e₀–₈₀. A soma das contribuições Shapley corresponde à redução da variância entre o cenário observado e o cenário em que todos os grupos são equalizados.

## Decisões que Vladimir precisa tomar

### 1. Qual será a referência contrafactual?

- **A. Taxa nacional por idade, sexo e período (recomendação).** Cada microrregião recebe a taxa agregada do Brasil para aquela mesma idade, sexo e período. É uma referência comum, compreensível e alinhada ao precedente de Vierboom et al. (2019).
- **B. Taxa da macrorregião.** Compara cada microrregião com seu contexto regional. Pode mostrar desigualdades locais dentro de regiões, mas reduz o contraste entre regiões brasileiras.
- **C. Média simples das taxas das 558 microrregiões.** Dá o mesmo peso a cada território na construção da referência, em vez de refletir o total de óbitos e exposição. Responde a uma pergunta diferente da taxa nacional agregada.

**Recomendação: A.** Usar a taxa nacional agregada como análise principal; se houver interesse, B pode ser uma sensibilidade. A referência escolhida muda o tamanho e até o sinal das contribuições.

### 2. Todas as microrregiões terão o mesmo peso?

- **A. Pesos iguais (recomendação).** Cada uma das 558 microrregiões conta igualmente. Mede desigualdade entre territórios, independentemente de seu tamanho populacional.
- **B. Ponderação pela população.** Territórios mais populosos influenciam mais. Mede a dispersão territorial vivida sob uma distribuição populacional, e não a desigualdade entre unidades em pé de igualdade.

**Recomendação: A como resultado principal; B como sensibilidade.** As duas são legítimas, mas respondem a perguntas distintas. Não se deve trocar uma pela outra sem declarar a mudança.

### 3. Quantos e quais grupos de causas?

- **A. Manter os 19 grupos atuais.** Preserva mais detalhes, mas exige 524.288 cenários exatos (2¹⁹), tornando o cálculo pesado.
- **B. Agrupar em cerca de 10–12 grupos amplos (recomendação).** Permite 1.024 a 4.096 cenários (2¹⁰ a 2¹²), mantendo categorias epidemiologicamente interpretáveis. Proposta inicial: agressões/intervenção legal; intenção indeterminada; suicídios; transporte; demais causas externas; COVID-19; outras infecciosas; neoplasias; circulatórias; respiratórias; mal definidas/sem causa; demais doenças.
- **C. Usar 13–14 grupos.** Preserva mais distinções, mas exige 8.192 a 16.384 cenários e maior custo. Acima disso, considerar aproximação por amostragem de ordens, com erro Monte Carlo informado.

**Recomendação: B.** A lista final precisa ser conferida com o classificador e manter grupos mutuamente exclusivos e exaustivos. O agrupamento também muda a interpretação: uma categoria ampla pode esconder diferenças entre causas específicas.

### 4. Como tratar mortes por intenção indeterminada?

- **A. Mantê-las como grupo separado (recomendação principal).** Não presume que sejam agressões e preserva o que o SIM efetivamente registrou.
- **B. Reclassificar 50% como agressões.** Cenário intermediário de sensibilidade.
- **C. Reclassificar 100% como agressões.** Cenário-limite que mostra quanto a conclusão mudaria sob essa hipótese.

**Recomendação: A no cenário principal e apresentar também 0%, 50% e 100% como agressão**, como na análise de blindagem. Esses cenários medem a sensibilidade à classificação; não identificam qual morte indeterminada foi de fato homicídio.

### 5. Como tratar COVID-19 e 2020–2021?

- **A. COVID-19 como grupo próprio e 2020–2021 como período separado (recomendação).** Permite distinguir a contribuição da COVID e a mudança excepcional da pandemia.
- **B. COVID-19 própria, mas juntar 2020–2021 aos períodos vizinhos.** Aumenta a estabilidade das contagens, mas dilui o choque pandêmico.
- **C. Excluir 2020–2021 da análise principal.** Evita que a pandemia domine a comparação, mas deixa de responder sobre toda a série; deve aparecer apenas como sensibilidade.

**Recomendação: A.** Manter também 2022–2024 separado. A classificação de COVID deve seguir a regra já auditada no projeto: U07.1/U07.2 e B34.2 somente quando acompanhado do marcador U07.1/U07.2. Não misturar silenciosamente COVID com outras infecciosas.

### 6. Como tratar a mortalidade na idade zero?

- **A. Usar nascidos vivos do SINASC como denominador (recomendação, se a cobertura e a compatibilidade forem adequadas).** É o denominador epidemiologicamente apropriado para a mortalidade infantil. A taxa deve ser convertida de modo coerente para a tábua; não pode ser tratada como se fosse uma taxa baseada em pessoas-ano da população estimada.
- **B. Excluir a idade zero da H10 principal.** É mais seguro se não for possível compatibilizar nascidos vivos, óbitos, território e período. A interpretação passa a ser sobrevivência condicional a ter chegado à idade de um ano, e não e₀–₈₀ desde o nascimento.
- **C. Manter a população estimada de idade zero.** Facilita a comparabilidade com a base atual, mas pode distorcer a taxa infantil e, por consequência, a esperança de vida desde o nascimento. Não recomendo como resultado principal.

**Recomendação: A somente após validar o SINASC e a compatibilidade territorial e temporal; se isso não for possível, B.** Não usar C como solução automática.

## O que há de novo — e o que não há

A decomposição da variância territorial da esperança de vida por idade e causa já tem precedente direto em Vierboom, Preston e Hendi (2019), que substituíram taxas locais por nacionais em sequência. Portanto, a ideia geral não é inédita. O uso de Shapley oferece uma atribuição simétrica das interações entre causas, sem depender de uma única ordem de substituição. A aplicação às 558 microrregiões, ao painel 2000–2024 e às sensibilidades explícitas para SIM, intenção indeterminada, pandemia e idade zero pode formar uma contribuição específica — mas isso precisa ser demonstrado, não presumido.

A proposta também deve dialogar com Calazans, Guimarães e Nepomuceno (2023), Monteiro da Silva et al. (2026) e Baptista, Queiroz e Pinheiro (2021), que já estudaram contribuições por idade/causa ou padrões regionais brasileiros; e com Nau e Firebaugh (2012), cuja decomposição trata da variância individual da idade à morte, objeto diferente da variância territorial de e₀–₈₀. Lima et al. (2024) é referência central para discutir qualidade do SIM nas 558 microrregiões.

**Decisão final:** Vladimir aprova ou altera cada escolha acima. Só depois disso Claude executará a análise com dados reais no computador local. Até lá, este documento é uma proposta de método, não um resultado.
