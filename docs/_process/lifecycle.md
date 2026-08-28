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

## Codigo entra a partir da fase 13

Commit que toca codigo do produto exige a fase corrente ser `13-build-log` ou
posterior. O `commit-msg` recusa fora disso, com a lista dos arquivos e o que
se perde: codigo sem spec que o descreva, sem review de papel distinto do
executor, e sem rastro da decisao de produto que o originou.

Nao e bloqueio automatico. E recusa com o custo na tela e um caminho de saida
que exige ato deliberado: a linha `Sem-fase: <motivo, e quem autorizou>` no
proprio commit. Quem autoriza e humano, o agente pergunta. O `gate-check` conta
quantas existem (codigo `PH-01`, aviso), para a divida nao sumir de vista.

O registro vive na mensagem do commit, entao reescrita de historico
(`--amend`, rebase) pode apaga-lo, e `--no-verify` pula os hooks. Garantia
forte contra isso e protecao de branch no servidor, fora do alcance do kit.

O que conta como codigo do produto esta em `code-paths.md`, e e do projeto:
configuracao de CI, arquivo de build, lockfile e documentacao de raiz ficam de
fora por padrao. Barrar isso so ensinaria o time a autorizar no automatico, e
autorizacao que vira rotina para de significar alguma coisa.

Rode `bin/lifecycle/plan` para ver o que falta ate a fase de build.

## Modo reverso

Quando o kit e instalado num projeto em andamento, as fases ja vencidas sao
preenchidas a partir do que existe (codigo, documento, produto no ar). Cada
template tem a secao "Modo reverso" com a instrucao especifica. O que nao for
possivel recuperar vira `open_question` em `docs/STATE.md`, nunca suposicao.

Instale com `install.sh <alvo> --reverso`. Isso grava `import_mode: reverse` e
suspende o gate por fase: o agente reconstroi tudo e deixa em `proposed`, cada
afirmacao com seus ponteiros em `reconstructed_from`. A confirmacao acontece
uma vez, em bloco, numa sessao com um humano. Ver `gates.md`.

`bin/lifecycle/plan` muda no modo reverso: em vez da tabela de fases, abre pela
duvida. Perguntas em aberto primeiro, depois reconstrucoes sem ponteiro, depois
as com ponteiro para voce amostrar. Vinte documentos em ordem numa sessao so e
a receita da leitura diagonal, que e o que a confirmacao em bloco precisa
evitar para nao virar carimbo com passo extra.
