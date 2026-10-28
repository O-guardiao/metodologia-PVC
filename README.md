# metodologia-PVC

**PVC — Protótipo Vertical Comissionável**, em um pacote modular para agentes.
Pacote **0.3.0** · Fonte metodológica **PVC v1.0**.

A IA começa por uma entrada curta, lê uma operação e consulta referências quando
a tarefa exige. Cada projeto guarda seu estado para continuar em outra sessão.
A visão completa e a maturidade desejada permanecem explícitas: o fluxo pequeno
é uma unidade de execução, não um limite para o produto.

## Instalação local manual

Requisitos: Git e Python 3.10+. Sem dependências Python externas.
Base 0.1.1 validada em Windows/Python 3.14. A extensão 0.2.0 foi reconstruída e
validada separadamente em Linux na nuvem; veja o relatório de validação.

Na raiz do **projeto que usará PVC**:

```text
git clone https://github.com/O-guardiao/metodologia-PVC.git .pvc-method
python .pvc-method/scripts/pvc.py check-package
python .pvc-method/scripts/pvc.py init --project . --goal "Visão completa do produto" --version "0.1"
```

O clone exige destino novo; init preserva estado existente. Acrescente manualmente
ao AGENTS.md, preservando regras existentes:

```markdown
Para trabalho PVC, leia .pvc-method/skills/pvc/SKILL.md e apenas a operação escolhida.
Ao iniciar ou retomar, execute python .pvc-method/scripts/pvc.py resume --project .
Antes de navegar no código, use pvc_map.py --project . entry; sem mapa, siga docs/CATALOGO.md.
```

Essa instrução usa leitura local, sem depender de descoberta automática de skills
pelo host. Não há instalação global, hooks automáticos ou publicação em marketplaces.
Mantenha `.pvc-method/` fora do controle de versão do produto. Versione o estado
sanitizado `.pvc/state.json` e os documentos/evidências úteis do próprio projeto.
Revise dados sensíveis antes de compartilhar; não grave credenciais no estado.

## Carregamento sob demanda

```text
python .pvc-method/scripts/pvc.py route executar
python .pvc-method/scripts/pvc.py route delimitar --topic contratos
python .pvc-method/scripts/pvc.py resume --project .
```

Route retorna caminhos sem carregar conteúdo. O agente lê só os arquivos escolhidos.
Trocar de skill não limpa contexto anterior: faça checkpoint e retome em sessão nova.

Os [fundamentos de programação](references/fundamentos.md) têm gatilhos próprios:
concorrência, idempotência, autorização, separação de responsabilidades e integração.
Cada referência explicita definição, risco, decisão prática, prova mínima e limites.

| Operação | Resultado |
|---|---|
| [Retomar](skills/pvc-retomar/SKILL.md) | Estado conferido, incertezas e próximo passo |
| [Delimitar](skills/pvc-delimitar/SKILL.md) | Critérios, preservações e impacto |
| [Executar](skills/pvc-executar/SKILL.md) | Fluxo implementado, verificações e checkpoint |
| [Verificar](skills/pvc-verificar/SKILL.md) | Revalidação, decisão e handoff |

## Continuidade e evidências

Módulos declaram arquivos de requisitos, contratos, código, testes e configuração,
mais dependências. O CLI identifica provas obsoletas nos módulos e consumidores
transitivos. Mudanças independentes preservam as provas restantes.

Antes do teste, obtenha snapshot; após executar, registre a saída com record.
São exigidos versão e hash anteriores à execução. [Contrato de estado](docs/ESTADO.md).

Teste passado não é comissionamento. G8/G9 exigem evidência operacional e decisão
explícita. O CLI verifica coerência dos registros, mas não autentica alegações,
interpreta suficiência do relatório ou descobre dependências omitidas.

## Validação e origem

```text
python -m unittest discover -s tests -v
python scripts/pvc.py check-package
```

[Resultados e limites](docs/VALIDACAO.md) ·
[Ensaio comportamental observado e limites](docs/AVALIACAO-COMPORTAMENTAL.md) ·
[Harmonização G5–G7](docs/adr/0001-gates.md) ·
[Proveniência](docs/PROVENIENCIA.md).

A fonte integral está em references/source, fora das rotas padrão.
A [licença preexistente](LICENSE) permanece intacta; a proveniência esclarece
o status do material original do Drive.

## Catálogo textual e operação de IA

[Procedimento executável](docs/CATALOGO.md) · [Fábrica com IA](docs/FABRICA.md).
O CLI `scripts/pvc_map.py` mantém gerações JSON/Markdown com índices hierárquicos
e diagramas Mermaid derivados dos mesmos registros. Consulta por aliases e
paginação evita despejar todo o mapa no contexto; `show` retorna o contrato focal.

Sequência: entrada → consulta → plano → checkpoint Git → alteração delimitada →
candidata → testes reais → revisão → promoção local → reconciliação. Falhas não
substituem a baseline. Journal interrompido bloqueia novas ações até recuperação.

Os controles valem para comandos deste CLI, não impedem outro shell nem obrigam
a IA a compreender a entrada. Catálogo é declarado, não extração automática de
todas as funções. Novo clone/worktree exige `relocate --expected-head SHA` com cópia exata e limpa;
o vínculo local preserva identidade e não renova provas. Não há demonstração de escala de um milhão de linhas,
CodeGraph, serviço de agentes ou OpenTelemetry instalado.

## Foco de entrega: E2E, não quantidade de testes

A [operação E2E](docs/E2E.md) define jornadas críticas, cenários e critérios antes
de implementar. Evidências novas classificam nível, cenário, perfil, interface,
commit, fronteiras reais e simulações. Todas as jornadas críticas precisam de
provas atuais ponta a ponta; G8/G9 ainda exigem relatório operacional e decisão
explícita. Unidade/integração ajudam diagnóstico, nunca substituem essa cobertura.

O validador registra legado sem metadados como **não classificado**, sem convertê-lo
em E2E. Uma API testada não demonstra interface web; essa exige navegador real no
fluxo. Ambiente indisponível, cenário omitido ou fronteira simulada mantêm aceite
pendente. Contagens da suíte deste pacote verificam mecanismos da metodologia,
não que aplicações de clientes estejam funcionando.
