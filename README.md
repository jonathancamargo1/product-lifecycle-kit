# product-lifecycle-kit

Kit reutilizavel para conduzir um produto de software da ideia a retrospectiva,
sessao apos sessao, sem perder contexto e sem pular etapas.

Ele vive num repositorio privado seu e e instalado em qualquer repositorio de
projeto no momento em que o projeto comeca. Depois de instalado, o projeto pode
ser conduzido por Codex, por Claude Code, ou pelos dois em sessoes alternadas,
com o mesmo estado, os mesmos gates e o mesmo protocolo.

## O problema que ele resolve

Um agente de codigo esquece tudo entre uma sessao e outra. Sem estrutura, cada
sessao recomeca do zero, inventa regra de negocio que ninguem pediu, e declara
pronto o que ninguem verificou. O kit ataca as tres coisas: o estado sobrevive
em arquivo, as duvidas viram pergunta em vez de suposicao, e o "pronto" e
verificado por maquina.

## Arquitetura em tres aneis

| Anel | Conteudo | Funciona sem agente | Quem impoe |
|---|---|---|---|
| Nucleo | `docs/_process/`, `docs/_context/`, `docs/STATE.md`, `bin/`, templates | Sim | Os proprios scripts recusam operacoes invalidas |
| Enforcement comum | Git hooks `pre-commit` e `commit-msg` | Sim | Git, independentemente de quem commita |
| Adaptadores | `adapters/claude-code/`, `adapters/codex/` | Nao se aplica | O runtime do agente, quando disponivel |

A regra que sustenta o desenho: qualquer garantia que exista num adaptador
existe tambem, mesmo que mais tarde, no enforcement comum. Um projeto instalado
com `--adapters none` ainda tem todos os gates funcionando. A tabela de
correspondencia esta mais abaixo, e a prova de cada linha esta no modo B.

## Instalar

Clone o kit uma vez, numa pasta fixa da maquina:

```sh
git clone <url-do-seu-kit-privado> ~/product-lifecycle-kit
```

Depois, em cada projeto novo:

```sh
cd /caminho/do/projeto
git init                                  # se ainda nao for um repositorio
~/product-lifecycle-kit/install.sh . --adapters all
```

Opcoes de `--adapters`: `all` (padrao), `none`, ou uma lista como
`claude-code,codex`. `none` instala apenas o nucleo e os git hooks, o que ja
garante todos os gates.

A instalacao nunca sobrescreve arquivo existente: o que ja estava la e
preservado e listado no fim. Se o alvo tiver um kit anterior em
`docs/templates/`, os templates equivalentes sao reaproveitados e os que faltam
sao adicionados, num conjunto so.

Depois de instalar, declare o projeto e o tier em `docs/STATE.md`:

```yaml
project: nome-do-projeto
tier: 2
```

## Atualizar

```sh
cd ~/product-lifecycle-kit && git pull
~/product-lifecycle-kit/install.sh /caminho/do/projeto --update
```

O `--update` substitui apenas processo, scripts, git hooks e os adaptadores que
ja estavam instalados. Ele nunca toca em `docs/STATE.md`, `docs/_context/`,
`docs/_handoffs/`, `docs/areas/` nem no `AGENTS.md` que voce editou. Arquivo
que o projeto customizou nao e substituido: e listado para revisao manual. A
prova disso e o modo C, mais abaixo.

## Usar no dia a dia

O protocolo e o mesmo nos dois runtimes. A primeira acao da sessao e
`session-open`. A ultima e `session-close`. Sem excecao.

| Acao | Qualquer runtime | Claude Code tambem |
|---|---|---|
| Abrir sessao | `bin/lifecycle/session-open --agent <codex\|claude-code\|human>` | `/session-open` |
| Criar artefato | `bin/lifecycle/new-artifact <fase> <area> "<titulo>" --owner <nome> [--inputs <paths>]` | `/new-artifact` |
| Abrir decisao | `bin/lifecycle/decide --titulo "..." --afeta <path>` | `/decide` |
| Verificar gates | `bin/lifecycle/gate-check` | nao ha |
| Fechar sessao | `bin/lifecycle/session-close --handoff <arquivo>` | `/session-close` |

`session-open` imprime o contexto minimo da sessao e nada alem: `AGENTS.md`, o
estado, o ultimo handoff, o glossario, os principios e o template da fase
corrente. O agente nunca carrega o projeto inteiro.

No Claude Code, o hook `SessionStart` faz a abertura sozinho. No Codex, quem
manda rodar e o `AGENTS.md`.

## Quem aprova

O agente nunca aprova nada. Ele escreve `status: proposed` e para. Quem escreve
`approved` e um humano, editando duas coisas que precisam concordar: o
frontmatter do artefato e o gate correspondente em `docs/STATE.md`.

Isso e verificado por maquina, nao por convencao: `gate-check` recusa
`approved` sem `approved_by` e `approved_at` (FM-03) e recusa `approved_by` que
contenha `agent`, `codex`, `claude`, `ai` ou `bot` (FM-04).

Nao existe `bin/approve`, e isso e proposital. Um script de aprovacao
facilitaria justamente o que o kit quer manter dificil e deliberado.

## As 20 fases e os tiers

As fases estao em `docs/_process/lifecycle.md`, uma por template em
`docs/_process/templates/`. Quais sao obrigatorias depende do tier:

| Tier | Descricao | Fases obrigatorias |
|---|---|---|
| 1 | Ajuste: correcao, regra simples, mudanca sem nova tela | 01, 13, 14, 17 |
| 2 | Feature: nova rota ou capacidade em produto existente | 01, 02, 05, 07, 08, 11, 12, 13, 14, 15, 16, 17 |
| 3 | Produto novo ou usuario desconhecido | todas as 20 |

Fase nao obrigatoria pelo tier nao aparece no painel da area e nao bloqueia
nada. Na duvida entre dois tiers, escolha o maior.

## gate-check

Roda sozinho no `pre-commit`, no `session-open` e no `session-close`. Tambem
pode ser chamado direto, com `--phase <slug>` para perguntar se uma fase pode
comecar, e `--json` para consumo por script.

