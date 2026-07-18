from datetime import datetime

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.dashboard.models import SubscriptionPlan, UserSettings

from .models import StripeCustomer, Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

User = get_user_model()


class SubscriptionService:
    """Stripe subscription business logic."""

    @staticmethod
    def get_or_create_customer(user):
        try:
            return StripeCustomer.objects.get(user=user)
        except StripeCustomer.DoesNotExist:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name() or user.email,
                metadata={'user_id': user.id},
            )
            return StripeCustomer.objects.create(
                user=user,
                stripe_customer_id=customer.id,
            )

    @staticmethod
    def create_checkout_session(user, plan, success_url, cancel_url):
        stripe_customer = SubscriptionService.get_or_create_customer(user)

        subscription_data = {
            'metadata': {
                'user_id': user.id,
                'plan_slug': plan.slug,
            },
        }
        if plan.trial_days:
            subscription_data['trial_period_days'] = plan.trial_days

        session = stripe.checkout.Session.create(
            customer=stripe_customer.stripe_customer_id,
            mode='subscription',
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            metadata={
                'user_id': user.id,
                'plan_slug': plan.slug,
            },
            subscription_data=subscription_data,
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_collection='always',
        )
        return session

    @staticmethod
    def create_portal_session(user, return_url):
        stripe_customer = StripeCustomer.objects.get(user=user)
        return stripe.billing_portal.Session.create(
            customer=stripe_customer.stripe_customer_id,
            return_url=return_url,
        )

    @staticmethod
    def sync_subscription_from_stripe(subscription_data):
        stripe_sub_id = subscription_data['id']
        customer_id = subscription_data['customer']
        metadata = subscription_data.get('metadata', {})

        price_id = subscription_data['items']['data'][0]['price']['id']
        plan = SubscriptionPlan.objects.filter(stripe_price_id=price_id).first()

        user_id = metadata.get('user_id')
        if user_id:
            user = User.objects.get(id=int(user_id))
        else:
            sc = StripeCustomer.objects.get(stripe_customer_id=customer_id)
            user = sc.user

        stripe_customer_obj = StripeCustomer.objects.get(stripe_customer_id=customer_id)

        from datetime import timezone as py_timezone

        def ts_to_dt(timestamp):
            return datetime.fromtimestamp(timestamp, tz=py_timezone.utc) if timestamp else None

        subscription, _created = Subscription.objects.update_or_create(
            stripe_subscription_id=stripe_sub_id,
            defaults={
                'user': user,
                'stripe_customer': stripe_customer_obj,
                'plan': plan,
                'status': subscription_data['status'],
                'current_period_start': ts_to_dt(subscription_data.get('current_period_start')),
                'current_period_end': ts_to_dt(subscription_data.get('current_period_end')),
                'trial_start': ts_to_dt(subscription_data.get('trial_start')),
                'trial_end': ts_to_dt(subscription_data.get('trial_end')),
                'cancel_at_period_end': subscription_data.get('cancel_at_period_end', False),
                'canceled_at': ts_to_dt(subscription_data.get('canceled_at')),
            },
        )
        SubscriptionService._sync_user_settings(subscription)
        return subscription

    @staticmethod
    def _sync_user_settings(subscription):
        user_settings, _ = UserSettings.objects.get_or_create(user=subscription.user)
        user_settings.subscription_plan = subscription.plan

        status_map = {
            'active': 'active',
            'trialing': 'trial',
            'canceled': 'cancelled',
            'past_due': 'active',
            'unpaid': 'inactive',
            'incomplete': 'inactive',
            'incomplete_expired': 'cancelled',
        }
        user_settings.subscription_status = status_map.get(subscription.status, 'inactive')
        user_settings.subscription_start_date = subscription.current_period_start
        user_settings.subscription_end_date = subscription.current_period_end
        user_settings.trial_end_date = subscription.trial_end
        user_settings.save()

    @staticmethod
    def cancel_at_period_end(subscription):
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True,
        )
        subscription.cancel_at_period_end = True
        subscription.save()

class AccessService:
    """Subscription-based access control."""

    ALLOWED_STATUSES = {'active', 'trialing'}

    @staticmethod
    def user_has_access(user):
        return Subscription.objects.filter(
            user=user, status__in=AccessService.ALLOWED_STATUSES
        ).exists()

    @staticmethod
    def get_current_subscription(user):
        return Subscription.objects.filter(
            user=user, status__in=AccessService.ALLOWED_STATUSES
        ).first()

    @staticmethod
    def get_subscription_status(user):
        sub = Subscription.objects.filter(user=user).order_by('-created_at').first()
        if not sub:
            return {
                'has_subscription': False,
                'status': 'none',
                'plan_name': 'Free',
                'is_active': False,
                'is_trialing': False,
                'is_trial': False,
                'end_date': None,
                'trial_end_date': None,
                'cancel_at_period_end': False,
            }
        return {
            'has_subscription': True,
            'status': sub.status,
            'plan_name': sub.plan.name if sub.plan else 'Unknown',
            'is_active': sub.status == 'active',
            'is_trialing': sub.status == 'trialing',
            'is_trial': sub.status == 'trialing',
            'end_date': sub.current_period_end,
            'trial_end_date': sub.trial_end,
            'cancel_at_period_end': sub.cancel_at_period_end,
        }
