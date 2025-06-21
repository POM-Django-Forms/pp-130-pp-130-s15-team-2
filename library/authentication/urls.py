from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Librarian user management
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
]
