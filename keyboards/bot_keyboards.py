from typing import Dict, Tuple

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from keyboards.bot_buttons import BUTTONS_DCT
from settings.config import START_SETTINGS_FORM


async def form_webapp_kbrd(buttons_data):
    """
    Формирование клавиатуры с одной WebApp кнопкой
    :param buttons_data: tuple - Данные для клавиатуры ((название кнопки, ссылка на страницу), ...).
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=name,
                web_app=WebAppInfo(url=link)
            )
        ]
        for name, link in buttons_data
    ])


'''НИЖЕ СТАРОЕ, ЛЕЖИТ ПОКА ЧТО ДЛЯ ПРИМЕРА'''


async def start_handler_kbrd():
    """
    Формируем клавиатуру для стартового хэндлера.
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text='➕ Подключить свои каналы',
                web_app=WebAppInfo(url=START_SETTINGS_FORM)
            )
        ],
        [
            BUTTONS_DCT.get('COME_BACK_LATER')
        ],
    ])


async def new_comment_kbrd(task_id):
    """
    Формирование клавиатуры для сообщения с новым комментом.
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text='💬 Ответить',
                callback_data=f'answer_comment {task_id}'
            ),
        ],
    ])


CANCEL_SEND_COMMENT_KBRD = InlineKeyboardMarkup([
    [
        BUTTONS_DCT['COME_BACK_LATER'],
    ],
])
