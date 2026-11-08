# Análise da evolução V0 → V10 — DogTech

#### LOC (ncloc)

| Transição | Valor anterior | Valor atual | Δ | Δ% |
|---|---|---|---|---|
| V0→V1 | 91 | 397 | +306 | +336,3% |
| V1→V2 | 397 | 664 | +267 | +67,3% |
| V2→V3 | 664 | 1005 | +341 | +51,4% |
| V3→V4 | 1005 | 1213 | +208 | +20,7% |
| V4→V5 | 1213 | 1322 | +109 | +9,0% |
| V5→V6 | 1322 | 1527 | +205 | +15,5% |
| V6→V7 | 1527 | 1674 | +147 | +9,6% |
| V7→V8 | 1674 | 1866 | +192 | +11,5% |
| V8→V9 | 1866 | 2170 | +304 | +16,3% |
| V9→V10 | 2170 | 2533 | +363 | +16,7% |

#### Complexidade ciclomática

| Transição | Anterior | Atual | Δ | Δ% |
|---|---|---|---|---|
| V0→V1 | 1 | 64 | +63 | +6300,0%* |
| V1→V2 | 64 | 141 | +77 | +120,3% |
| V2→V3 | 141 | 243 | +102 | +72,3% |
| V3→V4 | 243 | 294 | +51 | +21,0% |
| V4→V5 | 294 | 329 | +35 | +11,9% |
| V5→V6 | 329 | 377 | +48 | +14,6% |
| V6→V7 | 377 | 406 | +29 | +7,7% |
| V7→V8 | 406 | 475 | +69 | +17,0% |
| V8→V9 | 475 | 541 | +66 | +13,9% |
| V9→V10 | 541 | 618 | +77 | +14,2% |

\* V0=1 é uma base matematicamente não-nula, mas tão pequena que o percentual
(6300%) não é informativo — registrado aqui pela regra formal, mas a leitura
correta é pelo valor absoluto (+63) e pelo fato de ser a transição V0→V1, onde
literalmente toda a lógica de negócio do sistema é introduzida pela primeira vez.

#### WMC (soma por classe)

| Transição | Anterior | Atual | Δ | Δ% |
|---|---|---|---|---|
| V0→V1 | 2,0 | 70,0 | +68,0 | +3400,0%* |
| V1→V2 | 70,0 | 151,0 | +81,0 | +115,7% |
| V2→V3 | 151,0 | 259,0 | +108,0 | +71,5% |
| V3→V4 | 259,0 | 318,0 | +59,0 | +22,8% |
| V4→V5 | 318,0 | 354,0 | +36,0 | +11,3% |
| V5→V6 | 354,0 | 407,0 | +53,0 | +15,0% |
| V6→V7 | 407,0 | 443,0 | +36,0 | +8,8% |
| V7→V8 | 443,0 | 509,0 | +66,0 | +14,9% |
| V8→V9 | 509,0 | 583,0 | +74,0 | +14,5% |
| V9→V10 | 583,0 | 667,0 | +84,0 | +14,4% |

\* mesma observação da complexidade ciclomática (base pequena em V0).

#### CBO (média por classe)

| Transição | Anterior | Atual | Δ | Δ% |
|---|---|---|---|---|
| V0→V1 | 2,00 | 5,00 | +3,00 | +150,0% |
| V1→V2 | 5,00 | 6,00 | +1,00 | +20,0% |
| V2→V3 | 6,00 | 5,81 | −0,19 | −3,2% |
| V3→V4 | 5,81 | 5,65 | −0,16 | −2,8% |
| V4→V5 | 5,65 | 5,74 | +0,09 | +1,6% |
| V5→V6 | 5,74 | 6,22 | +0,48 | +8,4% |
| V6→V7 | 6,22 | 6,58 | +0,36 | +5,8% |
| V7→V8 | 6,58 | 6,79 | +0,21 | +3,2% |
| V8→V9 | 6,79 | 7,05 | +0,26 | +3,8% |
| V9→V10 | 7,05 | 7,00 | −0,05 | −0,7% |

#### LCOM (média por classe)

