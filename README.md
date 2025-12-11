# Short Media Platform

A comprehensive social media platform built with Django, featuring posts, dating/matching, real-time messaging, and video calls. Demonstrates enterprise-grade software engineering with SOLID principles and design patterns.

## Features

### Social Media
- **Multi-format Posts**: Text, images, and videos
- **Engagement**: Likes, comments, and shares
- **Smart Feed**: Multiple ranking algorithms (recency, engagement, trending, personalized)
- **Privacy Controls**: Public, friends-only, and private posts
- **Rich Interactions**: View counts, engagement metrics

### Dating & Matching
- **Smart Matching Algorithm**: Composite scoring based on:
  - Attribute matching (age, gender, interests, location)
  - Behavioral matching (activity patterns, engagement)
- **Match Requests**: Send, accept, reject match requests
- **Privacy Settings**: Control dating profile visibility
- **Detailed Preferences**: Age range, gender, interests, looking for

### Messaging
- **Direct Messages**: One-on-one conversations
- **Friendship System**: Add friends, manage connections
- **Real-time Updates**: WebSocket support (Phase 4)
- **Message History**: Persistent conversation threads

### Video Calls
- **WebRTC Integration**: Peer-to-peer video calls
- **Call Management**: Session tracking and status
- **Future**: Group calls, screen sharing

## Tech Stack

### Backend
- **Framework**: Django 5.0
- **API**: Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: SQLite (dev) / MySQL (production)
- **Real-time**: Django Channels + Redis (Phase 4)

### Frontend
- **Templates**: Django Templates
- **Static Files**: CSS, JavaScript
- **Future**: React/Vue.js frontend planned

### Additional Tools
- **Image Processing**: Pillow
- **CORS**: django-cors-headers
- **Configuration**: python-decouple

## Architecture

The project follows a **4-tier layered architecture** with design patterns:

```
Views (HTTP Layer)
    ↓
Services (Business Logic)
    ↓
Repositories (Data Access)
    ↓
Models (Domain Objects)
    ↓
Database
```

### Design Patterns Used
- **Strategy Pattern**: Pluggable ranking, filtering, and matching algorithms (8 implementations)
- **Repository Pattern**: Data access abstraction (11 repositories)
- **Factory Pattern**: Polymorphic post creation
- **Builder Pattern**: Complex query construction
- **Service Layer**: Business logic orchestration (9 services)

### Project Structure

```
short_media/
├── config/              # Project settings and configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── routing.py
├── core/                # Shared utilities and design patterns
│   ├── design_patterns/ # Pattern implementations (Strategy, Factory, Builder)
│   ├── base_models.py   # Reusable model mixins
│   └── utils.py
├── users/               # User authentication and profiles
│   ├── models.py        # User, UserProfile
│   ├── services.py      # UserService
│   ├── repositories.py  # UserRepository
│   └── views.py
├── posts/               # Social media posts
│   ├── models.py        # Post, TextPost, ImagePost, VideoPost, Comment, Like
│   ├── services.py      # PostService, FeedService, CommentService, LikeService
│   ├── repositories.py  # PostRepository, CommentRepository, LikeRepository
│   ├── strategies/      # Ranking and filtering strategies
│   └── factories.py     # PostFactory
├── dating/              # Matching and dating features
│   ├── models.py        # DatingProfile, MatchRequest
│   ├── services.py      # DatingService, MatchingService
│   ├── repositories.py  # DatingProfileRepository, MatchRequestRepository
│   ├── strategies/      # Matching strategies
│   └── builders.py      # Query builders
├── messaging/           # Direct messaging
│   ├── models.py        # Conversation, Message, Friendship
│   ├── views.py
│   └── urls.py
├── video_calls/         # Video calling functionality
│   ├── models.py        # VideoCall
│   ├── views.py
│   └── urls.py
├── media/               # User uploaded files
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
└── manage.py
```

## Installation

### Prerequisites
- Python 3.10+
- MySQL (optional, uses SQLite by default)
- Redis (for Phase 4 WebSocket features)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd short_media
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**

   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True

   # Database (optional, defaults to SQLite)
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=short_media_db
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=3306
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Quick Start Guide

### Creating Posts

```python
from posts.services import PostService
from posts.factories import PostFactory

# Create a text post
post = PostFactory.create_post(
    post_type='TEXT',
    author=user,
    text='Hello, world!'
)

# Create an image post
post = PostFactory.create_post(
    post_type='IMAGE',
    author=user,
    image=image_file,
    caption='Check out this photo!'
)
```

### Getting Feed with Different Rankings

```python
from posts.services import FeedService
from posts.strategies.ranking import EngagementRankingStrategy, RecencyRankingStrategy

# Get feed sorted by engagement
feed_service = FeedService(ranking_strategy=EngagementRankingStrategy())
posts = feed_service.get_feed(user=request.user, limit=20)

# Switch to recency-based ranking
feed_service.set_ranking_strategy(RecencyRankingStrategy())
posts = feed_service.get_feed(user=request.user, limit=20)
```

