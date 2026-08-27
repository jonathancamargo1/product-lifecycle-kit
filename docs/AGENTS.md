# AGENTS

Fonte unica de regras para qualquer agente aqui. `CLAUDE.md` so importa este
arquivo; o Codex le direto daqui.

## Protocolo de sessao

Primeira acao da sessao e `session-open`. Ultima e `session-close`. Sem
excecao. Se a saida de `session-open` nao esta no seu contexto, rode antes de
qualquer outra coisa.

| Acao | Qualquer runtime | Claude Code tambem |
|---|---|---|
| Abrir sessao | `bin/lifecycle/session-open --agent <codex\|claude-code\|human>` | `/session-open` |
| Ver o que falta | `bin/lifecycle/plan` | `/plan` |
| Criar artefato | `bin/lifecycle/new-artifact <fase> <area> "<titulo>" --owner <nome> [--inputs <paths>]` | `/new-artifact` |
| Abrir decisao | `bin/lifecycle/decide --titulo "..." --afeta <path>` | `/decide` |
| Verificar tudo | `bin/lifecycle/gate-check` | nao ha |
| Fechar sessao | `bin/lifecycle/session-close --handoff <arquivo>` | `/session-close` |

`--inputs` e obrigatorio fora das fases 01 e 02. Um artefato por gate: para
substituir um que ja existe, use `--supersede`.

O handoff vai num arquivo temporario fora de `docs/_handoffs/`, com tres
secoes nesta ordem e no maximo 15 linhas: `## Fiz`, `## Falta`, `## Cuidado
com`. O script move para o lugar certo.

## Codigo so da fase 13 em diante

Commit que toca codigo do produto exige a fase corrente ser 13-build-log ou
posterior. O `commit-msg` recusa fora disso e explica o que se perde. Se
precisar entrar assim mesmo, **pergunte ao humano e espere a resposta**; com a
autorizacao dele, registre no commit a linha `Sem-fase: <por que entra sem
fase, e quem autorizou>`. Nunca escreva esse trailer sozinho: autorizar a si
mesmo e o mesmo que aprovar o proprio gate, e a regra 4 proibe.

## Regras

1. Processo, Contexto e Estado sao camadas separadas. Nunca as misture.
2. Carregue estado, verdades e a fase atual. Nunca o projeto inteiro.
3. Gate e verificado por maquina. Aprovado sem evidencia e erro, nao atalho.
4. Voce nao aprova nada. Escreva `proposed`; humano escreve `approved`.
5. Duvida de negocio vira `open_question` no STATE.md, nunca suposicao.
6. Estrutura nasce com o artefato. Pasta vazia e proibida.
7. Um artefato por gate. O anterior vira `superseded` com link para o novo.
8. Status vive em dois lugares apenas: frontmatter do artefato e STATE.md.
9. Template cabe em uma pagina. Campo que nao muda decisao e removido.
10. Kit anterior em `docs/templates`: reaproveite, nunca crie um segundo.
11. O que pode virar script ou hook vira. Nao confie na sua memoria.
12. O nucleo nao sabe qual agente o opera. Adaptador nunca substitui gate.
13. O kit e versionado. `docs/KIT_VERSION` diz qual versao esta instalada.

## O que voce pode e nao pode editar

Pode: artefatos `draft` ou `review` em `docs/areas/`, `docs/STATE.md`,
handoffs, e o codigo do projeto. Nao pode: `docs/_context/CONTEXT.md`, ADR
`accepted`, artefato `approved`, `docs/_process/` inteiro, e este arquivo.

Nunca aprove um gate. Nunca suponha regra de negocio. Nunca edite CONTEXT.md,
ADR aceita, artefato aprovado ou docs/_process sem decisao humana registrada.
