# Protocolo de sessao

Vale para qualquer runtime. Os git hooks nao dependem de agente nenhum, entao
valem sempre. Ja o campo `--agent` aceita apenas `codex`, `claude-code` ou
`human`: quem opera de um editor, Cursor incluido, abre a sessao como `human`.

## A regra

A primeira acao de qualquer sessao e `session-open`. A ultima e
`session-close`. Sem excecao.

Uma sessao que nao fechou deixa `session_open: true` em `docs/STATE.md`, e a
proxima `session-open` se recusa a abrir ate que a anterior seja fechada.
Isso e proposital: sessao sem handoff e contexto perdido.

## Abertura

```
bin/lifecycle/session-open --agent <codex|claude-code|human>
```

O script marca `session_open: true`, grava `session_agent`, incrementa
`session_counter` e imprime, nesta ordem e nada alem disso:

1. `AGENTS.md`
2. `docs/STATE.md`
3. o handoff apontado por `last_session`, se existir
4. `docs/_context/CONTEXT.md`
5. `docs/_context/principles.md`
6. o template da `current_phase`, se houver fase corrente

Depois roda `gate-check` e imprime o resultado. Esse conjunto e todo o
contexto da sessao. O agente nao carrega o projeto inteiro (principio 2).

No Claude Code, o hook `SessionStart` faz isso automaticamente. No Codex, a
instrucao esta em `AGENTS.md` e o comando e rodado como primeira acao.

## Fechamento

```
bin/lifecycle/session-close --handoff <arquivo>
```

O handoff tem exatamente tres secoes e no maximo 15 linhas de conteudo:

```markdown
## Fiz
## Falta
## Cuidado com
```

O script valida o handoff, move para `docs/_handoffs/YYYY-MM-DD-sessao-NN.md`,
atualiza `last_session`, marca `session_open: false`, roda `gate-check` e, se
o resultado for limpo, commita `docs` com a mensagem
`sessao NN: <fase> <resumo>`.

`session-close --check` apenas verifica se a sessao pode encerrar. Sai com 1 e
o motivo se algo falta. E o que o hook `Stop` do Claude Code usa.

Em qualquer runtime, com ou sem hook, o `pre-commit` recusa commit em `docs/`
enquanto `session_open` for `true`. Sessao aberta nao vira historico: ou fecha
com handoff, ou o trabalho fica fora do repositorio.

## Por que 15 linhas

Handoff longo nao e lido. O proximo agente precisa de tres coisas: o que
mudou, o que ficou pendente, e onde estao as minas. Todo o resto esta nos
artefatos e no `docs/STATE.md`.

## Duvida de negocio

Nunca vira suposicao. Vira `open_question` em `docs/STATE.md`, com id,
pergunta e data. Se a duvida bloqueia a fase, use `bin/lifecycle/decide` para
abrir uma decisao pendente e encerre a sessao.
