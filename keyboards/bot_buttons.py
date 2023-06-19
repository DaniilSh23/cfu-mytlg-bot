from pyrogram.types import InlineKeyboardButton


BUTTONS_DCT = {
    'CANCEL_COMMENT': InlineKeyboardButton(
        text=f'❌ Отменить',
        callback_data='cancel_comment'
    ),
}
