# Especificação metodológica — H1 adulta e cronologia τ × homicídios
**EXPVIDA | 27/11/2026**  
**Status:** proposta metodológica para decisão de Vladimir e execução local por Claude. Não foram executadas análises novas nem produzidos resultados com dados reais.

## 1. Escopo e sequência

Depois da H10, ficam propostas duas etapas complementares:

1. **H1 — compressão adulta:** testar se a heterogeneidade territorial da sobrevivência/mortalidade se concentra mais nas idades adultas jovens, especialmente 15–44 anos, ao longo dos seis períodos e por sexo.
2. **Cronologia τ × homicídios:** testar se a elevação da heterogeneidade territorial dos riscos masculinos jovens acompanha, no tempo e no território, a onda de homicídios, e se a associação é robusta aos cenários de reclassificação de 0%, 50% e 100% da intenção indeterminada como agressão.

As etapas não devem fundir estimandos. τ é a dispersão dos efeitos territoriais do risco na escala logarítmica. A decomposição de Arriaga reparte diferenças de expectativa de vida por idade. A taxa de homicídios mede eventos de violência. Uma correlação entre essas medidas não demonstra causalidade.

---

# PARTE I — H1: compressão da heterogeneidade na idade adulta jovem

## 2. Pergunta e hipótese

**Pergunta:** entre 2000 e 2024, a heterogeneidade territorial da mortalidade se concentrou progressivamente nas idades adultas jovens, em especial entre 15 e 44 anos? A concentração é semelhante entre homens e mulheres?

**Hipótese operacional H1-adulta:** a participação das idades de 15–44 anos na área sob o perfil etário de τ e na variância territorial da diferença de e0–80 aumenta ao longo dos seis períodos, com concentração mais intensa entre homens.

A hipótese é descritiva. Não significa que a desigualdade individual de sobrevivência tenha sido causada por um fator específico.

## 3. Dados de entrada do repositório

- `DIVERGENCIA_POR_IDADE.csv`: estimativas de τ, IC, número de óbitos e período, por sexo e idade. É a fonte principal do perfil etário.
- `BRASIL_taxas_por_idade.csv`: óbitos e pessoas-ano por microrregião, sexo, idade e período; permite reconstruir tábuas e taxas de referência.
- `divergencia_modelo.py`: funções `carregar`, `esperados`, `ajustar`, `tabua_lx`, `arriaga_e0_80`, `tabua_vec` e `arriaga_vec`.
- `arriaga_territorial.py`: implementação já existente da decomposição de Arriaga com riscos territoriais suavizados pelo modelo Poisson-lognormal. A versão atual usa como padrão 2015–2019; Claude deverá generalizar a rotina aos seis períodos sem alterar o significado das funções.
- `MUNICIPIO_MICRORREGIAO.csv` e `tabela_municipio_microrregiao.py`: tabela municipal usada pelo projeto para construir o universo territorial; não criar outra tabela de correspondência.
- `RESULTADOS_DIVERGENCIA.md`, `REVISAO_TECNICA.md` e `SENSIBILIDADE_FAIXAS.csv`: documentação dos testes anteriores, agrupamentos e sensibilidades.

## 4. Cálculo A — concentração de τ por idade

A base principal já apresenta τ por faixas quinquenais e seis períodos. Para cada sexo (s), período (p) e faixa etária (a), usar (tau_{s,p,a}) de `DIVERGENCIA_POR_IDADE.csv`.

Definir a área ponderada do perfil etário:

```
A_s,p(B) = soma, para cada idade a em B, de [largura_a * tau_s,p,a]
P_tau_15-44,s,p = A_s,p(15-44) / A_s,p(0-79)
R_tau_s,p = A_s,p(15-44) / [A_s,p(0-14) + A_s,p(45-79)]
```

A ponderação pela largura evita somar uma faixa de um ano com uma faixa de cinco anos como se representassem a mesma extensão de idade. Essa participação é um resumo descritivo da área sob o perfil de τ; não é parcela causal nem decomposição aditiva de τ.

