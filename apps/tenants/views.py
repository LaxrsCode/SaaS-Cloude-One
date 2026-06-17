from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from apps.tenants.models import Business, BusinessSettings, BusinessMember, Service
from apps.tenants.forms import RegisterBusinessForm, BusinessSettingsForm, ServiceForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# ---- Views Publicas Lading Page ----
@require_http_methods(['GET'])
@login_required
def public_landing_page(request):
    return render(request, 'tenants/public_landing_page.html',{
        'business': request.tenant,
    })

@require_http_methods(['GET'])
@login_required
def tenant_preview(request, slug):
    business = get_object_or_404(Business, slug=slug, is_active=True)
    return render(request, 'tenants/tenant_preview.html', {
        'business': business,
    })


# ---- Views Gestion Dashboard Business ----

@require_http_methods(['POST'])
@login_required
def tenant_register(request):
    if request.method == 'POST':
        form = RegisterBusinessForm(request.POST)
        form.owner = request.user
        if form.is_valid():
            business = form.save()
            messages.success(request,f'"{business.name}" creado existoxamente')
            return redirect('tenants:tenant_settings', slug=business.slug)
    else:
        form = RegisterBusinessForm()

    return render(request, 'tenants/tenant_register.html', {
        'form': form,
    })

@login_required
@require_http_methods(['GET'])
def tenant_list(request):
    businesses = Business.objects.filter(owner=request.user, is_active=True)
    return render(request, 'tenants/tenant_list.html', {
        'businesses': businesses,
    })



@login_required
@require_http_methods(['GET', 'POST'])
def tenant_settings(request, slug):
    business = get_object_or_404(Business, slug=slug, owner=request.user, is_active=True)
    settings = business.settings

    if request.method == 'POST':
        form = BusinessSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada.')
            return redirect('tenants:tenant_settings', slug=business.slug)
    else:
        form = BusinessSettingsForm(instance=settings)

    return render(request, 'tenants/tenant_settings.html', {
        'form': form,
        'business': business,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def tenant_members(request, slug):
    business = get_object_or_404(Business, slug=slug, owner=request.user, is_active=True)
    members = BusinessMember.objects.filter(business=business)

    return render(request, 'tenants/tenant_members.html', {
        'business': business,
        'members': members,
    })


@login_required
@require_http_methods(['POST'])
def tenant_member_invite(request, slug):
    business = get_object_or_404(Business, slug=slug, owner=request.user, is_active=True)
    email = request.POST.get('email')
    role = request.POST.get('role', 'staff')

    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
        BusinessMember.objects.get_or_create(
            business=business,
            user=user,
            defaults={'role': role, 'is_active': True},
        )
        messages.success(request, f'{email} agregado como {role}.')
    except User.DoesNotExist:
        messages.error(request, f'No existe un usuario con el email {email}.')

    return redirect('tenants:tenant_members', slug=business.slug)


# ---- Views Gestion Servicios ----

@login_required
@require_http_methods(['GET'])
def service_list(request, slug):
    business = get_object_or_404(Business, slug=slug, owner=request.user, is_active=True)
    services = business.services.all()
    return render(request, 'tenants/service_list.html', {
        'business': business,
        'services': services,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def service_create(request, slug):
    business = get_object_or_404(Business, slug=slug, owner=request.user, is_active=True)

    if request.method == 'POST':
        form = ServiceForm(request.POST, business=business)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Servicio "{service.name}" creado.')
            return redirect('tenants:service_list', slug=business.slug)
    else:
        form = ServiceForm(business=business)

    return render(request, 'tenants/service_form.html', {
        'form': form,
        'business': business,
        'is_edit': False,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def service_edit(request, slug, service_id):
    business = get_object_or_404(Business, slug=slug, owner=request.user, is_active=True)
    service = get_object_or_404(Service, pk=service_id, business=business)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service, business=business)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Servicio "{service.name}" actualizado.')
            return redirect('tenants:service_list', slug=business.slug)
    else:
        form = ServiceForm(instance=service, business=business)

    return render(request, 'tenants/service_form.html', {
        'form': form,
        'business': business,
        'service': service,
        'is_edit': True,
    })


@login_required
@require_http_methods(['POST'])
def service_delete(request, slug, service_id):
    business = get_object_or_404(Business, slug=slug, owner=request.user, is_active=True)
    service = get_object_or_404(Service, pk=service_id, business=business)
    service.is_active = False
    service.save(update_fields=['is_active'])
    messages.success(request, f'Servicio "{service.name}" desactivado.')
    return redirect('tenants:service_list', slug=business.slug)