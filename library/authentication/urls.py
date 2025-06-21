from django.urls import path, include, reverse_lazy
from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from .views import RegisterView, CustomLoginView, custom_logout, ProfileView
from .user_views import user_list, UserDetailView

app_name = 'authentication'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Password change
    path('password/change/',
        PasswordChangeView.as_view(
            template_name='registration/password_change_form.html',
            success_url=reverse_lazy('authentication:password_change_done')
        ),
        name='password_change'
    ),
    path('password/change/done/',
        PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
        ),
        name='password_change_done'
    ),
    
    # Password reset
    path('password/reset/',
        PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url=reverse_lazy('authentication:password_reset_done')
        ),
        name='password_reset'
    ),
    path('password/reset/done/',
        PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path('password/reset/confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('authentication:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path('password/reset/complete/',
        PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    
    # Librarian user management
    path('users/', user_list, name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
]
