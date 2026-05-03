from django.urls import path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def notification_list(request):
    notifications = request.user.notifications.all()[:50]
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, "notifications/list.html", {"notifications": notifications})

app_name = "notifications"
urlpatterns = [
    path("", notification_list, name="list"),
]
