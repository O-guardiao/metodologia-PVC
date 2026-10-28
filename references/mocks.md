# Referência: mocks

Extrato PVC v1.0, seções 21. [Proveniência](../docs/PROVENIENCIA.md).

# 21. Padrão 17 — Registro de mocks, placeholders e dívidas técnicas

## 21.1 Objetivo

Evitar que simulação seja confundida com implementação real.

## 21.2 Tipos

### Mock

Simula dependência.

### Stub

Retorna resposta fixa.

### Fake

Implementação simplificada que parece real, mas não serve para produção.

### Placeholder

Espaço reservado para implementação futura.

### Dívida técnica

Escolha consciente que reduz qualidade agora e exige correção depois.

## 21.3 Registro obrigatório

```markdown
# MOCK_REGISTER.md

| ID | Local | Tipo | Motivo | Risco | Como remover | Gate limite | Status |
|---|---|---|---|---|---|---|---|
| M-001 | src/payment.ts | Mock | API real não configurada | Alto | Integrar sandbox | G6 | Aberto |
```

## 21.4 Regra PVC

> Mock não registrado é bug crítico de processo.

---
