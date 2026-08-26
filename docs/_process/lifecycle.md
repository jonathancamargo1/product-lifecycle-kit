# Ciclo de vida

Vinte fases, da ideia a retrospectiva. Cada fase produz um artefato e um gate.
Quais fases sao obrigatorias depende do tier (ver `tiers.md`).

| # | Fase | Template | Artefato produzido |
|---|---|---|---|
| 01 | Contexto | 01-contexto.md | Contexto e nao-escopo |
| 02 | Discovery | 02-discovery.md | Problem statement com evidencia |
| 03 | CSD e glossario | 03-csd.md | Matriz CSD e glossario |
| 04 | Personas e jornada | 04-personas-jornada.md | Personas e jornada as-is |
| 05 | PRD | 05-prd.md | PRD com metrica de sucesso |
| 06 | ADRs | 06-adr.md | Decisoes irreversiveis em MADR |
| 07 | Arquitetura de informacao | 07-flows-ia.md | Sitemap e user flows |
| 08 | Wireframes | 08-wireframes.md | Baixa fidelidade navegavel |
| 09 | Teste de usabilidade lo-fi | 09-usability.md | Roteiro e relatorio |
| 10 | UI | 10-ui.md | Alta fidelidade com estados |
| 11 | Spec tecnica | 11-spec.md | Spec estimavel |
| 12 | Backlog e handoff | 12-backlog-handoff.md | Vertical slices |
| 13 | Build | 13-build-log.md | Log de execucao |
| 14 | Review | 14-review.md | Review de codigo e QA visual |
| 15 | Red team | 15-threat-review.md | Riscos e mitigacoes |
| 16 | Verify | 16-verify.md | Aceite contra o PRD |
| 17 | Ship | 17-ship.md | Checklist de deploy |
| 18 | Handoff operacional | 18-runbook.md | Runbook |
| 19 | Medir | 19-medir.md | 30 dias de dado |
| 20 | Retro | 20-retro.md | Postmortem sem culpa |

## O que e um slug de fase

O slug e o nome do template sem a extensao. `05-prd`, `13-build-log`,
`15-threat-review`. E o valor do campo `phase` no frontmatter e a chave do
mapa `gates` em `docs/STATE.md`.

Os scripts aceitam prefixo que resolva para um unico slug. `13` e `13-build`
resolvem para `13-build-log`. Prefixo ambiguo e recusado com erro.

## Ordem

As fases avancam em ordem numerica. `gate-check` recusa iniciar uma fase se
alguma fase obrigatoria anterior, pelo tier declarado, ainda nao esta
aprovada (codigo SQ-01). Fase nao obrigatoria pelo tier e ignorada por
completo: nao aparece no painel da area e nao bloqueia nada.

## Modo reverso

Quando o kit e instalado num projeto em andamento, as fases ja vencidas sao
preenchidas a partir do que existe (codigo, documento, produto no ar). Cada
template tem a secao "Modo reverso" com a instrucao especifica. O que nao for
possivel recuperar vira `open_question` em `docs/STATE.md`, nunca suposicao.
