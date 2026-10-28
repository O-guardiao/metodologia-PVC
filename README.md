# metodologia-PVC

**PVC — Protótipo Vertical Comissionável**, em um pacote modular para agentes.
Pacote **0.1.1** · Fonte metodológica **PVC v1.0**.

A IA começa por uma entrada curta, lê uma operação e consulta referências quando
a tarefa exige. Cada projeto guarda seu estado para continuar em outra sessão.
A visão completa e a maturidade desejada permanecem explícitas: o fluxo pequeno
é uma unidade de execução, não um limite para o produto.

## Instalação local manual

Requisitos: Git e Python 3.10+. Sem dependências Python externas.
Validado em Windows/Python 3.14. Outros hosts ainda não foram exercitados.

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
