from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_subscription_confirmation_email(user_email, plan_name):
    send_mail(
        subject=f"Subscription Confirmed - {plan_name}",
        message=f"Your subscription to the {plan_name} plan has been confirmed. Thank you!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )


@shared_task
def send_subscription_cancellation_email(user_email):
    send_mail(
        subject="Subscription Cancelled",
        message="Your subscription has been cancelled. We're sorry to see you go!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )


@shared_task
def send_trial_started_email(user_email):
    send_mail(
        subject="Welcome to Your Free Trial!",
        message="Your 14-day free trial has started. Explore all premium features!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )
