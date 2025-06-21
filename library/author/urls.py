from django.urls import path
from django.views.decorators.http import require_http_methods
from . import views

app_name = 'author'

urlpatterns = [
    # Author list and CRUD operations
    path('', views.author_list_view, name='author_list'),
    path('create/', views.author_create_view, name='author_create'),
    path('<int:author_id>/', views.author_detail_view, name='author_detail'),
    path('<int:author_id>/edit/', views.author_edit_view, name='author_edit'),
    path('delete/<int:author_id>/', views.author_delete_view, name='author_delete'),
    
    # API endpoints
    path('api/quick-add/', views.author_quick_add, name='author_quick_add'),
]