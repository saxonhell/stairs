

from django.urls import path
from . import views
from .views import handle_crud_operations

urlpatterns = [
    path('', views.student_detail, name='student_detail'),
    path('all', views.review_list, name='review_list'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/add/', views.add_movie, name='add_movie'),
    path('reviews/add/', views.add_review, name='add_review'),
    path('discussions/', views.discussion_list, name='discussion_list'),
    path('discussions/add/', views.add_discussion, name='add_discussion'),
    path('discussions/<int:discussion_id>/', views.discussion_detail, name='discussion_detail'),
    path('crud/', handle_crud_operations, name='crud_operations'),
    path('Fdirector', views.most_discussed_director, name='most_discussed_director'),
    path('directors/add/', views.add_director, name='add_director'),
    path('directors/', views.director_list, name='director_list'),

]