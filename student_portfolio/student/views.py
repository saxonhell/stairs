from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponse

from .form import ReviewForm, DiscussionForm, CommentForm, MovieForm, UserForm, DirectorForm, SignUpForm
from .models import Review, Discussion, Comment, Movie, Director, CustomUser
from django.shortcuts import render, get_object_or_404, redirect

from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('movie_list')  # Перенаправление после успешной регистрации
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})



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


@login_required  # Ограничиваем доступ только для аутентифицированных пользователей
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
        'Director': Director,
    }

    form_mapping = {
        'Movie': MovieForm,
        'Review': ReviewForm,
        'Discussion': DiscussionForm,
        'Comment': CommentForm,
        'Director': DirectorForm,
    }

    # Проверяем, что модель существует в нашем маппинге
    if model_name not in model_mapping:
        return HttpResponse("Invalid model specified.")

    model_class = model_mapping[model_name]
    form_class = form_mapping.get(model_name)

    # Выполнение CRUD операций для фильмов (Movie) только для администраторов
    if model_name == 'Movie':
        if not request.user.is_staff:
            return HttpResponse("Только администраторы могут выполнять эту операцию.", status=403)

    # Для добавления нового объекта
    if action == 'create':
        if request.method == 'POST':
            form = form_class(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)

                # Привязка пользователя к объектам
                if model_name == 'Comment':
                    obj.user = request.user  # Устанавливаем текущего пользователя как автора комментария
                elif model_name == 'Discussion':
                    obj.user = request.user  # Устанавливаем текущего пользователя как автора обсуждения

                obj.save()
                return redirect('student_detail')
        else:
            form = form_class()
        return render(request, 'crud_form.html', {'form': form, 'action': action, 'model_name': model_name})

    # Для обновления объекта
    elif action == 'update' and obj_id:
        obj = get_object_or_404(model_class, id=obj_id)

        # Проверка, что пользователь может редактировать только свои комментарии
        if model_name == 'Comment' and obj.user != request.user:
            return HttpResponse("Вы можете редактировать только свои комментарии.", status=403)

        if request.method == 'POST':
            form = form_class(request.POST, instance=obj)

            if form.is_valid():
                form.save()
                return redirect('student_detail')
        else:
            form = form_class(instance=obj)
        return render(request, 'crud_form.html', {'form': form, 'action': action, 'model_name': model_name})

    # Для удаления объекта
    elif action == 'delete' and obj_id:
        obj = get_object_or_404(model_class, id=obj_id)

        # Проверка, что пользователь может удалять только свои комментарии
        if model_name == 'Comment' and obj.user != request.user:
            return HttpResponse("Вы можете удалять только свои комментарии.", status=403)

        if request.method == 'POST':
            obj.delete()
            return redirect('student_detail')
        return render(request, 'crud_delete_confirm.html', {'obj': obj, 'model_name': model_name})

    else:
        # Чтение списка объектов (CRUD - Read)
        objects = model_class.objects.all()
        return render(request, 'crud_list.html', {'objects': objects, 'model_name': model_name})
def discussion_list(request):
    discussions = Discussion.objects.all()
    return render(request, 'discussion_list.html', {'discussions': discussions})


# Список обсуждений
@login_required
def discussion_detail(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id)
    comments = discussion.comments.all()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.discussion = discussion
            comment.user = request.user  # Привязываем текущего пользователя
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
class MovieCreateView(UserPassesTestMixin, CreateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movie_form.html'
    success_url = reverse_lazy('movie_list')

    def test_func(self):
        return self.request.user.is_staff  # Доступ только для администраторов

    def handle_no_permission(self):
        return HttpResponse("Только администраторы могут выполнять эту операцию.", status=403)


class MovieUpdateView(UserPassesTestMixin, UpdateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movie_form.html'
    success_url = reverse_lazy('movie_list')

    def test_func(self):
        return self.request.user.is_staff  # Доступ только для администраторов

    def handle_no_permission(self):
        return HttpResponse("Только администраторы могут выполнять эту операцию.", status=403)

class MovieDeleteView(UserPassesTestMixin, DeleteView):
    model = Movie
    template_name = 'crud_delete_confirm.html'
    success_url = reverse_lazy('movie_list')

    def test_func(self):
        return self.request.user.is_staff  # Доступ только для администраторов

    def handle_no_permission(self):
        return HttpResponse("Только администраторы могут выполнять эту операцию.", status=403)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comment_form.html'
    success_url = reverse_lazy('discussion_list')

    def test_func(self):
        comment = self.get_object()
        return comment.user == self.request.user

    def handle_no_permission(self):
        return HttpResponse("Вы можете редактировать только свои комментарии.", status=403)

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'
    success_url = reverse_lazy('discussion_list')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def test_func(self):
        comment = self.get_object()
        return comment.user == self.request.user

    def handle_no_permission(self):
        return HttpResponse("Вы можете удалять только свои комментарии.", status=403)