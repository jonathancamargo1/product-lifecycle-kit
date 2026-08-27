# Definition of Ready

Uma fase pode comecar quando todos os itens abaixo sao verdadeiros. Os itens
marcados com codigo sao verificados por `gate-check`; os demais sao
julgamento humano e entram no README da area.

## Verificado por maquina

- [ ] O `tier` em `docs/STATE.md` e 1, 2 ou 3 (ST-05). Sem tier declarado o
      kit nao sabe quais fases exigir, e o sequenciamento fica desligado.
- [ ] Toda fase obrigatoria anterior, pelo tier declarado, esta `approved`
      (SQ-01).
- [ ] `docs/STATE.md` e parseavel e tem todos os campos (ST-01).
- [ ] Nao ha decisao `PENDING` em `decisions.log` sem `blocked_by`
      correspondente (DC-01).
- [ ] Todo path em `inputs` do artefato existe (IN-01).
- [ ] Nenhum termo proibido do glossario aparece no codigo ou nos documentos
      (VC-01).

## Julgamento humano

- [ ] O tier declarado corresponde ao tamanho real da mudanca.
- [ ] Existe uma pessoa nomeada como `owner`, nao um time.
- [ ] As `open_questions` abertas nao bloqueiam esta fase especifica.
- [ ] Os inputs desta fase estao aprovados, nao apenas `proposed`.
- [ ] Nenhum input esta marcado `STALE` sem alguem ter olhado o motivo.

## Como usar

Rode `bin/lifecycle/gate-check --phase <slug>` antes de comecar. Se sair 1, a
fase nao esta pronta e o relatorio diz o que falta. `new-artifact` roda essa
verificacao sozinho e se recusa a criar o artefato se ela falhar.

Se o bloqueio for uma duvida de negocio, abra a decisao com
`bin/lifecycle/decide` e encerre a sessao. Nao contorne o gate.
