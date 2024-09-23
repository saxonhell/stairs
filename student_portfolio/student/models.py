from django.db import models

# Create your models here.


from django.db import models


class Review(models.Model):
    review_text = models.TextField()  # Поле для текста отзыва

    def __str__(self):
        return self.review_text
