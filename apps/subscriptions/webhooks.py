import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import WebhookEvent
from .services import SubscriptionService
from apps.dashboard.tasks import (
    send_subscription_confirmation_email,
    send_subscription_cancellation_email,
    send_trial_started_email,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    event_id = event['id']
    if WebhookEvent.objects.filter(stripe_event_id=event_id).exists():
        return JsonResponse({'status': 'already_processed'})

    WebhookEvent.objects.create(stripe_event_id=event_id)

    event_type = event['type']
    data = event['data']['object']

    handlers = {
        'checkout.session.completed': _handle_checkout_completed,
        'customer.subscription.created': _handle_subscription_created,
        'customer.subscription.updated': _handle_subscription_updated,
        'customer.subscription.deleted': _handle_subscription_deleted,
        'invoice.paid': _handle_invoice_paid,
        'invoice.payment_failed': _handle_invoice_payment_failed,
        'customer.subscription.trial_will_end': _handle_trial_will_end,
    }

    handler = handlers.get(event_type)
    if handler:
        handler(data)
        return JsonResponse({'status': 'processed'})

    return JsonResponse({'status': 'unhandled'})


def _handle_checkout_completed(session):
    pass


def _handle_subscription_created(subscription):
    sub = SubscriptionService.sync_subscription_from_stripe(subscription)
    if sub.status == 'trialing':
        send_trial_started_email.delay(user_email=sub.user.email)
    elif sub.status == 'active':
        name = sub.plan.name if sub.plan else 'Pro'
        send_subscription_confirmation_email.delay(
            user_email=sub.user.email,
            plan_name=name,
        )


def _handle_subscription_updated(subscription):
    SubscriptionService.sync_subscription_from_stripe(subscription)


def _handle_subscription_deleted(subscription):
    sub = SubscriptionService.sync_subscription_from_stripe(subscription)
    send_subscription_cancellation_email.delay(user_email=sub.user.email)

def _handle_invoice_paid(invoice):
    if invoice.get('subscription'):
        sub = stripe.Subscription.retrieve(invoice['subscription'])
        SubscriptionService.sync_subscription_from_stripe(sub)


def _handle_invoice_payment_failed(invoice):
    if invoice.get('subscription'):
        sub = stripe.Subscription.retrieve(invoice['subscription'])
        SubscriptionService.sync_subscription_from_stripe(sub)


def _handle_trial_will_end(subscription):
    sub = SubscriptionService.sync_subscription_from_stripe(subscription)
    if sub and sub.user:
        send_trial_started_email.delay(user_email=sub.user.email)
