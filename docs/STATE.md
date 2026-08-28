# STATE

Onde estamos. Muda toda sessao. Unico lugar, junto com o frontmatter dos
artefatos, onde status existe.

```yaml
project: null
tier: null                    # 1 | 2 | 3
import_mode: null             # reverse enquanto a importacao nao foi confirmada
current_phase: null
current_area: null
next_action: null             # uma frase imperativa
blocked_by: null              # slug de gate, id de decisao ou null
open_questions: []            # {id, question, raised_at, answered}
gates: {}                     # slug da fase: {status, evidence, by, date}
last_session: null            # path do ultimo handoff
session_counter: 0
session_open: false           # true entre session-open e session-close
session_agent: null           # codex | claude-code | human
```
