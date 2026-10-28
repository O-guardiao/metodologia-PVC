# Catálogo textual e mudança controlada

Este módulo acrescenta navegação e atualização verificável ao PVC. O método permanece
fora do produto; o estado/mapa pertence ao produto. Não requer SQLite, CodeGraph,
Tree-sitter, LSP ou serviço remoto. Catálogos são arquivos escritos por pessoas/agentes,
e suas relações precisam ser conferidas no código.

## Caminhos e papéis

Nos comandos abaixo, `<pacote>` é o caminho do pacote PVC e `<projeto>` é a raiz do
produto. Substitua esses marcadores por caminhos reais; use aspas quando houver espaços.
Todos os comandos recebem `--project` **antes** da operação.

```text
<projeto>/
  src/ ...
  tests/ ...
  .pvc-map/
    CURRENT
    generations/<id>/
      catalog.json
      manifest.json
      audit.json  # gerações promovidas
      INDEX.md
      catalogs/<catalogo>.md
    change.json
    journal.json
    receipt.json
    logs/
```

- `CURRENT` aponta para a geração validada. Gerações e índices são preservados como
  histórico e versionados com o código. Não edite uma geração já validada.
- `catalog.json` contém registros e relações; `manifest.json` registra a identidade e
  o estado dos arquivos. Índices Markdown e diagramas Mermaid são derivados dos mesmos
  registros. Não mantenha o diagrama como segunda fonte manual.
- `change.json` contém a mudança pendente, plano, checkpoint, candidata e resultados.
  Logs e journal registram execução/recuperação; não são o catálogo validado.
- `receipt.json` vincula a emissão de `entry` à geração atual; `plan`, `query` e
  `show` exigem esse recibo. Ele prova passagem pelo comando, não leitura/compreensão
  pela IA. `audit.json` preserva comandos, resultados, hashes e revisão na geração
  promovida; logs locais completos ficam fora do Git para reduzir exposição.
- O `.gitignore` interno exclui os arquivos transitórios definidos pelo módulo.
  Não ignore toda a pasta `.pvc-map`, pois perderia o mapa validado no Git.

O índice serve como entrada e encaminhamento. Não cole a árvore completa ou todos os
símbolos no contexto. Faça consultas limitadas e abra apenas o catálogo relevante.

## 1. Preparar os registros

Crie um JSON de entrada num diretório de preparação fora do produto, por exemplo
`../pvc-inputs/catalog.json`. Ele pode permanecer fora do Git do produto porque a
geração guarda sua cópia; se preferir uma fonte autoral dentro do produto, inclua-a
no plano de alteração e no controle de versão.

Formato mínimo ilustrativo, com caminhos que precisam existir no produto:

```json
{
  "schema_version": 1,
  "catalogs": [
    {"id": "produto", "title": "Produto", "parent": null,
     "purpose": "Organizar as capacidades e seus limites."},
    {"id": "tarefas", "title": "Tarefas", "parent": "produto",
     "purpose": "Criar e renomear tarefas preservando identidade."}
  ],
  "symbols": [
    {
      "id": "titulo-validar", "name": "validar_titulo",
      "path": "src/titulo.py", "kind": "function", "catalog": "tarefas",
      "purpose": "Normalizar e validar o título antes de persistir.",
      "inputs": ["Texto informado pelo usuário"],
      "outputs": ["Título normalizado ou erro de validação"],
      "invariants": ["Não persistir título vazio"],
      "depends_on": [], "aliases": ["nome da tarefa", "título inválido"],
      "tests": ["tests/test_titulo.py"], "confidence": "declared",
      "unknown_dependencies": []
    },
    {
      "id": "tarefa-criar", "name": "criar_tarefa",
      "path": "src/tarefas.py", "kind": "function", "catalog": "tarefas",
      "purpose": "Validar e criar uma tarefa sem alterar tarefas existentes.",
      "inputs": ["Título e identificador da tarefa"],
      "outputs": ["Tarefa criada ou erro sem efeito parcial"],
      "invariants": ["Identificadores existentes não são sobrescritos"],
      "depends_on": ["titulo-validar"], "aliases": ["botão criar tarefa"],
      "tests": ["tests/test_tarefas.py"], "confidence": "declared",
      "unknown_dependencies": ["Confirmar integração de persistência antes de produção"]
    }
  ]
}
```

