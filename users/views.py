from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegisterForm, LoginForm, AvatarUpdateForm
from .models import User
import csv
from django.http import HttpResponse


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



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user.is_online = True
            user.save(update_fields=['is_online'])
            login(request, user)
            return redirect('users:profile')
    else:
        form = LoginForm()
    return render(request, 'users/auth.html', {'form': form})


@login_required
def logout_view(request):
    user = request.user
    user.is_online = False
    user.save(update_fields=['is_online'])
    logout(request)
    return redirect('users:login')


@login_required
def profile_view(request):
    user_id = request.GET.get('user')
    if user_id:
        user_obj = get_object_or_404(User, id=user_id)
    else:
        user_obj = request.user

    if request.method == 'POST' and request.user == user_obj:
        form = AvatarUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = AvatarUpdateForm(instance=request.user)

    request.user.update_last_seen()

    return render(request, 'users/profile.html', {
        'user_obj': user_obj,
        'avatar_form': form,
    })



@login_required
def download_user_data(request):
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
