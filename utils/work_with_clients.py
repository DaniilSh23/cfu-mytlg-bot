import asyncio
import os
import shutil

from pyrogram.errors import (UserAlreadyParticipant, FloodWait, UserBannedInChannel, UserBlocked, InviteHashExpired,
                             InviteHashInvalid, AuthKeyUnregistered)
from pyrogram.raw import functions

from client_work import client_work
from settings.config import WORKING_CLIENTS, MY_LOGGER, BASE_DIR, CLIENT_CHANNELS, FLOOD_WAIT_LIMIT
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

    if get_channels_rslt is None:
        MY_LOGGER.error(f'Не удалось получить каналы для акка с PK={acc_pk}. Останавливаем работу акка.')
        return False

    CLIENT_CHANNELS[acc_pk] = []
    for j_ch in get_channels_rslt:
        CLIENT_CHANNELS[acc_pk].append(j_ch)
    return True


async def check_channel_async(app, channel_link):
    """
    Функция для проверки канала (вступление в него и/или получение данных о нём)
    """
    MY_LOGGER.info(f'Вызвана функция для вступления в канал {channel_link!r} аккаунтом PK=={app.acc_pk!r}')

    ch_hash = channel_link.split('/')[-1]
    join_target = channel_link if ch_hash.startswith('+') else f"@{ch_hash}"
    error = None
    channel_obj = None
    brake_ch = False
    while True:
        try:
            await app.join_chat(join_target)
            channel_obj = await app.get_chat(join_target)
            success = True
            break

        except UserAlreadyParticipant as err:
            MY_LOGGER.info(f'Получено исключение, что юзер уже участник канала: {err}. '
                           f'Ждём 2 сек и берём инфу о чате')
            error = err.MESSAGE
            await asyncio.sleep(2)
            channel_obj = await app.get_chat(channel_link)
            success = True
            break

        except FloodWait as err:
            if int(err.value) > FLOOD_WAIT_LIMIT:
                MY_LOGGER.warning(f'Получен слишком высокий флуд: {err.value} сек. Прерываем подписку на каналы')
                error = (f'Получен слишком высокий флуд: {err.value} сек. Прерываем подписку на каналы. '
                         f'Оригинальный текст ошибки: {err!r}')
                success = False
                brake_ch = True
                break
            MY_LOGGER.info(f'Напоролся на флуд. Ждём {err.value} секунд')
            error = err.MESSAGE
            await asyncio.sleep(int(err.value))
            MY_LOGGER.debug(f'Повторяем попытку вступить в канал.')

        except UserBannedInChannel as err:
            MY_LOGGER.warning(f'Пользователь забанен в канале: {err}')
            error = err.MESSAGE
            success = False
            break

        except UserBlocked as err:
            MY_LOGGER.warning(f'Пользователь заблокирован: {err}')
            error = err.MESSAGE
            success = False
            break

        except InviteHashExpired as err:
            MY_LOGGER.warning(f'Ссылка для подключения неактуальна: {err}')
            error = err.MESSAGE
            success = False
            break

        except InviteHashInvalid as err:
            MY_LOGGER.warning(f'Ссылка для подключения невалидна: {err}')
            error = err.MESSAGE
            success = False
            break

        except AuthKeyUnregistered as err:
            MY_LOGGER.critical(f'Сессия слетела. ЭТО НАДО КАК-ТО ОБРАБАТЫВАТЬ: {err}')
            error = err.MESSAGE
            success = False
            break

        except Exception as err:
            MY_LOGGER.warning(f'Ошибка при проверке канала: {err}')
            error = f'Необрабатываемая ошибка: {err!r}'
            success = False
            break

    if channel_obj:
        return {
            'success': success,
            'brake_ch': brake_ch,
            'result': {
                'ch_id': channel_obj.id,
                'ch_name': channel_obj.title,
                'description': channel_obj.description if channel_obj.description else '',
                'members_count': channel_obj.members_count,
            }
        }
    else:
        return {
            'success': success,
            'break': brake_ch,
            'result': {
                'ch_id': 'undefined',
                'ch_name': None,
                'description': error,
                'members_count': None,
            },
        }
