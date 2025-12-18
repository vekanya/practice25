from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegisterForm, LoginForm, AvatarUpdateForm
from .models import User


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
    # Получаем профиль пользователя из GET параметра или текущего пользователя
    user_id = request.GET.get('user')
    if user_id:
        user_obj = get_object_or_404(User, id=user_id)
    else:
        user_obj = request.user

    # Обработка смены аватара (только для своего профиля)
    if request.method == 'POST' and request.user == user_obj:
        form = AvatarUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = AvatarUpdateForm(instance=request.user)

    # Обновляем время последнего визита для текущего пользователя
    request.user.update_last_seen()

    return render(request, 'users/profile.html', {
        'user_obj': user_obj,
        'avatar_form': form,
    })