| Codigo | Verifica | Severidade |
|---|---|---|
| FM-01 | Frontmatter presente e parseavel em todo `.md` sob `docs/areas/` | erro |
| FM-02 | Campos obrigatorios presentes e `status` dentro do enum | erro |
| FM-03 | `approved` sem `approved_by` ou `approved_at` | erro |
| FM-04 | `approved_by` contem identificador de agente | erro |
| FM-05 | `superseded` sem `superseded_by` | erro |
| IN-01 | Path em `inputs` nao existe | erro |
| IN-02 | Input modificado apos `approved_at` | aviso STALE |
| IN-03 | `inputs` vazio fora das fases 01 e 02 | erro |
| ST-01 | `STATE.md` parseavel e com todos os campos | erro |
| ST-02 | Gate em `STATE.md` diverge do frontmatter do artefato | erro |
| ST-03 | Path de `evidence` nao existe | erro |
| SQ-01 | Fase em andamento com gate obrigatorio anterior nao aprovado | erro |
| DC-01 | `PENDING` em `decisions.log` sem `blocked_by` correspondente | erro |
| VC-01 | Termo proibido pelo glossario aparece no codigo ou nos documentos | erro |
| DR-01 | Pasta vazia sob `docs/areas/` | aviso |
| KV-01 | `docs/KIT_VERSION` ausente ou incompativel com os scripts | aviso |

Avisos nao alteram o exit code. `IN-03` nao consta da especificacao original e
esta registrado em `OPEN_QUESTIONS.md`.

## Adaptador versus enforcement comum

Cada garantia dos hooks do adaptador Claude Code tem um equivalente que nao
depende de agente nenhum. A coluna da direita e o que sustenta o modo Codex, e
esta demonstrada no modo B abaixo.

| Garantia | Hook do Claude Code | Equivalente comum | Onde a prova esta |
|---|---|---|---|
| Escrita em arquivo protegido nao entra | `PreToolUse` roda `guard-write`, exit 2 bloqueia a ferramenta | `pre-commit` roda `guard-commit`, que recusa o commit | Modo B, blocos 5 e 5a |
| Decisao humana libera a escrita | mesmo hook, apos entrada `DECIDED` | mesmo guard, apos entrada `DECIDED` | Modo B, blocos 6 e 6a |
| Sessao nao encerra sem handoff | `Stop` roda `session-close --check` e bloqueia | `guard-commit` recusa commit em `docs/` enquanto `session_open` for `true` | Modo B, sessoes 01 a 04, e `bin/tests/test_guards.py` |
| Sessao anterior nao fica aberta | consequencia do `Stop` | `session-open` se recusa a abrir | Modo A, bloco 3a |
| Mensagem de commit de sessao correta | nao ha | `commit-msg` valida `sessao NN` contra `session_counter` | Modo B, bloco 7 |
| Contexto carregado na abertura | `SessionStart` roda `session-open` | instrucao em `AGENTS.md` | Modo B, bloco 3 |

A ultima linha e a unica garantia que fica so no adaptador, e nao ha como impor
por maquina: nenhum script obriga um agente a ler antes de agir. As outras sao
impostas por git, e por isso valem em qualquer runtime, inclusive num humano no
editor. Isso esta registrado em `OPEN_QUESTIONS.md`, Q19.

A diferenca entre os dois runtimes e o momento, nao o resultado. No Claude Code
a escrita indevida e barrada na hora. No Codex ela chega ao disco e e barrada
no commit. Nos dois casos ela nao entra no repositorio.

## Estrutura

Arvore do kit:

```text
.gitignore
CHANGELOG.md
OPEN_QUESTIONS.md
README.md
VERSION
adapters/
  claude-code/
    .claude/
      commands/
        decide.md
        new-artifact.md
        session-close.md
        session-open.md
      hooks/
        guard-write.sh
        stop-gate.sh
      settings.json
    CLAUDE.md
    merge-settings.py
  codex/
    README.md
bin/
  _kitlib.py
  decide
  gate-check
  guard-commit
  guard-write
  new-artifact
  session-close
  session-open
  tests/
    __init__.py
    kitfixture.py
    test_gate_check.py
    test_guards.py
    test_new_artifact.py
    test_session.py
docs/
  AGENTS.md
  STATE.md
  _context/
    CONTEXT.md
    adr/
      0000-template.md
    decisions.log
    personas/
      .gitkeep
    principles.md
  _handoffs/
    .gitkeep
  _process/
    definition-of-done.md
    definition-of-ready.md
    gates.md
    lifecycle.md
    protected-paths.md
    session-protocol.md
    templates/
      01-contexto.md
      02-discovery.md
      03-csd.md
      04-personas-jornada.md
      05-prd.md
      06-adr.md
      07-flows-ia.md
      08-wireframes.md
      09-usability.md
      10-ui.md
      11-spec.md
      12-backlog-handoff.md
      13-build-log.md
      14-review.md
      15-threat-review.md
      16-verify.md
      17-ship.md
      18-runbook.md
      19-medir.md
      20-retro.md
      area-readme.md
    tiers.md
  areas/
    .gitkeep
git-hooks/
  commit-msg
  pre-commit
install.sh
proofs/
  README.md
  adapters-none.sh
  modo-a-claude-code.sh
  modo-b-codex.sh
  modo-c-update.sh
  varredura.sh
```

Arvore de um projeto alvo recem instalado com `install.sh . --adapters all`,
antes de qualquer fase comecar. `docs/areas/` nasce vazio porque estrutura so
nasce quando o artefato nasce:

```text
.claude
.claude/commands
.claude/commands/decide.md
.claude/commands/new-artifact.md
.claude/commands/session-close.md
.claude/commands/session-open.md
.claude/hooks
.claude/hooks/guard-write.sh
.claude/hooks/stop-gate.sh
.claude/settings.json
AGENTS.md
CLAUDE.md
bin
bin/lifecycle
bin/lifecycle/_kitlib.py
bin/lifecycle/decide
bin/lifecycle/gate-check
bin/lifecycle/guard-commit
bin/lifecycle/guard-write
bin/lifecycle/new-artifact
bin/lifecycle/session-close
bin/lifecycle/session-open
docs
docs/.kit-manifest
docs/KIT_VERSION
docs/STATE.md
docs/_context
docs/_context/CONTEXT.md
docs/_context/adr
docs/_context/adr/0000-template.md
docs/_context/decisions.log
docs/_context/principles.md
docs/_handoffs
docs/_process
docs/_process/definition-of-done.md
docs/_process/definition-of-ready.md
docs/_process/gates.md
docs/_process/lifecycle.md
docs/_process/protected-paths.md
docs/_process/session-protocol.md
docs/_process/templates
docs/_process/templates/01-contexto.md
docs/_process/templates/02-discovery.md
docs/_process/templates/03-csd.md
docs/_process/templates/04-personas-jornada.md
docs/_process/templates/05-prd.md
docs/_process/templates/06-adr.md
docs/_process/templates/07-flows-ia.md
docs/_process/templates/08-wireframes.md
docs/_process/templates/09-usability.md
docs/_process/templates/10-ui.md
docs/_process/templates/11-spec.md
docs/_process/templates/12-backlog-handoff.md
docs/_process/templates/13-build-log.md
docs/_process/templates/14-review.md
docs/_process/templates/15-threat-review.md
docs/_process/templates/16-verify.md
docs/_process/templates/17-ship.md
docs/_process/templates/18-runbook.md
docs/_process/templates/19-medir.md
docs/_process/templates/20-retro.md
docs/_process/templates/area-readme.md
docs/_process/tiers.md
docs/areas
docs/codex-adapter.md
```

Arvore de um projeto alvo depois de `install.sh . --adapters claude-code`, com
as quatro fases do tier 1 ja executadas. E a saida real do modo A:

```text
.
./.claude
./.claude/commands
./.claude/commands/decide.md
./.claude/commands/new-artifact.md
./.claude/commands/session-close.md
./.claude/commands/session-open.md
./.claude/hooks
./.claude/hooks/guard-write.sh
./.claude/hooks/stop-gate.sh
./.claude/settings.json
./AGENTS.md
./CLAUDE.md
./bin
./bin/lifecycle
./bin/lifecycle/_kitlib.py
./bin/lifecycle/decide
./bin/lifecycle/gate-check
./bin/lifecycle/guard-commit
./bin/lifecycle/guard-write
./bin/lifecycle/new-artifact
./bin/lifecycle/session-close
./bin/lifecycle/session-open
./docs
./docs/.kit-manifest
./docs/KIT_VERSION
./docs/STATE.md
./docs/_context
./docs/_context/CONTEXT.md
./docs/_context/adr
./docs/_context/adr/0000-template.md
./docs/_context/decisions.log
./docs/_context/principles.md
./docs/_handoffs
./docs/_handoffs/2026-08-26-sessao-01.md
./docs/_handoffs/2026-08-26-sessao-02.md
./docs/_handoffs/2026-08-26-sessao-03.md
./docs/_handoffs/2026-08-26-sessao-04.md
./docs/_process
./docs/_process/definition-of-done.md
./docs/_process/definition-of-ready.md
./docs/_process/gates.md
./docs/_process/lifecycle.md
./docs/_process/protected-paths.md
./docs/_process/session-protocol.md
./docs/_process/templates
./docs/_process/templates/01-contexto.md
./docs/_process/templates/02-discovery.md
./docs/_process/templates/03-csd.md
./docs/_process/templates/04-personas-jornada.md
./docs/_process/templates/05-prd.md
./docs/_process/templates/06-adr.md
./docs/_process/templates/07-flows-ia.md
./docs/_process/templates/08-wireframes.md
./docs/_process/templates/09-usability.md
./docs/_process/templates/10-ui.md
./docs/_process/templates/11-spec.md
./docs/_process/templates/12-backlog-handoff.md
./docs/_process/templates/13-build-log.md
./docs/_process/templates/14-review.md
./docs/_process/templates/15-threat-review.md
./docs/_process/templates/16-verify.md
./docs/_process/templates/17-ship.md
./docs/_process/templates/18-runbook.md
./docs/_process/templates/19-medir.md
./docs/_process/templates/20-retro.md
./docs/_process/templates/area-readme.md
./docs/_process/tiers.md
./docs/areas
./docs/areas/nucleo
./docs/areas/nucleo/01-contexto
./docs/areas/nucleo/01-contexto/contexto-do-prova-a.md
./docs/areas/nucleo/13-build-log
./docs/areas/nucleo/13-build-log/build-do-prova-a.md
./docs/areas/nucleo/14-review
./docs/areas/nucleo/14-review/review-do-prova-a.md
./docs/areas/nucleo/17-ship
./docs/areas/nucleo/17-ship/ship-do-prova-a.md
./docs/areas/nucleo/README.md
```

`bin/lifecycle/` tem esse nome para nao colidir com um `bin/` que o projeto ja
tenha. Os testes do kit nao sao copiados para o alvo.


## Prova de funcionamento

Tudo abaixo e saida real, colada sem edicao. Os scripts que geram cada bloco
estao em `proofs/` e podem ser rodados de novo do zero. Os modos A e B foram
executados com o kit na versao 1.0.0; o modo C e o que levou o kit a 1.1.0, que
e exatamente o que ele existe para demonstrar.

### Testes

Um caso que passa e um que falha para cada codigo de `gate-check`, mais os
testes dos guards, das sessoes e do `new-artifact`.

```text
$ python3 -m unittest discover bin/tests
...................................................................................................
----------------------------------------------------------------------
Ran 99 tests in 10.839s

OK
EXIT: 0
```

### Modo A: repositorio operado pelo Claude Code

`proofs/modo-a-claude-code.sh`. Instala com `--adapters claude-code`, declara o
projeto `prova-a` no tier 1 e roda as quatro fases obrigatorias do tier (01,
13, 14, 17) em quatro sessoes. Entre uma sessao e outra, um humano aprova o
gate editando o frontmatter e o `docs/STATE.md`.

Os hooks de runtime do Claude Code chamam exatamente estes scripts. Como nao ha
uma sessao do Claude Code viva dentro da prova, os scripts sao invocados
diretamente, que e o que o hook faria.

