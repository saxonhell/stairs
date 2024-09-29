from django import forms
from .models import Movie, Review, Discussion, Comment, User, Director

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'director']

class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = ['name']


# Форма для создания отзыва
class ReviewForm(forms.ModelForm):
    user_name = forms.CharField(max_length=100, label="Username")

    class Meta:
        model = Review
        fields = ['user_name', 'review_text', 'movie']

# Форма для создания комментария
class CommentForm(forms.ModelForm):
    user_name = forms.CharField(max_length=100, label="Username")

    class Meta:
        model = Comment
        fields = ['user_name', 'comment_text', 'discussion']



# Форма для создания обсуждения
class DiscussionForm(forms.ModelForm):
    user_name = forms.CharField(max_length=100, label="Username")

    class Meta:
        model = Discussion
        fields = ['user_name', 'title', 'movie']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']