# Provas

Scripts que geram, do zero, cada bloco da secao "Prova de funcionamento" do
README. Cada um recria o alvo do zero e escreve a saida no stdout.

## Fluxo completo

```sh
mkdir -p proofs/out
proofs/modo-a-claude-code.sh /tmp/prova-a   > proofs/out/prova-a.out
proofs/modo-b-codex.sh       /tmp/prova-b   > proofs/out/prova-b.out
proofs/adapters-none.sh      /tmp/prova-none > proofs/out/prova-none.out
proofs/encadeamento.sh       /tmp/prova-chain > proofs/out/encadeamento.out
proofs/modo-c-update.sh      /tmp/prova-b 1.1.0 > proofs/out/prova-c.out
proofs/varredura.sh                          > proofs/out/varredura.out
python3 -m unittest discover bin/tests       > proofs/out/testes.out 2>&1
```

Depois monte a secao no README:

```sh
python3 proofs/build-readme.py proofs/out
```

`build-readme.py` tambem precisa de tres arquivos que descrevem a estrutura:
`arvore-kit.out`, `arvore-all.txt`, `arvore-alvo.out`, e de `readme-topo.md`,
que e tudo o que vem antes da secao "Estrutura" no README atual. Ele avisa qual
esta faltando em vez de gerar um README pela metade.

## Ordem e efeitos colaterais

`modo-c-update.sh` precisa de um alvo ja instalado, entao roda depois do modo
B. Ele monta a versao nova numa copia temporaria do kit, nunca no kit real:
uma prova que suja o repositorio que ela mesma testa nao e reproduzivel. Passe
uma versao ainda nao usada no segundo argumento.

`varredura.sh` le `git ls-files`, entao arquivos novos precisam estar ao menos
em staging para serem varridos.

Os scripts assumem o kit em `/home/user/product-lifecycle-kit`. Ajuste a
variavel `KIT` no topo de cada um, ou exporte `KIT=/caminho/do/kit`, se o seu
clone estiver em outro lugar.

## Por que a fence dos blocos tem quatro crases

As saidas contem blocos de tres crases: o `session-open` imprime o
`docs/STATE.md`, que e um bloco yaml. Uma fence externa de tres crases seria
fechada por eles no meio do caminho, e metade do README passaria a renderizar
como markdown solto.
