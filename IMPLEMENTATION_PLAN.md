# Short Media Platform - Implementation Plan

## Overview
Building a traditional Django web application with clean architecture, featuring social posts, dating, video calls, and real-time notifications with a green-white theme.

## Technology Stack

### Backend
- **Django 5.0**: Web framework
- **Django REST Framework**: API endpoints for AJAX/WebSocket
- **Django Channels**: WebSocket support for real-time features
- **djangorestframework-simplejwt**: JWT authentication
- **Pillow**: Image processing
- **python-decouple**: Environment variable management
- **mysqlclient**: MySQL database connector
- **Redis**: Channel layer backend for Django Channels

### Frontend
- **Bootstrap 5**: Base UI framework
- **Custom CSS**: Green-white theme
- **JavaScript/AJAX**: Dynamic interactions
- **WebRTC**: Video calling functionality

### Database
- **SQLite**: Development
- **MySQL**: Production (configured via .env)

## Project Structure

```
short_media/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── config/                          # Project configuration
│   ├── __init__.py
│   ├── settings.py                  # Django settings
│   ├── urls.py                      # Root URL configuration
│   ├── asgi.py                      # ASGI for Channels
│   ├── wsgi.py                      # WSGI
│   └── routing.py                   # WebSocket routing
├── core/                            # Shared utilities
│   ├── __init__.py
│   ├── base_models.py              # Abstract base models
│   ├── exceptions.py               # Custom exceptions
│   ├── utils.py                    # Utility functions
│   └── design_patterns/            # Reusable pattern implementations
│       ├── strategy.py
│       ├── factory.py
│       ├── builder.py
│       └── state.py
├── users/                          # User authentication & profiles
│   ├── models.py                   # User, UserProfile, OTPVerification
│   ├── services.py                 # AuthenticationService, ProfileService
│   ├── repositories.py             # UserRepository
│   ├── views.py                    # Login, signup, profile views
│   ├── api.py                      # API endpoints
│   ├── serializers.py              # DRF serializers
│   ├── forms.py                    # Django forms
│   ├── urls.py                     # URL routing
│   └── templates/users/            # HTML templates
│       ├── signup.html
│       ├── login.html
│       ├── verify_otp.html
│       └── profile.html
├── posts/                          # Social posts system
│   ├── models.py                   # Post, TextPost, ImagePost, VideoPost, Comment, Like
│   ├── services.py                 # PostService, FeedService
│   ├── repositories.py             # PostRepository
│   ├── strategies/                 # Strategy pattern implementations
│   │   ├── ranking.py              # Feed ranking strategies
│   │   └── filters.py              # Post filters
│   ├── factories.py                # PostFactory
│   ├── views.py                    # Feed, post detail, create post views
│   ├── api.py                      # API endpoints
│   ├── urls.py
│   └── templates/posts/
│       ├── feed.html
│       ├── post_detail.html
│       └── create_post.html
├── dating/                         # Dating/matching features
│   ├── models.py                   # MatchRequest, UserPreferences
│   ├── services.py                 # DatingService, MatchingService
│   ├── repositories.py             # MatchRequestRepository
│   ├── strategies/                 # Matching strategies
│   │   ├── attribute_matching.py
│   │   └── behavioral_matching.py
│   ├── builders.py                 # SearchQueryBuilder
│   ├── views.py                    # Match feed, requests views
│   ├── api.py
│   ├── urls.py
│   └── templates/dating/
│       ├── matches.html
│       ├── requests.html
│       └── preferences.html
├── video_calls/                    # Video calling system
│   ├── models.py                   # VideoCallSession
│   ├── services.py                 # VideoCallService
│   ├── repositories.py             # VideoCallRepository
│   ├── states.py                   # State pattern: RingingState, ActiveState, etc.
│   ├── views.py                    # Call interface views
│   ├── api.py
│   ├── consumers.py                # WebSocket consumers for signaling
│   ├── routing.py                  # WebSocket routing
│   ├── urls.py
│   └── templates/video_calls/
│       ├── call.html
│       └── incoming_call.html
├── notifications/                  # Notification system
│   ├── models.py                   # Notification
│   ├── services.py                 # NotificationService
│   ├── repositories.py             # NotificationRepository
│   ├── strategies/                 # Notification channel strategies
│   │   ├── push_notification.py
│   │   ├── email_notification.py
│   │   └── sms_notification.py
│   ├── consumers.py                # WebSocket consumers for real-time notifications
│   ├── api.py
│   ├── urls.py
│   └── templates/notifications/
│       └── notification_list.html
├── static/                         # Static files
│   ├── css/
│   │   ├── base.css               # Green-white theme
│   │   ├── auth.css
│   │   ├── posts.css
│   │   ├── dating.css
│   │   └── video_calls.css
│   ├── js/
│   │   ├── main.js
│   │   ├── posts.js
│   │   ├── dating.js
│   │   ├── video_calls.js         # WebRTC implementation
│   │   └── notifications.js       # WebSocket client
│   └── images/
│       └── logo.png
├── media/                          # User-uploaded files
│   ├── profile_pictures/
│   ├── posts/
│   │   ├── images/
│   │   └── videos/
│   └── thumbnails/
└── templates/                      # Global templates
    ├── base.html                   # Base template with navbar
    ├── home.html                   # Landing page
    └── components/
        ├── navbar.html
        └── notification_bell.html
```

