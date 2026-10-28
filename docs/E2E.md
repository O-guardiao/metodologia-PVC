# PVC: entregar jornadas, não uma contagem de testes

Extensão operacional de 2026-10-28. O foco da entrega é demonstrar as **jornadas
críticas ponta a ponta**. Testes unitários e de integração continuam necessários
para localizar defeitos e cobrir regras; mil testes verdes não substituem uma
jornada que falha na interface, na persistência ou no resultado do usuário.

## 1. Delimitar o que será provado

Antes de implementar, abra o catálogo e localize entrada, regras, consumidores,
persistência e saída. Registre os módulos participantes e seus arquivos de
configuração em `modules.<nome>.inputs`; dependências omitidas não são descobertas
pelo validador. No estado `.pvc/state.json`, acrescente `journeys`:

```json
{
  "journeys": [{
    "id": "PEDIDO", "modules": ["checkout", "orders"], "critical": true,
    "interface": "browser", "profile": "local-isolado",
    "boundaries": ["browser", "http", "regras", "sqlite"],
    "scenarios": [
      {"id": "criar", "criteria": ["total-correto", "persiste-apos-reabrir"]},
      {"id": "invalido", "criteria": ["erro-visivel", "sem-registro-parcial"]},
      {"id": "duplicado", "criteria": ["rejeita-duplicado", "preserva-original"]}
    ]
  }]
}
```

Este é um fragmento, não substitua o restante do estado. Os módulos precisam
existir. Use IDs estáveis e critérios com expectativa e observação descritas no
requisito/log: “persiste” sem conferir o registro não basta. Selecione cenários de
erro, autorização, duplicação, recuperação ou concorrência conforme o risco real.
Não esconda cenários difíceis removendo-os da declaração para obter verde.

- Produto web: navegador real → ação na UI → HTTP → regras → armazenamento →
  resultado observado na UI; recarregue/reabra e confirme persistência.
- Produto API: cliente da API → contrato real → regras → armazenamento → resposta
  e leitura posterior. É E2E da API delimitada, **não** prova de frontend.
- Produto CLI: processo CLI → argumentos/entrada → regras → armazenamento → saída
  e novo processo de consulta. Não precisa inventar um navegador.

O perfil identifica a configuração testada. Documente versões de runtime, browser,
banco, flags, dados e destinos; configure dados sintéticos e recursos isolados.
Um backend falso sob uma tela real não prova a jornada com backend real.

## 2. Preparar ambiente sem efeitos indevidos

1. Confira comandos, variáveis, credenciais referenciadas e destinos antes de rodar.
   Não use produção, clientes, cobrança ou envio real por conveniência.
2. Use banco/diretório descartável por cenário e porta local livre. Prepare migrations
   e dados necessários; confirme prontidão antes da interação. Limpe apenas recursos
   que o próprio teste criou, respeitando as permissões vigentes.
3. Reutilize ferramentas já disponíveis. Ausência de navegador, sandbox de provedor
   ou autorização mantém a jornada **bloqueada**, não “passou com ressalva”.
4. Use uma identidade de teste autorizada quando autenticação fizer parte da jornada.
   Não contorne login necessário para chamar uma prova parcial de ponta a ponta.
5. Para serviços externos, diferencie simulador, sandbox real do provedor e produção.
   Um simulador ajuda no diagnóstico, mas não prova compatibilidade com o destino.

## 3. Executar e observar as fronteiras

Na raiz do produto, substituindo `<pacote>` pelo caminho do método:

```text
git rev-parse HEAD
git status --short
python <pacote>/scripts/pvc.py validate --project .
python <pacote>/scripts/pvc.py snapshot --project . --module checkout --journey PEDIDO
```

Guarde o `version` e o `fingerprint` **antes** da execução. O snapshot da jornada
abrange sua definição e os fingerprints de todos os módulos participantes, incluindo
dependências declaradas. Alterar a API pode invalidar a prova da jornada iniciada
no frontend. Configuração relevante deve estar em `inputs`, não só em uma descrição.

Execute cada cenário pelo ponto de entrada declarado. Confira mais que status HTTP
ou aparência otimista da tela: valor correto, estado persistido, ausência de efeito
parcial em falha e comportamento após nova leitura. Não use chamada direta à função
interna como substituto da ação do usuário. Uma chamada API pode preparar dados ou
inspecionar efeito, mas a ação UI alegada precisa acontecer no navegador.

Preserve comando, exit code, versões, resultados esperados/observados, timestamps e
artefatos úteis. Traces/screenshots auxiliam diagnóstico; não publique tokens,
sessões ou dados pessoais. Teste vermelho ajuda localizar o defeito; a entrega
exige repetir a jornada após a correção na mesma versão/configuração registrada.

## 4. Classificar e registrar, sem inflar a alegação

Prepare um JSON de verificação por cenário, por exemplo `verification-criar.json`:

```json
{
  "level": "e2e", "journey": "PEDIDO", "scenario": "criar",
  "profile": "local-isolado", "interface": "browser",
  "commit": "SUBSTITUA_PELO_SHA_COMPLETO_OBSERVADO",
  "source_state": "dirty",
  "criteria": ["total-correto", "persiste-apos-reabrir"],
  "boundaries": ["browser", "http", "regras", "sqlite"],
  "simulated_boundaries": []
}
```

