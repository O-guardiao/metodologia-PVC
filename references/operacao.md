# Referência: operacao

Extrato PVC v1.0, seções 6, 8, 14. [Proveniência](../docs/PROVENIENCIA.md).

# 6. Padrão 2 — SDD: Spec-Driven Development

## 6.1 Objetivo

Spec-Driven Development é uma abordagem em que a especificação orienta o desenvolvimento.

Em vez de começar pelo código, começa-se por:

- o que precisa ser feito;
- por que precisa ser feito;
- quais são as regras;
- quais são as entradas e saídas;
- quais são os critérios de aceite;
- quais são as restrições.

## 6.2 Por que SDD é importante com IA

Agentes de IA são bons em gerar implementação a partir de contexto. Se o contexto é ruim, a implementação tende a ser instável.

SDD reduz:

- ambiguidade;
- invenção da IA;
- drift de escopo;
- decisões implícitas;
- retrabalho;
- código sem critério de aceite.

## 6.3 Três níveis de SDD

### Nível 1 — Spec-first

A especificação é escrita antes da implementação.

Uso:

- tarefas pequenas;
- features específicas;
- ajustes pontuais.

### Nível 2 — Spec-anchored

A especificação continua existindo depois da implementação e serve como âncora para manutenção.

Uso:

- projetos médios;
- sistemas que evoluem;
- projetos solo com IA.

### Nível 3 — Spec-as-source

A especificação vira a fonte principal do sistema. O humano altera a spec, e agentes atualizam implementação.

Uso:

- projetos muito bem disciplinados;
- produtos com automação pesada;
- equipes com processo maduro.

Para seu caso, comece com **spec-anchored**. Spec-as-source é poderoso, mas perigoso se você ainda não tem disciplina de testes e rastreabilidade.

## 6.4 Artefatos do SDD

- `SPEC.md`
- `PLAN.md`
- `TASKS.md`
- `REQUIREMENTS_MATRIX.md`
- `ACCEPTANCE_CRITERIA.md`
- `TEST_PLAN.md`

## 6.5 Processo SDD mínimo

```text
1. Especificar o problema
2. Especificar usuários e contexto
3. Especificar requisitos
4. Especificar entradas e saídas
5. Especificar restrições
6. Especificar critérios de aceite
7. Planejar arquitetura
8. Quebrar em tarefas
9. Implementar
10. Testar contra a especificação
11. Atualizar documentação
```

## 6.6 Regra para IA

> Nenhuma implementação sem especificação mínima.

## 6.7 Prompt padrão

```text
Você é um engenheiro de requisitos.
Antes de implementar qualquer código, leia a intenção abaixo e produza uma especificação objetiva.
Inclua: objetivo, não-objetivos, usuários, fluxo principal, fluxos de erro, requisitos funcionais, requisitos não funcionais, restrições, critérios de aceite e dúvidas críticas.
Não implemente código nesta etapa.
```

---

# 8. Padrão 4 — ConOps: Concept of Operations

## 8.1 Objetivo

ConOps descreve como o sistema será usado no mundo real antes de decidir como será implementado.

Ele responde:

- quem opera?
- onde opera?
- quando opera?
- com quais entradas?
- quais saídas?
- quais falhas são aceitáveis?
- quais falhas são críticas?
- qual é o ambiente operacional?

## 8.2 Por que ConOps é útil com IA

A IA tende a implementar a solução mais óbvia a partir do prompt. ConOps força o sistema a ser pensado pela operação, não pela interface.

Sem ConOps, a IA pode criar algo bonito, mas desconectado do uso real.

## 8.3 Estrutura de ConOps

```markdown
# CONOPS.md

## 1. Missão do sistema

## 2. Usuários e papéis

## 3. Ambiente operacional

## 4. Fluxo nominal

## 5. Fluxos alternativos

## 6. Fluxos de falha

## 7. Limites do sistema

## 8. Dependências externas

## 9. Restrições legais, técnicas e comerciais

## 10. Critérios de sucesso operacional

## 11. Critérios de falha inaceitável
```

## 8.4 Exemplo aplicado

Sistema: agente de cobrança para microempresa.

Fluxo nominal:

```text
Cliente atrasa pagamento → sistema identifica atraso → gera mensagem → humano aprova → mensagem é enviada → resposta é registrada → status é atualizado.
```

Fluxo de falha:

```text
API do WhatsApp cai → sistema não tenta enviar infinitamente → registra falha → notifica humano → mantém fila para retry controlado.
```

## 8.5 Regra PVC

> Nenhum projeto começa pelo código. Começa pela operação.

---

# 14. Padrão 10 — WBS: Work Breakdown Structure

## 14.1 Objetivo

WBS decompõe o escopo em entregáveis menores.

Não é uma lista de tarefas aleatórias. É uma árvore de entregáveis.

## 14.2 Por que serve para IA

A IA costuma transformar uma ideia grande em tarefas genéricas demais.

WBS força decomposição por produto/entrega.

## 14.3 WBS ruim

```text
- fazer backend
- fazer frontend
- fazer banco
- testar
```

## 14.4 WBS boa

```text
1. Fluxo de criação de tarefa
  1.1 Contrato POST /tasks
  1.2 Validação de payload
  1.3 Persistência no banco
  1.4 Resposta padronizada
  1.5 Log de criação
  1.6 Teste de payload válido
  1.7 Teste de payload inválido
  1.8 Evidência no commissioning report
```

## 14.5 Regra PVC

> Quebre por fluxo operacional, não por camada técnica isolada.

## 14.6 Template de WBS

```markdown
# WBS.md

## 1. Fluxo principal
### 1.1 Entrada
### 1.2 Validação
### 1.3 Processamento
### 1.4 Persistência
### 1.5 Saída
### 1.6 Log
### 1.7 Teste
### 1.8 Evidência

## 2. Fluxo de erro
### 2.1 Erro de entrada
### 2.2 Erro de dependência externa
### 2.3 Erro de permissão
### 2.4 Erro interno
### 2.5 Retry ou fallback
```

---
