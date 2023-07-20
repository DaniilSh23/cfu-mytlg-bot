import asyncio
import datetime

from pyrogram import Client, filters

from filters.client_filters import listening_channel_filter
from settings.config import MY_LOGGER, CLIENT_CHANNELS, TOKEN
from utils.post_filters import PostFilters
from utils.req_to_bot_api import get_related_news, write_new_post


@Client.on_message(filters.channel & listening_channel_filter)
async def listening_chat_handler(client, update):  # TODO: дописать: приняли пост и сохранили его в БД
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
    if related_news.get('related_news'):
        MY_LOGGER.debug(f'Вызываем фильтры')
        post_filters = await PostFilters.complete_filtering(
            new_post=update.text,
            old_posts=related_news.get('posts'),
            separator=related_news.get('separator'),
        )
        if not all(post_filters.filtration_result):
            post_is_unique = False

    if post_is_unique:
        write_new_post_rslt = await write_new_post(ch_pk=this_channel.get("pk"), text=update.text)
        # TODO: дописать обработку ответа на запрос для записи нового поста


# @Client.on_message()
async def all_updates(client, update):
    """
    Все апдейты
    """
    MY_LOGGER.success(f'Клиент {client.name!r} в работе. Получил апдейт.')
    MY_LOGGER.debug(update)
