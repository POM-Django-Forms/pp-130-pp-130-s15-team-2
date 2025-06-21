from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('all-orders/', views.all_orders, name='all_orders'),
    path('close/<int:order_id>/', views.close_order, name='close_order'),
    path('user/<int:user_id>/books/', views.user_books, name='user_books'),
]