Além do agregado 15–44, apresentar 15–29 e 30–44 separadamente. Isso impede que a escolha do limite de idade esconda o pico de 15–29 ou um deslocamento para 30–44.

## 5. Cálculo B — contribuição de Arriaga para a dispersão territorial de e0–80

O cálculo de τ não substitui a decomposição da sobrevivência. Para cada período e sexo:

1. Construir a tábua de referência Brasil com os óbitos e pessoas-ano agregados das 558 microrregiões, usando as mesmas convenções de `divergencia_modelo.py`.
2. Para cada microrregião, estimar as taxas suavizadas por idade: taxa do restante do Brasil na idade correspondente multiplicada por (exp(mu+u_i)), com (mu) e (u_i) do modelo Poisson-lognormal.
3. Construir a tábua territorial e calcular (e_{0-80,i}).
4. Usar a função existente `arriaga_vec` (ou `arriaga_e0_80` em uma execução unitária) para obter (c_{i,a}), a contribuição em anos de vida da faixa etária (a) para (G_i=e_{0-80,i}-e_{0-80,Brasil}).
5. Para cada faixa ou conjunto (B), somar (c_{i,B}=sum_{ain B}c_{i,a}).
6. Calcular a participação por covariância:

```
P_Arriaga_B = Cov_i(c_i,B, G_i) / Var_i(G_i)
G_i = soma, para todas as idades a, de c_i,a
```

A soma das participações por idade deve ser 1, salvo erro numérico. Contribuições negativas são possíveis e devem permanecer visíveis; não truncar valores negativos para zero. O procedimento corresponde à lógica já documentada em `REVISAO_TECNICA.md` e implementada no campo `parte_da_variancia_de_e0` de `arriaga_territorial.py`.

Calcular (P^A_{15-44}), (P^A_{15-29}) e (P^A_{30-44}) para cada sexo e período. Se (operatorname{Var}(G_i)=0) ou houver tábuas não calculáveis, registrar como não estimável e explicar a regra; não substituir por zero.

## 6. Inferência e sensibilidades da H1-adulta

- Usar bootstrap pareado em blocos de UF, mantendo os mesmos sorteios entre idades, sexos e períodos, em coerência com a validação espacial do EXPVIDA.
- Em cada replicação, reconstruir as estimativas necessárias a τ e à decomposição de Arriaga; não tratar os τ pontuais já publicados como se fossem observações independentes.
- Com 27 UFs, reconhecer a limitação do número de blocos. Reportar número de replicações válidas e falhas.
- Apresentar estimativas pontuais e IC95% para (P^tau_{15-44}), (R^tau), (P^A_{15-44}) e contrastes entre períodos.
- Como há apenas seis períodos, não usar uma regressão temporal com aparência de grande precisão. Mostrar trajetória e diferenças entre períodos, com inferência por bootstrap pareado.
- Sensibilidades obrigatórias: 15–29 versus 15–44; 15–39 versus 15–44; homens e mulheres separadamente; painel fixo das 558 microrregiões; ponderação territorial igual (principal) versus ponderação por população (secundária); excluir idade zero da tábua como sensibilidade; resultados sem pandemia (comparar períodos ordinários) e com 2020–2021 isolado; taxas observadas versus taxas suavizadas quando metodologicamente comparáveis.
- A análise de idade zero precisa respeitar a especificação SINASC, se aprovada e validada. Até lá, manter explícito que a primeira faixa usa o denominador anterior e não misturar as versões.

## 7. Resultados esperados — formato de tabela e figura

**Tabela H1-A — concentração de τ**
- Linhas: sexo × período.
- Colunas: (A(15–44)), (A(0–79)), (P^tau_{15–44}), (R^tau), (P^tau_{15–29}), (P^tau_{30–44}), IC95%.

