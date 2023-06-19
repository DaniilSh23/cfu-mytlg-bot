from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from keyboards.bot_buttons import BUTTONS_DCT


async def form_webapp_kbrd(form_link, btn_text):
    """
    Формирование клавиатуры для перехода к форме, которая реализована через веб-приложение.
    :param form_link: ссылка на веб-форму.
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=btn_text,
                web_app=WebAppInfo(url=form_link)
            )
        ],
    ])


'''НИЖЕ СТАРОЕ, ЛЕЖИТ ПОКА ЧТО ДЛЯ ПРИМЕРА'''


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
        BUTTONS_DCT['CANCEL_COMMENT'],
    ],
])
