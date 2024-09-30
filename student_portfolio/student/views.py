from django.http import HttpResponse

from .form import ReviewForm, DiscussionForm, CommentForm, MovieForm, UserForm, DirectorForm
from .models import Review, Discussion, Comment, User, Movie, Director
from django.shortcuts import render, get_object_or_404, redirect

from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

def director_list(request):
    directors = Director.objects.all()
    return render(request, 'director_list.html', {'directors': directors})

def add_director(request):
    if request.method == 'POST':
        form = DirectorForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем нового режиссёра в базе данных
            return redirect('director_list')  # Перенаправляем на список режиссёров (создадим его позже)
    else:
        form = DirectorForm()
    return render(request, 'add_director.html', {'form': form})

def most_discussed_director(request):
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    # Преобразование строковых дат в объекты datetime
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        # Если дата начала не указана или неверна, используем 30 дней назад
        start_date = timezone.now() - timedelta(days=30)
    try:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        # Если дата окончания не указана или неверна, используем текущую дату
        end_date = timezone.now()

    # Агрегируем количество обсуждений по режиссёрам в заданном периоде
    directors = Director.objects.annotate(
        discussion_count=Count(
            'movies__discussions',
            filter=Q(movies__discussions__created_at__range=(start_date, end_date))
        )
    ).order_by('-discussion_count')

    most_discussed_director = directors.first()

    return render(request, 'most_discussed_director.html', {
        'most_discussed_director': most_discussed_director,
        'start_date': start_date,
        'end_date': end_date
    })



def handle_crud_operations(request):
    action = request.GET.get('action', 'read')  # по умолчанию - read
    model_name = request.GET.get('model', 'Movie')  # по умолчанию - Movie
    obj_id = request.GET.get('id')  # ID объекта для операций update/delete

    # Определяем модель по имени
    model_mapping = {
        'Movie': Movie,
        'Review': Review,
        'Discussion': Discussion,
        'Comment': Comment,
        'User': User,
        'Director': Director,
    }

    form_mapping = {
        'Movie': MovieForm,
        'Review': ReviewForm,
        'Discussion': DiscussionForm,
        'Comment': CommentForm,
        'User': UserForm,
        'Director': DirectorForm,
    }

    # Проверяем, что модель существует в нашем маппинге
    if model_name not in model_mapping:
        return HttpResponse("Invalid model specified.")

    model_class = model_mapping[model_name]
    form_class = form_mapping.get(model_name)

    # Выполнение CRUD операций
    if action == 'create':
        if request.method == 'POST':
            form = form_class(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)

                if model_name in ['Comment', 'Discussion', 'Review']:
                    user_name = form.cleaned_data.get('user_name')
                    if user_name:
                        user, created = User.objects.get_or_create(username=user_name)
                        obj.user = user

                obj.save()
                return redirect('crud_operations')
        else:
            form = form_class()
        return render(request, 'crud_form.html', {'form': form, 'action': action, 'model_name': model_name})

    elif action == 'update' and obj_id:
        obj = get_object_or_404(model_class, id=obj_id)

        if request.method == 'POST':
            form = form_class(request.POST, instance=obj)

            if form.is_valid():
                if model_name in ['Comment', 'Discussion', 'Review']:
                    user_name = form.cleaned_data.get('user_name')
                    if user_name:
                        user, created = User.objects.get_or_create(username=user_name)
                        obj.user = user

                form.save()
                return redirect('crud_operations')
        else:
            initial_data = {}
            if model_name in ['Comment', 'Discussion', 'Review'] and obj.user:
                initial_data['user_name'] = obj.user.username
            form = form_class(instance=obj, initial=initial_data)

        return render(request, 'crud_form.html', {'form': form, 'action': action, 'model_name': model_name})

    elif action == 'delete' and obj_id:
        obj = get_object_or_404(model_class, id=obj_id)
        if request.method == 'POST':
            obj.delete()
            return redirect('crud_operations')
        return render(request, 'crud_delete_confirm.html', {'obj': obj, 'model_name': model_name})

    else:
        objects = model_class.objects.all()
        return render(request, 'crud_list.html', {'objects': objects, 'model_name': model_name})



