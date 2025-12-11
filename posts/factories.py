"""
Factory pattern implementation for creating posts.
"""

from core.design_patterns.factory import BaseFactory
from .models import TextPost, ImagePost, VideoPost, Post


class PostFactory(BaseFactory):
    """
    Factory for creating different types of posts.
    Implements Factory pattern from core.
    """

    def __init__(self):
        super().__init__()
        # Register post types
        self.register_product('TEXT', TextPost)
        self.register_product('IMAGE', ImagePost)
        self.register_product('VIDEO', VideoPost)

    def create_text_post(self, author, text, **kwargs):
        """Create a text post."""
        return TextPost.objects.create(
            author=author,
            text=text,
            **kwargs
        )

    def create_image_post(self, author, image, caption='', **kwargs):
        """Create an image post."""
        return ImagePost.objects.create(
            author=author,
            image=image,
            caption=caption,
            **kwargs
        )

    def create_video_post(self, author, video, caption='', duration=0, thumbnail=None, **kwargs):
        """Create a video post."""
        return VideoPost.objects.create(
            author=author,
            video=video,
            caption=caption,
            duration=duration,
            thumbnail=thumbnail,
            **kwargs
        )

    def create_post(self, post_type, **kwargs):
        """
        Create a post using the registered type.

        Args:
            post_type: Type of post ('TEXT', 'IMAGE', 'VIDEO')
            **kwargs: Arguments for post creation

        Returns:
            Post: Created post instance
        """
        if post_type == 'TEXT':
            return self.create_text_post(**kwargs)
        elif post_type == 'IMAGE':
            return self.create_image_post(**kwargs)
        elif post_type == 'VIDEO':
            return self.create_video_post(**kwargs)
        else:
            raise ValueError(f"Unknown post type: {post_type}")


# Singleton instance
post_factory = PostFactory()
