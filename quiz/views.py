from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Quiz, Question, Choice, Player
from .ai_service import generate_questions_from_text
import PyPDF2
import docx

# Секретный код преподавателя
TEACHER_SECRET_CODE = "VENERA2026"


def extract_text_from_file(uploaded_file):
    """Извлекает текст из загруженных PDF и Word файлов"""
    text = ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
    return text


def index(request):
    """Главная страница: вход для учеников по коду"""
    if request.method == 'POST':
        join_code = request.POST.get('join_code')
        player_name = request.POST.get('player_name')

        try:
            quiz = Quiz.objects.get(join_code=join_code)
            player = Player.objects.create(quiz=quiz, name=player_name)
            request.session['player_id'] = player.id

            # Перенаправляем ученика на страницу самой игры
            return redirect('play_quiz', quiz_id=quiz.id)

        except Quiz.DoesNotExist:
            return HttpResponse("Ошибка: Тест с таким кодом не найден!")

    return render(request, 'quiz/index.html')


def create_quiz(request):
    if request.method == 'POST':
        teacher_code = request.POST.get('teacher_code')
        if teacher_code != TEACHER_SECRET_CODE:
            return HttpResponse("Ошибка: Неверный секретный код!")

        title = request.POST.get('title')
        text = request.POST.get('text', '')

        uploaded_file = request.FILES.get('document')
        if uploaded_file:
            file_text = extract_text_from_file(uploaded_file)
            text += "\n" + file_text

        if not text.strip():
            return HttpResponse("Ошибка: Нет текста для генерации!")

        quiz = Quiz.objects.create(title=title, source_text=text)

        # 2. Увеличиваем количество вопросов до 20
        questions_data = generate_questions_from_text(text, num_questions=20)

        if questions_data:
            for q_data in questions_data:
                question = Question.objects.create(quiz=quiz, text=q_data['question'])
                for c_data in q_data['choices']:
                    Choice.objects.create(
                        question=question,
                        text=c_data['text'],
                        is_correct=c_data['is_correct']
                    )
            return render(request, 'quiz/success.html', {'quiz': quiz})
        else:
            quiz.delete()
            return HttpResponse("Ошибка ИИ при генерации.")

    return render(request, 'quiz/create_quiz.html')


def play_quiz(request, quiz_id):
    """Страница прохождения теста"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    return render(request, 'quiz/play_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })


from django.http import JsonResponse


def save_result(request):
    if request.method == 'POST':
        score = request.POST.get('score')
        player_id = request.session.get('player_id')

        if player_id:
            try:
                player = Player.objects.get(id=player_id)
                player.score = int(score)
                player.save()

                # ИСПРАВЛЕНО: просто order_by
                leaders = Player.objects.filter(quiz=player.quiz).order_by('-score')[:5]
                leaders_list = [{"name": l.name, "score": l.score} for l in leaders]

                return JsonResponse({"status": "ok", "leaders": leaders_list})
            except Player.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Player not found"}, status=404)

    return JsonResponse({"status": "error"}, status=400)

def quiz_results(request, quiz_id):
    """Отдельная страница для учителя: мониторинг результатов"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'quiz/results.html', {'quiz': quiz})

def get_leaderboard(request, quiz_id):
    """API для живого (Live) обновления списка лидеров каждые 3 секунды"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    leaders = Player.objects.filter(quiz=quiz).order_by('-score')[:15] # Показываем топ 15
    leaders_list = [{"name": l.name, "score": l.score} for l in leaders]
    return JsonResponse({"status": "ok", "leaders": leaders_list})