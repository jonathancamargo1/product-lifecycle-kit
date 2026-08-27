---
phase: 11-spec
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Spec técnica

## Propósito
Fixar como o sistema será construído: dados, contratos, integrações, segurança e observabilidade.
Existe para que um dev estime e implemente sem abrir uma rodada de perguntas.

## Gate de saída
Modelo de dados, APIs, integrações, segurança e observabilidade descritos, threat model inicial feito, e um dev estima sem perguntar nada.
- [ ] Toda entidade tem campos, tipos, obrigatoriedade e regra de unicidade escritos.
- [ ] Todo endpoint tem método, path, request, response de sucesso e lista de erros.
- [ ] Cada log, métrica e alerta tem nome e condição de disparo definidos.
- [ ] Um dev que não escreveu a spec leu e estimou sem abrir `open_question` nova.

## Esqueleto

### Escopo
<!-- Liste comportamentos dentro e fora. Não serve "MVP do módulo X". Serve lista de comportamentos nomeados. -->

### Modelo de dados
<!-- Uma subseção por entidade: campo, tipo, nulo, default, unicidade, relação. Não serve diagrama sem campos. -->

### Contratos de API
<!-- Por endpoint: método, path, auth exigida, request, response, erros com código. Não serve "CRUD padrão". -->

### Integrações
<!-- Por sistema externo: o que chamamos, quando, timeout, retry, comportamento quando ele está fora do ar. Não serve só o nome do fornecedor. -->

### Segurança
<!-- Papéis x operações permitidas, dado sensível e onde ele fica, o que é criptografado em trânsito e em repouso. Não serve "usa autenticação". -->

### Observabilidade
<!-- Três listas separadas. O que loga: evento e campos. O que mede: métrica e unidade. Qual alerta: condição, severidade, quem recebe. Não serve "vamos monitorar". -->

### Threat model inicial
<!-- Por ativo: quem ataca, por qual caminho, impacto, mitigação prevista aqui. Ameaça sem mitigação entra como item de entrada da fase 15, não some. -->

### Decisões técnicas
<!-- Cada escolha não óbvia com a alternativa descartada e o motivo. Se for irreversível, abra ADR e cite o número. -->

### Estimativa
<!-- Nome do dev que estimou, data, tamanho por slice. Sem nome e data o gate não fecha. -->

## Anti-padrões
- Escrever "conforme o padrão do time" no lugar do contrato. Quem estima não sabe qual padrão e volta com pergunta.
- Deixar campo sem tipo e sem regra de nulo. A ambiguidade vira migration errada e retrabalho na fase 13.
- Marcar risco de segurança como "resolver depois" sem virar item da fase 15. O risco sai do processo em vez de ser aceito por alguém.

## Modo reverso
Extraia o modelo de dados das migrations ou da introspecção do banco, os contratos das rotas do código, as integrações dos clients HTTP e das variáveis de ambiente.
Observabilidade sai da configuração de logs, dos dashboards e das regras de alerta já ativas.
Threat model se monta lendo o middleware de auth, a tabela de permissões e os pontos onde dado sensível é persistido.
O que não existir no código nem em documento vira `open_question` no STATE.md, nunca suposição sobre a intenção original.
