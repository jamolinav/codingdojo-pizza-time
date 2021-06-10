from django.urls import path
from . import views
from django.conf.urls import handler404

urlpatterns = [
    path('', views.register, name='home_examen_app'),
    path('register', views.register, name='register_examen_app'),
    path('login', views.login, name='login_examen_app'),
    path('logout', views.logout, name='logout_examen_app'),

    path('wishes', views.wishes, name='wishes'),
    path('add_wish', views.add_wish, name='add_wish'),
    path('remove_wish/<int:id_wish>', views.remove_wish, name='remove_wish'),
    path('grand_wish/<int:id_wish>', views.grand_wish, name='grand_wish'),
    path('edit_wish/<int:id_wish>', views.edit_wish, name='edit_wish'),
    path('update_wish', views.update_wish, name='update_wish'),
    path('add_like/<int:id_wish>', views.add_like, name='add_like'),
    path('view_stats', views.view_stats, name='view_stats'),
]

handler404 = 'examen_app.views.error_404_view'