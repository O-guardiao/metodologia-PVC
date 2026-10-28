# Fundamentos de programação: gatilhos

Em execução e verificação, identifique quais invariantes a mudança pode afetar.
Leia apenas as referências cujos gatilhos se aplicam; registre critério e prova
no requisito/relatório do projeto.

| Gatilho | Tema para route --topic | Referência |
|---|---|---|
| Escritas simultâneas, saldo, estoque, reserva ou edição concorrente | concorrencia | [Concorrência](fundamentos/concorrencia.md) |
| Retry, webhook, fila, comando repetido ou efeito externo incerto | idempotencia | [Idempotência](fundamentos/idempotencia.md) |
| Entrada do cliente, identidade, permissões ou isolamento entre tenants | autorizacao | [Fronteira de confiança](fundamentos/autorizacao.md) |
| Regra de negócio presa à tela, ao transporte ou ao banco | responsabilidades | [Responsabilidades](fundamentos/responsabilidades.md) |
| Contrato entre módulos, persistência, serviço ou política de acesso | testes-integracao | [Testes de integração](fundamentos/testes-integracao.md) |

Exemplo: route executar --topic idempotencia seleciona uma referência, não as cinco.
Fundamentos são critérios de raciocínio e prova; não exigem um framework,
arquitetura fixa ou número arbitrário de testes.
