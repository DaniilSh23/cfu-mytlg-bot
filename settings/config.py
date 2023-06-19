import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('TOKEN', '5265303938:AAE1daGp-VJR0R15J9tHksR38hQlbCXMYdU')
API_ID = os.environ.get('API_ID', '1234567890')
API_HASH = os.environ.get('API_HASH', 'какой-то там хэш')

# Константы для API Django проекта
BASE_HOST_URL = os.environ.get('BASE_HOST_URL', 'http://127.0.0.1:8000/')
CHECK_USER_URL = f'{BASE_HOST_URL}service_desk_bot/check_user/'     # TODO: пока лежит для примера

# Ссылки на веб-страницы
BASE_HOST_URL = 'https://yandex.ru/'    # TODO: это пока что заглушка, потом удалить
START_SETTINGS_FORM = f'{BASE_HOST_URL}mytlg/start_settings/'

# Состояния
STATES_DCT = dict()