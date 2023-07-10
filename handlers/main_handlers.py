from pyrogram import Client, filters
from keyboards.bot_keyboards import start_handler_kbrd
from secondary_functions.req_to_bot_api import post_for_write_user
from settings.config import MY_LOGGER


@Client.on_message(filters.command(['start', 'menu']))
async def start_handler(_, update):
    """
    Хэндлер для старта бота, предлагаем подключить свои каналы или вернуться к этому позже
    """
    MY_LOGGER.info(f'Стартовый хэндлер для юзера {update.from_user.id!r}')
    write_usr_rslt = await post_for_write_user(tlg_username=update.from_user.username, tlg_id=update.from_user.id)
    if write_usr_rslt:
        await update.reply_text(
            text='Привет!\nЭтот бот поможет получать только самую важную информацию и здорово сэкономит Ваше время.\n'
                 'Вы можете подключить каналы, которые уже есть в Вашем профиле Telegram или вернуться к этому позже.',
            reply_markup=await start_handler_kbrd()
        )

    else:
        MY_LOGGER.error(f'Юзер {update.from_user.id!r} получил сообщение, что у бота тех работы!')
        await update.reply_text(
            text=f'У бота технические работы. Мы скоро закончим.🪛'
        )


