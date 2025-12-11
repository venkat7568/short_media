"""Views for messaging and friend requests."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q, Max
from django.utils import timezone
from .models import Conversation, Message, Friendship

User = get_user_model()


@login_required
def inbox_view(request):
    """Display user's message inbox with all conversations."""
    # Get friends and dating partners
    friends = request.user.profile.get_friends()
    dating_partners = request.user.profile.get_dating_relationships()

    # Get all conversations where user is a participant
    conversations = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).select_related('participant1', 'participant2', 'participant1__profile', 'participant2__profile').order_by('-last_message_at')

    # Build conversation data with other participant and last message
    conversations_data = []
    friend_ids = [friend.id for friend in friends]
    dating_ids = [partner.id for partner in dating_partners]

    for conv in conversations:
        other_user = conv.get_other_participant(request.user)
        last_message = conv.messages.last()
        unread_count = conv.get_unread_count(request.user)

        # Determine relationship type
        is_friend = other_user.id in friend_ids
        is_dating = other_user.id in dating_ids

        conversations_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
            'is_friend': is_friend,
            'is_dating': is_dating,
        })

    # Sort: Dating first, then friends, then others
    conversations_data.sort(key=lambda x: (not x['is_dating'], not x['is_friend'], -x['conversation'].last_message_at.timestamp()))

    return render(request, 'messaging/inbox.html', {
        'conversations': conversations_data,
        'friends': friends,
        'dating_partners': dating_partners,
    })


@login_required
def conversation_view(request, username):
    """Display conversation with a specific user."""
    other_user = get_object_or_404(User, username=username)

    if other_user == request.user:
        return redirect('messaging:inbox')

    # Get or create conversation
    conversation = Conversation.objects.filter(
        Q(participant1=request.user, participant2=other_user) |
        Q(participant1=other_user, participant2=request.user)
    ).first()

    if not conversation:
        # Create new conversation (always order participants consistently)
        if request.user.id < other_user.id:
            conversation = Conversation.objects.create(
                participant1=request.user,
                participant2=other_user
            )
        else:
            conversation = Conversation.objects.create(
                participant1=other_user,
                participant2=request.user
            )

    # Mark all messages from other user as read
    unread_messages = conversation.messages.filter(
        receiver=request.user,
        is_read=False
    )
    for msg in unread_messages:
        msg.mark_as_read()

    # Get all messages
    messages = conversation.messages.select_related('sender', 'receiver').all()

    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'other_user': other_user,
        'messages': messages,
    })


@login_required
@require_POST
def send_message_view(request, username):
    """API endpoint to send a message."""
    other_user = get_object_or_404(User, username=username)

    if other_user == request.user:
        return JsonResponse({'error': 'Cannot message yourself'}, status=400)

    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    # Get or create conversation
    conversation = Conversation.objects.filter(
        Q(participant1=request.user, participant2=other_user) |
        Q(participant1=other_user, participant2=request.user)
    ).first()

    if not conversation:
        if request.user.id < other_user.id:
            conversation = Conversation.objects.create(
                participant1=request.user,
                participant2=other_user
            )
        else:
            conversation = Conversation.objects.create(
                participant1=other_user,
                participant2=request.user
            )

    # Create message
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        receiver=other_user,
        text=text
    )

    # Update conversation's last_message_at
    conversation.last_message_at = timezone.now()
    conversation.save()

    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'text': message.text,
            'sender': message.sender.username,
            'created_at': message.created_at.isoformat(),
        }
    })


@login_required
def friend_requests_view(request):
    """Display all friend requests, knowing requests, and dating requests."""
    from dating.models import MatchRequest

    # Friend requests
    received_friend_requests = Friendship.objects.filter(
        receiver=request.user,
        status='PENDING'
    ).select_related('sender', 'sender__profile')

    sent_friend_requests = Friendship.objects.filter(
        sender=request.user,
        status='PENDING'
    ).select_related('receiver', 'receiver__profile')

    accepted_friendships = Friendship.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status='ACCEPTED'
    ).select_related('sender', 'receiver', 'sender__profile', 'receiver__profile')

    # Knowing requests (PENDING knowing requests)
    received_knowing_requests = MatchRequest.objects.filter(
        receiver=request.user,
        status='PENDING'
    ).select_related('sender', 'sender__profile')

    sent_knowing_requests = MatchRequest.objects.filter(
        sender=request.user,
        status='PENDING'
    ).select_related('receiver', 'receiver__profile')

    # Knowing Each Other (ACCEPTED knowing status)
    knowing_relationships = MatchRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status='KNOWING'
    ).select_related('sender', 'receiver', 'sender__profile', 'receiver__profile')

    # Dating relationships
    accepted_dating = MatchRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status='ACCEPTED'
    ).select_related('sender', 'receiver', 'sender__profile', 'receiver__profile')

    return render(request, 'messaging/requests.html', {
        'received_friend_requests': received_friend_requests,
        'sent_friend_requests': sent_friend_requests,
        'accepted_friendships': accepted_friendships,
        'received_knowing_requests': received_knowing_requests,
        'sent_knowing_requests': sent_knowing_requests,
        'knowing_relationships': knowing_relationships,
        'accepted_dating': accepted_dating,
    })


@login_required
@require_POST
def send_friend_request_view(request, username):
    """Send a friend request to another user."""
    receiver = get_object_or_404(User, username=username)

    if receiver == request.user:
        return JsonResponse({'error': 'Cannot befriend yourself'}, status=400)

    # Check if request already exists
    existing = Friendship.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).first()

    if existing:
        if existing.status == 'ACCEPTED':
            return JsonResponse({'error': 'Already friends'}, status=400)
        elif existing.status == 'PENDING':
            return JsonResponse({'error': 'Request already sent'}, status=400)

    # Create friend request
    Friendship.objects.create(
        sender=request.user,
        receiver=receiver,
        status='PENDING'
    )

    return JsonResponse({'success': True})


@login_required
@require_POST
def accept_friend_request_view(request, request_id):
    """Accept a friend request."""
    friendship = get_object_or_404(Friendship, id=request_id, receiver=request.user, status='PENDING')
    friendship.status = 'ACCEPTED'
    friendship.save()

    return JsonResponse({'success': True})


@login_required
@require_POST
def reject_friend_request_view(request, request_id):
    """Reject a friend request."""
    friendship = get_object_or_404(Friendship, id=request_id, receiver=request.user, status='PENDING')
    friendship.status = 'REJECTED'
    friendship.save()

    return JsonResponse({'success': True})


@login_required
@require_POST
def remove_friend_view(request, user_id):
    """Remove a friend (unfriend)."""
    from django.contrib import messages

    other_user = get_object_or_404(User, id=user_id)

    # Find the friendship
    friendship = Friendship.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user),
        status='ACCEPTED'
    ).first()

    if not friendship:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'You are not friends with this user'}, status=400)
        messages.error(request, 'You are not friends with this user.')
        return redirect('users:profile')

    # Remove friendship
    friendship.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, f'You have removed {other_user.username} from your friends.')
    return redirect('users:profile')
