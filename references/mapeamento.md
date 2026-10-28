# Mapeamento para agentes: localizar antes de alterar

Use este tema ao iniciar um produto, retomar uma tarefa, localizar um defeito ou
mudar um contrato compartilhado. O [procedimento executável](../docs/CATALOGO.md)
explica comandos, estados e recuperação. A [operação de fábrica](../docs/FABRICA.md)
explica delegação, isolamento, observabilidade e controles do ambiente.

## O que registrar

O catálogo é um mapa hierárquico, não uma cópia de todo o código nem uma prova de
que o produto funciona. Organize sistema → domínio/subsistema → módulo → símbolos.
Use IDs estáveis e caminhos relativos; uma renomeação precisa preservar ou migrar
explicitamente a identidade. Um registro identifica:

- Nome, aliases compreensíveis ao usuário, tipo, arquivo e catálogo responsável.
- Propósito: por que existe e qual comportamento implementa.
- Entradas, saídas e invariantes que a mudança precisa preservar.
- Dependências por ID e testes associados. Consumidores são derivados das arestas
  reversas; não mantenha uma segunda lista manual contraditória.
- Confiança da descrição e dependências ainda desconhecidas.

Inclua também rotas, contratos, configurações, eventos, migrações e acesso a dados.
Uma função isolada não revela configuração dinâmica, permissões ou efeitos externos.
Não invente arestas para fazer o diagrama parecer completo. Marque o desconhecido.

## Três naturezas de informação

1. **Estrutural:** caminho existente, hash, identidade e vínculo registrado.
2. **Declarada:** propósito e dependências escritos por alguém, inclusive uma IA.
   `reviewed` exige o hash atual em `reviewed_sha256`, mas continua sendo declaração
   de revisão, não inferência automática do validador.
3. **Observada:** teste, trace ou inspeção ligado à versão e ao ambiente examinados.
   Um trace observado não prova que todos os caminhos de execução foram percorridos.

Esta versão trabalha com arquivos escritos; não possui extração semântica universal.
Uma cobertura declarada não significa que todas as funções foram descobertas. Arquivo
inventariado sem registros e dependência desconhecida continuam limitações visíveis.

## Como navegar

Comece pela entrada curta. Busque os termos do pedido e seus aliases; abra o catálogo
específico, consulte o símbolo e seus consumidores. Só então leia a implementação,
contratos e testes relevantes. Se não houver correspondência suficiente, faça busca
focal no código e registre o que faltava no mapa candidato. Não carregue todos os
catálogos para compensar uma consulta ruim.

O plano pode ampliar seu escopo quando uma dependência real exigir, mas precisa
explicar a ampliação e renovar as verificações. Alterar só o arquivo mencionado pelo
usuário não é uma regra de correção: um botão pode falhar no serviço que ele chama.

## Atualizar sem apagar a referência anterior

Preserve a baseline validada enquanto o trabalho está em andamento. Registre plano,
delta e catálogo candidato separadamente. Depois de alterar, teste e revise o diff.
Promova somente a combinação atual de código, catálogo e provas. Falha, interrupção
ou mudança concorrente não autoriza substituir silenciosamente a baseline.

Diagramas e índices são projeções dos mesmos registros: não edite um diagrama à mão
para disfarçar uma relação ausente no catálogo. O mapa precisa mostrar sua revisão e
suas limitações. Uma mudança no código pode tornar a explicação do propósito obsoleta,
mesmo que o nome da função permaneça igual.

## Prova mínima e limites

Demonstre localização, impacto, falha reproduzida, alteração delimitada, teste atual e
retomada sem histórico. Teste índice obsoleto, caminho removido, IDs duplicados,
dependência desconhecida e tentativa de promoção após falha.

Não estime maturidade, receita ou capacidade da IA por contagem de linhas. Catálogo
consultável reduz leituras desnecessárias; não oferece memória infinita, garantia de
correção ou escalabilidade comprovada em um milhão de linhas.

## Referências de projeto

- [Aider: mapa selecionado por relevância e orçamento](https://aider.chat/docs/repomap.html).
- [SCIP: representação de navegação semântica](https://github.com/scip-code/scip).
- [clangd: custos e composição de índices](https://clangd.llvm.org/design/indexing).
- [Harness engineering: conhecimento versionado e restrições mecânicas](https://openai.com/index/harness-engineering/).

São referências de desenho, não dependências instaladas nem alegações de equivalência.
