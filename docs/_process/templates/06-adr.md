---
phase: 06-adr
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# ADRs

## Propósito
Registrar cada decisão irreversível em um arquivo MADR próprio.
Guardar as opções descartadas e o preço que a decisão cobra depois.

## Gate de saída
Toda decisão irreversível da área tem uma ADR em formato MADR aceita por um humano.
- [ ] Cada ADR vive em `docs/_context/adr/NNNN-slug.md`, uma decisão por arquivo.
- [ ] Toda ADR tem contexto, duas ou mais opções, decisão e consequências boas e ruins.
- [ ] Nenhuma ADR marcada como aceita tem `approved_by: null`.
- [ ] PRD e backlog citam o número da ADR onde a decisão foi tomada.

## Esqueleto

### ADR NNNN: <título que nomeia a escolha>
<!-- Título é a escolha, ex "Usar Postgres como store principal". Não serve rótulo
     de tema, ex "Banco de dados" ou "Arquitetura". -->

#### Contexto e problema
<!-- 3 a 6 linhas. Qual força obriga a decidir agora e qual restrição real limita
     (prazo, custo, time, compliance, contrato existente). Não descreva a solução
     aqui. Não serve "precisamos escolher uma tecnologia". -->

#### Opções consideradas
<!-- Mínimo duas opções que alguém defenderia de verdade. Opção de palha não conta.
     Uma linha a favor e uma contra em cada. Não serve "outras alternativas". -->
- Opção A, <nome>. A favor: ... Contra: ...
- Opção B, <nome>. A favor: ... Contra: ...

#### Decisão
<!-- Uma frase no formato "Escolhemos X". Depois 1 a 3 linhas ligando a escolha ao
     critério declarado no contexto. Não serve "é a melhor prática do mercado". -->

#### Consequências
<!-- As duas listas são obrigatórias. Ruim é o que passa a doer: custo, lock-in,
     latência, trabalho manual. Lista de ruins vazia significa decisão não entendida. -->
- Boas:
- Ruins:

#### Reversibilidade e status
<!-- Diga o que custaria voltar atrás em dinheiro, tempo ou migração de dados.
     O agente escreve `proposed` e para. Quem troca para `accepted` e preenche
     `approved_by` e `approved_at` é humano. Não serve o agente aceitar a própria ADR. -->
- Custo de reverter:
- Status: proposed

#### Depois de aceita
<!-- ADR aceita vira arquivo protegido: não se edita. Mudou a decisão, crie uma ADR
     nova e preencha `superseded_by` na antiga apontando para a nova. -->

## Anti-padrões
- ADR escrita depois do código já mergeado. Vira ata, não decisão: ninguém pode mais escolher outra opção.
- Segunda opção inventada só para preencher a seção. Esconde que nunca houve comparação real e deixa a reversão sem alternativa mapeada.
- Agente marca `status: accepted` por conta própria. Quebra o gate: a decisão passa sem nenhum humano responsável por ela.

## Modo reverso
Liste no código e na infra o que hoje seria caro trocar (banco, runtime, autenticação,
formato de API, provedor de deploy). Cada item vira uma ADR retroativa, com contexto e
opções reconstruídos de commits, README, issues e PRs antigos. Opção descartada que
ninguém lembra vira `open_question` no STATE.md, nunca suposição. Nasce `proposed`.
