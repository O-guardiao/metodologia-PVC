# Proveniência

Conteúdo da fonte PVC v1.0, consultada em 2026-10-28. Consulte [a política de origem](../../docs/PROVENIENCIA.md). Este arquivo é referência histórica, fora do carregamento padrão. A nomenclatura operacional de gates está no [ADR-0001](../../docs/adr/0001-gates.md).

# Metodologia PVC — Protótipo Vertical Comissionável

**Subtítulo:** Manual prático para transformar vibecoding, spec-driven development e agentes de IA em entrega limpa, rastreável e operável.

**Versão:** 1.0  
**Uso:** Projetos pessoais, automações, agentes de IA, IAaaS, micro-SaaS, sistemas internos, protótipos comerciais e produtos digitais.  
**Premissa:** IA pode acelerar implementação, mas não substitui escopo, verificação, integração, critérios de aceite, evidência e responsabilidade operacional.

---

## Sumário

1. [Diagnóstico do problema](#1-diagnóstico-do-problema)
2. [A tese central: sair do MVP puro para o PVC](#2-a-tese-central-sair-do-mvp-puro-para-o-pvc)
3. [Glossário essencial](#3-glossário-essencial)
4. [Mapa dos padrões usados](#4-mapa-dos-padrões-usados)
5. [Padrão 1 — MVP: Produto Mínimo Viável](#5-padrão-1--mvp-produto-mínimo-viável)
6. [Padrão 2 — SDD: Spec-Driven Development](#6-padrão-2--sdd-spec-driven-development)
7. [Padrão 3 — AGENTS.md e instruções persistentes para IA](#7-padrão-3--agentsmd-e-instruções-persistentes-para-ia)
8. [Padrão 4 — ConOps: Concept of Operations](#8-padrão-4--conops-concept-of-operations)
9. [Padrão 5 — Engenharia de Sistemas](#9-padrão-5--engenharia-de-sistemas)
10. [Padrão 6 — V-Model, verificação e validação](#10-padrão-6--v-model-verificação-e-validação)
11. [Padrão 7 — TRL: Technology Readiness Level](#11-padrão-7--trl-technology-readiness-level)
12. [Padrão 8 — LOD: Level of Development / Level of Detail](#12-padrão-8--lod-level-of-development--level-of-detail)
13. [Padrão 9 — Stage-Gate / Phase-Gate](#13-padrão-9--stage-gate--phase-gate)
14. [Padrão 10 — WBS: Work Breakdown Structure](#14-padrão-10--wbs-work-breakdown-structure)
15. [Padrão 11 — Definition of Done](#15-padrão-11--definition-of-done)
16. [Padrão 12 — FMEA: Failure Mode and Effects Analysis](#16-padrão-12--fmea-failure-mode-and-effects-analysis)
17. [Padrão 13 — Comissionamento](#17-padrão-13--comissionamento)
18. [Padrão 14 — Handoff operacional](#18-padrão-14--handoff-operacional)
19. [Padrão 15 — ADR: Architecture Decision Record](#19-padrão-15--adr-architecture-decision-record)
20. [Padrão 16 — Matriz de rastreabilidade](#20-padrão-16--matriz-de-rastreabilidade)
21. [Padrão 17 — Registro de mocks, placeholders e dívidas técnicas](#21-padrão-17--registro-de-mocks-placeholders-e-dívidas-técnicas)
22. [A metodologia combinada: PVC](#22-a-metodologia-combinada-pvc)
23. [Fluxo operacional completo](#23-fluxo-operacional-completo)
24. [Estrutura de pastas padrão](#24-estrutura-de-pastas-padrão)
25. [Papéis de agentes de IA dentro da metodologia](#25-papéis-de-agentes-de-ia-dentro-da-metodologia)
26. [Prompts reutilizáveis](#26-prompts-reutilizáveis)
27. [Templates copiáveis](#27-templates-copiáveis)
28. [Checklists por gate](#28-checklists-por-gate)
29. [Métricas de controle](#29-métricas-de-controle)
30. [Como adaptar por tipo de projeto](#30-como-adaptar-por-tipo-de-projeto)
31. [Erros comuns e antídotos](#31-erros-comuns-e-antídotos)
32. [Veredito e regra final](#32-veredito-e-regra-final)
33. [Fontes e referências](#33-fontes-e-referências)

---

# 1. Diagnóstico do problema

O problema não é que a IA não consiga gerar código. O problema é que a IA frequentemente gera **artefatos com aparência de conclusão**, mas sem maturidade operacional.

Em projetos feitos com vibecoding, é comum aparecer:

- fluxo visual funcionando apenas no caminho feliz;
- mock fingindo integração real;
- placeholder esquecido;
- código morto;
- dados simulados sem etiqueta;
- integração parcial;
- ausência de testes;
- ausência de log;
- ausência de rollback;
- ausência de documentação operacional;
- ausência de critério objetivo de aceite;
- ausência de rastreabilidade entre requisito, código e teste.

Isso cria um falso progresso: parece que o produto avançou, mas o núcleo operacional continua frágil.

**MVP é bom para validar demanda. Não é suficiente para garantir produto limpo.**

O método aqui proposto usa padrões de várias áreas para corrigir esse gap:

- engenharia de sistemas;
- construção civil;
- gestão de projetos;
- qualidade industrial;
- desenvolvimento ágil;
- comissionamento;
- documentação arquitetural;
- spec-driven development com IA.

---

# 2. A tese central: sair do MVP puro para o PVC

## 2.1 O que é MVP

MVP significa **Minimum Viable Product**, ou Produto Mínimo Viável. A lógica é criar a menor versão possível de um produto para validar uma hipótese com usuários reais.

MVP responde principalmente:

> Existe demanda real para isso?

Ele não responde necessariamente:

> O sistema está integrado, testado, auditável, seguro e operável?

## 2.2 O problema do MVP com IA

Para uma pessoa experiente, o MVP pode ser intencionalmente incompleto. Ela sabe onde estão os atalhos. Ela sabe que aquele mock será removido. Ela sabe que aquela integração ainda não é real.

Para vibecoding com IA, isso vira risco porque:

1. A IA pode continuar construindo em cima de um mock.
2. O usuário pode esquecer que algo era provisório.
3. O projeto cresce sem arquitetura clara.
4. A documentação não acompanha a realidade.
5. O protótipo fica bonito, mas não confiável.

## 2.3 O que é PVC

**PVC significa Protótipo Vertical Comissionável.**

Definição:

> Um recorte pequeno do produto que executa um fluxo real de ponta a ponta, com integrações reais ou mocks explicitamente registrados, testes, logs, documentação, rollback e critérios objetivos de aceite.

O PVC não tenta construir o produto inteiro. Ele tenta construir **um fluxo completo, verificável e operável**.

## 2.4 Diferença entre MVP e PVC

| Critério | MVP | PVC |
|---|---|---|
| Objetivo principal | Validar demanda | Validar operação |
| Pergunta central | Alguém quer isso? | Isso funciona de ponta a ponta? |
| Tolerância a mock | Alta | Baixa e explícita |
| Tolerância a placeholder | Alta | Só com registro e prazo |
| Foco | Mercado e aprendizado | Sistema, integração e entrega |
| Risco | Protótipo virar gambiarra | Mais lento no começo |
| Entrega | Demonstrável | Operável |
| Critério de sucesso | Interesse do usuário | Evidência de funcionamento |

## 2.5 Regra central do PVC

> Pequeno pode. Simulado pode temporariamente. Incompleto oculto não pode.

---

# 3. Glossário essencial

## Artefato

Documento, código, teste, log, decisão, checklist ou evidência produzida durante o projeto.

## Critério de aceite

Condição objetiva que define quando uma entrega pode ser aceita.

Exemplo ruim:

> Login funcionando.

Exemplo bom:

> Dado um usuário cadastrado, quando ele envia e-mail e senha válidos para `POST /login`, então o sistema retorna token válido, registra log de autenticação e rejeita senha inválida com erro 401.

## Fluxo vertical

Caminho completo de ponta a ponta atravessando interface, backend, banco, integração, log e resposta ao usuário.

Exemplo:

> Cliente envia pedido → sistema valida → salva no banco → calcula valor → envia notificação → registra log → retorna status.

## Mock

Simulação temporária de uma dependência real.

Exemplo:

- simular API de pagamento;
- simular resposta de IA;
- simular envio de e-mail;
- simular banco de dados com arquivo local.

## Placeholder

Marcador provisório deixado para implementação futura.

Exemplo:

```js
// TODO: implementar pagamento real depois
```

## Comissionamento

Processo de verificar, testar, documentar e aceitar que um sistema está funcionando de acordo com requisitos definidos.

## Handoff

Transferência organizada do projeto para operação, manutenção ou continuação por outra pessoa/agente.

## Gate

Ponto formal de decisão: continuar, corrigir, pausar ou matar o projeto.

## Rastreabilidade

Capacidade de ligar uma necessidade original a requisitos, decisões, código, testes e evidências.

---

# 4. Mapa dos padrões usados

| Padrão | Origem | Função dentro do PVC |
|---|---|---|
| MVP | Startup / produto | Validar demanda, não acabamento |
| SDD | Engenharia de software com IA | Fazer especificação antes do código |
| AGENTS.md | Agentes de código | Manter instruções persistentes do projeto |
| ConOps | Engenharia de sistemas | Descrever operação real antes da solução |
| Engenharia de Sistemas | Aeroespacial/industrial | Integrar partes em sistema coerente |
| V-Model / V&V | Sistemas críticos | Ligar requisito a teste e aceite |
| TRL | NASA / tecnologia | Medir maturidade do sistema |
| LOD | BIM / construção | Separar placeholder de implementação confiável |
| Stage-Gate | Gestão de produto/projeto | Controlar avanço por decisões formais |
| WBS | Gestão de projetos | Decompor escopo em entregáveis |
| Definition of Done | Scrum / Agile | Definir qualidade mínima da entrega |
| FMEA | Qualidade industrial | Antecipar falhas e riscos |
| Comissionamento | Construção/indústria | Provar que funciona em ambiente previsto |
| Handoff | Operações/projetos | Transferir conhecimento operacional |
| ADR | Arquitetura de software | Registrar decisões técnicas |
| Matriz de rastreabilidade | Sistemas/qualidade | Conectar requisito → código → teste → evidência |
| Registro de mocks | Adaptação PVC | Impedir simulação oculta |

---

# 5. Padrão 1 — MVP: Produto Mínimo Viável

## 5.1 Origem e objetivo

O MVP é usado em produto, startups e inovação para validar hipóteses com o menor investimento possível.

O MVP é útil quando a dúvida principal é:

- há demanda?
- o usuário entende o valor?
- alguém pagaria?
- a dor é real?
- a proposta é desejável?

## 5.2 Como funciona

1. Definir uma hipótese.
2. Criar a menor entrega possível para testá-la.
3. Expor a usuários reais.
4. Medir comportamento.
5. Aprender.
6. Decidir se continua, muda ou abandona.

## 5.3 Onde o MVP falha com IA

MVP falha quando é usado para responder perguntas técnicas que ele não foi feito para responder.

Ele não garante:

- arquitetura saudável;
- integração real;
- teste;
- segurança;
- manutenção;
- continuidade;
- operabilidade.

## 5.4 Como usar MVP dentro do PVC

Use MVP apenas para validar mercado e proposta de valor.

Depois que a ideia mostrar sinal de valor, passe para PVC.

Modelo:

```text
MVP valida demanda.
PVC valida operação.
```

## 5.5 Checklist de uso correto

- [ ] A hipótese de mercado está clara?
- [ ] O experimento é barato?
- [ ] O usuário real será exposto ao fluxo?
- [ ] A métrica de aprendizado está definida?
- [ ] Está explícito que MVP não significa sistema pronto?

---

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

# 7. Padrão 3 — AGENTS.md e instruções persistentes para IA

## 7.1 Objetivo

`AGENTS.md` é um arquivo de instruções persistentes para agentes de IA que trabalham no projeto.

Ele funciona como um “manual de comportamento” para o agente.

## 7.2 Por que isso importa

Sem instruções persistentes, a IA esquece padrões entre sessões, branches ou tarefas.

`AGENTS.md` ajuda a fixar:

- comandos de instalação;
- comandos de teste;
- estilo de código;
- estrutura de pastas;
- regras de segurança;
- proibições;
- critérios mínimos de entrega;
- processo de revisão.

## 7.3 O que colocar no AGENTS.md

- Visão do projeto.
- Como instalar dependências.
- Como rodar localmente.
- Como testar.
- Onde ficam documentos.
- Como registrar decisões.
- Como registrar mocks.
- O que a IA nunca pode fazer.
- Definition of Done.
- Processo de commit/branch.

## 7.4 Exemplo

```markdown
# AGENTS.md

## Missão
Este projeto segue a metodologia PVC: Protótipo Vertical Comissionável.
O objetivo não é gerar código rapidamente; é entregar fluxos pequenos, reais, testados e operáveis.

## Regras obrigatórias
- Não criar mock sem registrar em `docs/MOCK_REGISTER.md`.
- Não alterar arquitetura sem ADR em `docs/adr/`.
- Não considerar tarefa concluída sem teste ou evidência.
- Não remover logs de auditoria.
- Não expor secrets em código, README, logs ou exemplos.
- Não criar endpoints sem documentar contrato em `docs/INTERFACES.md`.

## Comandos
- Instalar: `npm install` ou `pip install -r requirements.txt`
- Rodar local: `docker compose up --build`
- Testar: `npm test` ou `pytest`
- Ver logs: `docker compose logs -f`

## Definition of Done
Uma tarefa só é concluída se:
- requisito vinculado;
- código implementado;
- teste executado;
- mock registrado ou removido;
- documentação atualizada;
- evidência registrada no relatório de comissionamento.
```

## 7.5 Erro comum

Usar `AGENTS.md` como texto genérico motivacional.

Errado:

```text
Seja cuidadoso e faça código limpo.
```

Certo:

```text
Antes de abrir PR, rode `pytest`. Se falhar, não marque a tarefa como concluída.
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

# 10. Padrão 6 — V-Model, verificação e validação

## 10.1 Objetivo

O V-Model liga cada etapa de definição a uma etapa correspondente de teste.

Forma simplificada:

```text
Necessidade do usuário          ↔ Validação operacional
Requisitos do sistema           ↔ Teste de sistema
Arquitetura                     ↔ Teste de integração
Design de componente            ↔ Teste de componente
Implementação                   ↔ Teste unitário
```

## 10.2 Verificação vs validação

## Verificação

Pergunta:

> Estamos construindo corretamente?

Exemplo:

- o endpoint retorna o formato esperado?
- o banco salva o registro?
- o teste passa?
- o webhook rejeita payload inválido?

## Validação

Pergunta:

> Estamos construindo a coisa certa?

Exemplo:

- esse fluxo resolve o problema real do usuário?
- o operador consegue usar?
- o resultado tem valor prático?
- o sistema funciona no ambiente real?

## 10.3 Métodos de verificação

- Teste: executar e medir resultado.
- Inspeção: revisar código, tela, contrato, log ou documento.
- Análise: avaliar por lógica, cálculo, comparação ou revisão técnica.
- Demonstração: mostrar o fluxo funcionando.

## 10.4 Aplicação PVC

Todo requisito precisa ter método de verificação.

Exemplo:

| ID | Requisito | Método | Evidência |
|---|---|---|---|
| R-001 | Criar tarefa via API | Teste | resposta 201 + registro no banco |
| R-002 | Rejeitar payload inválido | Teste | resposta 400 |
| R-003 | Registrar erro externo | Inspeção | log com correlation_id |
| R-004 | Usuário entende status | Demonstração | teste manual com operador |

## 10.5 Regra PVC

> Requisito sem verificação é desejo, não requisito.

---

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

# 15. Padrão 11 — Definition of Done

## 15.1 Objetivo

Definition of Done é a descrição formal do estado necessário para considerar uma entrega concluída.

## 15.2 Por que é crítica com IA

A IA costuma dizer “concluído” quando:

- escreveu código;
- não rodou teste;
- não testou erro;
- não atualizou documentação;
- não removeu mock;
- não verificou integração.

Definition of Done impede isso.

## 15.3 DoD PVC

Uma entrega só é concluída se:

- [ ] Está vinculada a um requisito.
- [ ] O requisito tem critério de aceite.
- [ ] O código foi implementado.
- [ ] O teste mínimo foi criado ou justificadamente dispensado.
- [ ] O fluxo principal foi testado.
- [ ] Pelo menos um fluxo de erro foi testado.
- [ ] Logs foram verificados.
- [ ] Mocks foram removidos ou registrados.
- [ ] Placeholders foram removidos ou registrados.
- [ ] Variáveis de ambiente foram documentadas.
- [ ] Documentação foi atualizada.
- [ ] Risco relevante foi revisado.
- [ ] Evidência foi registrada.
- [ ] Rollback foi descrito quando aplicável.

## 15.4 Regra PVC

> Código escrito não é entrega concluída.

---

# 16. Padrão 12 — FMEA: Failure Mode and Effects Analysis

## 16.1 Objetivo

FMEA é uma técnica para identificar modos de falha, causas, efeitos, severidade, probabilidade, detecção e ações preventivas.

## 16.2 Por que serve para IA

Agentes automatizados podem errar em escala.

Exemplos:

- enviar mensagem errada para muitos clientes;
- cobrar valor errado;
- excluir dados;
- repetir tarefa infinitamente;
- vazar segredo em log;
- pagar boleto errado;
- responder cliente com informação falsa.

## 16.3 Estrutura FMEA simples

| Campo | Pergunta |
|---|---|
| Função | O que o componente deveria fazer? |
| Modo de falha | Como pode falhar? |
| Causa | Por que falharia? |
| Efeito | O que acontece se falhar? |
| Severidade | Quão grave é? |
| Ocorrência | Quão provável é? |
| Detecção | Quão fácil é detectar? |
| Ação | Como reduzir risco? |
| Dono | Quem responde? |
| Status | Aberto/mitigado/aceito |

## 16.4 RPN: Risk Priority Number

Modelo tradicional:

```text
RPN = Severidade × Ocorrência × Detecção
```

Escala simples:

- 1 = baixo
- 5 = médio
- 10 = alto

Exemplo:

| Falha | Severidade | Ocorrência | Detecção | RPN |
|---|---:|---:|---:|---:|
| Pagar boleto errado | 10 | 3 | 6 | 180 |
| Log sem correlation_id | 4 | 6 | 5 | 120 |
| Mensagem duplicada | 6 | 5 | 4 | 120 |

## 16.5 Regra PVC

> Qualquer automação que mexe com dinheiro, dados pessoais, contratos ou reputação precisa de FMEA antes de produção.

---

# 17. Padrão 13 — Comissionamento

## 17.1 Objetivo

Comissionamento é o processo de verificar e documentar que um sistema funciona conforme os requisitos definidos pelo dono/usuário do projeto.

Na construção civil e indústria, isso evita entregar um prédio ou máquina que “parece pronto”, mas não opera corretamente.

Em software com IA, evita entregar app que “parece pronto”, mas depende de mock, não tem log, não tem teste e não suporta erro.

## 17.2 O que comissionamento não é

Comissionamento não é apenas:

- rodar uma vez;
- abrir a tela;
- ver se o botão aparece;
- confiar no que a IA disse;
- fazer demo feliz.

## 17.3 Tipos de comissionamento no PVC

### Pré-comissionamento

Verifica se o sistema está preparado para teste.

- dependências instaladas;
- ambiente sobe;
- `.env` existe;
- banco conecta;
- migrations rodam;
- endpoints respondem;
- logs aparecem.

### Comissionamento funcional

Verifica se os fluxos operacionais funcionam.

- caminho feliz;
- erro de entrada;
- erro externo;
- retry;
- timeout;
- rollback;
- persistência;
- observabilidade.

### Comissionamento operacional

Verifica se alguém consegue operar e manter.

- README;
- handoff;
- backup;
- restauração;
- logs;
- runbook;
- alertas;
- permissões.

## 17.4 Regra PVC

> Sem relatório de comissionamento, não existe entrega operacional.

---

# 18. Padrão 14 — Handoff operacional

## 18.1 Objetivo

Handoff é a transferência de conhecimento para continuidade.

Mesmo se você trabalha sozinho, o handoff é necessário porque o “você do futuro” não lembrará de tudo.

## 18.2 Conteúdo mínimo

- o que o sistema faz;
- como instalar;
- como rodar;
- como testar;
- como subir;
- como desligar;
- como restaurar backup;
- onde estão logs;
- onde estão secrets;
- quais pendências existem;
- quais decisões foram tomadas;
- quais riscos continuam abertos.

## 18.3 Regra PVC

> Projeto sem handoff vira dependência da memória humana.

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

# 22. A metodologia combinada: PVC

## 22.1 Definição formal

PVC é uma metodologia de entrega assistida por IA baseada em:

- especificação antes do código;
- operação antes da interface;
- fluxo vertical antes de feature horizontal;
- verificação antes de avanço;
- maturidade explícita;
- mocks controlados;
- comissionamento antes de entrega;
- handoff antes de continuidade.

## 22.2 Fórmula

```text
PVC = SDD + ConOps + Engenharia de Sistemas + V-Model + TRL + LOD + Stage-Gate + WBS + DoD + FMEA + Comissionamento + Handoff + ADR + Rastreabilidade + Registro de Mocks
```

## 22.3 Princípios

1. **Operação antes de solução.**
2. **Especificação antes de código.**
3. **Fluxo vertical antes de lista de features.**
4. **Integração real antes de aparência de produto.**
5. **Mock permitido, mas nunca oculto.**
6. **Requisito sem teste não passa.**
7. **Entrega sem evidência não é entrega.**
8. **Decisão arquitetural precisa de registro.**
9. **Gate é decisão, não formalidade.**
10. **Handoff é parte do produto.**

## 22.4 O que é uma unidade de entrega PVC

Uma unidade de entrega PVC é um fluxo pequeno, completo e comissionável.

Exemplo:

```text
Receber pedido → validar → salvar → processar → responder → registrar log → tratar erro → testar → documentar → comissionar.
```

## 22.5 O que não é unidade de entrega PVC

- só tela;
- só endpoint;
- só banco;
- só layout;
- só mock;
- só prompt;
- só automação sem log;
- só código sem teste.

---

# 23. Fluxo operacional completo

## 23.1 Macrofluxo

```text
G0 Intenção
↓
G1 ConOps
↓
G2 Requisitos
↓
G3 Interfaces
↓
G4 Riscos / FMEA
↓
G5 WBS / plano de tarefas
↓
G6 Implementação vertical
↓
G7 Integração e testes
↓
G8 Comissionamento
↓
G9 Handoff
↓
Operação controlada
```

## 23.2 Fluxo detalhado

### Etapa 0 — Intenção

Saída:

- `PROJECT_BRIEF.md`

Perguntas:

- qual dor?
- para quem?
- qual resultado esperado?
- qual fluxo real?
- qual risco se falhar?

### Etapa 1 — ConOps

Saída:

- `CONOPS.md`

### Etapa 2 — Requisitos

Saídas:

- `REQUIREMENTS_MATRIX.md`
- `ACCEPTANCE_CRITERIA.md`

### Etapa 3 — Interfaces

Saídas:

- `INTERFACES.md`
- contratos de API;
- modelo de dados.

### Etapa 4 — Riscos

Saída:

- `RISK_REGISTER_FMEA.md`

### Etapa 5 — Plano

Saídas:

- `WBS.md`
- `TASKS.md`

### Etapa 6 — Implementação

Saídas:

- código;
- testes;
- logs;
- migrations;
- configs.

### Etapa 7 — Verificação

Saídas:

- resultado de testes;
- evidências;
- correções.

### Etapa 8 — Comissionamento

Saída:

- `COMMISSIONING_REPORT.md`

### Etapa 9 — Handoff

Saída:

- `HANDOFF.md`
- `RUNBOOK.md`

---

# 24. Estrutura de pastas padrão

```text
/project
  README.md
  AGENTS.md
  .env.example
  docker-compose.yml

  /docs
    PROJECT_BRIEF.md
    CONOPS.md
    REQUIREMENTS_MATRIX.md
    ACCEPTANCE_CRITERIA.md
    INTERFACES.md
    DATA_MODEL.md
    RISK_REGISTER_FMEA.md
    WBS.md
    TASKS.md
    MOCK_REGISTER.md
    DEFINITION_OF_DONE.md
    COMMISSIONING_REPORT.md
    HANDOFF.md
    RUNBOOK.md

    /adr
      ADR-0001-template.md

    /evidence
      logs/
      screenshots/
      api-responses/
      test-results/

  /src
  /tests
  /scripts
  /config
```

---

# 25. Papéis de agentes de IA dentro da metodologia

## 25.1 Arquiteto de sistemas

Função:

- ler ConOps;
- propor arquitetura;
- identificar lacunas;
- criar ADRs;
- revisar dependências.

## 25.2 Engenheiro de requisitos

Função:

- transformar intenção em requisitos;
- criar critérios de aceite;
- detectar ambiguidade;
- montar matriz de rastreabilidade.

## 25.3 Implementador

Função:

- escrever código;
- seguir contratos;
- não inventar escopo;
- atualizar documentação técnica.

## 25.4 QA / Auditor

Função:

- testar;
- revisar mocks;
- procurar placeholders;
- verificar DoD;
- reprovar entrega incompleta.

## 25.5 Comissionador

Função:

- executar fluxo ponta a ponta;
- registrar evidência;
- listar pendências;
- aprovar ou reprovar operação.

## 25.6 Operador / SRE leve

Função:

- revisar logs;
- validar backup;
- validar rollback;
- documentar runbook.

## 25.7 Regra

> Não use o mesmo agente mental para criar e aprovar. Quem implementa não deve ser o único a auditar.

Mesmo se for a mesma IA, rode em papéis separados.

---

# 26. Prompts reutilizáveis

## 26.1 Prompt: transformar ideia em ConOps

```text
Você é um engenheiro de sistemas.
Transforme a ideia abaixo em um CONOPS.md.
Não proponha código ainda.
Inclua: missão do sistema, usuários, ambiente operacional, fluxo nominal, fluxos alternativos, fluxos de falha, dependências, limites, restrições, riscos operacionais e critérios de sucesso.
Se houver ambiguidade, liste as lacunas em vez de inventar.

Ideia:
[cole aqui]
```

## 26.2 Prompt: criar requisitos verificáveis

```text
Você é um engenheiro de requisitos.
Leia o CONOPS.md abaixo e gere uma REQUIREMENTS_MATRIX.md.
Cada requisito deve ter ID, descrição, tipo, prioridade, critério de aceite, método de verificação e status inicial.
Não escreva código.
Não inclua requisito impossível de verificar.
```

## 26.3 Prompt: criar interfaces

```text
Você é um arquiteto de integração.
Com base nos requisitos, gere INTERFACES.md.
Inclua endpoints, eventos, payloads, respostas, erros, autenticação, dependências, formato de logs e contratos entre módulos.
Marque claramente qualquer integração ainda não definida como pendência.
```

## 26.4 Prompt: FMEA

```text
Você é um analista de risco FMEA.
Leia CONOPS.md, REQUIREMENTS_MATRIX.md e INTERFACES.md.
Liste modos de falha, causas, efeitos, severidade, ocorrência, detecção, RPN e mitigação.
Dê prioridade a falhas envolvendo dinheiro, dados pessoais, reputação, exclusão de dados, loops infinitos, automação sem supervisão e vazamento de secrets.
```

## 26.5 Prompt: implementação restrita

```text
Você é o implementador.
Implemente apenas os requisitos [IDs].
Não implemente escopo não solicitado.
Não crie mock sem registrar em MOCK_REGISTER.md.
Não altere arquitetura sem ADR.
Ao terminar, informe arquivos modificados, testes executados e pendências.
```

## 26.6 Prompt: auditoria de entrega

```text
Você é auditor QA severo.
Leia os arquivos alterados, REQUIREMENTS_MATRIX.md, MOCK_REGISTER.md e DEFINITION_OF_DONE.md.
Procure: mock oculto, placeholder, código morto, requisito sem teste, erro sem tratamento, log ausente, quebra de contrato, variável .env não documentada e documentação desatualizada.
Classifique a entrega como APROVADA, APROVADA COM RESTRIÇÕES ou REPROVADA.
```

## 26.7 Prompt: comissionamento

```text
Você é comissionador operacional.
Monte um COMMISSIONING_REPORT.md para o fluxo [nome].
Inclua ambiente, versão, pré-condições, passos executados, resultado esperado, resultado observado, evidências, falhas, pendências, decisão e próximo gate.
Não aprove sem evidência.
```

---

# 27. Templates copiáveis

## 27.1 PROJECT_BRIEF.md

```markdown
# PROJECT_BRIEF.md

## Nome do projeto

## Problema real

## Usuário-alvo

## Resultado esperado

## Escopo inicial

## Fora de escopo

## Hipóteses

## Riscos óbvios

## Métrica de sucesso

## Decisão atual
Continuar / Pausar / Matar / Pesquisar mais
```

## 27.2 CONOPS.md

```markdown
# CONOPS.md

## 1. Missão do sistema

## 2. Usuários e papéis

| Papel | O que faz | Permissões | Riscos |
|---|---|---|---|

## 3. Ambiente operacional

## 4. Fluxo nominal

## 5. Fluxos alternativos

## 6. Fluxos de falha

## 7. Dependências externas

## 8. Limites do sistema

## 9. Restrições

## 10. Critérios de sucesso operacional

## 11. Critérios de falha inaceitável
```

## 27.3 REQUIREMENTS_MATRIX.md

```markdown
# REQUIREMENTS_MATRIX.md

| ID | Requisito | Tipo | Prioridade | Critério de aceite | Método de verificação | Status |
|---|---|---|---|---|---|---|
| R-001 |  | Funcional | Alta |  | Teste | Pendente |
```

## 27.4 INTERFACES.md

```markdown
# INTERFACES.md

## Interface: [nome]

### Tipo
API / Evento / Banco / Arquivo / Webhook / UI

### Entrada

```json
{}
```

### Saída de sucesso

```json
{}
```

### Erros previstos

| Código | Causa | Resposta | Log necessário |
|---|---|---|---|

### Autenticação/autorização

### Dependências

### Mock permitido?
Sim/Não

### Critério para remover mock
```

## 27.5 MOCK_REGISTER.md

```markdown
# MOCK_REGISTER.md

| ID | Local | Tipo | Motivo | Risco | Como remover | Gate limite | Status |
|---|---|---|---|---|---|---|---|
```

## 27.6 RISK_REGISTER_FMEA.md

```markdown
# RISK_REGISTER_FMEA.md

| ID | Função | Modo de falha | Causa | Efeito | S | O | D | RPN | Mitigação | Dono | Status |
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|
```

## 27.7 DEFINITION_OF_DONE.md

```markdown
# DEFINITION_OF_DONE.md

Uma entrega só pode ser marcada como concluída se:

- [ ] Requisito vinculado.
- [ ] Critério de aceite definido.
- [ ] Código implementado.
- [ ] Teste executado.
- [ ] Fluxo feliz testado.
- [ ] Fluxo de erro testado.
- [ ] Logs verificados.
- [ ] Mocks removidos ou registrados.
- [ ] Placeholders removidos ou registrados.
- [ ] `.env.example` atualizado.
- [ ] README ou docs atualizados.
- [ ] Evidência registrada.
- [ ] Risco revisado.
- [ ] Rollback descrito quando aplicável.
```

## 27.8 COMMISSIONING_REPORT.md

```markdown
# COMMISSIONING_REPORT.md

## Sistema

## Versão / commit

## Ambiente
Local / staging / produção controlada

## Fluxo testado

## Pré-condições

## Passos executados

| Passo | Ação | Resultado esperado | Resultado observado | Status |
|---|---|---|---|---|

## Evidências

- logs:
- prints:
- resposta API:
- registro no banco:

## Falhas encontradas

## Pendências

## Decisão
Aprovado / Aprovado com restrições / Reprovado

## Próximo gate
```

## 27.9 HANDOFF.md

```markdown
# HANDOFF.md

## O que o sistema faz

## Como instalar

## Como configurar

## Variáveis de ambiente

| Variável | Obrigatória | Exemplo | Descrição |
|---|---|---|---|

## Como rodar

## Como testar

## Como fazer deploy

## Como ver logs

## Como fazer backup

## Como restaurar

## Como desligar

## Riscos conhecidos

## Pendências

## Decisões importantes

## Contatos / responsáveis
```

## 27.10 ADR.md

```markdown
# ADR-0001 — [título]

## Status
Proposta / Aceita / Rejeitada / Substituída

## Contexto

## Decisão

## Alternativas consideradas

## Consequências positivas

## Consequências negativas

## Data
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

# 29. Métricas de controle

## 29.1 Métricas de qualidade

- % de requisitos com teste.
- % de requisitos com evidência.
- número de mocks abertos.
- número de placeholders abertos.
- número de falhas FMEA críticas sem mitigação.
- número de gates reprovados.
- número de bugs encontrados antes da produção.
- número de bugs encontrados depois da produção.

## 29.2 Métricas de fluxo

- tempo de ideia até ConOps;
- tempo de ConOps até primeiro fluxo vertical;
- tempo de implementação até comissionamento;
- tempo médio de correção por gate;
- número de fluxos comissionados por mês.

## 29.3 Métricas de IA

- % de código aceito sem modificação;
- % de código rejeitado por mock oculto;
- % de tarefas em que IA inventou escopo;
- % de tarefas com documentação incompleta;
- número de vezes que IA removeu comportamento necessário;
- custo de tokens por entrega comissionada.

## 29.4 Métrica principal

> Fluxos reais ponta a ponta comissionados por mês.

Não meça vaidade:

- número de arquivos;
- número de linhas de código;
- número de telas;
- número de prompts.

Meça entrega operável.

---

# 30. Como adaptar por tipo de projeto

## 30.1 Projeto pessoal simples

Use versão leve:

- ConOps curto;
- matriz de requisitos simples;
- registro de mocks;
- DoD;
- commissioning report curto;
- handoff.

Não precisa exagerar em FMEA se não houver risco relevante.

## 30.2 Automação com n8n/Activepieces

Obrigatório:

- ConOps;
- interfaces/webhooks;
- FMEA;
- logs;
- retry;
- idempotência;
- registro de credenciais;
- handoff.

Riscos principais:

- loop infinito;
- envio duplicado;
- dado errado;
- credencial exposta;
- automação rodando fora de hora;
- ausência de alerta.

## 30.3 Agente de atendimento

Obrigatório:

- política de resposta;
- limites do agente;
- escalonamento humano;
- logs de conversa;
- proteção de dados pessoais;
- FMEA reputacional;
- teste com casos ambíguos.

## 30.4 Agente de pagamento ou financeiro

Obrigatório:

- supervisão humana;
- whitelist de destinatários;
- limite de valor;
- dupla confirmação;
- logs imutáveis;
- FMEA rigorosa;
- rollback quando possível;
- auditoria.

Regra:

> Automação financeira sem autorização explícita e trilha de auditoria não deve ir para produção.

## 30.5 Micro-SaaS

Obrigatório:

- requisitos;
- autenticação;
- autorização;
- banco;
- backup;
- logs;
- billing se houver cobrança;
- termos/política se houver dados pessoais;
- monitoramento básico;
- comissionamento por fluxo.

## 30.6 IAaaS / serviço para microempresa

Obrigatório:

- escopo contratual;
- limites do agente;
- handoff para cliente;
- relatório de comissionamento;
- registro de riscos;
- matriz de responsabilidades;
- logs e auditoria;
- plano de suporte.

---

# 31. Erros comuns e antídotos

## Erro 1 — Começar pelo código

Antídoto:

> Comece por ConOps e requisitos.

## Erro 2 — Aceitar mock como produto

Antídoto:

> Mock register obrigatório.

## Erro 3 — Fazer features horizontais

Exemplo ruim:

- tela de login;
- tela de cadastro;
- dashboard;
- configurações.

Antídoto:

> Faça fluxo vertical pequeno.

## Erro 4 — Não testar erro

Antídoto:

> Cada fluxo deve ter caminho feliz e pelo menos um caminho de falha.

## Erro 5 — Não registrar decisão

Antídoto:

> ADR para decisões arquiteturais.

## Erro 6 — Handoff inexistente

Antídoto:

> O projeto só passa G9 se outra pessoa/agente conseguir rodar.

## Erro 7 — Confundir velocidade com progresso

Antídoto:

> Progresso real = requisito verificado + evidência + operação.

## Erro 8 — IA inventar escopo

Antídoto:

> Implementador só pode executar IDs de requisito autorizados.

## Erro 9 — Falta de ambiente controlado

Antídoto:

> Separar local, staging e produção sempre que possível.

## Erro 10 — Não controlar maturidade

Antídoto:

> TRL-PVC e LOD-PVC por módulo.

---

# 32. Veredito e regra final

MVP continua útil para validar demanda. Mas para projetos criados com IA, especialmente vibecoding, MVP é insuficiente como metodologia de entrega.

A metodologia mais adequada para você é:

```text
PVC — Protótipo Vertical Comissionável
```

Porque ela força a IA a sair de:

```text
“parece funcionar”
```

para:

```text
“funciona, foi testado, está documentado, tem evidência, tem limites e pode ser operado.”
```

Regra final:

> O projeto só avançou quando um fluxo real ficou menor, mais claro, mais testado, mais integrado e mais operável.

Se a IA gerou mais código, mais telas e mais arquivos, mas não aumentou a capacidade operacional comprovada, ela não entregou progresso. Ela entregou ruído.

---

# 33. Fontes e referências

Estas fontes fundamentam os padrões citados. A metodologia PVC é uma adaptação prática que combina padrões existentes de várias áreas.

## Engenharia de sistemas, verificação e validação

- NASA Systems Engineering Handbook: https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf
- NASA Product Verification: https://www.nasa.gov/reference/5-3-product-verification/

## TRL — Technology Readiness Level

- NASA Technology Readiness Levels: https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/
- NASA TRL Definitions PDF: https://www.nasa.gov/wp-content/uploads/2017/12/458490main_trl_definitions.pdf

## LOD — Level of Development / BIM

- BIMForum LOD Specification 2024: https://bimforum.org/bimforum-level-of-development-lod-specification-2024-in-english-and-spanish-language-version/
- BIMForum LOD Resource Page: https://bimforum.org/resource/lod-level-of-development-lod-specification/

## Scrum / Definition of Done

- Scrum Guide 2020: https://scrumguides.org/scrum-guide.html

## Spec-Driven Development e agentes de IA

- Martin Fowler — Spec-Driven Development: https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- GitHub Spec Kit: https://github.com/github/spec-kit
- GitHub Blog — Spec-driven development with AI: https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
- OpenAI Codex — AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- AGENTS.md open format: https://agents.md/

## Stage-Gate

- Stage-Gate Overview: https://www.stage-gate.com/blog/the-stage-gate-model-an-overview/
- PMI Phase-Gate discussion: https://www.pmi.org/learning/library/phase-gate-processes-promising-complex-547

## WBS — Work Breakdown Structure

- PMI — Work Breakdown Structure Basic Principles: https://www.pmi.org/learning/library/work-breakdown-structure-basic-principles-4883

## FMEA

- ASQ — Failure Mode and Effects Analysis: https://asq.org/quality-resources/fmea
- AHRQ — FMEA Analysis: https://digital.ahrq.gov/health-it-tools-and-resources/evaluation-resources/workflow-assessment-health-it-toolkit/all-workflow-tools/fmea-analysis

## Comissionamento

- WBDG — Building Commissioning Process: https://stg.wbdg.org/building-commissioning
- ASHRAE Commissioning Resources: https://www.ashrae.org/technical-resources/bookstore/commissioning
- ASHRAE Owner's Project Requirements example: https://www.ashrae.org/file%20library/about/new%20hq/ashrae-opr-attachment-to-design-services-rfp-signed.pdf

---

# Apêndice A — Prompt mestre para iniciar um novo projeto PVC

Use este prompt no início de qualquer projeto:

```text
Você vai operar dentro da metodologia PVC — Protótipo Vertical Comissionável.

Objetivo da metodologia:
Construir fluxos pequenos, reais, integrados, testados, documentados e operáveis usando IA, sem confundir mock, placeholder ou protótipo visual com produto pronto.

Regras:
1. Não implemente código antes de criar ou revisar CONOPS.md, REQUIREMENTS_MATRIX.md e INTERFACES.md.
2. Todo requisito precisa de critério de aceite e método de verificação.
3. Todo mock, stub, fake ou placeholder precisa ser registrado em MOCK_REGISTER.md.
4. Toda decisão arquitetural relevante precisa de ADR.
5. Toda entrega precisa passar pela Definition of Done.
6. Todo fluxo entregue precisa ter evidência no COMMISSIONING_REPORT.md.
7. Se encontrar ambiguidade, risco ou dependência não resolvida, registre como lacuna. Não invente silenciosamente.
8. Implemente apenas os requisitos autorizados por ID.
9. Ao final, classifique o estado do módulo em TRL-PVC e LOD-PVC.
10. Não declare conclusão sem testes, evidência e pendências explícitas.

Minha ideia/projeto:
[descreva aqui]

Primeira tarefa:
Gere PROJECT_BRIEF.md e CONOPS.md. Não escreva código ainda.
```

---

# Apêndice B — Prompt mestre para auditar um projeto PVC existente

```text
Você é auditor técnico severo de projetos criados com IA.
Audite este projeto usando a metodologia PVC — Protótipo Vertical Comissionável.

Verifique:
- se existe ConOps;
- se requisitos têm critérios de aceite;
- se interfaces estão documentadas;
- se há mocks ocultos;
- se há placeholders;
- se há código morto;
- se há endpoints sem contrato;
- se há variáveis .env não documentadas;
- se há testes mínimos;
- se há logs;
- se há comissionamento;
- se há handoff;
- se há ADR para decisões importantes;
- qual TRL-PVC e LOD-PVC de cada módulo crítico.

Classifique:
- APROVADO;
- APROVADO COM RESTRIÇÕES;
- REPROVADO.

Não seja otimista sem evidência.
```

---

# Apêndice C — Anti-prompt: o que nunca pedir à IA

Evite:

```text
Crie um app completo de X.
```

Evite:

```text
Continue melhorando até ficar bom.
```

Evite:

```text
Faça tudo de ponta a ponta.
```

Evite:

```text
Implemente as melhores práticas.
```

Esses prompts são amplos demais.

Prefira:

```text
Implemente apenas R-001, R-002 e R-003 conforme REQUIREMENTS_MATRIX.md.
Não crie escopo novo.
Não use mock sem registrar.
Ao final, rode os testes e atualize COMMISSIONING_REPORT.md com evidências.
```

---

# Apêndice D — Exemplo de aplicação rápida

## Projeto

Agente simples de tarefas pessoais.

## Fluxo PVC escolhido

```text
Usuário envia tarefa → API valida → banco salva → IA classifica prioridade → sistema retorna status → log registra evento.
```

## Requisitos

| ID | Requisito | Verificação |
|---|---|---|
| R-001 | Receber tarefa via API | Teste POST /tasks |
| R-002 | Rejeitar tarefa sem título | Teste 400 |
| R-003 | Salvar tarefa no banco | Inspeção DB |
| R-004 | Classificar prioridade | Teste com mock registrado ou IA real |
| R-005 | Registrar log | Inspeção logs |

## Mocks

| ID | Local | Tipo | Gate limite |
|---|---|---|---|
| M-001 | priorityClassifier | Mock de IA | G6 |

## Comissionamento

Aprovado apenas se:

- API responde;
- banco salva;
- log aparece;
- erro é tratado;
- mock está registrado;
- handoff explica como rodar.

---

# Apêndice E — Resumo executivo em uma página

## Problema

IA gera código rápido, mas pode deixar mocks, placeholders e integrações falsas.

## Solução

Usar PVC: Protótipo Vertical Comissionável.

## Unidade de entrega

Fluxo real ponta a ponta.

## Padrões combinados

- SDD;
- ConOps;
- Engenharia de Sistemas;
- V-Model;
- TRL;
- LOD;
- Stage-Gate;
- WBS;
- DoD;
- FMEA;
- Comissionamento;
- Handoff;
- ADR;
- Rastreabilidade;
- Mock Register.

## Regra principal

Pequeno pode. Simulado pode temporariamente. Incompleto oculto não pode.

## Métrica principal

Fluxos reais comissionados por mês.


