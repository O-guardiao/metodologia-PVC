# Validação da versão 0.1.0

Data: 2026-10-28. Ambiente: Windows, Python 3.14.7, sem bibliotecas externas.

## Executado

| Verificação | Resultado | Evidência |
|---|---|---|
| unittest discover -s tests -v | 39 testes passaram, zero falhas e zero skips | [Saída da suíte](evidence/tests.txt) |
| check-package | 5 skills; limite de 500 palavras respeitado; caminhos Markdown locais válidos | CLI reproduzível |
| Instalação manual em diretório separado | init, resume e route funcionaram, inclusive caminho com espaços e chamada fora do projeto | [Smoke test](evidence/installation.json) |
| Repetir init | Estado existente preservado | Suíte + smoke test |
| Preservação da fonte | Texto original coincide após preâmbulo editorial; normalização LF | [Manifesto SHA-256](../references/source/manifest.json) |
| git diff --check | Sem erros de whitespace nos arquivos adicionados/editados fora da cópia histórica | Revisão antes de publicar |

A suíte inclui estado ausente/JSON inválido, retomada com ação incerta,
identidades separadas, prova de outro projeto, mudança de contrato com consumidor
transitivo e módulo independente, configuração, versão antiga, mudança entre
snapshot e registro, artefato adulterado, histórico substituído, links ausentes,
ciclos, lock de escrita e caminhos fora da raiz. Também executa o fluxo CLI
snapshot → record → validate e uma fixture sintética com sucesso/erro.

As primeiras execuções revelaram um diretório temporário restrito pelo sandbox e
saída não UTF-8 em pipes no Windows. Os testes agora usam scratch local; a saída
do CLI é UTF-8. Ambos foram corrigidos e a suíte completa passou novamente.

## Limites e não executado

- Nenhum teste comportamental de LLM ou retomada em sessões reais foi executado.
  Existe um [protocolo de avaliação](../evals/retomada.md); não há garantia universal.
- A suíte valida mecanismos, não comissionamento de um produto real. A fixture é
  declaradamente sintética. Fundamentos escritos não são alegação de auditoria
  ou correção de apps externos.
- Nenhuma CI remota, marketplace, instalação global ou integração automática
  multi-host foi ativada. Compatibilidade em Linux/macOS e Python 3.10–3.13 está
  declarada como requisito de linguagem, mas não exercitada neste ambiente.
- O grafo e a cobertura são declarados. Dependência omitida, configuração externa
  não representada e log falso exigem inspeção; o CLI não os descobre/autentica.
- Links Markdown verificam destinos locais, não âncoras nem disponibilidade de
  todos os links históricos externos. Fontes técnicas dos cinco fundamentos
  foram consultadas durante a redação.

Próximo passo: executar o protocolo com sessões novas em um projeto descartável,
medindo seleção de material, retomada e revalidação, antes de anunciar eficácia
comportamental ou expandir adaptadores.
