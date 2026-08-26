---
phase: 19-medir
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Medir

## Propósito
Comparar 30 dias de dado real contra o baseline e o alvo declarados no PRD.
O resultado pode ser que a métrica não moveu, e esse resultado também fecha o gate.

## Gate de saída
Trinta dias de dado da métrica do PRD e de uso real, comparados com baseline e alvo do PRD.
- [ ] A série cobre 30 dias corridos, com data de início e fim escritas.
- [ ] Baseline e alvo estão copiados do PRD, com link para o trecho de origem.
- [ ] Uso real está medido em pessoas ou contas distintas, não só em eventos.
- [ ] Há uma decisão escrita: manter, iterar ou desligar, com dono nominal.

## Esqueleto

### Janela medida
<!-- Datas exatas e o que distorce a leitura. Não serve: "último mês", janela escolhida depois do dado. -->

- Início e fim da janela:
- Eventos que afetam a leitura (incidente, campanha, feriado):

### Métrica do PRD contra baseline e alvo
<!-- Números do PRD, sem reinterpretar. Alvo vago no PRD: diga isso, não invente outro.
Não serve: trocar a métrica por outra que subiu. -->

| Métrica | Baseline (PRD) | Alvo (PRD) | Medido em 30 dias | Atingiu |
|---|---|---|---|---|
|  |  |  |  | sim / não |

### Uso real
<!-- Pessoas ou contas distintas e recorrência. Não serve: total de pageviews. -->

- Usuários distintos na janela e quantos voltaram mais de uma vez:
- Uso induzido (campanha, treino, aviso) versus espontâneo:
- Onde o uso para (último passo antes do abandono):

### Leitura
<!-- Três a cinco linhas ligando número a comportamento observado. Não serve: narrativa sem evidência. -->

### Se a métrica não moveu
<!-- Marque uma hipótese e a próxima ação. Alvo atingido: escreva "não aplicável".
Não serve: "precisa de mais tempo" sozinho. -->

- [ ] Ninguém chegou a usar (problema de distribuição)
- [ ] Usaram e abandonaram (problema de produto)
- [ ] Usaram e a métrica não respondeu (métrica errada ou hipótese refutada)
- [ ] Instrumentação incorreta (o dado não reflete o comportamento)
- Próxima ação, dono e prazo:

### Decisão
<!-- Manter, iterar ou desligar. Um humano decide. O agente registra, não aprova. -->

## Anti-padrões
- Trocar a métrica do PRD por outra depois de ver o resultado. Isso apaga a hipótese original e o aprendizado junto com ela.
- Contar evento em vez de pessoa. Dez mil eventos de três usuários parecem adoção e não são.
- Encerrar a janela cedo porque o número já está bom. Trinta dias existem para pegar o retorno, não a novidade.

## Modo reverso
Sem PRD, o baseline sai do período equivalente anterior ao lançamento, com a mesma query, e fica marcado como baseline reconstruído.
O uso real sai de logs, banco ou analytics já existentes, sempre contando identidade distinta e não evento.
Se não existe alvo declarado em lugar nenhum, não invente: registre open_question no STATE.md e peça o alvo a um humano.
Se a série tem menos de 30 dias, escreva quantos dias existem e mantenha o gate aberto até completar a janela.
