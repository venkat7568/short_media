"""
Matching strategies for dating app.

Uses Strategy pattern for different matching algorithms.
"""

from typing import List, Dict
from datetime import datetime, timedelta
from django.db.models import QuerySet, Q
from django.contrib.auth import get_user_model
from core.design_patterns.strategy import IStrategy


User = get_user_model()


class AttributeMatchingStrategy(IStrategy):
    """
    Attribute-based matching strategy.
    Matches users based on profile attributes (age, gender, location, interests).
    """

    def execute(self, user, users_queryset: QuerySet = None) -> List[Dict]:
        """
        Find matches based on user attributes.

        Args:
            user: The user to find matches for
            users_queryset: Optional queryset of users to search within

        Returns:
            List of dicts with 'user' and 'score' keys, sorted by score descending
        """
        if not hasattr(user, 'dating_preferences'):
            return []

        prefs = user.dating_preferences
        profile = user.profile

        if not prefs.is_active:
            return []

        # Base queryset
        if users_queryset is None:
            users_queryset = User.objects.select_related('profile', 'dating_preferences').all()

        # Exclude self and blocked users
        blocked_ids = profile.blocked_users.values_list('id', flat=True)
        users_queryset = users_queryset.exclude(
            Q(id=user.id) | Q(id__in=blocked_ids)
        )

        # Filter by active preferences
        users_queryset = users_queryset.filter(dating_preferences__is_active=True)

        # Calculate match scores
        matches = []
        for candidate in users_queryset:
            score = self._calculate_match_score(user, candidate)
            if score > 0:  # Only include if there's some match
                matches.append({
                    'user': candidate,
                    'score': score,
                    'breakdown': self._get_score_breakdown(user, candidate)
                })

        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches

    def _calculate_match_score(self, user, candidate) -> float:
        """Calculate match score between two users."""
        score = 0.0
        max_score = 100.0

        user_prefs = user.dating_preferences
        user_profile = user.profile
        candidate_prefs = candidate.dating_preferences
        candidate_profile = candidate.profile

        # Age compatibility (20 points max)
        if candidate_profile.date_of_birth:
            candidate_age = self._calculate_age(candidate_profile.date_of_birth)

            # Check if candidate's age is within user's preference range
            if user_prefs.min_age <= candidate_age <= user_prefs.max_age:
                score += 10

            # Check if user's age is within candidate's preference range
            if user_profile.date_of_birth:
                user_age = self._calculate_age(user_profile.date_of_birth)
                if candidate_prefs.min_age <= user_age <= candidate_prefs.max_age:
                    score += 10

        # Gender compatibility (15 points max)
        if user_prefs.preferred_gender == 'ANY' or user_prefs.preferred_gender == candidate_profile.gender:
            score += 7.5
        if candidate_prefs.preferred_gender == 'ANY' or candidate_prefs.preferred_gender == user_profile.gender:
            score += 7.5

        # Interests match (30 points max)
        user_interests = set(user_prefs.get_interests_list())
        candidate_interests = set(candidate_prefs.get_interests_list())

        if user_interests and candidate_interests:
            common_interests = user_interests & candidate_interests
            interest_score = (len(common_interests) / max(len(user_interests), len(candidate_interests))) * 30
            score += interest_score

        # Looking for compatibility (20 points max)
        if user_prefs.looking_for == 'ANY' or candidate_prefs.looking_for == 'ANY':
            score += 10
        elif user_prefs.looking_for == candidate_prefs.looking_for:
            score += 20

        # Location proximity (15 points max)
        # Simplified: Just check if locations are set and match
        if user_profile.location and candidate_profile.location:
            if user_profile.location.lower() == candidate_profile.location.lower():
                score += 15
            elif user_profile.location.lower() in candidate_profile.location.lower() or candidate_profile.location.lower() in user_profile.location.lower():
                score += 7.5

        return min(score, max_score)

    def _get_score_breakdown(self, user, candidate) -> Dict:
        """Get detailed breakdown of match score."""
        user_prefs = user.dating_preferences
        user_profile = user.profile
        candidate_prefs = candidate.dating_preferences
        candidate_profile = candidate.profile

        breakdown = {
            'age_match': 0,
            'gender_match': 0,
            'interests_match': 0,
            'looking_for_match': 0,
            'location_match': 0,
        }

        # Age
        if candidate_profile.date_of_birth and user_profile.date_of_birth:
            candidate_age = self._calculate_age(candidate_profile.date_of_birth)
            user_age = self._calculate_age(user_profile.date_of_birth)
            if user_prefs.min_age <= candidate_age <= user_prefs.max_age:
                breakdown['age_match'] += 10
            if candidate_prefs.min_age <= user_age <= candidate_prefs.max_age:
                breakdown['age_match'] += 10

        # Gender
        if user_prefs.preferred_gender == 'ANY' or user_prefs.preferred_gender == candidate_profile.gender:
            breakdown['gender_match'] += 7.5
        if candidate_prefs.preferred_gender == 'ANY' or candidate_prefs.preferred_gender == user_profile.gender:
            breakdown['gender_match'] += 7.5

        # Interests
        user_interests = set(user_prefs.get_interests_list())
        candidate_interests = set(candidate_prefs.get_interests_list())
        if user_interests and candidate_interests:
            common_interests = user_interests & candidate_interests
            breakdown['interests_match'] = (len(common_interests) / max(len(user_interests), len(candidate_interests))) * 30
            breakdown['common_interests'] = list(common_interests)

        # Looking for
        if user_prefs.looking_for == 'ANY' or candidate_prefs.looking_for == 'ANY':
            breakdown['looking_for_match'] = 10
        elif user_prefs.looking_for == candidate_prefs.looking_for:
            breakdown['looking_for_match'] = 20

        # Location
        if user_profile.location and candidate_profile.location:
            if user_profile.location.lower() == candidate_profile.location.lower():
                breakdown['location_match'] = 15
            elif user_profile.location.lower() in candidate_profile.location.lower() or candidate_profile.location.lower() in user_profile.location.lower():
                breakdown['location_match'] = 7.5

        return breakdown

    @staticmethod
    def _calculate_age(birth_date) -> int:
        """Calculate age from birth date."""
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


