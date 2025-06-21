from django import template
from ..models import CustomUser

register = template.Library()

@register.filter(name='has_role')
def has_role(user, role_name):
    """
    Check if a user has a specific role.
    Usage: {% if user|has_role:'librarian' %}
    """
    if not user.is_authenticated:
        return False
        
    role_mapping = {
        'librarian': CustomUser.ROLE_LIBRARIAN,
        'visitor': CustomUser.ROLE_VISITOR,
    }
    
    role_value = role_mapping.get(role_name.lower(), -1)
    return user.role == role_value

@register.filter(name='is_librarian')
def is_librarian(user):
    """Check if the user is a librarian."""
    return user.is_authenticated and user.role == CustomUser.ROLE_LIBRARIAN

@register.filter(name='is_visitor')
def is_visitor(user):
    """Check if the user is a visitor."""
    return user.is_authenticated and user.role == CustomUser.ROLE_VISITOR

@register.simple_tag
def get_role_display(role_value):
    """Get the display name for a role value."""
    return dict(CustomUser.ROLE_CHOICES).get(role_value, 'Unknown')
