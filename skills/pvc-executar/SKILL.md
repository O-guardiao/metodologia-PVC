---
name: pvc-executar
description: Use para implementar um recorte PVC delimitado com requisitos, critérios e dependências definidos.
---

# Executar recorte

1. Confirme a mudança ativa e leia os requisitos, contratos e testes diretamente
   ligados a ela. Reavalie o impacto se encontrar consumidor não registrado.
2. Implemente o fluxo de ponta a ponta por incrementos verificáveis. Escolha
   os [fundamentos acionados pela mudança](../../references/fundamentos.md):
   concorrência, repetição, autorização, responsabilidades ou integração.
   Para cada tema aplicável, explicite invariante, decisão e prova mínima. Escolha
   TDD/BDD ou outra técnica adequada aos critérios. Mantenha caminhos de erro,
   persistência e observabilidade pertinentes ao cenário.
3. Consulte `contratos` para interfaces/ADR; `mocks` quando houver simulação ou
   placeholder; `riscos` quando descobrir novo modo de falha. Registre motivo,
   limite, risco e remoção de cada mock. Atualize o grafo e as entradas declaradas.
4. Obtenha `snapshot` antes de executar verificações do produto e preserve saídas observadas em arquivos.
   Registre evidência com `record` somente após execução na mesma versão e
   configuração; consulte [estado](../../docs/ESTADO.md) para o contrato do CLI.
5. Atualize fase, pendências e próximo passo. Se houver interrupção com efeito
   externo desconhecido, registre a ação como `uncertain` antes de encerrar.
   Faça checkpoint antes de trocar de sessão.

Concluído quando o recorte está implementado, as verificações executadas têm
evidências e falhas explícitas, e o estado aponta para verificar. Código escrito
ou resultado `passed` não autoriza declarar G8 aprovado.
