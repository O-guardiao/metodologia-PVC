# Operação de fábrica de software com IA

Este documento descreve uma sequência operacional. O [catálogo](CATALOGO.md) oferece
comandos locais; os controles adicionais abaixo dependem do ambiente e só podem ser
ativados dentro das permissões do projeto. O PVC não instala serviços, hooks globais,
branch protection, credenciais ou OpenTelemetry automaticamente.

## 1. Receber uma intenção e transformá-la em trabalho verificável

1. Registre o pedido em linguagem comum, o resultado observável e o comportamento
   existente que deve continuar funcionando. Pergunte somente o que muda a decisão
   e não pode ser descoberto nas fontes autorizadas.
2. Identifique raiz, projeto, branch e tarefa. Execute a entrada do catálogo e confira
   validade da baseline; se houver trabalho interrompido, consulte `status` primeiro.
3. Busque a funcionalidade por nome/alias. Abra apenas os registros relevantes e siga
   dependências e consumidores. Confira a implementação real e seus contratos.
4. Registre incertezas. Se o mapa não representar um consumidor, não conclua que ele
   não existe; amplie a investigação focal e anote a lacuna.
5. Construa o plano com arquivos permitidos, símbolos afetados, preservações, comandos
   de teste e próximo passo. Escolha os [fundamentos](../references/fundamentos.md)
   acionados: concorrência, repetição, autorização, responsabilidades e integração.

Uma fábrica não é uma fila de agentes que todos leem o repositório inteiro. Decomponha
por resultado e contrato; cada executor recebe a entrada curta, seu recorte e as provas
necessárias. O objetivo do produto permanece compartilhado e persistido.

## 2. Isolar alterações sem confundir isolamento com segurança

Antes de uma tarefa Git, execute e examine:

```sh
git status --short
git branch --show-current
git rev-parse HEAD
git worktree list --porcelain
```

Pare diante de alterações desconhecidas. Não use `reset --hard`, `clean -fd` ou checkout
forçado para obter uma aparência de limpeza. Preserve trabalho existente e escolha um
novo diretório quando a política permitir.

Para trabalho paralelo autorizado, uma opção é:

```sh
git worktree add -b pvc/tarefa-123 ../pvc-tarefa-123 <commit-base-verificado>
git -C ../pvc-tarefa-123 status --short
```

O nome e caminho precisam ser novos. O arquivo `.git` da worktree é metadado Git,
não código catalogável. Para usar a baseline num clone/worktree em outro caminho,
confira `git rev-parse HEAD` contra o commit esperado e execute
`python <pacote>/scripts/pvc_map.py --project <cópia> relocate --expected-head <SHA>`.
Exige Git limpo, inventário idêntico e nenhuma mudança pendente. O vínculo local
não altera identidade/manifesto nem renova provas. Depois execute `entry` e revalide
configuração/testes locais; não trate provas antigas como comissionamento local.

Worktree separa diretório e branch; não separa banco, rede, portas nem credenciais.
Use configuração de teste identificável, banco descartável separado e portas distintas
quando necessários. Se esse isolamento não estiver disponível, não rode teste que
possa atingir produção. Nunca use credenciais reais para tornar uma fixture conveniente.

## 3. Checkpoint, execução e feedback

1. Confira estado limpo e commit-base antes do checkpoint. O checkpoint do PVC registra
   uma referência verificável; Git é quem preserva o código commitado.
2. Faça a alteração delimitada. Se encontrar requisito ou consumidor adicional,
   interrompa a edição e revise o plano/escopo antes de prosseguir.
3. Mantenha o mapa candidato separado da baseline. Registre falhas e ações incertas.
4. Inspecione os comandos de teste antes de autorizar sua execução: scripts podem
   escrever arquivos, chamar APIs ou enviar mensagens. `shell=False` reduz interpretação
   de shell, mas não transforma qualquer programa em seguro.
5. Execute testes em ambiente isolado, preserve saídas e códigos reais. Não aceite logs
   copiados de uma execução antiga como prova atual.
6. Revise diff, arquivos novos e impacto. Não altere os critérios para esconder falha.
7. Promova a revisão coerente conforme [CATALOGO.md](CATALOGO.md). Mudança posterior
   invalida a prova correspondente; uma aprovação antiga não segue o código novo.

## 4. Revisão separada e integração

O executor entrega objetivo, alterações, testes e limitações. O revisor recebe esses
artefatos e o diff, mas verifica contra requisitos e estado real. Evite ensinar ao
revisor a conclusão desejada. Cenários de aceitação independentes são úteis para
revelar implementações que apenas satisfazem testes estreitos.

Antes de integração, confira a revisão combinada com a base atual, não apenas o branch
isolado. Registre separadamente: commit local, push aceito, commit remoto, checks e merge.
O PVC não concede autorização de merge ou deployment; respeite a política do projeto.

