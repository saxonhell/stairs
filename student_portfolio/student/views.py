from django.shortcuts import render

# Create your views here.


from .models import Review
from django.shortcuts import render, get_object_or_404
from .models import Movie

def student_detail(request):
    return render(request, 'student_detail.html')

def review_list(request):
    reviews = Review.objects.all()  # Получаем все отзывы из базы данных
    return render(request, 'review.html', {'reviews': reviews})  # Передаем их в шаблон



def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)  # Получаем фильм по ID или возвращаем 404
    reviews = movie.reviews.all()  # Получаем все отзывы для данного фильма
    return render(request, 'movie_detail.html', {'movie': movie, 'reviews': reviews})
