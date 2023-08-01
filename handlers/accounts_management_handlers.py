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
    MY_LOGGER.debug(f'Получен апдейт для старта клиента {update.caption!r}')
    MY_LOGGER.debug(f'Достаём нужные данные из апдейта и сохраняем для бота файл сессии')
    split_caption = update.caption.split()

    if len(split_caption) == 3:
        _, acc_pk, file_name = split_caption
        proxy_str = None
    else:
        _, acc_pk, file_name, proxy_str = split_caption

    if WORKING_CLIENTS.get(acc_pk):
        MY_LOGGER.warning(f'Клиент {acc_pk!r} уже запущен!')
        # Удаляем сообщение с командой бота
        await update.delete()
        return

    # Создаём папку с файлами сессий, если её нет
    if not os.path.exists(os.path.join(BASE_DIR, 'session_files')):
        os.mkdir(os.path.join(BASE_DIR, 'session_files'))

    MY_LOGGER.debug(f'Скачиваем файл сессии из телеграмма')
    sess_file_path = await update.download(file_name=os.path.join(BASE_DIR, 'session_files', file_name))
    MY_LOGGER.debug(f'Файл скачать и лежит в : {sess_file_path}')

    try:
        session_name = file_name.split('.')[0]
        workdir = os.path.join(BASE_DIR, 'session_files')

        # Получаем текущий eventloop, создаём task
        loop = asyncio.get_event_loop()
        task = loop.create_task(client_work(session_name, workdir, acc_pk, proxy_str=proxy_str))

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
    _, acc_pk, file_name = update.caption.split()
    session_name = file_name.split('.')[0]
    MY_LOGGER.debug(f'Получен апдейт по остановке клиента {session_name!r}')

    # Если клиент не был ранее запущен в боте
    if not WORKING_CLIENTS.get(acc_pk):
        # Удаляем файл сессии из проекта бота
        session_file_path = os.path.join(BASE_DIR, 'session_files', file_name)
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
