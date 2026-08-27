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

## Q14. Acentuacao: templates acentuados, resto do kit em ASCII

Os 20 templates de fase usam portugues acentuado nos titulos de secao
(`## Proposito` saiu como `## Propósito`). Os documentos de processo, o
AGENTS.md, os scripts e este arquivo usam portugues sem acento, por escolha
de portabilidade.

Interpretacao adotada: as duas convencoes convivem. O texto acentuado e
portugues correto e os templates sao o que o humano mais le; o resto do kit e
ASCII para nunca depender de locale em terminal, hook ou pipe. Nenhum script
casa titulo de secao por texto, entao a divergencia nao quebra nada.

Se voce preferir uma convencao unica, a decisao e sua: acentuar tudo e mais
correto, tirar acento de tudo e mais portavel.

Efeito: `docs/_process/templates/*.md` versus o restante do kit.

## Q15. `gate-check` ignora `README.md` sob `docs/areas/`

FM-01 exige frontmatter em todo `.md` sob `docs/areas/`. Mas o painel da area
e um `README.md` que nasce de `area-readme.md`, e a secao 4 nao da frontmatter
a esse template.

Interpretacao adotada: `README.md` sob `docs/areas/` e excluido de FM-01. E
painel, nao artefato: nao tem gate, nao tem `inputs` e nao tem aprovacao.

Efeito: `bin/gate-check`, funcao `artifacts()`.

## Q16. VC-01 nao varre `docs/_process/`

VC-01 deveria varrer `docs/` inteiro atras de termos proibidos. Mas
`docs/_process/` e material do kit, nao vocabulario do projeto, e templates
genericos acionam falso positivo em qualquer glossario minimamente restritivo.

Interpretacao adotada: VC-01 pula `docs/_process/`. Varre `docs/` fora dele,
mais `src/`, `app/` e `packages/`.

Efeito: `bin/gate-check`, funcao `check_vocabulary()`.

## Q17. `new-artifact` ganhou `--inputs` e passou a exigi-lo

A secao 9 nao da a `new-artifact` nenhuma forma de declarar `inputs`. Mas a
secao 5 proibe `inputs` vazio fora das fases 01 e 02. Sem a opcao, todo
artefato criado da fase 03 em diante nasceria reprovado pelo proprio
`gate-check`, travando o `session-close` seguinte.

Interpretacao adotada: `--inputs a,b` foi acrescentado, e `new-artifact`
recusa criar sem ele fora das fases 01 e 02, alem de recusar input
inexistente. A regra passa a ser imposta na criacao, e nao descoberta depois.

Efeito: `bin/new-artifact`.

## Q18. O painel da area e vista derivada, regerada por script

A secao 4 exige um painel de gates por area com coluna `Status`. O principio 8
diz que status vive em dois lugares apenas. Sao exigencias que se chocam: o
painel e uma terceira copia do status.

Interpretacao adotada: o painel e vista derivada, nunca fonte.
`kit.refresh_area_panels()` reescreve a tabela inteira a partir de
`docs/STATE.md`, e roda em todo `new-artifact` e em todo `session-close`.
Assim a terceira copia existe (a secao 4 pede) mas nao pode divergir (o
principio 8 exige). Fases nao obrigatorias pelo tier nao entram no painel.

Efeito: `bin/_kitlib.py`, `bin/new-artifact`, `bin/session-close`.

## Q19. A garantia do hook Stop no enforcement comum

A secao 2 exige que toda garantia de adaptador exista tambem no enforcement
comum. O hook `Stop` do Claude Code impede encerrar com a sessao aberta.
Nenhum outro runtime tem equivalente, e a deteccao tardia via `session-open`
nao serve: quando ela acontece, o handoff daquela sessao ja foi perdido.

Interpretacao adotada: `guard-commit` recusa qualquer commit que toque
`docs/` enquanto `session_open` for `true`. Commit de codigo fora de `docs/`
passa livre, para o protocolo de sessao nao virar refem de um commit de
fonte. Trabalho de processo nao entra no historico sem handoff, em qualquer
runtime.

