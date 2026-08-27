---
phase: 12-backlog-handoff
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Backlog e handoff

## Propósito
Quebrar a spec em vertical slices entregáveis, cada uma com critério de aceite verificável por máquina.
Entregar ao executor o pacote de design das fases 08 e 10 junto, para que nada dependa de conversa.

## Gate de saída
Backlog fechado em vertical slices, cada slice com critério de aceite verificável por máquina, e pacote de design referenciado.
- [ ] Cada slice entrega valor de ponta a ponta, não uma camada isolada.
- [ ] Cada critério de aceite nomeia um teste automatizado (arquivo e caso), não prosa.
- [ ] Cada slice referencia a tela ou o flow correspondente das fases 08 e 10 por ID.
- [ ] Toda dúvida de negócio virou `open_question` no STATE.md, nenhuma virou suposição no card.

## Esqueleto

### Pacote de design referenciado
<!-- Links e IDs dos artefatos da fase 08 (wireframes, flows) e da fase 10 (hi-fi). Não serve "ver no Figma". Serve nome do frame e ID. -->

### Slices
<!-- Repita o bloco abaixo por slice. Ordene por dependência, nunca por camada técnica. -->

#### Slice NN: <nome>
- Valor entregue: <!-- o que a pessoa passa a conseguir fazer. Não serve "criar tabela X". -->
- Escopo técnico: <!-- endpoints, entidades e telas tocadas, citando as seções da fase 11. -->
- Design de referência: <!-- ID do frame hi-fi e do flow. Sem ID, a slice não está pronta para handoff. -->
- Critério de aceite:
  - [ ] <!-- teste automatizado nomeado: caminho do arquivo e nome do caso. Não serve "funciona conforme esperado". -->
  - [ ] <!-- segundo caso, cobrindo o erro previsto na spec. -->
- Fora de escopo: <!-- o que parece pertencer à slice e não pertence. -->

### Ordem de execução
<!-- Sequência das slices e a dependência que justifica cada posição. Não serve prioridade sem motivo declarado. -->

### Handoff
<!-- Quem executa (nome de pessoa), o que já está disponível (ambiente, dados de teste, credenciais) e o que falta. -->

## Anti-padrões
- Slice horizontal do tipo "criar o schema" ou "montar a API". Nada é demonstrável no fim e o gate vira opinião.
- Aceite escrito como "deve funcionar corretamente". Nenhuma máquina verifica isso e a fase 14 vira discussão de gosto.
- Card que resolve dúvida de negócio com uma decisão inventada no texto. A decisão entra sem dono e reaparece como bug depois.

## Modo reverso
Reconstrua as slices a partir do que já existe: agrupe rotas, telas e tabelas por jornada de usuário, nunca por camada técnica.
Cada slice já entregue recebe como critério de aceite o teste que hoje a cobre; se não existe teste, o critério é escrever esse teste.
O pacote de design vem das telas de produção ou do arquivo de design vigente, referenciado por ID.
Funcionalidade sem dono, sem teste e sem tela correspondente vira `open_question` no STATE.md, nunca aceite presumido.
