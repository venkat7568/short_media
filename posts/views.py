"""
Views for posts app.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST

from .models import Post
from .forms import TextPostForm, ImagePostForm, VideoPostForm, CommentForm
from .services import PostService, FeedService, CommentService, LikeService
from .strategies.ranking import RecencyRankingStrategy, EngagementRankingStrategy

# Initialize services
post_service = PostService()
feed_service = FeedService()
comment_service = CommentService()
like_service = LikeService()


@login_required
def home_view(request):
    """Display the home feed."""
    # Get ranking preference from query params or session
    ranking = request.GET.get('ranking', 'recency')

    if ranking == 'engagement':
        feed_service.set_ranking_strategy(EngagementRankingStrategy())
    else:
        feed_service.set_ranking_strategy(RecencyRankingStrategy())

    posts = feed_service.get_feed(user=request.user, limit=20)

    # Get user's liked posts
    user_liked_post_ids = list(request.user.likes.values_list('post_id', flat=True))

    return render(request, 'posts/home.html', {
        'posts': posts,
        'current_ranking': ranking,
        'user_liked_post_ids': user_liked_post_ids,
    })

# Alias for backward compatibility
feed_view = home_view


@login_required
@require_http_methods(["GET", "POST"])
def create_post_view(request):
    """Create a new post."""
    post_type = request.GET.get('type', 'text')

    if request.method == 'POST':
        if post_type == 'text':
            form = TextPostForm(request.POST)
            if form.is_valid():
                post = post_service.create_text_post(
                    author=request.user,
                    text=form.cleaned_data['text'],
                    visibility=form.cleaned_data['visibility']
                )
                messages.success(request, 'Post created successfully!')
                return redirect('posts:feed')

        elif post_type == 'image':
            form = ImagePostForm(request.POST, request.FILES)
            if form.is_valid():
                post = post_service.create_image_post(
                    author=request.user,
                    image=request.FILES['image'],
                    caption=form.cleaned_data['caption'],
                    visibility=form.cleaned_data['visibility']
                )
                messages.success(request, 'Image post created successfully!')
                return redirect('posts:feed')

        elif post_type == 'video':
            form = VideoPostForm(request.POST, request.FILES)
            if form.is_valid():
                post = post_service.create_video_post(
                    author=request.user,
                    video=request.FILES['video'],
                    caption=form.cleaned_data['caption'],
                    visibility=form.cleaned_data['visibility']
                )
                messages.success(request, 'Video post created successfully!')
                return redirect('posts:feed')
    else:
        if post_type == 'text':
            form = TextPostForm()
        elif post_type == 'image':
            form = ImagePostForm()
        elif post_type == 'video':
            form = VideoPostForm()
        else:
            form = TextPostForm()

    return render(request, 'posts/create_post.html', {
        'form': form,
        'post_type': post_type,
    })


@login_required
def post_detail_view(request, post_id):
    """View a single post with comments."""
    post = get_object_or_404(Post, id=post_id)

    # Increment views
    post_service.increment_view(post)

    # Get comments
    comments = comment_service.get_comments(post)

    # Check if user has liked
    user_has_liked = like_service.has_liked(post, request.user)

    # Handle comment form
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_service.add_comment(
                post=post,
                author=request.user,
                text=form.cleaned_data['text']
            )
            messages.success(request, 'Comment added!')
            return redirect('posts:post_detail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'user_has_liked': user_has_liked,
        'form': form,
    })


@login_required
@require_POST
def like_post_view(request, post_id):
    """Toggle like on a post (AJAX)."""
    post = get_object_or_404(Post, id=post_id)

    liked = like_service.toggle_like(post, request.user)

    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes_count,
    })


@login_required
@require_POST
def delete_post_view(request, post_id):
    """Delete a post."""
    post = get_object_or_404(Post, id=post_id)

    if post_service.delete_post(post, request.user):
        messages.success(request, 'Post deleted successfully!')
    else:
        messages.error(request, 'You can only delete your own posts.')

    return redirect('posts:feed')


@login_required
def user_posts_view(request, username):
    """View posts by a specific user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user = get_object_or_404(User, username=username)
    posts = post_service.get_user_posts(user)

    # Check which posts the current user has liked
    for post in posts:
        post.user_has_liked = like_service.has_liked(post, request.user)

    return render(request, 'posts/user_posts.html', {
        'profile_user': user,
        'posts': posts,
    })


@login_required
def trending_posts_view(request):
    """View trending/popular posts ranked by hashtags (likes)."""
    # Use engagement ranking strategy
    from .strategies.ranking import EngagementRankingStrategy
    trending_feed_service = FeedService(ranking_strategy=EngagementRankingStrategy())

    posts = trending_feed_service.get_feed(request.user, limit=50)

    # Check which posts user has liked
    user_liked_post_ids = list(request.user.likes.values_list('post_id', flat=True))

    return render(request, 'posts/trending.html', {
        'posts': posts,
        'user_liked_post_ids': user_liked_post_ids,
    })