Uma garantia continua so no adaptador, e nao ha como impor por maquina: o
`SessionStart` carrega o contexto sozinho no Claude Code, e nos demais
runtimes isso depende de o agente ler `AGENTS.md`. Nenhum script obriga um
agente a ler antes de agir.

Efeito: `bin/guard-commit`, `adapters/codex/README.md`.

## Q20. Adicoes a arvore da secao 3

Alem de `bin/decide` (Q7), o kit tem quatro arquivos que a arvore da secao 3
nao lista:

- `bin/_kitlib.py`: biblioteca compartilhada pelos scripts. Sem ela, o parser
  de YAML, o contrato de frontmatter e a regra de path protegido estariam
  copiados em sete executaveis.
- `adapters/claude-code/merge-settings.py`: mescla hooks num
  `.claude/settings.json` que ja existe, como a secao 13 pede. Vive no
  adaptador, nao no nucleo, porque so serve a um runtime.
- `adapters/claude-code/.claude/hooks/`: dois wrappers de encanamento. O
  runtime entrega o evento como JSON no stdin, e os scripts do nucleo recebem
  argumentos. Os wrappers so traduzem entre os dois, sem nenhuma regra propria.
- `proofs/`: os scripts que geram as provas do README, para que a secao
  "Prova de funcionamento" seja reproduzivel e nao apenas colada.

Efeito: arvore do kit.

## Q21. Codigo ST-04, para `last_session` apontar para arquivo que existe

A tabela da secao 8 tem ST-03 para o `evidence` dos gates, mas nada para
`last_session`. Uma revisao encontrou o buraco: era possivel ficar com
`last_session` apontando para um handoff inexistente e `gate-check` sair 0.

Interpretacao adotada: criado o codigo `ST-04`, severidade erro, com teste que
passa e teste que falha. E o segundo codigo fora da tabela da secao 8, junto
com IN-03 (Q6).

Efeito: `bin/gate-check`, `bin/tests/test_session.py`.

## Q22. `new-artifact --supersede`

A secao 9 nao diz o que acontece quando `new-artifact` roda numa fase que ja
tem artefato. O comportamento inicial era sobrescrever o gate em STATE.md, o
que apagava `by` e `date` de uma aprovacao humana (contra o principio 4) e
deixava dois artefatos vivos no mesmo gate (contra o principio 7).

Interpretacao adotada: `new-artifact` recusa criar num gate que ja tem
artefato. Com `--supersede`, cria o novo e marca o anterior com
`status: superseded` e `superseded_by` apontando para o substituto, que e
exatamente o fluxo que o principio 7 descreve. Substituir passa a ser ato
explicito, nunca efeito colateral.

Efeito: `bin/new-artifact`, `docs/AGENTS.md`.

## Q23. Nao existe atalho para desligar o enforcement comum

Durante a construcao os git hooks tinham uma variavel de ambiente que os
desligava. Uma revisao apontou o obvio: o hook mora dentro do repositorio que
o agente opera, entao qualquer agente que leia `.git/hooks/pre-commit`
descobre o atalho, e no modo Codex o enforcement comum e a unica rede que
existe.

Interpretacao adotada: a variavel foi removida. Nao ha, e nao deve haver,
forma sancionada de pular os hooks.

Fica registrado o que nenhum hook pode fechar: `git commit --no-verify` e do
proprio git e ignora qualquer hook. Isso vale para todo repositorio do mundo e
nao e uma brecha do kit. A diferenca e que `--no-verify` deixa rastro obvio na
intencao de quem o digitou, enquanto uma variavel do kit pareceria sancionada.

Efeito: `git-hooks/pre-commit`, `git-hooks/commit-msg`.

## Q24. As provas nao alteram o kit

A prova do modo C precisa de uma versao nova do kit. Fazer isso no proprio
repositorio deixava o kit permanentemente numa versao diferente da que estava
colada nas provas dos modos A e B, o que quebrava a reproducibilidade que a
secao 15 exige.

