

from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_detail, name='student_detail'),
    path('all', views.review_list, name='review_list'),
]