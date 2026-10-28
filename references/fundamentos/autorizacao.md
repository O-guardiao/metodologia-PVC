# Fronteira de confiança e autorização

**Definição.** Autenticação identifica o ator; autorização decide se ele pode
executar determinada ação sobre um recurso. O cliente não é autoridade para preço,
papel, proprietário ou tenant: a decisão deve ser aplicada na fronteira confiável.

**Risco.** Esconder um botão deixa APIs acessíveis. Aceitar IDs/papéis enviados
pelo cliente pode permitir acesso cruzado ou alteração indevida.

**Decisão prática.** Defina matriz ator × ação × recurso × tenant. Valide entrada
e calcule regras sensíveis no servidor; derive identidade de contexto autenticado.
Aplique menor privilégio e negação quando não há concessão prevista.
[OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

**Prova mínima.** Chame a fronteira sem UI: anônimo, autorizado, papel insuficiente
e outro tenant. Altere identificadores e campos sensíveis. Confira dados retornados
e ausência de alteração indevida, além do status. Teste usando papéis reais da aplicação.

**Limites.** USING(true) isolado não demonstra vulnerabilidade: acesso público
intencional depende da operação, papel e política completa. Examine também
WITH CHECK, privilégios e bypass de proprietário/superusuário. auth.uid() não é
o único modelo válido; use a identidade e política do sistema.
RLS controla linhas e não protege automaticamente campos sensíveis; confira
privilégios de coluna, projeção de saída e testes com papéis restritos.
[Políticas de linha PostgreSQL](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).
