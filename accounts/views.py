from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.conf import settings
import secrets

from .forms import SignUpForm, SignInForm, ProfileForm, ChangePasswordForm, CustomPasswordResetForm, CustomSetPasswordForm
from .models import UserProfile


def signup(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send welcome email
            try:
                send_mail(
                    subject='Welcome to PackAxis!',
                    message=f'Hi {user.first_name},\n\nThank you for creating an account with PackAxis. You can now enjoy faster checkout and track your orders.\n\nBest regards,\nThe PackAxis Team',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            
            # Log the user in
            login(request, user)
            messages.success(request, f'Welcome to PackAxis, {user.first_name}! Your account has been created.')
            
            # Redirect to next page or home
            next_url = request.GET.get('next', 'core:index')
            return redirect(next_url)
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def signin(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            remember_me = form.cleaned_data.get('remember_me', True)
            
            login(request, user)
            
            # Set session expiry based on remember me
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when browser closes
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
            
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect to next page or home
            next_url = request.GET.get('next', 'core:index')
            return redirect(next_url)
    else:
        form = SignInForm()
    
    return render(request, 'accounts/signin.html', {'form': form})


def signout(request):
    """User logout view"""
    if request.user.is_authenticated:
        messages.info(request, 'You have been signed out successfully.')
    logout(request)
    return redirect('core:index')


@login_required
def profile(request):
    """User profile view and edit"""
    user = request.user
    profile = user.profile if hasattr(user, 'profile') else UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=user)
        if form.is_valid():
            # Update user fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            
            # Save profile
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile, user=user)
    
    # Get user's recent orders
    orders = []
    if hasattr(user, 'orders'):
        orders = user.orders.all().order_by('-created_at')[:5]
    
    context = {
        'form': form,
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keep user logged in
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('accounts:profile')
    else:
        form = ChangePasswordForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def order_history(request):
    """View all user orders"""
    orders = []
    if hasattr(request.user, 'orders'):
        orders = request.user.orders.all().order_by('-created_at')
    
    return render(request, 'accounts/order_history.html', {'orders': orders})


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    form_class = CustomPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view"""
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    form_class = CustomSetPasswordForm


def password_reset_done(request):
    """Password reset email sent"""
    return render(request, 'accounts/password_reset_done.html')


def password_reset_complete(request):
    """Password reset complete"""
    return render(request, 'accounts/password_reset_complete.html')


@require_POST
def check_email(request):
    """AJAX endpoint to check if email is already registered"""
    import json
    data = json.loads(request.body)
    email = data.get('email', '').lower()
    
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})