| Transição | Anterior | Atual | Δ | Δ% |
|---|---|---|---|---|
| V0→V1 | 0,00 | 11,44 | +11,44 | N/C (base=0) |
| V1→V2 | 11,44 | 75,67 | +64,23 | +561,5% |
| V2→V3 | 75,67 | 81,05 | +5,38 | +7,1% |
| V3→V4 | 81,05 | 67,00 | −14,05 | −17,3% |
| V4→V5 | 67,00 | 67,59 | +0,59 | +0,9% |
| V5→V6 | 67,59 | 58,38 | −9,21 | −13,6% |
| V6→V7 | 58,38 | 59,24 | +0,86 | +1,5% |
| V7→V8 | 59,24 | 69,00 | +9,76 | +16,5% |
| V8→V9 | 69,00 | 60,09 | −8,91 | −12,9% |
| V9→V10 | 60,09 | 51,60 | −8,49 | −14,1% |

#### Complexidade cognitiva

| Transição | Anterior | Atual | Δ | Δ% |
|---|---|---|---|---|
| V0→V1 | 0 | 31 | +31 | N/C (base=0) |
| V1→V2 | 31 | 75 | +44 | +141,9% |
| V2→V3 | 75 | 103 | +28 | +37,3% |
| V3→V4 | 103 | 124 | +21 | +20,4% |
| V4→V5 | 124 | 158 | +34 | +27,4% |
| V5→V6 | 158 | 179 | +21 | +13,3% |
| V6→V7 | 179 | 204 | +25 | +14,0% |
| V7→V8 | 204 | 243 | +39 | +19,1% |
| V8→V9 | 243 | 254 | +11 | +4,5% |
| V9→V10 | 254 | 285 | +31 | +12,2% |

#### Duplicação (%)

| Transição | Anterior | Atual | Δ | Δ% |
|---|---|---|---|---|
| V0→V1 | 0,0 | 0,0 | 0,0 | — (sem alteração) |
| V1→V2 | 0,0 | 0,0 | 0,0 | — |
| V2→V3 | 0,0 | 0,0 | 0,0 | — |
| V3→V4 | 0,0 | 0,0 | 0,0 | — |
| V4→V5 | 0,0 | 0,0 | 0,0 | — |
| V5→V6 | 0,0 | 0,0 | 0,0 | — |
| V6→V7 | 0,0 | 0,0 | 0,0 | — |
| V7→V8 | 0,0 | 0,0 | 0,0 | — |
| V8→V9 | 0,0 | 1,8 | +1,8 | N/C (base=0) |
| V9→V10 | 1,8 | 1,5 | −0,3 | −16,7% |

#### Code smells

| Transição | Anterior | Atual | Δ | Δ% |
|---|---|---|---|---|
| V0→V1 | 0 | 2 | +2 | N/C (base=0) |
| V1→V2 até V9→V10 | 2 | 2 | 0 | 0,0% (nas 8 transições seguintes) |

#### Taxa de aprovação (TA, %)

| Transição | Anterior | Atual | Δ (p.p.) | Δ% |
|---|---|---|---|---|
| V0→V1 | Não calculável | 100,0 | — | não aplicável (V0 não tem base numérica) |
| V1→V2 | 100,0 | 83,3 | −16,7 | −16,7% |
| V2→V3 | 83,3 | 85,7 | +2,4 | +2,9% |
| V3→V4 | 85,7 | 100,0 | +14,3 | +16,7% |
| V4→V5 | 100,0 | 100,0 | 0,0 | 0,0% |
| V5→V6 | 100,0 | 100,0 | 0,0 | 0,0% |
| V6→V7 | 100,0 | 100,0 | 0,0 | 0,0% |
| V7→V8 | 100,0 | 100,0 | 0,0 | 0,0% |
| V8→V9 | 100,0 | 66,7 | −33,3 | −33,3% |
| V9→V10 | 66,7 | 100,0 | +33,3 | +49,9% |

### 14.3 — Classificação da trajetória (considerando o sentido de cada métrica)

