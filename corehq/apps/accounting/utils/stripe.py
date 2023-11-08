from decimal import ROUND_DOWN, Decimal
from django.conf import settings
from corehq.apps.accounting.utils import log_accounting_info
import stripe


def get_customer_cards(username, domain):
    from corehq.apps.accounting.models import StripePaymentMethod, PaymentMethodType

    try:
        payment_method = StripePaymentMethod.objects.get(
            web_user=username,
            method_type=PaymentMethodType.STRIPE
        )
        stripe_customer = payment_method.customer
        return dict(stripe_customer.cards)
    except StripePaymentMethod.DoesNotExist:
        pass
    except stripe.error.AuthenticationError:
        if not settings.STRIPE_PRIVATE_KEY:
            log_accounting_info("Private key is not defined in settings")
        else:
            raise
    return None


def charge_through_stripe(card, customer, amount_in_dollars, currency, description, idempotency_key=None):
    """
    Creates a charge on a customer's card using Stripe's payment processing service.

    This function is a simple wrapper around the Stripe API's `Charge.create` method.

    Parameters:
    - card (str): The card token or ID representing the payment source to be charged.
    - customer (str): The ID of the stripe customer to whom the card belongs.
    - amount_in_dollars (int): The amount to charge in dollars
    - currency (str): The three-letter ISO currency code representing the currency of the charge.
    - description (str): An arbitrary string attached to the charge, for describing the transaction.
    - idempotency_key (str, optional): A unique key that ensures idempotence of the charge.

    """
    amount_in_cents = int((amount_in_dollars * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_DOWN))

    return stripe.Charge.create(
        card=card,
        customer=customer,
        amount=amount_in_cents,
        currency=currency,
        description=description,
        idempotency_key=idempotency_key,
    )
