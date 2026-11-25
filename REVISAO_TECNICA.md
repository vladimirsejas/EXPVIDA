# Revisão técnica das análises de divergência por idade

Documento de 24/11/2026. Complementa RESULTADOS_DIVERGENCIA.md. Tudo o que está aqui pode ser conferido nos arquivos CSV e nos scripts que acompanham. Nada foi enviado ao GitHub e nenhum arquivo original do EXPVIDA foi alterado.

## 1. Correção da afirmação "as três hipóteses foram confirmadas"

A afirmação foi exagerada. A classificação correta está na tabela abaixo.

| Hipótese | Classificação | Base |
|---|---|---|
| H2: desigualdade dos homens maior em 15 a 29 anos | Estatisticamente significativa e robusta | Razão de τ 1,49 (IC 95% 1,31 a 1,70) contra 1 a 14 e 2,46 (2,25 a 2,70) contra 30 a 59 em 2015-2019; positiva nos seis períodos; sobrevive a Holm (30 testes) e a dois outros agrupamentos de faixas |
| H3: o padrão por idade difere entre os sexos | Significativa quanto à diferença dos perfis; evidência parcial quanto ao pico feminino na infância | Wald p de 10⁻²¹ a 10⁻⁵⁷; pico masculino em 15 a 29 nos seis períodos; pico feminino em 1 a 14 em cinco períodos, em 80 e mais em 2000-2004 |
| H1: parte da desigualdade já existe no primeiro ano | Evidência parcial | τ da faixa 0 > 0 em todos os casos (resultado trivial com muitos óbitos); participação de 6,7% (homens) e 14,1% (mulheres) na variância da e0-80; mas o τ inclui erro de registro e de população, que estes dados não separam |
| Ainda não demonstrado | A origem causal de qualquer um dos padrões; que τ seja só mortalidade "real"; que a IMD seja superior à IDT; qualquer ineditismo | |

## 2. Testes estatísticos: métodos, valores, intervalos e limitações

Modelo comum. Em cada faixa de idade, sexo e período, os óbitos da microrregião i seguem Poisson com média E_i · exp(μ + u_i), onde E_i são os óbitos esperados pela taxa do resto do Brasil (a própria microrregião é excluída do cálculo, "leave-one-out"), μ é um nível comum e u_i ~ Normal(0, τ²). O parâmetro τ é o desvio-padrão entre microrregiões do logaritmo da razão de risco depois de retirado o acaso de Poisson. A verossimilhança marginal é calculada por quadratura de Gauss-Hermite adaptativa (15 nós, moda de Newton por unidade) e maximizada por L-BFGS-B em (μ, log τ). O intervalo de confiança de τ é por verossimilhança perfilada (raiz por brentq). O que τ mede: toda variação sistemática além do acaso, incluindo erros de registro de óbitos e de estimativa da população. Validação por simulação: com τ verdadeiro de 0; 0,05; 0,2; 0,5 o modelo recuperou 0,001; 0,055; 0,194; 0,461.

Os testes usam seis faixas agrupadas (0; 1 a 14; 15 a 29; 30 a 59; 60 a 79; 80 e mais), padronização indireta dentro da faixa, e bootstrap em conglomerados de microrregiões, pareado entre as faixas e os sexos (1000 repetições em 2015-2019 e 300 nos outros períodos; semente 20261124).

H1a. Teste de razão de verossimilhança de τ = 0 na faixa 0, com mistura 0,5·χ²₁ (τ no limite do espaço paramétrico). Em 2015-2019: τ = 0,201 (IC 0,184 a 0,216) nos homens e 0,186 (0,167 a 0,204) nas mulheres. Estatística de 9.693 e 6.333 em 2000-2004; p tão pequeno que o programa arredonda para zero. Limitação: com milhares de óbitos o teste rejeita τ = 0 para qualquer erro sistemático mínimo; o p quase nada informa, o tamanho é que importa.

