from settings.config import WORKING_CLIENTS, MY_LOGGER, TOKEN, BOT_USERNAME
import uvloop
from pyrogram import Client

from utils.req_to_bot_api import set_acc_run_flag


async def client_work(session_name, workdir, acc_pk, proxy_str=None):
    """
    Такс в eventloop'e для одного клиента телеграм
    """
    plugins = dict(
        root="handlers",
        include=[
            "client_handlers",
        ]
    )

    uvloop.install()  # Это для ускорения работы бота

    MY_LOGGER.info(f'Запускаем клиент аккаунта {session_name!r}')
    client = Client(session_name, plugins=plugins, workdir=workdir)
    client.acc_pk = acc_pk

    # Добавляем проксю, если она передана
    if proxy_str:
        MY_LOGGER.debug(f'Подключаем аккаунт через проксю: {proxy_str!r}')
        proxy_lst = proxy_str.split(':')
        proxy_dct = {
            'scheme': proxy_lst[0],
            'hostname': proxy_lst[1],
            'port': int(proxy_lst[2]),
        }
        if proxy_lst[3] != '' and proxy_lst[4] != '':
            proxy_dct['username'] = proxy_lst[3]
            proxy_dct['password'] = proxy_lst[4]
        client.proxy = proxy_dct
        client.ipv6 = True

    MY_LOGGER.debug(f'WORKING_CLIENTS.get(acc_pk) == {WORKING_CLIENTS.get(acc_pk)}')
    try:
        MY_LOGGER.debug(f'Клиент {session_name!r} отправляет команду /start боту')
        async with client as client:
            send_start = await client.send_message(chat_id=BOT_USERNAME, text='/start')
            MY_LOGGER.debug(f'Результат отправки клиентом {session_name!r} команды /start боту: {send_start}')

        await client.start()    # Стартуем клиент аккаунта
        stop_flag = WORKING_CLIENTS.get(acc_pk)[0]
        MY_LOGGER.success(f'Клиент {session_name!r} успешно запущен!')
        await stop_flag.wait()  # Ожидаем поднятия флага

        MY_LOGGER.warning(f'Стоп флаг был поднят. Останавливаем клиент {session_name!r}')
        await client.stop()  # Останавливаем клиент аккаунт
        return  # Выходим из функции

    except Exception as error:
        MY_LOGGER.error(f'CLIENT {session_name!r} CRASHED WITH SOME ERROR\n\t{error}')
        await client.stop()
        # Отправляем запрос о том, что аккаунт НЕ запущен
        rslt = await set_acc_run_flag(acc_pk=acc_pk, is_run=False)
        if not rslt:
            MY_LOGGER.error(f'Не удалось установить флаг is_run в True для акка PK={acc_pk} через API запрос')

    except (KeyboardInterrupt, SystemExit):
        MY_LOGGER.warning(f'CLIENT {session_name!r} STOPPED BY CTRL+C!')
        await client.stop()
