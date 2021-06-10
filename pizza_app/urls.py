from django.urls import path
from . import views
from django.conf.urls import handler404

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register_pizza_app'),
    path('login', views.login, name='login_pizza_app'),
    path('logout', views.logout, name='logout_pizza_app'),
]

handler404 = 'pizza_app.views.error_404_view'