**Tabela H1-B — contribuição Arriaga**
- Linhas: sexo × período.
- Colunas: (P^A_{15–44}), (P^A_{15–29}), (P^A_{30–44}), soma das contribuições por idade, erro de fechamento.

**Figura H1-1:** dois painéis (homens e mulheres), perfil de τ por idade e período, com linhas separadas para os seis períodos e sem transformar os valores em taxas de mortalidade.

**Figura H1-2:** trajetória das participações (P^tau_{15–44}) e (P^A_{15–44}) nos seis períodos, com IC95% quando disponíveis. As duas curvas devem ficar visualmente separadas porque os estimandos são diferentes.

## 8. O que confirmaria ou refutaria H1-adulta

**Evidência favorável:**
- (P^tau_{15–44}) e/ou (R^tau) aumentam nos períodos mais recentes em comparação com os primeiros, com diferenças que não sejam explicadas apenas pela pandemia;
- a contribuição de Arriaga (P^A_{15–44}) também cresce ou permanece elevada, mostrando que a concentração não aparece apenas na dispersão de riscos;
- o padrão se mantém nas sensibilidades de faixa etária e no painel territorial fixo;
- a concentração masculina é maior ou mais persistente que a feminina, se essa parte da hipótese for mantida.

**Evidência contrária ou insuficiente:**
- a participação de 15–44 fica estável ou diminui;
- o aumento existe apenas em 15–29, mas não no agregado 15–44, contrariando a formulação ampla;
- a concentração desaparece ao retirar 2020–2021 ou ao mudar discretamente os limites das faixas;
- τ indica concentração, mas Arriaga não mostra participação correspondente na diferença de sobrevivência. Nesse caso, relatar que a heterogeneidade dos riscos e a contribuição à dispersão de e0–80 não convergem, sem forçar uma conclusão única.

---

# PARTE II — Cronologia τ × homicídios

## 9. Pergunta e hipótese

**Pergunta:** o aumento ou a persistência de τ nas idades masculinas jovens acompanha, no tempo e no território, a onda de homicídios registrada nas microrregiões brasileiras?

**Hipótese:** microrregiões e períodos com taxas mais elevadas de homicídios entre homens jovens tendem a apresentar efeitos territoriais mais elevados para o risco de morte masculino nas idades jovens, e a associação permanece qualitativamente semelhante quando 0%, 50% ou 100% dos óbitos por intenção indeterminada são reclassificados como agressões.

A hipótese não afirma que os homicídios expliquem integralmente τ. A mortalidade geral inclui muitas causas, e τ não é aditivo por causa.

## 10. Dados de entrada do repositório

- `VIOLENCIA_MICRO_ANUAL.csv`: painel anual por microrregião, com população, população masculina 15–29, homicídios, homicídios por arma de fogo, homicídios masculinos 15–29, taxa anual e média móvel de três anos.
- `VIOLENCIA_ANUAL_MUNICIPIO.csv`: base municipal anual de óbitos violentos, por sexo, idade e causa; é a entrada para reconstruir cenários de agressões/intenção indeterminada no nível municipal e depois microrregional.
- `BRASIL_taxas_por_idade.csv`: óbitos e pessoas-ano nas seis janelas, por microrregião, sexo e idade.
- `DIVERGENCIA_POR_IDADE.csv`: τ por idade, sexo e período, para os seis períodos.
- `CAUSAS_TEMPORAL.csv` e `CAUSAS_TAU.csv`: resultados existentes por causa e período, úteis como comparação e diagnóstico, não como substitutos do painel territorial.
- `causas_temporal.py`, `causas_tau.py`, `analise_violencia.py` e `divergencia_modelo.py`: regras existentes de estimação e agregação.
- `MUNICIPIO_MICRORREGIAO.csv` e `POP_MUNICIPIO.csv`: geografia e denominadores usados pelo projeto.
- `HOMICIDIO_LOCAL_REGIAO.csv`: descrição complementar do local de ocorrência por região e ano; não é a medida principal de exposição territorial.

