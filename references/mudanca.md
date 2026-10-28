# Controle de mudança e continuidade

Extensão operacional 0.1.0 sobre PVC v1.0 §§18–20, 22 e 29. A fonte original
já contém handoff, rastreabilidade e maturidade; esta extensão define invalidação
de provas e o checkpoint entre sessões.

- Mantenha visão completa, módulos, TRL/LOD atual e alvo. Recorte pequeno não é teto do produto.
- Para ampliar/aprofundar, identifique capacidade, cenário, critério e preservações.
- Declare requisitos, código, contratos, testes e configuração não secreta em
  `inputs`; cada consumidor aponta para fornecedores em `depends_on`.
- Mudança em entrada ou na definição do módulo invalida provas dele e dos consumidores
  transitivos. Mudança de versão do projeto invalida todas. Alterações em módulos
  independentes preservam provas do restante.
- Dependências não declaradas são ponto cego: revise consumidores no código.
  Arquivos novos só são cobertos após inclusão em inputs; diretórios/globs não são aceitos.
- Evidências guardam identidade do projeto, versão, impressão digital e hash do artefato.
  Configuração externa precisa de exportação sanitizada ou identificador em arquivo declarado.
- Após compactação, use estado e arquivos atuais. Histórico de conversa não é autoridade.
- Ações pendentes guardam destino, status e consulta necessária. Consulte o destino
  antes de repetir qualquer efeito cujo resultado seja incerto.
- Preserve decisões antigas como histórico; obsolescência significa revalidar,
  não afirma que o produto quebrou.

Use [o contrato de estado](../docs/ESTADO.md) para representar isso no CLI.