`depends_on` aponta do consumidor para aquilo que ele usa; os consumidores são derivados.
Use `declared`, `reviewed` ou `unknown` para explicitar a confiança. Mesmo `reviewed` é
uma declaração humana/agente, não prova gerada automaticamente. `reviewed` exige
`reviewed_sha256` com o hash SHA-256 atual do arquivo: releia o propósito e contrato
antes de renovar esse valor; não copie o novo hash para fingir revisão. Um item desconhecido
não vira conhecido porque o validador aceitou a estrutura.

IDs e caminhos não substituem explicação. Descreva entrada, saída, motivo, invariante,
integração e teste. Registre rotas, jobs, schemas, eventos e configurações como artefatos
quando forem relevantes. Não é necessário criar uma pasta para cada função: agrupe
registros por domínio/módulo e preserve IDs consultáveis.

## 2. Estabelecer a primeira baseline

Confira a raiz e os arquivos existentes. Leia o estado do Git; preserve alterações
alheias. Inicialize o catálogo:

```text
python <pacote>/scripts/pvc_map.py --project <projeto> init --catalog ../pvc-inputs/catalog.json
python <pacote>/scripts/pvc_map.py --project <projeto> entry --limit 10 --offset 0
python <pacote>/scripts/pvc_map.py --project <projeto> status
```

Confira o índice gerado, as relações, a cobertura declarada e as limitações. Inicializar
um mapa não certifica que o software funciona. Antes de editar o produto, registre os
arquivos pretendidos e a primeira geração no Git, depois confira o commit:

```sh
git -C <projeto> status --short
git -C <projeto> add -- <arquivos-iniciais-revisados> .pvc-map
git -C <projeto> diff --cached --stat
git -C <projeto> diff --cached
git -C <projeto> commit -m "chore: establish reviewed catalog baseline"
git -C <projeto> status --short
git -C <projeto> rev-parse HEAD
```

Não use `git add .` sem examinar o que será incluído. Não versione credenciais ou dados
pessoais em catálogos, fixtures e logs. A publicação remota exige autorização própria.

Para produto novo, comece por objetivo, limites e estrutura mínima, sem inventar código
pronto ou evidência. O catálogo inicial pode representar a organização ainda incompleta;
use ao menos um catálogo, permitindo `symbols: []`; o primeiro plano pode ter
`affected: []` e deve declarar os arquivos a criar e os testes que a aceitarão.
À medida que funções forem implementadas, inclua-as na candidata antes da promoção.

## 3. Encontrar a mudança e conferir suas conexões

```text
python <pacote>/scripts/pvc_map.py --project <projeto> entry --limit 10 --offset 0
python <pacote>/scripts/pvc_map.py --project <projeto> query "botão criar tarefa" --limit 10 --offset 0
python <pacote>/scripts/pvc_map.py --project <projeto> query "titulo" --catalog tarefas --limit 10 --offset 0
python <pacote>/scripts/pvc_map.py --project <projeto> show --symbol titulo-validar --limit 10 --offset 0
```

Leia os resultados, a página pertinente e seus consumidores. Confira no código o que
será alterado; leia os contratos e testes relacionados. Se o comportamento não estiver
catalogado, investigue de forma focal e registre a lacuna. Busca vazia não prova ausência.
Confira contagens e páginas seguintes; não conclua com base num resultado truncado.

Uma solicitação de alterar um botão pode exigir corrigir autorização ou serviço. Registre
o fluxo real e o menor conjunto de mudanças que resolve a causa; não edite somente o
arquivo visual nem refatore áreas independentes por conveniência.

## 4. Delimitar e preservar o ponto de retorno

Crie `../pvc-inputs/plan.json` após a localização e inspeção:

```json
{
  "intent": "Rejeitar título composto só por espaços em criação e renomeação.",
  "scope": ["src/titulo.py", "tests/test_titulo.py", "tests/test_tarefas.py"],
  "affected": ["titulo-validar", "tarefa-criar"],
  "preserve": ["IDs existentes", "Ajuda", "Nenhum efeito após rejeição"],
  "tests": [["python", "-m", "unittest", "discover", "-s", "tests", "-v"]],
  "next_step": "Reproduzir o defeito antes de alterar a regra compartilhada."
}
```

