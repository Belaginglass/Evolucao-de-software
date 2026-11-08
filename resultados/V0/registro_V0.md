# Registro da Versão V0 — DogTech

Campos conforme a seção 3.6 (Coleta e registro dos dados) do artigo.

## Identificação

- **Versão / Incremento:** V0 (estrutura inicial — anterior a qualquer incremento)
- **Commit Git:** `516a5fb9c89e81bfe800690df66ce538933e90da` (root-commit, branch `master`, repositório `Projeto/`)
- **Mensagem de commit:** "V0 - estrutura inicial do DogTech"
- **Gerado por:** pesquisador (não houve solicitação ao Gemini nesta versão — conforme seção 3.4 do artigo, V0 é construído manualmente, antes do início da geração assistida).
- **Alterações em relação à versão anterior:** não aplicável (primeira versão do projeto).

## Arquivos que compõem a versão (14 arquivos)

```
.gitignore
data/.gitkeep
pom.xml
src/main/java/com/tcc/iterativa/GeracaoIterativaApplication.java
src/main/java/com/tcc/iterativa/config/package-info.java
src/main/java/com/tcc/iterativa/controller/package-info.java
src/main/java/com/tcc/iterativa/dto/package-info.java
src/main/java/com/tcc/iterativa/model/package-info.java
src/main/java/com/tcc/iterativa/repository/package-info.java
src/main/java/com/tcc/iterativa/service/package-info.java
src/main/resources/application.properties
src/main/resources/ceps.csv
src/main/resources/templates/.gitkeep
src/test/java/com/tcc/iterativa/GeracaoIterativaApplicationTests.java
```

Não fazem parte do commit (propositalmente, via `.gitignore`): `.env` (chave de API do Gemini), `data/*.db` (banco SQLite local), `target/` (build).

Ferramenta externa usada apenas para coleta de métricas, não versionada no projeto: `Projeto/tools/ck-0.7.0-jar-with-dependencies.jar` (baixado do Maven Central — `com.github.mauricioaniche:ck:0.7.0:jar-with-dependencies` — e listado em `.gitignore`).

## Compilação e inicialização (seção 5.2)

| Verificação | Resultado |
|---|---|
| `mvn clean compile` | ✅ Sucesso, sem erros |
| `mvn test` (inclui `contextLoads`) | ✅ Sucesso — contexto Spring sobe por completo (pool Hikari conecta no SQLite, Hibernate inicializa, Thymeleaf configurado) |
| `mvn spring-boot:run` (execução real) | ✅ Tomcat iniciado na porta 8080 em ~3,3s; `GET /` respondeu HTTP 404 (esperado — nenhuma rota implementada ainda) |
| Erros de compilação/execução | Nenhum |

Aviso benigno registrado no log (não é erro): `spring.jpa.open-in-view is enabled by default` — comportamento padrão do Spring Boot, não configurado explicitamente nesta versão.

## Métricas estruturais (seção 5.4 / 3.5)

### SonarQube (Docker local, `localhost:9000`, versão do servidor 26.10.0.133078)

- **Projeto:** `dogtech` — "DogTech - SGA (TCC)"
- **Análise associada ao commit:** `516a5fb9c89e81bfe800690df66ce538933e90da` (revisão confirmada pela própria API do SonarQube)

| Métrica | Valor em V0 |
|---|---|
| Linhas de código (ncloc) | 91 |
| Complexidade ciclomática (complexity) | 1 |
| Complexidade cognitiva (cognitive_complexity) | 0 |
| Code smells | 0 |
| Bugs | 0 |
| Vulnerabilidades | 0 |
| Duplicação (duplicated_lines_density) | 0,0% |
| Classes | 1 (apenas `GeracaoIterativaApplication`; `package-info.java` e a classe de teste não contam como classe de produção) |
| Funções/métodos | 1 |
| Cobertura de testes (coverage) | 33,3% |
| Débito técnico estimado (sqale_index) | 0 |

### CK — métricas de código orientado a objetos (`ck-0.7.0-jar-with-dependencies.jar`, saída em `resultados/V0/ck/`)

Executado sobre `Projeto/src` (inclui também a classe de teste). Duas classes identificadas:

| Classe | WMC | CBO | DIT | RFC | LCOM | LCOM* | TCC | LCC | LOC |
|---|---|---|---|---|---|---|---|---|---|
| `com.tcc.iterativa.GeracaoIterativaApplication` | 1 | 2 | 1 | 1 | 0,0 | N/A | N/A | N/A | 5 |
| `com.tcc.iterativa.GeracaoIterativaApplicationTests` | 1 | 2 | 1 | 0 | 0,0 | N/A | N/A | N/A | 4 |

**N/A em `LCOM*`, `TCC` e `LCC`:** o CK retornou `NaN` explicitamente para essas três colunas em ambas as classes — correto, pois ambas têm apenas 1 método, e essas três métricas (variante de Henderson-Sellers do LCOM, Tight/Loose Class Cohesion) dependem de comparar **pares** de métodos; com um único método não há par a comparar, logo o valor é indisponível, não zero (ver `protocolo_metricas.md`, seção 6.3). Já `LCOM` (coluna simples do CK) retornou `0,0` de forma válida mesmo com 1 método — é um 0 genuíno calculado pela ferramenta, não um placeholder.

Arquivos completos (inclui também `field.csv`, `method.csv`, `variable.csv`): `resultados/V0/ck/`.

## Interpretação

V0 representa, como esperado, uma baseline praticamente nula: duas classes triviais (ponto de entrada da aplicação e teste de contexto), sem lógica de negócio, sem code smells, sem complexidade relevante e sem cobertura de funcionalidades (a cobertura de 33,3% reportada pelo SonarQube refere-se apenas à classe de entrada, testada indiretamente pelo `contextLoads`). Esta versão serve como ponto de partida (zero) para comparação com V1–V10, conforme planejado na seção 5.4 do artigo — qualquer crescimento de LOC, complexidade, acoplamento ou code smells observado a partir de V1 é atribuível à introdução das funcionalidades dos incrementos, não a ruído pré-existente.

## Resultados de testes funcionais (seção 7 — ver `resultados/protocolo_avaliacao_funcional.md`)

`mvn test` e `mvn verify` executados com sucesso (ver tabela de compilação acima). O único teste que de fato roda nesta versão é o `contextLoads` (JUnit/Spring Boot Test, genérico — não corresponde a nenhum `RFxxx` específico), aprovado.

Dos 46 casos de `testes/casos_teste.xlsx`, apenas `CT045` (RNF001) e `CT046` (RNF008) estão rotulados como pertencentes a V0 — os outros 44 cobrem funcionalidades dos incrementos I1–I10, ainda não implementadas. Registrados na aba "Execuções por Versão" como **Não executado**, com o motivo "funcionalidade ainda não implementada em V0 (apenas esqueleto, sem cadastro de usuário nem telas)" — não como reprovados, e não como 0.

**Taxa de aprovação (TA) em V0: não calculável** (`T_executados = 0`, pois nenhum caso foi de fato aprovado ou reprovado — os dois aplicáveis estão "não executado"). Isso é o valor correto conforme a regra da seção 7.3 (nunca reportar 0% quando o denominador é zero).

**Cobertura de linhas (JaCoCo/SonarQube) = 33,3%** — não confundir com a TA acima: é apenas a fração de linhas exercitadas pelo `contextLoads`, não uma medida de corretude funcional (ver seção 7.4 do protocolo).
