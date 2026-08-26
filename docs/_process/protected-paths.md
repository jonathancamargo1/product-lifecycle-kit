# Paths protegidos

Este arquivo e lido por `bin/lifecycle/guard-write` e
`bin/lifecycle/guard-commit`. O bloco de codigo `protected-globs` abaixo e
dado de maquina: uma linha por padrao glob, relativo a raiz do repositorio.
Linha vazia e linha iniciada por `#` sao ignoradas. Editar esse bloco muda o
comportamento dos guards.

## Sempre protegidos

```protected-globs
docs/_context/CONTEXT.md
docs/_process/**
AGENTS.md
docs/AGENTS.md
```

## Protegidos por status do frontmatter

Estes nao sao glob. Sao regras avaliadas sobre o frontmatter do arquivo:

- Qualquer `.md` sob `docs/_context/adr/` com `status: accepted`.
- Qualquer `.md` sob `docs/areas/` com `status: approved`.

## Como o guard decide

`guard-write <path>` inspeciona o arquivo como ele esta em disco, antes da
escrita. `guard-commit` inspeciona o arquivo como ele esta em HEAD, antes do
staging. Nos dois casos, o que e protegido e o estado ja registrado, nunca o
estado que se pretende gravar.

Essa distincao importa: o proprio ato humano de aprovar um artefato troca
`status: proposed` por `status: approved`. Se o guard olhasse o conteudo novo,
aprovar um gate seria impossivel. Arquivo que nao existe em HEAD e liberado,
porque criar arquivo novo nunca destroi decisao registrada.

## Como liberar uma escrita

Uma escrita em path protegido e liberada quando existe, em
`docs/_context/decisions.log`, uma entrada com status `DECIDED` cujo campo
`Afeta` inclui aquele path, com data igual ou posterior a ultima modificacao
registrada do arquivo.

A ultima modificacao registrada e a data do ultimo commit que tocou o arquivo.
Sem git ou sem historico, cai para o mtime do arquivo.

Para abrir a decisao:

```
bin/lifecycle/decide --titulo "..." --afeta docs/_context/CONTEXT.md
```

O script cria a entrada `PENDING`, aponta `blocked_by` em `docs/STATE.md` e
manda encerrar a sessao. Um humano preenche `Decisao`, `Decidido por` e troca
o status para `DECIDED`. So entao a escrita passa.

## Por que `docs/_process` inteiro

Processo e a camada quase imutavel (principio 1). Um agente que pode reescrever
o proprio processo pode reescrever o gate que o incomoda. Mudanca de processo
vem do kit, via `install.sh --update`, ou de decisao humana registrada.
