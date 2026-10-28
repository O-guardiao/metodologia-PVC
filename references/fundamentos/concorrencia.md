# Concorrência e condições de corrida

**Definição.** Uma condição de corrida ocorre quando a ordem de operações
concorrentes pode violar uma regra. Exemplo: duas reservas leem uma vaga e ambas
confirmam. A invariante é reservas confirmadas ≤ capacidade.

**Risco.** Ler, verificar e gravar separadamente permite decisões sobre estado
que já mudou. Uma transação, isoladamente, não garante o isolamento necessário.

**Decisão prática.** Escreva a invariante e a fronteira atômica. Escolha restrição
de unicidade, atualização condicional, versão otimista, bloqueio ou isolamento
compatível com o banco. Confira conflitos/deadlocks e retentativa limitada.
[PostgreSQL: isolamento](https://www.postgresql.org/docs/current/transaction-iso.html)
e [bloqueios](https://www.postgresql.org/docs/current/explicit-locking.html).

**Prova mínima.** Controle o ponto de disputa com barreira/evento quando viável;
duas conexões tentam consumir a mesma capacidade. Confira resultados e estado
persistido, incluindo falha e rollback. Lançar Promise.all não prova que a
intercalação crítica ocorreu. [Barreiras em Python](https://docs.python.org/3/library/threading.html#barrier-objects).
Distinga a disputa pela última unidade de duas compras legítimas com estoque
suficiente: ambas devem poder concluir sem perda de atualização.

**Limites.** SELECT FOR UPDATE não é receita portátil nem solução para toda corrida.
SQLite serializa escritas e tem comportamento próprio; não oferece esse comando
como bloqueio de linha. Confira o banco e modo de journal usados no teste.
[Isolamento SQLite](https://www.sqlite.org/isolation.html).
