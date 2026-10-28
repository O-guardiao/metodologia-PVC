# Referência: contratos

Ao criar ou alterar uma interface, registre tipo, entrada, saída de sucesso,
erros/códigos, autenticação/autorização, dependências, logs e permissão/remoção de
mock (PVC §27.4). Use exemplos concretos de payload e testes de consumidor.
Inclua o arquivo do contrato nos inputs do fornecedor e declare seus consumidores
no estado. Uma inspeção do grafo não substitui busca por chamadas no código.

Extrato PVC v1.0, seções 9, 19, 20. [Proveniência](../docs/PROVENIENCIA.md).

# 9. Padrão 5 — Engenharia de Sistemas

## 9.1 Objetivo

Engenharia de sistemas é a disciplina de pensar o sistema inteiro: partes, interfaces, requisitos, integração, teste, operação e ciclo de vida.

Ela é útil quando o problema não é só “criar uma peça”, mas garantir que várias peças funcionem juntas.

## 9.2 Por que serve para vibecoding

Vibecoding com IA gera partes rápido. O risco é que as partes não formem um sistema coerente.

Engenharia de sistemas força perguntas como:

- quais são os subsistemas?
- como eles se comunicam?
- quais são os requisitos de cada subsistema?
- quais são as interfaces?
- como verificar cada parte?
- como validar o sistema inteiro?

## 9.3 Componentes principais

- necessidade operacional;
- requisitos;
- arquitetura;
- interfaces;
- integração;
- verificação;
- validação;
- operação;
- manutenção;
- descarte/evolução.

## 9.4 Aplicação em projeto com IA

Exemplo: agente de atendimento.

Subsistemas:

```text
1. Entrada de mensagem
2. Classificação de intenção
3. Recuperação de contexto
4. Geração de resposta
5. Aprovação humana
6. Envio
7. Log
8. Métricas
9. Escalonamento para humano
```

A IA pode implementar cada parte, mas você precisa controlar o sistema.

## 9.5 Checklist

- [ ] O sistema foi dividido em subsistemas?
- [ ] Cada subsistema tem responsabilidade clara?
- [ ] Cada interface está documentada?
- [ ] Cada dependência externa está listada?
- [ ] Existe plano de integração?
- [ ] Existe plano de teste ponta a ponta?
- [ ] Existe plano de operação?

---

# 19. Padrão 15 — ADR: Architecture Decision Record

## 19.1 Objetivo

ADR registra decisões técnicas importantes.

Não é documentação longa. É memória de decisão.

## 19.2 Por que serve para IA

A IA pode mudar arquitetura sem perceber ou sugerir alternativas incompatíveis com decisões anteriores.

ADR fixa:

- o que foi decidido;
- por quê;
- alternativas consideradas;
- consequências;
- status.

## 19.3 Template

```markdown
# ADR-0001 — Título da decisão

## Status
Proposta / Aceita / Rejeitada / Substituída

## Contexto
Qual problema levou à decisão?

## Decisão
O que foi decidido?

## Alternativas consideradas
Quais opções foram avaliadas?

## Consequências
Quais impactos positivos e negativos?

## Data
AAAA-MM-DD
```

## 19.4 Regra PVC

> Mudança arquitetural sem ADR é mudança invisível.

---

# 20. Padrão 16 — Matriz de rastreabilidade

## 20.1 Objetivo

Rastreabilidade conecta necessidade, requisito, implementação, teste e evidência.

## 20.2 Por que serve para IA

Sem rastreabilidade, a IA pode:

- implementar coisa não pedida;
- esquecer requisito;
- criar feature órfã;
- remover comportamento importante;
- passar para outra tarefa sem concluir a anterior.

## 20.3 Estrutura mínima

| Necessidade | Requisito | Componente | Teste | Evidência | Status |
|---|---|---|---|---|---|
| Criar tarefa | R-001 | taskController | test_create_task | log + DB row | aprovado |

## 20.4 Regra PVC

> Se não é rastreável, não é controlável.

---
