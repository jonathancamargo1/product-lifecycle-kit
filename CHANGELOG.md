# Changelog

Formato: uma secao por versao, mais nova em cima. Semver. O major muda quando
um projeto instalado precisa de intervencao manual para continuar valendo.

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

## 1.0.0

Primeira versao.

- Nucleo agnostico de runtime: `docs/_process`, `docs/_context`, `docs/STATE.md`
  e os scripts em `bin/`, sem nenhuma dependencia de agente.
- 20 fases com template de uma pagina cada, mais o painel de area
  (`area-readme.md`).
- `gate-check` com 16 codigos de verificacao, saida em texto e em JSON.
- `guard-write` e `guard-commit`: a mesma regra de path protegido, aplicada na
  escrita e no commit.
- `session-open`, `session-close`, `new-artifact` e `decide`.
- Enforcement comum via git hooks `pre-commit` e `commit-msg`, instalados
  encadeando hooks existentes.
- Adaptadores opcionais para Claude Code (hooks de runtime e slash commands) e
  Codex (documentacao do mapeamento).
- `install.sh` com instalacao, atualizacao (`--update`) e escolha de
  adaptadores.
