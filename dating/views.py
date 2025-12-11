"""Views for dating app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.exceptions import ValidationException, NotFoundException
from .services import DatingService, MatchingService
from .forms import UserPreferencesForm, MatchRequestForm
from .models import MatchRequest


dating_service = DatingService()
matching_service = MatchingService()


@login_required
def discover_matches_view(request):
    """
    View for discovering potential matches.
    Shows all friends and known people, ranked by compatibility.
    """
    # Get or create user preferences
    preferences = dating_service.get_or_create_preferences(request.user)

    # Discover matches (shows all friends/known people ranked by compatibility)
    matches = dating_service.discover_matches(request.user, limit=50)

    context = {
        'matches': matches,
        'preferences': preferences,
    }
    return render(request, 'dating/discover.html', context)


@login_required
def match_requests_view(request):
    """
    View for viewing match requests (sent and received).
    """
    pending_received = dating_service.get_pending_received_requests(request.user)
    pending_sent = dating_service.get_pending_sent_requests(request.user)
    accepted = dating_service.get_accepted_requests(request.user)

    context = {
        'pending_received': pending_received,
        'pending_sent': pending_sent,
        'accepted': accepted,
    }
    return render(request, 'dating/requests.html', context)


@login_required
def my_matches_view(request):
    """
    View for viewing active matches.
    """
    matches = dating_service.get_user_matches(request.user)

    context = {
        'matches': matches,
    }
    return render(request, 'dating/matches.html', context)


@login_required
def preferences_view(request):
    """
    View for managing dating preferences.
    """
    preferences = dating_service.get_or_create_preferences(request.user)

    if request.method == 'POST':
        form = UserPreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your dating preferences have been updated.')
            return redirect('dating:preferences')
    else:
        form = UserPreferencesForm(instance=preferences)

    context = {
        'form': form,
        'preferences': preferences,
    }
    return render(request, 'dating/preferences.html', context)


@login_required
@require_POST
def send_match_request_view(request, user_id):
    """
    View for sending a match request.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        receiver = get_object_or_404(User, id=user_id)
        message = request.POST.get('message', '')

        match_request = dating_service.send_match_request(
            sender=request.user,
            receiver=receiver,
            message=message
        )

        messages.success(request, f'Match request sent to {receiver.username}!')

        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'Match request sent to {receiver.username}!'
            })

        return redirect('dating:discover')

    except ValidationException as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return redirect('dating:discover')


@login_required
@require_POST
def accept_match_request_view(request, request_id):
    """
    View for accepting a match request.
    """
    try:
        response_message = request.POST.get('response_message', '')
        match = dating_service.accept_match_request(
            request_id=request_id,
            user=request.user,
            response_message=response_message
        )

        messages.success(request, 'Match request accepted! You are now matched.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Match request accepted!'
            })

        return redirect('dating:requests')

    except (ValidationException, NotFoundException) as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return redirect('dating:requests')


@login_required
@require_POST
def reject_match_request_view(request, request_id):
    """
    View for rejecting a match request.
    """
    try:
        response_message = request.POST.get('response_message', '')
        dating_service.reject_match_request(
            request_id=request_id,
            user=request.user,
            response_message=response_message
        )

        messages.success(request, 'Match request rejected.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Match request rejected.'
            })

        return redirect('dating:requests')

    except (ValidationException, NotFoundException) as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return redirect('dating:requests')


@login_required
@require_POST
def block_user_from_request_view(request, request_id):
    """
    View for blocking a user from a match request.
    """
    try:
        dating_service.block_user_from_request(
            request_id=request_id,
            user=request.user
        )

        messages.success(request, 'User has been blocked.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'User has been blocked.'
            })

        return redirect('dating:requests')

    except (ValidationException, NotFoundException) as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return redirect('dating:requests')


@login_required
@require_POST
def cancel_match_request_view(request, request_id):
    """
    View for canceling a sent match request.
    """
    try:
        dating_service.cancel_match_request(
            request_id=request_id,
            user=request.user
        )

        messages.success(request, 'Match request canceled.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Match request canceled.'
            })

        return redirect('dating:requests')

    except (ValidationException, NotFoundException) as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return redirect('dating:requests')


@login_required
@require_POST
def unmatch_view(request, match_id):
    """
    View for unmatching with a user.
    """
    try:
        dating_service.unmatch(
            match_id=match_id,
            user=request.user
        )

        messages.success(request, 'You have been unmatched.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'You have been unmatched.'
            })

        return redirect('dating:matches')

    except (ValidationException, NotFoundException) as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return redirect('dating:matches')


