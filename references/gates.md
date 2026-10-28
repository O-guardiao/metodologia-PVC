# Referência: gates

Extrato PVC v1.0, seções 13, 28. [Proveniência](../docs/PROVENIENCIA.md).

O pacote usa §§13.3/28 conforme [ADR-0001](../docs/adr/0001-gates.md).

# 13. Padrão 9 — Stage-Gate / Phase-Gate

## 13.1 Objetivo

Stage-Gate divide um projeto em fases e coloca portões formais de decisão entre elas.

Em cada gate, decide-se:

- continuar;
- corrigir;
- pausar;
- pivotar;
- matar o projeto.

## 13.2 Por que serve para IA

Agentes de IA tendem a continuar produzindo. Eles raramente param sozinhos para perguntar:

> A base está sólida o suficiente para continuar?

Stage-Gate força pausas de qualidade.

## 13.3 Gates do PVC

| Gate | Nome | Objetivo | Decisão |
|---|---|---|---|
| G0 | Intenção | Definir problema e valor | Continuar ou matar |
| G1 | Operação | Aprovar ConOps | Continuar/corrigir |
| G2 | Requisitos | Aprovar requisitos e critérios | Continuar/corrigir |
| G3 | Interfaces | Aprovar contratos e dependências | Continuar/corrigir |
| G4 | Riscos | Aprovar FMEA inicial | Continuar/corrigir |
| G5 | Implementação vertical | Construir menor fluxo ponta a ponta | Continuar/corrigir |
| G6 | Integração | Remover ou registrar mocks | Continuar/corrigir |
| G7 | Verificação | Testes e evidências | Continuar/corrigir |
| G8 | Comissionamento | Aceite operacional | Aprovar/reprovar |
| G9 | Handoff | Operação e continuidade | Liberar/segurar |

## 13.4 Regra PVC

> Nenhum gate é “reunião”. Gate é decisão baseada em evidência.

## 13.5 Critérios de decisão

Para cada gate, use:

```text
GO: pode avançar.
GO COM RESTRIÇÕES: pode avançar, mas pendências estão registradas.
NO-GO: não pode avançar.
KILL: projeto deve ser encerrado ou recomeçado.
```

---

# 28. Checklists por gate

## G0 — Intenção

- [ ] Problema claro.
- [ ] Usuário definido.
- [ ] Resultado esperado definido.
- [ ] Métrica de sucesso definida.
- [ ] Fora de escopo definido.

Decisão:

```text
GO / GO COM RESTRIÇÕES / NO-GO / KILL
```

## G1 — ConOps

- [ ] Fluxo nominal descrito.
- [ ] Fluxos de erro descritos.
- [ ] Ambiente operacional descrito.
- [ ] Usuários e papéis descritos.
- [ ] Critérios de sucesso operacional definidos.

## G2 — Requisitos

- [ ] Cada requisito tem ID.
- [ ] Cada requisito tem critério de aceite.
- [ ] Cada requisito tem método de verificação.
- [ ] Requisitos não verificáveis foram removidos ou reescritos.

## G3 — Interfaces

- [ ] Entradas definidas.
- [ ] Saídas definidas.
- [ ] Erros definidos.
- [ ] Autenticação definida.
- [ ] Dependências listadas.
- [ ] Mocks declarados.

## G4 — Riscos

- [ ] FMEA criada.
- [ ] Falhas críticas identificadas.
- [ ] Mitigações definidas.
- [ ] Riscos aceitos explicitamente.

## G5 — Implementação vertical

- [ ] WBS por fluxo criada.
- [ ] Tarefas pequenas.
- [ ] Escopo restrito.
- [ ] Branch ou versão separada.

## G6 — Integração

- [ ] Serviços sobem juntos.
- [ ] Banco conecta.
- [ ] Endpoints respondem.
- [ ] Mocks removidos ou registrados.
- [ ] Logs aparecem.

## G7 — Verificação

- [ ] Testes executados.
- [ ] Fluxo feliz aprovado.
- [ ] Fluxo de erro aprovado.
- [ ] Evidências salvas.
- [ ] Requisitos rastreados.

## G8 — Comissionamento

- [ ] Relatório preenchido.
- [ ] Ambiente informado.
- [ ] Versão/commit informado.
- [ ] Falhas registradas.
- [ ] Decisão formal tomada.

## G9 — Handoff

- [ ] Instalação documentada.
- [ ] Operação documentada.
- [ ] Teste documentado.
- [ ] Backup documentado.
- [ ] Rollback documentado.
- [ ] Pendências explícitas.

---