Demonstra, na ordem: `session-open` recusando abrir com a sessao anterior
aberta (3a); `session-close --check` saindo 1 com a sessao aberta e 0 depois
(3b e 3e); `gate-check --phase 13-build` saindo 1 antes de aprovar a fase 01 e
0 depois (3c e 4a); e `guard-write` saindo 2 num artefato aprovado (4b).

```text

----- 1. Instalacao -----
$ /home/user/product-lifecycle-kit/install.sh . --adapters claude-code
Instalando o product-lifecycle-kit 1.0.0 em /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-a.
Adaptador claude-code.

docs/KIT_VERSION: 1.0.0
Rodando gate-check no alvo.

gate-check: nenhuma ocorrencia.

Instalacao concluida. gate-check saiu com 0.
EXIT: 0

----- 2. Git hooks instalados -----
$ ls -1 .git/hooks/pre-commit .git/hooks/commit-msg
.git/hooks/commit-msg
.git/hooks/pre-commit
EXIT: 0
gate-check: nenhuma ocorrencia.
commit inicial ok

----- 3. Sessao 01, fase 01-contexto -----
$ python3 bin/lifecycle/session-open --agent claude-code
=== AGENTS.md
# AGENTS

Instrucoes para qualquer agente que opere este repositorio. Fonte unica de
regras: `CLAUDE.md` apenas importa este arquivo, o Codex le direto daqui.

## Protocolo de sessao

Primeira acao da sessao e `session-open`. Ultima e `session-close`. Sem
excecao. Se a saida de `session-open` nao esta no seu contexto, rode antes de
qualquer outra coisa.

## Comandos

| Acao | Qualquer runtime | Claude Code tambem |
|---|---|---|
| Abrir sessao | `bin/lifecycle/session-open --agent <codex\|claude-code\|human>` | `/session-open` |
| Criar artefato | `bin/lifecycle/new-artifact <fase> <area> "<titulo>" --owner <nome>` | `/new-artifact` |
| Abrir decisao | `bin/lifecycle/decide --titulo "..." --afeta <path>` | `/decide` |
| Verificar tudo | `bin/lifecycle/gate-check` | nao ha |
| Fechar sessao | `bin/lifecycle/session-close --handoff <arquivo>` | `/session-close` |

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

## O que voce pode editar

Artefatos em `docs/areas/` com status `draft` ou `review`, `docs/STATE.md`,
handoffs em `docs/_handoffs/`, e o codigo do projeto.

## O que voce nao pode editar

`docs/_context/CONTEXT.md`, ADR com status `accepted`, artefato com status
`approved`, `docs/_process/` inteiro, e este arquivo. Os guards recusam a
escrita e o `pre-commit` recusa o commit.

## Ao concluir um artefato

Marque `status: proposed`. Nunca `approved`. Registre o gate em
`docs/STATE.md` com `evidence` apontando para o artefato, e pare. Quem aprova
e humano, editando frontmatter e STATE.md.

Nunca aprove um gate. Nunca suponha regra de negocio. Nunca edite CONTEXT.md,
ADR aceita, artefato aprovado ou docs/_process sem decisao humana registrada.

=== docs/STATE.md
# STATE

Onde estamos. Muda toda sessao. Unico lugar, junto com o frontmatter dos
artefatos, onde status existe.

```yaml
project: prova-a
tier: 1                       # 1 | 2 | 3
current_phase: null
current_area: null
next_action: Escrever o contexto e o nao-escopo # uma frase imperativa
blocked_by: null              # slug de gate, id de decisao ou null
open_questions: []            # {id, question, raised_at, answered}
gates: {}                     # slug da fase: {status, evidence, by, date}
last_session: null            # path do ultimo handoff
session_counter: 1
session_open: true            # true entre session-open e session-close
session_agent: claude-code    # codex | claude-code | human
```

=== docs/_context/CONTEXT.md
# CONTEXT

O que e verdade neste projeto. Muda apenas por decisao registrada em
`_context/decisions.log`. Este arquivo e protegido: `guard-write` e
`guard-commit` recusam alteracao sem decisao `DECIDED` correspondente.

## Projeto

<!-- Uma frase: o que este produto faz e para quem. Sem adjetivo. -->

## Glossario

<!-- Termo canonico e definicao. Um termo por linha. O nome que aparece aqui e
     o nome que aparece no codigo, na UI e nos documentos. Divergencia entre
     glossario e codigo e bug de produto, nao questao de estilo. -->

| Termo | Definicao | Nao confundir com |
|---|---|---|

## Termos proibidos

<!-- Lido por gate-check, codigo VC-01. Um termo por item de lista. Aceita
     "- termo" e "- termo: motivo". Termo entre crases e tratado como
     literal. VC-01 procura cada termo em docs/, src/, app/ e packages/, sem
     diferenciar maiusculas, e falha se encontrar. Esta secao nao e varrida
     contra si mesma.

     Use para matar sinonimo que ja causou confusao: se o glossario diz
     "assinante", "usuario premium" nao pode sobreviver no codigo. -->

## Regras de negocio invariantes

<!-- Regra que o produto nao pode violar, com a origem (contrato, lei,
     decisao registrada). Se a origem for "alguem falou", nao e invariante,
     e suposicao: vire open_question no STATE.md. -->

## Restricoes tecnicas

<!-- Limite que nenhuma fase pode ignorar: stack imposta, integracao
     obrigatoria, janela de manutencao, requisito de compliance. -->

## Metricas canonicas

<!-- Como cada metrica citada nos PRDs e calculada. Duas definicoes da mesma
     metrica e a forma mais comum de duas equipes discordarem por meses. -->

=== docs/_context/principles.md
# Principios do produto

Criterios de desempate. Quando duas opcoes sao defensaveis, o principio
decide, e a decisao nao precisa subir.

<!-- Escreva cada principio como um trade-off com lado escolhido, no formato
     "X antes de Y". Principio que ninguem pode discordar nao e principio, e
     slogan: "qualidade importa" nao decide nada. -->

## 1. PREENCHER

<!-- O trade-off em uma frase. -->

Consequencia aceita: <!-- o que se perde ao escolher esse lado. Todo
principio custa alguma coisa. Se nao custa, nao e principio. -->

Exemplo real: <!-- uma decisao concreta ja tomada por esse principio. -->

## 2. PREENCHER

Consequencia aceita:

Exemplo real:

## 3. PREENCHER

Consequencia aceita:

Exemplo real:

<!-- Tres a cinco principios. Mais que isso ninguem lembra na hora de decidir,
     e principio esquecido nao desempata nada. -->

## Como usar

Este arquivo e lido no inicio de toda sessao, junto com CONTEXT.md. O agente
usa para decidir sozinho o que e desempate, e apenas isso. Duvida de negocio
continua virando open_question, nunca suposicao apoiada em principio.

=== gate-check
gate-check: nenhuma ocorrencia.

Sessao 01 aberta para o agente claude-code.
Ultima acao da sessao: session-close --handoff <arquivo>.
EXIT: 0

----- 3a. session-open recusa abrir com a sessao anterior aberta -----
$ python3 bin/lifecycle/session-open --agent claude-code
session-open: a sessao 1 ainda esta aberta (agente claude-code).
Feche primeiro com: session-close --handoff <arquivo>
EXIT: 1

----- 3b. session-close --check recusa enquanto a sessao esta aberta -----
$ python3 bin/lifecycle/session-close --check
Sessao nao pode encerrar: a sessao 1 esta aberta e nao tem handoff.
Feche com: session-close --handoff <arquivo>
EXIT: 1

----- 3c. gate-check --phase 13-build ANTES de aprovar a fase 01 -----
$ python3 bin/lifecycle/gate-check --phase 13-build
[SQ-01] docs/STATE.md:9 fase 13-build-log exige a fase obrigatoria 01-contexto aprovada, mas ela esta nao registrado
gate-check: 1 erro(s), 0 aviso(s).
EXIT: 1
$ python3 bin/lifecycle/new-artifact 01-contexto nucleo Contexto do prova-a --owner Jonathan Camargo
Artefato criado: docs/areas/nucleo/01-contexto/contexto-do-prova-a.md
Gate 01-contexto registrado como in_progress em docs/STATE.md.
Preencha o template e marque status: proposed. Nunca approved.
EXIT: 0
artefato docs/areas/nucleo/01-contexto/contexto-do-prova-a.md marcado proposed pelo agente

----- 3d. session-close com handoff -----
$ python3 bin/lifecycle/session-close --handoff /tmp/handoff-a.md
Handoff registrado em docs/_handoffs/2026-08-26-sessao-01.md.
gate-check: nenhuma ocorrencia.
Commit: sessao 01: 01-contexto escrevi o contexto e o nao-escopo
EXIT: 0

----- 3e. session-close --check depois de fechar -----
$ python3 bin/lifecycle/session-close --check
session-close: nada pendente, a sessao pode encerrar.
EXIT: 0

----- 4. Humano aprova o gate 01 -----
gate 01-contexto aprovado por Jonathan Camargo em 2026-08-26
gate-check: nenhuma ocorrencia.
commit da aprovacao ok

----- 4a. gate-check --phase 13-build DEPOIS de aprovar a fase 01 -----
$ python3 bin/lifecycle/gate-check --phase 13-build
gate-check: nenhuma ocorrencia para iniciar 13-build-log.
EXIT: 0

----- 4b. guard-write num artefato aprovado -----
$ python3 bin/lifecycle/guard-write docs/areas/nucleo/01-contexto/contexto-do-prova-a.md
Arquivo protegido. Abra uma decisao (script decide) ou resolva a pendente.
docs/areas/nucleo/01-contexto/contexto-do-prova-a.md (artefato aprovado)
EXIT: 2

----- 5. Sessao seguinte, fase 13-build -----
$ python3 bin/lifecycle/session-open --agent claude-code
[saida completa suprimida, ver sessao 01]
EXIT: 0
$ python3 bin/lifecycle/new-artifact 13-build nucleo Build do prova-a --owner Jonathan Camargo --inputs docs/areas/nucleo/01-contexto/contexto-do-prova-a.md
Artefato criado: docs/areas/nucleo/13-build-log/build-do-prova-a.md
Gate 13-build-log registrado como in_progress em docs/STATE.md.
Preencha o template e marque status: proposed. Nunca approved.
EXIT: 0
artefato docs/areas/nucleo/13-build-log/build-do-prova-a.md marcado proposed pelo agente
$ python3 bin/lifecycle/session-close --handoff /tmp/handoff-a.md
Handoff registrado em docs/_handoffs/2026-08-26-sessao-02.md.
gate-check: nenhuma ocorrencia.
Commit: sessao 02: 13-build-log executei a fase 13-build
EXIT: 0
gate 13-build-log aprovado por Jonathan Camargo em 2026-08-26
gate-check: nenhuma ocorrencia.
commit da aprovacao ok

----- 5. Sessao seguinte, fase 14-review -----
$ python3 bin/lifecycle/session-open --agent claude-code
[saida completa suprimida, ver sessao 01]
EXIT: 0
$ python3 bin/lifecycle/new-artifact 14-review nucleo Review do prova-a --owner Jonathan Camargo --inputs docs/areas/nucleo/13-build-log/build-do-prova-a.md
Artefato criado: docs/areas/nucleo/14-review/review-do-prova-a.md
Gate 14-review registrado como in_progress em docs/STATE.md.
Preencha o template e marque status: proposed. Nunca approved.
EXIT: 0
artefato docs/areas/nucleo/14-review/review-do-prova-a.md marcado proposed pelo agente
$ python3 bin/lifecycle/session-close --handoff /tmp/handoff-a.md
Handoff registrado em docs/_handoffs/2026-08-26-sessao-03.md.
gate-check: nenhuma ocorrencia.
Commit: sessao 03: 14-review executei a fase 14-review
EXIT: 0
gate 14-review aprovado por Jonathan Camargo em 2026-08-26
gate-check: nenhuma ocorrencia.
commit da aprovacao ok

----- 5. Sessao seguinte, fase 17-ship -----
$ python3 bin/lifecycle/session-open --agent claude-code
[saida completa suprimida, ver sessao 01]
EXIT: 0
$ python3 bin/lifecycle/new-artifact 17-ship nucleo Ship do prova-a --owner Jonathan Camargo --inputs docs/areas/nucleo/14-review/review-do-prova-a.md
Artefato criado: docs/areas/nucleo/17-ship/ship-do-prova-a.md
Gate 17-ship registrado como in_progress em docs/STATE.md.
Preencha o template e marque status: proposed. Nunca approved.
EXIT: 0
artefato docs/areas/nucleo/17-ship/ship-do-prova-a.md marcado proposed pelo agente
$ python3 bin/lifecycle/session-close --handoff /tmp/handoff-a.md
Handoff registrado em docs/_handoffs/2026-08-26-sessao-04.md.
gate-check: nenhuma ocorrencia.
Commit: sessao 04: 17-ship executei a fase 17-ship
EXIT: 0
gate 17-ship aprovado por Jonathan Camargo em 2026-08-26
gate-check: nenhuma ocorrencia.
commit da aprovacao ok

----- 6. Estado final -----
$ python3 bin/lifecycle/gate-check
gate-check: nenhuma ocorrencia.
EXIT: 0
$ sed -n /```yaml/,/```/p docs/STATE.md
```yaml
project: prova-a
tier: 1                       # 1 | 2 | 3
current_phase: 17-ship
current_area: nucleo
next_action: Escrever o contexto e o nao-escopo # uma frase imperativa
blocked_by: null              # slug de gate, id de decisao ou null
open_questions: []            # {id, question, raised_at, answered}
gates:                        # slug da fase: {status, evidence, by, date}
  01-contexto:
    status: approved
    evidence: docs/areas/nucleo/01-contexto/contexto-do-prova-a.md
    by: Jonathan Camargo
    date: 2026-08-26
  13-build-log:
    status: approved
    evidence: docs/areas/nucleo/13-build-log/build-do-prova-a.md
    by: Jonathan Camargo
    date: 2026-08-26
  14-review:
    status: approved
    evidence: docs/areas/nucleo/14-review/review-do-prova-a.md
    by: Jonathan Camargo
    date: 2026-08-26
  17-ship:
    status: approved
    evidence: docs/areas/nucleo/17-ship/ship-do-prova-a.md
    by: Jonathan Camargo
    date: 2026-08-26
