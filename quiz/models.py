import random
from django.db import models

def generate_join_code():
    return str(random.randint(100000, 999999))

class Quiz(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название теста")
    source_text = models.TextField(blank=True, null=True, verbose_name="Текст для ИИ")
    join_code = models.CharField(max_length=6, default=generate_join_code, unique=True, verbose_name="Код доступа")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (Код: {self.join_code})"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500, verbose_name="Текст вопроса")

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200, verbose_name="Вариант ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный?")

    def __str__(self):
        return f"{self.text} - {'Правильно' if self.is_correct else 'Ошибка'}"

class Player(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=100, verbose_name="Имя игрока")
    score = models.IntegerField(default=0, verbose_name="Счет")

    def __str__(self):
        return f"{self.name} ({self.score} очков)"

# Create your models here.
