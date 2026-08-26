---
phase: 14-review
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Review

## Propósito
Conferir código e resultado visual contra o hi-fi da fase 10 e a spec da fase 11.
Quem revisa não pode ser quem executou, e o registro precisa mostrar isso.

## Gate de saída
Checklist de código e QA visual contra o hi-fi concluídos por um papel distinto do executor.
- [ ] Campo revisor preenchido com nome de pessoa diferente do executor da fase 13.
- [ ] Todo item do checklist de código marcado, com achado ou com "sem achado".
- [ ] Cada tela do hi-fi comparada, com evidência (captura ou link) anexada.
- [ ] Todo achado bloqueante tem destino registrado: correção aplicada ou retorno à fase 11.

## Esqueleto

### Identificação
- Executor: <!-- nome de pessoa da fase 13. -->
- Revisor: <!-- nome de pessoa, papel distinto do executor. Mesma pessoa nos dois campos invalida o gate. -->
- Data e escopo revisado: <!-- commits, PRs ou slices. Não serve "a branch". -->

### Checklist de código
- [ ] Contratos de API batem com a fase 11 (payload, códigos de erro, auth).
- [ ] Modelo de dados implementado com os tipos, nulos e unicidades da fase 11.
- [ ] Tratamento de erro e timeout das integrações existe e é exercitado por teste.
- [ ] Logs, métricas e alertas da fase 11 emitem de fato, verificado em execução.
- [ ] Nenhum segredo, credencial ou dado sensível em código, log ou fixture.
<!-- Marque só o que você conferiu lendo ou rodando. Marcar por confiança no executor invalida a revisão. -->

### QA visual contra o hi-fi
<!-- Uma linha por tela: ID do frame da fase 10, estado testado (vazio, carregando, erro, cheio), resultado, evidência. Não serve "visualmente ok". -->

### Achados
<!-- Por achado: severidade (bloqueante ou não), onde, o que difere do esperado, destino. Divergência de spec volta para a fase 11, não vira ajuste combinado no review. -->

### Resultado
<!-- Escreva a conclusão do revisor e deixe `status: proposed`. Aprovação é escrita por humano no frontmatter, nunca pelo agente. -->

## Anti-padrões
- Executor revisando o próprio código por falta de gente disponível. O gate existe para trazer olho externo, e some inteiro.
- QA visual feito só na tela cheia e no desktop. Estados de vazio, erro e carregamento são onde o hi-fi é desrespeitado.
- Achado bloqueante fechado no chat sem entrar no artefato. Some do histórico e volta como bug sem dono.

## Modo reverso
Revise contra o que existe hoje: compare rotas e telas de produção com o hi-fi vigente e com a spec reconstruída na fase 11.
Se não há hi-fi, use a tela de produção como referência declarada e anote isso no campo de escopo.
Escolha um revisor sem commits no período revisado, e registre o nome dele.
Comportamento que ninguém sabe dizer se é intencional ou defeito vira `open_question` no STATE.md, nunca achado presumido nem aprovação tácita.