class BehavioralMatchingStrategy(IStrategy):
    """
    Behavioral matching strategy.
    Matches users based on activity patterns and engagement.
    """

    def execute(self, user, users_queryset: QuerySet = None) -> List[Dict]:
        """
        Find matches based on user behavior.

        Args:
            user: The user to find matches for
            users_queryset: Optional queryset of users to search within

        Returns:
            List of dicts with 'user' and 'score' keys, sorted by score descending
        """
        # Base queryset
        if users_queryset is None:
            users_queryset = User.objects.select_related('profile').all()

        # Exclude self
        users_queryset = users_queryset.exclude(id=user.id)

        # Calculate behavioral scores
        matches = []
        for candidate in users_queryset:
            score = self._calculate_behavioral_score(user, candidate)
            if score > 0:
                matches.append({
                    'user': candidate,
                    'score': score,
                })

        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches

    def _calculate_behavioral_score(self, user, candidate) -> float:
        """Calculate behavioral match score."""
        score = 0.0

        # Activity level similarity (30 points max)
        user_posts_count = user.posts.count()
        candidate_posts_count = candidate.posts.count()

        if user_posts_count > 0 and candidate_posts_count > 0:
            activity_similarity = 1 - abs(user_posts_count - candidate_posts_count) / max(user_posts_count, candidate_posts_count)
            score += activity_similarity * 30

        # Recent activity (20 points max)
        recent_date = datetime.now() - timedelta(days=7)
        user_recent_active = user.posts.filter(created_at__gte=recent_date).exists()
        candidate_recent_active = candidate.posts.filter(created_at__gte=recent_date).exists()

        if user_recent_active and candidate_recent_active:
            score += 20

        # Engagement pattern similarity (50 points max)
        user_likes_count = user.likes.count()
        user_comments_count = user.comments.count()
        candidate_likes_count = candidate.likes.count()
        candidate_comments_count = candidate.comments.count()

        if user_likes_count > 0 and candidate_likes_count > 0:
            likes_similarity = 1 - abs(user_likes_count - candidate_likes_count) / max(user_likes_count, candidate_likes_count)
            score += likes_similarity * 25

        if user_comments_count > 0 and candidate_comments_count > 0:
            comments_similarity = 1 - abs(user_comments_count - candidate_comments_count) / max(user_comments_count, candidate_comments_count)
            score += comments_similarity * 25

        return score


class CompositeMatchingStrategy(IStrategy):
    """
    Composite matching strategy.
    Combines multiple strategies with weights.
    """

    def __init__(self, strategies_with_weights=None):
        """
        Initialize composite strategy.

        Args:
            strategies_with_weights: List of tuples (strategy, weight)
                                   Default: [(AttributeMatchingStrategy(), 0.7), (BehavioralMatchingStrategy(), 0.3)]
        """
        if strategies_with_weights is None:
            strategies_with_weights = [
                (AttributeMatchingStrategy(), 0.7),
                (BehavioralMatchingStrategy(), 0.3),
            ]
        self.strategies_with_weights = strategies_with_weights

    def execute(self, user, users_queryset: QuerySet = None) -> List[Dict]:
        """
        Find matches using combined strategies.

        Args:
            user: The user to find matches for
            users_queryset: Optional queryset of users to search within

        Returns:
            List of dicts with 'user' and 'score' keys, sorted by score descending
        """
        # Collect all candidate users
        all_candidates = {}

        for strategy, weight in self.strategies_with_weights:
            matches = strategy.execute(user, users_queryset)
            for match in matches:
                candidate_id = match['user'].id
                if candidate_id not in all_candidates:
                    all_candidates[candidate_id] = {
                        'user': match['user'],
                        'score': 0.0,
                        'strategy_scores': {}
                    }
                # Add weighted score
                all_candidates[candidate_id]['score'] += match['score'] * weight
                all_candidates[candidate_id]['strategy_scores'][strategy.__class__.__name__] = match['score']

        # Convert to list and sort
        matches = list(all_candidates.values())
        matches.sort(key=lambda x: x['score'], reverse=True)

        return matches
