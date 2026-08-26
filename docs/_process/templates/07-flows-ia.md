---
phase: 07-flows-ia
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Arquitetura de informação

## Propósito
Definir onde cada coisa mora (sitemap) e por onde a pessoa passa para conseguir o que quer.
Provar, requisito por requisito, que o PRD inteiro tem caminho navegável.

## Gate de saída
O sitemap existe e todo requisito do PRD aparece em pelo menos um user flow.
- [ ] Sitemap cobre todas as telas, incluindo login, erro e estados de acesso negado.
- [ ] Cada requisito do PRD tem uma linha na tabela de rastreabilidade.
- [ ] Nenhuma linha da tabela está vazia ou com "a definir".
- [ ] Cada flow tem pelo menos um caminho de erro ou de saída sem sucesso.

## Esqueleto

### Sitemap
<!-- Árvore com indentação, um nível por profundidade de navegação. Cada nó é uma
     tela real com nome estável, ex "Detalhe do pedido". Não serve nome de menu
     ("Configurações gerais") sem tela por trás, nem "etc". -->
```
- Home
  - <Tela>
    - <Tela filha>
```

### User flows
<!-- Um bloco por flow. Cobrir os flows críticos primeiro. Passo é uma ação da pessoa
     ou uma resposta do sistema, na ordem. Não serve prosa descrevendo a experiência. -->

#### Flow F1: <objetivo em uma frase, do ponto de vista da pessoa>
- Ator: <papel do usuário, não persona de marketing>
- Gatilho: <o que faz o flow começar>
- Passos:
  1. <tela>: <ação da pessoa ou resposta do sistema>
  2. ...
- Caminho de erro: <o que acontece quando falha, e para onde a pessoa vai>
  <!-- Não serve "mostrar mensagem de erro" sem dizer para onde ela volta. -->
- Fim: <estado final observável, ex "pedido criado e visível na lista">

### Rastreabilidade PRD para flow
<!-- Uma linha por requisito do PRD, usando o ID do PRD. Requisito sem flow é
     bloqueio de gate, não item para depois. Se o requisito não couber em nenhum
     flow, abra `open_question` no STATE.md em vez de inventar tela. -->

| Requisito (ID do PRD) | Flow | Passo | Tela |
|---|---|---|---|
| REQ-01 | F1 | 3 | <tela> |

### Vocabulário e navegação
<!-- Nome oficial de cada objeto e ação, um por linha. É esse nome que vai para
     wireframe, UI e código. Não serve dois nomes para a mesma coisa. -->

## Anti-padrões
- Sitemap bonito com telas que nenhum flow visita. Tela órfã não tem dono e vira escopo escondido no build.
- Flow só com caminho feliz. O primeiro erro real em produção não tem destino, e o time inventa um às pressas.
- Requisito marcado como coberto por um flow que só o cita de passagem. A cobertura fica falsa e o gate deixa passar buraco.

## Modo reverso
Extraia o sitemap das rotas existentes (router, páginas, menu) e nomeie cada tela pelo
que ela mostra, não pelo path. Reconstrua os flows navegando o produto e anotando os
passos reais, incluindo os erros que conseguir provocar. Requisito do PRD sem tela não
vira flow suposto: abra `open_question` e deixe a linha marcada como não coberta.