last_session: docs/_handoffs/2026-08-26-sessao-04.md # path do ultimo handoff
session_counter: 4
session_open: false           # true entre session-open e session-close
session_agent: claude-code    # codex | claude-code | human
```
EXIT: 0
$ git log --oneline
9d65f46 humano aprova o gate 17-ship
cefc7da sessao 04: 17-ship executei a fase 17-ship
0ba37f0 humano aprova o gate 14-review
3d624ef sessao 03: 14-review executei a fase 14-review
195a7ac humano aprova o gate 13-build-log
7a1d4c8 sessao 02: 13-build-log executei a fase 13-build
b42a49c humano aprova o gate 01-contexto
90d5251 sessao 01: 01-contexto escrevi o contexto e o nao-escopo
e370d6e instala o product-lifecycle-kit
EXIT: 0
```

### Modo B: repositorio operado pelo Codex

`proofs/modo-b-codex.sh`. Instala com `--adapters codex`, que nao instala hook
de runtime nenhum. A mesma sequencia de quatro sessoes, com `--agent codex`.

Alem do ciclo, demonstra as tres coisas que so o modo B pode provar, porque sao
as que existem sem rede de seguranca de runtime: o `git commit` de uma edicao
num artefato aprovado sem decisao e abortado pelo `pre-commit` com a saida de
`guard-commit` (5a); o mesmo commit passa depois de uma entrada `DECIDED` em
`decisions.log` com o path em `Afeta` (6a); e o `commit-msg` recusa
`sessao 99` quando o `session_counter` e 4 (7).

