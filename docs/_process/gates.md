# Gates

Um gate e o criterio binario de saida de uma fase. Ou o criterio esta
satisfeito com evidencia, ou a fase nao terminou. Nao existe gate parcial.

## Estados

| Estado | Significado | Quem escreve |
|---|---|---|
| `in_progress` | Artefato criado, trabalho em andamento | `new-artifact` |
| `proposed` | Agente terminou e considera o criterio satisfeito | agente ou humano |
| `approved` | Humano verificou a evidencia e aprovou | humano, apenas |
| `superseded` | Substituido por outro artefato | humano ou agente |

O agente nunca escreve `approved`. Esse e o principio 4 e e verificado por
maquina: `gate-check` recusa `approved_by` que contenha `agent`, `codex`,
`claude`, `ai` ou `bot`, em qualquer combinacao de maiusculas (codigo FM-04).

## Como um humano aprova um gate

Aprovar e sempre uma edicao dupla. Os dois lugares precisam concordar, e
`gate-check` recusa a divergencia (codigo ST-02).

1. No frontmatter do artefato: `status: approved`, `approved_by: <seu nome>`,
   `approved_at: <YYYY-MM-DD>`.
2. Em `docs/STATE.md`, no mapa `gates`, na chave do slug da fase:
   `status: approved`, `evidence: <path do artefato>`, `by: <seu nome>`,
   `date: <YYYY-MM-DD>`.

Nao existe script de aprovacao, e isso e proposital. Um `bin/approve`
facilitaria justamente o que o principio 4 quer manter dificil e deliberado.

## Confirmacao em bloco, no modo reverso

Gate no modo normal e gate no modo reverso sao atos diferentes com o mesmo
nome. No modo normal, aprovar e autorizar: o artefato e insumo da fase
seguinte, e aprovar cedo compromete o que vem depois. No modo reverso nada
esta sendo autorizado, porque a decisao ja aconteceu e esta no codigo. Aprovar
ali e verificar uma reconstrucao.

Exigir vinte autorizacoes para algo que ninguem esta autorizando e o desenho
que produz carimbo automatico, e um `approved` carimbado e pior que um
`proposed` honesto: mente para todo leitor futuro. Por isso, enquanto
`import_mode` for `reverse`, o gate por fase fica suspenso e a confirmacao
acontece uma vez, em bloco, com `confirm-import`.

Muda a granularidade da deliberacao, nao a natureza dela:

- quem confirma continua sendo humano. `confirm-import` recusa `--by` que
  contenha `agent`, `codex`, `claude`, `ai` ou `bot`, igual ao FM-04.
- toda afirmacao reconstruida carrega `reconstructed_from` no frontmatter, com
  os ponteiros que a sustentam. Sem isso a confirmacao e inauditavel por
  construcao: nao da nem para amostrar. `confirm-import` recusa, e `gate-check`
  acusa `RV-01`.
- pergunta em aberto sem resposta bloqueia a confirmacao. Intencao e nao-escopo
  nunca sao confirmados em bloco, porque nunca estiveram nos artefatos: sao
  resposta que um humano da na sessao.
- o gate confirmado assim fica com `method: reverse-batch` no `STATE.md`. Um
  leitor daqui a um ano precisa conseguir separar o que foi vivido do que foi
  reconstruido, senao o proprio registro mente sobre a propria forca.

`import_mode` cai sozinho na confirmacao. E marcador de importacao, com comeco
e fim, nao um modo de operacao permanente: depois dele o projeto vive no modo
normal e gate se aprova um a um.

## Substituicao

Um gate tem um artefato. Quando um artefato e substituido, o antigo recebe
`status: superseded` e `superseded_by` com o path do substituto (codigo
FM-05). O antigo nunca e apagado: o historico da decisao e parte do contexto.

## Evidencia

`evidence` em `docs/STATE.md` aponta para um arquivo que existe (codigo
ST-03). Um gate marcado como aprovado sem evidencia e erro, nao convencao.

## Frescor dos inputs

Se um artefato listado em `inputs` foi modificado depois do `approved_at`
deste artefato, `gate-check` emite o aviso `STALE` (codigo IN-02). Aviso nao
derruba o build. Serve para lembrar que a base mudou e a conclusao pode nao
valer mais.
