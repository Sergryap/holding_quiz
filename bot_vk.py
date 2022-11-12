from typing import List

import vk_api as vk
import random
import logging
import json
import redis
import os

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.vk_api import VkApiMethod
from environs import Env

from get_question_answer import compare_strings, get_random_quiz
from logger import BotLogsHandler
from time import sleep

logger = logging.getLogger('telegram_logging')


def get_markup():
    keyboard = VkKeyboard(inline=False)
    buttons = ['Новый вопрос', 'Сдаться', 'Мой счет']
    for number, button in enumerate(buttons):
        keyboard.add_button(button, VkKeyboardColor.PRIMARY)
        if number == 1:
            keyboard.add_line()
    return keyboard.get_keyboard()


def global_handler(event, vk_api: VkApiMethod, redis_connect: redis.Redis, quiz: List[dict]) -> None:
    user_id = event.user_id
    message_user = event.text
    messages = []
    redis_user = json.loads(redis_connect.get(user_id))

    if redis_user:
        answer_correct_redis = redis_user.get('answer')
        current_number_question = redis_user.get('number_question', 0)
        all_numbers_question = redis_user.get('all_numbers', [current_number_question])
        waiting_answer = redis_user.get('waiting_answer')
    else:
        current_number_question = 0
        all_numbers_question = [0]
        waiting_answer = False

    number_question = current_number_question
    if message_user == 'Новый вопрос' and not waiting_answer:
        while number_question in all_numbers_question or number_question == current_number_question:
            question_random = random.choice(quiz)
            question = question_random['question']
            answer_correct = question_random['answer']
            number_question = question_random['number']
        all_numbers_question.append(number_question)
        redis_connect.set(
            user_id,
            json.dumps(
                {
                    'answer': answer_correct,
                    'waiting_answer': True,
                    'number_question': number_question,
                    'all_numbers': all_numbers_question,
                }
            )
        )
        messages.append(question)

    elif waiting_answer and message_user == 'Сдаться':
        messages.append(f'Правильный ответ:\n{answer_correct_redis}')
        while number_question in all_numbers_question or number_question == current_number_question:
            question_random = random.choice(quiz)
            next_question = question_random['question']
            next_answer_correct = question_random['answer']
            number_question = question_random['number']
        all_numbers_question.append(number_question)
        redis_connect.set(
            user_id,
            json.dumps(
                {
                    'answer': next_answer_correct,
                    'waiting_answer': True,
                    'number_question': number_question,
                    'all_numbers': all_numbers_question,
                }
            )
        )
        messages.append(f'Следующий вопрос:\n\n{next_question}')

    elif waiting_answer:
        similar_answer = compare_strings(answer_correct_redis, message_user)
        if similar_answer:
            messages.append('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
            redis_connect.set(
                user_id,
                json.dumps(
                    {
                        'answer': None,
                        'waiting_answer': False,
                        'number_question': number_question,
                        'all_numbers': all_numbers_question,
                    }
                )
            )
        else:
            messages.append('Неправильно... Попробуешь ещё раз?')
    else:
        user_info = vk_api.users.get(user_ids=user_id)
        first_name = user_info[0]['first_name']
        messages.append(f'Привет, {first_name}! Я бот для викторин. Чтобы начать нажми «Новый вопрос»')

    for msg in messages:
        vk_api.messages.send(
            user_id=user_id,
            message=msg,
            random_id=random.randint(1, 1000),
            keyboard=get_markup()
        )


def main() -> None:
    env = Env()
    env.read_env()

    logger.addHandler(BotLogsHandler(
        token=env('TOKEN_TG_LOG'),
        chat_id=env('CHAT_ID_LOG')
    ))

    redis_connect = redis.Redis(
        host=env('REDIS_HOST'),
        port=env('REDIS_PORT'),
        password=env('PASSWORD_DB'),
    )

    quiz = get_random_quiz()

    while True:

        try:
            vk_session = vk.VkApi(token=env('TOKEN_VK'))
            vk_api = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)
            logger.warning('Бот ВК "holding_quize" запущен')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    global_handler(event, vk_api, redis_connect, quiz)

        except ConnectionError as err:
            logger.warning(f'Соединение было прервано: {err}', stack_info=True)
            sleep(5)
            continue
        except Exception as err:
            logger.exception(err)
            sleep(5)

    logger.critical('Бот ВК упал')


if __name__ == '__main__':
    main()