A base `VIOLENCIA_MICRO_ANUAL.csv` atual já contém homicídios masculinos 15–29 (`homic_h1529`) e população masculina 15–29 (`pop_h1529`). Não contém, por si só, uma medida masculina 15–44. Para a análise principal proposta, manter 15–29 como faixa diretamente compatível com o arquivo atual; 15–44 exigirá reconstrução dos numeradores e denominadores nessa faixa.

**Atenção à definição do arquivo existente:** `analise_violencia.py` define `HOMIC` como agressões por arma de fogo, arma branca, outros meios **e intervenção legal** (Y35–Y36). Assim, as colunas `homic` e `homic_h1529` de `VIOLENCIA_MICRO_ANUAL.csv` não são automaticamente idênticas ao cenário A = agressões X85–Y09 usado nesta especificação; além disso, o arquivo não incorpora intenção indeterminada Y10–Y34. Para os três cenários comparáveis, reconstruir os numeradores a partir de `VIOLENCIA_ANUAL_MUNICIPIO.csv`, mantendo intervenção legal em coluna separada. Usar as taxas prontas de `VIOLENCIA_MICRO_ANUAL.csv` somente como conferência da série de homicídios conforme a definição daquele script.

## 11. Unidade de análise e cuidado com τ

O parâmetro τ é um único resumo da dispersão territorial para cada combinação sexo × idade × período; ele não é um valor de τ individual para cada microrregião. Portanto:

- **Não** correlacionar um τ nacional único com centenas de taxas microrregionais como se τ fosse uma variável territorial.
- Para a associação territorial, usar os efeitos territoriais (u_i) (modas dos efeitos aleatórios) devolvidos por `divergencia_modelo.ajustar`, por microrregião, idade, sexo e período.
- Usar τ como resumo temporal da intensidade global da heterogeneidade e (u_i) como medida territorial relativa para a análise de correspondência com homicídios.
- A interpretação de (u_i) deve reconhecer que são estimativas com shrinkage e incerteza; não tratá-las como riscos observados sem erro.

## 12. Construção dos três cenários de intenção indeterminada

Construir, por município, ano, sexo e faixa etária, três numeradores de violência:

```
H_0   = A
H_50  = A + 0,5*I
H_100 = A + I
```

A é o número de óbitos por agressões (CID-10 X85–Y09, segundo o classificador do projeto) e I é o número de óbitos por intenção indeterminada (Y10–Y34). A intervenção legal (Y35–Y36) deve permanecer identificada separadamente no cálculo principal; não incorporá-la silenciosamente a A. Se a análise de blindagem anterior tiver uma convenção distinta para intervenção legal, reproduzi-la como cenário adicional documentado.

Agregar cada cenário com a mesma tabela município–microrregião e dividir pela população masculina de 15–29 anos (ou pela faixa de idade correspondente) para obter taxa por 100 mil pessoas-ano:

```
R_homicide_i,t,z = 100000 * H_i,t,z / PY_male_young_i,t
z in {0, 50, 100}
```

A população anual atual de `VIOLENCIA_MICRO_ANUAL.csv` é construída a partir de médias das populações dos períodos do projeto. Para a análise anual, conferir se essa aproximação anual é aceitável. Se houver população municipal anual observada/estimada em outra fonte local, documentar a escolha; não tratar uma população de período repetida em cada ano como observação anual independente sem ressalva.

A classificação de agressões e intenção indeterminada deve usar causa básica e os grupos do classificador do projeto. Não inferir que uma morte indeterminada foi homicídio; os três cenários são limites hipotéticos de sensibilidade, não uma reclassificação factual dos registros.

## 13. Cálculo temporal e territorial

### 13.1 Análise principal por seis períodos

Para cada período e cenário:

