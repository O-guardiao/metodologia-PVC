# Referência: maturidade

Extrato PVC v1.0, seções 11, 12. [Proveniência](../docs/PROVENIENCIA.md).

# 11. Padrão 7 — TRL: Technology Readiness Level

## 11.1 Objetivo

TRL mede maturidade tecnológica. A escala tradicional vai de 1 a 9, onde 1 é princípio inicial e 9 é tecnologia provada em ambiente operacional.

## 11.2 Por que serve para IA/vibecoding

A IA pode fazer algo parecer pronto quando ainda está em nível baixo de maturidade.

TRL obriga a perguntar:

> Isso é ideia, prova de conceito, protótipo integrado ou sistema operacional?

## 11.3 TRL adaptado ao PVC

| Nível | Nome | Descrição |
|---|---|---|
| TRL-PVC 1 | Ideia | Problema e hipótese descritos |
| TRL-PVC 2 | Conceito operacional | ConOps inicial criado |
| TRL-PVC 3 | Prova de conceito isolada | Um componente funciona isoladamente |
| TRL-PVC 4 | Componente validado localmente | Código local roda com dados controlados |
| TRL-PVC 5 | Integração simulada | Componentes conversam com mocks explícitos |
| TRL-PVC 6 | Protótipo integrado local/staging | Fluxo vertical integrado em ambiente controlado |
| TRL-PVC 7 | Operação controlada com dados reais | Funciona com dados reais limitados e supervisão |
| TRL-PVC 8 | Sistema comissionado | Testes, logs, rollback, docs e aceite completos |
| TRL-PVC 9 | Produção comprovada | Uso real recorrente, métricas e manutenção ativa |

## 11.4 Como usar

Cada módulo recebe um TRL-PVC.

Exemplo:

| Módulo | TRL-PVC | Observação |
|---|---:|---|
| Login | 7 | Funciona com dados reais controlados |
| Pagamento | 5 | Ainda usa sandbox/mock |
| Notificação | 6 | Integração em staging |
| Auditoria | 4 | Logs locais apenas |

## 11.5 Regra PVC

> O sistema inteiro não pode ser considerado mais maduro do que seu módulo crítico mais imaturo.

Se pagamento está em TRL-PVC 5, o produto de pagamento não está em TRL-PVC 8.

---

# 12. Padrão 8 — LOD: Level of Development / Level of Detail

## 12.1 Objetivo

LOD vem do BIM/construção para indicar o quanto um elemento de modelo pode ser usado e confiado.

Para IA, LOD ajuda a separar:

- ideia;
- placeholder;
- componente genérico;
- componente detalhado;
- componente integrado;
- componente validado.

## 12.2 O problema que resolve

Em vibecoding, a IA pode criar uma função chamada `processPayment()` que parece real, mas por dentro só retorna sucesso fixo.

Isso precisa ser rotulado como LOD baixo.

## 12.3 LOD adaptado para software com IA

| LOD-PVC | Estado | Pode confiar para quê? |
|---|---|---|
| LOD 100 | Conceitual | Entender intenção |
| LOD 200 | Placeholder/mock | Demonstração limitada |
| LOD 300 | Implementação real isolada | Teste local do componente |
| LOD 350 | Integrado com outros módulos | Teste de fluxo local/staging |
| LOD 400 | Pronto para operação controlada | Uso com supervisão |
| LOD 500 | As-built / validado em produção | Referência operacional real |

## 12.4 Exemplo

```text
Função: enviar cobrança por WhatsApp
LOD 100: ideia descrita
LOD 200: console.log simulando envio
LOD 300: chamada real à API sandbox
LOD 350: chamada real integrada ao CRM e banco
LOD 400: envio controlado com logs e retry
LOD 500: envio usado em produção, monitorado e documentado
```

## 12.5 Regra PVC

> Todo componente precisa declarar seu LOD.

## 12.6 Como registrar

```markdown
## Componentes e LOD

| Componente | LOD atual | LOD alvo | Bloqueio |
|---|---:|---:|---|
| paymentService | 200 | 400 | Falta API sandbox |
| taskRepository | 350 | 400 | Falta teste de rollback |
| notificationWorker | 300 | 400 | Falta retry e DLQ |
```

---