```text

----- 1. Instalacao sem nenhum hook de runtime -----
$ /home/user/product-lifecycle-kit/install.sh . --adapters codex
Instalando o product-lifecycle-kit 1.0.0 em /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b.
Adaptador codex.

docs/KIT_VERSION: 1.0.0
Rodando gate-check no alvo.

gate-check: nenhuma ocorrencia.

Instalacao concluida. gate-check saiu com 0.
EXIT: 0

----- 2. Nenhum artefato de runtime de agente foi instalado -----
$ ls -a .
.
..
.git
AGENTS.md
bin
docs
EXIT: 0
$ ls .git/hooks/pre-commit .git/hooks/commit-msg
.git/hooks/commit-msg
.git/hooks/pre-commit
EXIT: 0
gate-check: nenhuma ocorrencia.
commit inicial ok

----- 3. Sessao 01, fase 01-contexto, invocando os scripts direto -----
$ python3 bin/lifecycle/session-open --agent codex
[cabecalho de AGENTS.md, STATE.md, CONTEXT.md e principles.md suprimido aqui, 171 linhas]
gate-check: nenhuma ocorrencia.

Sessao 01 aberta para o agente codex.
Ultima acao da sessao: session-close --handoff <arquivo>.
EXIT: 0
$ python3 bin/lifecycle/new-artifact 01-contexto nucleo Contexto do prova-b --owner Jonathan Camargo
Artefato criado: docs/areas/nucleo/01-contexto/contexto-do-prova-b.md
Gate 01-contexto registrado como in_progress em docs/STATE.md.
Preencha o template e marque status: proposed. Nunca approved.
EXIT: 0
artefato docs/areas/nucleo/01-contexto/contexto-do-prova-b.md marcado proposed pelo agente
$ python3 bin/lifecycle/session-close --handoff /tmp/handoff-b.md
Handoff registrado em docs/_handoffs/2026-08-26-sessao-01.md.
gate-check: nenhuma ocorrencia.
Commit: sessao 01: 01-contexto escrevi o contexto e o nao-escopo
EXIT: 0
gate 01-contexto aprovado por Jonathan Camargo em 2026-08-26
gate-check: nenhuma ocorrencia.
commit da aprovacao ok

----- 4. Sessao seguinte, fase 13-build -----
$ python3 bin/lifecycle/session-open --agent codex
EXIT: 0
$ python3 bin/lifecycle/new-artifact 13-build nucleo Build do prova-b --owner Jonathan Camargo --inputs docs/areas/nucleo/01-contexto/contexto-do-prova-b.md
Artefato criado: docs/areas/nucleo/13-build-log/build-do-prova-b.md
Gate 13-build-log registrado como in_progress em docs/STATE.md.
Preencha o template e marque status: proposed. Nunca approved.
EXIT: 0
artefato docs/areas/nucleo/13-build-log/build-do-prova-b.md marcado proposed pelo agente
$ python3 bin/lifecycle/session-close --handoff /tmp/handoff-b.md
Handoff registrado em docs/_handoffs/2026-08-26-sessao-02.md.
gate-check: nenhuma ocorrencia.
Commit: sessao 02: 13-build-log executei a fase 13-build
EXIT: 0
gate 13-build-log aprovado por Jonathan Camargo em 2026-08-26
gate-check: nenhuma ocorrencia.
commit da aprovacao ok

----- 4. Sessao seguinte, fase 14-review -----
$ python3 bin/lifecycle/session-open --agent codex
EXIT: 0
$ python3 bin/lifecycle/new-artifact 14-review nucleo Review do prova-b --owner Jonathan Camargo --inputs docs/areas/nucleo/13-build-log/build-do-prova-b.md
Artefato criado: docs/areas/nucleo/14-review/review-do-prova-b.md
Gate 14-review registrado como in_progress em docs/STATE.md.
Preencha o template e marque status: proposed. Nunca approved.
EXIT: 0
artefato docs/areas/nucleo/14-review/review-do-prova-b.md marcado proposed pelo agente
$ python3 bin/lifecycle/session-close --handoff /tmp/handoff-b.md
Handoff registrado em docs/_handoffs/2026-08-26-sessao-03.md.
gate-check: nenhuma ocorrencia.
Commit: sessao 03: 14-review executei a fase 14-review
EXIT: 0
gate 14-review aprovado por Jonathan Camargo em 2026-08-26
gate-check: nenhuma ocorrencia.
commit da aprovacao ok

----- 4. Sessao seguinte, fase 17-ship -----
$ python3 bin/lifecycle/session-open --agent codex
EXIT: 0
$ python3 bin/lifecycle/new-artifact 17-ship nucleo Ship do prova-b --owner Jonathan Camargo --inputs docs/areas/nucleo/14-review/review-do-prova-b.md
Artefato criado: docs/areas/nucleo/17-ship/ship-do-prova-b.md
Gate 17-ship registrado como in_progress em docs/STATE.md.
Preencha o template e marque status: proposed. Nunca approved.
EXIT: 0
artefato docs/areas/nucleo/17-ship/ship-do-prova-b.md marcado proposed pelo agente
$ python3 bin/lifecycle/session-close --handoff /tmp/handoff-b.md
Handoff registrado em docs/_handoffs/2026-08-26-sessao-04.md.
gate-check: nenhuma ocorrencia.
Commit: sessao 04: 17-ship executei a fase 17-ship
EXIT: 0
gate 17-ship aprovado por Jonathan Camargo em 2026-08-26
gate-check: nenhuma ocorrencia.
commit da aprovacao ok

----- 5. Edicao num artefato aprovado. Nada impede a escrita no disco. -----
$ git add docs/areas/nucleo/01-contexto/contexto-do-prova-b.md
EXIT: 0

----- 5a. git commit e abortado pelo pre-commit, com a saida de guard-commit -----
$ git commit -m altera um artefato aprovado sem decisao
gate-check: nenhuma ocorrencia.
Arquivo protegido. Abra uma decisao (script decide) ou resolva a pendente.
  docs/areas/nucleo/01-contexto/contexto-do-prova-b.md (artefato aprovado)
EXIT: 1

----- 5b. o artefato aprovado continua intocado no repositorio -----
$ git log --oneline -1 -- docs/areas/nucleo/01-contexto/contexto-do-prova-b.md
aa1d370 humano aprova o gate 01-contexto
EXIT: 0

----- 6. Entrada DECIDED em decisions.log liberando o mesmo path -----
decisao D-0001 registrada como DECIDED, Afeta: docs/areas/nucleo/01-contexto/contexto-do-prova-b.md
$ git add -A
EXIT: 0

----- 6a. o mesmo commit agora passa -----
$ git commit -m corrige o artefato aprovado sob a decisao D-0001
gate-check: nenhuma ocorrencia.
[main c5a90b4] corrige o artefato aprovado sob a decisao D-0001
 2 files changed, 8 insertions(+)
EXIT: 0

----- 7. commit-msg recusa sessao 99 quando o session_counter e 4 -----
$ grep session_counter docs/STATE.md
session_counter: 4
$ git commit -m sessao 99: 17-ship resumo mentiroso
gate-check: nenhuma ocorrencia.
commit-msg: a mensagem diz sessao 99 mas o session_counter em docs/STATE.md e 4.
EXIT: 1

----- 7a. a mesma mudanca passa com uma mensagem que nao e de sessao -----
$ git commit -m adiciona uma nota solta
gate-check: nenhuma ocorrencia.
[main d2d40b3] adiciona uma nota solta
 1 file changed, 1 insertion(+)
 create mode 100644 nota.txt
EXIT: 0

----- 8. Estado final -----
$ python3 bin/lifecycle/gate-check
gate-check: nenhuma ocorrencia.
EXIT: 0
$ git log --oneline
d2d40b3 adiciona uma nota solta
c5a90b4 corrige o artefato aprovado sob a decisao D-0001
d260cd8 humano aprova o gate 17-ship
5436d41 sessao 04: 17-ship executei a fase 17-ship
b57d32f humano aprova o gate 14-review
92a6c69 sessao 03: 14-review executei a fase 14-review
c55a7a5 humano aprova o gate 13-build-log
637befc sessao 02: 13-build-log executei a fase 13-build
aa1d370 humano aprova o gate 01-contexto
1f20976 sessao 01: 01-contexto escrevi o contexto e o nao-escopo
6847eb5 instala o product-lifecycle-kit
EXIT: 0
```

