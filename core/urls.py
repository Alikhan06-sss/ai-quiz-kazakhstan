from django.contrib import admin
from django.urls import path, include
from quiz import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quiz.urls')), # Подключаем ссылки приложения quiz
    path('quiz/<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    path('api/leaderboard/<int:quiz_id>/', views.get_leaderboard, name='get_leaderboard'),
]