"""
Custom decorators for the E-Food application.
Contains authentication and authorization decorators.
"""

# Import HTTP utilities
from django.http import HttpResponse

# Import redirect function for navigation
from django.shortcuts import redirect

# Import Django's Group model for role-based access control
from django.contrib.auth.models import Group

# Import all models from this app
from .models import *


def admin_required(view_func):
    """
    Decorator to check if user belongs to 'admin_owner' group.
    Restricts view access to admin users only.
    Non-admin users are redirected to home page.
    
    Args:
        view_func: The view function to wrap
    
    Returns:
        Wrapper function that checks admin status before executing view
    
    Usage:
        @admin_required
        def my_admin_view(request):
            # Admin-only logic here
            pass
    """
    
    def wrapper_func(request, *args, **kwargs):
        """
        Inner wrapper function that performs the actual check.
        
        Args:
            request: HTTP request object
            *args: Additional positional arguments passed to view
            **kwargs: Additional keyword arguments passed to view
        
        Returns:
            Either the view result or redirect to home page
        """
        # Get the group associated with the current user
        group = Group.objects.get(user=request.user)
        
        # Check if user's group name is 'admin_owner'
        if group.name == 'admin_owner':
            # User is admin - execute the view function
            return view_func(request, *args, **kwargs)
        else:
            # User is not admin - redirect to home page
            return redirect('/')
    
    # Return the wrapper function
    return wrapper_func