H1b. Participação de cada faixa na variância da expectativa de vida temporária entre 0 e 80 anos (e0-80), pela decomposição de Arriaga (as contribuições somam exatamente a diferença em relação ao Brasil, verificado com erro de 10⁻¹⁴) e participação por covariância cov(c_a, Σc)/var(Σc). Em 2015-2019, a faixa 0 contribui com 6,7% nos homens (IC 5,2 a 8,3%) e 14,1% nas mulheres (11,5 a 16,8%); entre períodos, 4,7% a 9,6% nos homens e 8,1% a 16,7% nas mulheres. Limitações: e0-80 é truncada em 80 anos; a decomposição é descritiva e depende da escala escolhida (variância); o denominador da faixa 0 é a população estimada, não os nascidos vivos.

H2. Razões τ(15-29)/τ(1-14) e τ(15-29)/τ(30-59) para os homens, com IC percentil do bootstrap pareado; valor-p analítico pela aproximação normal do logaritmo da razão (erro-padrão tirado da largura do IC). Tabela por período em RESULTADOS_DIVERGENCIA.md. 2015-2019: 1,49 (1,31 a 1,70) e 2,46 (2,25 a 2,70). Pandemia: 1,13 (1,01 a 1,28), p ajustado de Holm 0,041, o resultado mais frágil dos 30. Limitações: depende de como as faixas são agrupadas (ver seção 5); resultado ecológico e de todas as causas.

H3. Teste de Wald de que os perfis de log τ por faixa são paralelos entre homens e mulheres (contrastes em relação à primeira faixa, 5 graus de liberdade, covariância por bootstrap). Estatística de 104 a 274 e p de 3,7·10⁻²¹ a 3,2·10⁻⁵⁷. Complemento: probabilidade de a faixa de pico coincidir nos dois sexos no bootstrap (no máximo 2%). Limitação: o Wald com covariância de bootstrap em 300 repetições (cinco períodos) tem uma matriz estimada com ruído; por isso foi conferido com agrupamentos alternativos (seção 5), que deram p da ordem de 10⁻⁴³ a 10⁻⁴⁵.

Múltiplos testes. Os 30 testes (H1a x 12, H2 x 12, H3 x 6, contados por sexo e contraste) foram corrigidos por Holm com valores-p analíticos (primeira versão usava p de bootstrap, com resolução 1/B, e era artificialmente estrita; foi substituída). Resultado: os 30 sobrevivem a 5% (TESTES_HIPOTESES_HOLM.csv).

## 3. Definição matemática da IMD e o que ela mede

Para uma microrregião e um sexo, seja e0-80 a expectativa de vida temporária entre 0 e 80 anos calculada da tábua de vida (a mesma de piloto_expectativa.py: Coale-Demeny para a0 e a1, intervalo aberto 80+ como l/m). Seja G = e0-80(microrregião) − e0-80(Brasil). A decomposição de Arriaga escreve G = Σ_a c_a, em que c_a é a contribuição, em anos de vida, da faixa de idade a (efeito direto mais efeito indireto na sobrevivência). Definindo o acumulado relativo S_k = (Σ_{a ≤ k} c_a) / G, a

IMD = idade de início da primeira faixa k em que S_k ≥ 0,5.

A IMD só é definida se (i) o valor-p de G (normal, com erro-padrão de 200 sorteios de Poisson dos óbitos, população fixa) tem q < 0,05 por Benjamini-Hochberg sobre as 558 microrregiões e (ii) |G| ≥ 0,3 ano. O intervalo de confiança vem dos percentis 2,5 e 97,5 da IMD calculada nos sorteios com o mesmo sinal de G.

O que mede: a idade até a qual já se formou metade da diferença total de anos de vida em relação ao Brasil. É um resumo do centro de massa da diferença ao longo da idade. O que não mede: a idade em que a diferença começa. IMD_SEM_RUIDO.csv (imd_sem_ruido.py) mostra isso: se a mortalidade sobe por um fator constante (RR 1,4 ou 1,2) a partir de 15, 40 ou 60 anos, a IMD exata, sem nenhum ruído, vale 50, 60 e 65 nos homens (55, 60 e 65 nas mulheres). Ou seja, a IMD é sempre maior que a idade de início, e um RR constante a partir dos 15 anos já rende IMD de 50 ou 55.