# Представление для создания обсуждения
def add_discussion(request):
    if request.method == 'POST':
        discussion_form = DiscussionForm(request.POST)
        if discussion_form.is_valid():
            discussion = discussion_form.save(commit=False)
            # Получаем введённое имя пользователя
            user_name = discussion_form.cleaned_data['user_name']

            # Проверяем, существует ли пользователь с таким именем
            user, created = User.objects.get_or_create(username=user_name)

            # Устанавливаем пользователя в поле user
            discussion.user = user

            discussion.save()
            return redirect('discussion_list')  # Перенаправление после успешного сохранения
    else:
        discussion_form = DiscussionForm()

    return render(request, 'add_discussion.html', {'discussion_form': discussion_form})


# Представление для создания комментария в обсуждении
def add_comment(request, discussion_id):
    discussion = Discussion.objects.get(pk=discussion_id)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)

            # Получаем имя пользователя из формы
            user_name = comment_form.cleaned_data['user_name']

            # Ищем или создаем пользователя
            user, created = User.objects.get_or_create(username=user_name)

            # Привязываем пользователя к комментарию
            comment.user = user
            comment.discussion = discussion  # Связываем комментарий с обсуждением
            comment.save()
            return redirect('discussion_detail', pk=discussion.pk)  # Перенаправление после сохранения
    else:
        comment_form = CommentForm()

    return render(request, 'discussion_detail.html', {'form': comment_form, 'discussion': discussion})


def edit_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        form = MovieForm(request.POST, instance=movie)
        if form.is_valid():
            form.save()
            return redirect('movie_list')
    else:
        form = MovieForm(instance=movie)
    return render(request, 'edit_movie.html', {'form': form, 'movie': movie})

def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        movie.delete()
        return redirect('movie_list')
    return render(request, 'delete_movie.html', {'movie': movie})

def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('movie_list')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'edit_review.html', {'form': form, 'review': review})

def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.delete()
        return redirect('movie_list')
    return render(request, 'delete_review.html', {'review': review})

def edit_discussion(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id)
    if request.method == 'POST':
        form = DiscussionForm(request.POST, instance=discussion)
        if form.is_valid():
            form.save()
            return redirect('discussion_list')
    else:
        form = DiscussionForm(instance=discussion)
    return render(request, 'edit_discussion.html', {'form': form, 'discussion': discussion})

def delete_discussion(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id)
    if request.method == 'POST':
        discussion.delete()
        return redirect('discussion_list')
    return render(request, 'delete_discussion.html', {'discussion': discussion})


def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            # Получаем введённое имя пользователя из формы
            user_name = form.cleaned_data['user_name']

            # Ищем пользователя или создаём нового, если его нет
            user, created = User.objects.get_or_create(username=user_name)

            # Привязываем пользователя к комментарию
            comment.user = user
            form.save()  # Сохраняем комментарий с новым пользователем

            return redirect('discussion_detail', discussion_id=comment.discussion.id)
    else:
        # Передаем текущее имя пользователя в поле user_name при рендеринге формы
        form = CommentForm(instance=comment, initial={'user_name': comment.user.username if comment.user else ''})

    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('discussion_detail', discussion_id=comment.discussion.id)
    return render(request, 'delete_comment.html', {'comment': comment})


# Список обсуждений
def discussion_list(request):
    discussions = Discussion.objects.all()
    return render(request, 'discussion_list.html', {'discussions': discussions})

# Детали обсуждения и комментарии
def discussion_detail(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id)
    comments = discussion.comments.all()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.discussion = discussion  # Привязываем комментарий к обсуждению

            # Получаем введённое имя пользователя
            user_name = form.cleaned_data['user_name']

            # Ищем или создаем пользователя с введенным именем
            user, created = User.objects.get_or_create(username=user_name)

            # Привязываем найденного или созданного пользователя к комментарию
            comment.user = user

            comment.save()
            return redirect('discussion_detail', discussion_id=discussion.id)
    else:
        form = CommentForm()

    return render(request, 'discussion_detail.html', {'discussion': discussion, 'comments': comments, 'form': form})


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
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            user_name = review_form.cleaned_data['user_name']
            user, created = User.objects.get_or_create(username=user_name)
            review.user = user
            review.save()
            return redirect('movie_detail', movie_id=review.movie.id)  # Здесь передаем movie_id
    else:
        review_form = ReviewForm()

    return render(request, 'add_review.html', {'review_form': review_form})

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
