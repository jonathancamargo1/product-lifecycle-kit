# Perguntas em aberto

Este arquivo registra toda ambiguidade, lacuna ou conflito encontrado na
especificacao v2, e a interpretacao conservadora adotada na construcao do kit.
Nenhum item abaixo impediu a construcao. Responda cada um antes de instalar o
kit num projeto real.

Formato: pergunta, interpretacao adotada, onde o efeito aparece.

## Q1. Slug canonico da fase 13

A secao 4 nomeia o arquivo `13-build-log.md`, o que faz o slug ser
`13-build-log`. A secao 14.4 pede `gate-check --phase 13-build`.

Interpretacao adotada: o slug canonico e o nome do arquivo de template sem a
extensao (`13-build-log`). `gate-check --phase` e `new-artifact` aceitam
qualquer prefixo que resolva para exatamente um slug, entao `13-build` e
`13` funcionam. Prefixo ambiguo e erro explicito.

Efeito: `bin/gate-check`, `bin/new-artifact`.

## Q2. Chave do mapa `gates` em STATE.md com mais de uma area

A secao 6 diz "chave = slug da fase". A secao 4 define um painel de gates por
area (`area-readme.md`), e STATE.md tem `current_area`. Num projeto com duas
areas, duas areas na mesma fase colidem na mesma chave.

Interpretacao adotada: seguir a secao 6 ao pe da letra. A chave e o slug da
fase. O campo `evidence` aponta para o artefato, que carrega a area no
frontmatter e no path. O painel por area vive no README da area. Projetos
multi area devem tratar STATE.md como o estado da area corrente.

Efeito: `bin/gate-check` (ST-02), `bin/new-artifact`, `docs/STATE.md`.

## Q3. Qual data compara `guard-write` com a data da decisao

A secao 9 pede "data posterior a ultima modificacao" do arquivo protegido.
Nao diz se a ultima modificacao e o mtime do sistema de arquivos ou a data do
ultimo commit. mtime nao sobrevive a um clone.

Interpretacao adotada: a data do ultimo commit que tocou o arquivo
(`git log -1 --format=%cd`). Sem git ou sem historico do arquivo, cai para o
mtime. A comparacao e por data (YYYY-MM-DD) e usa maior ou igual, porque
decisao e edicao costumam acontecer no mesmo dia.

Efeito: `bin/guard-write`, `bin/guard-commit`.

## Q4. Qual versao do arquivo o `guard-commit` inspeciona

A regra "artefato com status approved e protegido" tem um efeito colateral
que a especificacao nao trata: o proprio ato humano de aprovar troca
`status: proposed` por `status: approved`. Se o guard olhasse o conteudo em
staging, aprovar um gate seria impossivel.

Interpretacao adotada: `guard-write` inspeciona o arquivo como esta em disco
antes da escrita, e `guard-commit` inspeciona o arquivo como esta em HEAD
antes do staging. Em ambos, o que e protegido e o estado ja registrado, nunca
o estado que se pretende gravar. Arquivo novo, ausente em HEAD, e liberado.

Efeito: `bin/guard-write`, `bin/guard-commit`, prova do modo B no README.

## Q5. Formato dos termos proibidos lidos por VC-01

A secao 8 exige VC-01 mas nao define como os termos proibidos sao escritos em
CONTEXT.md.

Interpretacao adotada: uma secao `## Termos proibidos` em
`docs/_context/CONTEXT.md`, com um termo por item de lista. Aceita
`- termo` e `- termo: motivo`. Termo entre crases e tratado como literal. A
busca ignora maiusculas, exige limite de palavra, e nao le a propria secao que
lista os termos.

Efeito: `bin/gate-check` (VC-01), `docs/_context/CONTEXT.md`.

## Q6. Codigo de verificacao para `inputs` vazio fora das fases 01 e 02

A secao 5 diz que `inputs` so pode ser vazio nas fases 01 e 02. A tabela da
secao 8 nao tem codigo para essa verificacao.

Interpretacao adotada: criado o codigo `IN-03`, severidade erro, com teste que
passa e teste que falha, igual aos demais. E o unico codigo fora da tabela da
secao 8.

