from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_quiz, name='create_quiz'),
    # Убедись, что здесь в конце стоит name='play_quiz'
    path('play/<int:quiz_id>/', views.play_quiz, name='play_quiz'),
    path('save_result/', views.save_result, name='save_result'),
]