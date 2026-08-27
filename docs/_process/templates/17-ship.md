---
phase: 17-ship
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Ship

## Propósito
Colocar em produção com caminho de volta testado antes de existir usuário afetado.
Deploy sem rollback exercitado não é deploy, é aposta.

## Gate de saída
Checklist de deploy completo, feature flag nomeada, e rollback testado antes do go-live.
- [ ] Cada passo do checklist de deploy tem responsável nominal e ordem definida.
- [ ] A feature flag existe com nome exato, valor default e local de controle registrados.
- [ ] O rollback foi executado de verdade, com data, hora e quem executou, antes do go-live.
- [ ] Critério de abortar está escrito em número, não em julgamento.

## Esqueleto

### Checklist de deploy
<!-- Passos na ordem real de execução, cada um com dono nominal e verificação.
Não serve: "subir código", passo sem verificação, dono que é nome de time. -->

| # | Passo | Responsável | Como verificar que deu certo |
|---|---|---|---|
| 1 |  |  |  |

### Feature flag
<!-- Nome exato como está no código. Se não há flag, escreva por que e o que
substitui o desligamento rápido. Não serve: "flag de release", nome aproximado. -->

- Nome da flag e valor default no go-live:
- Onde se liga e desliga (painel, arquivo ou comando):
- Quem tem permissão para virar:
- Público exposto no go-live (percentual ou lista):

### Plano de rollback
<!-- Voltar ao estado anterior, incluindo dado e migração. Não serve: "reverter o commit" sozinho. -->

1. Passo:
2. Passo:
- Tempo estimado até estar de volta e o que acontece com dado gravado na exposição:

### Prova de que o rollback foi testado
<!-- Ensaio real antes do go-live, com dado representativo. Não serve: "é trivial", teste para depois. -->

- Data, hora e quem executou:
- Ambiente e tempo real medido:
- O que quebrou no ensaio e o que foi ajustado:

### Critério de abortar
<!-- Número e janela. Não serve: "se der problema", "se ficar ruim". -->

- Métrica observada, limite, janela e quem decide abortar:

## Anti-padrões
- Testar o rollback depois do go-live. O ensaio só tem valor enquanto errar ainda é barato.
- Flag sem dono de permissão. Na hora do incidente ninguém sabe quem pode virar e o desligamento vira reunião.
- Rollback que ignora migração de banco. O código volta, o schema não, e o sistema fica em estado que ninguém testou.

## Modo reverso
Extraia o checklist do que hoje é feito na mão para publicar, observando um deploy real e anotando cada passo na ordem.
A flag sai do código: procure o nome literal no repositório e no painel de configuração, não no que as pessoas lembram.
Se o rollback nunca foi exercitado, marque como não testado e ensaie antes do próximo go-live, sem passar o gate por histórico.
Se não existir critério numérico de abortar, isso vira open_question no STATE.md até um humano definir o limite.
