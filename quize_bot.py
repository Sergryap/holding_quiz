import json
import logging
import telegram
import redis
import re

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env
from get_question_answer import get_random_question
from logger import BotLogsHandler


class UpdaterRedisInit(Updater):
    def __init__(self, token, host, port, password):
        super().__init__(token)
        self.redis_init = redis.Redis(
            host=host,
            port=port,
            password=password,
        )
        self.dispatcher.user_data.update({'redis_init': self.redis_init})


def start(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение при выполнении команды /start."""
    user = update.effective_user
    update.message.reply_text(
        fr'Привет, {user.full_name}! Я бот для викторин',
        reply_markup=get_markup()
    )


def msg_user(update: Update, context: CallbackContext) -> None:
    redis_connect = context.dispatcher.user_data['redis_init']
    user_id = update.effective_user.id
    message_user = update.message.text
    redis_user = redis_connect.get(user_id)
    user_data = json.loads(redis_user) if redis_user else {}

    if message_user == 'Новый вопрос':
        question, answer_correct = get_random_question()
        redis_connect.set(
            user_id,
            json.dumps({
                'answer': answer_correct,
                'waiting_answer': True
            })
        )
        msg = question
    elif user_data.get('waiting_answer'):
        answer_correct = user_data['answer']
        pattern = re.compile(f'({answer_correct}?)', re.IGNORECASE)
        result = pattern.search(message_user)
        if result:
            msg = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
            redis_connect.delete(user_id)
        else:
            msg = 'Неправильно... Попробуешь ещё раз?'
    else:
        msg = message_user

    update.message.reply_text(
        text=msg,
        reply_markup=get_markup()
    )


def get_markup() -> telegram.ReplyKeyboardMarkup:
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    return telegram.ReplyKeyboardMarkup(
        keyboard=custom_keyboard,
        resize_keyboard=True
    )


def main() -> None:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    env = Env()
    env.read_env()

    updater = UpdaterRedisInit(
        token=env('TOKEN_TG'),
        host=env('REDIS_HOST'),
        port=env('REDIS_PORT'),
        password=env('PASSWORD_DB'),
    )
    updater.logger.addHandler(BotLogsHandler(
        token=env('TOKEN_TG_LOG'),
        chat_id=env('CHAT_ID_LOG')
    ))
    dispatcher = updater.dispatcher
    updater.logger.warning('Бот Telegram "holding_quize" запущен')
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, msg_user))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