## Implementation Phases

### Phase 1: Project Setup & User Authentication (Days 1-3)
**Goal**: Users can sign up with email, verify OTP, and login with JWT

#### Tasks:
1. **Project Initialization**
   - Create Django project with proper structure
   - Install dependencies (Django, DRF, Channels, JWT, etc.)
   - Configure settings for SQLite/MySQL switching
   - Set up .env integration with python-decouple
   - Configure static and media files

2. **Core Infrastructure**
   - Create `core` app with base models and utilities
   - Implement design pattern base classes (Strategy, Factory, etc.)
   - Set up custom exceptions
   - Create base repository pattern

3. **User Authentication**
   - Custom User model extending AbstractUser
   - UserProfile model (bio, profile picture, preferences)
   - OTPVerification model (email, code, expiry, is_verified)
   - AuthenticationService with email OTP flow
   - UserRepository for data access

4. **Views & Templates**
   - Signup page (email, password, username)
   - OTP verification page (6-digit code input)
   - Login page (email/password)
   - Profile page (view/edit profile)
   - Green-white themed CSS

5. **JWT Integration**
   - Configure djangorestframework-simplejwt
   - Custom token authentication middleware
   - Token refresh endpoints

6. **Email Service**
   - SMTP configuration using .env credentials
   - Email template for OTP
   - OTP generation and validation (6 digits, 10-minute expiry)

### Phase 2: Posts System & Feed (Days 4-6)
**Goal**: Users can create text/image/video posts, view feed with ranking

#### Tasks:
1. **Domain Models**
   - Abstract Post model
   - TextPost, ImagePost, VideoPost (Factory pattern)
   - Comment model
   - Like model
   - PostVisibility enum (PUBLIC, FRIENDS, PRIVATE)

2. **Service Layer**
   - PostFactory (creates appropriate post type)
   - PostService (CRUD operations)
   - FeedService (orchestrates ranking and filtering)
   - PostRepository

3. **Strategy Implementations**
   - RecencyRankingStrategy
   - EngagementRankingStrategy (likes*2 + views)
   - PersonalizedRankingStrategy (future: ML-based)
   - VisibilityFilter
   - BlockedUsersFilter
   - ContentModerationFilter

4. **Views & Templates**
   - Feed page with infinite scroll
   - Create post modal (select type: text/image/video)
   - Post detail page with comments
   - Like/comment AJAX endpoints
   - File upload handling for images/videos

5. **Frontend**
   - Facebook-style feed layout
   - Post creation form with type selection
   - Image/video preview before upload
   - Real-time like/comment updates

### Phase 3: Dating Features (Days 7-9)
**Goal**: Users can find matches, send requests, accept/reject

#### Tasks:
1. **Domain Models**
   - MatchRequest (sender, receiver, status, timestamp)
   - UserPreferences (age range, location, interests)
   - MatchStatus enum (PENDING, ACCEPTED, REJECTED, BLOCKED)

2. **Service Layer**
   - DatingService (orchestration)
   - MatchingService (applies strategies)
   - MatchRequestRepository
   - SearchQueryBuilder (Builder pattern)

3. **Strategy Implementations**
   - AttributeMatchingStrategy (age, location, interests)
   - BehavioralMatchingStrategy (activity patterns)
   - MLMatchingStrategy (placeholder for future)

4. **Views & Templates**
   - Match discovery page (swipeable cards)
   - Match requests page (pending/accepted)
   - User preferences settings
   - Chat interface for matched users

5. **API Endpoints**
   - GET /api/dating/matches (paginated matches)
   - POST /api/dating/request (send match request)
   - PUT /api/dating/request/:id/accept
   - PUT /api/dating/request/:id/reject
   - PUT /api/dating/request/:id/block

### Phase 4: Video Calls (Days 10-12)
**Goal**: Users can initiate video calls, receive calls, manage call state

