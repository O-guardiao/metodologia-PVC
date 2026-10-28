---
name: pvc
description: Use para iniciar, retomar ou evoluir um projeto pelo PVC, selecionando apenas a operação necessária.
---

# PVC — Protótipo Vertical Comissionável

Entregue fluxos reais, verificáveis e operáveis. Preserve a visão completa do produto
e as metas de maturidade; o recorte limita a execução atual, não a ambição.

1. Identifique a raiz do projeto e a localização deste pacote. Estado vive em
   `<projeto>/.pvc/state.json`; método e referências vivem neste pacote.
2. Escolha uma operação. Leia **somente** o SKILL.md escolhido:

| Situação | Operação |
|---|---|
| Início de sessão, compactação, trabalho interrompido ou estado desconhecido | [Retomar](../pvc-retomar/SKILL.md) |
| Estado conhecido, nova capacidade, aprofundamento ou alteração compartilhada | [Delimitar](../pvc-delimitar/SKILL.md) |
| Mudança delimitada, critérios e dependências conhecidos | [Executar](../pvc-executar/SKILL.md) |
| Evidências, integração, aceite operacional ou handoff a conferir | [Verificar](../pvc-verificar/SKILL.md) |

3. Use `python <pacote>/scripts/pvc.py route OPERACAO` para obter os caminhos
   básicos. Acrescente `--topic TEMA` apenas quando o caso acionar aquele tema.
   O comando lista caminhos; não lê o manual nem injeta conteúdo.
4. Encerre cada operação com estado persistido, próximo passo concreto e incertezas.

Uma ação externa interrompida exige consulta ao destino antes de repetição.
Evidência de teste não equivale a comissionamento. Abrir outra skill não limpa
o contexto anterior: faça checkpoint e use sessão nova quando necessário.
