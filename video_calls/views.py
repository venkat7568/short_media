"""Views for video calls app."""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
import uuid
from .models import VideoCallSession, CallStatus


@login_required
def start_random_call_view(request):
    """
    Start a random Omegle-style call.
    Matches with someone waiting or creates a new waiting session.
    """
    # Check if user already has an active call
    existing_call = VideoCallSession.objects.filter(
        Q(caller=request.user) | Q(receiver=request.user),
        status__in=[CallStatus.WAITING, CallStatus.ACTIVE]
    ).first()

    if existing_call:
        return redirect('video_calls:call_room', room_id=existing_call.room_id)

    # Try to find someone waiting with matching preferences
    user_prefs = getattr(request.user, 'dating_preferences', None)

    waiting_calls = VideoCallSession.objects.filter(
        status=CallStatus.WAITING,
        is_random=True,
        receiver__isnull=True
    ).exclude(caller=request.user)

    # If user has preferences, try to match
    if user_prefs and user_prefs.is_active:
        for waiting_call in waiting_calls:
            other_prefs = getattr(waiting_call.caller, 'dating_preferences', None)
            if other_prefs and other_prefs.is_active:
                # Check gender preference
                if user_prefs.preferred_gender != 'ANY':
                    other_profile = waiting_call.caller.profile
                    if other_profile.gender != user_prefs.preferred_gender:
                        continue

                # Match found
                waiting_call.receiver = request.user
                waiting_call.status = CallStatus.ACTIVE
                waiting_call.started_at = timezone.now()
                waiting_call.save()
                return redirect('video_calls:call_room', room_id=waiting_call.room_id)

    # If no preference match, try any waiting call
    waiting_call = waiting_calls.first()
    if waiting_call:
        waiting_call.receiver = request.user
        waiting_call.status = CallStatus.ACTIVE
        waiting_call.started_at = timezone.now()
        waiting_call.save()
        return redirect('video_calls:call_room', room_id=waiting_call.room_id)

    # No one waiting, create new waiting session
    room_id = str(uuid.uuid4())
    call = VideoCallSession.objects.create(
        caller=request.user,
        status=CallStatus.WAITING,
        is_random=True,
        room_id=room_id
    )

    return redirect('video_calls:call_room', room_id=room_id)


@login_required
def call_room_view(request, room_id):
    """
    Video call room view.
    """
    try:
        call = VideoCallSession.objects.get(room_id=room_id)

        # Check if user is part of this call
        if request.user not in [call.caller, call.receiver]:
            messages.error(request, 'You are not part of this call.')
            return redirect('video_calls:start_random')

        # Determine the other user
        other_user = call.receiver if call.caller == request.user else call.caller

        context = {
            'call': call,
            'other_user': other_user,
            'room_id': room_id,
            'is_waiting': call.status == CallStatus.WAITING,
        }

        return render(request, 'video_calls/call_room.html', context)

    except VideoCallSession.DoesNotExist:
        messages.error(request, 'Call session not found.')
        return redirect('video_calls:start_random')


@login_required
@require_POST
def skip_call_view(request, room_id):
    """
    Skip current call and find another person.
    """
    try:
        call = VideoCallSession.objects.get(room_id=room_id)

        # End current call
        call.status = CallStatus.ENDED
        call.ended_at = timezone.now()
        if call.started_at:
            duration = (call.ended_at - call.started_at).total_seconds()
            call.duration = int(duration)
        call.save()

        # Start new random call
        return redirect('video_calls:start_random')

    except VideoCallSession.DoesNotExist:
        return redirect('video_calls:start_random')


@login_required
@require_POST
def end_call_view(request, room_id):
    """
    End the current call.
    """
    try:
        call = VideoCallSession.objects.get(room_id=room_id)

        call.status = CallStatus.ENDED
        call.ended_at = timezone.now()
        if call.started_at:
            duration = (call.ended_at - call.started_at).total_seconds()
            call.duration = int(duration)
        call.save()

        messages.success(request, 'Call ended.')
        return JsonResponse({'status': 'success'})

    except VideoCallSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Call not found'}, status=404)


@login_required
def call_status_view(request, room_id):
    """
    API endpoint to check call status.
    Used for polling to detect when someone joins.
    """
    try:
        call = VideoCallSession.objects.get(room_id=room_id)

        return JsonResponse({
            'status': call.status,
            'has_partner': call.receiver is not None,
            'partner_username': call.receiver.username if call.receiver else None,
        })

    except VideoCallSession.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)
