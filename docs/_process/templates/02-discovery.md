---
phase: 02-discovery
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Discovery

## Propósito
Transformar o contexto em um problem statement sustentado por evidência externa.
Separar o que foi observado fora do time do que o time acredita.

## Gate de saída
O problem statement se sustenta em evidência externa (entrevistas, dados, suporte, benchmark), nunca em opinião do time.
- [ ] Cada afirmação do problem statement tem fonte citável ao lado dela.
- [ ] Há no mínimo 3 fontes e no mínimo 2 tipos de fonte diferentes.
- [ ] Toda fonte é rastreável: id de entrevista, query, id de ticket ou link.
- [ ] Evidência que contradiz a tese está registrada, não omitida.

## Esqueleto

### Problem statement
<!-- 3 a 5 linhas. Quem sofre, o que acontece, com que frequência, qual o custo.
Cada frase termina com o id da fonte entre colchetes. Não serve frase sem id,
"os usuários reclamam muito" nem "acreditamos que". -->

### Evidência
<!-- Uma linha por fonte. Tipo: entrevista, dado, suporte ou benchmark.
O rastro precisa permitir que outra pessoa reabra a fonte sozinha: id e data da
entrevista, a query SQL ou o link do dashboard, o id do ticket, a URL do estudo.
Não serve "conversas com clientes" nem "sabemos pelo suporte". -->
| id | Tipo | Rastro | O que mostra | Data |
|---|---|---|---|---|
| E1 |  |  |  |  |

### Tamanho do problema
<!-- Quantas pessoas ou casos por período, e o custo em dinheiro, tempo ou risco.
Escreva a conta e a fonte de cada número. Não serve estimativa sem conta. -->

### Evidência contrária
<!-- O que apareceu e enfraquece a tese. Se não houver, escreva o que você
procurou e não achou. Não serve deixar vazio. -->

### Opiniões do time
<!-- Tudo que o time acha e não conseguiu comprovar fica aqui, fora do problem
statement. Cada item vira suposição na fase 03 ou `open_question` no STATE.md. -->

### Lacunas de evidência
<!-- O que falta apurar e quem apura. Dúvida de negócio vira `open_question`
no STATE.md, com o id citado aqui. Nunca vira suposição silenciosa. -->

## Anti-padrões
- Citar "feedback de clientes" sem id de entrevista. Ninguém consegue conferir.
- Usar relatório de mercado como única fonte. Não prova o problema do seu usuário.
- Promover opinião do time a problem statement por falta de dado. Inverte o gate.

## Modo reverso
Reconstrua evidência de tickets de suporte, sessões de analytics, logs de erro e
notas de CS já existentes; cite id e período de cada extração.
Entrevistas antigas só valem com data e roteiro recuperáveis.
Onde não houver fonte, escreva a lacuna e abra `open_question` no STATE.md.
