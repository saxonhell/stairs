

from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_detail, name='student_detail'),
    path('all', views.review_list, name='review_list'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/add/', views.add_movie, name='add_movie'),
    path('reviews/add/', views.add_review, name='add_review'),

]