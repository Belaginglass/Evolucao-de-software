# Requisitos transversais — DogTech

Este documento tem o objetivo de identificar quais requisitos do documento original pertencem a um único incremento, quais aparecem em vários incrementos, e quais precisam ser considerados **desde o V0** (versão base, antes do primeiro incremento funcional), para que o LLM gerador de código não implemente cada incremento de forma isolada, prejudicando a integração do sistema.

## 1. Requisitos que precisam ser considerados desde o V0 (base arquitetural)

Estes não pertencem a um caso de uso específico — são decisões estruturais que, se adiadas, forçam retrabalho em vários incrementos.

| ID | Nome | Por que precisa estar no V0 |
|---|---|---|
| `RNF003` | Arquitetura do software (MVC + SOA + DAO) | Define a organização em camadas de **todo** o código a ser gerado; se não for fixada no V0, cada incremento pode adotar uma estrutura de pastas/camadas diferente. |
| `RNF008` | Campo de ajuda (ícone "?") | Convenção de UI aplicável a qualquer tela criada em qualquer incremento. |
| `RNF001` | Criptografia do sistema (SHA-256 + salt 8 bits) | Qualquer fluxo que crie ou altere senha (UC001, UC002, UC006, UC011) depende da mesma rotina de hashing; deve existir um único componente de hashing reaproveitado, não uma implementação por incremento. |
| `RN001` | Validação de e-mail e senha | Mesma regra de validação é citada em UC001 (login/recuperação) e UC002 (cadastro); deve ser um validador único e compartilhado. |
| `RNF005` | Alterar estados (padrão de projeto *State*) | O próprio documento cita que o padrão deve ser usado "para realizar as funções de alteração de estado **existentes no sistema**", citando como exemplos a mudança de estado da adoção (UC005/UC006/UC010) **e** o processo de aceite de um novo usuário administrativo (UC004) — ou seja, é uma decisão de design única que sustenta múltiplos incrementos. |
| `RN009` | Gerência de agendas | Um único serviço de agenda (vinculado a e-mail) é reaproveitado por UC004 (criação da agenda ao conceder privilégio), UC006 (agendamento de visita) e UC008 (agendamento de prestação de serviço). Projetar esse serviço apenas quando ele aparece pela primeira vez (I5) evita reimplementá-lo em I7 e I9. |


## 2. Requisitos que aparecem em mais de um incremento

| ID | Nome | Incrementos afetados | Observação |
|---|---|---|---|
| `RF004` | Adoção de Animal (Manter adoção) | I6 (sinalização de interesse) e I7 (aprovação) | O próprio texto do RF004 descreve as duas pontas do mesmo fluxo: "permitir a sinalização de interesse [...] este interesse deverá ser aprovado". |
| `RN004` | Estados da adoção | I6 (estado inicial "aguardando"), I7 (transições por avaliação), I8 (estados de pós-adoção) | Depende de `RNF005` (padrão *State*) — ver seção 1. |
| `RN008` | Listagem de pedidos de adoções | I6 (criação da fila) e I7 (listagem/agrupamento para o gestor) | Mesma estrutura de dados (fila) é produzida em I6 e consumida/ordenada em I7. |
| `RN009` | Gerência de agendas | I5, I7, I9 | Ver seção 1. |
| `RN010` | Escolha de dados na tela inicial do sistema | I1 (tela de destino após login) e I4 (conteúdo da própria página inicial) | Regra definida integralmente em I4 (UC009), mas seu efeito é observado já em I1. |
| `RN012` | Feedback de pós-adoção | I7 (pedir/ver feedback a partir da avaliação) e I8 (ciclo completo de feedback) | Regra definida integralmente em I8 (UC010), mas o fluxo de avaliação (UC006) também a referencia. |
| `RNF007` | Sumarização de doações e feedback | I8 (feedback) e I10 (doações) | O próprio texto do requisito menciona ambos os assuntos na mesma regra. |

## 3. Requisitos que pertencem a um único incremento

Todos os demais requisitos mapeados nos arquivos `I1.md` a `I10.md` são específicos de seu incremento e não precisam de coordenação extra:

- **I1:** `RF001`, `RN005`
- **I2:** `RF010`, `RN002`, `RN011`, `RNF002` (cadastro/UC002; citação de UC04 mantida conforme o original — ver observações em `I2.md` e `I5.md`)
- **I3:** `RF002`, `RF008`, `RF014`, `RN003`, `RNF004`, `RNF006`
- **I4:** requisito de usuário "[ATR-01] Manter página inicial" (seção 2.2)
- **I5:** `RF006`
- **I6:** `RF003`, `RN006`
- **I7:** `RN007`, `RN014`, `RN015`, `RN016`
- **I8:** `RF005`, `RF009`, `RF011`
- **I9:** `RF012`
- **I10:** `RF013`, `RN013`, requisitos de usuário "[ATR-01] Manter eventos" e "[ATR-01]/[ATR-02] Manter relatórios" (seção 2.2)

## 4. Lacuna identificada no documento original

O documento salta de `RF006` para `RF008` na seção 4 (Requisitos Funcionais) — não existe um `RF007` no texto-fonte. 