### Modo C: atualizacao

`proofs/modo-c-update.sh`. Com o projeto `prova-b` ja instalado na versao
1.0.0, sobe o kit para 1.1.0, acrescenta a secao correspondente ao
`CHANGELOG.md` e roda `install.sh <prova-b> --update`.

O que a prova mede: uma soma sha256 de tudo que o `--update` tem proibido
tocar, tirada antes e depois. `docs/STATE.md`, `docs/_handoffs/` e
`docs/areas/` ficam identicos; so `docs/KIT_VERSION`, os scripts e o manifesto
mudam.

```text

----- 1. Estado antes do update -----
$ cat /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b/docs/KIT_VERSION
1.0.0
EXIT: 0
impressao digital de STATE.md + _handoffs + areas: fc21c651c595c5279f5b98d007dd4f1028214359fbf3fcc46bd65432c857a1cf

----- 2. Nova versao do kit -----
VERSION agora e 1.1.0 e o CHANGELOG.md ganhou a secao 1.1.0
$ cat /home/user/product-lifecycle-kit/VERSION
1.1.0
EXIT: 0

----- 3. install.sh --update -----
$ /home/user/product-lifecycle-kit/install.sh /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b --update
Atualizando o kit em /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b para a versao 1.1.0.
Versao anterior: 1.0.0
  adaptador claude-code nao estava instalado, pulando
Adaptador codex.

Mudancas desta versao (CHANGELOG.md):
  ## 1.1.0
  
  Versao usada para provar o fluxo `install.sh --update` (modo C do README).
  Nenhuma mudanca de comportamento em relacao a 1.0.0: processo e scripts sao
  reenviados ao alvo e `docs/KIT_VERSION` passa a 1.1.0, sem tocar em estado,
  contexto, handoffs ou artefatos.
  

docs/KIT_VERSION: 1.1.0
Rodando gate-check no alvo.

gate-check: nenhuma ocorrencia.

Instalacao concluida. gate-check saiu com 0.
EXIT: 0

----- 4. KIT_VERSION mudou -----
$ cat /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b/docs/KIT_VERSION
1.1.0
EXIT: 0

----- 5. STATE.md, _handoffs e areas nao mudaram -----
antes:  fc21c651c595c5279f5b98d007dd4f1028214359fbf3fcc46bd65432c857a1cf
depois: fc21c651c595c5279f5b98d007dd4f1028214359fbf3fcc46bd65432c857a1cf
IGUAIS. O update nao tocou em estado, handoffs nem artefatos.

----- 5a. git status do alvo depois do update -----
$ git -C /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b status --short
 M bin/lifecycle/_kitlib.py
 M docs/.kit-manifest
 M docs/KIT_VERSION
EXIT: 0

----- 6. gate-check continua limpo depois do update -----
$ git -C /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b --no-pager log --oneline -1
d2d40b3 adiciona uma nota solta
EXIT: 0
$ python3 bin/lifecycle/gate-check
gate-check: nenhuma ocorrencia.
EXIT: 0
```

