# Provas

Scripts que geram, do zero, cada bloco da secao "Prova de funcionamento" do
README. Rode um por vez, de qualquer diretorio. Cada um recria o alvo do zero.

```sh
proofs/modo-a-claude-code.sh /tmp/prova-a
proofs/modo-b-codex.sh       /tmp/prova-b
proofs/adapters-none.sh      /tmp/prova-none
proofs/modo-c-update.sh      /tmp/prova-b 1.1.0
proofs/varredura.sh
```

Ordem importa em dois pontos. `modo-c-update.sh` precisa de um alvo ja
instalado, entao roda depois do modo B. E ele altera o proprio kit: escreve a
nova versao em `VERSION`, em `bin/_kitlib.py` e no `CHANGELOG.md`, porque e
exatamente isso que a prova precisa demonstrar. Passe uma versao ainda nao
usada no segundo argumento.

Os scripts assumem o kit em `/home/user/product-lifecycle-kit`. Ajuste a
variavel `KIT` no topo de cada um se o seu clone estiver em outro lugar.
