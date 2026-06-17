from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_allauth_email(subject, body, recipient_list, from_email=None, html_body=None):
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(subject, body, from_email, recipient_list)
    if html_body:
        msg.attach_alternative(html_body, 'text/html')
    msg.send()
