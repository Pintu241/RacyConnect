from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, CollectorProfile, RecyclerProfile
from .forms import (
    UserRegistrationForm,
    LoginForm,
    UserProfileForm,
    CollectorProfileForm,
    RecyclerProfileForm,
)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    role_param = request.GET.get('role', User.ROLE_CUSTOMER)
    initial_role = role_param if role_param in [User.ROLE_CUSTOMER, User.ROLE_COLLECTOR, User.ROLE_RECYCLER] else User.ROLE_CUSTOMER

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to RecyConnect, {user.first_name or user.username}! Your account has been created.")
            return redirect('dashboard:index')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm(initial={'role': initial_role})

    return render(request, 'accounts/register.html', {'form': form, 'selected_role': initial_role})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:index')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out safely.")
    return redirect('core:home')


@login_required
def profile_view(request):
    user = request.user
    collector_form = None
    recycler_form = None

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        
        valid = user_form.is_valid()
        if user.is_collector:
            collector_form = CollectorProfileForm(request.POST, request.FILES, instance=user.collector_profile)
            valid = valid and collector_form.is_valid()
        elif user.is_recycler:
            recycler_form = RecyclerProfileForm(request.POST, instance=user.recycler_profile)
            valid = valid and recycler_form.is_valid()

        if valid:
            user_form.save()
            if collector_form:
                collector_form.save()
            if recycler_form:
                recycler_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please check the highlighted errors.")
    else:
        user_form = UserProfileForm(instance=user)
        if user.is_collector:
            collector_form = CollectorProfileForm(instance=user.collector_profile)
        elif user.is_recycler:
            recycler_form = RecyclerProfileForm(instance=user.recycler_profile)

    context = {
        'user_form': user_form,
        'collector_form': collector_form,
        'recycler_form': recycler_form,
    }
    return render(request, 'accounts/profile.html', context)
