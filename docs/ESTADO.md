# Estado por projeto — schema_version 1

Estado: `<projeto>/.pvc/state.json`. Método: pacote separado.
Sempre informe --project. Use um escritor por vez; o CLI usa lock e gravação atômica.
Edição manual precisa ser coordenada. Após queda, confira que não há escritor ativo
antes de remover .pvc/write.lock.

## Campos

Init cria UUID, objetivo, versão e próximo passo, sem fabricar módulos ou aprovação.
Edite o JSON para delimitar e valide em seguida.
A [fixture completa](../tests/fixtures/state.json) demonstra o formato, mas não
substitui a identidade criada por init.

| Campo | Uso |
|---|---|
| project_id | Identidade estável e exclusiva; não reutilizar em outro projeto |
| goal | Visão completa do produto |
| version | Versão explícita sob exame; mudar invalida todas as provas |
| next_step | Próxima ação concreta |
| active_change | null ou id, intent, modules, preserve, phase, next_step |
| modules | Mapa com inputs, requirements, depends_on, maturity |
| evidence | Histórico criado por record |
| decisions | Decisões explícitas com responsável e evidências |
| pending_actions | Ações com destino, consulta e próximo passo |
| links | Caminhos locais de documentos |
| blockers | Bloqueios atuais |

Exemplo de módulo, após criar os arquivos reais:

```json
{
  "persistencia": {
    "inputs": ["docs/requisitos.md", "docs/contrato.md", "src/store.py", "tests/test_store.py", "config-publica.json"],
    "requirements": ["R-001", "R-002"],
    "depends_on": [],
    "maturity": {"trl": 4, "trl_target": 8, "lod": 300, "lod_target": 400}
  }
}
```

Requisitos devem ter critérios e métodos nos documentos. O CLI valida IDs e arquivos,
não a qualidade do texto. Depends_on aponta do consumidor para fornecedores.
Ciclos são rejeitados: agrupe componente fortemente acoplado ou refine os limites.

Inputs são arquivos relativos existentes, sem globs/diretórios. Inclua fontes,
requisitos, contratos, testes, lockfiles e configuração relevante. Mudança em entrada
ou definição invalida módulo e consumidores transitivos. TRL/LOD são avaliações e
não entram no hash.

Configuração externa exige identificador/exportação sanitizada em input, incluindo
versão de serviço/dataset quando relevante. Nunca inclua secrets. Arquivos novos
e dependências omitidas são pontos cegos que exigem revisão do código.

## Evidências

Obtenha snapshot **antes** de executar. Rode a verificação no ambiente informado,
preserve saída em arquivo e use os valores anteriores:

```text
python <pacote>/scripts/pvc.py snapshot --project <projeto> --module persistencia
python <pacote>/scripts/pvc.py record --project <projeto> --module persistencia --artifact evidence/teste-001.txt --kind test --result passed --environment "local Python 3.14" --procedure "python -m unittest discover -s tests -v" --observed-version "0.1" --expected-fingerprint "<hash-anterior>"
python <pacote>/scripts/pvc.py validate --project <projeto>
```

Procedure é texto, nunca executado pelo CLI. Record rejeita snapshot/versão
incompatíveis, guarda SHA-256 do artefato e data UTC. O chamador atesta execução;
o log não é autenticado. Não reapresente log antigo como nova prova.
Registre failed quando houver falha.

Tipos: test, inspection, operational. Uma prova nova substitui no resumo a anterior
**do mesmo módulo e tipo**. O artefato novo deve consolidar toda a cobertura
aplicável daquele tipo, incluindo falhas, não apenas o último teste.
Histórico mantém superseded; prova alterada fica stale; prova intacta, current.

A comparação usa arquivos e versão explícita, não HEAD do Git. Registre commit
no relatório e use versão imutável para promover release. Commit novo não promove
aceite automaticamente.

## Decisões e interrupção

Decisão: id, module, gate (G0–G9), decision (GO, GO_WITH_RESTRICTIONS, NO_GO, KILL),
reason, reviewer, version, fingerprint, evidence_ids. Use versão/hash do snapshot
examinado e IDs efetivamente revisados. Restrições entram em reason e blockers.
Decisão antiga não se transfere automaticamente à prova nova.

GO não pode referenciar falha, outro módulo/projeto ou ID inexistente.
G8/G9 exigem operational e relatório conforme PVC; isso é verificação estrutural.
Critérios completos estão no tema gates. Responsável ainda decide suficiência.

Ação interrompida: id, action, target, status (pending, uncertain, confirmed, denied),
verification e next_step. Confirmed significa resultado consultado, não sucesso.
Registre observação/data em verification. Consulte destino antes de repetir efeito
incerto. Negativa requer nova autorização/evidência pertinente. CLI não executa ações.

## Códigos e retomada

- 0: registros coerentes sem prova ativa obsoleta.
- 1: arquivo, estrutura ou decisão inválidos.
- 2: estrutura coerente com evidência/decisão ativa obsoleta.

Zero não significa testes passados: ausência de prova, falha, bloqueio e ação
pendente continuam visíveis. Operational_approval sempre exige revisão explícita.
Resume mostra provas/decisões ativas, objetivo, mudança, bloqueios, maturidade,
links e próximo passo. Histórico permanece no arquivo.
