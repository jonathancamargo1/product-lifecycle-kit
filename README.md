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

## Instalar a partir de outro repositorio, com um agente

O caso mais comum: voce esta numa sessao aberta num projeto novo e quer o kit
ali. O agente dessa sessao nao sabe onde o kit mora, e este README, que
explicaria, esta dentro do kit que ele ainda nao tem. Entao seja explicito.
Cole isto na sessao do projeto, trocando a URL pela do seu kit:

```
Adicione o repositorio <owner>/product-lifecycle-kit ao escopo desta sessao,
clone ele para /tmp/plk, e rode:

    /tmp/plk/install.sh . --adapters all

Depois preencha project e tier em docs/STATE.md, commite a instalacao, e
abra a primeira sessao com bin/lifecycle/session-open.
```

Tres coisas que costumam travar:

- **O kit e um repositorio privado.** Uma sessao nova so enxerga o repositorio
  em que foi aberta. Ela precisa anexar o do kit ao escopo antes de clonar, ou
  o clone falha com "not found" mesmo que voce tenha acesso.
- **`install.sh` nao adivinha o alvo.** O primeiro argumento e o repositorio de
  destino, e ele precisa ja ser um repositorio git. Rode de dentro do projeto,
  com `.` como alvo.
- **`project` e `tier` nao se preenchem sozinhos.** O kit instala com os dois
  em `null`, e o `install.sh` termina dizendo exatamente isso. Enquanto o tier
  for `null`, `new-artifact` recusa criar artefato e `gate-check` acusa ST-05,
  de proposito: sem tier o kit nao sabe quais fases exigir, e um gate que nao
  exige nada e pior do que gate nenhum, porque parece que existe.

O que a instalacao faz com um projeto que ja tem codigo: acrescenta
`AGENTS.md`, `CLAUDE.md`, `.claude/`, `bin/lifecycle/`, `docs/` e os dois git
hooks. Nao toca em nenhum arquivo que ja existia, e lista no fim o que pulou.

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
| Ver o que falta | `bin/lifecycle/plan` | `/plan` |
| Verificar gates | `bin/lifecycle/gate-check` | nao ha |
| Fechar sessao | `bin/lifecycle/session-close --handoff <arquivo>` | `/session-close` |

`session-open` imprime o contexto minimo da sessao e nada alem: `AGENTS.md`, o
estado, o ultimo handoff, o glossario, os principios e o template da fase
corrente. O agente nunca carrega o projeto inteiro.

No Claude Code, o hook `SessionStart` faz a abertura sozinho. No Codex, quem
manda rodar e o `AGENTS.md`.

## O que falta

`bin/lifecycle/plan` compara as fases obrigatorias do tier com os gates que
existem e imprime o buraco, em ordem, com a proxima acao pronta para copiar:

```sh
$ bin/lifecycle/plan
Tier 2: 12 fases obrigatorias, faltam 11 de 12.

  01-contexto         approved     docs/areas/checkout/01-contexto/contexto.md
> 02-discovery        pendente
> 05-prd              pendente
  ...

Proxima acao: criar o artefato da fase 02-discovery.
```

E o unico lugar que mostra o que nunca foi comecado. O painel da area lista o
que existe e o `gate-check` verifica o que existe; nenhum dos dois enxerga
ausencia. Por isso o painel tambem passou a listar as fases pendentes: por
omissao, ele fazia um projeto pela metade parecer completo.

## Codigo entra a partir da fase 13

Commit que toca codigo do produto exige a fase corrente ser `13-build-log` ou
posterior. Fora disso o `commit-msg` recusa, lista os arquivos e diz o que se
perde: codigo sem spec que o descreva, sem review de papel distinto do
executor, e sem rastro da decisao de produto que o originou.

Nao e bloqueio automatico, e isso e deliberado. Um kit que impede hotfix e um
kit que as pessoas desligam. A saida existe, mas custa um ato explicito:

```
Sem-fase: <por que entra sem fase, e quem autorizou>
```

Tres consequencias de desenho. Quem autoriza e humano: o `AGENTS.md` proibe o
agente de escrever esse trailer sozinho, com a analogia direta de que
autorizar a si mesmo e o mesmo que aprovar o proprio gate. A autorizacao fica
no historico do git para sempre, nao num arquivo que alguem limpa depois. E o
`gate-check` conta quantas existem (`PH-01`, aviso) e mostra em toda sessao,
porque `session-open` roda o `gate-check`.

