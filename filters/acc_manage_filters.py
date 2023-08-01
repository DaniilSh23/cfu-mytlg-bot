from pyrogram import filters
from pyrogram.types import Message

from settings.config import BOT_MANAGER_ID


async def func_start_client_filter(_, __, update: Message):
    """
    Фильтрация апдейтов с командами боту стартовать клиент
    """
    if update.chat.id == int(BOT_MANAGER_ID):
        if update.caption:
            return update.caption.startswith('/start_acc') and len(update.caption.split()) >= 3


async def func_stop_client_filter(_, __, update: Message):
    """
    Фильтрация апдейтов с командами боту стартовать клиент
    """
    if update.chat.id == int(BOT_MANAGER_ID):
        if update.caption:
            return update.caption.startswith('/stop_acc') and len(update.caption.split()) >= 3


async def func_update_acc_channels_filter(_, __, update: Message):
    """
    Функция фильтрации для хэндлера обновления списка каналов для заданного аккаунта.
    """
    if update.chat.id == int(BOT_MANAGER_ID):
        if update.text:
            return update.text.startswith('*&*&update_channels') and len(update.text.split()) == 2


start_client_filter = filters.create(func_start_client_filter)
stop_client_filter = filters.create(func_stop_client_filter)
update_acc_channels_filter = filters.create(func_update_acc_channels_filter)