O exemplo exige adaptar símbolos e escopo ao projeto, incluindo o consumidor de
renomeação se existir. Não deixe uma dependência conhecida de fora para caber no exemplo.
Os comandos são vetores de argumentos, não strings de shell. Verifique seus efeitos
antes de executar; um teste pode acessar produção mesmo sem usar shell.

```text
python <pacote>/scripts/pvc_map.py --project <projeto> plan --spec ../pvc-inputs/plan.json
python <pacote>/scripts/pvc_map.py --project <projeto> checkpoint
python <pacote>/scripts/pvc_map.py --project <projeto> status
```

O checkpoint exige uma base Git limpa e verificável antes das edições. Preserve o commit
exibido. Se o mapa estiver stale, a árvore tiver mudanças desconhecidas ou houver tarefa
pendente, investigue e reconcilie antes de avançar. O CLI não apaga mudanças para limpar
esse estado. Uma ação externa incerta exige consulta ao destino, não mera repetição.

## 5. Alterar mantendo a baseline intacta

Implemente o recorte e seus testes. Trabalhe apenas nos arquivos delimitados. Se o
impacto real exigir mais arquivos, revise a delimitação antes de ampliar a tarefa;
não finja que a alteração adicional estava prevista. A baseline em `CURRENT` continua
apontando para o mapa anterior enquanto o código de trabalho diverge.

Copie os registros para `../pvc-inputs/candidate.json`, atualize propósito, símbolos,
dependências e testes afetados e prepare a candidata:

```text
python <pacote>/scripts/pvc_map.py --project <projeto> candidate --catalog ../pvc-inputs/candidate.json
python <pacote>/scripts/pvc_map.py --project <projeto> status
```

Não modifique os índices gerados ou `CURRENT` manualmente. Mudança pendente não é mudança
aceita. Arquivo novo, removido ou movido precisa aparecer corretamente na candidata;
propósito e dependências também exigem revisão quando o código muda.

## 6. Executar, revisar e promover

Depois de inspecionar e autorizar os comandos de teste e seu ambiente:

```text
python <pacote>/scripts/pvc_map.py --project <projeto> test --run-reviewed-tests
python <pacote>/scripts/pvc_map.py --project <projeto> status
```

Registre falhas reais; elas impedem promoção. Corrija a causa e rode novamente. Uma
mudança depois do teste torna a prova antiga insuficiente. Não altere código ou catálogo
entre obter prova e promover sem renovar as verificações. Comando de teste que altera
entradas examinadas também exige nova conferência; código de saída zero sozinho não basta.

O revisor abre diff, arquivos novos/removidos, candidata e logs. Compara o resultado com
intenção, invariantes e consumidores. Só depois registra a conclusão:

```text
python <pacote>/scripts/pvc_map.py --project <projeto> review --reviewer "revisor-identificado" --note "Causa corrigida; criação e renomeação verificadas; ajuda preservada; sem mudança fora do escopo."
python <pacote>/scripts/pvc_map.py --project <projeto> promote
python <pacote>/scripts/pvc_map.py --project <projeto> status
```

Use uma nota verdadeira, não copie a conclusão ilustrativa. O registro identifica o
revisor, mas não autentica sua independência. Promoção confere pré-condições, cria a nova
geração e registra os caminhos permitidos e mapa no commit local. Não faz push remoto.
Confira `git show --stat`, `git status --short` e o commit real antes de declarar entrega.

Um teste passado ou mapa promovido não equivale a comissionamento operacional G8/G9.
A [verificação de evidências](ESTADO.md) e os critérios de aceite continuam aplicáveis.

## 7. Retomar após interrupção

```text
python <pacote>/scripts/pvc_map.py --project <projeto> status
python <pacote>/scripts/pvc_map.py --project <projeto> recover
python <pacote>/scripts/pvc_map.py --project <projeto> entry --limit 10 --offset 0
```