| Métrica | Trajetória observada | Classificação | Justificativa |
|---|---|---|---|
| LOC | Crescimento monotônico em todas as 10 transições (91→2533) | **Crescimento esperado** (não é melhoria nem degradação por si só) | Cada incremento adiciona funcionalidades novas por definição (etapa 10 do artigo); LOC subir é a consequência direta do escopo crescente, não um sinal de qualidade. |
| Complexidade ciclomática | Crescimento monotônico (1→618), taxa percentual decrescente a partir de V2 (de 120% para ~10-20% por transição) | **Sinal de atenção, mas esperado e desacelerando** | Cresce porque há mais decisões/ramificações (mais regras de negócio reais sendo implementadas). A desaceleração percentual sugere que o crescimento está ficando sublinear em relação ao tamanho do sistema, não explodindo. |
| WMC | Mesmo padrão da complexidade ciclomática (2→667) | **Sinal de atenção, mas esperado** | Por definição, WMC é a soma das complexidades por método; acompanha a complexidade ciclomática de perto (correlação esperada, não uma descoberta independente). |
| CBO | Oscila numa faixa estreita (5,65 a 7,05), com 2 quedas (V2→V3 e V3→V4, e novamente V9→V10) | **Estabilidade** | Mesmo com o sistema triplicando de tamanho (LOC), o acoplamento médio por classe não cresceu de forma proporcional — ficou relativamente contido. |
| LCOM | Sobe forte em V1-V3 (0→81,05), depois tendência de queda até V10 (51,6), com oscilações | **Degradação inicial seguida de melhoria estrutural parcial** | Os primeiros incrementos (autenticação, cadastro, animais) parecem ter introduzido classes menos coesas; a partir de I4 a tendência de LCOM é predominantemente de queda (menos falta de coesão), embora não monotônica. |
| Complexidade cognitiva | Crescimento monotônico (0→285) | **Sinal de atenção, mas esperado** | Mesmo padrão e mesma leitura da complexidade ciclomática — o sistema fica mais difícil de entender à medida que cresce, o que é esperado, mas vale observar se a taxa por linha de código se mantém razoável (ver nota abaixo). |
| Duplicação | Zero por 9 versões consecutivas (V0-V8), aparece em V9 (1,8%) e cai em V10 (1,5%) | **Degradação pontual e isolada, de magnitude baixa** | Nenhuma duplicação por quase todo o experimento é um sinal estrutural positivo notável; o surgimento tardio em I9, mesmo pequeno, é o único episódio de duplicação do projeto. |
| Code smells | Salta de 0 para 2 em V1, e permanece EXATAMENTE em 2 por todas as 9 transições seguintes (V1 a V10) | **Degradação pontual isolada em V1, seguida de estabilidade total** | É notável que, apesar do código mais que sextuplicar (397→2533 LOC) entre V1 e V10, nenhum code smell novo foi introduzido pelo SonarQube nesse intervalo — os mesmos 2 smells de V1 persistem sem aumentar nem serem corrigidos. |
| TA | Oscila entre 66,7% e 100%, sem tendência direcional única | **Estabilidade com dois episódios pontuais de degradação, ambos ligados a gaps funcionais específicos identificados (não a regressões)** | As quedas (V2, V3, V9) coincidem exatamente com os incrementos em que um caso de teste específico foi reprovado por uma lacuna de implementação documentada (CT011, CT014, CT037) — nunca por quebra de funcionalidade já existente. |

**Nota sobre densidade de complexidade:** dividindo complexidade ciclomática por
LOC, a razão cai de ~0,70 (V0, 1/91 — pouco significativo pela base pequena) para
~0,16 em V1 (64/397) e se mantém entre 0,14 e 0,25 do V2 ao V10 (ex.: V10 =
618/2533 ≈ 0,24). Ou seja, a complexidade por linha de código não dispara ao
longo do experimento — cresce, mas aproximadamente na mesma proporção do
tamanho do sistema, não mais rápido que ele.

## 15. Corretude funcional e regressões

### Tabela consolidada (dados reais, não ilustrativos)

| Versão | Testes executados | Aprovados | Reprovados | Não executados | TA |
|---|---|---|---|---|---|
| V0 | 0 | 0 | 0 | 2 | Não calculável |
| V1 | 6 | 6 | 0 | 1 | 100,0% |
| V2 | 6 | 5 | 1 | 0 | 83,3% |
| V3 | 7 | 6 | 1 | 0 | 85,7% |
| V4 | 2 | 2 | 0 | 0 | 100,0% |
| V5 | 3 | 3 | 0 | 0 | 100,0% |
| V6 | 3 | 3 | 0 | 1 | 100,0% |
| V7 | 4 | 4 | 0 | 0 | 100,0% |
| V8 | 4 | 4 | 0 | 1 | 100,0% |
| V9 | 3 | 2 | 1 | 0 | 66,7% |
| V10 | 4 | 4 | 0 | 1 | 100,0% |

