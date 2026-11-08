# Esclarecimentos e decisões de interpretação

Este apêndice consolida toda decisão de interpretação tomada neste experimento sobre
pontos em que o documento de requisitos original (*Requisitos_e_Casos_de_Uso.pdf*) é
ambíguo, incompleto ou internamente inconsistente. Nenhuma decisão aqui cria um
requisito novo todas resolvem uma lacuna ou inconsistência já presente no documento
-fonte, de forma explícita e rastreável
("Eventuais limitações ou decisões presentes na especificação serão registradas, de
modo a preservar a rastreabilidade entre os requisitos e o comportamento observado").

Este arquivo é enviado ao Gemini em toda chamada,
junto com o prompt-base e o prompt específico do incremento, para que as mesmas
decisões sejam aplicadas de forma consistente em todos os incrementos.

## 1 — Página única de autenticação (afeta I1 / RF001 / UC001)

O `<RF001>` do documento original descreve duas páginas de autenticação: uma pública
(menu principal, cadastro de adotante) e outra restrita, acessível apenas por URL
direta (cadastro administrativo). Para este experimento, usa-se **uma única página de
autenticação** — login, cadastro e recuperação de senha no mesmo ponto de entrada. O
redirecionamento por nível de acesso ocorre **depois** do login (`<RN010>`), não na
escolha de qual página acessar.


## 2 — Busca de CEP via arquivo local, sem API externa (afeta I2 / RNF002)

A `<RNF002>` do documento original prevê consultar uma API externa de CEP (Postmon ou
similar). Para este experimento, usa-se o arquivo `Projeto/src/main/resources/ceps.csv`
(colunas: `cep` — 8 dígitos, sem hífen —, `rua`, `bairro`, `cidade`, `estado`) como
fonte local, eliminando a dependência de rede durante a geração e execução
automatizada dos testes ao longo do experimento. A implementação da busca de CEP deve
consultar esse arquivo (carregado do classpath), nunca fazer uma chamada HTTP externa.

Dados do CSV coletados de fontes públicas reais
referentes a Juiz de Fora/MG.

## 3 — Lacuna: não existe `RF007` no documento original

A seção 4 (Requisitos Funcionais) do documento original salta de `<RF006>` para
`<RF008>` — não há um `RF007`. Isso não é uma omissão desta extração; é uma lacuna do
próprio documento-fonte. Nenhum requisito foi criado para preencher esse número.

## 4 — Inconsistência na `<RNF002>`: citação de "UC02 e UC04"

O texto da `<RNF002>` ("Busca de CEP") cita literalmente que a busca de CEP ocorre
"nos cadastros especificados no UC02 e UC04". UC002 (Cadastro) de fato tem campos de
endereço (`<RN002>`). UC004 (Manter Privilégio dos Atores), porém, não possui nenhum
campo de endereço nos fluxos descritos, a citação ao UC004 é mantida tal como
está no documento original (possível erro de numeração de uma revisão anterior do
documento-fonte), sem reinterpretação. Ao implementar I5 (UC004), **não** é esperado
que exista busca de CEP.


## 5 — Requisitos sem `RFxxx` numerado, derivados da seção 2.2 (Requisitos dos usuários)

Três funcionalidades não têm um `<RFxxx>` numerado dedicado na seção 4 do documento
original, apenas uma menção na lista de "Requisitos dos usuários":

- "Manter página inicial" (afeta I4 / UC009) — `[ATR-01] Manter página inicial.`
- "Manter eventos" (afeta I10 / UC012) — `[ATR-01] Manter eventos.`
- "Manter relatórios" (afeta I10 / UC014) — `[ATR-01] Manter relatórios.` e
  `[ATR-02] Manter relatórios.`

Para essas três, a especificação funcional usada é o próprio caso de uso (UC009,
UC012, UC014) descrito na seção 6 do documento original — não um RF numerado.

## 6 — `UC014` (Manter relatórios) não especifica quais relatórios devem existir

O documento original diz apenas que "o sistema deverá prover uma página com
relatórios... contendo dados que sejam interessantes para os gestores em específico",
sem listar quais relatórios ou quais dados. Para I10, a implementação deve prover uma
página de relatórios funcional, mas o conteúdo exato de cada relatório é uma decisão de
implementação em aberto, qualquer relatório implementado deve usar apenas dados já
existentes no sistema (ex.: contagem de adoções por estado, animais cadastrados por
espécie), nunca inventar uma fonte de dados nova só para preencher a tela.


## 7 — RF008 (Manter baias) como entidade própria, não campo de texto (afeta I3)

RN003 lista "baia do animal" como um atributo do cadastro de animal, mas RF008
("Manter baias") exige CRUD próprio (identificador opcional, nome obrigatório).
Decisão: `Baia` é uma entidade própria, com repositório e controlador dedicados,
referenciada pelo `Animal` não um campo de texto livre. (Registrada originalmente
apenas no prompt de I3 e como correção durante a geração; centralizada aqui
retroativamente.)

## 8 — Papéis administrativos: de "ADMIN" genérico para DIRETOR_GERAL/GESTOR_ADOCAO (afeta I1-I4, substituído em I5)

Os incrementos I1-I4 usaram um papel único "ADMIN" como aproximação temporária
para "ter privilégio administrativo", já que UC004 (papéis reais) só é
implementado em I5. A partir de I5, os papéis passam a ser "DIRETOR_GERAL" e
"GESTOR_ADOCAO" (RF006), e o cadastro público precisa oferecer essas opções para
que o próprio UC004 seja alcançável. "ADMIN" foi mantido como valor de
compatibilidade (não removido), mas não é mais a via normal de obter privilégio
administrativo a partir de I5.

## 9 — RN012 (prazo de 5/15 dias no pós-adoção) sem bloqueio de data real (afeta I8)

RN012 descreve prazos de 5 e 15 dias para a troca de feedback de pós-adoção. Para
permitir verificação manual do fluxo sem esperar dias reais, optou-se por NÃO
implementar o bloqueio rígido de data (o gestor/adotante pode trocar feedback a
qualquer momento após a adoção ser marcada como "ADOTADO"). A notificação
automática após 15 dias sem interação (RN012, parte final) não foi implementada
nesta decisão e o caso de teste `CT033`
("Não executado"). Essa é uma simplificação deliberada para viabilizar o
experimento, não uma omissão do requisito original.
