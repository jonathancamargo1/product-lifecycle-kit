# Definition of Done

Uma fase termina quando todos os itens abaixo sao verdadeiros.

## Verificado por maquina

- [ ] O artefato tem frontmatter completo e valido (FM-01, FM-02).
- [ ] `inputs` aponta para arquivos que existem (IN-01), e nao esta vazio fora
      das fases 01 e 02 (IN-03).
- [ ] O gate em `docs/STATE.md` concorda com o frontmatter do artefato
      (ST-02) e o `evidence` existe (ST-03).
- [ ] `approved` traz `approved_by` e `approved_at` (FM-03), e `approved_by`
      nao e um agente (FM-04).
- [ ] Artefato substituido traz `superseded_by` (FM-05).
- [ ] `gate-check` sai com 0.

## Julgamento humano

- [ ] O criterio binario da secao "Gate de saida" do template esta satisfeito,
      com evidencia apontavel, nao com afirmacao.
- [ ] O que nao coube no artefato virou `open_question`, nao suposicao.
- [ ] Nenhum campo do template ficou com texto placeholder.
- [ ] Um humano leu e aprovou. O agente parou em `proposed`.

## O que nao conta como pronto

- Artefato marcado `approved` pelo agente. Isso e erro, e `gate-check` recusa.
- Gate marcado sem `evidence`, ou com `evidence` apontando para arquivo que
  nao existe.
- Criterio de aceite escrito em prosa, quando o template pede verificavel por
  maquina.
- Suposicao de regra de negocio disfarcada de decisao tecnica.
