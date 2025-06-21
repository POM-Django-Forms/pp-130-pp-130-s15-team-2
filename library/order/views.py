from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from book.models import Book
from .models import Order

User = get_user_model()


@login_required
def create_order(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        if not book_id:
            messages.error(request, 'No book specified.')
            return redirect('book:book_list')
            
        book = get_object_or_404(Book, id=book_id)
        
        if book.count <= 0:
            messages.error(request, 'This book is currently out of stock.')
            return redirect('book:book_detail', book_id=book.id)
        
        # Check if user already has this book
        existing_order = Order.objects.filter(
            user=request.user, 
            book=book, 
            end_at__isnull=True
        ).exists()
        
        if existing_order:
            messages.warning(request, 'You have already borrowed this book.')
            return redirect('book:book_detail', book_id=book.id)
        
        # Create the order
        order = Order.objects.create(
            user=request.user,
            book=book,
            plated_end_at=timezone.now() + timedelta(days=14)  # 2 weeks to return
        )
        
        # Decrease book count
        book.count -= 1
        book.save()
        
        messages.success(request, f'You have successfully borrowed "{book.name}". Please return it by {order.plated_end_at.strftime("%B %d, %Y")}.')
        return redirect('order:my_orders')
    
    return redirect('book:book_list')


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user, end_at__isnull=True).select_related('book')
    context = {
        'orders': orders,
        'my_orders': True
    }
    return render(request, 'order/order_list.html', context)


@login_required
def all_orders(request):
    if not request.user.is_librarian:
        return redirect('book:book_list')
        
    orders = Order.objects.filter(end_at__isnull=True).select_related('book', 'user')
    
    # Filtering
    user_id = request.GET.get('user_id')
    if user_id:
        orders = orders.filter(user_id=user_id)
    
    context = {
        'orders': orders,
        'all_orders': True,
        'selected_user': int(user_id) if user_id else None
    }
    return render(request, 'order/order_list.html', context)


@login_required
def close_order(request, order_id):
    if not request.user.is_librarian:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('book:book_list')
    
    order = get_object_or_404(Order, id=order_id, end_at__isnull=True)
    
    if request.method == 'POST':
        # Mark order as returned
        order.end_at = timezone.now()
        order.save()
        
        # Increase book count
        book = order.book
        book.count += 1
        book.save()
        
        messages.success(request, f'Order #{order.id} has been closed. Book "{book.name}" is now available.')
        return redirect('order:all_orders')


@login_required
def user_books(request, user_id):
    """View to show all books borrowed by a specific user"""
    if not request.user.is_librarian:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('book:book_list')
    
    user = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=user).select_related('book').order_by('-created_at')
    
    context = {
        'user_orders': orders,
        'target_user': user,
        'is_user_books': True
    }
    return render(request, 'order/user_books.html', context)
    
    context = {'order': order}
    return render(request, 'order/close_order_confirm.html', context)
