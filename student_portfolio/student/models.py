from django.db import models

# Create your models here.


from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=100)  # Название фильма
    description = models.TextField()  # Описание фильма

    def __str__(self):
        return self.title


class Review(models.Model):
    review_text = models.TextField()  # Поле для текста отзыва
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews', null=True)  # Связь с моделью Movie

    def __str__(self):
        return self.review_text