@login_required
@require_POST
def send_knowing_request_view(request, user_id):
    """
    Send a 'know each other' request to another user.
    This is the first step before dating.
    """
    from django.contrib.auth import get_user_model
    from django.db.models import Q
    User = get_user_model()

    try:
        receiver = get_object_or_404(User, id=user_id)

        if receiver == request.user:
            messages.error(request, 'Cannot send request to yourself.')
            return redirect('users:user_profile', username=receiver.username)

        # Check if request already exists
        existing = MatchRequest.objects.filter(
            Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)
        ).first()

        if existing:
            if existing.status == 'KNOWING':
                messages.info(request, 'You are already knowing each other.')
            elif existing.status == 'ACCEPTED':
                messages.info(request, 'You are already dating.')
            elif existing.status == 'PENDING':
                messages.info(request, 'Request already sent.')
            else:
                # Update existing rejected/blocked request to pending
                existing.status = 'PENDING'
                existing.save()
                messages.success(request, 'Know each other request sent!')
        else:
            # Create new request
            MatchRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                status='PENDING',
                message='Would like to know you better'
            )
            messages.success(request, 'Know each other request sent!')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('users:user_profile', username=receiver.username)

    except Exception as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
        return redirect('users:search')


@login_required
@require_POST
def accept_knowing_request_view(request, request_id):
    """
    Accept a 'know each other' request.
    This sets the status to KNOWING.
    """
    try:
        match_request = get_object_or_404(MatchRequest, id=request_id, receiver=request.user)

        if match_request.status != 'PENDING':
            messages.error(request, 'This request is not pending.')
            return redirect('messaging:requests')

        # Set to knowing status
        match_request.set_knowing()
        messages.success(request, f'You are now knowing each other with {match_request.sender.username}!')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('messaging:requests')

    except Exception as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
        return redirect('messaging:requests')


@login_required
@require_POST
def send_dating_request_view(request, user_id):
    """
    Send a dating request to someone you're already knowing.
    This upgrades KNOWING status to PENDING (for dating).
    """
    from django.contrib.auth import get_user_model
    from django.db.models import Q
    User = get_user_model()

    try:
        receiver = get_object_or_404(User, id=user_id)

        # Check if they're already knowing each other
        existing = MatchRequest.objects.filter(
            Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)
        ).first()

        if not existing or existing.status != 'KNOWING':
            messages.error(request, 'You need to know each other first before dating.')
            return redirect('users:user_profile', username=receiver.username)

        # Update to pending dating request
        existing.status = 'PENDING'
        existing.message = 'Would you like to start dating?'
        existing.sender = request.user
        existing.receiver = receiver
        existing.save()

        messages.success(request, 'Dating request sent!')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('users:user_profile', username=receiver.username)

    except Exception as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
        return redirect('users:user_profile', username=receiver.username)


@login_required
@require_POST
def breakup_view(request, user_id):
    """
    Break up with someone you're dating.
    This is a force breakup - no approval needed from the other person.
    """
    from django.contrib.auth import get_user_model
    from django.db.models import Q
    User = get_user_model()

    try:
        other_user = get_object_or_404(User, id=user_id)

        # Find the dating relationship
        match_request = MatchRequest.objects.filter(
            Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user),
            status='ACCEPTED'
        ).first()

        if not match_request:
            messages.error(request, 'You are not dating this person.')
            return redirect('users:user_profile', username=other_user.username)

        # Force breakup
        match_request.breakup()
        messages.success(request, f'You have broken up with {other_user.username}.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('users:user_profile', username=other_user.username)

    except Exception as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
        return redirect('users:user_profile', username=other_user.username)


@login_required
@require_POST
def unknow_view(request, user_id):
    """
    Remove 'knowing each other' status.
    This breaks the knowing relationship without going to dating.
    """
    from django.contrib.auth import get_user_model
    from django.db.models import Q
    User = get_user_model()

    try:
        other_user = get_object_or_404(User, id=user_id)

        # Find the knowing relationship
        match_request = MatchRequest.objects.filter(
            Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user),
            status='KNOWING'
        ).first()

        if not match_request:
            messages.error(request, 'You are not knowing each other.')
            return redirect('users:user_profile', username=other_user.username)

        # Remove knowing status
        match_request.unknow()
        messages.success(request, f'You are no longer knowing {other_user.username}.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('users:user_profile', username=other_user.username)

    except Exception as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
        return redirect('users:user_profile', username=other_user.username)
