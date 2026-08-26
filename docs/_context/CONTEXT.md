# CONTEXT

O que e verdade neste projeto. Muda apenas por decisao registrada em
`_context/decisions.log`. Este arquivo e protegido: `guard-write` e
`guard-commit` recusam alteracao sem decisao `DECIDED` correspondente.

## Projeto

<!-- Uma frase: o que este produto faz e para quem. Sem adjetivo. -->

## Glossario

<!-- Termo canonico e definicao. Um termo por linha. O nome que aparece aqui e
     o nome que aparece no codigo, na UI e nos documentos. Divergencia entre
     glossario e codigo e bug de produto, nao questao de estilo. -->

| Termo | Definicao | Nao confundir com |
|---|---|---|

## Termos proibidos

<!-- Lido por gate-check, codigo VC-01. Um termo por item de lista. Aceita
     "- termo" e "- termo: motivo". Termo entre crases e tratado como
     literal. VC-01 procura cada termo em docs/, src/, app/ e packages/, sem
     diferenciar maiusculas, e falha se encontrar. Esta secao nao e varrida
     contra si mesma.

     Use para matar sinonimo que ja causou confusao: se o glossario diz
     "assinante", "usuario premium" nao pode sobreviver no codigo. -->

## Regras de negocio invariantes

<!-- Regra que o produto nao pode violar, com a origem (contrato, lei,
     decisao registrada). Se a origem for "alguem falou", nao e invariante,
     e suposicao: vire open_question no STATE.md. -->

## Restricoes tecnicas

<!-- Limite que nenhuma fase pode ignorar: stack imposta, integracao
     obrigatoria, janela de manutencao, requisito de compliance. -->

## Metricas canonicas

<!-- Como cada metrica citada nos PRDs e calculada. Duas definicoes da mesma
     metrica e a forma mais comum de duas equipes discordarem por meses. -->
