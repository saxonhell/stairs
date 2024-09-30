

from django.urls import path
from . import views
from .views import handle_crud_operations, MovieListView, MovieDetailView, MovieCreateView, MovieUpdateView, \
    MovieDeleteView

urlpatterns = [
    path('', views.student_detail, name='student_detail'),
    path('all', views.review_list, name='review_list'),
    #path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    #path('movies/', views.movie_list, name='movie_list'),
    path('discussions/', views.discussion_list, name='discussion_list'),
    path('discussions/<int:discussion_id>/', views.discussion_detail, name='discussion_detail'),
    path('crud/', handle_crud_operations, name='crud_operations'),
    path('Fdirector', views.most_discussed_director, name='most_discussed_director'),
    path('directors/', views.director_list, name='director_list'),
    path('movies/', MovieListView.as_view(), name='movie_list'),
    path('movie/<int:pk>/', MovieDetailView.as_view(), name='movie_detail'),
    path('movie/create/', MovieCreateView.as_view(), name='movie_create'),
    path('movie/update/<int:pk>/', MovieUpdateView.as_view(), name='movie_update'),
    path('movie/delete/<int:pk>/', MovieDeleteView.as_view(), name='movie_delete'),

]