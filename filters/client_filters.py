from pyrogram import filters

from settings.config import CLIENT_CHANNELS, MY_LOGGER


async def func_listening_channel_filter(_, client, update):
    """
    Фильтрация апдейта из канала, который прослушивает аккаунт.
    """
    if not update.text:
        MY_LOGGER.warning(f'У поста отсутствует текст, он не будет передан в хэндлер!')
        return False

    channels = CLIENT_CHANNELS[client.acc_pk]
    ch_ids_lst = [str(i_ch.get('channel_id')) for i_ch in channels]
    return update.chat and str(update.chat.id) in ch_ids_lst


listening_channel_filter = filters.create(func_listening_channel_filter)
