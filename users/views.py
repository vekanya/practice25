from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from .models import User
from .forms import AvatarUpdateForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:profile')
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
    if request.method == 'POST':
        form = AvatarUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = AvatarUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {
        'user_obj': request.user,
        'avatar_form': form,
    })
