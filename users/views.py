"""
Views for User authentication and profile management.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from .forms import SignupForm, LoginForm, OTPVerificationForm, ProfileUpdateForm, PasswordChangeForm
from .services import AuthenticationService, ProfileService
from core.exceptions import (
    AuthenticationException,
    InvalidOTPException,
    UserAlreadyExistsException,
    ExternalServiceException,
)


# Initialize services
auth_service = AuthenticationService()
profile_service = ProfileService()


@require_http_methods(["GET", "POST"])
def signup_view(request):
    """
    Handle user signup.
    GET: Display signup form
    POST: Process signup and redirect to OTP verification
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                # Create user and send OTP
                user, otp_code = auth_service.signup(
                    email=form.cleaned_data['email'],
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1']
                )

                # Store user ID in session for OTP verification
                request.session['pending_user_id'] = user.id
                request.session['pending_user_email'] = user.email

                messages.success(
                    request,
                    f'Account created successfully! Please check your email for the verification code.'
                )
                return redirect('users:verify_otp')

            except UserAlreadyExistsException as e:
                messages.error(request, str(e))
            except ExternalServiceException as e:
                messages.error(request, 'Failed to send verification email. Please try again.')
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again.')
    else:
        form = SignupForm()

    return render(request, 'users/signup.html', {'form': form})


@require_http_methods(["GET", "POST"])
def verify_otp_view(request):
    """
    Handle OTP verification.
    GET: Display OTP verification form
    POST: Verify OTP and redirect to login or home
    """
    # Check if there's a pending user
    pending_user_id = request.session.get('pending_user_id')
    pending_user_email = request.session.get('pending_user_email')

    if not pending_user_id:
        messages.error(request, 'No pending verification found.')
        return redirect('users:signup')

    # Get user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=pending_user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('users:signup')

    # If already verified, redirect to login
    if user.is_verified:
        messages.info(request, 'Your account is already verified. Please log in.')
        return redirect('users:login')

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            try:
                # Verify OTP
                auth_service.verify_otp(user, form.cleaned_data['otp_code'])

                # Clear session
                del request.session['pending_user_id']
                del request.session['pending_user_email']

                messages.success(
                    request,
                    'Email verified successfully! You can now log in.'
                )
                return redirect('users:login')

            except InvalidOTPException as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again.')
    else:
        form = OTPVerificationForm()

    return render(request, 'users/verify_otp.html', {
        'form': form,
        'email': pending_user_email,
    })


