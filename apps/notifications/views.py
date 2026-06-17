from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(['GET'])
def notification_list(request):
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
@require_http_methods(['POST'])
def notification_mark_read(request, notification_id):
    notification = request.user.notifications.filter(id=notification_id).first()
    if notification:
        notification.is_read = True
        notification.save()
    return redirect('notifications:notification_list')


@login_required
@require_http_methods(['POST'])
def notification_mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications:notification_list')


@login_required
@require_http_methods(['GET'])
def notification_unread_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': count})