Efeito: `bin/gate-check`, `bin/tests/test_gate_check.py`.

## Q7. `bin/decide` ausente da arvore da secao 3

A secao 3 nao lista `bin/decide` na arvore do kit, mas a secao 9 o especifica
e a secao 11 depende dele para o slash command `/decide`.

Interpretacao adotada: `bin/decide` existe. A arvore da secao 3 foi tratada
como incompleta, nao como proibicao.

Efeito: `bin/decide`.

## Q8. `bin/tests/` vai para o repositorio alvo

A secao 13 manda copiar `bin/` para `bin/lifecycle/` no alvo, sem dizer se os
testes do kit acompanham.

Interpretacao adotada: `bin/tests/` nao e copiado. O alvo recebe apenas os
executaveis. Os testes sao do kit e rodam no repositorio do kit.

Efeito: `install.sh`.

## Q9. Pastas vazias no repositorio alvo

A secao 3 diz que `.gitkeep` so existe dentro do kit e que `install.sh` nao
cria pastas de area. Mas o alvo precisa de `docs/_handoffs/` e `docs/areas/`.

Interpretacao adotada: `install.sh` cria os dois diretorios no sistema de
arquivos e nao coloca `.gitkeep`. Git nao versiona diretorio vazio, entao
nenhuma pasta vazia entra no historico do alvo. DR-01 continua avisando sobre
pasta vazia dentro de `docs/areas/`, que e o caso que importa.

Efeito: `install.sh`, `bin/gate-check` (DR-01).

## Q10. Laco infinito no hook Stop do Claude Code

A secao 11 manda o hook `Stop` bloquear o encerramento enquanto a sessao
estiver aberta. Um hook Stop que sempre bloqueia pode prender o agente.

Interpretacao adotada: o hook le o stdin do evento e, se o runtime informar
`stop_hook_active` verdadeiro, sai com 0 para nao entrar em laco. Fora esse
caso, bloqueia com exit 2 e a mensagem prevista. A documentacao consultada em
code.claude.com/docs/en/hooks nao lista esse campo no payload de Stop, entao a
protecao e defensiva e inofensiva se o campo nao vier.

Efeito: `adapters/claude-code/.claude/settings.json`,
`adapters/claude-code/.claude/hooks/stop-gate.sh`.

## Q11. Plugin superpowers indisponivel no ambiente de construcao

A secao 14 manda usar o plugin superpowers. O ambiente remoto onde o kit foi
construido nao tem o plugin instalado.

Interpretacao adotada: a metodologia da secao 14 foi seguida na mesma ordem e
com as mesmas saidas (brainstorming antes de qualquer arquivo, plano com
tarefas independentes, execucao em ondas com subagentes, testes antes da
implementacao, verificacao antes de declarar pronto, revisao final por
subagente revisor distinto do executor). O que faltou foi a ferramenta, nao o
processo.

Efeito: ordem de construcao do kit.

## Q12. `session_agent` aceita valores fora dos tres previstos

A secao 6 lista `codex | claude-code | human`. A secao 9 exige `--agent` com
esses tres valores.

Interpretacao adotada: `session-open` recusa qualquer outro valor. Um quarto
runtime exige atualizar o kit, o que e proposital: o campo serve para saber
quem operou a sessao, e um valor livre destruiria isso.

Efeito: `bin/session-open`.

## Q13. Aprovacao humana precisa tocar dois arquivos

ST-02 exige que o gate em STATE.md e o frontmatter do artefato concordem.
Logo, aprovar um gate e sempre uma edicao dupla: frontmatter mais STATE.md.
A especificacao nao oferece script para isso, e o principio 4 diz que o agente
nao aprova nada.

Interpretacao adotada: nenhum script de aprovacao foi criado. A edicao dupla e
manual e humana, documentada em `docs/_process/gates.md`. Criar um
`bin/approve` facilitaria justamente o que o principio 4 quer dificultar.

Efeito: `docs/_process/gates.md`, provas dos modos A e B.
