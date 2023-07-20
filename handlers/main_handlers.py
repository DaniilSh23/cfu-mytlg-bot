from pyrogram import Client, filters
from keyboards.bot_keyboards import form_webapp_kbrd
from utils.req_to_bot_api import post_for_write_user
from settings.config import MY_LOGGER, WRITE_INTERESTS_FORM


@Client.on_message(filters.command(['start', 'menu']))
async def start_handler(_, update):
    """
    Хэндлер для старта бота, предлагаем подключить свои каналы или вернуться к этому позже
    """
    MY_LOGGER.info(f'Стартовый хэндлер для юзера {update.from_user.id!r}')
    write_usr_rslt = await post_for_write_user(tlg_username=update.from_user.username, tlg_id=update.from_user.id)
    if write_usr_rslt:
        await update.reply_text(
            text=f'👋 Привет!\n\n⏳ Этот бот создан, чтобы экономить Ваше время.'
                 f'\n\nКак?\n🌊 Он позволяет <b>не распылять внимание на бурный поток информации</b>, '
                 f'а сам подготовит для Вас всё самое интересное и актуальное\n\n'
                 f'✏️ <b>Для старта Вам необходимо только заполнить свои интересы.</b>',
            reply_markup=await form_webapp_kbrd(form_link=WRITE_INTERESTS_FORM, btn_text='✏️ Записать интересы')
        )

    else:
        MY_LOGGER.error(f'Юзер {update.from_user.id!r} получил сообщение, что у бота тех работы!')
        await update.reply_text(
            text=f'У бота технические работы. Мы скоро закончим.🪛'
        )


