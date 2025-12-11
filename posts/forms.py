"""Forms for posts."""

from django import forms
from .models import Post, Comment, PostVisibility


class TextPostForm(forms.Form):
    """Form for creating text posts."""
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': "What's on your mind?",
            'rows': 4,
        }),
        max_length=5000
    )
    visibility = forms.ChoiceField(
        choices=PostVisibility.choices,
        initial=PostVisibility.PUBLIC,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ImagePostForm(forms.Form):
    """Form for creating image posts."""
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )
    caption = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Add a caption...',
            'rows': 3,
        }),
        max_length=2000
    )
    visibility = forms.ChoiceField(
        choices=PostVisibility.choices,
        initial=PostVisibility.PUBLIC,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class VideoPostForm(forms.Form):
    """Form for creating video posts."""
    video = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/*',
        })
    )
    caption = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Add a caption...',
            'rows': 3,
        }),
        max_length=2000
    )
    visibility = forms.ChoiceField(
        choices=PostVisibility.choices,
        initial=PostVisibility.PUBLIC,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CommentForm(forms.Form):
    """Form for adding comments."""
    text = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Write a comment...',
        }),
        max_length=1000
    )
