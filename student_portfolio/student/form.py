from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Movie, Review, Discussion, Comment, Director, CustomUser


class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']

class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser  # Указываем, что форма основана на модели CustomUser
        fields = ['username']  # Поля, которые будут доступны в форме

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie  # Указываем модель, для которой создаем форму
        fields = ['title', 'description', 'director']  # Указываем поля, которые хотим отображать на форме

    # Валидация для поля title
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError("Название фильма должно содержать не менее 3 символов.")
        return title

    # Валидация для поля description
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 5:
            raise forms.ValidationError("Описание фильма должно содержать не менее 5 символов.")
        return description

class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = ['name']

# Форма для создания отзыва
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text', 'movie']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text', 'discussion']


# Форма для создания обсуждения
class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'movie']