Checks obrigatórios e proteção de branch podem impedir integração inválida no destino,
mas sua configuração é uma ação separada. Git hooks locais podem ser ignorados. Não
anuncie proteção ativa porque um exemplo de configuração existe no repositório.

## 5. Inicialização automática e limites de controle

Para um host que permita bootstrap, configure **localmente e com autorização** a leitura
da skill de entrada e a execução de `entry` no início/retomada. Primeiro teste numa
fixture: índice ausente, índice stale, sessão nova e ação interrompida.

Um interceptor anterior à ferramenta pode verificar projeto, tarefa, caminhos e fase,
negando mutação sem pré-condições. Isso só controla ferramentas realmente interceptadas:

- Um hook para `Edit` não cobre necessariamente Bash, Python, MCP ou agentes filhos.
- Verificação depois da escrita detecta o efeito, mas não o desfaz.
- Erro, timeout e saída inválida precisam de comportamento testado. Não presuma
  fail-closed; confira a documentação e versão do host.
- Quem pode modificar o interceptor ou executar fora dele pode contorná-lo. Separação
  de permissões e gates independentes são necessários para fronteira forte.

Não existe aqui adaptador universal instalado. O CLI bloqueia suas próprias operações
inválidas; não prova que a IA leu, entendeu ou respeitou o mapa por outro caminho.

## 6. Observabilidade e OpenTelemetry, quando já disponível

O pacote não instala SDK/Collector nem envia telemetria. Para integrar a uma aplicação
que **já possui** OpenTelemetry, execute uma tarefa específica de instrumentação:

1. Abra a configuração existente do SDK, propagador e exporter. Confirme destino,
   ambiente de teste, política de dados e limites de retenção; não adivinhe endpoint.
2. Crie um span raiz por execução/tarefa. Operações de localizar, analisar impacto,
   editar, testar e integrar podem gerar spans filhos com início/fim e resultado.
3. Correlacione IDs de tarefa, projeto, sessão, revisão-base e referência de evidência.
   Esses nomes são contrato do projeto, não convenções oficiais obrigatórias.
4. Registre código de saída, duração e referência ao artefato. Não envie código-fonte,
   prompts completos, tokens, dados de clientes, senhas ou URLs com credenciais.
5. Propague contexto somente a destinos autorizados. Baggage não é local para segredos.
6. Execute uma fixture com um teste que falha. Confirme no destino autorizado a árvore
   de spans, a falha e a correlação com o log; confirme também o que foi omitido.
7. Registre revisão, configuração sanitizada e evidência da consulta ao destino.

Se SDK/Collector não existir, use os logs locais da tarefa e marque a integração como
não executada. Um JSON com timestamps não deve ser anunciado como exportação OTel.
Traces explicam o que ocorreu; não autorizam ações nem comprovam todos os caminhos.

## 7. Retomada e ponto de retorno

Ao voltar de uma interrupção, leia `status`, confirme Git e confira o destino de ações
incertas antes de repetir. Um processo pode ter terminado depois de perder a conexão.
O comando `recover` reconcilia registros locais conforme seu contrato; não equivale a
restaurar automaticamente código ou dados.

Para inspecionar um ponto Git sem apagar o trabalho atual:

```sh
git show --stat <commit-base-verificado>
git diff <commit-base-verificado> --
git worktree add -b pvc/recuperacao-123 ../pvc-recuperacao-123 <commit-base-verificado>
```

A última ação cria uma cópia de recuperação e exige caminho/branch novos e autorização.
Confira-a antes de decidir que alterações reaplicar. Migrações e efeitos externos exigem
seu próprio plano de recuperação; restaurar arquivos não desfaz transações ou mensagens.
Só remova worktrees depois de verificar que o trabalho está preservado e a remoção é
permitida. Nenhuma limpeza destrutiva automática faz parte desta sequência.

## Fontes e critérios de implantação

- [Git worktree](https://git-scm.com/docs/git-worktree) e [hooks](https://git-scm.com/docs/githooks).
- [Claude Code hooks: eventos e decisões dependentes do runtime](https://code.claude.com/docs/en/hooks).
- [GitHub: branches protegidos](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
- [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/) e [propagação](https://opentelemetry.io/docs/concepts/context-propagation/).
- [StrongDM: cenários de avaliação e simulações de serviços](https://factory.strongdm.ai/).
- [Anthropic: continuidade entre sessões](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents).

Esses relatos orientam o desenho; não demonstram eficácia universal, memória infinita
ou que seres humanos sejam sempre o gargalo. Meça localização correta, dependências
omitidas, regressões, contexto consumido, tempo e recuperação no projeto real.
