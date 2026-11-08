# Resultados consolidados para o artigo — DogTech (V0–V10)

## 1 — Resultados estruturais

### Tabela consolidada

| Métrica | V0 | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 | V9 | V10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LOC | 91 | 397 | 664 | 1005 | 1213 | 1322 | 1527 | 1674 | 1866 | 2170 | 2533 |
| Complexidade ciclomática | 1 | 64 | 141 | 243 | 294 | 329 | 377 | 406 | 475 | 541 | 618 |
| WMC | 2,0 | 70,0 | 151,0 | 259,0 | 318,0 | 354,0 | 407,0 | 443,0 | 509,0 | 583,0 | 667,0 |
| CBO (média/classe) | 2,00 | 5,00 | 6,00 | 5,81 | 5,65 | 5,74 | 6,22 | 6,58 | 6,79 | 7,05 | 7,00 |
| LCOM (média/classe) | 0,00 | 11,44 | 75,67 | 81,05 | 67,00 | 67,59 | 58,38 | 59,24 | 69,00 | 60,09 | 51,60 |
| Complexidade cognitiva | 0 | 31 | 75 | 103 | 124 | 158 | 179 | 204 | 243 | 254 | 285 |
| Duplicação (%) | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 1,8 | 1,5 |
| Code smells | 0 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |

### Gráficos (`resultados/graficos/`)
- `01_loc.png` — LOC por versão.
- `02_complexidade.png` — Complexidade ciclomática, cognitiva e WMC por versão.
- `03_cbo_lcom.png` — CBO e LCOM (médias por classe) por versão.
- `04_duplicacao_smells.png` — Duplicação (%) e code smells por versão.

### Leitura rápida
LOC cresce ~28× (91→2533). Complexidade ciclomática/cognitiva/WMC crescem em
todas as 10 transições, sem exceção, mas a taxa percentual de crescimento
desacelera a partir de V2 (de +120% para a faixa de +8% a +20% por versão).
CBO permanece estável numa faixa estreita (5,65–7,05). LCOM sobe forte em
V1–V3 e depois tende a cair. Duplicação é 0% em 9 das 11 versões. Code smells
salta de 0 para 2 em V1 e nunca mais muda.

## 2 — Resultados funcionais

### Tabela consolidada

| Versão | Testes executados | Aprovados | Reprovados | Não executados | TA | Cobertura (JaCoCo, %) |
|---|---|---|---|---|---|---|
| V0 | 0 | 0 | 0 | 2 | Não calculável | 33,3 |
| V1 | 6 | 6 | 0 | 1 | 100,0% | 53,8 |
| V2 | 6 | 5 | 1 | 0 | 83,3% | 55,1 |
| V3 | 7 | 6 | 1 | 0 | 85,7% | 53,5 |
| V4 | 2 | 2 | 0 | 0 | 100,0% | 49,6 |
| V5 | 3 | 3 | 0 | 0 | 100,0% | 48,3 |
| V6 | 3 | 3 | 0 | 1 | 100,0% | 46,5 |
| V7 | 4 | 4 | 0 | 0 | 100,0% | 45,4 |
| V8 | 4 | 4 | 0 | 1 | 100,0% | 45,9 |
| V9 | 3 | 2 | 1 | 0 | 66,7% | 45,8 |
| V10 | 4 | 4 | 0 | 1 | 100,0% | 43,5 |

Gráfico: `resultados/graficos/05_testes_ta.png` (barras empilhadas de
aprovados/reprovados/não executados + linha de TA).

### Regressões identificadas
**Uma**, contida antes de ser committada: em I5, a introdução dos papéis
`DIRETOR_GERAL`/`GESTOR_ADOCAO` quebrou temporariamente o acesso
administrativo de I3/I4 (formulário de cadastro desatualizado). Corrigida na
mesma rodada de geração — a versão V5 final não contém a regressão. Nenhuma
versão committada apresentou funcionalidade anterior quebrada (confirmado por
teste de regressão manual em todas as 10 versões).

### Evolução da cobertura de testes
Cobertura (linhas, via JaCoCo/SonarQube) foi acompanhada como métrica
auxiliar (nunca como critério de aceite, por decisão registrada ao longo do
experimento): 33,3% (V0) → 53,8% (V1) → 55,1% (V2) → 53,5% (V3) → 49,6% (V4)
→ 48,3% (V5) → 46,5% (V6) → 45,4% (V7) → 45,9% (V8) → 45,8% (V9) → 43,5%
(V10). Diferente de LOC/complexidade, a cobertura **tende a cair** ao longo
do experimento (pico em V2, com queda quase monotônica depois) — o volume de
código novo por incremento cresceu mais rápido do que o volume de testes
JUnit escritos pelo Gemini para cobri-lo. É exatamente o caso prático que
justifica nunca usar cobertura como proxy de corretude (seção 7.4 do
protocolo): a TA permaneceu em 100% em varias dessas mesmas versões (V4–V8)
enquanto a cobertura caía de 49,6% para 45,4% — cobertura e corretude se
moveram em direções diferentes.

