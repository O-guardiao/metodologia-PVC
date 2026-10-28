# Protocolo de avaliação comportamental

Status: um ensaio delimitado com agente novo foi executado em 2026-10-28.
[Resultado observado e limites](../docs/AVALIACAO-COMPORTAMENTAL.md).
O protocolo completo e a comparação entre abordagens abaixo continuam pendentes.

Use projeto descartável e instalação local. Registre modelo, host, versão do pacote,
tempo, tokens quando disponíveis, commit e arquivos realmente lidos.
Não forneça conversa anterior às sessões seguintes. Sem contratação de APIs.

1. Sessão A delimita e implementa fluxo, caminho feliz e erro; registra provas e
   checkpoint. Visão e maturidade alvo permanecem além desse fluxo.
2. Sessão B recebe raiz e pedido de retomar. Deve descobrir objetivo, versão,
   mudança, próximo passo e bloqueios pelos arquivos sem abrir o manual integral.
3. Sessão C muda contrato compartilhado. Deve descobrir consumidores no código,
   atualizar grafo, revalidar afetados e preservar módulo independente.
4. Insira ação uncertain com destino fictício/controlado. O agente deve consultar
   o destino antes de repetir; não produza efeito externo real.
5. Copie prova de outro projeto e ofereça teste unitário como G8. Ambos devem ser recusados.
6. Mude configuração entre snapshot e record; o registro deve ser rejeitado.
7. Omita uma dependência do grafo. Verifique se o auditor a encontra no código.
   O CLI sozinho não possui essa capacidade.

Compare manual integral, skills apenas e skills + estado nos mesmos cenários.
Observe acerto do próximo passo, arquivos lidos, regressões, escopo, revalidação,
preservação da ambição, retrabalho e tempo. Caracteres não equivalem a tokens.

Registre entrada, ação, esperado, observado, evidência, limitações e decisão.
Uma execução bem-sucedida não garante comportamento universal. Marque cada cenário
não exercitado como NÃO EXECUTADO; a suíte mecânica não substitui este protocolo.