O limite, que nenhum hook fecha: o trailer e texto de commit, entao um agente
que decida mentir consegue escreve-lo. E o mesmo teto do `--no-verify`. O kit
torna o desvio caro, visivel e permanente; nao torna impossivel.

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
| ST-04 | `last_session` aponta para handoff que nao existe | erro |
| ST-05 | Projeto com trabalho em andamento e `tier` nao declarado | erro |
| SQ-01 | `current_phase` em andamento com gate obrigatorio anterior nao aprovado | erro |
| DC-01 | `PENDING` em `decisions.log` sem `blocked_by` correspondente | erro |
| VC-01 | Termo proibido pelo glossario aparece no codigo ou nos documentos | erro |
| PH-01 | Commits de codigo que entraram sem fase de build | aviso |
| DR-01 | Pasta vazia sob `docs/areas/` | aviso |
| KV-01 | `docs/KIT_VERSION` ausente ou incompativel com os scripts | aviso |

Avisos nao alteram o exit code. `IN-03`, `ST-04`, `ST-05` e `PH-01` nao
constam da tabela da especificacao original; estao registrados em
`OPEN_QUESTIONS.md`, Q6, Q21, Q27 e Q29.

## Adaptador versus enforcement comum

Cada garantia dos hooks do adaptador Claude Code tem um equivalente que nao
depende de agente nenhum. A coluna da direita e o que sustenta o modo Codex, e
esta demonstrada no modo B abaixo.

| Garantia | Hook do Claude Code | Equivalente comum | Onde a prova esta |
|---|---|---|---|
| Escrita em arquivo protegido nao entra | `PreToolUse` roda `guard-write`, exit 2 bloqueia a ferramenta | `pre-commit` roda `guard-commit`, que recusa o commit | Modo B, blocos 5 e 5a |
| Decisao humana libera a escrita | mesmo hook, apos entrada `DECIDED` | mesmo guard, apos entrada `DECIDED` | Modo B, blocos 6 e 6a |
| Sessao nao encerra sem handoff | `Stop` roda `session-close --check` e bloqueia | `guard-commit` recusa commit em `docs/` enquanto `session_open` for `true` | Modo B, blocos 5, 5a e 5b |
| Sessao anterior nao fica aberta | consequencia do `Stop` | `session-open` se recusa a abrir (script, nao git hook) | Modo A, bloco 3a |
| Mensagem de commit de sessao correta | nao ha | `commit-msg` valida `sessao NN` contra `session_counter` | Modo B, bloco 8 |
| Contexto carregado na abertura | `SessionStart` roda `session-open` | so instrucao em `AGENTS.md`, sem equivalente de maquina | Modo B, bloco 3 |

A ultima linha e a unica garantia que fica so no adaptador, e nao ha como impor
por maquina: nenhum script obriga um agente a ler antes de agir. As outras sao
impostas por git, e por isso valem em qualquer runtime, inclusive num humano no
editor. Isso esta registrado em `OPEN_QUESTIONS.md`, Q19.

A diferenca entre os dois runtimes e o momento, nao o resultado. No Claude Code
a escrita indevida e barrada na hora. No Codex ela chega ao disco e e barrada
no commit. Nos dois casos ela nao entra no repositorio.

## Estrutura

Arvore do kit:

````text
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
        plan.md
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
  plan
  session-close
  session-open
  tests/
    __init__.py
    kitfixture.py
    test_code_phase.py
    test_gate_check.py
    test_guards.py
    test_kitlib.py
    test_new_artifact.py
    test_plan.py
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
  build-readme.py
  encadeamento.sh
  fase-para-codigo.sh
  modo-a-claude-code.sh
  modo-b-codex.sh
  modo-c-update.sh
  varredura.sh
````

Arvore de um projeto alvo recem instalado com `install.sh . --adapters all`,
antes de qualquer fase comecar. `docs/areas/` nasce vazio porque estrutura so
nasce quando o artefato nasce:

````text
.claude
.claude/commands
.claude/commands/decide.md
.claude/commands/new-artifact.md
.claude/commands/plan.md
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
bin/lifecycle/plan
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
````

Arvore de um projeto alvo depois de `install.sh . --adapters claude-code`, com
as quatro fases do tier 1 ja executadas. E a saida real do modo A:

````text
.
./.claude
./.claude/commands
./.claude/commands/decide.md
./.claude/commands/new-artifact.md
./.claude/commands/plan.md
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
./bin/lifecycle/plan
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
./docs/_handoffs/2026-08-27-sessao-01.md
./docs/_handoffs/2026-08-27-sessao-02.md
./docs/_handoffs/2026-08-27-sessao-03.md
./docs/_handoffs/2026-08-27-sessao-04.md
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
````

