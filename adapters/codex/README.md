# Adaptador Codex

O Codex nao tem hooks de runtime. Ele le `AGENTS.md` na raiz do repositorio e
segue as instrucoes de la. Por isso, neste runtime o protocolo e imposto por
duas coisas apenas:

1. `AGENTS.md`, que manda rodar `session-open` como primeira acao e
   `session-close` como ultima.
2. Os git hooks `pre-commit` e `commit-msg`, instalados por `install.sh`, que
   nao dependem de nenhum agente.

Este adaptador nao instala nada alem disso. Ele existe para documentar o
mapeamento entre os dois runtimes.

## Mapeamento de comandos

| Acao | Claude Code | Codex |
|---|---|---|
| Abrir sessao | `/session-open` | `bin/lifecycle/session-open --agent codex` |
| Criar artefato | `/new-artifact ...` | `bin/lifecycle/new-artifact <fase> <area> "<titulo>" --owner <nome> [--inputs <paths>]` |
| Abrir decisao | `/decide ...` | `bin/lifecycle/decide --titulo "..." --afeta <path>` |
| Verificar gates | nao ha | `bin/lifecycle/gate-check` |
| Fechar sessao | `/session-close` | `bin/lifecycle/session-close --handoff <arquivo>` |

## O que voce perde sem hooks de runtime, e onde recupera

| Garantia | Claude Code | Codex |
|---|---|---|
| Contexto carregado na abertura | hook `SessionStart` roda `session-open` sozinho | `AGENTS.md` manda rodar como primeira acao |
| Escrita em arquivo protegido | hook `PreToolUse` bloqueia a ferramenta, exit 2 | `pre-commit` roda `guard-commit` e recusa o commit |
| Sessao encerrada sem handoff | hook `Stop` bloqueia o encerramento | `pre-commit` roda `guard-commit`, que recusa qualquer commit em `docs/` enquanto `session_open` for `true`. O trabalho nao entra sem handoff |
| Mensagem de commit de sessao | nenhuma vantagem | `commit-msg` valida em ambos |

A diferenca e o momento, nao o resultado. No Claude Code a escrita indevida e
barrada na hora. No Codex ela chega ao disco e e barrada no commit. Nos dois
casos ela nao entra no repositorio.

A unica garantia que fica so no adaptador e a da linha 1: o Claude Code carrega
o contexto sozinho, e no Codex isso depende de `AGENTS.md` ser lido. Nao ha
como uma maquina obrigar um agente a ler antes de agir. As outras tres
garantias sao impostas por git, nao por agente, e por isso valem em qualquer
runtime, inclusive num humano no editor.

## Sessao tipica

```sh
bin/lifecycle/session-open --agent codex
bin/lifecycle/new-artifact 01 onboarding "Contexto de Onboarding" --owner "Nome da Pessoa"
# preencha o artefato, marque status: proposed
printf '## Fiz\n- ...\n\n## Falta\n- ...\n\n## Cuidado com\n- ...\n' > /tmp/handoff.md
bin/lifecycle/session-close --handoff /tmp/handoff.md
```