@require_http_methods(["POST"])
def resend_otp_view(request):
    """
    Resend OTP to user's email.
    """
    pending_user_id = request.session.get('pending_user_id')

    if not pending_user_id:
        return JsonResponse({'error': 'No pending verification found.'}, status=400)

    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=pending_user_id)
        auth_service.resend_otp(user)
        return JsonResponse({'message': 'OTP sent successfully!'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Failed to resend OTP.'}, status=500)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handle user login.
    GET: Display login form
    POST: Authenticate user and redirect to home
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                # Authenticate user
                user, tokens = auth_service.login(
                    email_or_username=form.cleaned_data['email_or_username'],
                    password=form.cleaned_data['password']
                )

                # Log user in
                auth_login(request, user)

                # Store tokens in session if needed
                request.session['access_token'] = tokens['access']
                request.session['refresh_token'] = tokens['refresh']

                messages.success(request, f'Welcome back, {user.username}!')

                # Redirect to next or home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)

            except AuthenticationException as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again.')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Handle user logout.
    """
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile_view(request):
    """
    Redirect to user's own public profile.
    This allows users to see their profile as others see it,
    with all relationship sections (friends, knowing, dating).
    """
    return redirect('users:user_profile', username=request.user.username)


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit_view(request):
    """
    Display and update user profile.
    GET: Display profile edit form
    POST: Update profile
    """
    user = request.user
    profile = profile_service.get_profile(user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Update user fields
                if form.cleaned_data.get('first_name'):
                    user.first_name = form.cleaned_data['first_name']
                if form.cleaned_data.get('last_name'):
                    user.last_name = form.cleaned_data['last_name']
                user.save()

                # Update profile fields
                profile_data = {
                    'bio': form.cleaned_data.get('bio'),
                    'date_of_birth': form.cleaned_data.get('date_of_birth'),
                    'gender': form.cleaned_data.get('gender'),
                    'location': form.cleaned_data.get('location'),
                    'relationship_status': form.cleaned_data.get('relationship_status'),
                }

                # Handle profile picture upload
                if form.cleaned_data.get('profile_picture'):
                    profile_data['profile_picture'] = form.cleaned_data['profile_picture']

                # Remove None values
                profile_data = {k: v for k, v in profile_data.items() if v is not None}

                profile_service.update_profile(user, **profile_data)

                messages.success(request, 'Profile updated successfully!')
                return redirect('users:profile')

            except Exception as e:
                messages.error(request, 'Failed to update profile. Please try again.')
    else:
        # Pre-populate form with existing data
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': profile.bio if profile else '',
            'date_of_birth': profile.date_of_birth if profile else None,
            'gender': profile.gender if profile else '',
            'location': profile.location if profile else '',
            'relationship_status': profile.relationship_status if profile else '',
        }
        form = ProfileUpdateForm(initial=initial_data)

    return render(request, 'users/profile.html', {
        'form': form,
        'profile': profile,
    })


@login_required
@require_http_methods(["GET", "POST"])
def change_password_view(request):
    """
    Handle password change.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            try:
                auth_service.change_password(
                    user=request.user,
                    old_password=form.cleaned_data['old_password'],
                    new_password=form.cleaned_data['new_password1']
                )
                messages.success(request, 'Password changed successfully!')
                return redirect('users:profile')

            except AuthenticationException as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, 'Failed to change password. Please try again.')
    else:
        form = PasswordChangeForm()

    return render(request, 'users/change_password.html', {'form': form})


def home_view(request):
    """
    Home/landing page view.
    """
    return render(request, 'home.html')


@login_required
@require_http_methods(["GET"])
def search_users_view(request):
    """
    Search for users by username or name.
    Can filter by dating visibility.
    """
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('filter', 'all')  # 'all', 'dating', 'friends'
    results = []

    if query:
        from django.contrib.auth import get_user_model
        from django.db.models import Q
        from dating.models import MatchRequest, MatchStatus

        User = get_user_model()
        queryset = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id).select_related('profile')

        # Apply dating filter
        if filter_type == 'dating':
            queryset = queryset.filter(profile__show_in_dating_search=True)

        results_list = list(queryset[:20])

        # Add relationship status for each user
        for user in results_list:
            match_request = MatchRequest.objects.filter(
                Q(sender=request.user, receiver=user) |
                Q(sender=user, receiver=request.user)
            ).first()

            if not match_request:
                user.relationship_status = 'none'
                user.request_id = None
            elif match_request.status == MatchStatus.PENDING:
                if match_request.sender == request.user:
                    user.relationship_status = 'pending_sent'
                else:
                    user.relationship_status = 'pending_received'
                user.request_id = match_request.id
            elif match_request.status == MatchStatus.KNOWING:
                user.relationship_status = 'knowing'
                user.request_id = match_request.id
            elif match_request.status == MatchStatus.ACCEPTED:
                user.relationship_status = 'dating'
                user.request_id = match_request.id
            else:
                user.relationship_status = 'none'
                user.request_id = None

        results = results_list

    return render(request, 'users/search_results.html', {
        'query': query,
        'results': results,
        'filter_type': filter_type,
    })


@login_required
@require_http_methods(["GET"])
def user_profile_view(request, username):
    """
    View another user's public profile and posts.
    """
    from django.contrib.auth import get_user_model
    from django.shortcuts import get_object_or_404
    from django.db.models import Q
    from posts.models import Post, PostVisibility
    from dating.models import MatchRequest, MatchStatus

    User = get_user_model()
    profile_user = get_object_or_404(User, username=username)

    # Get public posts
    posts = Post.objects.filter(
        author=profile_user,
        visibility=PostVisibility.PUBLIC
    ).order_by('-created_at')[:20]

    # Check if there's an existing match request
    existing_request = MatchRequest.objects.filter(
        Q(sender=request.user, receiver=profile_user) |
        Q(sender=profile_user, receiver=request.user)
    ).first()

    # Get user's liked posts
    user_liked_post_ids = list(request.user.likes.values_list('post_id', flat=True))

    context = {
        'profile_user': profile_user,
        'profile': profile_user.profile,
        'posts': posts,
        'user_liked_post_ids': user_liked_post_ids,
        'existing_request': existing_request,
        'is_own_profile': request.user == profile_user,
    }

    return render(request, 'users/user_profile.html', context)
