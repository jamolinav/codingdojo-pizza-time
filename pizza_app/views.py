from django.shortcuts import render, redirect
from .forms.pizza_app.user import UserForm, UserLoginForm
from .forms.pizza_app.pizza import PizzaForm
from collections import namedtuple
from typing import ContextManager
from django.contrib import messages
from pizza_app.models import *
from datetime import datetime, timezone, timedelta
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from random import randint

# Create your views here.
APP_NAME = 'pizza_app'
def home(request):
    user = None
    if 'logged_user' in request.session:
        users = User.objects.filter(email=request.session['logged_user'])
        if len(users) > 0:
            user = users[0]

    context = {
        'my_pizzas' : Pizza.objects.filter(user=user),
        'pizzas' : Pizza.objects.filter(user__in=User.objects.filter(user_type=UserType.objects.get(type='admin'))),
        'extras' : Extra.objects.all(),
    }
    return render(request, f'{APP_NAME}/index.html', context)
    
def error_404_view(request, exception):
    print('ERROR 404')
    return HttpResponse("Hola, esta página no está disponible o no es válida.")

def register(request):

    if request.method == 'GET':
        '''
        if user.user_type == 'adm':
            user_form = UserForm()
        else:
            user_form = UserAdminForm()
        '''
        user_form = UserForm()
        context = {
            'user_form' : user_form,
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
            request.session['logged_user']      = user.email
            request.session['logged_perfil']    = user.user_type.name
            request.session['logged_user_name'] = user.first_name + ' ' + user.last_name
        else:
            context = {
                'user_form' : UserForm(request.POST),
                'user_login_form' : UserLoginForm(),
            }
            return render(request, f'{APP_NAME}/register.html', context)

    return redirect('home')

def login(request):
    if request.method == 'GET':
        user_form = UserForm()
        user_login_form = UserLoginForm()
        context = {
            'user_form' : user_form,
            'user_login_form' : user_login_form,
            }
        return render(request, f'{APP_NAME}/login.html', context)

    if request.method == 'POST':
        loginForm = UserLoginForm(request.POST)
        if loginForm.is_valid():
            logged_user = loginForm.login(request.POST)
            if logged_user:
                request.session['logged_user_name'] = logged_user.first_name + ' ' + logged_user.last_name
                request.session['logged_user']      = logged_user.email
                request.session['logged_perfil']    = logged_user.user_type.name
                print('logged_user: ', request.session['logged_user'])
                return redirect('home')
            else:
                messages.error(request, 'usuario no existe o clave inválida')
            
        user_form = UserForm()
        user_login_form = UserLoginForm(request.POST)
        context = {
            'user_form' : user_form,
            'user_login_form' : user_login_form,
        }
        return render(request, f'{APP_NAME}/login.html', context)

def logout(request):
    try:
        del request.session['logged_user']
        del request.session['logged_user_name']
        del request.session['logged_perfil']
        del request.session['carrito']
        del request.session['total_carrito']
    except:
        print('Error')
    return redirect('home')

def create_pizza(request):

    if 'logged_user' not in request.session:
        return redirect(login)
    else:
        users = User.objects.filter(email=request.session['logged_user'])
        if len(users) > 0:
            user = users[0]
        else:
            return redirect(login)

    if request.method == 'GET':
        request.session['price'] = 0
        context = {
                'ingredients' : Ingredient.objects.all(),
                'pizza_form' : PizzaForm()
            }
        return render(request, f'{APP_NAME}/create_pizza.html', context)

    if request.method == 'POST':
        print(request.POST)


        errors = Pizza.objects.validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            context = {
                'ingredients' : Ingredient.objects.all(),
                'pizza' : request.POST,
            }
            return render(request, f'{APP_NAME}/create_pizza.html', context)

        pizza = Pizza()
        pizza.name          = request.POST['name']
        pizza.image         = request.POST['image']
        pizza.discount      = request.POST['discount']
        pizza.special_price = request.POST['special_price'] if 'special_price' in request.POST and request.POST['special_price'] != '' else 0
        pizza.user          = user
        pizza.price         = request.POST['price']
        pizza.save()
        # Obtener todos los ingredientes seleccionados
        price = 0
        for key, value in request.POST.items():
            print(key)
            if 'Option' in key:
                values = value.split('|')
                id = values[0]
                options = IngredientOption.objects.filter(id=id)
                if len(options) > 0:
                    option = options[0]
                    price = price + option.price
                    pizza.all_ingredients.add(option)

        pizza.price         = price
        pizza.save()

        return redirect('home')

def get_price(request):
    if request.method == 'POST':
        print(request.POST)
        
        request.session['price'] = 0
        for key, value in request.POST.items():
            print(key)
            if 'Option' in key:
                values = value.split('|')
                id = values[0]
                price = values[1]
                options = IngredientOption.objects.filter(id=id)
                if len(options) > 0:
                    option = options[0]
                price = option.price
                request.session['price'] = request.session['price'] + int(price)

        price = request.session['price']
        return JsonResponse({'price' : price})

    return redirect(create_pizza)

def add_pizza(request, id_pizza):

    if 'logged_user' not in request.session:
        return redirect(login)
    else:
        users = User.objects.filter(email=request.session['logged_user'])
        if len(users) > 0:
            user = users[0]
        else:
            return redirect(login)

    if request.method == 'GET':
        pizzas = Pizza.objects.filter(id=id_pizza)
        if len(pizzas) > 0:
            pizza = pizzas[0]

            #del request.session['carrito']
            #del request.session['total_carrito']
            carrito = []
            total_carrito = 0
            if 'carrito' in request.session:
                carrito = request.session['carrito']
            if 'total_carrito' in request.session:
                total_carrito = request.session['total_carrito']

            total_carrito += pizza.price
            request.session['total_carrito'] = total_carrito
            value = randint(1000000, 9999999)
            carrito.append({'id_carrito': value, 'item': 'pizza', 'id': pizza.id, 'name': pizza.name, 'price': pizza.price, 'image': pizza.image})
            request.session['carrito'] = carrito
            print(carrito)
            

    return redirect('home')

def add_extra(request, id_extra):

    if 'logged_user' not in request.session:
        return redirect(login)
    else:
        users = User.objects.filter(email=request.session['logged_user'])
        if len(users) > 0:
            user = users[0]
        else:
            return redirect(login)

    if request.method == 'GET':
        extras = Extra.objects.filter(id=id_extra)
        if len(extras) > 0:
            extra = extras[0]

            #del request.session['carrito']
            #del request.session['total_carrito']
            carrito = []
            total_carrito = 0
            if 'carrito' in request.session:
                carrito = request.session['carrito']
            if 'total_carrito' in request.session:
                total_carrito = request.session['total_carrito']

            total_carrito += extra.price
            request.session['total_carrito'] = total_carrito
            value = randint(1000000, 9999999)
            carrito.append({'id_carrito': value, 'item': 'extra', 'id': extra.id, 'name': extra.name, 'price': extra.price, 'image': extra.image})
            request.session['carrito'] = carrito
            print(carrito)
            
    return redirect('home')

def ver_carrito(request):

    if 'logged_user' not in request.session:
        return redirect(login)
    else:
        users = User.objects.filter(email=request.session['logged_user'])
        if len(users) > 0:
            user = users[0]
        else:
            return redirect(login)

    if request.method == 'GET':
        items = []
        if 'carrito' in request.session:
            carrito = request.session['carrito']

            for item in carrito:
                print(item)
                print(item['id'])
                items.append(item['id'])

        context = {
            'items' : Pizza.objects.all(),
        }

        return render(request, f'{APP_NAME}/carrito.html', context)

def del_item_carrito(request, carrito_id):

    if 'logged_user' not in request.session:
        return redirect(login)
    else:
        users = User.objects.filter(email=request.session['logged_user'])
        if len(users) > 0:
            user = users[0]
        else:
            return redirect(login)

    if request.method == 'GET':
        items = []
        if 'carrito' in request.session:
            carrito = request.session['carrito']

            del request.session['carrito']
            del request.session['total_carrito']

            total_carrito = 0
            for item_carrito in carrito:
                if item_carrito['id_carrito'] == int(carrito_id):
                    print('elimina item')
                else:
                    items.append(item_carrito)
                    total_carrito += item_carrito['price']
                    
            request.session['total_carrito'] = total_carrito
            request.session['carrito'] = items

    return redirect(ver_carrito)

def del_pizza(request, pizza_id):

    if 'logged_user' not in request.session:
        return redirect(login)
    else:
        users = User.objects.filter(email=request.session['logged_user'])
        if len(users) > 0:
            user = users[0]
        else:
            return redirect(login)

    if request.method == 'GET':
        pizzas = Pizza.objects.filter(id=pizza_id)
        print(pizza_id)
        print(pizzas)
        if len(pizzas) > 0:
            pizza = pizzas[0]

        if pizza.user == user:
            pizza.delete()
            messages.error(request, 'Pizza eliminada!')
        else:
            messages.error(request, 'Pizza no puede ser eliminada')
            

    return redirect('home')