from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.dashboard.models import SubscriptionPlan
from .models import StripeCustomer
from .services import AccessService, SubscriptionService


@login_required
def subscription_page(request):
    sub_info = AccessService.get_subscription_status(request.user)
    plans = SubscriptionPlan.objects.filter(is_active=True, price__gt=0)
    has_stripe_customer = StripeCustomer.objects.filter(user=request.user).exists()
    return render(request, 'subscriptions/subscription.html', {
        'subscription': sub_info,
        'plans': plans,
        'has_stripe_customer': has_stripe_customer,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    })


@login_required
@require_POST
def create_checkout_session(request):
    plan_slug = request.POST.get('plan') or request.GET.get('plan', 'pro')
    plan = get_object_or_404(SubscriptionPlan, slug=plan_slug, is_active=True)

    if not plan.stripe_price_id:
        messages.error(request, 'This plan is not configured for billing yet.')
        return redirect('subscriptions:subscription_page')

    success_url = request.build_absolute_uri(
        reverse('dashboard:settings') + '?session_id={CHECKOUT_SESSION_ID}'
    )
    cancel_url = request.build_absolute_uri(reverse('dashboard:subscription_plans'))

    session = SubscriptionService.create_checkout_session(
        user=request.user,
        plan=plan,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return redirect(session.url)


@login_required
def customer_portal(request):
    if not StripeCustomer.objects.filter(user=request.user).exists():
        messages.warning(request, 'No billing account found. Subscribe to a plan first.')
        return redirect('dashboard:subscription_plans')

    return_url = request.build_absolute_uri(reverse('dashboard:settings'))
    session = SubscriptionService.create_portal_session(
        user=request.user,
        return_url=return_url,
    )
    return redirect(session.url)

