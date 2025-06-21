from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import BookCreateView, BookUpdateView

app_name = 'book'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('new/', login_required(BookCreateView.as_view()), name='book_create'),
    path('<int:pk>/edit/', login_required(BookUpdateView.as_view()), name='book_edit'),
    path('<int:book_id>/', views.book_detail, name='book_detail'),
    path('user/<int:user_id>/', views.user_books, name='user_books'),
]
