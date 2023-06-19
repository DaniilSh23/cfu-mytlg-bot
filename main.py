import uvloop
from pyrogram import Client
from loguru import logger


if __name__ == '__main__':
    try:
        logger.info('BOT IS READY TO LAUNCH!\nstarting the countdown...')
        logger.info('3... SET PATH TO HANDLERS')

        plugins = dict(
            root="handlers",    # Указываем директорию-корень, где лежат все обработчики
            include=[   # Явно прописываем какие файлы с хэндлерами подключаем
                "main_handlers",
            ]
        )  # Путь пакета с обработчиками

        logger.info('2... DO SOMETHING ELSE')
        # scheduler = AsyncIOScheduler()
        # scheduler.add_job(job, "interval", seconds=3)
        # scheduler.start()
        # ANY_ENTITIES_STORAGE['scheduler'] = scheduler

        logger.info('1... BOT SPEED BOOST')
        uvloop.install()  # Это для ускорения работы бота

        logger.info('LAUNCH THIS FU... BOT NOW!!!')
        Client("test_bot", plugins=plugins).run()
    except Exception as error:
        logger.error(f'BOT CRASHED WITH SOME ERROR\n\t{error}')
    except (KeyboardInterrupt, SystemExit):
        logger.warning('BOT STOPPED BY CTRL+C!')