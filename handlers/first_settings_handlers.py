from pyrogram import Client
from pyrogram.types import CallbackQuery, Message

from filters.first_settings_filters import come_back_later_filter
from keyboards.bot_keyboards import form_webapp_kbrd
from settings.config import WRITE_INTERESTS_FORM


@Client.on_callback_query(come_back_later_filter)
async def come_back_later_handler(client, update: CallbackQuery):
    """
    Хэндлер для обработки нажатия кнопки "Вернуться позже"
    """
    await update.answer(f'👌 Окей. Вернёмся позже...')
    await update.edit_message_text(
        text='✏️ Давайте <b>сформулируем Ваши интересы.</b>\n👇 Нажмите на кнопку ниже',
        reply_markup=await form_webapp_kbrd(form_link=WRITE_INTERESTS_FORM, btn_text='✏️ Записать интересы')
    )
