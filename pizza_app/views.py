from django.shortcuts import render, redirect
from .forms.pizza_app.user import UserForm, UserLoginForm
from collections import namedtuple
from typing import ContextManager
from django.contrib import messages
from pizza_app.models import *
from datetime import datetime, timezone, timedelta
from django.http import HttpResponse, JsonResponse
from django.db.models import Count

# Create your views here.
APP_NAME = 'pizza_app'
def home(request):
    return render(request, f'{APP_NAME}/index.html')
    
def error_404_view(request, exception):
    print('ERROR 404')
    return HttpResponse("Hola, esta página no está disponible o no es válida.")

def register(request):

    if request.method == 'GET':
        user_form = UserForm()
        user_login_form = UserLoginForm()
        context = {
            'user_form' : user_form,
            'user_login_form' : user_login_form,
        }
        return render(request, f'{APP_NAME}/register.html', context)
    
    if request.method == 'POST':
        print(request.POST)
        errors = User.objects.validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            context = {
                'user_form' : UserForm(request.POST),
                'user_login_form' : UserLoginForm(),
            }
            return render(request, f'{APP_NAME}/register.html', context)

        if User.ifExists(request.POST['email']):
            messages.error(request, 'Usuario ya existe')
            context = {
                'user_form' : UserForm(request.POST),
                'user_login_form' : UserLoginForm(),
            }
            return render(request, f'{APP_NAME}/register.html', context)

        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            request.session['logged_user'] = user.email
            request.session['logged_user_name'] = user.first_name + ' ' + user.last_name
        else:
            context = {
                'user_form' : UserForm(request.POST),
                'user_login_form' : UserLoginForm(),
            }
            return render(request, f'{APP_NAME}/register.html', context)

    return redirect('wishes')

def login(request):
    if request.method == 'GET':
        user_form = UserForm()
        user_login_form = UserLoginForm()
        context = {
            'user_form' : user_form,
            'user_login_form' : user_login_form,
            }
        return render(request, f'{APP_NAME}/register.html', context)

    if request.method == 'POST':
        loginForm = UserLoginForm(request.POST)
        if loginForm.is_valid():
            logged_user = loginForm.login(request.POST)
            if logged_user:
                request.session['logged_user_name'] = logged_user.first_name + ' ' + logged_user.last_name
                request.session['logged_user'] = logged_user.email
                print('logged_user: ', request.session['logged_user'])
                return redirect('wishes')
            else:
                messages.error(request, 'usuario no existe o clave inválida')
            
        user_form = UserForm()
        user_login_form = UserLoginForm(request.POST)
        context = {
            'user_form' : user_form,
            'user_login_form' : user_login_form,
        }
        return render(request, f'{APP_NAME}/register.html', context)

def logout(request):
    try:
        del request.session['logged_user']
        del request.session['logged_user_name']
    except:
        print('Error')
    return redirect('home')

