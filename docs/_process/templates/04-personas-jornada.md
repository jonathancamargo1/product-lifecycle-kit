---
phase: 04-personas-jornada
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Personas e jornada

## Propósito
Descrever quem usa e o caminho real que essa pessoa percorre hoje, sem o produto.
Apontar onde dói mais e em que passo exato o produto entra.

## Gate de saída
Existe a jornada as-is em passos, com pontos de dor rankeados e o passo onde o produto entra marcado.
- [ ] A jornada descreve o fluxo atual, incluindo planilha, WhatsApp e gambiarra.
- [ ] Cada dor tem posição única no ranking e o critério do ranking está escrito.
- [ ] Exatamente um passo está marcado como ponto de entrada do produto.
- [ ] Cada persona tem pelo menos um atributo que muda decisão de produto.

## Esqueleto

### Personas
<!-- Uma por bloco, no máximo 3. Só entra atributo que muda decisão: o que a
pessoa decide, o que a impede, com que frequência faz a tarefa, que ferramenta
usa hoje. Não serve idade, foto, hobby nem biografia de personagem. -->
- Persona:
  Decide:
  Faz a tarefa (frequência):
  Ferramenta que usa hoje:
  O que a trava:
  Fonte (id da fase 02):

### Jornada as-is
<!-- Passos numerados do gatilho até o desfecho, como acontece hoje. Cada passo
diz quem faz, onde faz e quanto tempo leva. Não serve jornada da solução futura
nem passo sem ator. -->
| # | Passo | Quem faz | Onde | Tempo | Dor |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |

### Dores rankeadas
<!-- Ranking sem empate. Escreva o critério antes da tabela (frequência vezes
custo, ou risco). Cada dor aponta o passo da jornada e a evidência. Não serve
"alta, média, baixa" sem critério. -->
Critério do ranking:

| Posição | Dor | Passo | Evidência (id) |
|---|---|---|---|
| 1 |  |  |  |

### Onde o produto entra
<!-- Número do passo, o que muda nele e por que este passo e não o anterior.
Não serve "melhora a jornada toda". -->
Passo de entrada:
O que muda nele:
Por que aqui:

## Anti-padrões
- Persona com biografia e sem decisão. Não muda nenhuma escolha de produto.
- Desenhar a jornada já com a solução dentro. Some a dor que justifica o trabalho.
- Ranking de dor por intuição do time. Contradiz o gate da fase 02.

## Modo reverso
Personas saem de perfis reais no banco, papéis de permissão e segmentos de CRM.
A jornada as-is sai de funis de analytics, logs de sessão e caminhos de suporte.
Dores rankeadas saem de volume de ticket por etapa e taxa de abandono por tela.
Passo sem dado observado vira `open_question` no STATE.md, nunca passo inventado.