`bin/lifecycle/` tem esse nome para nao colidir com um `bin/` que o projeto ja
tenha. Os testes do kit nao sao copiados para o alvo.


## Prova de funcionamento

Tudo abaixo e saida real, colada sem edicao, gerada com o kit na versao 1.0.0.
Os scripts que produzem cada bloco estao em `proofs/` e podem ser rodados de
novo do zero. Nenhum deles altera o kit: a prova do modo C monta a versao nova
numa copia temporaria, justamente para que os outros blocos continuem
reproduziveis.

### Testes

Um caso que passa e um que falha para cada codigo de `gate-check`, mais os
testes dos guards, das sessoes, do `new-artifact` e do round-trip de YAML.

````text
$ python3 -m unittest discover bin/tests
........................................................................................................................................................
----------------------------------------------------------------------
Ran 152 tests in 22.240s

OK
EXIT: 0
````

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

````text

----- 1. Instalacao -----
$ /home/user/product-lifecycle-kit/install.sh . --adapters claude-code
Instalando o product-lifecycle-kit 1.1.0 em /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-a.
Adaptador claude-code.

docs/KIT_VERSION: 1.1.0
Rodando gate-check no alvo.

gate-check: nenhuma ocorrencia.

Instalacao concluida. gate-check saiu com 0.

ACAO NECESSARIA: tier nao declarado em docs/STATE.md.
  valor atual: null

Abra docs/STATE.md e preencha os dois campos:
     project: <nome-do-projeto>
     tier:    1, 2 ou 3     (ver docs/_process/tiers.md)

O tier decide quais fases sao obrigatorias. Enquanto ele nao
for 1, 2 ou 3, new-artifact recusa criar artefato e o
gate-check acusa ST-05, o que faz o pre-commit recusar
qualquer commit. Na duvida entre dois tiers, escolha o maior.

Para comecar, commite a instalacao e abra a primeira sessao:
     git add -A && git commit -m "instala o product-lifecycle-kit"
     bin/lifecycle/session-open --agent <codex|claude-code|human>

Todo o resto do protocolo esta em AGENTS.md, na raiz.
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
gate-check: nenhuma ocorrencia.
Handoff registrado em docs/_handoffs/2026-08-27-sessao-01.md.
Commit: sessao 01: 01-contexto escrevi o contexto e o nao-escopo
EXIT: 0

----- 3e. session-close --check depois de fechar -----
$ python3 bin/lifecycle/session-close --check
session-close: nada pendente, a sessao pode encerrar.
EXIT: 0

----- 4. Humano aprova o gate 01 -----
gate 01-contexto aprovado por Jonathan Camargo em 2026-08-27
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
gate-check: nenhuma ocorrencia.
Handoff registrado em docs/_handoffs/2026-08-27-sessao-02.md.
Commit: sessao 02: 13-build-log executei a fase 13-build
EXIT: 0
gate 13-build-log aprovado por Jonathan Camargo em 2026-08-27
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
gate-check: nenhuma ocorrencia.
Handoff registrado em docs/_handoffs/2026-08-27-sessao-03.md.
Commit: sessao 03: 14-review executei a fase 14-review
EXIT: 0
gate 14-review aprovado por Jonathan Camargo em 2026-08-27
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
gate-check: nenhuma ocorrencia.
Handoff registrado em docs/_handoffs/2026-08-27-sessao-04.md.
Commit: sessao 04: 17-ship executei a fase 17-ship
EXIT: 0
gate 17-ship aprovado por Jonathan Camargo em 2026-08-27
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
    date: 2026-08-27
  13-build-log:
    status: approved
    evidence: docs/areas/nucleo/13-build-log/build-do-prova-a.md
    by: Jonathan Camargo
    date: 2026-08-27
  14-review:
    status: approved
    evidence: docs/areas/nucleo/14-review/review-do-prova-a.md
    by: Jonathan Camargo
    date: 2026-08-27
  17-ship:
    status: approved
    evidence: docs/areas/nucleo/17-ship/ship-do-prova-a.md
    by: Jonathan Camargo
    date: 2026-08-27
