from pyrogram import filters
from pyrogram.types import Message, CallbackQuery

from settings.config import ANSWER_COMMENT_STATES


async def func_new_comment_filter(_, __, update: Message):
    """
    Фильтрация апдейтов, в которых прилетает новый коммент
    """
    if update.text:
        return update.text.startswith('**comment')


async def func_answer_comment_filter(_, __, update: CallbackQuery):
    """
    Фильтр для нажатия на кнопку "ответить" на коммент.
    """
    if update.data:
        return update.data.split()[0] == 'answer_comment'


async def func_cancel_comment_answer_filter(_, __, update: CallbackQuery):
    """
    Фильтр для нажатия на кнопку отмены ответа на коммент.
    """
    if update.data:
        return update.data.split()[0] == 'cancel_comment'


async def func_send_comment_answer_filter(_, __, update: Message):
    """
    Фильтр сообщений - ответов на коммент.
    """
    comment_data = ANSWER_COMMENT_STATES.get(update.from_user.id)
    if comment_data:
        return comment_data.split()[0] == 'input_comment'


new_comment_filter = filters.create(func_new_comment_filter)
answer_comment_filter = filters.create(func_answer_comment_filter)
cancel_comment_answer_filter = filters.create(func_cancel_comment_answer_filter)
send_comment_answer_filter = filters.create(func_send_comment_answer_filter)
