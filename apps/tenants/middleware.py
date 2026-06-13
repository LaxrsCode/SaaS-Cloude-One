from django.http import Http404
from django.conf import settings


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]

        request.tenant = None

        RESERVED_SUBDOMAINS = frozenset({'www', 'api', 'admin'})

        if host != settings.MAIN_DOMAIN and host.endswith('.' + settings.MAIN_DOMAIN):
            subdomain = host.removesuffix('.' + settings.MAIN_DOMAIN)
            if subdomain and subdomain not in RESERVED_SUBDOMAINS:
                from apps.tenants.models import Business
                try:
                    request.tenant = Business.objects.get(
                        subdomain=subdomain, is_active=True
                    )
                    request.urlconf = 'apps.tenants.public_urls'
                except Business.DoesNotExist:
                    raise Http404("Business not found")


        return self.get_response(request)