## 4. A IMD é superior à IDT? Não foi demonstrado

A IDT (idt_experimento.py) estima a idade de início: primeira sequência de pelo menos 2 faixas consecutivas, no mesmo sentido, com teste exato de Poisson aprovado por BH-FDR 5% (558 × 18 testes por sexo e período) e RR ≥ 1,2 (ou ≤ 1/1,2). A IMD e a IDT têm estimandos diferentes, então "melhor" só tem sentido para critérios específicos. O que os dados mostram:

Falsos positivos: IDT, 0 microrregião em 200 simulações sem divergência; IMD, 0,25 (homens) e 0,20 (mulheres) microrregião por simulação de 558 (a primeira versão sem FDR marcava cerca de 6%).

Detecção com RR 1,4 (2015-2019): IDT 97% a 100% nos homens e 91% a 100% nas mulheres; IMD 85% a 100% e 81% a 100%. Com RR 1,2: IDT 43% a 94% (homens) e 27% a 86% (mulheres); IMD 32% a 100% e 26% a 100%; a IMD vai melhor em microrregiões pequenas e médias quando a diferença começa aos 15 ou 40 anos, e pior quando começa aos 60 (por exemplo, homens, RR 1,2, 15 anos, pequenas: 98% contra 66%; 60 anos, pequenas: 32% contra 43%).

Erro: o erro da IDT é medido contra a idade verdadeira de início (mediana de 0 a 5 anos com RR 1,4; de 5 a 50 anos de atraso com RR 1,2). O erro da IMD é medido contra a própria IMD sem ruído (95% a 100% dentro de 5 anos com RR 1,4); os dois erros não são comparáveis.

Reprodutibilidade entre períodos: IDT, Spearman 0,72 a 0,80, kappa de ter ou não a medida 0,52 a 0,65, mesma faixa ou vizinha 46% a 69%, mesma faixa exata 30% a 37%; IMD, Spearman 0,69 a 0,78, kappa 0,25 a 0,44, mesma faixa ou vizinha 66% a 70%, mesma faixa exata 29% a 37%. A IMD não é mais reprodutível em Spearman nem em kappa.

Cobertura nos dados reais (2015-2019): IDT presente em 178 de 558 (32%) microrregiões nos homens e 72 (13%) nas mulheres; IMD definida em 387 (69%) e 287 (51%). Isso é sinal de que a IMD pede menos (só G significativo), não de que seja mais precisa.

Conclusão. A IMD é uma medida complementar, útil para resumir e comparar quando a IDT não existe. Ela não substitui a IDT, e nenhum dos dois é um indicador consolidado.

## 5. Sensibilidade e reprodutibilidade

Reprodutibilidade computacional. Todos os sorteios usam a semente 20261124. Duas execuções completas dos 20 CSV produzem arquivos idênticos (md5 igual). O mesmo vale para SENSIBILIDADE_FAIXAS.csv e TESTES_HIPOTESES_HOLM.csv.

Reprodução do que já existia. As taxas por idade passadas pela tábua de vida do projeto reproduzem as expectativas já publicadas com diferença máxima de 0,00005 ano; óbitos e pessoas-ano coincidem exatamente.

Erro de população (hipotético, 2% e 5% por microrregião): em 2015-2019 reduz τ em cerca de 0,01 no máximo (por exemplo aos 80+ nos homens, de 0,123 para 0,112). Exclusão de microrregiões com menos de 500 óbitos: τ praticamente igual. Unidade territorial: com UF como unidade o τ cai bastante (homens, 15 a 19 anos: 0,29 contra 0,41). Tabela por idade em DIVERGENCIA_SENSIBILIDADE.csv (e em RESULTADOS_DIVERGENCIA.md).

