# Fixture sintética: jornada web completa

Esta aplicação mínima é um exemplo executável de **fronteira E2E web**. Não é um
produto comissionado nem prova de que aplicações externas funcionam. Não há login,
pagamento, serviços externos ou promessa de segurança de produção.

Fluxo coberto: formulário em Chromium real → JavaScript/fetch → HTTP real em
`127.0.0.1` → validação/regra de preço → transação SQLite real → resultado na tela →
nova página/contexto e consulta/reload → resultado persistido novamente visível.
O teste também consulta o banco independentemente, evitando aceitar só um status200.
Nenhuma dessas fronteiras é mockada; os dados de pedidos são sintéticos.

| Jornada | Critério observável |
|---|---|
| WEB-CREATE | 4 unidades × 300 centavos =1200, mesma ordem visível após nova página e reload; registro independente no banco |
| WEB-INVALID | Quantidade negativa mostra rejeição; nenhum banco/registro parcial; consulta posterior não encontra pedido |
| WEB-DUPLICATE | Pedido repetido é rejeitado; total original permanece na tela e no banco após reload |

## Execução explícita e isolada

Pré-requisitos **já disponíveis no ambiente**: Python3.10+, pacote Python Playwright,
Chromium executável no PATH e permissão de criar processos/sockets locais. Este
exemplo não instala dependências nem baixa navegador. Se faltar infraestrutura,
registre **não executado/bloqueado**, não aprove a jornada.

Na raiz do pacote:

```text
PVC_RUN_BROWSER_E2E=1 python -m unittest discover -s tests -p test_e2e_fixture.py -v
```

Os três testes `HttpApplicationIntegration` rodam sem browser para diagnóstico
HTTP/regras/SQLite; não aprovam interface. Os três `BrowserApplicationE2E` usam
o navegador real somente com opt-in.

Cada teste cria banco/diretório temporário próprio, serviço loopback com porta
escolhida pelo SO e navegador headless próprio; fecha navegador/processo e remove
somente seus dados temporários. Não aponte para banco de produção nem exponha o
servidor. `--no-sandbox` está limitado a essa fixture descartável; não é orientação
para navegação arbitrária/produção.

Sem `PVC_RUN_BROWSER_E2E=1`, a suíte marca as jornadas **skip**. Isso mantém o pacote
stdlib utilizável sem instalar browser, mas não é passe E2E. Com opt-in e browser
presente, falha de startup vira erro real, nunca skip silencioso. Consulte a saída
para separar problema do ambiente de falha da jornada.

Uma execução HTTP direta pode diagnosticar servidor e persistência, mas **não**
substitui estes testes de interface. Para um produto real, substitua esta fixture
pelas jornadas críticas e dependências reais do produto; declare simulações.
