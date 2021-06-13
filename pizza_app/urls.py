from django.urls import path
from . import views
from django.conf.urls import handler404

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register_pizza_app'),
    path('login', views.login, name='login_pizza_app'),
    path('logout', views.logout, name='logout_pizza_app'),

    path('create_pizza', views.create_pizza, name='create_pizza'),
    path('get_price', views.get_price, name='get_price'),
    path('add_pizza/<int:id_pizza>', views.add_pizza, name='add_pizza'),
    path('add_extra/<int:id_extra>', views.add_extra, name='add_extra'),
    path('ver_carrito', views.ver_carrito, name='ver_carrito'),
    path('del_item_carrito/<str:carrito_id>', views.del_item_carrito, name='del_item_carrito'),
    path('delete_pizza/<int:pizza_id>', views.del_pizza, name='delete_pizza'),
]

handler404 = 'pizza_app.views.error_404_view'