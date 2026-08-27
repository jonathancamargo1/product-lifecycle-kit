from pathlib import Path
SP = Path("/tmp/claude-0/-home-user-product-lifecycle-kit/60dcdfed-09ac-5fd3-bcc6-7904234f2c90/scratchpad")
def b(n): return (SP / n).read_text(encoding="utf-8").rstrip("\n")
F = chr(96) * 3
partes = [b("readme-topo.md")]
partes.append("""
## Estrutura

Arvore do kit:

%stext
%s
%s

Arvore de um projeto alvo recem instalado com `install.sh . --adapters all`,
antes de qualquer fase comecar. `docs/areas/` nasce vazio porque estrutura so
nasce quando o artefato nasce:

%stext
%s
%s

Arvore de um projeto alvo depois de `install.sh . --adapters claude-code`, com
as quatro fases do tier 1 ja executadas. E a saida real do modo A:

%stext
%s
%s

`bin/lifecycle/` tem esse nome para nao colidir com um `bin/` que o projeto ja
tenha. Os testes do kit nao sao copiados para o alvo.
""" % (F, b("arvore-kit.out").split("\n", 1)[1], F,
       F, b("arvore-all.txt"), F,
       F, b("arvore-alvo.out").split("\n", 1)[1], F))

blocos = [
    ("### Testes", """Um caso que passa e um que falha para cada codigo de `gate-check`, mais os
testes dos guards, das sessoes, do `new-artifact` e do round-trip de YAML.""", "testes.out"),
    ("### Modo A: repositorio operado pelo Claude Code", """`proofs/modo-a-claude-code.sh`. Instala com `--adapters claude-code`, declara o
projeto `prova-a` no tier 1 e roda as quatro fases obrigatorias do tier (01,
13, 14, 17) em quatro sessoes. Entre uma sessao e outra, um humano aprova o
gate editando o frontmatter e o `docs/STATE.md`.

Os hooks de runtime do Claude Code chamam exatamente estes scripts. Como nao ha
uma sessao do Claude Code viva dentro da prova, os scripts sao invocados
diretamente, que e o que o hook faria.

Demonstra, na ordem: `session-open` recusando abrir com a sessao anterior
aberta (3a); `session-close --check` saindo 1 com a sessao aberta e 0 depois
(3b e 3e); `gate-check --phase 13-build` saindo 1 antes de aprovar a fase 01 e
0 depois (3c e 4a); e `guard-write` saindo 2 num artefato aprovado (4b).""", "prova-a.out"),
    ("### Modo B: repositorio operado pelo Codex", """`proofs/modo-b-codex.sh`. Instala com `--adapters codex`, que nao instala hook
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
  a mesma mudanca passa com uma mensagem que nao e de sessao (8a).""", "prova-b.out"),
    ("### Modo C: atualizacao", """`proofs/modo-c-update.sh`. Com o projeto `prova-b` ja instalado na versao
1.0.0, monta uma copia temporaria do kit na versao 1.1.0, com a secao
correspondente no `CHANGELOG.md`, e roda o `install.sh` dessa copia com
`--update`.

O que a prova mede: uma soma sha256 de tudo que o `--update` tem proibido
tocar, tirada antes e depois. `docs/STATE.md`, `docs/_handoffs/` e
`docs/areas/` ficam identicos; so `docs/KIT_VERSION`, os scripts e o manifesto
mudam. O bloco 6 mostra que o kit real continua na versao de antes.

Os arquivos de processo que o `--update` reescreve podem ser commitados porque
`guard-commit` reconhece, pelo sha256 em `docs/.kit-manifest`, o que o proprio
kit instalou. Edicao a mao no mesmo arquivo continua barrada.""", "prova-c.out"),
    ("### Instalacao sem nenhum adaptador", """Criterio de aceite: `install.sh --adapters none` num repositorio vazio termina
com `gate-check` exit 0 e os dois git hooks instalados. E o caso que prova o
principio 12, o de que o nucleo nao depende de agente nenhum. Repare tambem no
aviso impresso no fim: sem `tier` declarado o kit nao sabe o que exigir, e diz
isso em vez de deixar passar.""", "prova-none.out"),
    ("### Encadeamento de hooks e merge de settings", """`proofs/encadeamento.sh`. A secao 13 exige que `install.sh` encadeie um hook de
git que ja exista, em vez de sobrescrever, e que mescle os hooks num
`.claude/settings.json` do projeto sem remover os que ja estavam la. Esta prova
instala num repositorio que ja tem os dois.""", "encadeamento.out"),
    ("### Varredura de caracteres e limites", """Nenhum arquivo do kit contem o caractere travessao longo nem emoji. Nenhum
template passa de 80 linhas, `docs/AGENTS.md` nao passa de 60, e
`adapters/claude-code/CLAUDE.md` tem exatamente 2. Nenhuma pasta vazia fora dos
`.gitkeep` previstos.

O proprio scanner nunca escreve o travessao literalmente: ele monta o caractere
a partir do codepoint U+2014. Se o escrevesse, o arquivo do scanner seria uma
ocorrencia e a varredura acusaria a si mesma.""", "varredura.out"),
]

prova = ["""
## Prova de funcionamento

Tudo abaixo e saida real, colada sem edicao, gerada com o kit na versao 1.0.0.
Os scripts que produzem cada bloco estao em `proofs/` e podem ser rodados de
novo do zero. Nenhum deles altera o kit: a prova do modo C monta a versao nova
numa copia temporaria, justamente para que os outros blocos continuem
reproduziveis.
"""]
for titulo, texto, arquivo in blocos:
    prova.append("\n%s\n\n%s\n\n%stext\n%s\n%s\n" % (titulo, texto, F, b(arquivo), F))
partes.append("".join(prova))

partes.append("""
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
""")
Path("README.md").write_text("\n".join(partes) + "\n", encoding="utf-8")
print("README reescrito")
