---
phase: 16-verify
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Verify

## Propósito
Provar que o que foi construído atende ao PRD da fase 05, requisito por requisito.
Provar com usuário real e com métrica emitindo dado, não com opinião de quem construiu.

## Gate de saída
Aceite completo contra o PRD, teste com usuário real feito, e métrica do PRD instrumentada e emitindo dado em produção.
- [ ] Cada requisito do PRD tem veredito passou ou falhou, com evidência linkada.
- [ ] Um usuário real, que não construiu nem revisou, executou a tarefa principal sozinho.
- [ ] A métrica do PRD aparece em produção com data e valor, query ou print anexado.
- [ ] Cada falha tem destino explícito: corrigir antes do ship ou backlog com justificativa.

## Esqueleto

### Aceite requisito a requisito
<!-- Uma linha por requisito do PRD, na mesma ordem e com o mesmo id do PRD.
Evidência é link para teste, gravação, print ou query.
Não serve: "testado ok", "funciona", linha sem id de requisito. -->

| Id do PRD | Requisito | Veredito | Evidência |
|---|---|---|---|
|  |  | passou / falhou |  |

### Teste com usuário real
<!-- Quem, quando, qual tarefa, sem ajuda. Escreva o que a pessoa fez, não o que
ela achou. Não serve: demo guiada, feedback de colega do time, "mostrei e gostaram". -->

- Pessoa e contexto:
- Tarefa pedida:
- Completou sozinha (sim / não) e onde travou:
- Tempo até concluir:

### Prova da métrica do PRD
<!-- Nome exato da métrica no PRD, onde é emitida, onde é lida, e uma leitura real
de produção. Não serve: "instrumentar depois", dado de staging, painel vazio. -->

- Métrica do PRD e ponto de emissão (arquivo e evento):
- Onde consultar (painel ou query):
- Primeira leitura em produção (data e valor):

### Falhas encontradas
<!-- Só o que falhou, uma linha por falha, sempre com dono nominal.
Não serve: "ajustes menores", "alguns bugs". -->

| Falha | Requisito afetado | Destino | Responsável |
|---|---|---|---|

### Open questions
<!-- Dúvida de negócio do aceite vira open_question no STATE.md. Não serve: responder sozinho. -->

## Anti-padrões
- Marcar requisito como passou sem link de evidência. O aceite vira memória, e memória não sobrevive ao próximo release.
- Chamar demo guiada de teste com usuário. Quem guia esconde justamente o ponto onde o usuário travaria sozinho.
- Declarar a métrica instrumentada porque o código emite o evento. Emitir não prova que o dado chega, persiste e é legível.

## Modo reverso
Sem PRD, extraia os requisitos do comportamento em produção e liste como requisitos observados, cada um marcado como não ratificado.
Para a métrica, procure o que já é coletado hoje (logs, analytics, banco) e registre o que existe de fato, com a query usada.
Se baseline ou alvo não existirem em lugar nenhum, isso vira open_question no STATE.md, nunca número inventado.
Se nunca houve teste com usuário, agende um antes do gate: o gate passa por evidência, não por histórico.
