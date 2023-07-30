import asyncio
import os
import shutil

from pyrogram import Client, filters

from client_work import client_work
from filters.acc_manage_filters import start_client_filter, stop_client_filter
from settings.config import MY_LOGGER, WORKING_CLIENTS, BASE_DIR
from utils.req_to_bot_api import set_acc_run_flag
from utils.work_with_clients import stop_client_async_task, get_channels_for_acc


@Client.on_message(filters.me & filters.private & start_client_filter)
async def start_client_handler(_, update):
    """
    Хэндлер для старта нового потока с клиентом аккаунта телеграм.
    Бот отправляет сообщение в чат к акку, управляющему ботом и передаёт там путь к нужному файлу сессии
    """
    MY_LOGGER.debug(f'Получен апдейт для старта клиента {update.text!r}')
    MY_LOGGER.debug(f'Достаём нужные данные из апдейта и перемещаем в проект бота файл сессии')
    _, session_path, acc_pk, proxy_str = update.text.split()

    if WORKING_CLIENTS.get(acc_pk):
        MY_LOGGER.warning(f'Клиент {acc_pk!r} уже запущен!')
        # Удаляем сообщение с командой бота
        await update.delete()
        return

    # Создаём папку с файлами сессий, если её нет
    if not os.path.exists(os.path.join(BASE_DIR, 'session_files')):
        os.mkdir(os.path.join(BASE_DIR, 'session_files'))

    try:
        session_name = os.path.split(session_path)[1].split('.')[0]
        shutil.copy2(session_path, os.path.join(BASE_DIR, 'session_files'))
        workdir = os.path.join(BASE_DIR, 'session_files')

        # Получаем текущий eventloop, создаём task
        loop = asyncio.get_event_loop()
        task = loop.create_task(client_work(session_name, workdir, proxy_str, acc_pk))

        # Флаг остановки таска
        stop_flag = asyncio.Event()

        # Запись таска и флага в общий словарь (флаг пока опущен)
        WORKING_CLIENTS[acc_pk] = [stop_flag, task]

    except Exception:
        # Отправляем запрос о том, что аккаунт НЕ запущен
        rslt = await set_acc_run_flag(acc_pk=acc_pk, is_run=False)
        if not rslt:
            MY_LOGGER.error(f'Не удалось установить флаг is_run в False для акка PK={acc_pk} через API запрос')
        return

    # Запрашиваем список каналов
    get_channels_rslt = await get_channels_for_acc(acc_pk=acc_pk)
    if not get_channels_rslt:
        await stop_client_async_task(acc_pk=acc_pk, session_name=session_name)

    # Удаляем сообщение с командой бота
    await update.delete()


@Client.on_message(filters.me & filters.private & stop_client_filter)
async def stop_client_handler(client, update):
    """
    Хэндлер для остановки клиента по его имени сессии
    """
    _, session_path, acc_pk, __ = update.text.split()
    session_name = os.path.split(session_path)[1].split('.')[0]
    MY_LOGGER.debug(f'Получен апдейт по остановке клиента {session_name!r}')

    # Если клиент не был ранее запущен в боте
    if not WORKING_CLIENTS.get(acc_pk):
        # Удаляем файл сессии из проекта бота
        session_file_path = os.path.join(BASE_DIR, 'session_files', f'{session_name}.session')
        if os.path.exists(session_file_path):
            os.remove(session_file_path)
            MY_LOGGER.info(f'Файл сессии {session_file_path!r} из проекта бота удалён.')
        # Удаляем сообщение с командой бота
        await update.delete()
        return

    # Остановка таска с запущенным аккаунтом
    await stop_client_async_task(acc_pk=acc_pk, session_name=session_name)

    # Удаляем сообщение с командой бота
    await update.delete()