from pyrogram.errors import UserDeactivatedBan

from settings.config import WORKING_CLIENTS, MY_LOGGER, BOT_USERNAME, CLIENT_CHANNELS
import uvloop
from pyrogram import Client

from utils.req_to_bot_api import set_acc_flags
from utils.work_with_clients import stop_account_actions


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

    # Создаём в словаре каналов ключ для данного аккаунта, если такового ещё нет
    if not CLIENT_CHANNELS.get(client.acc_pk):
        CLIENT_CHANNELS[client.acc_pk] = []

    try:
        MY_LOGGER.debug(f'Клиент {session_name!r} отправляет команду /start боту')
        async with client as client:
            send_start = await client.send_message(chat_id=BOT_USERNAME, text='/start')
            MY_LOGGER.debug(f'Результат отправки клиентом {session_name!r} команды /start боту: '
                            f'{True if send_start.id else False}')

        await client.start()    # Стартуем клиент аккаунта
        stop_flag = WORKING_CLIENTS.get(acc_pk)[0]
        MY_LOGGER.success(f'Клиент {session_name!r} успешно запущен!')
        WORKING_CLIENTS[acc_pk][2] = True   # Устанавливаем флаг успешного запуска аккаунта
        await stop_flag.wait()  # Ожидаем поднятия флага

        MY_LOGGER.warning(f'Стоп флаг был поднят. Останавливаем клиент {session_name!r}')
        await client.stop()  # Останавливаем клиент аккаунт
        return  # Выходим из функции

    except UserDeactivatedBan as err:
        MY_LOGGER.error(f'Аккаунт {client.acc_pk!r} получил бан. Текст ошибки: {err!r}')
        WORKING_CLIENTS[acc_pk][2] = None
        await stop_account_actions(acc_pk=acc_pk, err=err, session_name=session_name, error_type='ban',
                                   err_text=f'Аккаунт {acc_pk} был забанен.')
        await set_acc_flags(acc_pk=acc_pk, banned=True, is_run=False, waiting=False)

    except ConnectionError as err:
        MY_LOGGER.error(f'CONNECTION ERRRRRR! {err}')
        return

    except (KeyboardInterrupt, SystemExit) as err:
        MY_LOGGER.warning(f'CLIENT {session_name!r} STOPPED BY CTRL+C!')
        WORKING_CLIENTS[acc_pk][2] = None
        await stop_account_actions(acc_pk=acc_pk, err=err, session_name=session_name)
        await client.stop()

    except Exception as err:
        MY_LOGGER.error(f'CLIENT {session_name!r} CRASHED WITH SOME ERROR\n\t{err}')
        WORKING_CLIENTS[acc_pk][2] = None
        await stop_account_actions(acc_pk=acc_pk, err=err, session_name=session_name)
        await client.stop()


