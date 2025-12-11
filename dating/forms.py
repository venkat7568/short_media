"""Forms for dating app."""

from django import forms
from .models import UserPreferences, MatchRequest


class UserPreferencesForm(forms.ModelForm):
    """Form for user dating preferences."""

    interests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your interests separated by commas (e.g., Movies, Music, Sports)'
        }),
        help_text='Enter your interests separated by commas'
    )

    class Meta:
        model = UserPreferences
        fields = [
            'min_age',
            'max_age',
            'preferred_gender',
            'max_distance',
            'preferred_location',
            'interests',
            'looking_for',
            'is_active'
        ]
        widgets = {
            'min_age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 18,
                'max': 100,
                'placeholder': '18'
            }),
            'max_age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 18,
                'max': 100,
                'placeholder': '100'
            }),
            'preferred_gender': forms.Select(attrs={'class': 'form-control'}),
            'max_distance': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 1000,
                'placeholder': '50'
            }),
            'preferred_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City or region'
            }),
            'looking_for': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'min_age': 'Minimum Age',
            'max_age': 'Maximum Age',
            'preferred_gender': 'Preferred Gender',
            'max_distance': 'Maximum Distance (km)',
            'preferred_location': 'Preferred Location',
            'interests': 'Interests',
            'looking_for': 'Looking For',
            'is_active': 'Active (Show my profile in matches)',
        }

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        min_age = cleaned_data.get('min_age')
        max_age = cleaned_data.get('max_age')

        if min_age and max_age and min_age > max_age:
            raise forms.ValidationError('Minimum age cannot be greater than maximum age')

        return cleaned_data


class MatchRequestForm(forms.Form):
    """Form for sending match requests."""

    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Write an optional message (e.g., "Hi! I think we have similar interests...")'
        }),
        max_length=500,
        label='Message (Optional)'
    )
