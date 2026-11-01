from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles):
    """Decorator for views that checks if the logged-in user belongs to allowed roles."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_platform_admin or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to access that section.")
            return redirect('dashboard:index')
        return _wrapped_view
    return decorator

def customer_required(view_func):
    return role_required(['customer'])(view_func)

def collector_required(view_func):
    return role_required(['collector'])(view_func)

def recycler_required(view_func):
    return role_required(['recycler'])(view_func)

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_platform_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Administrative privileges required.")
        return redirect('dashboard:index')
    return _wrapped_view
