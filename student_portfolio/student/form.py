from django import forms
from .models import Movie, Review

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text', 'movie']