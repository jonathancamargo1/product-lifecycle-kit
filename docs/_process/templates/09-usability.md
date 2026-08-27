---
phase: 09-usability
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Teste de usabilidade lo-fi

## Propósito
Testar os wireframes com gente de fora do time antes de existir código.
Sair com problemas rankeados, não com opinião coletada.

## Gate de saída
Roteiro de 5 tarefas aplicado, 4 de 5 usuários completam as tarefas críticas sem ajuda, e existe relatório com problemas rankeados.
- [ ] Roteiro tem exatamente 5 tarefas, cada uma com critério de sucesso observável.
- [ ] Tarefas críticas estão marcadas antes da primeira sessão, não depois.
- [ ] Pelo menos 5 participantes, nenhum deles do time do produto.
- [ ] Relatório lista cada problema com severidade, frequência e tela.

## Esqueleto

### Participantes
<!-- Quem é usuário do problema descrito no PRD. Uma linha por pessoa: papel, data,
     e se usou o produto antes. Não serve colega de time nem "usuário genérico". -->

### Roteiro de tarefas
<!-- Exatamente 5. Cada tarefa é um objetivo com contexto, nunca instrução de clique.
     Não serve "clique em Novo pedido". Serve "você precisa repor o estoque de X". -->

| # | Tarefa (contexto dado à pessoa) | Crítica? | Critério de sucesso observável |
|---|---|---|---|
| 1 | <situação e objetivo> | sim | <estado final visível, sem ajuda do moderador> |

<!-- Critério de sucesso é binário e visível de fora, ex "chegou na tela de confirmação
     em até 3 minutos, sem dica". Não serve "entendeu a tela" ou "gostou". -->

### Como conduzir sem induzir
<!-- Regras fixas do moderador. -->
- Leia a tarefa em voz alta, do jeito escrito, e cale a boca.
- Pergunta da pessoa é devolvida: "o que você faria se eu não estivesse aqui?".
- Só ajude depois de registrar a tarefa como falha, e anote em que passo travou.
- Nunca pergunte se a pessoa gostou nem se a tela está clara.
  <!-- Preferência declarada não é dado de usabilidade. O dado é o que ela conseguiu fazer. -->

### Resultados por tarefa
| # | Tarefa | Sucessos | Falhas | Com ajuda | Onde travou |
|---|---|---|---|---|---|

### Relatório de problemas
<!-- Um problema por linha, ordenado por severidade e depois por frequência.
     Severidade: bloqueia, atrasa, incomoda. Frequência: quantos dos participantes.
     Encaminhamento aponta a fase (07 ou 08) que precisa mudar. Não serve "melhorar UX". -->

| Problema (comportamento observado) | Tela | Severidade | Frequência | Encaminhamento |
|---|---|---|---|---|

## Anti-padrões
- Tarefa escrita com o nome do botão dentro. A pessoa procura a palavra na tela e o teste vira busca textual.
- Moderador explicando a tela quando a pessoa hesita. Apaga exatamente o dado que o teste existe para coletar.
- Problema registrado como sugestão da pessoa. Sugestão não tem severidade nem frequência e o ranking do gate fica sem base.

## Modo reverso
Sem wireframes novos, rode o teste no produto atual: as 5 tarefas saem dos flows
críticos da fase 07. Dados antigos (suporte, analytics, gravações) entram no relatório
como frequência, mas não substituem sessões: sem 5 participantes, o gate não passa.
Tarefa que não dá para executar no produto atual vira `open_question` no STATE.md.