Interpretacao adotada: `proofs/modo-c-update.sh` monta a versao nova numa
copia temporaria do kit e roda o `install.sh` de la. O kit real nunca e
tocado, e o modo C pode rodar quantas vezes for preciso, sempre com o mesmo
resultado.

Efeito: `proofs/modo-c-update.sh`, versao publicada do kit.

## Q25. Como o `install.sh --update` consegue ser commitado

`docs/_process/**` e glob protegido, e `--update` reescreve exatamente esses
arquivos. Uma revisao encontrou o impasse: depois de uma atualizacao legitima
do kit, o projeto nao conseguia commitar o resultado.

Interpretacao adotada: `guard-commit` libera um path protegido quando o
sha256 do conteudo em staging bate com o que `install.sh` gravou em
`docs/.kit-manifest`. So o conteudo que o proprio kit instalou passa; qualquer
edicao a mao no mesmo arquivo continua barrada, porque o hash deixa de bater.

Nao e porta dos fundos: para burlar, o agente teria que reproduzir byte a byte
um arquivo do kit, que e o mesmo que nao ter mudado nada.

Efeito: `bin/_kitlib.py`, `bin/guard-commit`, `bin/tests/test_guards.py`.

## Q26. `session-close` roda o gate-check antes de mexer no estado

A secao 9 descreve a ordem: mover o handoff, atualizar `last_session`, marcar
`session_open: false`, rodar `gate-check`, commitar se sair 0. Seguir isso ao
pe da letra criava um beco sem saida: com o gate falhando, a sessao ficava
fechada, nada era commitado, e `session-close` recusava rodar de novo por nao
haver sessao aberta. So dava para sair editando `docs/STATE.md` a mao.

Interpretacao adotada: `gate-check` roda antes de qualquer mutacao. No caminho
feliz o resultado e identico ao da secao 9. No caminho de erro a sessao
continua aberta e o handoff intacto, entao basta corrigir e rodar de novo.

Efeito: `bin/session-close`, `bin/tests/test_session.py`.

## Q27. Codigo ST-05, para tier nao declarado

O kit instala com `tier: null`, e `required_phases(None)` devolve `None`, o que
faz SQ-01 nao ter o que verificar. O efeito, encontrado depois do primeiro
merge: um projeto onde ninguem preencheu o tier rodava com o sequenciamento
desligado, e o `gate-check` dizia "nenhuma ocorrencia". Dava para criar o
artefato da fase 13 sem nunca ter passado pela 01.

Interpretacao adotada: criado o codigo `ST-05`, severidade erro, que dispara
quando o projeto ja tem gate registrado ou `current_phase` definida e o `tier`
nao e 1, 2 nem 3. Projeto recem instalado, ainda sem trabalho nenhum, nao e
cobrado, senao o `gate-check` que o `install.sh` roda no fim ja acusaria.

`tem_trabalho` considera tres sinais: gate registrado, `current_phase`
definida, ou qualquer artefato em `docs/areas/`. O terceiro cobre o modo
reverso, em que o backfill escreve os artefatos antes de mexer no estado.

Alem disso, `new-artifact` recusa criar sem tier declarado, e `install.sh`
termina imprimindo os proximos passos, com o preenchimento de `project` e
`tier` em primeiro lugar. E o terceiro codigo fora da tabela da secao 8, junto
com IN-03 (Q6) e ST-04 (Q21).

A alternativa seria o `install.sh` perguntar o tier na instalacao. Foi
descartada: `install.sh` precisa rodar sem terminal interativo, dentro de uma
sessao de agente.

O que ST-05 nao cobre, e vale saber: ele obriga a declarar o tier, mas o
SQ-01 continua olhando apenas a `current_phase`. Um `STATE.md` preenchido a
mao, com gates registrados e sem `current_phase`, tem o tier cobrado mas nao
tem o sequenciamento verificado.

Ampliar o SQ-01 para varrer todo gate aberto foi tentado e revertido, porque
colide de frente com Q2: os gates sao chaveados so pela fase, entao quando uma
segunda area comeca uma fase anterior ela sobrescreve aquele gate, e todo gate
posterior ainda aberto passaria a falhar. O efeito medido foi um projeto
travado, sem poder commitar nem fechar a sessao, depois de um `new-artifact`
que tinha acabado de suceder. O teste
`test_sq01_nao_trava_segunda_area_na_mesma_fase` existe para impedir que
alguem tente de novo sem resolver Q2 antes.

