# O que conta como codigo do produto

Lido por `bin/lifecycle/_kitlib.py`, que decide se um commit precisa de uma
fase de build aberta (ver `lifecycle.md`). O bloco `non-code-globs` abaixo e
dado de maquina: uma linha por padrao, relativo a raiz do repositorio. Linha
vazia e linha iniciada por `#` sao ignoradas.

Tudo que NAO casa com esses padroes e tratado como codigo do produto.

## Nao e codigo do produto

```non-code-globs
docs/**
.claude/**
.github/**
bin/lifecycle/**
proofs/**
AGENTS.md
CLAUDE.md
README.md
LICENSE
LICENSE.md
CONTRIBUTING.md
CHANGELOG.md
.gitignore
.gitattributes
.editorconfig
Makefile
Dockerfile
docker-compose.yml
package.json
package-lock.json
pnpm-lock.yaml
yarn.lock
pyproject.toml
poetry.lock
requirements.txt
tsconfig.json
```

## Por que esta lista existe

A regra existe para impedir que feature de produto entre sem spec e sem
review. Configuracao de CI, arquivo de build, lockfile e documentacao de raiz
nao sao feature: barrar isso so ensinaria o time a escrever autorizacao no
automatico, e uma autorizacao que vira rotina para de significar alguma coisa.

Ajuste a lista ao seu projeto. Se o seu produto tem codigo dentro de um path
que esta aqui, tire da lista. Este arquivo e protegido: alterar exige decisao
registrada, como qualquer coisa em `docs/_process/`.
