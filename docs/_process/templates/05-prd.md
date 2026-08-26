---
phase: 05-prd
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# PRD

## Propósito
Fixar o que será construído, para quem, e como saberemos em produção se funcionou.
É o contrato entre discovery e execução.

## Gate de saída
Existe métrica de sucesso mensurável em produção, com baseline e alvo, e o não escopo está escrito.
- [ ] A métrica tem baseline com data, alvo numérico e prazo de avaliação.
- [ ] Está escrito o evento, a query ou o dashboard que lê a métrica em produção.
- [ ] A seção "Não escopo" tem no mínimo 3 itens com motivo.
- [ ] Cada requisito tem critério de aceite verificável por outra pessoa.

## Esqueleto

### Problema
<!-- 2 a 3 linhas herdadas da fase 02, com os ids. Não serve problema sem fonte. -->

### Usuário
<!-- Qual persona da fase 04 e em que passo da jornada. Não serve "todos". -->

### Escopo
<!-- O que entra, em comportamento observável. Não serve nome de tela solto. -->

### Não escopo
<!-- Parte do gate. O que fica de fora, com motivo, incluindo o que foi pedido
e recusado. Não serve "fase 2". -->
- Fora:
  Motivo:

### Requisitos
<!-- Um por linha, com critério de aceite. Só must ou should. Não serve "rápido". -->
| id | Requisito | Critério de aceite | Prioridade |
|---|---|---|---|
| R1 |  |  |  |

### Métrica de sucesso
<!-- Uma métrica primária. Baseline medido, com data e fonte. Não serve número
sem baseline nem métrica que só existe em ambiente de teste. -->
Métrica primária:
Baseline (valor, data, fonte):
Alvo e prazo:
Métrica de guarda (o que não pode piorar):

### Instrumentação
<!-- Como a métrica é lida em produção, e quem monta isso antes do deploy.
Não serve "analytics já cobre". -->
Evento, campos e onde é emitido:
Query ou dashboard:
Dono da instrumentação:

## Anti-padrões
- Métrica sem baseline. Qualquer resultado depois vira vitória ou derrota narrativa.
- Instrumentação deixada para depois do deploy. O evento não nasce e a métrica morre.
- Não escopo vazio porque "tudo pode ser útil". O escopo cresce sem decisão registrada.

## Modo reverso
Escopo e requisitos saem do comportamento atual, lido em rotas, handlers, testes
e feature flags ligadas. Baseline sai do dado de produção de hoje, nunca de estimativa.
Sem evento para a métrica, crie um requisito de instrumentação e leve a dúvida
sobre o alvo para `open_question` no STATE.md.
