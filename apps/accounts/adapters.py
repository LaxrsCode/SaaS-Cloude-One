from allauth.account.adapter import DefaultAccountAdapter
from allauth.core import context as allauth_context
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction

from .tasks import send_allauth_email


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        request = allauth_context.request
        ctx = {
            'request': request,
            'email': email,
            'current_site': get_current_site(request),
        }
        ctx.update(context)
        msg = self.render_mail(template_prefix, email, ctx)

        html_body = None
        if getattr(msg, 'alternatives', None):
            for content, mimetype in msg.alternatives:
                if mimetype == 'text/html':
                    html_body = content
                    break
        elif getattr(msg, 'content_subtype', None) == 'html':
            html_body = msg.body

        def enqueue():
            send_allauth_email.delay(
                subject=msg.subject,
                body=msg.body,
                recipient_list=list(msg.to),
                from_email=msg.from_email,
                html_body=html_body,
            )

        transaction.on_commit(enqueue)
