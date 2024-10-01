from django import forms
from .models import Movie, Review, Discussion, Comment, User, Director

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