1. Agregar homicídios masculinos jovens e denominadores anuais em cada microrregião; calcular taxa média do período como soma dos eventos dividida pela soma das pessoas-ano, multiplicada por 100 mil.
2. Estimar o modelo Poisson-lognormal de mortalidade geral masculina para as faixas 15–19, 20–24 e 25–29 (e, como agregado secundário, 15–29), usando `divergencia_modelo.esperados` e `divergencia_modelo.ajustar`.
3. Guardar (tau_{p,a}), IC e (u_{i,p,a}). A base de taxas por período já oferece τ agregado; os efeitos territoriais precisam ser recuperados ao ajustar novamente o modelo para cada combinação.
4. Relacionar (u_{i,p,a}) à taxa de homicídios (R^{(0)}, R^{(50)}, R^{(100)}) na mesma microrregião e período.
5. Estimar associação territorial com correlação de Spearman como descrição e regressão de painel com efeitos fixos de período e erros agrupados por UF ou bootstrap por blocos de UF. A forma final deve ser escolhida antes de olhar os resultados.
6. Parear os mesmos sorteios de UFs entre os três cenários de intenção indeterminada, faixas etárias e períodos.

O contraste principal é a associação entre a taxa de homicídios e o efeito territorial (u_i) da mortalidade geral masculina jovem. O τ de cada período é apresentado como trajetória paralela de heterogeneidade agregada, não como desfecho territorial da regressão.

### 13.2 Análise anual — extensão condicionada à disponibilidade

A onda de homicídios já está disponível anualmente em `VIOLENCIA_MICRO_ANUAL.csv`. Entretanto, o painel `BRASIL_taxas_por_idade.csv` está agregado nos seis períodos, não em anos civis. Para uma cronologia anual genuína de τ, Claude precisará reconstruir matrizes anuais de óbitos SIM e pessoas-ano por microrregião, sexo e idade a partir das fontes anuais que geraram os arquivos do projeto.

Se os arquivos anuais não estiverem disponíveis no computador, **não interpolar τ entre os seis períodos**. Nesse caso, a análise principal permanece em seis períodos, e a curva anual de homicídios aparece apenas como contexto descritivo, sem atribuir valores anuais de τ.

## 14. Resultados esperados — tabelas e figuras

**Tabela HT-1 — evolução temporal**
- Linhas: período × cenário de intenção indeterminada.
- Colunas: τ geral masculino 15–29, τ 15–19, τ 20–24, τ 25–29, IC95%, taxa média de homicídios 15–29 por 100 mil e número de microrregiões.

**Tabela HT-2 — associação territorial**
- Linhas: período × cenário.
- Colunas: correlação Spearman entre (u_i) e taxa de homicídios, coeficiente da associação ajustada, IC95%, número de microrregiões e número de UFs.

**Figura HT-1:** linhas anuais das taxas de homicídios masculinos 15–29 por 100 mil, Brasil e grandes regiões, com os seis períodos destacados. Não desenhar τ anual se ele não tiver sido estimado anualmente.

**Figura HT-2:** gráficos de dispersão por período entre taxa de homicídios 15–29 e (u_i) masculino 15–29, com painel separado para cenários 0%, 50% e 100%. Identificar pontos como microrregiões apenas se a figura não expuser dados individuais; os dados são agregados territoriais.

**Figura HT-3:** trajetória de τ masculino 15–29 nos seis períodos, com IC95%, em painel separado das taxas de homicídios. O objetivo é comparar movimentos, não sugerir equivalência de escala.

## 15. O que confirmaria ou refutaria a hipótese

**Evidência favorável:**
- a elevação ou persistência de τ masculino 15–29 coincide temporalmente com períodos de maior taxa de homicídios;
- microrregiões com taxas de homicídios mais elevadas tendem a apresentar (u_i) mais alto na mortalidade geral masculina jovem;
- a associação territorial tem direção semelhante nos cenários 0%, 50% e 100%, embora sua magnitude possa variar;
- os resultados resistem a retirar uma UF por vez, controlar diferenças regionais e excluir microrregiões com contagens muito baixas.

