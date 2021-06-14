from django.shortcuts import render, redirect
from .forms.pizza_app.user import UserForm, UserLoginForm
from .forms.pizza_app.pizza import PizzaForm
from .forms.pizza_app.address import AddressForm
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

    users_type = UserType.objects.filter(type='admin')
    if len(users_type) > 0:
        user_type = users_type[0]
    else:
        user_type = None

    context = {
        'my_pizzas' : Pizza.objects.filter(user=user),
        'pizzas' : Pizza.objects.filter(user__in=User.objects.filter(user_type=user_type)),
        'extras' : Extra.objects.all(),
    }
    return render(request, f'{APP_NAME}/index.html', context)
    
def error_404_view(request, exception):
    print('ERROR 404')
    return HttpResponse("Hola, esta página no está disponible o no es válida.")

def register(request):

    if request.method == 'GET':
        user_form = UserForm()
        context = {
            'user_form' : user_form,
        }
        return render(request, f'{APP_NAME}/register.html', context)
    
    if request.method == 'POST':
        users_type = UserType.objects.all()
        if len(users_type) < 1:
            type_admin = UserType.objects.create(name='Administrador', type='admin')
            type_user = UserType.objects.create(name='Empleado', type='user')
            type_client = UserType.objects.create(name='Cliente', type='client')
        else:
            type_client = UserType.objects.get(name='Cliente', type='client')

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
            users = User.objects.all()
            if len(users) > 0:
                user = user_form.save(commit=False)
                user.user_type = type_client
                user.save()
            else:
                user = user_form.save(commit=False)
                user.user_type = UserType.objects.get(type='admin')
                user.save()

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

        if 'name' not in request.POST or 'image' not in request.POST or 'discount' not in request.POST or 'special_price' not in request.POST or 'price' not in request.POST:
            messages.error(request, 'Falta información para crear Pizza')
            context = {
                'ingredients' : Ingredient.objects.all(),
                'pizza' : request.POST,
            }
            return render(request, f'{APP_NAME}/create_pizza.html', context)

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

        if price <= 0:
            messages.error(request, 'Falta información ingredientes')
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
        pizza.price         = price
        pizza.save()

        for key, value in request.POST.items():
            print(key)
            if 'Option' in key:
                values = value.split('|')
                id = values[0]
                options = IngredientOption.objects.filter(id=id)
                if len(options) > 0:
                    option = options[0]
                    pizza.all_ingredients.add(option)

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
        
        tax = 0
        delivery = 0
        if 'carrito' in request.session:
            carrito = request.session['carrito']
            total_carrito = 0

            for item in carrito:
                total_carrito += item['price']
                
            tax = round(total_carrito / 5)
            delivery = round(total_carrito / 10)
            request.session['tax'] = tax
            request.session['delivery'] = delivery
            request.session['total_carrito'] = total_carrito + tax + delivery

        context = {
            'items' : Pizza.objects.all(),
            'addresses' : Address.objects.filter(user=user),
            'orders' : Order.objects.filter(user=user),
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

def create_address(request):

    if 'logged_user' not in request.session:
        return redirect(login)
    else:
        users = User.objects.filter(email=request.session['logged_user'])
        if len(users) > 0:
            user = users[0]
        else:
            return redirect(login)

    regiones = Region.objects.all()
    if len(regiones) < 1:
        region = Region.objects.create(name='Metropolitana')

    cities = City.objects.all()
    if len(cities) < 1:
        city = City.objects.create(name='Santiago', region=Region.objects.get(name='Metropolitana'))
    
    comunas = Comuna.objects.all()
    if len(comunas) < 1:
        comuna = Comuna.objects.create(name='Santiago Centro', city=City.objects.get(name='Santiago'))
        comuna = Comuna.objects.create(name='La Reina', city=City.objects.get(name='Santiago'))
        comuna = Comuna.objects.create(name='Providencia', city=City.objects.get(name='Santiago'))
        comuna = Comuna.objects.create(name='Las Condes', city=City.objects.get(name='Santiago'))
        comuna = Comuna.objects.create(name='Recoleta', city=City.objects.get(name='Santiago'))
        comuna = Comuna.objects.create(name='Estacion Central', city=City.objects.get(name='Santiago'))
        comuna = Comuna.objects.create(name='La Florida', city=City.objects.get(name='Santiago'))
        comuna = Comuna.objects.create(name='Puente Alto', city=City.objects.get(name='Santiago'))

    if request.method == 'GET':
        context = {
                'address_form' : AddressForm(),
                'addresses' : Address.objects.filter(user=user),
            }
        return render(request, f'{APP_NAME}/address.html', context)
    
    if request.method == 'POST':
        print(request.POST)

        address_form = AddressForm(request.POST)

        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = user
            address.save()
        else:
            context = {
                'address_form' : AddressForm(request.POST)
            }
            return render(request, f'{APP_NAME}/address.html', context)

    return redirect('ver_carrito')

def make_purchases(request):

    if 'logged_user' not in request.session:
        return redirect(login)
    else:
        users = User.objects.filter(email=request.session['logged_user'])
        if len(users) > 0:
            user = users[0]
        else:
            return redirect(login)

    if request.method == 'POST':
        print(request.POST)
        
        if 'carrito' in request.session:
            carrito = request.session['carrito']
            if len(carrito) > 0:
                if 'addresses' not in request.POST:
                    messages.error(request, 'Seleccione una dirección de envío')
                else:
                    addresses = Address.objects.filter(id=int(request.POST['addresses']))
                    if len(addresses) > 0:

                        address = addresses[0]

                        order = Order()
                        order.user = user
                        order.address = address
                        order.total = request.session['total_carrito']
                        order.total_discount = 0
                        order.fee_delivery = request.session['delivery']
                        order.tax = request.session['tax']
                        order.save()

                        for item_carrito in carrito:
                            print(item_carrito)
                            if item_carrito['item'] == 'pizza':
                                pizza = Pizza.objects.get(id=item_carrito['id'])
                                details = DetailPizzaOrder()
                                details.order = order
                                details.quantity = 1
                                details.save()
                                details.all_pizzas.add(pizza)
                            if item_carrito['item'] == 'extra':
                                extra = Extra.objects.get(id=item_carrito['id'])
                                details = DetailExtraOrder()
                                details.order = order
                                details.quantity = 1
                                details.save()
                                details.all_extras.add(extra)

                        del request.session['carrito']
                        del request.session['total_carrito']
                        del request.session['tax']
                        del request.session['delivery']
                    else:
                        messages.error(request, 'Seleccione una dirección de envío')
            else:
                messages.error(request, 'No hay Items para generar la compra')
        else:
            messages.error(request, 'No hay Items para generar la compra')

    return redirect('ver_carrito')

def make_pizzas_data(request):
    # el usuario inicial es un Administrador
    users = User.objects.all()
    if len(users) < 1:
        messages.error(request, 'No hay usuarios registrados, registrese para quedar como Administrador y luego precargar datos.')
        return redirect('register_pizza_app')
    else:
        user = User.objects.get(user_type=UserType.objects.get(type='admin'))

    # Crea los ingredientes
    ing = Ingredient.objects.create(name='Tamaño', price=2000, discount=False, special_price=0, optional=True, orden=0, multiple_option=False)
    opt = IngredientOption.objects.create(option='Extra Grande', price=1200, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Familiar', price=1000, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Mediana', price=900, discount=False, special_price=0, orden=0, ingredient=ing)

    # Tipo de Masa
    ing = Ingredient.objects.create(name='Tipo de Masa', price=2000, discount=False, special_price=0, optional=True, orden=0, multiple_option=False)
    opt = IngredientOption.objects.create(option='Tradicional', price=2000, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Delgada', price=1500, discount=False, special_price=0, orden=0, ingredient=ing)

    # Carnes
    ing = Ingredient.objects.create(name='Carnes', price=2000, discount=False, special_price=0, optional=False, orden=0, multiple_option=True)
    opt = IngredientOption.objects.create(option='Tocino', price=800, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Jamón', price=800, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Peperoni', price=800, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Pollo', price=800, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Carne', price=800, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Lomito', price=800, discount=False, special_price=0, orden=0, ingredient=ing)

   # Vegetales
    ing = Ingredient.objects.create(name='Vegetales', price=2000, discount=False, special_price=0, optional=False, orden=0, multiple_option=True)
    opt = IngredientOption.objects.create(option='Tomate', price=600, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Champiñon', price=600, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Choclo', price=600, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Cebolla', price=600, discount=False, special_price=0, orden=0, ingredient=ing)
    opt = IngredientOption.objects.create(option='Aceituna', price=600, discount=False, special_price=0, orden=0, ingredient=ing)

    # Crea Pizza Napolitana
    pizza = Pizza.objects.create(name='Napolitana', image='napolitana.jpeg', user=user, price=0, discount=False, special_price=0)

    ingredient1 = IngredientOption.objects.filter(ingredient=Ingredient.objects.get(name='Tipo de Masa')).get(option='Tradicional')
    ingredient2 = IngredientOption.objects.filter(ingredient=Ingredient.objects.get(name='Tamaño')).get(option='Familiar')
    ingredient3 = IngredientOption.objects.filter(ingredient=Ingredient.objects.get(name='Carnes')).get(option='Jamón')
    ingredient4 = IngredientOption.objects.filter(ingredient=Ingredient.objects.get(name='Vegetales')).get(option='Tomate')

    pizza.all_ingredients.add(ingredient1)
    pizza.all_ingredients.add(ingredient2)
    pizza.all_ingredients.add(ingredient3)
    pizza.all_ingredients.add(ingredient4)
    pizza.price = ingredient1.price + ingredient2.price + ingredient3.price + ingredient4.price
    pizza.save()

   # Crea Pizza Italiana
    pizza = Pizza.objects.create(name='Italiana', image='italiana.jpeg', user=user, price=0, discount=False, special_price=0)

    ingredient1 = IngredientOption.objects.filter(ingredient=Ingredient.objects.get(name='Tipo de Masa')).get(option='Tradicional')
    ingredient2 = IngredientOption.objects.filter(ingredient=Ingredient.objects.get(name='Tamaño')).get(option='Familiar')
    ingredient3 = IngredientOption.objects.filter(ingredient=Ingredient.objects.get(name='Carnes')).get(option='Peperoni')
    ingredient4 = IngredientOption.objects.filter(ingredient=Ingredient.objects.get(name='Vegetales')).get(option='Champiñon')
    ingredient5 = IngredientOption.objects.filter(ingredient=Ingredient.objects.get(name='Vegetales')).get(option='Cebolla')

    pizza.all_ingredients.add(ingredient1)
    pizza.all_ingredients.add(ingredient2)
    pizza.all_ingredients.add(ingredient3)
    pizza.all_ingredients.add(ingredient4)
    pizza.all_ingredients.add(ingredient5)
    pizza.price = ingredient1.price + ingredient2.price + ingredient3.price + ingredient4.price + ingredient5.price
    pizza.save()

    return redirect('home')

def make_extras_data(request):
    users = User.objects.all()
    if len(users) < 1:
        messages.error(request, 'No hay usuarios registrados, registrese para quedar como Administrador y luego precargar datos.')
        return redirect('register_pizza_app')

    extra1 = Extra.objects.create(name='Alitas de Pollo', price=4500, image='alitas.jpeg', discount=False, special_price=0)
    extra2 = Extra.objects.create(name='Palitos de Ajo', price=2800, image='palitos.jpeg', discount=False, special_price=0)

    return redirect('home')

def del_data(request):
    delete = Order.objects.all().delete()
    delete = Extra.objects.all().delete()
    delete = Pizza.objects.all().delete()
    delete = Ingredient.objects.all().delete()
    delete = Region.objects.all().delete()
    delete = Address.objects.all().delete()
    delete = User.objects.all().delete()
    delete = UserType.objects.all().delete()

    del request.session['logged_user']
    del request.session['logged_user_name']
    del request.session['logged_perfil']
    del request.session['carrito']
    del request.session['total_carrito']
    
    return redirect('home')