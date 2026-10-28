# Testes de integração

**Definição.** Exercitam a colaboração entre componentes e suas fronteiras reais:
por exemplo, serviço com banco, serialização com API ou autorização com persistência.

**Risco.** Mocks podem concordar entre si enquanto divergem da API, do esquema
ou da transação real. Um status 200 não demonstra que o efeito correto persistiu.

**Decisão prática.** Escolha fronteiras de maior risco e ambiente isolado,
reproduzível e próximo das propriedades usadas em produção. Declare versões,
configuração, dados e mocks restantes. Cubra contrato, sucesso, erro e recuperação
aplicáveis. Use recursos controlados, não produção por conveniência.
Antes de executar, inspecione scripts, credenciais referenciadas e destinos:
testes também podem enviar mensagens, cobrar ou apagar dados. Confirme isolamento.

**Prova mínima.** Execute a fronteira, confira saída e estado persistido/efeito,
incluindo rollback quando falhar. Limpe dados entre cenários. Para concorrência,
controle a disputa; para retries, injete falhas nas fronteiras relevantes.
Registre comando, versão, ambiente e resultados esperados/observados.

**Limites.** Unitários continuam úteis para regras e casos de borda; E2E verificam
fluxos do ponto de vista do usuário. Integração não substitui nenhum dos dois.
Um teste nem um percentual isolado garante cobertura suficiente. Priorize
invariantes e riscos do cenário.
[Pirâmide de testes, Ham Vocke](https://martinfowler.com/articles/practical-test-pyramid.html).

Passar testes integrais não aprova operação automaticamente: PVC ainda exige
avaliação de logs, riscos, rollback, handoff e aceite correspondente.
