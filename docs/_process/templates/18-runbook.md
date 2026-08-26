---
phase: 18-runbook
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Handoff operacional

## Propósito
Entregar o sistema para quem não o construiu, com README e runbook suficientes para operar.
O teste é literal: alguém de fora liga, diagnostica e reverte sem chamar quem escreveu o código.

## Gate de saída
README e runbook suficientes para alguém que não construiu operar o sistema.
- [ ] Uma pessoa que não participou do build executou este runbook do início ao fim e assinou embaixo.
- [ ] Essa pessoa subiu o ambiente e reverteu uma mudança usando só o que está escrito aqui.
- [ ] Todo alerta listado tem link direto e um primeiro passo escrito.
- [ ] Cada contato de escalonamento é nome de pessoa com canal, nunca nome de time.

## Esqueleto

### Como rodar e operar
<!-- Comandos literais e copiáveis. Segredos por nome, nunca valor. Não serve: "siga o README". -->

- Subir local:
- Onde roda em produção (serviço, região, repositório de deploy):
- Variáveis de ambiente obrigatórias (nome e onde buscar o valor):
- Tarefas de rotina e periodicidade:

### Como diagnosticar
<!-- Sintoma visível primeiro, com comando ou query exata. Não serve: "verificar os logs". -->

| Sintoma visível | Onde olhar (comando, painel ou query) | Causa provável |
|---|---|---|
|  |  |  |

### Como reverter
<!-- O plano da fase 17 na forma operacional, para alguém sob pressão. Não serve: só um link. -->

1. Desligar a feature flag (nome exato e onde):
2. Reverter deploy (comando exato):
3. Verificar que voltou (o que precisa aparecer):
- Quando NÃO reverter e escalonar direto:

### Alertas e onde ficam
<!-- Não serve: alerta sem primeiro passo, alerta que ninguém recebe. -->

| Alerta | Canal | Limite | Primeiro passo |
|---|---|---|---|
|  |  |  |  |

### Quem chamar
<!-- Pessoas nominais em ordem de acionamento. Não serve: "time de plataforma", lista sem ordem. -->

| Ordem | Pessoa | Canal | Assunto que resolve |
|---|---|---|---|
| 1 |  |  |  |

## Anti-padrões
- Runbook escrito por quem construiu e revisado por quem construiu. Ele preenche mentalmente os passos ausentes e o próximo operador não.
- Escalonamento apontando para um time. Às três da manhã, um nome de time não atende, uma pessoa atende.
- Diagnóstico organizado por componente interno. Quem opera vê sintoma, não arquitetura, e não acha a seção certa.

## Modo reverso
Extraia os comandos do histórico de shell, dos scripts de CI e do que o time realmente digita, não do que o README antigo diz.
Os alertas saem da ferramenta de monitoramento, com nome e limite exatos; o escalonamento sai do histórico dos últimos incidentes.
O que não existir (alerta ausente, dono ausente, passo que ninguém sabe) vira open_question no STATE.md, nunca chute plausível.
Valide passando o documento para alguém de fora executar: sem esse ensaio, o gate não fecha.
