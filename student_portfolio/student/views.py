from .form import MovieForm, ReviewForm
from .models import Review
from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie

# Представление для добавления фильма
def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем фильм в базу данных
            return redirect('movie_list')  # Перенаправляем на список фильмов
    else:
        form = MovieForm()
    return render(request, 'add_movie.html', {'form': form})

# Представление для добавления отзыва
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем отзыв в базу данных
            return redirect('movie_list')  # Перенаправляем на список фильмов или другую страницу
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form})

# Представление для списка фильмов с отзывами
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movie_list.html', {'movies': movies})

def student_detail(request):
    return render(request, 'student_detail.html')

def review_list(request):
    reviews = Review.objects.all()  # Получаем все отзывы из базы данных
    return render(request, 'review.html', {'reviews': reviews})  # Передаем их в шаблон

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)  # Получаем фильм по ID или возвращаем 404
    reviews = movie.reviews.all()  # Получаем все отзывы для данного фильма
    return render(request, 'movie_detail.html', {'movie': movie, 'reviews': reviews})
