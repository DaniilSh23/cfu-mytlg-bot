import asyncio
import datetime
import os
import time

from pyrogram.errors import (UserAlreadyParticipant, FloodWait, UserBannedInChannel, UserBlocked, InviteHashExpired,
                             InviteHashInvalid, AuthKeyUnregistered)

from settings.config import WORKING_CLIENTS, MY_LOGGER, BASE_DIR, CLIENT_CHANNELS, FLOOD_WAIT_LIMIT, TOKEN
from utils.req_to_bot_api import get_channels, post_account_error, set_acc_flags


async def stop_account_actions(err, acc_pk, session_name, error_type='other', err_text='some error...'):
    """
    Функция для выполнения действий при остановке аккаунта из-за ошибки
    """
    # Записываем данные об ошибке аккаунта
    rslt = await post_account_error(req_data={
        "token": TOKEN,
        "error_type": error_type,
        "error_description": f"{err_text} | {err!r}",
        "account": int(acc_pk),
    })
    if not rslt:
        MY_LOGGER.error(f'Не удалось записать в БД данные об ошибке акка PK={acc_pk} через API запрос')
    # Отмечаем в БД, что аккаунт остановлен
    rslt = await set_acc_flags(acc_pk=acc_pk, is_run=False)
    if not rslt:
        MY_LOGGER.error(f'Не удалось установить флаг is_run в True для акка PK={acc_pk} через API запрос')
    # Удаляем файл сессии
    session_file_path = os.path.join(BASE_DIR, 'session_files', f'{session_name}.session')
    if os.path.exists(session_file_path):
        os.remove(session_file_path)
        MY_LOGGER.info(f'Файл сессии {session_file_path!r} из проекта бота удалён.')


async def stop_client_async_task(acc_pk, session_name=None):
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

    if session_name:
        # Удаляем файл сессии из проекта бота
        session_file_path = os.path.join(BASE_DIR, 'session_files', f'{session_name}.session')
        if os.path.exists(session_file_path):
            os.remove(session_file_path)
            MY_LOGGER.info(f'Файл сессии {session_file_path!r} из проекта бота удалён.')


async def start_client_async_task(session_file, proxy, acc_pk):
    """
    Функция для старта асинхронного таска для клиента
    """
    from client_work import client_work

    MY_LOGGER.info(f'Вызвана функция для запуска асинхронного таска клиента телеграм')
    session_name = os.path.split(session_file)[1].split('.')[0]
    workdir = os.path.join(BASE_DIR, 'session_files')

    # Получаем текущий eventloop, создаём task
    loop = asyncio.get_event_loop()
    task = loop.create_task(client_work(session_name, workdir, acc_pk, proxy))

    stop_flag = asyncio.Event()   # Флаг остановки таска
    is_running = False

    # Запись таска и флага в общий словарь (флаг пока опущен)
    WORKING_CLIENTS[acc_pk] = [stop_flag, task, is_running]

    MY_LOGGER.info(f'Функция для запуска асинхронного таска клиента телеграм (acc_pk=={acc_pk}) ВЫПОЛНЕНА')


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