### Instalacao sem nenhum adaptador

Criterio de aceite: `install.sh --adapters none` num repositorio vazio termina
com `gate-check` exit 0 e os dois git hooks instalados. E o caso que prova o
principio 12, o de que o nucleo nao depende de agente nenhum.

```text
$ /home/user/product-lifecycle-kit/install.sh . --adapters none
Instalando o product-lifecycle-kit 1.0.0 em /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-none.

docs/KIT_VERSION: 1.0.0
Rodando gate-check no alvo.

gate-check: nenhuma ocorrencia.

Instalacao concluida. gate-check saiu com 0.
EXIT: 0

----- os dois git hooks estao instalados e executaveis -----
$ ls -l .git/hooks/pre-commit .git/hooks/commit-msg
-rwxr-xr-x 1 root root 2399 Aug 26 23:46 .git/hooks/commit-msg
-rwxr-xr-x 1 root root  672 Aug 26 23:46 .git/hooks/pre-commit
EXIT: 0

----- nenhum arquivo de adaptador foi instalado -----
$ ls -a .
.
..
.git
AGENTS.md
bin
docs
EXIT: 0

----- gate-check no alvo -----
$ python3 bin/lifecycle/gate-check
gate-check: nenhuma ocorrencia.
EXIT: 0
```

### Varredura de caracteres e limites

Nenhum arquivo do kit contem o caractere travessao longo nem emoji. Nenhum
template passa de 80 linhas, `docs/AGENTS.md` nao passa de 60, e
`adapters/claude-code/CLAUDE.md` tem exatamente 2. Nenhuma pasta vazia fora dos
`.gitkeep` previstos.

O proprio scanner nunca escreve o travessao literalmente: ele monta o caractere
a partir do codepoint U+2014. Se o escrevesse, o arquivo do scanner seria uma
ocorrencia e a varredura acusaria a si mesma.

```text
$ grep -rn --exclude-dir=.git -e "<U+2014>" .
EXIT: 1

$ python3 varredura de codepoints em todos os arquivos versionados
arquivos versionados verificados: 75
ocorrencias de travessao U+2014 ou emoji: 0
EXIT: 0

$ limites de tamanho
templates: 21 arquivos, maior tem 75 linhas, limite 80
docs/AGENTS.md: 56 linhas, limite 60
adapters/claude-code/CLAUDE.md: 2 linhas, exigido 2

$ pastas vazias fora dos .gitkeep
nenhuma
```


## Antes de instalar num projeto real

1. Responda cada item de `OPEN_QUESTIONS.md`. Sao 20, e cada um registra uma
   decisao tomada por interpretacao conservadora, nao por certeza.
2. Rode a prova do modo B voce mesmo, do zero, sem olhar esta secao. E o modo
   sem rede de seguranca de runtime: se funciona ali, funciona em qualquer
   lugar.
3. Instale num projeto tier 2 em andamento, em modo reverso, e compare o
   `docs/STATE.md` gerado com o que voce acredita ser o estado real.
4. Marque a tag `v1.0.0` no repositorio privado do kit. A partir dai, todo
   projeto novo comeca com `install.sh` e todo projeto antigo recebe
   `--update` quando o kit evoluir.

## Escopo

Kit privado, de uso interno. Nao ha promessa de compatibilidade entre majors: o
`CHANGELOG.md` diz o que muda e `docs/KIT_VERSION` diz o que cada projeto tem
instalado.

