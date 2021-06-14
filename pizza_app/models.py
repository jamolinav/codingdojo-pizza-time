from collections import namedtuple
from typing import ItemsView
from django.db import models
from datetime import datetime, timedelta
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
import re
from django.db.models.base import Model
from django.db.models.deletion import get_candidate_relations_to_delete
from django.db.models.fields import CommaSeparatedIntegerField
import bcrypt

MIN_FIELD_LENGHT = 3

def ValidarLongitudMinima(cadena):
    if len(cadena) < MIN_FIELD_LENGHT:
        raise ValidationError(
            f"Deberia tener mas de {MIN_FIELD_LENGHT} caracteres")

class UserManager(models.Manager):
    def validator(self, postData):
        errors  = {}
        
        errorsEmail = self.checkEmail(postData['email'])
        if len(errorsEmail) > 0:
            errors['email'] = errorsEmail

        passw = postData['password']
        if len(passw) < 3:
            errors['password'] = 'Clave de al menos 3 caracteres'

        return errors


    def checkEmail(self, email):
        errors  = {}
        EMAIL_REGEX = re.compile(r'^[A-Za-z0-9.+_-]+@[A-Za-z0-9.+_-]+\.[A-Za-z]+$')
        if not EMAIL_REGEX.match(email):
            errors['email'] = 'Correo Inválido'
        return errors

class UserType(models.Model):
    name            = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    type            = models.CharField(max_length=45, validators=[ValidarLongitudMinima])

    def __str__(self):
        return '%s' % (self.name)

class User(models.Model):
    first_name      = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    last_name       = models.CharField(max_length=45)
    email           = models.CharField(max_length=100)
    password        = models.CharField(max_length=254)
    user_type       = models.ForeignKey(UserType, on_delete=models.CASCADE, related_name='all_users')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    objects         = UserManager()

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)
    
    @staticmethod
    def ifExists(email):
        users    = User.objects.filter(email = email)
        if len(users) > 0:
            return True
        else:
            return False

    @staticmethod
    def authenticate(email, password): 
        results = User.objects.filter(email = email) 
        if len(results) == 1:
            user = results[0]
            bd_password = user.password
            print(bd_password)
            if check_password(password, bd_password):
                  return user
        return None           

class Region(models.Model):
    name            = models.CharField(max_length=45, validators=[ValidarLongitudMinima])

class City(models.Model):
    name            = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    region          = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities')

class Comuna(models.Model):
    name            = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    city          = models.ForeignKey(City, on_delete=models.CASCADE, related_name='comunas')

    def __str__(self):
        return '%s' % (self.name)

class Address(models.Model):
    alias           = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    street          = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    number          = models.IntegerField()
    appartment      = models.CharField(max_length=15, default=None)
    floor           = models.CharField(max_length=15, default=None)
    comments        = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    comuna          = models.ForeignKey(Comuna, on_delete=models.CASCADE, related_name='addresses')
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_addresses')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

class Ingredient(models.Model):
    name            = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    price           = models.IntegerField()
    discount        = models.BooleanField(default=False)
    special_price   = models.IntegerField()
    optional        = models.BooleanField(default=False)
    orden           = models.IntegerField()
    multiple_option = models.BooleanField(default=False)

class IngredientOption(models.Model):
    option          = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    price           = models.IntegerField()
    discount        = models.BooleanField(default=False)
    special_price   = models.IntegerField(default=0)
    ingredient      = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='options')
    orden           = models.IntegerField(default=1)

    def __str__(self):
        return '%s' % (self.option)

class PizzaManager(models.Manager):
    def validator(self, postData):
        errors  = {}
        
        if len(postData['name']) < 3:
            errors['name'] = 'Debe agregar un nombre de al menos 3 caracteres'

        if len(postData['image']) < 3:
            errors['image'] = 'Debe agregar un nombre de imagen de al menos 3 caracteres'

        return errors

class Pizza(models.Model):
    name            = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    image           = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    price           = models.IntegerField()
    discount        = models.BooleanField(default=False)
    special_price   = models.IntegerField(default=0)
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_pizzas')
    all_users_like  = models.ManyToManyField(User, related_name='favorites_pizzas')
    all_ingredients = models.ManyToManyField(IngredientOption, related_name='all_in_pizzas')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    objects         = PizzaManager()

class Extra(models.Model):
    name            = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    image           = models.CharField(max_length=45, validators=[ValidarLongitudMinima])
    price           = models.IntegerField()
    discount        = models.BooleanField(default=False)
    special_price   = models.IntegerField()
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

class Order(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_orders')
    address         = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='orders')
    favorite        = models.BooleanField(default=False)
    total           = models.IntegerField()
    total_discount  = models.IntegerField()
    fee_delivery    = models.IntegerField()
    tax             = models.IntegerField()
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

class DetailPizzaOrder(models.Model):
    all_pizzas      = models.ManyToManyField(Pizza, related_name='all_pizzas_in_orders')
    quantity        = models.IntegerField()
    order           = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='all_pizzas_order')

class DetailExtraOrder(models.Model):
    all_extras      = models.ManyToManyField(Extra, related_name='all_extras_in_orders')
    quantity        = models.IntegerField()
    order           = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='all_extras_order')

class SpecialDiscount(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discounts_created')
    users_have_discount  = models.ManyToManyField(User, related_name='my_discounts')
    amount          = models.IntegerField()
    discount_used   = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

