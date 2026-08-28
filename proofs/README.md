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
proofs/fase-para-codigo.sh   /tmp/prova-fase  > proofs/out/fase-para-codigo.out
proofs/modo-reverso.sh       /tmp/prova-reverso > proofs/out/modo-reverso.out
proofs/modo-c-update.sh      /tmp/prova-b 1.2.0 > proofs/out/prova-c.out
proofs/varredura.sh                          > proofs/out/varredura.out
```

Duas saidas nao vem dos scripts acima. Os testes:

```sh
{ printf '$ python3 -m unittest discover bin/tests\n'
  python3 -m unittest discover bin/tests 2>&1
  printf 'EXIT: %d\n' "$?"; } > proofs/out/testes.out
```

E as tres arvores da secao "Estrutura", que `arvores.sh` gera de uma vez. Ele
precisa de um alvo instalado com `--adapters all`, que nenhum outro script
produz:

```sh
rm -rf /tmp/prova-all && mkdir -p /tmp/prova-all && git -C /tmp/prova-all init -q
./install.sh /tmp/prova-all --adapters all
proofs/arvores.sh /tmp/prova-all /tmp/prova-a
```

As tres tem formatos diferentes e o `build-readme.py` conta com isso: a do kit
e indentada, a do alvo recem instalado e plana sem `./` na frente, e a do modo
A e a saida crua de `find`. Rode `arvores.sh` com tudo ja em staging: a arvore
do kit sai de `git ls-files`, entao arquivo novo fora do index nao aparece.

`readme-topo.md` e tudo o que vem antes da secao "Estrutura" no README atual.

Depois monte a secao no README:

```sh
python3 proofs/build-readme.py proofs/out
```

Ele avisa qual arquivo esta faltando em vez de gerar um README pela metade, e
escreve sempre no `README.md` da raiz do kit, independente de onde voce o
chamou.

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