## 3 — Comparação entre V0 e V10 (variação total do experimento)

| Métrica | V0 | V10 | Δ absoluto | Δ% |
|---|---|---|---|---|
| LOC | 91 | 2533 | +2442 | +2683,5% |
| Complexidade ciclomática | 1 | 618 | +617 | +61700,0%* |
| WMC | 2,0 | 667,0 | +665,0 | +33250,0%* |
| CBO (média/classe) | 2,00 | 7,00 | +5,00 | +250,0% |
| LCOM (média/classe) | 0,00 | 51,60 | +51,60 | N/C (base=0) |
| Complexidade cognitiva | 0 | 285 | +285 | N/C (base=0) |
| Duplicação (%) | 0,0 | 1,5 | +1,5 | N/C (base=0) |
| Code smells | 0 | 2 | +2 | N/C (base=0) |
| TA | Não calculável | 100,0% | — | não aplicável |

\* Percentuais com base em V0 extremamente pequena (1 e 2, respectivamente);
informativos apenas no sentido de "o sistema foi de praticamente zero lógica
de negócio para um sistema funcional completo" — a leitura relevante é pelo
valor absoluto e pela trajetória versão-a-versão (seção 18.1), não por este
percentual isolado de ponta a ponta.

## 4 — Discussão

**O que aconteceu durante a evolução do DogTech.** Partindo de um esqueleto
sem nenhuma lógica de negócio (V0: 91 LOC, 2 classes triviais), o sistema foi
construído em 10 incrementos gerados pelo Gemini (`gemini-3.5-flash-lite`,
temperatura 0), cada um implementando um subconjunto fechado de requisitos do
documento original, chegando a V10 com 2533 LOC, 8 entidades de domínio e 12
controladores cobrindo autenticação, cadastro, gestão de animais, privilégios,
adoção (solicitação, avaliação, pós-adoção), apadrinhamento, eventos e
doações.

**Em quais incrementos ocorreram mudanças relevantes.** Três momentos se
destacam: (1) **I1**, onde a decisão inicial de formato de saída (unified
diff) teve que ser abandonada por falha estrutural repetida do modelo,
custando 11 chamadas à API para fechar a versão — o maior número do
experimento, por um motivo de protocolo, não de dificuldade do requisito em
si; (2) **I5**, onde a introdução de papéis reais (RF006) provocou uma
regressão real (contida antes do commit) e exigiu corrigir uma vulnerabilidade
de escalonamento de privilégio encontrada por teste manual — nenhum dos 17
testes JUnit escritos pelo próprio Gemini detectou essa falha; (3) **I8**,
onde um bug de regra de negócio real (RF009 — a menor nota entre avaliações
não prevalecia) também só foi detectado por verificação manual.

**Quais evidências sustentam as conclusões.** A conclusão central da análise
funcional (seção 15/16) — de que não há relação causal visível entre
crescimento estrutural e queda de corretude — se sustenta em cinco versões
consecutivas (V4–V8) em que complexidade cresceu continuamente e a TA
permaneceu em 100%, e nos dois únicos episódios de queda de TA (V2, V9), cuja
causa documentada foi sempre uma lacuna específica de implementação, nunca
uma consequência genérica do tamanho ou complexidade do sistema.

**Relação com as Leis de Lehman** (detalhe completo em
`resultados/interpretacao_lehman.md`): as Leis I (mudança contínua) e VI
(crescimento contínuo) se confirmam integralmente nesta trajetória. A Lei II
(complexidade crescente) se confirma para métricas de quantidade de decisões
(ciclomática, cognitiva, WMC), mas não para métricas de organização
(CBO/LCOM, que tiveram períodos reais de melhora). A Lei VII (declínio da
qualidade) **não se confirma como tendência** — os únicos sinais de
degradação observados foram pontuais, isolados e não-progressivos,
inclusive se recuperando na versão seguinte em todos os casos.

**Relação com o objetivo da pesquisa.** O objetivo era investigar como
qualidade estrutural e corretude evoluem ao longo de iterações de geração por
LLM. A resposta observada nesta trajetória específica é: a qualidade
estrutural (por métricas CK) cresceu de forma esperada e sem indícios de
deterioração acelerada, a corretude funcional se manteve majoritariamente
estável (8 das 10 versões com TA = 100% ou próxima disso), e os episódios de
falha identificados — tanto estruturais (a regressão de I5, o bug de I8)
quanto de completude (os 3 gaps aceitos) — foram sistematicamente capturáveis
por verificação manual independente dos testes do próprio modelo, reforçando
a importância metodológica de não depender só da suíte gerada pelo LLM para
avaliar corretude.