**Evidência contrária ou insuficiente:**
- τ aumenta em períodos sem aumento correspondente de homicídios;
- a correlação territorial entre homicídios e (u_i) é nula, instável ou muda de sinal entre períodos;
- a associação só aparece quando 100% da intenção indeterminada é reclassificada como agressão;
- o resultado desaparece ao retirar uma UF ou poucas microrregiões influentes;
- a associação aparece em 15–29, mas não em 15–44; nesse caso, restringir a conclusão à faixa que foi efetivamente sustentada.

Mesmo que todos os padrões sejam favoráveis, a conclusão permitida é “acompanhamento temporal e associação territorial compatíveis”, não “homicídios causaram o aumento de τ”.

## 16. Sensibilidades obrigatórias

1. Intenção indeterminada: 0%, 50% e 100% como agressão.
2. Intervenção legal: manter separada; sensibilidade adicional apenas se a blindagem anterior a tiver incorporado.
3. Faixas: 15–19, 20–24, 25–29, agregado 15–29 e, se os dados permitirem, 15–44.
4. Homicídios: total por agressões, arma de fogo e homicídios masculinos jovens; não confundir local de ocorrência com residência.
5. Taxa: soma de óbitos/soma de pessoas-ano; comparar com a média das taxas anuais apenas como sensibilidade.
6. Defasagem temporal: homicídios no mesmo período e período anterior, sem procurar várias defasagens até encontrar significância.
7. Unidade: microrregiões do painel fixo de 558; análise por UF como robustez, não como substituição do estimando.
8. Influência: retirar uma UF por vez e microrregiões com maior influência.
9. Incerteza: bootstrap pareado por blocos de UF; reportar falhas e número de replicações.
10. Qualidade do SIM: manter a intenção indeterminada como grupo explícito e relatar mudanças de cobertura; os cenários de reclassificação não corrigem sub-registro.
11. Cronologia anual: só calcular τ anual se óbitos e exposições anuais forem reconstruídos. Não interpolar resultados quinquenais.

---

# PARTE III — Decisões do Vladimir

O formato abaixo replica a lógica do documento `DECISOES_METODO_H10_2026-11-27.md`: opções explícitas, recomendação e justificativa. Nenhuma decisão deve ser tomada automaticamente por Claude.

## Decisão do Vladimir 1 — Faixa etária principal da compressão adulta

- **A. 15–44 anos (recomendação).** Captura a idade adulta jovem ampliada e permite dividir 15–29 e 30–44.
- **B. 15–29 anos.** Mantém foco no pico masculino já observado, mas pode deixar de detectar deslocamento para 30–44.
- **C. 15–49 anos.** Amplia a janela e inclui 45–49, mas reduz a especificidade de “adulto jovem”.

**Recomendação: A.** Usar 15–44 como hipótese principal e 15–29 como análise focal secundária. Não alterar o intervalo após observar os resultados.

## Decisão do Vladimir 2 — Medida principal de concentração

- **A. Área ponderada de τ por idade + participação Arriaga (recomendação).** Duas medidas complementares: uma da heterogeneidade dos riscos e outra da contribuição das idades à variância territorial de e0–80.
- **B. Apenas τ.** Mais simples, mas não mostra se a concentração de risco se traduz em contribuição à desigualdade de sobrevivência.
- **C. Apenas Arriaga.** Mais próximo da pergunta de sobrevivência, mas perde a medida direta de heterogeneidade residual por idade.

**Recomendação: A.** Manter os estimandos separados e exigir convergência interpretativa antes de falar em “compressão da desigualdade de sobrevivência”.

## Decisão do Vladimir 3 — Unidade temporal da cronologia τ × homicídios

- **A. Seis períodos do projeto (recomendação principal).** Usa as janelas já calculadas e permite comparação direta com τ existente.
- **B. Série anual 2000–2024.** É mais informativa para cronologia, mas exige reconstruir óbitos e exposições anuais; não existe τ anual pronto nos arquivos agregados atuais.
- **C. Seis períodos como principal e série anual de homicídios apenas como contexto.** Evita uma falsa série anual de τ e mantém a análise reprodutível com os arquivos atuais.

