from math import trunc

from django.db import models
from django.core.exceptions import ValidationError


def validate_movie_title(value):
    if len(value) < 3:
        raise ValidationError('Название фильма должно содержать не менее 3 символов')

# Модель режиссёра
class Director(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Модель фильма
class Movie(models.Model):
    title = models.CharField(max_length=100, validators=[validate_movie_title])
    description = models.TextField()
    director = models.ForeignKey(Director, on_delete=models.CASCADE, related_name='movies', null=True)

    def __str__(self):
        return self.title


# Модель пользователя
class User(models.Model):
    username = models.CharField(max_length=100)  # Имя пользователя, вводимое вручную

    def __str__(self):
        return self.username

# Модель отзыва, связанная с фильмом и пользователем
class Review(models.Model):
    review_text = models.TextField()  # Текст отзыва
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews', null=True)  # Связь с фильмом
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True)  # Связь с пользователем

    def __str__(self):
        return f'{self.user.username}: {self.review_text}'

class Discussion(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions', null=True)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)  # время создания

    def __str__(self):
        return self.title

class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # время создания

    def __str__(self):
        user_name = self.user.username if self.user else "Anonymous"
        return f'{user_name}: {self.comment_text}'