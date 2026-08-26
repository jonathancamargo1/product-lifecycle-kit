# Changelog

Formato: uma secao por versao, mais nova em cima. Semver. O major muda quando
um projeto instalado precisa de intervencao manual para continuar valendo.

## 1.1.0

Versao usada para provar o fluxo `install.sh --update` (modo C do README).
Nenhuma mudanca de comportamento em relacao a 1.0.0: processo e scripts sao
reenviados ao alvo e `docs/KIT_VERSION` passa a 1.1.0, sem tocar em estado,
contexto, handoffs ou artefatos.

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
