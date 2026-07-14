from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET'])
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "Sitemap: https://yourdomain.com/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


@require_http_methods(['GET'])
def home(request):
    features = [
        {
            'icon': 'building',
            'title': 'Multi-tenant real',
            'description': 'Cada negocio trabaja con sus propios datos, usuarios y configuración dentro de un mismo sistema centralizado.',
        },
        {
            'icon': 'calendar-check',
            'title': 'Reservas en tiempo real',
            'description': 'El sistema controla horarios, disponibilidad y solicitudes para evitar citas duplicadas o huecos manuales.',
        },
        {
            'icon': 'globe',
            'title': 'Landing pública automática',
            'description': 'Cada negocio puede tener una página pública para mostrar servicios, horarios, ubicación y botón de reserva.',
        },
        {
            'icon': 'users',
            'title': 'Clientes y servicios centralizados',
            'description': 'Toda la información comercial queda ordenada en un solo panel para consultar historial, notas y catálogo.',
        },
        {
            'icon': 'bell',
            'title': 'Recordatorios automáticos',
            'description': 'Las notificaciones ayudan a reducir ausencias y mantener una comunicación más clara con cada cliente.',
        },
        {
            'icon': 'shield-halved',
            'title': 'Seguridad y suscripciones',
            'description': 'Autenticación, planes de pago y aislamiento de datos para escalar con confianza sin mezclar información.',
        },
    ]

    return render(request, 'landing/home.html', {
        'features': features,
    })


@require_http_methods(['GET'])
def pricing(request):
    return render(request, 'landing/pricing.html')


@require_http_methods(['GET'])
def features(request):
    return render(request, 'landing/features.html')
