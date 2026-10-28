# ADR-0001 — Nomenclatura única dos gates

Status: aceita para o pacote 0.1.0. Data: 2026-10-28.

## Contexto
PVC v1.0 §§13.3 e 28 usam G5 Implementação vertical, G6 Integração,
G7 Verificação. §23.1 usa G5 WBS/plano, G6 Implementação vertical,
G7 Integração e testes. A numeração isolada é ambígua.

## Decisão
A operação deste pacote segue §§13.3 e 28. WBS/plano é preparação de G5,
já prevista no checklist de §28; não desaparece. Integração pertence a G6,
verificação a G7. G0–G4 e G8–G9 mantêm significado.

| Registro legado baseado em §23.1 | Migração por significado |
|---|---|
| G5 WBS/plano | Preparação de G5; não prova implementação |
| G6 Implementação vertical | G5 |
| G7 Integração e testes | Separar evidência de G6 e G7 |
| G8/G9 | Manter, revalidando a evidência se afetada |

## Alternativas
Adotar §23.1 conflitaria com tabela e checklists. Renumerar todos quebraria
referências. Conservar ambiguidade manteria retomadas inseguras.

## Consequências
A fonte histórica permanece intacta. O importador humano deve registrar qual
seção originou o gate legado; registro sem essa informação não recebe aprovação
automática. Critérios são reavaliados por significado, nunca por número apenas.
