---
name: pvc-verificar
description: Use para revalidar fluxos afetados, revisar evidências, comissionar ou conferir handoff de uma mudança PVC.
---

# Verificar e comissionar

Confira candidata, delta, consumidores, testes reais e lacunas de cobertura.
No [fluxo do mapa](../../docs/CATALOGO.md), registre `review` somente após provas
válidas; `promote` cria commit local com código e nova geração, sem push.
Journal pendente exige inspeção e `recover`, nunca repetição cega ou reset.
Rode `entry` após promoção e confira a geração; reconcilie o estado PVC e evidências
sem converter promoção técnica em aceite operacional. Revisor informado não prova
independência: registre quem de fato revisou.

**Entrega começa pela jornada E2E**, não pela soma de testes. Defina jornadas críticas,
cenários/critério e fronteiras reais em [E2E](../../docs/E2E.md). Para interface web,
exercite navegador → backend → persistência → resultado após recarga. Unitários e
integração diagnosticam; não substituem as jornadas. Ambiente bloqueado, mock no
caminho crítico ou cenário faltante mantêm aceite pendente, nunca aprovação por contagem.

1. Assuma papel de auditor e confronte o resultado com critérios e comportamento
   real. A fonte §25.7 exige separação de criação e auditoria: use revisão
   independente quando disponível; se feita pela mesma IA, declare a limitação.
2. Execute `validate --project <raiz>`. Corrija registros inválidos e renove provas
   obsoletas executando os testes pertinentes. Inspecione consumidores e arquivos
   fora do grafo: o validador só cobre dependências declaradas.
3. Leia [aceite e comissionamento](../../references/aceite.md).
   Aplique os [gatilhos dos fundamentos](../../references/fundamentos.md) às fronteiras
   afetadas e confira as invariantes e provas das referências selecionadas.
   Verifique fluxo nominal, erro, logs, mocks, riscos, integridade e rollback
   aplicáveis. Teste regressões nas capacidades afetadas.
4. Para decisão por gate, consulte `gates`. Registre decisão, responsável,
   restrições, evidências e versão. G8 requer relatório operacional e evidência
   `operational`; teste unitário passado sozinho não serve. A checagem mecânica
   não interpreta a veracidade ou suficiência do relatório.
5. Para entrega/retomada operacional, consulte `handoff`; execute as instruções
   em ambiente controlado. Registre o que não pôde testar. Para atualizar maturidade,
   consulte `maturidade` e sustente TRL/LOD com evidência, sem promoção automática.
6. Atualize estado, próximo passo e pendências. Arquive detalhes em arquivos
   ligados, mantendo o checkpoint curto. Reabra apenas critérios afetados.

Concluído quando existe decisão sustentada, limitações explícitas e próximo passo
retomável. Falha ou evidência insuficiente mantém NO-GO/revalidação pendente.
