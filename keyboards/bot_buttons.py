from pyrogram.types import InlineKeyboardButton


BUTTONS_DCT = {
    'COME_BACK_LATER': InlineKeyboardButton(
        text=f'Вернуться позже',
        callback_data='come_back_later'
    ),
}