last_session: docs/_handoffs/2026-08-27-sessao-04.md # path do ultimo handoff
session_counter: 4
session_open: false           # true entre session-open e session-close
session_agent: claude-code    # codex | claude-code | human
```
EXIT: 0
$ git log --oneline
4bda016 humano aprova o gate 17-ship
c3c4fd3 sessao 04: 17-ship executei a fase 17-ship
22e4e18 humano aprova o gate 14-review
f3375b7 sessao 03: 14-review executei a fase 14-review
19ca8e2 humano aprova o gate 13-build-log
c6d267b sessao 02: 13-build-log executei a fase 13-build
6d72aae humano aprova o gate 01-contexto
9e40d40 sessao 01: 01-contexto escrevi o contexto e o nao-escopo
58115ce instala o product-lifecycle-kit
EXIT: 0
````

### Modo B: repositorio operado pelo Codex

`proofs/modo-b-codex.sh`. Instala com `--adapters codex`, que nao instala hook
de runtime nenhum. A mesma sequencia de quatro sessoes, com `--agent codex`.

Alem do ciclo, demonstra o que so o modo B pode provar, porque sao as
garantias que existem sem rede de seguranca de runtime:

- commit em `docs/` com a sessao aberta e recusado, e passa depois do
  `session-close`; commit de codigo fora de `docs/` passa livre (5, 5a, 5b).
  E o equivalente comum do hook `Stop`.
- o `git commit` de uma edicao num artefato aprovado sem decisao e abortado
  pelo `pre-commit` com a saida de `guard-commit` (6a), e o mesmo commit passa
  depois de uma entrada `DECIDED` em `decisions.log` com o path em `Afeta`
  (7a).
- o `commit-msg` recusa `sessao 99` quando o `session_counter` nao bate (8), e
  a mesma mudanca passa com uma mensagem que nao e de sessao (8a).

````text

----- 1. Instalacao sem nenhum hook de runtime -----
$ /home/user/product-lifecycle-kit/install.sh . --adapters codex
Instalando o product-lifecycle-kit 1.1.0 em /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b.
Adaptador codex.

docs/KIT_VERSION: 1.1.0
Rodando gate-check no alvo.

gate-check: nenhuma ocorrencia.

Instalacao concluida. gate-check saiu com 0.

ACAO NECESSARIA: tier nao declarado em docs/STATE.md.
  valor atual: null

Abra docs/STATE.md e preencha os dois campos:
     project: <nome-do-projeto>
     tier:    1, 2 ou 3     (ver docs/_process/tiers.md)

O tier decide quais fases sao obrigatorias. Enquanto ele nao
for 1, 2 ou 3, new-artifact recusa criar artefato e o
gate-check acusa ST-05, o que faz o pre-commit recusar
qualquer commit. Na duvida entre dois tiers, escolha o maior.

Para comecar, commite a instalacao e abra a primeira sessao:
     git add -A && git commit -m "instala o product-lifecycle-kit"
     bin/lifecycle/session-open --agent <codex|claude-code|human>

Todo o resto do protocolo esta em AGENTS.md, na raiz.
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
[cabecalho de AGENTS.md, STATE.md, CONTEXT.md e principles.md suprimido aqui, 175 linhas]
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
gate-check: nenhuma ocorrencia.
Handoff registrado em docs/_handoffs/2026-08-27-sessao-01.md.
Commit: sessao 01: 01-contexto escrevi o contexto e o nao-escopo
EXIT: 0
gate 01-contexto aprovado por Jonathan Camargo em 2026-08-27
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
gate-check: nenhuma ocorrencia.
Handoff registrado em docs/_handoffs/2026-08-27-sessao-02.md.
Commit: sessao 02: 13-build-log executei a fase 13-build
EXIT: 0
gate 13-build-log aprovado por Jonathan Camargo em 2026-08-27
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
gate-check: nenhuma ocorrencia.
Handoff registrado em docs/_handoffs/2026-08-27-sessao-03.md.
Commit: sessao 03: 14-review executei a fase 14-review
EXIT: 0
gate 14-review aprovado por Jonathan Camargo em 2026-08-27
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
gate-check: nenhuma ocorrencia.
Handoff registrado em docs/_handoffs/2026-08-27-sessao-04.md.
Commit: sessao 04: 17-ship executei a fase 17-ship
EXIT: 0
gate 17-ship aprovado por Jonathan Camargo em 2026-08-27
gate-check: nenhuma ocorrencia.
commit da aprovacao ok

----- 5. Sessao aberta: o trabalho em docs/ nao entra sem handoff -----
$ grep session_open docs/STATE.md
session_open: true            # true entre session-open e session-close
$ git add -A
EXIT: 0
$ git commit -m tenta entrar com a sessao aberta
gate-check: nenhuma ocorrencia.
Sessao 5 ainda aberta (agente codex). O handoff dela nao foi escrito.
Feche com: session-close --handoff <arquivo>
EXIT: 1

----- 5a. O mesmo commit passa depois do session-close -----
$ python3 bin/lifecycle/session-close --handoff /tmp/handoff-b.md
gate-check: nenhuma ocorrencia.
Handoff registrado em docs/_handoffs/2026-08-27-sessao-05.md.
Commit: sessao 05: 17-ship trabalho da sessao 05
EXIT: 0

----- 5b. Codigo fora de docs/ nao e refem do protocolo de sessao -----
$ git commit -m commit de codigo com a sessao aberta
gate-check: nenhuma ocorrencia.
[main 11760f2] commit de codigo com a sessao aberta
 1 file changed, 1 insertion(+)
 create mode 100644 src/app.py
EXIT: 0

----- 6. Edicao num artefato aprovado. Nada impede a escrita no disco. -----
$ git add docs/areas/nucleo/01-contexto/contexto-do-prova-b.md
EXIT: 0

----- 6a. git commit e abortado pelo pre-commit, com a saida de guard-commit -----
$ git commit -m altera um artefato aprovado sem decisao
gate-check: nenhuma ocorrencia.
Arquivo protegido. Abra uma decisao (script decide) ou resolva a pendente.
  docs/areas/nucleo/01-contexto/contexto-do-prova-b.md (artefato aprovado)
EXIT: 1

----- 6b. o artefato aprovado continua intocado no repositorio -----
$ git log --oneline -1 -- docs/areas/nucleo/01-contexto/contexto-do-prova-b.md
307540e humano aprova o gate 01-contexto
EXIT: 0

----- 7. Entrada DECIDED em decisions.log liberando o mesmo path -----
decisao D-0001 registrada como DECIDED, Afeta: docs/areas/nucleo/01-contexto/contexto-do-prova-b.md
$ git add -A
EXIT: 0

----- 7a. o mesmo commit agora passa -----
$ git commit -m corrige o artefato aprovado sob a decisao D-0001
gate-check: nenhuma ocorrencia.
[main 9e72655] corrige o artefato aprovado sob a decisao D-0001
 2 files changed, 8 insertions(+)
EXIT: 0

----- 8. commit-msg recusa sessao 99 quando o session_counter nao bate -----
$ grep session_counter docs/STATE.md
session_counter: 6
$ git commit -m sessao 99: 17-ship resumo mentiroso
gate-check: nenhuma ocorrencia.
commit-msg: a mensagem diz sessao 99 mas o session_counter em docs/STATE.md e 6.
EXIT: 1

----- 8a. a mesma mudanca passa com uma mensagem que nao e de sessao -----
$ git commit -m adiciona uma nota solta
gate-check: nenhuma ocorrencia.
[main b74097e] adiciona uma nota solta
 1 file changed, 1 insertion(+)
 create mode 100644 nota.txt
EXIT: 0

----- 9. Estado final -----
$ python3 bin/lifecycle/gate-check
gate-check: nenhuma ocorrencia.
EXIT: 0
$ git log --oneline
b74097e adiciona uma nota solta
9e72655 corrige o artefato aprovado sob a decisao D-0001
f1b238a sessao 06: 17-ship commit de codigo
11760f2 commit de codigo com a sessao aberta
873f58a sessao 05: 17-ship trabalho da sessao 05
3caed79 humano aprova o gate 17-ship
395c349 sessao 04: 17-ship executei a fase 17-ship
c2ec0b9 humano aprova o gate 14-review
09c953e sessao 03: 14-review executei a fase 14-review
f596cd6 humano aprova o gate 13-build-log
4db8de4 sessao 02: 13-build-log executei a fase 13-build
307540e humano aprova o gate 01-contexto
d7ba32a sessao 01: 01-contexto escrevi o contexto e o nao-escopo
933869e instala o product-lifecycle-kit
EXIT: 0
````

### Modo C: atualizacao

`proofs/modo-c-update.sh`. Com o projeto `prova-b` ja instalado na versao
1.0.0, monta uma copia temporaria do kit na versao 1.1.0, com a secao
correspondente no `CHANGELOG.md`, e roda o `install.sh` dessa copia com
`--update`.

O que a prova mede: uma soma sha256 de tudo que o `--update` tem proibido
tocar, tirada antes e depois. `docs/STATE.md`, `docs/_handoffs/` e
`docs/areas/` ficam identicos; so `docs/KIT_VERSION`, os scripts e o manifesto
mudam. O bloco 6 mostra que o kit real continua na versao de antes.

Os arquivos de processo que o `--update` reescreve podem ser commitados porque
`guard-commit` reconhece, pelo sha256 em `docs/.kit-manifest`, o que o proprio
kit instalou. Edicao a mao no mesmo arquivo continua barrada.

````text

----- 1. Estado antes do update -----
$ cat /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b/docs/KIT_VERSION
1.1.0
EXIT: 0
impressao digital de STATE.md + _handoffs + areas: 54836ebb41342f0ea4d0769a113dffc490b8acbb38b1a24c73306be43d3fc3eb

----- 2. Nova versao do kit, montada numa copia temporaria -----
copia do kit montada na versao 1.2.0. O kit real segue intocado.
$ cat <copia>/VERSION
1.2.0
$ cat /home/user/product-lifecycle-kit/VERSION   (o kit real)
1.1.0

----- 3. install.sh --update, rodado a partir da copia -----
$ <copia>/install.sh /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b --update
Atualizando o kit em /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b para a versao 1.2.0.
Versao anterior: 1.1.0
  AGENTS.md nao tinha edicao do projeto, foi atualizado
  adaptador claude-code nao estava instalado, pulando
Adaptador codex.

Mudancas desta versao (CHANGELOG.md):
  ## 1.1.0
  
  Tres adicoes que responderam a uma pergunta simples: um agente instalado num
  repositorio novo conclui as etapas, e um agente instalado num repositorio que
  ja existe consegue reconhecer o que ha e planejar o que falta?
  
  - `bin/plan`: compara as fases obrigatorias do tier com os gates existentes e
    imprime o que falta, em ordem, com a proxima acao pronta para copiar. Antes
    nada no kit sabia dizer o que nunca tinha sido comecado.
  - O painel da area passa a listar as fases pendentes. Antes so mostrava o que
    existia, entao um projeto pela metade parecia completo.
  - Commit que toca codigo do produto exige a fase corrente ser `13-build-log`
    ou posterior. Nao e bloqueio automatico: o `commit-msg` recusa explicando o
    que se perde, e a passagem exige a linha `Sem-fase: <motivo, e quem
    autorizou>` no commit, que um humano autoriza e que fica no historico para
    sempre. `gate-check` conta as autorizacoes no codigo `PH-01`, aviso.
  
  Compativel com 1.0.0: nenhum projeto instalado precisa de intervencao manual.
  Projetos que ja commitavam codigo fora de fase passam a receber a recusa, que
  e o ponto.
  

docs/KIT_VERSION: 1.2.0
Rodando gate-check no alvo.

gate-check: nenhuma ocorrencia.

Instalacao concluida. gate-check saiu com 0.
EXIT: 0

----- 4. KIT_VERSION do alvo mudou -----
$ cat /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b/docs/KIT_VERSION
1.2.0
EXIT: 0

----- 5. STATE.md, _handoffs e areas nao mudaram -----
antes:  54836ebb41342f0ea4d0769a113dffc490b8acbb38b1a24c73306be43d3fc3eb
depois: 54836ebb41342f0ea4d0769a113dffc490b8acbb38b1a24c73306be43d3fc3eb
IGUAIS. O update nao tocou em estado, handoffs nem artefatos.

----- 5a. git status do alvo depois do update -----
$ git -C /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-b status --short
 M bin/lifecycle/_kitlib.py
 M docs/.kit-manifest
 M docs/KIT_VERSION
EXIT: 0

----- 6. O kit real continua na versao de antes -----
$ git -C /home/user/product-lifecycle-kit status --short VERSION CHANGELOG.md bin/_kitlib.py
 M bin/_kitlib.py
EXIT: 0

----- 7. gate-check continua limpo depois do update -----
$ python3 bin/lifecycle/gate-check
gate-check: nenhuma ocorrencia.
EXIT: 0
````

### Instalacao sem nenhum adaptador

Criterio de aceite: `install.sh --adapters none` num repositorio vazio termina
com `gate-check` exit 0 e os dois git hooks instalados. E o caso que prova o
principio 12, o de que o nucleo nao depende de agente nenhum. Repare tambem no
aviso impresso no fim: sem `tier` declarado o kit nao sabe o que exigir, e diz
isso em vez de deixar passar.

````text
$ /home/user/product-lifecycle-kit/install.sh . --adapters none
Instalando o product-lifecycle-kit 1.1.0 em /tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad/prova-none.

docs/KIT_VERSION: 1.1.0
Rodando gate-check no alvo.

gate-check: nenhuma ocorrencia.

Instalacao concluida. gate-check saiu com 0.

ACAO NECESSARIA: tier nao declarado em docs/STATE.md.
  valor atual: null

Abra docs/STATE.md e preencha os dois campos:
     project: <nome-do-projeto>
     tier:    1, 2 ou 3     (ver docs/_process/tiers.md)

O tier decide quais fases sao obrigatorias. Enquanto ele nao
for 1, 2 ou 3, new-artifact recusa criar artefato e o
gate-check acusa ST-05, o que faz o pre-commit recusar
qualquer commit. Na duvida entre dois tiers, escolha o maior.

Para comecar, commite a instalacao e abra a primeira sessao:
     git add -A && git commit -m "instala o product-lifecycle-kit"
     bin/lifecycle/session-open --agent <codex|claude-code|human>

Todo o resto do protocolo esta em AGENTS.md, na raiz.
EXIT: 0

----- os dois git hooks estao instalados e executaveis -----
$ ls -l .git/hooks/pre-commit .git/hooks/commit-msg
-rwxr-xr-x 1 root root 6584 Aug 27 15:00 .git/hooks/commit-msg
-rwxr-xr-x 1 root root  623 Aug 27 15:00 .git/hooks/pre-commit
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
````

### Codigo entra a partir da fase 13

`proofs/fase-para-codigo.sh`. Instala num repositorio que ja tem codigo,
declara tier 2, e tenta subir uma feature sem nenhuma fase comecada.

Demonstra: o `plan` mostrando as 12 fases pendentes (2); a recusa do
`commit-msg` com os arquivos e o custo na tela (3); o caminho recomendado
funcionando (4); a recusa continuando de pe na fase 01, porque codigo e
esperado da 13 em diante (5); a autorizacao explicita do humano deixando o
commit passar (6); a autorizacao sem motivo sendo recusada (7); e a divida
aparecendo no `gate-check` como `PH-01` com o rastro permanente no git log
(8).

````text

----- 1. Instalacao, tier 2 -----
gate-check: nenhuma ocorrencia.
instalado, tier 2, nenhuma fase comecada

----- 2. O que falta, antes de qualquer coisa -----
$ python3 bin/lifecycle/plan
Projeto: prova-fase
Tier 2: 12 fases obrigatorias, faltam 12 de 12.

> 01-contexto         pendente     
> 02-discovery        pendente     
> 05-prd              pendente     
> 07-flows-ia         pendente     
> 08-wireframes       pendente     
> 11-spec             pendente     
> 12-backlog-handoff  pendente     
> 13-build-log        pendente     
> 14-review           pendente     
> 15-threat-review    pendente     
> 16-verify           pendente     
> 17-ship             pendente     

Proxima acao: criar o artefato da fase 01-contexto.
  bin/lifecycle/new-artifact 01-contexto <area> "<titulo>" --owner "<nome>"
EXIT: 0

----- 3. O agente tenta subir feature sem fase de build -----
$ git commit -m adiciona feature de checkout
gate-check: nenhuma ocorrencia.
commit-msg: codigo entrando sem fase de build aberta.

  arquivos: src/app.py
  fase corrente: nenhuma (codigo e esperado da 13-build-log em diante)

O que se perde ao seguir assim: este codigo nao tem spec que o descreva,
nao passa por review de papel distinto do executor, e nao deixa rastro
de qual decisao de produto o originou. Daqui a tres meses ninguem sabe
por que ele existe.

O caminho recomendado, que diz qual e a proxima fase de verdade:
  bin/lifecycle/plan

Se mesmo assim este commit precisa entrar agora, pergunte ao humano e
registre a resposta dele no proprio commit:
  Sem-fase: <por que entra sem fase, e quem autorizou>

Nunca escreva esse trailer por conta propria. Ver AGENTS.md.
EXIT: 1

----- 4. O caminho recomendado funciona -----
$ python3 bin/lifecycle/new-artifact 01-contexto checkout Contexto do checkout --owner Jonathan Camargo
Artefato criado: docs/areas/checkout/01-contexto/contexto-do-checkout.md
Gate 01-contexto registrado como in_progress em docs/STATE.md.
Preencha o template e marque status: proposed. Nunca approved.
EXIT: 0

----- 5. Mas na fase 01 codigo continua recusado -----
$ git commit -m adiciona feature de checkout
gate-check: nenhuma ocorrencia.
commit-msg: codigo entrando sem fase de build aberta.

  arquivos: src/app.py
  fase corrente: 01-contexto (codigo e esperado da 13-build-log em diante)

O que se perde ao seguir assim: este codigo nao tem spec que o descreva,
nao passa por review de papel distinto do executor, e nao deixa rastro
de qual decisao de produto o originou. Daqui a tres meses ninguem sabe
por que ele existe.

O caminho recomendado, que diz qual e a proxima fase de verdade:
  bin/lifecycle/plan

Se mesmo assim este commit precisa entrar agora, pergunte ao humano e
registre a resposta dele no proprio commit:
  Sem-fase: <por que entra sem fase, e quem autorizou>

Nunca escreva esse trailer por conta propria. Ver AGENTS.md.
EXIT: 1

----- 6. Com autorizacao explicita do humano, passa -----
$ git commit -m corrige timeout do gateway

Sem-fase: hotfix de producao, autorizado por Jonathan Camargo
gate-check: nenhuma ocorrencia.
[main 0d01630] corrige timeout do gateway
 1 file changed, 1 insertion(+)
EXIT: 0

----- 7. A autorizacao vazia nao passa -----
$ git commit -m outra coisa

Sem-fase:
[PH-01] docs/STATE.md:9 1 commit(s) de codigo entraram sem fase de build aberta. Veja com: git log --grep '^Sem-fase:'
gate-check: 0 erro(s), 1 aviso(s).
commit-msg: Sem-fase: esta vazio. A autorizacao precisa de motivo:
  Sem-fase: <por que este codigo entra sem fase, e quem autorizou>
EXIT: 1

----- 8. A divida aparece em toda sessao, e o rastro e permanente -----
$ python3 bin/lifecycle/gate-check
[PH-01] docs/STATE.md:9 1 commit(s) de codigo entraram sem fase de build aberta. Veja com: git log --grep '^Sem-fase:'
gate-check: 0 erro(s), 1 aviso(s).
EXIT: 0
$ git log --grep ^Sem-fase: --oneline
0d01630 corrige timeout do gateway
EXIT: 0
````

### Encadeamento de hooks e merge de settings

`proofs/encadeamento.sh`. A secao 13 exige que `install.sh` encadeie um hook de
git que ja exista, em vez de sobrescrever, e que mescle os hooks num
`.claude/settings.json` do projeto sem remover os que ja estavam la. Esta prova
instala num repositorio que ja tem os dois.

````text
----- 1. O projeto ja tem um pre-commit proprio e hooks proprios -----
$ cat .git/hooks/pre-commit
#!/bin/sh
echo "HOOK ANTERIOR DO PROJETO RODOU"
exit 0
EXIT: 0

----- 2. Instalacao -----
  hook pre-commit existente preservado em pre-commit.local e encadeado
  .claude/settings.json existente teve os hooks mesclados
gate-check: nenhuma ocorrencia.

----- 3. O hook do projeto foi preservado, nao sobrescrito -----
$ cat .git/hooks/pre-commit.local
#!/bin/sh
echo "HOOK ANTERIOR DO PROJETO RODOU"
exit 0
EXIT: 0

----- 4. settings.json: o hook do projeto continua la -----
$ python3 lista os hooks de .claude/settings.json
PreToolUse     meu-hook-do-projeto.sh
PreToolUse     ${CLAUDE_PROJECT_DIR}/.claude/hooks/guard-write.sh
SessionStart   ${CLAUDE_PROJECT_DIR}/bin/lifecycle/session-open --agent claude-code
Stop           ${CLAUDE_PROJECT_DIR}/.claude/hooks/stop-gate.sh

----- 5. Num commit real, os dois rodam, o do projeto primeiro -----
$ git commit -m primeiro commit
HOOK ANTERIOR DO PROJETO RODOU
gate-check: nenhuma ocorrencia.
[main (root-commit) 4eed542] primeiro commit
 1 file changed, 1 insertion(+)
 create mode 100644 docs/nota.md
EXIT: 0
````

### Varredura de caracteres e limites

Nenhum arquivo do kit contem o caractere travessao longo nem emoji. Nenhum
template passa de 80 linhas, `docs/AGENTS.md` nao passa de 60, e
`adapters/claude-code/CLAUDE.md` tem exatamente 2. Nenhuma pasta vazia fora dos
`.gitkeep` previstos.

O proprio scanner nunca escreve o travessao literalmente: ele monta o caractere
a partir do codepoint U+2014. Se o escrevesse, o arquivo do scanner seria uma
ocorrencia e a varredura acusaria a si mesma.

````text
$ grep -rn --exclude-dir=.git -e "<U+2014>" .
EXIT: 1

$ python3 varredura de codepoints em todos os arquivos versionados
arquivos versionados verificados: 83
ocorrencias de travessao U+2014 ou emoji: 0
EXIT: 0

$ limites de tamanho
templates: 21 arquivos, maior tem 75 linhas, limite 80
docs/AGENTS.md: 60 linhas, limite 60
adapters/claude-code/CLAUDE.md: 2 linhas, exigido 2

$ pastas vazias fora dos .gitkeep
nenhuma
````


## Antes de instalar num projeto real

1. Responda cada item de `OPEN_QUESTIONS.md`. Sao 27, e cada um registra uma
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