#### Tasks:
1. **Domain Models**
   - VideoCallSession (caller, receiver, state, timestamps)
   - CallState interface with implementations:
     - RingingState
     - ActiveState
     - EndedState
     - MissedState

2. **Service Layer**
   - VideoCallService (manages lifecycle)
   - VideoCallRepository
   - State machine implementation

3. **WebRTC Integration**
   - Django Channels consumers for signaling
   - WebSocket routing for call events
   - STUN/TURN server configuration
   - Frontend WebRTC implementation (offer/answer/ICE)

4. **Views & Templates**
   - Call initiation button on profiles
   - Incoming call modal (accept/reject)
   - Video call interface (full-screen)
   - Call history page

5. **API Endpoints**
   - POST /api/calls/initiate
   - PUT /api/calls/:id/answer
   - PUT /api/calls/:id/end
   - GET /api/calls/history

### Phase 5: Notifications System (Days 13-14)
**Goal**: Real-time notifications for all platform events

#### Tasks:
1. **Domain Models**
   - Notification (user, type, content, read status, timestamp)
   - NotificationType enum (LIKE, COMMENT, MATCH_REQUEST, CALL, etc.)

2. **Service Layer**
   - NotificationService (orchestrates channels)
   - NotificationRepository
   - Strategy implementations:
     - PushNotificationStrategy
     - EmailNotificationStrategy
     - SMSNotificationStrategy

3. **WebSocket Integration**
   - Django Channels consumer for notifications
   - Real-time notification delivery
   - Read/unread status management

4. **Views & Templates**
   - Notification bell icon with count
   - Notification dropdown/page
   - Mark as read functionality

5. **Integration**
   - Hook notification triggers into all services:
     - PostService → notify on like/comment
     - DatingService → notify on match request
     - VideoCallService → notify on incoming call

### Phase 6: Frontend Polish & Theme (Days 15-16)
**Goal**: Cohesive green-white theme, responsive design, smooth UX

