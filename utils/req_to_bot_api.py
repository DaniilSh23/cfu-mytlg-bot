from typing import Tuple

import aiohttp as aiohttp
from settings.config import MY_LOGGER, WRITE_USR_URL, TOKEN, SET_ACC_RUN_FLAG_URL, GET_CHANNELS_URL, GET_SETTINGS_URL, \
    GET_RELATED_NEWS, WRITE_SUBSCRIPTION_RSLT, UPDATE_CHANNELS


async def post_for_write_user(tlg_id: str, tlg_username: str):
    """
    Вьюшка для стартовой записи или обновления в БД инфы о юзере телеграм.
    """
    data = {
        'token': TOKEN,
        "tlg_id": tlg_id,
        "tlg_username": tlg_username,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=WRITE_USR_URL, data=data) as response:
            if response.status == 200:
                MY_LOGGER.info(f"Успешный запрос для записи или обновления данных о юзере: {await response.json()}")
                return True
            else:
                MY_LOGGER.error(f"Неудачный запрос для записи инфы о юзере: "
                                f"status={response.status}|{response.text}")


async def get_channels(acc_pk):
    """
    Функция для получения подключенных к аккаунту каналов
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{GET_CHANNELS_URL}?token={TOKEN}&acc_pk={acc_pk}") as response:
            if response.status == 200:
                MY_LOGGER.success(f'Успешный GET запрос для получения списка каналов для прослушки')
                return await response.json()
            else:
                MY_LOGGER.warning(f'Неудачный запрос для получения списка каналов для прослушки. {response.status}')


async def set_acc_run_flag(acc_pk, is_run):
    """
    POST запрос для установки флага is_run для аккаунта
        acc_pk - первичный ключ БД аккаунта
        is_run - флаг запуска акка
    """
    data = {
        'token': TOKEN,
        'acc_pk': acc_pk,
        'is_run': is_run,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=SET_ACC_RUN_FLAG_URL, data=data) as response:
            if response.status == 200:
                MY_LOGGER.success(f'Успешный POST запрос для установки флага аккаунта is_run')
                return True
            else:
                MY_LOGGER.warning(f'Неудачный запрос для установки флага аккаунта is_run {response.status}')
                return False


async def get_settings(setting_key: str) -> Tuple[int, dict]:
    """
    GET запрос для получения какой-либо настройки из БД
    :param setting_key: str - ключ настройки
    :return: str
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{GET_SETTINGS_URL}?key={setting_key}&token={TOKEN}") as response:
            if response.status == 200:
                MY_LOGGER.success(f'Успешный GET запрос для получения настроек по ключу {setting_key!r}')
            else:
                MY_LOGGER.warning(f'Неудачный GET запрос для получения настроек по ключу {setting_key!r}')
            return response.status, await response.json()


async def get_related_news(ch_pk: str) -> dict | None:
    """
    GET запрос для получения новостей по теме. Передаём PK канала из которого пришёл новый пост.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{GET_RELATED_NEWS}?ch_pk={ch_pk}&token={TOKEN}") as response:
            if response.status == 200:
                MY_LOGGER.success(f'Успешный GET запрос для получения новостей по теме канала PK == {ch_pk!r}')
                return await response.json()
            else:
                MY_LOGGER.warning(f'Неудачный GET запрос для получения новостей по теме канала PK == {ch_pk!r}')


async def write_new_post(ch_pk, text, embedding):
    """
    POST запрос для записи в БД нового новостного поста.
    ch_pk - PK канала в котором вышел пост
    text - текст поста
    embedding - векторное представление текста поста(передать строку с числами через пробел)
    """
    data = {
        'token': TOKEN,
        'ch_pk': ch_pk,
        'text': text,
        'embedding': embedding,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=GET_RELATED_NEWS, data=data) as response:
            if response.status == 200:
                MY_LOGGER.success(f'Успешный POST запрос для записи нового поста')
                return True
            else:
                MY_LOGGER.warning(f'Неудачный POST запрос для записи нового поста')
                return False


async def send_subscription_results(req_data):
    """
    POST запрос для записи результатов подписки в БД.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url=WRITE_SUBSCRIPTION_RSLT, json=req_data) as response:
            if response.status == 200:
                MY_LOGGER.success(f'Успешный POST запрос для записи результатов подписки')
                return True
            else:
                MY_LOGGER.warning(f'Неудачный POST запрос для записи результатов подписки')
                return False


async def update_channels(req_data):
    """
    Записываем инфу о каналах в БД
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url=UPDATE_CHANNELS, json=req_data) as response:
            if response.status == 200:
                MY_LOGGER.success(f'Успешный POST запрос для обновления списка каналов')
                return True
            else:
                MY_LOGGER.warning(f'Неудачный POST запрос для обновления списка каналов')
                return False
