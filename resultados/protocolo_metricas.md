# Protocolo de avaliação estrutural — DogTech

Este documento fixa, de uma vez, como cada métrica é coletada, com quais
ferramentas/versões/configurações, e como tratar valores não aplicáveis — para que
V0 a V10 sejam medidos sempre da mesma forma (seção 3.5 do artigo: "mesma ferramenta,
configuração e procedimento de análise").

## 1. Métrica → ferramenta → campo exato

| Métrica (planilha do usuário) | Ferramenta | Campo exato | Granularidade | Observação |
|---|---|---|---|---|
| LOC | SonarQube | `ncloc` | projeto / arquivo | Linhas de código não comentadas; visão agregada. |
| LOC (por classe) | CK | `class.csv → loc` | classe | Usado quando a análise precisa ser por classe/incremento. |
| Complexidade ciclomática | SonarQube | `complexity` | projeto / arquivo / função | McCabe, direto. |
| Complexidade ciclomática (por método) | CK | `method.csv → wmc` | método | Apesar do nome "wmc" também no `method.csv`, nessa tabela a coluna representa a complexidade McCabe **daquele método individual** (não a soma da classe). |
| WMC | CK | `class.csv → wmc` | classe | Soma da complexidade ciclomática de todos os métodos da classe (definição original de Chidamber & Kemerer). SonarQube não expõe WMC por classe. |
| CBO | CK | `class.csv → cbo` e `cboModified` | classe | SonarQube não calcula CBO. |
| LCOM | CK | `class.csv → lcom` (e, quando disponível, `lcom*`) | classe | Ver regra de N/A abaixo para `lcom*`, `tcc`, `lcc` em classes com 0–1 método. |
| Complexidade cognitiva | SonarQube | `cognitive_complexity` | projeto / arquivo / função | CK não calcula complexidade cognitiva. |
| Duplicação | SonarQube | `duplicated_lines_density` (detalhe em `duplicated_lines` / `duplicated_blocks`) | projeto / arquivo | Motor CPD do SonarQube; precisa de um bloco mínimo de tokens repetidos para detectar. |
| Code smells | SonarQube | `code_smells` | projeto / arquivo | Conjunto padrão de regras Java do SonarQube ("Sonar way"). |
| Cobertura de testes (apoio, não pedida na tabela mas usada nos registros) | JaCoCo → SonarQube | `coverage` | projeto / classe / linha | JaCoCo gera `target/site/jacoco/jacoco.xml`; o `sonar-maven-plugin` importa esse relatório e o expõe via API do SonarQube. |

Nenhuma ferramenta isolada cobre as 8 métricas — por isso CK e SonarQube são usados em
conjunto (conforme já alertado no enunciado da etapa 6.2).

## 2. Ferramentas, versões e configuração fixadas

| Ferramenta | Versão | Onde está fixada |
|---|---|---|
| Java (JDK) | OpenJDK 17.0.21.0.2 (Microsoft build) | ambiente local |
| Maven | 3.10.0 | ambiente local (`C:\Tools\apache-maven-3.10.0`) |
| Spring Boot (parent) | 3.5.16 | `Projeto/pom.xml` |
| JaCoCo Maven Plugin | 0.8.12 | `Projeto/pom.xml` (`<plugins>`, goals `prepare-agent` + `report` na fase `test`) |
| sonar-maven-plugin (scanner) | 5.1.0.4751 | `Projeto/pom.xml` (`<plugins>`) — fixado a partir deste registro; em V0 foi invocado pela coordenada completa antes de ser declarado no pom |
| SonarQube (servidor) | 26.10.0.133078 | container Docker `sonarqube`, publicado em `localhost:9000` (local, não versionado no projeto) |
| CK | 0.7.0 (`com.github.mauricioaniche:ck`, classifier `jar-with-dependencies`) | baixado do Maven Central para `Projeto/tools/` (fora do Git — ver `.gitignore`) |
| Docker Engine | 29.8.2 | apenas como motor de execução do container do SonarQube |

**Comandos padrão (os mesmos para toda versão V0–V10, trocando apenas `Vn`):**

```bash
mvn clean compile
mvn test
mvn sonar:sonar -Dsonar.host.url=http://localhost:9000 -Dsonar.token=<token> \
    -Dsonar.projectKey=dogtech -Dsonar.projectName="DogTech - SGA (TCC)" \
    -Dsonar.projectVersion=Vn
java -jar tools/ck-0.7.0-jar-with-dependencies.jar "<caminho absoluto para Projeto/src>" \
    false 0 true "<caminho para resultados/Vn/ck/>"
```

- A chave do projeto no SonarQube (`sonar.projectKey=dogtech`) é **fixa** em todas as
  versões — é o que permite comparar a evolução das métricas na mesma linha do tempo
  (aba "Activity"/histórico do próprio SonarQube), em vez de criar um projeto novo por
  incremento.
- `sonar.projectVersion` muda a cada versão (`V0`, `V1`, ..., `V10`) e o scanner grava
  automaticamente o hash do commit Git correspondente (`revision`) — confirmado em V0
  (`516a5fb9c89e81bfe800690df66ce538933e90da`).
- O `.jar` do CK não é commitado (ver `.gitignore` do `Projeto/`); se for necessário
  reobtê-lo, a origem exata está documentada aqui (Maven Central, grupo/artefato/versão
  acima), não em um link solto.
- Nunca usar credenciais padrão/adivinhadas para acessar o SonarQube local: o token é
  gerado pelo pesquisador em "Minha Conta → Segurança" na própria instância em
  `localhost:9000` e usado apenas na variável de ambiente `SONAR_TOKEN` da sessão —
  nunca gravado em arquivo versionado.

## 3. Métricas não aplicáveis — como registrar

**Regra geral: nunca preencher com `0` um valor que a ferramenta não calculou.** Três
situações diferentes, com rótulos diferentes:

| Situação | Rótulo a usar | Exemplo real já encontrado |
|---|---|---|
| A ferramenta calculou e o resultado matematicamente é zero | `0` (valor genuíno) | `duplicated_lines_density = 0,0%` em V0 — o motor CPD rodou e não achou duplicação. `LCOM = 0,0` para uma classe com 1 método — cálculo válido, não indefinido. |
| A ferramenta tentou calcular, mas a métrica é matematicamente indefinida nesta versão (denominador zero, não há pares/elementos suficientes) | `N/A (indisponível)` + justificativa | CK retorna `NaN` em `lcom*`, `tcc` e `lcc` para classes com 0 ou 1 método, porque essas métricas comparam **pares** de métodos — sem par, não há cálculo (visto em V0, `GeracaoIterativaApplication` e `GeracaoIterativaApplicationTests`). |
| A métrica não foi coletada nesta versão por decisão do pesquisador, ou a ferramenta falhou/não rodou | `Não coletado` + justificativa | (nenhum caso ainda; reservado para, por exemplo, uma versão em que o SonarQube esteja fora do ar). |

Regras derivadas:
1. **Camadas ainda vazias não têm métrica "zero", têm métrica "N/A".** Enquanto
   `com.tcc.iterativa.model` não tiver nenhuma entidade JPA (caso de V0), qualquer
   métrica agregada "por entidade" (ex.: WMC médio das entidades) é `N/A` — não existe
   por não haver instâncias da categoria, não porque o valor calculado seja 0.
2. **Erro de análise nunca é 0.** Se o CK ou o SonarQube falharem ao processar um
   arquivo (erro de parsing, por exemplo), o registro daquela versão deve citar a
   mensagem de erro e marcar a métrica como `indisponível — erro de análise`, nunca `0`.
3. **Toda marcação de `N/A` ou `Não coletado` exige uma justificativa ao lado**, na
   mesma linha da tabela de registro da versão — nunca uma célula vazia ou um `N/A`
   sem explicação, para que a ausência seja rastreável na análise final (seções 3.7 e
   3.8 do artigo).
4. Esse tratamento já foi aplicado retroativamente ao registro de V0
   (`resultados/V0/registro_V0.md`), que antes omitia `lcom*`, `tcc` e `lcc` em vez de
   declará-los `N/A` — esse era exatamente o tipo de lacuna que este protocolo evita a
   partir de agora.
