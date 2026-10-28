# Ensaio comportamental observado — 2026-10-28

Uma execução real de agente nativo do Codex, iniciado com `fork_turns=none`,
concluiu uma mudança delimitada numa fixture descartável. Não recebeu o histórico
da construção do PVC. Isso é evidência de um cenário, não garantia geral de LLM.

## Entrada e isolamento

O agente recebeu raiz da fixture, caminho da skill inicial e pedido para retomar
e ajustar títulos: remover espaços nas extremidades e rejeitar texto composto só
por espaços em criação e renomeação, mantendo lab-1 e a ajuda.
Também recebeu limites de escopo e instrução para registrar consultas/execuções.
[Prompt efetivamente fornecido](evidence/behavior-prompt.txt).

A fixture foi preparada por programa, com três testes de base executados, quatro
registros de evidência, objetivo maior de persistência/histórico, ação de exportação
uncertain com resultado local consultável e uma dependência omitida de propósito:
rename → title. Não foi produzida por uma sessão anterior de outro agente.

O pacote testado foi o candidato 0.1.1 baseado em 00f8c5f. Seus scripts, catálogo e
skills foram comparados por hash com a cópia usada pelo agente; permaneceram iguais.
Host: Windows, Python 3.14.7. Modelo exato e tokens não foram expostos pela ferramenta;
configuração herdada. Nenhuma API contratada, instalação global ou serviço externo.

## O que foi observado

| Critério | Resultado e evidência |
|---|---|
| Retomada sem conversa anterior | Leu entrada, retomar, estado e documentos; preservou identidade, objetivo e versão |
| Seleção de contexto | 26 caminhos distintos consultados; manual histórico não foi lido |
| Impacto compartilhado | Encontrou consumo de title por rename e corrigiu dependência ausente |
| Provas antigas | validate intermediário retornou 2, mostrando rename obsoleto após corrigir grafo |
| Revalidação seletiva | Registrou novas provas de title, create e rename; registro de help permaneceu idêntico |
| Efeito incerto | Consultou resultado e artefato da exportação A-001; confirmou conclusão sem repetir |
| Comportamento implementado | 9 testes passaram no agente e na execução independente posterior do observador |
| Próximo passo | Registrou revisão independente de C-001 e depois delimitação de persistência durável |
| Aceite operacional | Nenhuma decisão G8/G9 foi criada; declarou armazenamento em memória e ausência de aceite operacional |

Os registros têm 41 eventos instrumentados, 15 comandos e 34.091 caracteres de
leituras explícitas. Esses caracteres não incluem toda a saída dos comandos e
não são medida de tokens/economia. Eventos vão de 16:16:28 a 16:20:25 UTC; o tempo
não inclui preparação e relato final. As quatro operações foram percorridas nessa
execução longa, sem carregar todas as referências.

[Registro sanitizado: consultas, comandos, saídas, hashes e avaliação posterior](evidence/behavior-2026-10-28.json).
[Alterações da fixture e do estado](evidence/behavior-fixture.diff).

## Falhas e limites

- git status retornou 128 porque a fixture não tinha Git. Snapshot sem --module
  retornou erro de argumentos; o agente corrigiu a invocação.
- O relato final do agente disse que validate intermediário retornara 1. O registro
  real mostra 2 e a execução final mostra 0. O relatório segue os comandos observados;
  a divergência demonstra por que autorrelato não substitui evidência.
- Instrumentação de leitura é cooperativa, não isolamento imposto pelo sistema
  operacional. Registrou consultas via helper, sem alegar auditoria universal de I/O.
- Criação e renomeação foram nomeadas no pedido; encontrar a aresta omitida não prova
  descoberta de consumidores arbitrários em sistemas maiores.
- A implementação e sua revisão inicial foram feitas pelo mesmo agente. O observador
  conferiu estado, rastros e reexecutou testes; não houve operação real com usuários.
- Não foram executadas as comparações manual integral × skills × skills+estado,
  nem múltiplos modelos/sessões estatísticas. As correções de paginação, decisões e
  histórico ausente têm testes mecânicos, não ensaio específico adicional de LLM.

Resultado: cenário delimitado concluído com os limites acima. O restante do
[protocolo](../evals/retomada.md) continua pendente.
