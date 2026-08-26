---
phase: 13-build-log
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Build

## Propósito
Registrar o que foi construído em cada slice, com o estado real da suíte de testes.
Serve também de barreira: mudança de spec ou de glossário não se resolve aqui.

## Gate de saída
Testes verdes, e nenhuma alteração de spec ou de glossário feita sem voltar à fase 11.
- [ ] Suíte completa executada, com comando, data e resultado colados abaixo.
- [ ] Todo teste nomeado na fase 12 existe e passa.
- [ ] Toda divergência em relação à spec está listada e tem o ID do retorno à fase 11.
- [ ] Nenhum termo do glossário foi criado ou redefinido no código sem passar pela fase 11.

## Esqueleto

### Slices concluídas
<!-- Uma linha por slice: ID, o que foi construído, commit ou PR. Não serve "diversos ajustes". -->

### Estado dos testes
<!-- Comando executado, data, total, passou, falhou, ignorado. Cole a saída resumida. Teste ignorado exige justificativa e nome de quem decidiu. -->

### Divergências em relação à spec
<!-- Por divergência: o que a fase 11 dizia, o que o código faz, e o ID do artefato de retorno à fase 11. -->
<!-- Regra dura: se a spec ou o glossário precisam mudar, pare, volte à fase 11 e mude lá. Não corrija a spec por aqui e não siga com o código divergente. -->

### Termos novos encontrados
<!-- Palavras que apareceram no código e não estão no glossário. Cada uma vira entrada da fase 11, nunca definição improvisada aqui. -->

### Decisões de implementação
<!-- Escolhas internas que não mudam contrato nem comportamento visível: nome de módulo, estrutura de pasta, biblioteca interna. Se muda contrato, é da fase 11. -->

### Débito assumido
<!-- O que ficou pior de propósito, por quê, e o que precisa acontecer para pagar. Sem prazo inventado. -->

### Pendências para a fase 14
<!-- O que o revisor precisa olhar de perto e por quê. Não serve "revisar tudo". -->

## Anti-padrões
- Ajustar a spec no próprio build log para o texto bater com o código entregue. O gate da fase 11 deixa de significar qualquer coisa.
- Registrar "testes passando localmente" sem comando e sem data. Ninguém reproduz e o gate deixa de ser verificável.
- Batizar um conceito novo no código e avisar depois. Glossário e código divergem em silêncio e a fase 14 revisa contra a base errada.

## Modo reverso
Reconstrua o log a partir do histórico de commits e dos PRs já mesclados, agrupando por slice da fase 12.
O estado dos testes vem de uma execução real feita agora, não do último resultado lembrado de CI.
Divergências saem da comparação entre o comportamento observado e a spec reconstruída na fase 11, e cada uma abre retorno à 11.
Motivo de decisão que ninguém lembra vira `open_question` no STATE.md, nunca justificativa reconstruída de memória.
