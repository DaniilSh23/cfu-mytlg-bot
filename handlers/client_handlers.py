import asyncio
import datetime
import json
import random

from pyrogram import Client, filters
from pyrogram.raw import functions

from filters.client_filters import listening_channel_filter
from settings.config import MY_LOGGER, CLIENT_CHANNELS, TOKEN
from utils.post_filters import PostFilters
from utils.req_to_bot_api import get_related_news, write_new_post, send_subscription_results
from utils.work_with_clients import check_channel_async


@Client.on_message(filters.channel & listening_channel_filter)
async def listening_chat_handler(client, update):
    """
    Ловим апдейты от чатов, которые прослушиваем.
    """
    MY_LOGGER.info(f'Получен апдейт из прослушиваемого канала с ID == {update.chat.id}')

    MY_LOGGER.debug(f'Ищем нужный канал в общем списке')
    channels = CLIENT_CHANNELS[client.acc_pk]
    this_channel = list(filter(lambda ch: str(ch.get('channel_id')) == str(update.chat.id), channels))[0]
    MY_LOGGER.debug(f'Инфа об этом канале: {this_channel}')

    MY_LOGGER.debug(f'Получаем все новостные посты для темы данного канала')
    related_news = await get_related_news(ch_pk=this_channel.get('pk'))
    if not related_news:
        MY_LOGGER.warning(f'Новостной пост из канала PK=={this_channel.get("pk")} не был обработан')
        return

    post_is_unique = True
    if related_news.get('posts'):
        MY_LOGGER.debug(f'Вызываем фильтры')
        post_filters_obj = PostFilters(
            new_post=update.text,
            old_posts=related_news.get('posts'),
            separator=related_news.get('separator'),
        )
        filtration_rslt = await post_filters_obj.complete_filtering()
        if not all(filtration_rslt):
            MY_LOGGER.debug(f'Фильтры для поста не пройдены. Откидываем пост.')
            post_is_unique = False

    if post_is_unique:
        await write_new_post(ch_pk=this_channel.get("pk"), text=update.text)


@Client.on_message(filters.bot & filters.command('subscribe_to_channels') & filters.document)
async def subscribe_to_channels(client, update):
    """
    Хэндлер на команду от бота начать подписываться на каналы.
    """
    MY_LOGGER.info(f'Получен апдейт с командой от бота subscribe_to_channels на аккаунт с PK=={client.acc_pk!r}')

    MY_LOGGER.debug(f'Скачиваем файл с данными для задачи в память и преобразуем в словарь')
    file = await update.download(in_memory=True)
    file_data = file.getvalue().decode('utf-8')
    cmd_data_dct = json.loads(file_data)

    # Словарь с результатами подписки
    task_result_dct = dict(token=TOKEN, task_pk=cmd_data_dct.get("task_pk"), fully_completed=True, results=[])
    for i_ch_pk, i_ch_lnk in cmd_data_dct["data"]:
        check_ch_rslt = await check_channel_async(app=client, channel_link=i_ch_lnk)

        # Подписка не удалась
        if not check_ch_rslt.get('success'):
            task_result_dct['fully_completed'] = False
            task_result_dct.get('results').append({
                'ch_pk': i_ch_pk,
                'success': check_ch_rslt.get('success'),
                'description': check_ch_rslt.get('result').get('description'),
            })
            continue

        # Успешная подписка
        task_result_dct.get('results').append({
            'ch_pk': i_ch_pk,
            'success': check_ch_rslt.get('success'),
            'ch_id': check_ch_rslt.get('result').get('ch_id'),
            'ch_name': check_ch_rslt.get('result').get('ch_name'),
            'ch_lnk': i_ch_lnk,
            'description': check_ch_rslt.get('result').get('description'),
            'subscribers_numb': check_ch_rslt.get('result').get('members_count')
        })
        sleep_time = random.randint(15, 25)
        MY_LOGGER.debug(f'Пауза перед следующей подпиской {sleep_time} сек.')
        await asyncio.sleep(sleep_time)

    MY_LOGGER.debug(f'Отправляем в БД результаты подписки')
    send_rslt = await send_subscription_results(req_data=task_result_dct)
    if send_rslt:
        MY_LOGGER.debug(f'Пополняем список каналов для данного аккаунта')
        for i_ch in task_result_dct.get('results'):
            if i_ch.get('success'):
                CLIENT_CHANNELS[client.acc_pk].append({
                    "pk": i_ch.get('ch_pk'),
                    "channel_id": i_ch.get('ch_id'),
                    "channel_name": i_ch.get('ch_name'),
                    "channel_link": i_ch.get('ch_lnk'),
                })
    await update.delete()   # удаляем сообщение с командой


# @Client.on_message()
async def all_updates(client, update):
    """
    Все апдейты
    """
    MY_LOGGER.success(f'Клиент {client.name!r} в работе. Получил апдейт.')
    MY_LOGGER.debug(update)
