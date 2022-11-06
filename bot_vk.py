import vk_api as vk
import random
import logging

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.vk_api import VkApiMethod
from environs import Env

from logger import BotLogsHandler
from time import sleep

logger = logging.getLogger('telegram_logging')


def global_handler(event, vk_api: VkApiMethod, env: Env) -> None:
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000)
    )


def main() -> None:
    env = Env()
    env.read_env()

    logger.addHandler(BotLogsHandler(
        token=env('TOKEN_TG_LOG'),
        chat_id=env('CHAT_ID_LOG')
    ))

    while True:

        try:
            vk_session = vk.VkApi(token=env('TOKEN_VK'))
            vk_api = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)
            logger.warning('Бот ВК "holding_quize" запущен')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    global_handler(event, vk_api, env)

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
