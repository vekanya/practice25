# users/middleware.py
from django.utils import timezone
import users.models

class OnlineStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            users.models.User.objects.filter(id=request.user.id).update(
                is_online=True,
                last_seen=timezone.now()
            )
        
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            # Ставим оффлайн через 5 минут бездействия
            users.models.User.objects.filter(id=request.user.id).update(
                is_online=False
            )
        
        return response
