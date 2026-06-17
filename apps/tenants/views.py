from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods

from .models import Business, BusinessMember, BusinessSettings


@login_required
@require_http_methods(['GET'])
def business_list(request):
    businesses = request.user.owned_businesses.all()
    memberships = request.user.business_memberships.filter(is_active=True)
    return render(request, 'tenants/business_list.html', {
        'owned_businesses': businesses,
        'memberships': memberships,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def business_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', 'otro')
        if not name:
            messages.error(request, 'Business name is required.')
            return render(request, 'tenants/business_form.html', {'categories': Business.CATEGORY_CHOICES})
        slug = slugify(name)
        if Business.objects.filter(slug=slug).exists():
            slug = f'{slug}-{Business.objects.filter(slug__startswith=slug).count()}'
        business = Business.objects.create(
            name=name,
            slug=slug,
            category=category,
            owner=request.user,
        )
        BusinessSettings.objects.create(business=business)
        BusinessMember.objects.create(
            business=business,
            user=request.user,
            role='owner',
        )
        messages.success(request, f'Business "{name}" created successfully.')
        return redirect('tenants:business_detail', slug=business.slug)
    return render(request, 'tenants/business_form.html', {'categories': Business.CATEGORY_CHOICES})


@login_required
@require_http_methods(['GET'])
def business_detail(request, slug):
    business = get_object_or_404(Business, slug=slug)
    is_member = business.members.filter(user=request.user, is_active=True).exists()
    if not is_member and not request.user.is_superuser:
        messages.error(request, 'You do not have access to this business.')
        return redirect('tenants:business_list')
    members = business.members.select_related('user').all()
    services = business.services.filter(is_active=True)
    staff = business.staff.filter(is_active=True)
    return render(request, 'tenants/business_detail.html', {
        'business': business,
        'members': members,
        'services': services,
        'staff': staff,
    })


@login_required
@require_http_methods(['POST'])
def business_remove_member(request, slug, member_id):
    business = get_object_or_404(Business, slug=slug, owner=request.user)
    member = get_object_or_404(BusinessMember, id=member_id, business=business)
    if member.role == 'owner':
        messages.error(request, 'Cannot remove the owner.')
    else:
        member.delete()
        messages.success(request, 'Member removed.')
    return redirect('tenants:business_detail', slug=business.slug)
