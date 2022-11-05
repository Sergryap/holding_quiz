import logging
import telegram

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env
from get_question_answer import get_random_question
from logger import BotLogsHandler


def start(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение при выполнении команды /start."""
    user = update.effective_user
    update.message.reply_text(
        fr'Привет, {user.full_name}! Я бот для викторин',
        reply_markup=get_markup()
    )


def msg_user(update: Update, context: CallbackContext) -> None:
    if update.message.text == 'Новый вопрос':
        msg = get_random_question()
    else:
        msg = update.message.text
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

    updater = Updater(env('TOKEN_TG'))
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
