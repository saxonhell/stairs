from django.shortcuts import render

# Create your views here.


from django.shortcuts import render
from .models import Review

def student_detail(request):
    return render(request, 'student_detail.html')

def review_list(request):
    reviews = Review.objects.all()  # Получаем все отзывы из базы данных
    return render(request, 'review.html', {'reviews': reviews})  # Передаем их в шаблон