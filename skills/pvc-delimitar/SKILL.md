---
name: pvc-delimitar
description: Use para delimitar uma nova mudança PVC, aprofundar capacidade ou avaliar impacto em contratos e consumidores.
---

# Delimitar mudança

1. Leia o estado atual e [controle de mudança](../../references/mudanca.md).
   Explicite capacidade pretendida, cenário operacional, não objetivos, critérios
   verificáveis e comportamentos que precisam sobreviver.
2. Escolha ampliar, aprofundar, corrigir integração ou investigar. Compare com as
   metas TRL/LOD do produto; preserve o horizonte além do recorte atual.
3. Mapeie requisitos, contratos, configuração, módulos e consumidores transitivos.
   Confirme dependências no código: o grafo declarado pode estar incompleto.
   Registre arquivos em `inputs` e dependências em `depends_on`.
4. Consulte por condição: `operacao` se uso/critério estiver indefinido;
   `contratos` se interfaces ou arquitetura mudarem; `maturidade` para metas;
   `riscos` para falhas/dados/automação; `gates` para critérios de decisão.
   Use o catálogo por `route delimitar --topic TEMA`, sem ler todos os temas.
5. Grave a mudança ativa: ID, resultado esperado, módulos, preservações, fase e
   próximo passo. Faça WBS por fluxo e vincule IDs de requisito aos testes previstos.
   Execute `validate --project <raiz>`; evidências obsoletas são pendências de
   revalidação. Registre decisões arquiteturais em ADR.

Concluído quando o recorte tem limites, critérios, impacto e verificações definidos.
Impedimentos materiais mantêm a fase em delimitar; trabalho independente pode seguir.
