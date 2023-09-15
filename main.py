import asyncio
import os
import random
import sentry_sdk

import uvloop
from pyrogram import Client, idle

from settings.config import WORKING_CLIENTS, BASE_DIR, MY_LOGGER, SENTRY_DSN
from utils.req_to_bot_api import get_active_accounts


async def main(bot_plugins):
    app = Client(name="test_bot", plugins=bot_plugins)
    await app.start()
    MY_LOGGER.success(f'BOT HAS BEEN IN ORBIT...{random.choice(seq=("🛰", "🛸", "🌌", "🌠", "👨‍🚀"))}')
    result = await get_active_accounts()    # Получаем аккаунты, которые должны быть запущены

    if not result:
        await app.stop()
        MY_LOGGER.error(f'Не удалось получить активные аккаунты. Бот остановлен!')
        return

    await idle()
    await app.stop()

    # Тормозим клиенты
    for i_acc_pk, i_acc_data in WORKING_CLIENTS.items():
        i_acc_data[0].set()
        await i_acc_data[1]

    # Удаляем файлы сессий
    session_files = os.path.join(BASE_DIR, 'session_files')
    for i_file in os.listdir(session_files):
        session_file_path = os.path.join(BASE_DIR, 'session_files', i_file)
        if os.path.exists(session_file_path):
            os.remove(session_file_path)
            MY_LOGGER.info(f'Файл сессии: {session_file_path!r} был удалён из ФС')


if __name__ == '__main__':
    # Инициализируем отслеживание ошибок через sentry
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )

    try:
        MY_LOGGER.info('BOT IS READY TO LAUNCH!\nstarting the countdown...')
        MY_LOGGER.info('3... SET PATH TO HANDLERS')

        plugins = dict(
            root="handlers",    # Указываем директорию-корень, где лежат все обработчики
            include=[   # Явно прописываем какие файлы с хэндлерами подключаем
                "main_handlers",
                "accounts_management_handlers",
            ]
        )  # Путь пакета с обработчиками

        MY_LOGGER.info('2... DO SOMETHING ELSE')
        # scheduler = AsyncIOScheduler()
        # scheduler.add_job(job, "interval", seconds=3)
        # scheduler.start()
        # ANY_ENTITIES_STORAGE['scheduler'] = scheduler

        MY_LOGGER.info('1... BOT SPEED BOOST')
        uvloop.install()  # Это для ускорения работы бота

        MY_LOGGER.info('LAUNCH THIS FU... BOT NOW!!!')
        asyncio.run(main(bot_plugins=plugins))
        # Client("test_bot", plugins=plugins).run()

    except (KeyboardInterrupt, SystemExit):
        MY_LOGGER.warning('BOT STOPPED BY CTRL+C!')
    # except Exception as error:
    #     MY_LOGGER.error(f'BOT CRASHED WITH SOME ERROR\n\t{error}\n{error.args}')
