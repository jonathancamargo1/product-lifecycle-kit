---
phase: 20-retro
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Retro

## Propósito
Fechar o ciclo julgando sistema e processo, nunca pessoa.
Cada suposição crítica da fase 03 sai daqui confirmada ou refutada, e o aprendizado volta para o CONTEXT.md.

## Gate de saída
Postmortem sem culpa, suposições da fase 03 marcadas como confirmadas ou refutadas, e CONTEXT.md atualizado.
- [ ] Nenhuma linha do documento nomeia pessoa como causa; causas apontam para sistema ou processo.
- [ ] Toda suposição crítica da fase 03 aparece com veredito confirmada ou refutada e evidência.
- [ ] O commit que atualiza docs/_context/CONTEXT.md está linkado aqui.
- [ ] Cada ação tem dono nominal e prazo, ou é explicitamente descartada.

## Esqueleto

### Linha do tempo
<!-- Fatos com data, verificáveis em commit, ticket ou alerta. Não serve: interpretação, "achamos que". -->

| Data | Fato | Onde está registrado |
|---|---|---|
|  |  |  |

### Suposições da fase 03
<!-- Texto original de cada suposição crítica. Veredito binário, evidência das fases 16 e 19.
Não serve: "parcialmente", suposição reescrita depois do resultado, suposição omitida. -->

| Suposição (texto da fase 03) | Veredito | Evidência | Impacto no produto |
|---|---|---|---|
|  | confirmada / refutada |  |  |

### Postmortem sem culpa
<!-- Causa como propriedade do processo, uma entrada por problema.
Não serve: nome de pessoa, "faltou atenção", "erro humano" como causa final. -->

- Problema:
- O que tornou o erro possível (processo, ferramenta, ausência de checagem):
- Por que só foi percebido quando foi percebido, e qual defesa nova impede a repetição:

### O que funcionou e deve virar padrão
<!-- Prática concreta e repetível. Não serve: "boa comunicação", elogio. -->

### Ações
<!-- Uma ação por linha, com dono nominal e prazo. Sem dono, a ação não existe. -->

| Ação | Dono | Prazo |
|---|---|---|

### Volta para o CONTEXT.md
<!-- Fato novo, restrição descoberta ou suposição refutada que outros ciclos herdam.
Cole o trecho e linke o commit. Não aprove: deixe status proposed e espere um humano. -->

- Trecho a inserir ou substituir, com o commit ou PR:

## Anti-padrões
- Escrever "erro humano" como causa raiz. Encerra a investigação exatamente onde a causa de processo começaria a aparecer.
- Omitir suposição refutada da fase 03. A retro passa a contar só o que deu certo e o próximo ciclo repete a mesma aposta.
- Ação sem dono e sem prazo. Vira lista de boas intenções que ninguém cobra no ciclo seguinte.

## Modo reverso
Reconstrua a linha do tempo a partir de commits, tickets, alertas e canais de incidente, usando só o que tem data.
Sem documento da fase 03, extraia as suposições implícitas do que foi construído e marque cada uma como suposição reconstruída antes do veredito.
Suposição que não dá para julgar com o dado existente vira open_question no STATE.md, nunca veredito de conveniência.
Se não existe CONTEXT.md, crie o trecho como proposta e deixe a aprovação para um humano.
