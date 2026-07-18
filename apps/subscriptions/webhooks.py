import logging
import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import StripeCustomer, WebhookEvent
from .services import SubscriptionService
from apps.dashboard.tasks import  send_subscription_confirmation_email, send_subscription_cancellation_email, send_trial_started_email

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()
logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.warning('Stripe webhook: payload inválido')
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning('Stripe webhook: firma inválida')
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    event_id = event['id']
    event_type = event['type']
    # Convertir a dict puro para que todos los handlers puedan usar .get() con seguridad
    raw = event['data']['object']
    data = raw.to_dict() if hasattr(raw, 'to_dict') else dict(raw)

    # Idempotencia: ignorar eventos ya procesados
    if WebhookEvent.objects.filter(stripe_event_id=event_id).exists():
        logger.info(f'Webhook duplicado ignorado: {event_id}')
        return JsonResponse({'status': 'already_processed'})
    WebhookEvent.objects.create(stripe_event_id=event_id)

    handlers = {
        'checkout.session.completed':           _handle_checkout_completed,
        'customer.subscription.created':        _handle_subscription_created,
        'customer.subscription.updated':        _handle_subscription_updated,
        'customer.subscription.deleted':        _handle_subscription_deleted,
        'invoice.paid':                         _handle_invoice_paid,
        'invoice.payment_failed':               _handle_invoice_payment_failed,
        'customer.subscription.trial_will_end': _handle_trial_will_end,
    }

    handler = handlers.get(event_type)
    if handler:
        try:
            handler(data)
        except Exception as e:
            logger.exception(f'Error handling {event_type}: {e}')
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
    sub = SubscriptionService.sync_subscription_from_stripe(subscription)
    if sub.is_trialing:
        send_trial_started_email.delay(sub.user.email)
    else:
        send_subscription_confirmation_email.delay(sub.user.email, sub.plan.name if sub.plan else '')


def _handle_subscription_updated(subscription):
    SubscriptionService.sync_subscription_from_stripe(subscription)


def _handle_subscription_deleted(subscription):
    sub = SubscriptionService.sync_subscription_from_stripe(subscription)
    send_subscription_cancellation_email.delay(sub.user.email)


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

