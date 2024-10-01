from django.http import HttpResponse

from .form import ReviewForm, DiscussionForm, CommentForm, MovieForm, UserForm, DirectorForm
from .models import Review, Discussion, Comment, User, Movie, Director
from django.shortcuts import render, get_object_or_404, redirect

from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy

def director_list(request):
    directors = Director.objects.all()
    return render(request, 'director_list.html', {'directors': directors})

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

def discussion_list(request):
    discussions = Discussion.objects.all()
    return render(request, 'discussion_list.html', {'discussions': discussions})


# Список обсуждений
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



# Представление для добавления отзыва
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




class MovieListView(ListView):
    model = Movie
    template_name = 'movie_list.html'
    context_object_name = 'movies'

# 2. Детали фильма
class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()  # Передаем отзывы
        return context

# Представление для создания фильма
class MovieCreateView(CreateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movie_form.html'
    success_url = reverse_lazy('movie_list')  # После успешного создания фильма перенаправляем на список фильмов

# Представление для редактирования фильма
class MovieUpdateView(UpdateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movie_form.html'
    success_url = reverse_lazy('movie_list')

# 5. Удаление фильма
class MovieDeleteView(DeleteView):
    model = Movie
    template_name = 'crud_delete_confirm.html'
    success_url = reverse_lazy('movie_list')