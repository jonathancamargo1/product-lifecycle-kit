---
phase: 15-threat-review
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Red team

## Propósito
Atacar de propósito o que foi construído e listar os riscos por severidade.
Nenhum risco alto sai daqui sem mitigação ou sem aceite explícito com nome e data.

## Gate de saída
Nenhum risco alto em aberto: cada um tem mitigação implementada ou aceite explícito registrado com nome e data.
- [ ] Cada risco tem severidade atribuída (alto, médio, baixo) com o motivo em uma linha.
- [ ] Todo risco alto tem mitigação aplicada e verificada, ou linha de aceite preenchida.
- [ ] Cada aceite traz nome de pessoa e data, nunca nome de time.
- [ ] Risco alto que exige mudança de contrato voltou à fase 11 com o ID do retorno registrado.

## Esqueleto

### Escopo do ataque
<!-- O que foi exercitado: endpoints, telas, integrações, jobs. Diga também o que ficou de fora e por quê. Não serve "o sistema". -->

### Método
<!-- Como atacou: revisão de código, requisição manipulada, ferramenta usada, dado malicioso. Não serve "análise de segurança". -->

### Riscos
<!-- Repita o bloco por risco, do mais severo para o menos. -->

#### R-NN: <título do risco>
- Severidade: <!-- alto, médio ou baixo, com o motivo em uma linha. -->
- Vetor: <!-- quem ataca e por qual caminho concreto, com o passo a passo reproduzível. -->
- Impacto: <!-- o que o atacante consegue: dado exposto, ação indevida, indisponibilidade. Não serve "grave". -->
- Mitigação: <!-- o que foi feito e onde, com commit ou PR, e como foi verificado. -->
- Aceite: <!-- só quando não há mitigação. Nome da pessoa que aceita, data, e até quando vale. Sem nome e data, o gate não fecha. -->

### Riscos herdados da fase 11
<!-- Cada ameaça do threat model inicial que ficou sem mitigação lá, com o desfecho aqui. Nenhuma pode sumir sem linha. -->

### Retornos abertos
<!-- Riscos que exigem mudança de spec ou de contrato: ID do retorno à fase 11 e o que precisa mudar. -->

## Anti-padrões
- Registrar risco alto com mitigação "será tratado no próximo ciclo". Isso não é mitigação nem aceite, e o gate fica aberto sem ninguém perceber.
- Aceitar risco em nome de um time ou de um cargo. Ninguém responde por ele quando o incidente acontece.
- Rebaixar a severidade para fechar o gate no prazo. O risco continua o mesmo e some do radar de quem responde por ele.

## Modo reverso
Levante riscos a partir do código em produção: autenticação, autorização por rota, validação de entrada, upload, dependências e segredos em configuração.
Some a isso o histórico real: incidentes passados, alertas recorrentes e achados de scanner já existentes.
Risco já conhecido e tolerado precisa de aceite retroativo com nome e data de hoje, nunca com data inventada.
Quando não dá para saber se um comportamento é proteção intencional ou brecha, vira `open_question` no STATE.md, nunca risco descartado por suposição.