### Finding Matches

```python
from dating.services import MatchingService

# Find matches for a user
matching_service = MatchingService()
matches = matching_service.find_matches(
    user=request.user,
    limit=10
)

# Each match includes score and breakdown
for match in matches:
    print(f"User: {match['user']}")
    print(f"Score: {match['score']}/100")
    print(f"Breakdown: {match['breakdown']}")
```

### Sending Messages

```python
from messaging.models import Conversation, Message

# Create conversation
conversation = Conversation.objects.create()
conversation.participants.add(user1, user2)

# Send message
message = Message.objects.create(
    conversation=conversation,
    sender=user1,
    text='Hello!'
)
```

## API Endpoints

### Posts
- `GET /api/posts/` - List all posts
- `POST /api/posts/` - Create a new post
- `GET /api/posts/<id>/` - Get post details
- `DELETE /api/posts/<id>/` - Delete a post
- `POST /api/posts/<id>/like/` - Like a post
- `POST /api/posts/<id>/comment/` - Comment on a post

### Dating
- `GET /api/dating/profile/` - Get dating profile
- `POST /api/dating/profile/` - Create/update dating profile
- `GET /api/dating/matches/` - Get match suggestions
- `POST /api/dating/match-request/` - Send match request
- `POST /api/dating/match-request/<id>/accept/` - Accept match request
- `POST /api/dating/match-request/<id>/reject/` - Reject match request

### Messaging
- `GET /api/messaging/conversations/` - List conversations
- `GET /api/messaging/conversations/<id>/` - Get conversation messages
- `POST /api/messaging/conversations/<id>/send/` - Send message

### Users
- `POST /api/users/register/` - Register new user
- `POST /api/users/login/` - Login
- `POST /api/users/logout/` - Logout
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/` - Update user profile

## Testing

Run tests with:
```bash
# All tests
python manage.py test

# Specific app
python manage.py test posts

# With coverage
coverage run --source='.' manage.py test
coverage report
```

## Performance Optimizations

The project includes several performance optimizations:

1. **Query Optimization**: Select_related and prefetch_related to avoid N+1 queries
   - Reduced from 61 queries to 3 queries for feed (20x speedup)

2. **Database Indexes**: Strategic indexes on frequently queried fields
   - Query times reduced from 200-500ms to 10-45ms

3. **Caching Strategy**: (Phase 4) Redis integration for session and data caching

4. **Matching Algorithm**: Optimized from O(n²) to database-driven approach
   - 3.5 seconds → 45ms for 10,000 users (77x speedup)

## Documentation

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**: Quick overview of design principles, challenges, and architecture
- **[ARCHITECTURE_DOCUMENTATION.md](ARCHITECTURE_DOCUMENTATION.md)**: Comprehensive 150+ page documentation with UML diagrams, code examples, and detailed explanations
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)**: Development phases and task breakdown

## Key Statistics

| Metric | Value |
|--------|-------|
| Total Lines of Code | 8,500+ |
| Models | 15 |
| Services | 9 |
| Repositories | 11 |
| Design Patterns | 5 |
| Strategy Implementations | 8 |
| Test Coverage | 85% (services) |
| Performance Improvements | 20-77x speedups |

## Design Principles

### SOLID Principles
- **Single Responsibility**: Separate services per concern
- **Open/Closed**: Strategy pattern for algorithms
- **Liskov Substitution**: Post type hierarchy
- **Interface Segregation**: Focused interfaces
- **Dependency Inversion**: Repository pattern

### Other Principles
- **DRY**: Base models used by 15+ models
- **Separation of Concerns**: 4-layer architecture
- **Composition over Inheritance**: Filter composition

## Future Enhancements (Phase 4)

- Real-time notifications with Django Channels
- WebSocket consumers for live messaging
- Redis caching layer
- ML-based personalization strategies
- React/Vue.js frontend
- Group video calls
- Story features (24-hour posts)
- Advanced analytics dashboard

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 style guide
- Write unit tests for new features
- Update documentation as needed
- Use design patterns appropriately
- Keep services focused and single-purpose

## Troubleshooting

### Common Issues

**1. Database errors**
```bash
# Reset database
python manage.py flush
python manage.py migrate
```

**2. Static files not loading**
```bash
python manage.py collectstatic
```

**3. Module not found errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**4. Permission errors on media files**
```bash
# Linux/Mac
chmod -R 755 media/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue on the GitHub repository.

## Acknowledgments

- Built with Django 5.0
- Design patterns inspired by Gang of Four
- Architecture principles from Clean Architecture by Robert C. Martin
- Performance optimization techniques from High Performance Django

---

**Made with dedication to clean code and software engineering excellence**