#### Tasks:
1. **Theme Implementation**
   - Define green color palette (#00C851, #007E33, etc.)
   - Base styles in base.css
   - Component-specific styles
   - Dark green navbar, white backgrounds
   - Green CTAs and hover states

2. **Responsive Design**
   - Mobile-first approach
   - Breakpoints for tablet/desktop
   - Touch-friendly buttons
   - Responsive navigation

3. **UX Enhancements**
   - Loading spinners
   - Toast notifications
   - Smooth transitions
   - Form validation feedback
   - Error handling

4. **Performance Optimization**
   - Image lazy loading
   - Video thumbnail generation
   - Query optimization
   - Caching strategy

## Design Patterns Implementation Details

### Strategy Pattern
```python
# Example: Feed Ranking
class IFeedRankingStrategy(ABC):
    @abstractmethod
    def rank(self, posts: QuerySet, user: User) -> QuerySet:
        pass

class RecencyRankingStrategy(IFeedRankingStrategy):
    def rank(self, posts: QuerySet, user: User) -> QuerySet:
        return posts.order_by('-created_at')

class EngagementRankingStrategy(IFeedRankingStrategy):
    def rank(self, posts: QuerySet, user: User) -> QuerySet:
        return posts.annotate(
            score=F('likes_count') * 2 + F('views_count')
        ).order_by('-score')

# Usage in FeedService
class FeedService:
    def __init__(self, ranking_strategy: IFeedRankingStrategy):
        self.ranking_strategy = ranking_strategy

    def get_feed(self, user: User, limit: int) -> QuerySet:
        posts = Post.objects.filter(visibility='PUBLIC')
        posts = self.ranking_strategy.rank(posts, user)
        return posts[:limit]
```

### Factory Pattern
```python
# Example: Post Creation
class PostFactory:
    @staticmethod
    def create_post(post_type: str, data: dict) -> Post:
        if post_type == 'TEXT':
            return TextPost.objects.create(**data)
        elif post_type == 'IMAGE':
            return ImagePost.objects.create(**data)
        elif post_type == 'VIDEO':
            return VideoPost.objects.create(**data)
        else:
            raise ValueError(f"Unknown post type: {post_type}")

# Usage in PostService
class PostService:
    def create_post(self, user: User, post_type: str, data: dict) -> Post:
        data['author'] = user
        post = PostFactory.create_post(post_type, data)
        return post
```

### State Pattern
```python
# Example: Video Call States
class CallState(ABC):
    @abstractmethod
    def ring(self, session: VideoCallSession): pass

    @abstractmethod
    def answer(self, session: VideoCallSession): pass

    @abstractmethod
    def end(self, session: VideoCallSession): pass

class RingingState(CallState):
    def ring(self, session): pass  # Already ringing

    def answer(self, session):
        session.state = ActiveState()
        session.start_time = timezone.now()
        session.save()

    def end(self, session):
        session.state = MissedState()
        session.save()

# Usage in VideoCallService
class VideoCallService:
    def initiate_call(self, caller: User, receiver: User) -> VideoCallSession:
        session = VideoCallSession.objects.create(
            caller=caller,
            receiver=receiver,
            state=RingingState()
        )
        session.state.ring(session)
        return session
```

### Builder Pattern
```python
# Example: Match Search Query
class SearchQueryBuilder:
    def __init__(self):
        self.query = Q()

    def with_age_range(self, min_age: int, max_age: int):
        self.query &= Q(age__gte=min_age, age__lte=max_age)
        return self

    def with_location(self, lat: float, lon: float, radius: int):
        # Simplified - use proper geospatial query
        self.query &= Q(location__distance_lt=(lat, lon, radius))
        return self

    def with_interests(self, interests: list):
        self.query &= Q(interests__overlap=interests)
        return self

    def build(self) -> Q:
        return self.query

# Usage in DatingService
builder = SearchQueryBuilder()
query = builder.with_age_range(25, 35)\
               .with_location(lat, lon, 50)\
               .with_interests(['music', 'sports'])\
               .build()
matches = User.objects.filter(query)
```

## Database Schema Highlights

### Users App
- **User**: id, email (unique), username, password_hash, is_verified, created_at
- **UserProfile**: user_id (FK), bio, profile_picture, age, location, interests (JSON)
- **OTPVerification**: user_id (FK), code, created_at, expires_at, is_used

### Posts App
- **Post** (abstract): id, author_id (FK), content, visibility, likes_count, views_count, created_at
- **TextPost**: post_ptr_id (FK), text
- **ImagePost**: post_ptr_id (FK), image_url, caption
- **VideoPost**: post_ptr_id (FK), video_url, duration, thumbnail_url
- **Comment**: id, post_id (FK), author_id (FK), text, created_at
- **Like**: id, post_id (FK), user_id (FK), created_at

### Dating App
- **MatchRequest**: id, sender_id (FK), receiver_id (FK), status, created_at, updated_at
- **UserPreferences**: user_id (FK), min_age, max_age, max_distance, interests (JSON)

### Video Calls App
- **VideoCallSession**: id, caller_id (FK), receiver_id (FK), status, start_time, end_time, duration

### Notifications App
- **Notification**: id, user_id (FK), type, content (JSON), is_read, created_at

## Configuration Details

### settings.py
```python
# Database switching based on environment
if os.getenv('USE_MYSQL', 'False') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# JWT configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Channels configuration
ASGI_APPLICATION = 'config.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

## Testing Strategy

### Unit Tests
- Test each service in isolation with mocked repositories
- Test strategy implementations with sample data
- Test state transitions in video call states

### Integration Tests
- Test full authentication flow (signup → OTP → login)
- Test post creation and feed generation
- Test match request lifecycle

### E2E Tests
- Test user journey from signup to creating first post
- Test complete dating flow
- Test video call initiation and acceptance

## Deployment Considerations

### Development
- SQLite database
- Django development server
- Local file storage

### Production
- MySQL database (configured in .env)
- Gunicorn + Nginx
- Redis for Channels
- Media files on filesystem (upgrade to S3 later)
- HTTPS for secure WebSocket connections
- Proper CORS configuration

## Success Criteria

✅ Users can sign up with email and verify via OTP
✅ Users can login and maintain JWT session
✅ Users can create text/image/video posts
✅ Feed displays posts with configurable ranking
✅ Users can like and comment on posts
✅ Users can discover matches based on preferences
✅ Users can send/accept/reject match requests
✅ Users can initiate video calls
✅ Video calls support WebRTC audio/video
✅ Real-time notifications for all events
✅ Green-white themed responsive UI
✅ Clean architecture with design patterns
✅ SQLite for dev, MySQL for production
✅ Easy to extend with new features

## Timeline Estimate
- **Phase 1**: 3 days (Setup + Auth)
- **Phase 2**: 3 days (Posts + Feed)
- **Phase 3**: 3 days (Dating)
- **Phase 4**: 3 days (Video Calls)
- **Phase 5**: 2 days (Notifications)
- **Phase 6**: 2 days (Polish)
- **Total**: 16 days (can be parallelized with team)

## Next Steps
Once approved, we'll start with Phase 1:
1. Initialize Django project
2. Set up core infrastructure
3. Implement user authentication with OTP
4. Create green-white themed login/signup pages
