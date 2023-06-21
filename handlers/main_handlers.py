from pyrogram import Client, filters
from keyboards.bot_keyboards import form_webapp_kbrd
from secondary_functions.req_to_bot_api import post_for_write_user
from settings.config import START_SETTINGS_FORM, MY_LOGGER


@Client.on_message(filters.command(['start', 'menu']))
async def start_handler(_, update):
    """
    Совершаем проверку наличия и активности юзера в Битриксе,
    если проверка дала положительный результат, то отдаём кнопку на форму для оставления заявки в Service Desk.
    """
    MY_LOGGER.info(f'Стартовый хэндлер для юзера {update.from_user.id!r}')
    write_usr_rslt = await post_for_write_user(tlg_username=update.from_user.username, tlg_id=update.from_user.id)
    if write_usr_rslt:
        await update.reply_text(
            text='Без лишних слов, предлагаю приступить к первоначальной настройке.\nНажмите на кнопку ниже👇',
            reply_markup=await form_webapp_kbrd(form_link=START_SETTINGS_FORM, btn_text='⚙️ Задать настройки')
        )

    else:
        MY_LOGGER.error(f'Юзер {update.from_user.id!r} получил сообщение, что у бота тех работы!')
        await update.reply_text(
            text=f'У бота технические работы. Мы скоро закончим.🪛'
        )
