from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Book
from author.models import Author


class BookListView(ListView):
    model = Book
    template_name = 'book/book_list.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('author')
        query = self.request.GET.get('q')
        author_id = self.request.GET.get('author')
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
        
        if author_id:
            queryset = queryset.filter(authors__id=author_id)
            
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['authors'] = Author.objects.all()
        context['selected_author'] = int(self.request.GET.get('author')) if self.request.GET.get('author') else None
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'book/book_detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available'] = self.object.count > 0
        return context


class BookCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    template_name = 'book/book_form.html'
    fields = ['name', 'description', 'count', 'authors']
    
    def test_func(self):
        return self.request.user.is_librarian
    
    def form_valid(self, form):
        messages.success(self.request, 'Book added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('book:book_detail', kwargs={'pk': self.object.pk})


class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    template_name = 'book/book_form.html'
    fields = ['name', 'description', 'count', 'authors']
    
    def test_func(self):
        return self.request.user.is_librarian
    
    def form_valid(self, form):
        messages.success(self.request, 'Book updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('book:book_detail', kwargs={'pk': self.object.pk})


class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = 'book/book_confirm_delete.html'
    success_url = reverse_lazy('book:book_list')
    
    def test_func(self):
        return self.request.user.is_librarian
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Book deleted successfully!')
        return super().delete(request, *args, **kwargs)


class UserBooksView(LoginRequiredMixin, ListView):
    template_name = 'order/user_books.html'
    context_object_name = 'user_orders'
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if not self.request.user.is_librarian and self.request.user.id != user_id:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied()
            
        from order.models import Order
        return Order.objects.filter(
            user_id=user_id
        ).select_related('book').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = get_object_or_404(
            'authentication.CustomUser', 
            id=self.kwargs.get('user_id')
        )
        return context