Agrupamento das faixas (SENSIBILIDADE_FAIXAS.csv, 2015-2019, 300 repetições): no agrupamento B, τ(10-24)/τ(1-9) = 1,41 (1,22 a 1,61), τ(10-24)/τ(25-44) = 1,64 (1,53 a 1,73), Wald 221,5 (6 gl), p = 5,0·10⁻⁴⁵; no agrupamento C, τ(15-24)/τ(1-14) = 1,61 (1,40 a 1,81), τ(15-24)/τ(25-34) = 1,35 (1,27 a 1,41), Wald 215,1, p = 1,2·10⁻⁴³. A conclusão de H2 e H3 não depende do agrupamento.

Estabilidade entre períodos (correlação de Pearson das estimativas por microrregião, 2010-2014 contra 2015-2019): homens 0,66 a 0,87 de 15 anos em diante; mulheres 0,35 a 0,86; infância 0,34 a 0,66 (DIVERGENCIA_ESTABILIDADE.csv).

Limitações que a sensibilidade não resolve: sub-registro de óbitos (o τ acima de 45 anos em 2000-2004 chegou a 0,25 a 0,31 nos homens contra 0,12 a 0,16 em 2015-2019, compatível com melhora do registro e com convergência real); denominador da faixa 0; unidade ecológica; todas as causas somadas.

## 6. Validação posterior (25/11/2026): dependência espacial, normalidade, simulações e influência

Detalhes e tabelas estão em RESULTADOS_DIVERGENCIA.md, seção "Validação do modelo e correção dos intervalos". Em resumo, e corrigindo as seções 1 a 5 onde for o caso: (i) a dependência espacial é forte (Moran de 0,33 a 0,65; os estados explicam de 26% a 57% da variação) e o bootstrap por microrregiões soltas subestimava a incerteza: com blocos de estados os intervalos ficam de 1,7 a 2,6 vezes mais largos e os valores-p extremos (10⁻⁵⁷) são otimistas; (ii) o estimador de τ é pouco enviesado (−7% a +4% nas simulações) e as razões de H2 são estáveis com efeitos t de Student; (iii) a cobertura dos intervalos do modelo para τ populacional cai para 23% a 73% com dependência espacial ou efeitos não normais, mas se mantém em 79% a 100% para o desvio-padrão das próprias 558 microrregiões; (iv) retirar qualquer microrregião ou estado não altera as conclusões (pior caso: sem São Paulo, razão de 2,14); (v) com intervalos corrigidos, H2 contra 30 a 59 anos vale nos seis períodos, H2 contra 1 a 14 anos não vale na pandemia e fica no limite em 2022-2024, H3 vale em todos os períodos quanto à diferença dos perfis, e a forma dos picos é segura a partir de 2005 (homens) e 2010 (mulheres). A classificação da seção 1 passa a ser: H2 significativa e robusta (contra 30 a 59 em todos os períodos; contra 1 a 14 até 2019); H3 significativa quanto à diferença dos perfis e parcial quanto ao pico feminino; H1 sem alteração (evidência parcial). A sentença "Wald p de 10⁻²¹ a 10⁻⁵⁷" da seção 2 deve ser lida com esta correção. A diferença homens menos mulheres concentra-se em 15 a 44 anos, com maior valor aos 15 a 19 (0,22; IC 0,15 a 0,27); o excesso feminino na infância é pequeno (−0,04 aos 1 a 4 anos) e não está estabelecido na faixa de 1 a 14.

## 7. Quadro de integração com o repositório

Nada foi integrado. Em relação ao commit original 600b594, o conjunto de alterações só adiciona arquivos novos. O diff completo está em DIFF_COMPLETO.patch e a lista de arquivos em DIFF_ARQUIVOS.txt. O LEIAME.md original não foi alterado; o texto que se sugeriria acrescentar está em LEIAME_proposta.diff, só como proposta para você decidir.
