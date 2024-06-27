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
    path('delete_data/<int:data_id>/', views.delete_data, name='delete_data'), 
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('nmap_tool/', views.nmap_tool, name='nmap_tool'),
    path('run_pwnxss/', views.run_pwnxss, name='run_pwnxss'),
    path('run_xsstrike/', views.run_xsstrike, name='run_xsstrike'),
    path('tool_results/', views.tool_results, name='tool_results'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
]
