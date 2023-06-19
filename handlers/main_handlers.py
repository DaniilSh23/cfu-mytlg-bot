from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from keyboards.bot_keyboards import form_webapp_kbrd
from secondary_functions.req_to_bot_api import post_for_check_user
from settings.config import START_SETTINGS_FORM


@Client.on_message(filters.command(['start', 'menu']))
async def start_handler(client, update):
    """
    Совершаем проверку наличия и активности юзера в Битриксе,
    если проверка дала положительный результат, то отдаём кнопку на форму для оставления заявки в Service Desk.
    """
    # check_usr_rslt = await post_for_check_user(tlg_username=update.from_user.username, tlg_id=update.from_user.id)
    check_usr_rslt = 200    # TODO: заглушка
    if check_usr_rslt == 200:
        await update.reply_text(
            text='Без лишних слов, предлагаю приступить к первоначальной настройке.\nНажмите на кнопку ниже👇',
            reply_markup=await form_webapp_kbrd(form_link=START_SETTINGS_FORM, btn_text='⚙️ Задать настройки')
        )

    elif check_usr_rslt == 400:
        await update.reply_text(
            text=f'Неудачная проверка доступа. Возможно у Вас не указан username в профиле Telegram 🪪'
        )

    elif check_usr_rslt == 403:
        await update.reply_text(
            text=f'К сожалению, у Вас нет доступа к дальнейшему функционалу. Вы точно сотрудник ЦФУ? 💼\n'
                 f'Также, пожалуйста, проверьте, что у Вас указан username в профиле Telegram 🪪'
        )

    elif check_usr_rslt == 502:
        await update.reply_text(
            text=f'Не удалось до конца провести проверку доступа. Проблема во взаимодействии с Битрикс. 🚧'
        )

    else:
        await update.reply_text(
            text=f'🔮 Произошло что-то непредвиденное...какая-то тёмная магия...\n'
                 f'Даже боюсь представить что, но бот не может дальше продолжать работать.'
        )
