import difflib
import json


def get_redis_user_data(user_id, redis_connect):
    """
    Получение данных о пользователе из Redis
    answer_correct - ответ на текущий волпрос
    number_question - номер текущего вопроса
    all_numbers - списиок вопросов, на которые пользователь уже отвечал
    waiting_answer - значение True указывает на состояние ожидания ответа от пользователя (для Vk)
    """
    redis_user = json.loads(redis_connect.get(user_id))

    if redis_user:
        answer_correct = redis_user.get('answer')
        number_question = redis_user.get('number_question', 0)
        waiting_answer = redis_user.get('waiting_answer')
        all_numbers = redis_user.get('all_numbers', [number_question])
    else:
        answer_correct = None
        number_question = 0
        all_numbers = [0]
        waiting_answer = False

    return (
        answer_correct,
        number_question,
        all_numbers,
        waiting_answer,
    )


def compare_strings(seq1, seq2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.85
