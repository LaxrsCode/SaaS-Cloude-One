import logging
import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import StripeCustomer, WebhookEvent
from .services import SubscriptionService

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()
logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request):

    # Convertir a dict una sola vez aquí para todos los handlers
    if hasattr(data, 'to_dict'):
        data = data.to_dict()

    handlers = {
        'checkout.session.completed':        _handle_checkout_completed,
        'customer.subscription.created':     _handle_subscription_created,
        'customer.subscription.updated':     _handle_subscription_updated,
        'customer.subscription.deleted':     _handle_subscription_deleted,
        'invoice.paid':                      _handle_invoice_paid,
        'invoice.payment_failed':            _handle_invoice_payment_failed,
        'customer.subscription.trial_will_end': _handle_trial_will_end,
    }

    handler = handlers.get(event_type)
    if handler:
        try:
            handler(data)
        except Exception as e:
            logger.exception(f"Error handling {event_type}: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'status': 'processed'})

    return JsonResponse({'status': 'unhandled'})


def _handle_checkout_completed(session):
    subscription_id = session.get('subscription')
    customer_id     = session.get('customer')

    if not subscription_id or not customer_id:
        logger.info("checkout.session.completed sin subscription_id — ignorando")
        return

    customer_email = (
        (session.get('customer_details') or {}).get('email')
        or session.get('customer_email')
    )
    if not customer_email:
        logger.warning("checkout.session.completed sin email — ignorando")
        return

    # Crear usuario si no existe (sin username, solo email)
    user, created = User.objects.get_or_create(
        email=customer_email,
        defaults={'is_active': True}
    )

    # Crear o vincular StripeCustomer
    stripe_customer_obj, _ = StripeCustomer.objects.get_or_create(
        stripe_customer_id=customer_id,
        defaults={'user': user}
    )
    if stripe_customer_obj.user_id != user.id:
        stripe_customer_obj.user = user
        stripe_customer_obj.save()

    # Recuperar suscripción de Stripe e inyectar user_id en metadata
    sub = stripe.Subscription.retrieve(subscription_id)
    sub_dict = sub.to_dict() if hasattr(sub, 'to_dict') else dict(sub)

    if not sub_dict.get('metadata', {}).get('user_id'):
        stripe.Subscription.modify(subscription_id, metadata={'user_id': str(user.id)})
        sub_dict['metadata'] = {'user_id': str(user.id)}

    SubscriptionService.sync_subscription_from_stripe(sub_dict)

    if created:
        logger.info(f"Nuevo usuario creado: {customer_email}")
        _send_welcome_email(user)


def _handle_subscription_created(subscription):
    SubscriptionService.sync_subscription_from_stripe(subscription)


def _handle_subscription_updated(subscription):
    SubscriptionService.sync_subscription_from_stripe(subscription)


def _handle_subscription_deleted(subscription):
    SubscriptionService.sync_subscription_from_stripe(subscription)


def _handle_invoice_paid(invoice):
    sub_id = invoice.get('subscription')
    if sub_id:
        sub = stripe.Subscription.retrieve(sub_id)
        sub_dict = sub.to_dict() if hasattr(sub, 'to_dict') else dict(sub)
        SubscriptionService.sync_subscription_from_stripe(sub_dict)


def _handle_invoice_payment_failed(invoice):
    sub_id = invoice.get('subscription')
    if sub_id:
        sub = stripe.Subscription.retrieve(sub_id)
        sub_dict = sub.to_dict() if hasattr(sub, 'to_dict') else dict(sub)
        SubscriptionService.sync_subscription_from_stripe(sub_dict)


def _handle_trial_will_end(subscription):
    pass


def _send_welcome_email(user):
    from django.core.mail import send_mail
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    uid   = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = f"http://localhost:8000/accounts/password/reset/key/{uid}-{token}/"

    send_mail(
        subject='¡Bienvenido! Activa tu cuenta',
        message=f"Hola,\n\nTu pago fue procesado. Establece tu contraseña aquí:\n{reset_url}",
        from_email='noreply@tudominio.com',
        recipient_list=[user.email],
        fail_silently=True,
    )