async def check_channel_async(app, channel_link):   # TODO: эта дрочь переписана, но не проверена
    """
    Функция для проверки канала (вступление в него и/или получение данных о нём)
    """
    MY_LOGGER.info(f'Вызвана функция для вступления в канал {channel_link!r} аккаунтом PK=={app.acc_pk!r}')

    ch_hash = channel_link.split('/')[-1]
    join_target = channel_link if ch_hash.startswith('+') else f"@{ch_hash}"
    error = None
    channel_obj = None
    brake_ch = False
    action_for_story = ''
    while True:
        try:
            await app.join_chat(join_target)
            channel_obj = await app.get_chat(join_target)
            success = True
            action_for_story = (f'{datetime.datetime.now()} | '
                                f'Успешная подписка на канал: {channel_obj.title}\n'
                                f'{action_for_story}')
            break

        except UserAlreadyParticipant as err:
            MY_LOGGER.info(f'Получено исключение, что юзер уже участник канала: {err}. '
                           f'Ждём 2 сек и берём инфу о чате')
            error = err.MESSAGE
            await asyncio.sleep(2)
            channel_obj = await app.get_chat(channel_link)
            success = True
            action_for_story = (f'{datetime.datetime.now()} | '
                                f'Юзер был подписан и мы просто достали инфу о канале {channel_obj.title}\n'
                                f'{action_for_story}')
            break

        except FloodWait as err:
            if int(err.value) >= FLOOD_WAIT_LIMIT:
                MY_LOGGER.warning(f'Получен слишком высокий флуд: {err.value} сек.')
                error = (f'Получен слишком высокий флуд: {err.value} сек.'
                         f'Оригинальный текст ошибки: {err!r}')
                success = False
                brake_ch = True
                # Записываем данные об ошибке аккаунта
                await post_account_error(req_data={
                    "token": TOKEN,
                    "error_type": "flood_wait",
                    "error_description": f"Длительный флуд, acc_pk == {app.acc_pk}! {err.value} сек. "
                                         f"(лимит флуда {FLOOD_WAIT_LIMIT} сек.). "
                                         f"Получен {datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y')}, "
                                         f"окончание {datetime.datetime.fromtimestamp(time.time() + int(err.value)).strftime('%H:%M:%S %d.%m.%Y')}"
                                         f"| {err!r}",
                    "account": int(app.acc_pk),
                })
                await set_acc_flags(acc_pk=app.acc_pk, waiting=True, is_run=True, banned=False)
                await asyncio.sleep(int(err.value))
                await set_acc_flags(acc_pk=app.acc_pk, waiting=False, is_run=True, banned=False)
                MY_LOGGER.debug(f'Повторяем попытку вступить в канал.')
                action_for_story = f'{datetime.datetime.now()} | {error}\n{action_for_story}'
                continue

            MY_LOGGER.info(f'Напоролся на флуд. Ждём {err.value} секунд')
            error = err.MESSAGE
            await asyncio.sleep(int(err.value))
            MY_LOGGER.debug(f'Повторяем попытку вступить в канал.')
            action_for_story = f'{datetime.datetime.now()} | {error}\n{action_for_story}'

        except UserBannedInChannel as err:
            MY_LOGGER.warning(f'Пользователь забанен в канале: {err}')
            error = err.MESSAGE
            success = False
            action_for_story = f'{datetime.datetime.now()} | {error}\n{action_for_story}'
            break

        except UserBlocked as err:
            MY_LOGGER.warning(f'Пользователь заблокирован: {err}')
            error = err.MESSAGE
            success = False
            action_for_story = f'{datetime.datetime.now()} | {error}\n{action_for_story}'
            break

        except InviteHashExpired as err:
            MY_LOGGER.warning(f'Ссылка для подключения неактуальна: {err}')
            error = err.MESSAGE
            success = False
            action_for_story = f'{datetime.datetime.now()} | {error}\n{action_for_story}'
            break

        except InviteHashInvalid as err:
            MY_LOGGER.warning(f'Ссылка для подключения невалидна: {err}')
            error = err.MESSAGE
            success = False
            action_for_story = f'{datetime.datetime.now()} | {error}\n{action_for_story}'
            break

        except AuthKeyUnregistered as err:
            MY_LOGGER.critical(f'Сессия слетела. acc_pk=={app.acc_pk} ЭТО НАДО КАК-ТО ОБРАБАТЫВАТЬ: {err}')
            error = err.MESSAGE
            success = False
            # Записываем данные об ошибке аккаунта
            await post_account_error(req_data={
                "token": TOKEN,
                "error_type": "СЛЕТЕЛА_СЕССИЯ",
                "error_description": f"Для аккаунта {app.acc_pk} слетела сессия! | {err!r}",
                "account": int(app.acc_pk),
            })
            action_for_story = f'{datetime.datetime.now()} | {error}\n{action_for_story}'
            break

        except UserDeactivatedBan as err:
            MY_LOGGER.error(f'Аккаунт {app.acc_pk!r} получил бан при подписке на канал. Текст ошибки: {err!r}')
            error = err
            success = False
            brake_ch = True
            # Записываем данные об ошибке аккаунта
            await post_account_error(req_data={
                "token": TOKEN,
                "error_type": "необрабатываемая_ошибка",
                "error_description": f"Необрабатываемая ошибка для аккаунта {app.acc_pk} | {err!r}",
                "account": int(app.acc_pk),
            })
            action_for_story = f'{datetime.datetime.now()} | {error}\n{action_for_story}'
            await set_acc_flags(acc_pk=app.acc_pk, banned=True, is_run=False, waiting=False)
            WORKING_CLIENTS[app.acc_pk][2] = None
            break

        except Exception as err:
            MY_LOGGER.warning(f'Ошибка при проверке канала: {err}')
            error = f'Необрабатываемая ошибка: {err!r}'
            success = False
            # Записываем данные об ошибке аккаунта
            await post_account_error(req_data={
                "token": TOKEN,
                "error_type": "необрабатываемая_ошибка",
                "error_description": f"Необрабатываемая ошибка для аккаунта {app.acc_pk} | {err!r}",
                "account": int(app.acc_pk),
            })
            action_for_story = f'{datetime.datetime.now()} | {error}\n{action_for_story}'
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
            },
            "action_story": action_for_story,
        }
    else:
        return {
            'success': success,
            'break_ch': brake_ch,
            'result': {
                'ch_id': 'undefined',
                'ch_name': None,
                'description': error,
                'members_count': None,
            },
            "action_story": action_for_story,
        }


""" НИЖЕ ДЛЯ ТЕСТА """


def exc_test():
    for i in range(10):
        try:
            if i == 5:
                10 / 0
            print(f'выполняем итерацию {i!r}')
            raise
        except ZeroDivisionError as err:
            print(f'Обрабатываем ошибку итерации {i!r} {err}')
            break
        except Exception as err:
            print(f'Обрабатываем ошибку итерации {i!r} {err}')
        finally:
            print(f'Вызван блок finally для итерации {i!r}')


if __name__ == '__main__':
    exc_test()