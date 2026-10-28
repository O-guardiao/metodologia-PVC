# Idempotência, repetição e efeitos incertos

**Definição.** Repetir a mesma operação lógica preserva o efeito pretendido,
sem duplicá-lo. Identifique a operação por chave estável, escopo e parâmetros.
Dois eventos distintos podem representar o mesmo efeito: defina identidade de
negócio sem suprimir atualizações legítimas. Reutilização de chave com payload
diferente precisa de tratamento explícito (por exemplo, rejeição documentada).

**Risco.** Marcar webhook como processado antes do efeito e ignorar repetições pode
perder o efeito se houver crash entre os passos. Executar antes de marcar pode duplicá-lo.

**Decisão prática.** Para efeito local, deduplicação e alteração devem compartilhar
a mesma transação/fronteira atômica, com unicidade sob concorrência. Para efeito
externo, registre estados pendente/em execução/confirmado/falha/incerto, retentativas
e reconciliação. Uma outbox pode tornar atômicos o estado local e a intenção de envio;
o consumidor ainda precisa tratar duplicatas.
[Transactional outbox, AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html).

Quando disponível, use idempotência do provedor com a mesma chave nas retentativas.
Confira escopo, parâmetros e expiração da chave; o contrato depende da API.
[Contrato de idempotência Stripe](https://docs.stripe.com/api/idempotent_requests).
Webhooks exigem também validação de origem/assinatura conforme o provedor;
duplicatas e entrega fora de ordem devem ser previstas.
[Webhooks Stripe](https://docs.stripe.com/webhooks).

**Prova mínima.** Repita sequencialmente e em concorrência; injete queda antes/depois
do efeito e antes da confirmação. Verifique efeito persistido, recuperação e estado
incerto, não só resposta HTTP. Para externo, consulte o destino antes de repetir.

**Limites.** Deduplicação local não garante exactly-once universal. Cache/Redis
podem participar da solução, mas precisam de garantias compatíveis com a invariante.
