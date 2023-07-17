import aiohttp as aiohttp
from settings.config import MY_LOGGER, WRITE_USR_URL, TOKEN


async def post_for_write_user(tlg_id: str, tlg_username: str):
    """
    Вьюшка для стартовой записи или обновления в БД инфы о юзере телеграм.
    """
    data = {
        'token': TOKEN,
        "tlg_id": tlg_id,
        "tlg_username": tlg_username,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=WRITE_USR_URL, data=data) as response:
            if response.status == 200:
                MY_LOGGER.info(f"Успешный запрос для записи или обновления данных о юзере: {await response.json()}")
                return True
            else:
                MY_LOGGER.error(f"Неудачный запрос для записи инфы о юзере: "
                                f"status={response.status}|{response.text}")
