---
phase: 08-wireframes
area: PREENCHER-AREA
title: PREENCHER-TITULO
status: draft
owner: PREENCHER-OWNER
inputs: []
approved_by: null
approved_at: null
superseded_by: null
---

# Wireframes

## Propósito
Desenhar em baixa fidelidade as telas dos flows críticos e ligá-las por navegação.
Testar estrutura e sequência antes que cor, tipografia e componente entrem na conversa.

## Gate de saída
Os flows críticos são navegáveis de ponta a ponta em baixa fidelidade.
- [ ] Cada tela do inventário aponta para um flow e um passo da fase 07.
- [ ] Dá para percorrer cada flow crítico clicando, sem alguém explicando o caminho.
- [ ] Todo arquivo citado existe no caminho indicado e abre.
- [ ] Nenhuma tela usa cor de marca, imagem final ou texto fictício de enfeite.

## Esqueleto

### Onde os arquivos vivem
<!-- Wireframes ficam em `docs/areas/<area>/wireframes/`, um arquivo por tela, nome
     `W-NN-slug.<ext>`. O link do protótipo navegável vai aqui, uma linha, com data de
     atualização. Não serve "está no Figma do time" sem link direto. -->
- Pasta:
- Protótipo navegável:
- Última atualização:

### Inventário de telas
<!-- Uma linha por tela. Flow e passo vêm da fase 07, sem renomear. Tela que não
     serve nenhum passo sai do inventário ou o flow é corrigido na fase 07. -->

| ID | Tela | Flow (07) | Passo | Arquivo |
|---|---|---|---|---|
| W-01 | <tela> | F1 | 2 | W-01-slug.png |

### Por tela
<!-- Um bloco por tela do inventário. Só o que muda decisão. -->

#### W-NN <tela>
- Objetivo da tela: <o que a pessoa consegue fazer aqui, uma frase>
- Blocos de conteúdo: <lista em ordem de leitura, ex cabeçalho, filtro, lista, ação>
  <!-- Não serve "conteúdo principal". Diga qual conteúdo. -->
- Ação primária: <uma só, a que leva ao próximo passo do flow>
- Saídas: <para onde cada ação leva, usando IDs de tela>
- Estados previstos: <vazio, erro, carregando, quando existirem nesta tela>
  <!-- Aqui só listar. O desenho de cada estado é da fase 10. -->

### Convenções de baixa fidelidade
<!-- Cinza, caixa e placeholder. Texto real só nos rótulos que a pessoa precisa ler
     para decidir. Sem ícone final, sem foto, sem paleta. Não serve wireframe já
     pintado com a marca: ele desloca a discussão para estética. -->

## Anti-padrões
- Telas soltas sem ligação entre si. Ninguém consegue testar o flow, e o problema de sequência só aparece no código.
- Wireframe já com cor, fonte e ícone finais. O feedback vira debate de estética e a estrutura passa sem revisão.
- Texto de placeholder repetido no lugar de rótulo real de botão e coluna. Esconde ambiguidade de vocabulário que estoura na UI.

## Modo reverso
Capture as telas atuais e transforme cada uma em um bloco do inventário, ligada ao flow
e ao passo da fase 07. Use o print no lugar do wireframe e marque a linha como
"derivado do produto atual". Passo de flow sem tela hoje não vira desenho inventado:
abra `open_question` no STATE.md e deixe a linha do inventário sem arquivo.
