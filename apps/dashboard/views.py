from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from apps.subscriptions.models import StripeCustomer
from apps.subscriptions.services import AccessService, SubscriptionService
from apps.subscriptions.views import AccessService


from .models import SubscriptionPlan, UserSettings
from .tasks import (send_subscription_cancellation_email,
    send_subscription_confirmation_email,
    send_trial_started_email,
)


@login_required
@require_http_methods(['GET'])
def dashboard_home(request):
    return render(request, 'dashboard/home.html')

@login_required
@require_http_methods(['GET', 'POST'])
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('dashboard:profile')
    return render(request, 'dashboard/profile.html')

@login_required
@require_http_methods(['GET', 'POST'])
def settings(request):
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_settings.notify_comments = request.POST.get('comments') == 'on'
        user_settings.notify_updates = request.POST.get('updates') == 'on'
        user_settings.notify_marketing = request.POST.get('marketing') == 'on'
        user_settings.save()
        messages.success(request, 'Settings updated successfully.')
        return redirect('dashboard:settings')

    context = {
        'notification_settings': {
            'comments': user_settings.notify_comments,
            'updates': user_settings.notify_updates,
            'marketing': user_settings.notify_marketing,
        },
        'subscription': AccessService.get_subscription_status(request.user),
    }
    return render(request, 'dashboard/settings.html', context)

@login_required
@require_http_methods(['GET'])
def subscription_plans(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)
    context = {
        'plans': plans,
        'subscription': AccessService.get_subscription_status(request.user),
    }
    return render(request, 'dashboard/subscription_plans.html', context)


@login_required
@require_http_methods(['POST'])
def subscribe_to_plan(request, plan_slug):
    plan = get_object_or_404(SubscriptionPlan, slug=plan_slug, is_active=True)

    # Plan gratuito: activar localmente sin Stripe
    if plan.price == 0:
        user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
        user_settings.subscription_plan = plan
        user_settings.subscription_status = 'active'
        user_settings.save()
        messages.success(request, f'Successfully subscribed to {plan.name} plan.')
        return redirect('dashboard:subscription_plans')

    # Plan de pago: redirigir a Stripe Checkout vía subscriptions app
    if not plan.stripe_price_id:
        messages.error(request, 'This plan is not properly configured for payments.')
        return redirect('dashboard:subscription_plans')

    from django.urls import reverse
    checkout_url = reverse('subscriptions:create_checkout_session') + f'?plan={plan.slug}'
    return redirect(checkout_url)

@login_required
@require_http_methods(['POST'])
def cancel_subscription(request):
    from apps.subscriptions.views import SubscriptionService, AccessService

    sub = AccessService.get_current_subscription(request.user)
    if not sub:
        messages.warning(request, 'You do not have an active subscription to cancel.')
        return redirect('dashboard:settings')

    try:
        SubscriptionService.cancel_at_period_end(sub)
        messages.success(request, 'Your subscription will be cancelled at the end of the billing period.')
    except Exception as e:
        messages.error(request, f'Could not cancel subscription: {e}')

    return redirect('dashboard:settings')

@login_required
@require_http_methods(['POST'])
def start_trial(request):
    # El trial ahora se maneja mediante Checkout Session en Stripe.
    # Redirigir al plan Pro para que el usuario inicie el trial allí.
    messages.info(request, 'Start your free trial by subscribing to the Pro plan.')
    return redirect('dashboard:subscription_plans')
