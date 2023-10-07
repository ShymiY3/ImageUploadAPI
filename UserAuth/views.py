from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from . import forms



def user_sign_in(request):
    if request.user.is_authenticated:
        return redirect(reverse('api-root'))
    
    
    if request.method == 'POST':
        form = forms.LoginForm(request, request.POST)
        if not form.is_valid():
            return redirect(reverse('sign_in'))    
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        remember_me = form.cleaned_data.get('remember_me')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            return redirect(reverse('api-root'))
        else:
            return redirect(reverse('sign_in'))
        
    form = forms.LoginForm()
    
    return render(request, 'login.html', context={'form': form})

def user_sign_up(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if not form.is_valid():
            return redirect(reverse('sign_up'))    
        form.save()
        return redirect(reverse('sign_in'))
        
    form = forms.RegistrationForm()
    
    return render(request, 'register.html', context={'form': form})

def user_log_out(request):
    logout(request)
    return redirect(reverse('sign_in'))