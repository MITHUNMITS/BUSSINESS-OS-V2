from __future__ import annotations

from django.db import transaction

from business_os.apps.payments.models import PaymentIntent, PaymentProvider, PaymentTransaction


@transaction.atomic
def create_manual_payment_intent(
    *,
    organization,
    provider: PaymentProvider,
    amount,
    currency: str,
    idempotency_key: str,
    metadata: dict | None = None,
) -> PaymentIntent:
    intent, _created = PaymentIntent.objects.get_or_create(
        organization=organization,
        provider=provider,
        idempotency_key=idempotency_key,
        defaults={
            "amount": amount,
            "currency": currency,
            "status": PaymentIntent.IntentStatus.SUCCEEDED
            if provider.provider_type in {PaymentProvider.ProviderType.COD, PaymentProvider.ProviderType.MANUAL}
            else PaymentIntent.IntentStatus.REQUIRES_PAYMENT,
            "metadata": metadata or {},
        },
    )
    if not intent.transactions.exists() and intent.status == PaymentIntent.IntentStatus.SUCCEEDED:
        PaymentTransaction.objects.create(
            organization=organization,
            provider=provider,
            intent=intent,
            amount=amount,
            currency=currency,
            status="succeeded",
        )
    return intent

