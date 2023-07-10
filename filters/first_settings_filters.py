from pyrogram import filters
from pyrogram.types import CallbackQuery


async def func_come_back_later_filter(_, __, update: CallbackQuery):
    """
    Функция фильтрации для хэндлера come_back_later_handler
    """
    if update.data:
        return update.data == 'come_back_later'

come_back_later_filter = filters.create(func_come_back_later_filter)
