# Referência: aceite

Extrato PVC v1.0, seções 10, 15, 17. [Proveniência](../docs/PROVENIENCIA.md).

**Extensão operacional 2026-10-28 — foco E2E.** Para entregar, execute todas as
jornadas críticas ponta a ponta pelo ponto de entrada alegado, incluindo efeitos
persistidos e cenários de erro pertinentes. Testes isolados são diagnóstico, não
substituto do aceite. A [sequência E2E](../docs/E2E.md) explicita configuração,
fronteiras, cenários, provas e bloqueios. O extrato histórico abaixo é preservado;
a dispensa de “teste mínimo” na DoD não dispensa E2E crítico nem autoriza declarar
aceite quando o ambiente está bloqueado. G8/G9 exigem cobertura E2E atual, relatório
operacional e decisão explícita; legado não classificado não conta como E2E.


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
- [ ] O teste mínimo foi criado ou justificadamente dispensado. **Nota da extensão:**
  isso não dispensa as jornadas críticas E2E; uma exceção mantém seu aceite pendente.
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
