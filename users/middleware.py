from django.utils import timezone
from rest_framework_simplejwt.tokens import UntypedToken
from django.shortcuts import get_object_or_404
from .models import User

class OnlineStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            try:
                token = auth_header[7:]
                token_obj = UntypedToken(token)
                user_id = token_obj['user_id']
                user = get_object_or_404(User, id=user_id)
                user.is_online = True
                user.update_last_seen()
                user.save(update_fields=['is_online', 'last_seen'])
                request.user = user  # Для шаблонов
            except:
                pass
        
        response = self.get_response(request)
        return response
