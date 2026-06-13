from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from apps.tenants.models import Business

# Create your views here.

@require_http_methods(['GET'])
def public_landing_page(request):
    return render(request, 'tenants/public_landing_page.html',{
        'business': request.tenant,
    })

@require_http_methods(['GET'])
def tenant_preview(request, slug):
    business = get_object_or_404(Business, slug=slug, is_active=True)
    return render(request, 'tenants/tenant_preview.html', {
        'business': business,
    })