O placeholder não é aceito: `commit` exige SHA hexadecimal completo de 40 ou 64
caracteres. `source_state` é `clean` ou `dirty`, conforme o checkout executado; um
commit de base não descreve sozinho mudanças não commitadas. A impressão digital
complementa essa identificação. Metadados são declarações auditáveis, não prova
criptográfica de que browser/comando realmente rodou.

```text
python <pacote>/scripts/pvc.py record --project . --module checkout --artifact evidence/pedido-criar.txt --kind test --result passed --environment "local-isolado; versões e configuração no artefato" --procedure "Cenário criar via navegador; persistência conferida após reabrir" --observed-version <VERSION_DO_SNAPSHOT> --expected-fingerprint <FINGERPRINT_DO_SNAPSHOT> --verification verification-criar.json
```

Registre cada cenário e repita snapshot/execução se entradas mudarem. O artefato não
pode ser `input` do módulo nem o próprio estado. `kind` continua distinguindo `test`,
`inspection` e `operational`; `verification.level` distingue `unit`, `integration`,
`e2e` e `simulated`. Simulação é também uma dimensão independente: mesmo `level=e2e`
com `simulated_boundaries` não vazia não satisfaz a jornada real exigida. Identidade
por módulo, tipo, nível, jornada, cenário, perfil e ambiente evita que uma prova
unitária ou de outra jornada substitua a prova E2E.

Se o ambiente impedir execução, grave artefato explicando impedimento, fronteira não
exercitada e próximo passo, com `--result blocked`. Não registre `passed`, não troque
a interface declarada e não aprove a jornada com um mock. Uma exceção pode permitir
continuar desenvolvimento independente, mas mantém o aceite dessa jornada pendente.

## 5. Verificar cobertura e decidir

```text
python <pacote>/scripts/pvc.py validate --project .
python <pacote>/scripts/pvc.py resume --project .
```

Em `validate`, confira `journey_coverage`; em `resume`, confira `e2e_acceptance`
e a página `journeys`. Confira critérios ausentes e provas atuais. Para cada jornada
crítica, todos os cenários/critérios exigidos precisam de evidência E2E atual,
passada, com perfil/interface/fronteiras correspondentes e sem fronteira simulada.
Somente happy path deixa negativos/recuperação declarados pendentes. Ausência de
jornadas declaradas não equivale a ausência de risco nem a aprovação.

G8/G9 exigem essa cobertura **e** evidência operacional **e** decisão explícita.
O relatório operacional inclui uso, logs, riscos, rollback/restauração e handoff
pertinentes. O registro da decisão deve referenciar as provas necessárias, não
somente um relatório genérico `operational`. Cobertura mecânica elegível não é
comissionamento automático; o revisor confere a suficiência e a realidade das provas.

Evidências antigas sem `verification` continuam legíveis como `unclassified`.
Não as converta automaticamente em E2E: execute a jornada e produza registro novo.
Uma promoção técnica do catálogo também não declara que a aplicação foi aceita.

## Exemplo executável deste pacote

A [fixture web isolada](../examples/e2e_web/README.md) demonstra formulário real,
HTTP loopback, regras e SQLite, com consulta em novo contexto/reload. Para executar
com Playwright/Chromium **já disponíveis**, sem instalar ou baixar ferramentas:

```text
PVC_RUN_BROWSER_E2E=1 python -m unittest discover -s tests -p test_e2e_fixture.py -v
```

Sem opt-in/infraestrutura, skip é **não executado**, jamais aprovação. Consulte a
saída concreta e o relatório de validação antes de afirmar resultado. A fixture é
uma pequena aplicação sintética delimitada; não comprova outros apps nem transforma
os testes de mecanismo do catálogo em testes de aplicação completa.

## Fontes técnicas primárias

- [Playwright: boas práticas](https://playwright.dev/docs/best-practices): comportamento
  visível, isolamento e assertions adequadas.
- [Playwright: testes de API](https://playwright.dev/docs/api-testing): preparação e
  verificação de estado via API não eliminam o teste UI da experiência alegada.
- [Playwright Trace Viewer](https://playwright.dev/docs/trace-viewer): diagnóstico de
  ações, rede e estado da página, com revisão de privacidade antes de compartilhar.
- [Testcontainers Python](https://testcontainers.com/guides/getting-started-with-testcontainers-for-python/):
  opção para dependências descartáveis reais quando já disponível/autorizada;
  não é dependência instalada por este pacote.
- [Stripe testing](https://docs.stripe.com/testing): exemplo de ambiente próprio de
  testes do provedor; citar a referência não autoriza credenciais, gastos ou uso.

### Migração de decisões antigas

Evidência legada permanece legível e não classificada. Se havia GO/G8 ou GO/G9
sem a cobertura agora exigida, registre nova decisão NO_GO para o mesmo módulo/gate,
com motivo e referências preservadas; não apague a decisão histórica. A decisão
supersedida não bloqueia a coleta das novas provas. Depois execute as jornadas,
registre suas evidências e faça nova revisão explícita. Exceção de desenvolvimento
não se transforma em aceite da jornada pendente.

### Não combinar ambientes para completar uma jornada

`environment` identifica a configuração concreta de execução, não apenas “teste”.
Registre versão/configuração sem segredos e mantenha a mesma identidade somente
quando realmente for o mesmo ambiente. Cenários no ambiente A não completam os
cenários faltantes do ambiente B, mesmo que ambos usem o mesmo `profile`. A cobertura
exige uma execução completa dos cenários/critérios em um ambiente/perfil coerente;
`validate` mostra os grupos e lacunas. Mudança de configuração relevante deve
atualizar os inputs/fingerprint e exigir reexecução.