Comece por `status`. Use `recover` quando houver promoção interrompida e o estado indicar
reconciliação necessária. O comando deve conferir journal, ponteiro e commit real;
não trate ausência de resposta como falha que permite repetir o commit. Resultado
inconclusivo permanece bloqueado. Recuperação não é `reset --hard` e não desfaz efeitos
externos. Se `recover` informar que a promoção não foi commitada, examine
`git diff --cached`, `git status --short` e o journal; confira que apenas o código
planejado, `CURRENT` e a nova geração íntegra estão staged. Corrija qualquer divergência
antes de continuar. Com essa correspondência confirmada, faça o commit local da promoção
e execute `recover` novamente. Não execute outro `promote` sobre journal pendente nem
remova o journal para ocultar a falha. Se HEAD mudou por outro motivo, pare para análise
de ancestralidade; não invente reconciliação automática. Para inspecionar um commit
anterior sem perder trabalho, veja [FABRICA.md](FABRICA.md).

## Cobertura, limites e critérios de honestidade

- O inventário usa arquivos e hashes; a lista de símbolos e arestas é declarada.
  Não existe parser universal nem garantia de inventário completo de funções.
- O inventário exclui nomes `.git`, `.pvc-map`, `.pvc-method`, `.venv`, `venv`,
  `node_modules` e `__pycache__`, em qualquer nível. `.git` pode ser diretório
  ou arquivo de worktree. Não usa `.gitignore` para esconder outros arquivos.
- Symlinks fora dos nomes excluídos são rejeitados, não seguidos. Arquivos binários
  podem receber hash/inventário; isso não significa compreensão de seu conteúdo.
  Não exponha dados sensíveis ao catálogo ou aos logs.
- Dependências por reflexão, configuração, evento ou serviço externo podem estar
  ausentes. Registre-as como desconhecidas até inspecionar a integração relevante.
- Índices stale não servem como retrato atual; durante trabalho pendente consulte
  baseline **e delta**, mantendo clara a diferença entre validado e em teste.
- O CLI valida suas próprias transições. Um agente com shell livre pode ignorá-lo
  ou alterar seus arquivos. Isso não é uma fronteira de segurança impenetrável.
- O manifesto inclui o caminho absoluto da raiz. Relocação para clone/worktree
  diferente exige o comando explícito descrito abaixo; sem vínculo, uso é bloqueado.
  Não altere o manifesto validado manualmente para contornar a identidade.
- Evidências locais, hashes e revisão não autentificam intenção nem eliminam risco.
  Não foi demonstrada eficácia universal em milhões de linhas ou em toda linguagem.

A instalação e as instruções de bootstrap do host precisam ser verificadas no ambiente
alvo. Não anuncie que a IA será obrigada a obedecer apenas porque o documento existe.

### Interrupção de testes

Antes de executar qualquer argv, `test` persiste fase candidata e remove prova/revisão
anterior. Interrupção deixa `execution_status` incerto; promoção permanece bloqueada.
Consulte `status`, inspecione logs e efeitos reais dos comandos, inclusive destinos
externos se existirem. Somente após resolver a incerteza, execute novamente `test`
com `--reconciled-effects "o que foi conferido no destino e resultado"`, além de
`--run-reviewed-tests`, e faça nova revisão. Uma razão vazia é rejeitada; a razão
é declaração auditável, não verificação automática do destino. O CLI não repete sozinho.

### Outro clone, worktree ou máquina

1. Verifique o SHA completo esperado na origem e no checkout de destino, sem
   assumir que o HEAD atual é o autorizado. Não transfira mudança pendente.
2. Execute `python <pacote>/scripts/pvc_map.py --project <destino> relocate --expected-head <SHA>`.
3. O comando exige Git limpo, ponteiro e geração commitados, páginas derivadas
   íntegras e inventário exatamente igual. Falha preserva manifesto e identidade.
4. O vínculo fica apenas em `.pvc-map/relocation.json` ignorado pelo Git.
   Não muda prova, data, identidade ou fonte; não comissiona o novo ambiente.
5. Execute `entry`, confira configurações/dependências externas e rode os testes
   pertinentes. A próxima promoção normal cria geração ligada ao checkout atual.

Mudança pendente/journal, artefato adulterado ou arquivos divergentes bloqueiam
relocação. Não apague estado para contornar o bloqueio: resolva a origem primeiro.
