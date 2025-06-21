from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.apps import apps

# Get the CustomUser model using the app registry to avoid circular imports
CustomUser = apps.get_model('authentication', 'CustomUser')


def get_user_list_context(users, search_query, request):
    """Helper function to get the context for the user list view."""
    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page = request.GET.get('page')
    
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
    
    return {
        'users': users,
        'search_query': search_query,
        'ROLE_LIBRARIAN': CustomUser.ROLE_LIBRARIAN,
        'is_paginated': users.has_other_pages(),
        'page_obj': users,  # For pagination in template
        'paginator': paginator,  # For page range in template
    }


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for librarians to see and manage details of a specific user.
    Allows updating user role and active status.
    """
    model = CustomUser
    template_name = 'authentication/user_detail.html'
    context_object_name = 'user_profile'
    
    def get_form_class(self):
        from .forms import CustomUserChangeForm
        return CustomUserChangeForm
    
    def test_func(self):
        return self.request.user.is_librarian or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, _("You don't have permission to access this page."))
        return redirect('book:book_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('User Details')
        return context
    
    def form_valid(self, form):
        # Prevent users from editing their own role/status
        if self.object == self.request.user:
            messages.warning(self.request, _("You cannot edit your own role or status."))
            return redirect('authentication:profile')
        
        # Save the form data
        self.object = form.save(commit=False)
        self.object.save()
        form.save_m2m()  # For many-to-many fields if any
        
        messages.success(self.request, _('User updated successfully.'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('authentication:user_detail', kwargs={'pk': self.object.pk})


@login_required
def user_list(request):
    """
    View for librarians to see a list of all users with pagination and search.
    """
    if not request.user.is_librarian and not request.user.is_superuser:
        messages.error(request, _("You don't have permission to access this page."))
        return redirect('book:book_list')
    
    search_query = request.GET.get('search', '')
    
    if search_query:
        users = CustomUser.objects.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        ).order_by('email')
    else:
        users = CustomUser.objects.all().order_by('email')
    
    context = get_user_list_context(users, search_query, request)
    return render(request, 'authentication/user_list.html', context)
