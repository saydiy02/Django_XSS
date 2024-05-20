from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('new_data/', views.new_data, name='new_data'),
    path('success/', views.success, name='success'),
    path('result/', views.result, name='result'),
    path('view_data/', views.view_data, name='view_data'),
    path('logout/', views.user_logout, name='logout'),
]
