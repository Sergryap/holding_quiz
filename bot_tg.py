import json
import logging
import telegram
import redis
import difflib

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from environs import Env
from get_question_answer import get_random_question
from logger import BotLogsHandler

logger = logging.getLogger('telegram_logging')


ATTEMPT = 1


class UpdaterRedisInit(Updater):
    def __init__(self, token, host, port, password):
        super().__init__(token)
        self.dispatcher.redis = redis.Redis(
            host=host,
            port=port,
            password=password,
        )


def get_user_data(update: Update, context: CallbackContext):
    redis_connect = context.dispatcher.redis
    user_id = update.effective_user.id
    redis_user = redis_connect.get(user_id)
    if redis_user:
        answer_correct = json.loads(redis_user).get('answer')
        number_question = json.loads(redis_user).get('number_question', 0)
        all_numbers = json.loads(redis_user).get('all_numbers', [number_question])
    else:
        answer_correct = None
        number_question = 0
        all_numbers = [0]

    return (
        redis_connect,
        user_id,
        answer_correct,
        number_question,
        all_numbers
    )


def get_markup() -> telegram.ReplyKeyboardMarkup:
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    return telegram.ReplyKeyboardMarkup(
        keyboard=custom_keyboard,
        resize_keyboard=True
    )


def compare_strings(seq1, seq2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.85


def start(update: Update, context: CallbackContext):
    """Отправляет сообщение при выполнении команды /start."""
    user = update.effective_user
    update.message.reply_text(
        f'Привет, {user.first_name}! Я бот для викторин. Чтобы начать нажми «Новый вопрос»',
        reply_markup=get_markup()
    )


def handle_new_question_request(update: Update, context: CallbackContext):
    (
        redis_connect,
        user_id,
        answer,
        current_question,
        all_numbers,
    ) = get_user_data(update, context)
    number_question = current_question
    while number_question in all_numbers or number_question == current_question:
        question, answer_correct, number_question = get_random_question()
    all_numbers.append(number_question)
    redis_connect.set(
        user_id,
        json.dumps({
            'answer': answer_correct,
            'number_question': number_question,
            'all_numbers': all_numbers,
        })
    )
    update.message.reply_text(
        text=question,
        reply_markup=get_markup()
    )
    return ATTEMPT


def handle_solution_attempt(update: Update, context: CallbackContext):
    (
        redis_connect,
        user_id,
        answer_correct,
        number_question,
        all_numbers,
    ) = get_user_data(update, context)
    similar_answer = compare_strings(answer_correct, update.message.text)
    if similar_answer:
        msg = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        redis_connect.set(
            user_id,
            json.dumps({
                'answer': None,
                'number_question': number_question,
                'all_numbers': all_numbers,
            })
        )
        next_state = ConversationHandler.END
    else:
        msg = 'Неправильно... Попробуешь ещё раз?'
        next_state = None
    update.message.reply_text(
        text=msg,
        reply_markup=get_markup()
    )
    return next_state


def show_correct_answer_and_next_question(update: Update, context: CallbackContext):
    (
        redis_connect,
        user_id,
        answer_correct,
        number_question_exist,
        all_numbers
    ) = get_user_data(update, context)
    update.message.reply_text(
        text=f'Правильный ответ:\n{answer_correct}',
        reply_markup=get_markup()
    )
    number_question = number_question_exist
    while number_question in all_numbers or number_question == number_question_exist:
        next_question, next_answer_correct, number_question = get_random_question()
    all_numbers.append(number_question)
    redis_connect.set(
        user_id,
        json.dumps({
            'answer': next_answer_correct,
            'number_question': number_question,
            'all_numbers': all_numbers,
        })
    )
    update.message.reply_text(
        text=f'Следующий вопрос:\n\n{next_question}',
        reply_markup=get_markup()
    )
    return ATTEMPT


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
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Новый вопрос'), handle_new_question_request)],
        states={
            ATTEMPT: [
                MessageHandler(
                    Filters.text & ~Filters.command & ~Filters.regex('Сдаться'),
                    handle_solution_attempt
                ),
                MessageHandler(
                    Filters.regex('Сдаться'), show_correct_answer_and_next_question
                )
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('Новый вопрос'), handle_new_question_request)]
    )

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
