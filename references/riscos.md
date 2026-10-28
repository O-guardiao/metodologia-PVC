# Referência: riscos

Extrato PVC v1.0, seções 16, 30. [Proveniência](../docs/PROVENIENCIA.md).

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
