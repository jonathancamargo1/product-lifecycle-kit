---
phase: 01-contexto
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Contexto

## Propósito
Registrar por que este trabalho existe, quem pede e o que limita a solução.
Fechar o espaço do problema antes de qualquer ideia de solução.

## Gate de saída
Existe uma lista explícita do que não será feito.
- [ ] A seção "Não será feito" tem no mínimo 3 itens, cada um com motivo.
- [ ] Cada restrição cita prazo, orçamento, sistema ou regra verificável.
- [ ] O solicitante está nomeado com nome de pessoa, nunca de time.
- [ ] Toda dúvida de negócio virou `open_question` no STATE.md.

## Esqueleto

### Contexto do negócio
<!-- 3 a 5 linhas: o que acontece com o negócio se nada for feito. Use número,
contrato ou fato datado. Não serve "melhorar a experiência", "ficar moderno". -->

### Quem pede
<!-- Nome da pessoa que assume a decisão e o orçamento. Não serve nome de time,
cargo genérico ou "a diretoria". -->

### Por que agora
<!-- O gatilho datado: contrato, mudança regulatória, incidente, janela de
mercado, custo que sobe. Não serve "é prioridade do trimestre". -->

### Restrições
<!-- Liste apenas as que matam soluções. Uma por bloco. Não serve "temos pouco
tempo" sem data, nem "orçamento apertado" sem número. -->
- Restrição:
  Fonte (contrato, política, sistema):
  O que ela proíbe na prática:

### Não será feito
<!-- Este é o gate. Cada item é algo que alguém espera e que ficará de fora,
com motivo. Não serve "fora de escopo" sem dizer qual é o item. -->
- Não faremos:
  Motivo:
  Quem espera isso:

### Dúvidas em aberto
<!-- Registre cada dúvida como `open_question` no STATE.md e cite o id aqui.
Nunca substitua uma dúvida de negócio por suposição própria. -->
- id:
  Pergunta:
  Quem responde:

## Anti-padrões
- Descrever a solução nesta fase. Congela a resposta antes de o problema existir.
- Deixar "Não será feito" genérico. O gate deixa de ser checável por outra pessoa.
- Nomear um time como solicitante. Ninguém responde pela decisão depois.

## Modo reverso
Extraia contexto de tickets, atas, README e do roadmap já publicado.
Restrições reais saem de dependências no código, contratos e limites de infra.
"Não será feito" não se deduz do produto existente: pergunte ao dono da decisão.
Sem resposta, abra `open_question` no STATE.md e deixe o item em branco.
