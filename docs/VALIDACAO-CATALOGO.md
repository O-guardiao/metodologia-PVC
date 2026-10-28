# Validação do catálogo textual 0.2.0

Data: 2026-10-28. Ambiente: Linux, Python 3.12.14, Git local; sem instalação de
bibliotecas ou serviços. Base publicada: `5a2f2ef9d226318a5959db8fc34dab3137ee52b1`.
A implementação Windows não foi recuperada; esta execução é uma reconstrução.

## Provas mecânicas

A suíte `python -m unittest discover -s tests -v` executa os 47 testes anteriores
e 35 novos casos de catálogo: **82 testes passaram**, sem skips. Saída: [suíte na nuvem](evidence/tests-cloud.txt).
`python scripts/pvc.py check-package` verifica links e limite das cinco skills;
não executa modelos. `git diff --check` verifica whitespace.

A integração cria repositórios Git temporários, executa comandos reais e verifica
fase, arquivos e commits. Cobre entrada obrigatória no CLI, esquema inválido
rejeitado antes de criar controle, consulta paginada/aliases, hierarquia e diagramas,
dependências e consumidores, inventário, teste falho preservando baseline, prova
obsoleta/adulterada, escopo excedido, symlinks, timeout, argv sem shell, worktree
com `.git` arquivo, staging prévio bloqueado e recuperação de promoção interrompida
antes do commit e depois de salvar estado promovido.

Quatro defeitos encontrados pela revisão de testes foram corrigidos e regredidos:
ordem não determinística de subcatálogos; parent de tipo inválido; janela de crash
entre salvar estado promovido e remover journal; e reteste interrompido que retinha
revisão antiga. Agora a revisão/prova anterior é invalidada e persistida antes
de executar qualquer comando de teste.

## Limites

- Fixtures sintéticas, não implantação de produto nem aceite operacional.
- O ensaio abaixo observa uma tarefa e um agente, não eficácia universal nem
  comparação controlada entre metodologias/modelos. O ensaio antigo avalia 0.1.1.
- Catálogo declara relações; não comprova completude semântica. Inventário lê
  bytes em streaming para hashes, não injeta o código inteiro no contexto da IA.
- Mapa vinculado ao caminho absoluto: `relocate` exige cópia idêntica, Git limpo,
  SHA esperado e nenhuma mudança pendente; não renova provas. Clone local real
  e rejeições por SHA, pendência e divergência foram testados.
- Comandos executam somente testes revisados; não há sandbox contra comandos
  perigosos. Controles podem ser contornados por shell ou edição manual externa.
- Troca de ponteiro e JSON usam replace atômico e fsync do arquivo; não há garantia
  de recuperação de perda física de disco/energia ou fsync de diretório em todo host.
- Logs locais ignorados podem conter segredos; revise retenção e compartilhamento.
  Audit versionado contém comandos/hashes/declarações, não autenticidade externa.
- Nenhuma evidência de escala empresarial, milhão de linhas ou OTel operacional.

## Ensaio observado com agente sem histórico

Executado na nuvem em 2026-10-28, 19:14–19:17 UTC, em repositório descartável
sintético separado. Tarefa em linguagem comum: mudar preço unitário de 2 para 3,
preservando administração, zero e rejeição de quantidade negativa. O avaliador
recebeu caminho/tarefa, não roteiro de solução nem histórico de implementação.

Observado:
- Leu AGENTS/entrada e operações PVC; `entry` mostrou baseline fresca. Consultas
  amplas/sem acento retornaram zero; recorreu aos índices relevantes e `show` para
  localizar preço/consumidor. Não abriu código administrativo, apenas hash/diff.
- Planejou cinco arquivos, obteve checkpoint, criou teste vermelho, corrigiu preço
  e executou quatro testes verdes. Código consumidor e administração intactos.
- Registrou duas evidências atuais no estado PVC, criou candidata, executou testes
  pelo mapa, recebeu revisão focal do observador e promoveu commit somente local.
- `snapshot` sem `--module` e uma fase de estado não suportada foram rejeitados.
  O agente diagnosticou ambos e corrigiu antes da promoção; falhas não omitidas.
- Resultado local: commit `f7e4002c5467d31745eb026722d765a9dedc55d8`, geração
  `9312b1fcf59244b0a9a75fd457eb8c97`, status fresco/delta zero, Git limpo, duas
  evidências atuais, sem aceite operacional. Observador reexecutou os quatro
  testes após commit e confirmou preservação dos dois arquivos.

O comando de reexecução foi `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m
unittest discover -s tests -v`. Os quatro testes da fixture são separados dos
82 testes do pacote. [Evidência técnica sanitizada](evidence/behavior-cloud.txt).

Hashes do pacote durante o ensaio: `pvc_catalog.py`
`fc8344ebd1da1083313575bb5a5f4b75533fc6cd01efaf7e3fdec6fc14194efa`;
`pvc_map_workflow.py`
`cdf2b0ef12519ce91433bb855a0adf32831ca88e2499e2f121884b133414387f`;
`pvc_map.py`
`a40ecd3f7d64b6a8678d2aba4e153c963149b72ab1ef1cf91eae259d6a8ba66d`.

### Ajuste posterior ao ensaio

O observador identificou `status.change.next_step` ainda exibindo o próximo passo
do plano inicial após promoção, embora o estado PVC estivesse atualizado. Corrigido
para orientar conferência do commit/aceite pendente e não repetir implementação;
o texto inicial permanece em `plan_next_step` histórico. Regressão mecânica nova
passou. O ensaio de agente não foi repetido após esse ajuste de projeção.
