---
name: pvc-retomar
description: Use ao iniciar sessão PVC, após compactação ou interrupção, ou quando o estado do projeto for desconhecido.
---

# Retomar

1. Leia as instruções locais. Execute `python <pacote>/scripts/pvc.py resume --project <raiz>`.
   Se o estado não existir, inspecione código, docs e trabalho aberto antes de
   `init --project <raiz> --goal "objetivo completo" --version "versão atual"`.
   Inicialização não aprova gates nem cria evidência.
2. Compare o resumo com arquivos reais e status do controle de versão. Leia apenas
   os documentos ligados à mudança ativa. Consulte [estado](../../docs/ESTADO.md)
   quando precisar criar ou corrigir registros. Preserve alterações alheias.
3. Para cada ação pendente/incerta, confira o destino e registre observado, data
   e próximo passo. Resultado incerto não autoriza repetição. Retome trabalho
   independente enquanto a ação estiver bloqueada.
4. Apresente objetivo, versão, mudança ativa, provas obsoletas, bloqueios e
   próximo passo. Estado insuficiente vira lacuna explícita, nunca conclusão inventada.
5. Atualize o checkpoint e encaminhe para delimitar, executar ou verificar somente
   quando a entrada dessa operação estiver satisfeita.

Concluído quando outro agente consegue identificar o próximo passo usando arquivos,
sem o histórico da conversa. Para operação/backup/restauração consulte o tema
`handoff`; retomada técnica não substitui handoff operacional.
