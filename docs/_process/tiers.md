# Tiers

O tier define quais fases sao obrigatorias. Fase nao obrigatoria para o tier
nao aparece no painel da area e nao e exigida por `gate-check`.

| Tier | Descricao | Fases obrigatorias |
|---|---|---|
| 1 | Ajuste: correcao, regra simples, mudanca sem nova tela | 01, 13, 14, 17 |
| 2 | Feature: nova rota ou capacidade em produto existente com usuario conhecido | 01, 02, 05, 07, 08, 11, 12, 13, 14, 15, 16, 17 |
| 3 | Produto novo ou usuario desconhecido | todas as 20 |

## Onde o tier e declarado

Em dois lugares, que precisam concordar: o campo `tier` em `docs/STATE.md` e o
campo `Tier` no cabecalho do README da area.

## Mudanca de tier

O tier pode subir a qualquer momento, sem cerimonia: subir significa exigir
mais fases, e exigir mais nunca e um risco.

O tier nao pode descer sem uma decisao registrada em
`docs/_context/decisions.log` com status `DECIDED`. Descer o tier apaga gates
obrigatorios, entao e exatamente o tipo de atalho que o kit existe para
impedir.

## Como escolher

Na duvida entre dois tiers, escolha o maior. O custo de uma fase a mais e uma
pagina de documento. O custo de uma fase a menos e descobrir em producao.

Perguntas que resolvem a maioria dos casos:

- A mudanca cria tela nova ou rota nova? Tier 2 no minimo.
- O usuario final e conhecido e ja usa o produto? Se nao, tier 3.
- A mudanca e reversivel com feature flag em minutos? Se nao, tier 3.