**Recomendação: C.** Começar com os seis períodos. Só acrescentar B se Claude localizar e validar as bases anuais de SIM e POPSVS e conseguir reestimar τ por ano sem interpolação.

## Decisão do Vladimir 4 — Medida territorial para a associação com homicídios

- **A. Efeitos territoriais (u_i) do Poisson-lognormal (recomendação).** São a medida microrregional coerente com o modelo; τ permanece como resumo global de cada período.
- **B. Taxas brutas de mortalidade masculina jovem.** São transparentes, mas misturam heterogeneidade real e flutuação de contagem.
- **C. Razão τ causa-específico/τ geral.** Não recomendada como percentual explicado; τ não é aditivo e essa razão não mede contribuição causal.

**Recomendação: A.** Usar (u_i) para a correspondência territorial, com shrinkage e incerteza explicitados. B pode aparecer como sensibilidade descritiva. Não usar C como explicação da mortalidade geral.

## Decisão do Vladimir 5 — Tratamento da intenção indeterminada

- **A. 0%, 50% e 100% como cenários de sensibilidade (recomendação).** Mantém o registro original no cenário 0 e mostra os limites de reclassificação.
- **B. 50% como cenário principal.** Resume um cenário intermediário, mas pressupõe uma fração sem comprovação.
- **C. 100% como agressão.** É um limite extremo, não uma estimativa factual.

**Recomendação: A.** Não escolher um único percentual como verdade. Manter agressões e intenção indeterminada separadas na base original e apresentar os três cenários. Intervenção legal deve continuar separada, salvo decisão adicional expressa.

## Decisão do Vladimir 6 — Inferência e dependência espacial

- **A. Bootstrap pareado em blocos de UF (recomendação).** Preserva dependência geográfica aproximada e pareia os cenários e períodos.
- **B. Bootstrap de microrregiões independentes.** Mais simples, mas contradiz a validação espacial do EXPVIDA e tende a subestimar incerteza.
- **C. Erros-padrão robustos sem bootstrap.** Podem ser apresentados como sensibilidade, mas exigem especificação do modelo e não substituem a inferência por blocos.

**Recomendação: A.** Usar o mesmo sorteio de UFs para todos os cenários comparados. Reportar a limitação de apenas 27 blocos.

## Decisão do Vladimir 7 — Formulação científica permitida

- **A. “Associação temporal e territorial compatível com a onda de homicídios” (recomendação).** Descritiva, prudente e alinhada ao desenho ecológico.
- **B. “Homicídios explicam a desigualdade territorial.”** Excede o desenho e confunde τ geral com causa específica.
- **C. “Homicídios causam o aumento de τ.”** Afirmação causal não identificada por este estudo.

**Recomendação: A.** Mesmo que os resultados sejam consistentes, não usar linguagem causal sem desenho causal adicional.

## 17. Ordem de execução sugerida

1. Vladimir decide as sete escolhas acima.
2. Claude confirma que a branch e os arquivos locais correspondem ao commit de origem.
3. Claude reproduz os resultados existentes de τ e valida a tabela de entrada.
4. Claude implementa a extensão da decomposição de Arriaga aos seis períodos e executa os testes de fechamento.
5. Claude produz as tabelas e figuras da H1-adulta.
6. Claude monta os cenários de homicídios e intenção indeterminada, confere os fechamentos por município/microrregião e executa a associação territorial nos seis períodos.
7. Apenas se os arquivos anuais de SIM e POPSVS forem localizados e validados, Claude avalia a extensão anual.
8. Entregar tabelas, figuras, logs, parâmetros, sementes, falhas, versões dos dados e commit de origem para revisão independente.

**Regra de bloqueio:** não declarar H1-adulta confirmada, nem afirmar que homicídios acompanham ou explicam τ, antes da execução local, da inferência por blocos e da auditoria de qualidade dos dados. A especificação define o método; não antecipa resultados.
