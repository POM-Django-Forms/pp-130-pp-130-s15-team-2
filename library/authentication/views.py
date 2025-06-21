from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .forms import CustomUserCreationForm, ProfileUpdateForm, PasswordChangeCustomForm


def is_librarian(user):
    return user.is_authenticated and user.role == CustomUser.ROLE_LIBRARIAN


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('book:book_list')

def custom_logout(request):
    next_page = request.GET.get('next', None)
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    if next_page:
        return redirect(next_page)
    return redirect('book:book_list')

class RegisterView(CreateView):
    """View for user registration."""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('book:book_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Create an Account')
        return context

    def form_valid(self, form):
        # Save the user
        response = super().form_valid(form)
        
        # Log the user in
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(email=email, password=password)
        
        if user is not None:
            login(self.request, user)
            messages.success(self.request, _('Registration successful! Welcome to the library.'))
        
        return response

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        return next_url if next_url else super().get_success_url()


class ProfileView(LoginRequiredMixin, UpdateView):
    """View for user profile management."""
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'registration/profile.html'
    success_url = reverse_lazy('authentication:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('My Profile')
        context['role_display'] = dict(CustomUser.ROLE_CHOICES).get(
            self.request.user.role, _('Unknown'))
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Profile updated successfully!'))
        return super().form_valid(form)


class ChangePasswordView(LoginRequiredMixin, FormView):
    """View for changing user password."""
    template_name = 'registration/change_password.html'
    form_class = PasswordChangeCustomForm
    success_url = reverse_lazy('authentication:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, _('Your password was successfully updated!'))
        return reverse('authentication:change_password')