Efeito: `bin/gate-check`, `bin/new-artifact`, `install.sh`,
`bin/tests/test_gate_check.py`, `bin/tests/test_new_artifact.py`.

## Q28. `bin/plan`, e por que o painel nao bastava

A especificacao nao pede um comando de plano. Na pratica faltava: o painel da
area lista o que existe, e o `gate-check` verifica o que existe. Nenhum dos
dois sabe dizer o que nunca foi comecado. Num projeto tier 2 com uma unica
fase criada, o painel mostrava uma linha e o `gate-check` saia 0, entao um
projeto com 11 de 12 fases faltando parecia completo.

Interpretacao adotada: `bin/plan` compara as fases obrigatorias do tier com os
gates existentes, imprime as que faltam em ordem e monta a proxima acao pronta
para copiar. O painel da area passou a listar as fases pendentes tambem, pelo
mesmo motivo: por omissao, ele mentia.

Consequencia aceita em projeto multi area: cada painel lista todas as fases
obrigatorias do tier, inclusive as que aquela area ainda nao comecou, e o
`Status geral` daquela area so fica `concluida` quando ela mesma fechou todas.
Isso e ruido quando as areas dividem fases entre si de proposito, e e a
resposta certa quando cada area e uma fatia de produto que percorre o ciclo
inteiro. O kit assume a segunda leitura. Se a sua for a primeira, o painel vai
parecer pessimista, e o `plan` tambem: os dois sao area cega, como o mapa de
gates (Q2).

Efeito: `bin/plan`, `bin/_kitlib.py` (`refresh_area_panels`),
`docs/_process/session-protocol.md`, adaptador do Claude Code (`/plan`).

## Q29. Codigo entrando sem fase de build

Medido antes de existir a regra: um agente commitava feature atras de feature
sem nunca rodar `session-open` nem criar artefato, e o `gate-check` respondia
"nenhuma ocorrencia", exit 0. O kit garantia integridade e ordem de quem
estava usando, e nada sobre alguma fase acontecer.

Interpretacao adotada, decidida com o dono do kit: **nao** e bloqueio
automatico. Commit que toca codigo do produto exige a fase corrente ser
`13-build-log` ou posterior; fora disso o `commit-msg` recusa, nomeia os
arquivos, e diz o que se perde (codigo sem spec, sem review de papel distinto,
sem rastro da decisao que o originou).

A saida exige ato deliberado: a linha `Sem-fase: <motivo, e quem autorizou>`
no proprio commit. Tres consequencias de desenho:

- Quem autoriza e humano. `AGENTS.md` proibe o agente de escrever o trailer
  por conta propria, com a analogia direta: autorizar a si mesmo e o mesmo que
  aprovar o proprio gate.
- A autorizacao fica no historico do git para sempre, nao num arquivo que
  alguem limpa depois.
- `gate-check` conta quantas existem (`PH-01`, aviso) e mostra em toda sessao,
  porque `session-open` roda o `gate-check`. A divida nao some de vista.

O limite que fica, e nenhum hook fecha: o trailer e texto de commit, entao um
agente que decida mentir consegue escreve-lo sozinho. E o mesmo teto do
`git commit --no-verify` (Q23). O kit torna o desvio caro, visivel e
permanente; nao torna impossivel.

A partir de que fase codigo e legitimo esta em `_kitlib.CODE_PHASE_FROM`, hoje
13. O SQ-01 garante que tudo que o tier exige antes da 13 ja esta aprovado
quando ela abre, entao exigir a 13 e o mesmo que exigir o PRD, a spec e o
backlog nos tiers que os tem.

Efeito: `git-hooks/commit-msg`, `bin/gate-check` (PH-01), `bin/_kitlib.py`,
`docs/AGENTS.md`, `docs/_process/lifecycle.md`.
