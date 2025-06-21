from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import Http404, HttpResponseForbidden
from django.db.models import Q
from .models import CustomUser


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

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', '0')  # Default to guest (0)
        
        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return redirect('authentication:register')
            
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('authentication:register')
            
        # Create the user
        user = CustomUser.objects.create_user(
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            role=int(role)  # Convert to int as our model expects integer for role
        )
        
        # Log the user in
        user = authenticate(email=email, password=password1)
        if user is not None:
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the library.')
            next_page = request.POST.get('next', None)
            if next_page:
                return redirect(next_page)
            return redirect('book:book_list')
    
    # Get role choices from the model
    role_choices = [
        {'value': CustomUser.ROLE_VISITOR, 'label': 'Guest User (Borrow Books)'},
        {'value': CustomUser.ROLE_LIBRARIAN, 'label': 'Librarian (Manage Library)'}
    ]
    return render(request, 'registration/register.html', {'role_choices': role_choices})


@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        # Update user's name if provided
        if first_name or last_name:
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('authentication:profile')
    
    # Get role display name
    role_display = dict(CustomUser.ROLE_CHOICES).get(request.user.role, 'Unknown')
    
    context = {
        'user': request.user,
        'role_display': role_display,
        'is_librarian': request.user.role == CustomUser.ROLE_LIBRARIAN
    }
    return render(request, 'registration/profile.html', context)


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def user_list(request):
    """
    View for librarians to see a list of all users with pagination and search.
    """
    # Only allow librarians to access this view
    if not is_librarian(request.user):
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    # Get search query if any
    search_query = request.GET.get('search', '').strip()
    
    # Get all users (exclude superusers)
    users = CustomUser.objects.filter(is_superuser=False)
    
    # Apply search filter if query exists
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(middle_name__icontains=search_query)
        )
    
    # Order by most recent first
    users = users.order_by('-date_joined')
    
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
    
    context = {
        'users': users,
        'search_query': search_query,
        'ROLE_LIBRARIAN': CustomUser.ROLE_LIBRARIAN,
        'is_paginated': users.has_other_pages(),
        'page_obj': users,  # For pagination in template
        'paginator': paginator,  # For page range in template
    }
    return render(request, 'authentication/user_list.html', context)


@login_required
def user_detail(request, user_id):
    """
    View for librarians to see and manage details of a specific user.
    Allows updating user role and active status.
    """
    # Only allow librarians to access this view
    if not is_librarian(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('book:book_list')
    
    try:
        # Get the user or return 404 (exclude superusers)
        user = get_object_or_404(CustomUser, id=user_id, is_superuser=False)
        
        # Handle form submission for updating user
        if request.method == 'POST':
            try:
                # Only allow updating role and active status
                new_role = request.POST.get('role')
                is_active = request.POST.get('is_active') == 'on' or request.POST.get('activate') == '1'
                
                # Update role if changed and valid
                if new_role and new_role.isdigit():
                    new_role = int(new_role)
                    if new_role in [choice[0] for choice in CustomUser.ROLE_CHOICES]:
                        user.role = new_role
                
                # Update active status
                user.is_active = is_active
                user.save(update_fields=['role', 'is_active', 'updated_at'])
                
                # Set appropriate success message
                if 'activate' in request.POST:
                    messages.success(request, f"User {user.email} has been activated successfully.")
                elif not is_active:
                    messages.warning(request, f"User {user.email} has been deactivated.")
                else:
                    messages.success(request, f"User {user.email} has been updated successfully.")
                
                return redirect('authentication:user_detail', user_id=user.id)
                
            except Exception as e:
                messages.error(request, f"An error occurred while updating the user: {str(e)}")
                return redirect('authentication:user_detail', user_id=user.id)
        
        # Get role choices from model's choices
        role_choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in CustomUser.ROLE_CHOICES
        ]
        
        # Get user's role display name
        role_display = dict(CustomUser.ROLE_CHOICES).get(user.role, 'Unknown')
        
        context = {
            'user_profile': user,
            'role_choices': role_choices,
            'role_display': role_display,
            'CustomUser': CustomUser  # Add CustomUser to the context for template use
        }
        
        return render(request, 'authentication/user_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('authentication:user_list')
    return render(request, 'authentication/user_detail.html', context)
