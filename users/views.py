import json
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import redirect
from app import settings
from .forms import RegisterForm, LoginForm, AvatarUpdateForm
from .models import User
import csv
from django.http import HttpResponse, JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework_simplejwt.tokens import UntypedToken  
from django.contrib.auth import get_user_model
User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)  
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('posts:home')
    else:
        form = RegisterForm()
    return render(request, 'users/reg.html', {'form': form})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user:
                user.is_online = True
                user.save(update_fields=['is_online'])
                
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    'success': True,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'detail': 'Неверный логин или пароль'
                }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'detail': 'Неверный JSON'}, status=400)
    
    return render(request, 'users/auth.html')

def logout_view(request):
    user = request.user
    user.is_online = False
    user.save(update_fields=['is_online'])
    logout(request)
    return redirect('users:login')

def profile_view(request):
    user_id = request.GET.get('user')
    if user_id:
        user_obj = get_object_or_404(User, id=user_id)
    else:
        user_obj = request.user

    user_obj.is_online = True
    user_obj.last_seen = timezone.now()
    user_obj.save(update_fields=['is_online', 'last_seen'])
    
    print(f"DEBUG: {user_obj.username} FORCED ONLINE: is_online={user_obj.is_online}")

    current_user = None
    
    jwt_user_id = request.GET.get('jwt_user_id')
    if jwt_user_id:
        try:
            current_user = get_object_or_404(User, id=jwt_user_id)
            print(f"JWT from GET: {current_user.username}")
        except:
            pass
    
    elif request.user.is_authenticated and hasattr(request.user, 'id'):
        current_user = request.user
        print(f"Django session user: {current_user.username}")
    
    if not current_user and user_obj == request.user:
        current_user = user_obj
        print(f"Own profile: current_user = {current_user.username}")

    if request.method == 'POST' and current_user == user_obj:
        form = AvatarUpdateForm(request.POST, request.FILES, instance=user_obj)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    elif current_user == user_obj:
        form = AvatarUpdateForm(instance=user_obj)
    else:
        form = AvatarUpdateForm()

    return render(request, 'users/profile.html', {
        'user_obj': user_obj,
        'avatar_form': form,
        'current_user': current_user,
        'is_own_profile': current_user == user_obj,  
        'is_admin': user_obj.is_staff or (current_user and current_user.is_staff),
    })


def download_user_data(request):
    if request.user.is_authenticated and hasattr(request.user, 'username'):
        user = request.user
    else:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.first()
        print(f"Fallback user: {user.username}")
    
    user = request.user
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="my_data_{user.username}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Phone', 'Posts Count', 'Comments Count'])
    
    
    writer.writerow([
        user.username,
        user.email or '',
        user.phone or '',
        user.posts.count(),
        user.comment_set.count()
    ])
    
    
    writer.writerow([])  
    writer.writerow(['ПОСТЫ:'])
    for post in user.posts.all():
        writer.writerow([
            f'Пост ID: {post.id}',
            post.text[:100],  
            post.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    
    writer.writerow([])  
    writer.writerow(['КОММЕНТАРИИ:'])
    for comment in user.comment_set.all():
        writer.writerow([
            f'Комментарий к посту ID: {comment.post.id}',
            comment.text[:100],
            comment.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response
