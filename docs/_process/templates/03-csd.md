---
phase: 03-csd
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# CSD e glossário

## Propósito
Separar o que está provado do que é aposta e do que ninguém sabe.
Dar plano de validação às apostas críticas e travar a linguagem no CONTEXT.md.

## Gate de saída
Toda suposição crítica tem plano de validação com custo e prazo, e `docs/_context/CONTEXT.md` está atualizado.
- [ ] Cada suposição marcada como crítica tem método, custo e data de resposta.
- [ ] Cada certeza aponta para uma evidência da fase 02 pelo id.
- [ ] Cada dúvida virou `open_question` no STATE.md, com o id citado aqui.
- [ ] CONTEXT.md tem os termos novos e a seção "Termos proibidos" atualizada.

## Esqueleto

### Certezas
<!-- Só entra o que tem evidência externa citada pelo id da fase 02.
Não serve consenso do time nem "todo mundo sabe". -->
| Afirmação | id da evidência |
|---|---|

### Suposições
<!-- Crítica significa: se estiver errada, o escopo muda ou o trabalho morre.
Custo em horas ou dinheiro, prazo em data. Não serve "validar com o time",
"vamos ver no beta" nem plano sem data. -->
| Suposição | Crítica? | Como valida | Custo | Responde até | Dono |
|---|---|---|---|---|---|

### Dúvidas
<!-- O que ninguém sabe e ninguém consegue supor com honestidade. Cada linha
vira `open_question` no STATE.md. Não converta dúvida em suposição. -->
| Dúvida | id no STATE.md | Quem responde |
|---|---|---|

### Glossário
<!-- Termos que mudam decisão ou que o time usa com sentidos diferentes.
Definição em uma frase, mais o termo que ele substitui. Não serve dicionário
de palavras óbvias. Copie cada linha para docs/_context/CONTEXT.md. -->
| Termo | Definição em uma frase | Substitui |
|---|---|---|

### Termos proibidos
<!-- Termo ambíguo ou herdado que não pode mais aparecer em artefato, e o que
usar no lugar. Estes vão para a seção "Termos proibidos" do CONTEXT.md e são
verificados por script. -->
- termo: use X no lugar, porque

## Anti-padrões
- Marcar tudo como certeza para acelerar o gate. A aposta não some, só fica invisível.
- Plano de validação sem data e sem custo. Nunca sai da fila e nada é decidido.
- Glossário com termo que ninguém disputa. Vira cerimônia e ninguém lê.

## Modo reverso
Certezas já existentes saem de métricas em produção e de testes que rodam hoje.
Suposições aparecem em comentários de código, feature flags antigas e TODOs.
O glossário sai dos nomes reais de tabelas, endpoints e telas, comparados ao termo
que o negócio usa. Termo cujo sentido ninguém confirma vira `open_question`.
