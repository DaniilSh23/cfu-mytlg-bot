import asyncio
import os
import shutil

from client_work import client_work
from settings.config import WORKING_CLIENTS, MY_LOGGER, BASE_DIR, CLIENT_CHANNELS
from utils.req_to_bot_api import get_channels


async def stop_client_async_task(acc_pk, session_name):
    """
    Функция для остановки асинхронного таска для клиента
    """
    stop_flag = WORKING_CLIENTS[acc_pk][0]
    WORKING_CLIENTS[acc_pk][0] = stop_flag.set()

    # Ожидаем завершения таска клиента (там в словаре лежит объект таска)
    await WORKING_CLIENTS[acc_pk][1]

    # Удаляем клиент из общего списка
    WORKING_CLIENTS.pop(acc_pk)
    MY_LOGGER.info(f'Клиент PK={acc_pk!r} успешно остановлен.')

    # Удаляем файл сессии из проекта бота
    session_file_path = os.path.join(BASE_DIR, 'session_files', f'{session_name}.session')
    if os.path.exists(session_file_path):
        os.remove(session_file_path)
        MY_LOGGER.info(f'Файл сессии {session_file_path!r} из проекта бота удалён.')


async def start_client_async_task(session_file, proxy, acc_pk):
    """
    Функция для старта асинхронного таска для клиента
    """
    MY_LOGGER.info(f'Вызвана функция для запуска асинхронного таска клиента телеграм')
    session_name = os.path.split(session_file)[1].split('.')[0]
    shutil.copy2(session_file, os.path.join(BASE_DIR, 'session_files'))
    workdir = os.path.join(BASE_DIR, 'session_files')

    # Получаем текущий eventloop, создаём task
    loop = asyncio.get_event_loop()
    task = loop.create_task(client_work(session_name, workdir, proxy, acc_pk))

    # Флаг остановки таска
    stop_flag = asyncio.Event()

    # Запись таска и флага в общий словарь (флаг пока опущен)
    WORKING_CLIENTS[acc_pk] = [stop_flag, task]
    MY_LOGGER.info(f'Функция для запуска асинхронного таска клиента телеграм ВЫПОЛНЕНА')


async def get_channels_for_acc(acc_pk):
    """
    Функция для запроса каналов для аккаунта и сохранения их в глобальный словарь.
    """
    # Запрашиваем список каналов
    MY_LOGGER.debug(f'Запрашиваем список каналов для прослушки аккаунтом PK={acc_pk}')
    get_channels_rslt = await get_channels(acc_pk=acc_pk)
    MY_LOGGER.debug(f'Полученный список каналов: {get_channels_rslt}')

    if not get_channels_rslt:
        MY_LOGGER.error(f'Не удалось получить каналы для акка с PK={acc_pk}. Останавливаем работу акка.')
        return False

    CLIENT_CHANNELS[acc_pk] = []
    for j_ch in get_channels_rslt:
        CLIENT_CHANNELS[acc_pk].append(j_ch)
    return True
