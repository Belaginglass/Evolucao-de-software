# Protocolo de avaliação funcional — DogTech

Procedimento fixo, repetido da mesma forma em V0–V10.

## 1. Execução da suíte

Comandos padrão, na raiz de `Projeto/`, nesta ordem, a cada versão:

```bash
mvn test      # executa a suíte JUnit acumulada (unitários + de integração leve)
mvn verify    # roda os testes de novo e, via jacoco-maven-plugin (ja fixado no pom.xml),
              # gera o relatório de cobertura em target/site/jacoco/ (jacoco.xml, jacoco.csv, index.html)
```

Confirmado em V0: `mvn test` e `mvn verify` executam sem erro e o JaCoCo gera
`jacoco.xml`/`jacoco.csv`/`index.html` normalmente (ainda sem cobertura relevante, pois
não há lógica de negócio nesta versão).

A suíte é **acumulativa**: a cada versão Vn, executam-se TODOS os casos de teste de
`testes/casos_teste.xlsx` cujo incremento seja ≤ n (ex.: em V5, executam-se os casos de
V0 + I1 + I2 + I3 + I4 + I5), não apenas os casos novos daquela versão. Isso é o que
permite detectar regressão (um caso aprovado em Vn e reprovado em Vn+1).

## 2. Registro dos resultados — onde e como

Cada execução de caso de teste em uma versão gera **uma linha nova** na aba
"Execuções por Versão" de `testes/casos_teste.xlsx` (nunca sobrescrever uma linha de
versão anterior — é um log, não um estado único por teste). Colunas:

| Coluna | Preenchimento |
|---|---|
| Versão | `V0`, `V1`, ..., `V10` |
| ID do teste | `CT001`, `CT002`, ... (de "Casos de Teste") |
| Incremento do teste | preenchido automaticamente por fórmula a partir de "Casos de Teste" |
| Situação | exatamente um de: `Aprovado`, `Reprovado`, `Não executado` |
| Resultado obtido | o que de fato aconteceu ao rodar o teste (preenchido quando Aprovado/Reprovado) |
| Motivo da não execução | obrigatório quando Situação = `Não executado` (ex.: "funcionalidade ainda não implementada nesta versão", "ambiente indisponível", "teste bloqueado por dependência de outro caso") |
| Mensagem de erro | obrigatório quando Situação = `Reprovado` e houver stacktrace/mensagem de falha do JUnit; opcional em outros casos |

Dois exemplos já registrados em V0 (`CT045`, `CT046` — RNF001 e RNF008): ambos
`Não executado`, com motivo "funcionalidade ainda não implementada em V0 (apenas
esqueleto)" — não há cadastro nem tela nesta versão, logo não é possível executar
esses dois casos, e isso é diferente de reprová-los.

## 3. Taxa de aprovação (TA)

$$TA = \frac{T_{aprovados}}{T_{executados}} \times 100$$

- `T_executados = T_aprovados + T_reprovados` — **nunca inclui** `Não executados` no
  denominador.
- Calculado automaticamente na aba "Suíte Acumulativa" (coluna "Taxa de aprovação
  (TA)"), por versão, a partir da aba "Execuções por Versão" (`COUNTIFS` por `Situação`
  dentro daquela `Versão`).
- **Se `T_executados = 0`** (nenhum caso aprovado ou reprovado ainda — caso de V0 hoje,
  com os 46 casos todos "Não executado" ou sem registro), a fórmula retorna o texto
  `"Não calculável"` — nunca `0%` nem `100%`. Isso já está implementado na planilha
  (`=IF(Executados=0,"Não calculável",ROUND(Aprovados/Executados*100,1))`).
- Verificação de consistência: uma vez a suíte totalmente executada numa versão,
  `Executados + Não_executados` deve ser igual a `Total acumulado` daquela linha (se não
  for, há casos da suíte que não foram nem rodados nem marcados como não executados —
  sinal de lacuna no registro).

## 4. Corretude ≠ cobertura ≠ métricas estruturais

Três números nunca devem ser combinados ou confundidos entre si, mesmo quando vêm da
mesma versão:

| O quê | Onde fica registrado | O que prova |
|---|---|---|
| **Resultado dos testes funcionais** (TA, Aprovado/Reprovado/Não executado) | `testes/casos_teste.xlsx` (abas "Execuções por Versão" e "Suíte Acumulativa") | Se o comportamento exigido pelos requisitos está correto — ou não. |
| **Cobertura de linhas** (JaCoCo `coverage`) | relatório `target/site/jacoco/` de cada versão + campo `coverage` no registro de métricas (`resultados/Vn/registro_Vn.md`) | Quanto do código foi exercitado por algum teste — nada sobre se o teste checou o comportamento certo. Sem meta numérica fixada — acompanhada apenas como mais uma métrica, não como critério de aceite. |
| **Métricas estruturais** (LOC, complexidade, WMC, CBO, LCOM, complexidade cognitiva, duplicação, code smells) | `resultados/protocolo_metricas.md` + `resultados/Vn/registro_Vn.md` | Como o código está organizado/complexo — nada sobre se ele funciona. |

Um sistema pode ter 95% de cobertura e 0% de TA (testes exercitam o código mas
verificam a coisa errada, ou o código está incorreto); e pode ter TA = 100% com
cobertura baixa (poucos testes, mas todos passam, cobrindo só o caminho feliz). Por
isso os registros de cada versão (`resultados/Vn/registro_Vn.md`) sempre apresentam
essas três dimensões em seções separadas, nunca uma combinada na outra.
