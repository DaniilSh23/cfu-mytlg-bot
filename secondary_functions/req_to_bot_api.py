import aiohttp as aiohttp
from loguru import logger
from settings.config import CHECK_USER_URL


async def post_for_check_user(tlg_username, tlg_id):
    """
    POST запрос для проверки пользователя в системе Битрикс.

    Принимает параметры:
        tlg_username - username пользователя в телеграме
        tlg_id - ID пользователя в телеграме

    Возвращает статус коды:
        200 - юзер успешно прошёл проверку,
        400 - неверный запрос, стоит также проверить параметры запроса,
        403 - юзер не прошёл проверку и не может получить доступ к боту,
        502 - неудачный запрос к API Битрикса.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url=CHECK_USER_URL, data={'tlg_username': tlg_username, 'tlg_id': tlg_id}) as response:
            if response.status == 200:
                logger.success(f'Успешный POST запрос для проверки юзера с tlg_username == {tlg_username}. Код 200')
                return 200
            elif response.status == 400:
                logger.warning(f'Неудачный запрос для проверки юзера с tlg_username == {tlg_username}. Код 400')
                return 400
            elif response.status == 403:
                logger.warning(f'Юзер с tlg_username == {tlg_username} не прошёл проверку в Битриксе. Код 403')
                return 403
            elif response.status == 502:
                logger.warning(f'При проверке юзера с tlg_username == {tlg_username} не удался запрос к Битриксу '
                               f'для записи tlg_id. Код 502')
                return 502
            else:
                logger.warning(f'Вообще хз, что тут произошло ещё.')
                return
