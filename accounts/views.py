from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def register_view(request):
    if request.method == 'POST':
        username  = request.POST.get('username')
        password  = request.POST.get('password')
        full_name = request.POST.get('full_name')
        role      = request.POST.get('role', 'engineer')
        email     = request.POST.get('email', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            username=username,
            password=password,
            full_name=full_name,
            email=email,
            role=role,
        )
        messages.success(request, f'User {username} created successfully!')
        return redirect('accounts:login')
    return render(request, 'accounts/register.html')