# Validação da extensão E2E 0.3.0

Data: 2026-10-28. A extensão altera o foco de aceite para jornadas críticas
completas; não converte quantidade de testes em prova de entrega.

## Mecanismos do método

A suíte padrão executou 115 testes: **112 passaram, 3 jornadas de navegador foram
explicitamente não executadas (skip opt-in)**. [Saída](evidence/tests-e2e-mechanisms.txt).
Inclui classificação legada, identidade por cenário/perfil/ambiente/nível, critérios
completos, provas obsoletas, efeito de mudança em qualquer módulo da jornada,
API sem prova de UI, simulações, snapshot composto e bloqueio de G8/G9 sem cobertura.
Esses testes provam mecanismos locais do pacote, não que uma aplicação está pronta.

## Aplicação sintética, fronteiras diferentes

A fixture em `examples/e2e_web` usa formulário/JavaScript, HTTP loopback, regras
e SQLite. Três testes de **integração backend** realmente passaram, verificando
criação e leitura, rejeição sem persistência parcial e duplicação preservando o
registro original. Isso não prova a interface web.

As três jornadas de navegador estão implementadas e requerem opt-in explícito.
Na primeira tentativa neste executor, Chromium falhou antes de interagir com a
aplicação: socket() Operation not permitted e SIGABRT. Uma tentativa de execução
escalada falhou na preparação bwrap, antes do teste. Nenhuma credencial/instalação
nova ou tentativa de contornar caminho proibido foi feita.

## E2E executado em outro executor autorizado

A tarefa cloud isolada executou as mesmas fontes verificadas por SHA-256 antes e
depois. Resultado confirmado pelo observador responsável: **6/6 passaram, zero
erros, zero skips**, em 4,588 segundos; três jornadas de navegador e três testes
HTTP de diagnóstico. Não confundir com os três skips locais da suíte padrão acima.

Ambiente: Python 3.12.14, Playwright 1.62.0, Chromium 154.0.8037.57 e SQLite 3.53.1.
Jornadas verificadas com navegador real:
- Criar pedido pela interface, conferir regra e banco, consultar em contexto novo
  e após reload: mesmo resultado persistido.
- Quantidade inválida: rejeição visível e nenhuma persistência parcial.
- Pedido duplicado: rejeição visível, registro e total original preservados.

[Registro técnico do executor](evidence/e2e-cloud-executor.txt). Nenhuma instalação,
credencial nova ou acesso ao produto do ambiente foi necessário; loopback e banco
temporário da fixture foram encerrados. Não houve captura de todo tráfego interno
do navegador; não se alega ausência absoluta de tráfego. Esses resultados validam
as jornadas declaradas da fixture sintética, não aplicativos externos ou operação
em produção.

## Regressão da revisão de cobertura

A revisão encontrou soma indevida de cenário feliz no ambiente A com cenário
negativo no ambiente B sob o mesmo perfil. Corrigido: `inspect` preserva environment
e a cobertura exige todos os cenários/critérios da jornada dentro de um único
ambiente e perfil. Relatório expõe avaliações por ambiente. Regressão pela API
pública `capture` demonstra G8 bloqueado na mistura e elegível somente após executar
o cenário faltante no mesmo ambiente. Elegível ainda não significa aceite automático.

## Limites

Metadados/relatórios são declarações com integridade local, não autenticidade
externa. Jornadas omitidas não são descobertas automaticamente. Configuração e
contratos relevantes precisam integrar `inputs` dos módulos da jornada. SHA de
commit base não representa sozinho árvore suja: source_state e fingerprint
registram o recorte, e a revisão precisa inspecionar o delta real.
