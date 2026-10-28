# Separação de responsabilidades

**Definição.** Apresentação traduz interação; domínio define regras/invariantes;
infraestrutura realiza efeitos como persistência e comunicação. A separação
permite mudar um detalhe sem reescrever a regra.

**Risco.** Uma regra implementada apenas num componente visual pode ser contornada
por outro cliente; regra misturada ao SDK/banco fica difícil de testar e reutilizar.

**Decisão prática.** Localize a decisão de negócio e dê-lhe uma interface explícita.
Passe dados necessários e mantenha efeitos em fronteiras identificáveis.
A UI apresenta resultado; o domínio decide; um adaptador pode persistir.
Isso pode caber em funções de um único módulo. Adicione abstração quando houver
dependência/variação real, não para preencher pastas.
Decida refatoração por acoplamento, duplicação de regra e impacto; quantidade de
linhas sozinha não determina a necessidade.

**Prova mínima.** Exercite a mesma regra sem renderizar a UI. Troque um adaptador
de teste e verifique a decisão; depois teste integração com a infraestrutura real.
Confirme que um caminho alternativo também aplica a regra.

**Limites.** Três camadas, repositórios e microsserviços não são exigência universal.
Separação lógica pode existir num monólito simples. A prova é preservar invariantes
e limitar impacto, não contar diretórios.
[Arquiteturas de aplicações, Microsoft](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures).
