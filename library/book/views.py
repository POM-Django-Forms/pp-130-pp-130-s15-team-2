from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Book
from author.models import Author
from .forms import BookForm

def is_librarian(user):
    return user.is_authenticated and user.is_librarian

class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'book/book_form.html'
    success_url = reverse_lazy('book:book_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Book'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Book added successfully!')
        return super().form_valid(form)

class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'book/book_form.html'
    
    def get_success_url(self):
        return reverse_lazy('book:book_detail', kwargs={'book_id': self.object.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit {self.object.name}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Book updated successfully!')
        return super().form_valid(form)


def book_list(request):
    books = Book.objects.all()
    
    # Filtering
    query = request.GET.get('q')
    author_id = request.GET.get('author')
    
    if query:
        books = books.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if author_id:
        books = books.filter(authors__id=author_id)
    
    authors = Author.objects.all()
    
    context = {
        'books': books,
        'authors': authors,
        'search_query': query or '',
        'selected_author': int(author_id) if author_id else None,
        'is_librarian': request.user.is_authenticated and request.user.is_librarian
    }
    return render(request, 'book/book_list.html', context)


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    context = {
        'book': book,
        'available': book.count > 0
    }
    return render(request, 'book/book_detail.html', context)


@login_required
def user_books(request, user_id):
    if not request.user.is_librarian and request.user.id != user_id:
        return redirect('book_list')
        
    from order.models import Order
    orders = Order.objects.filter(user_id=user_id, end_at__isnull=True)
    books = [order.book for order in orders]
    
    context = {
        'books': books,
        'user_books': True,
        'user_id': user_id,
        'is_librarian': request.user.is_authenticated and request.user.is_librarian
    }
    return render(request, 'book/book_list.html', context)
