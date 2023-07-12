import os
import sys

import loguru
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('TOKEN', '5265303938:AAE1daGp-VJR0R15J9tHksR38hQlbCXMYdU')
API_ID = os.environ.get('API_ID', '1234567890')
API_HASH = os.environ.get('API_HASH', 'какой-то там хэш')

# Абсолютный путь к директории проекта
BASE_DIR = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]

# Константы для API Django проекта
BASE_HOST_URL = os.environ.get('BASE_HOST_URL', 'http://127.0.0.1:8000/')
WRITE_USR_URL = f'{BASE_HOST_URL}mytlg/write_usr/'

# Ссылки на веб-страницы
START_SETTINGS_FORM = f'{BASE_HOST_URL}mytlg/start_settings/'
WRITE_INTERESTS_FORM = f'{BASE_HOST_URL}mytlg/write_interests/'
# TODO: закомментить, это тест
# START_SETTINGS_FORM = f'https://yandex.ru'
# WRITE_INTERESTS_FORM = f'https://yandex.ru'

# Состояния
STATES_DCT = dict()

# Настройки логгера
MY_LOGGER = loguru.logger
MY_LOGGER.remove()  # Удаляем все предыдущие обработчики логов
MY_LOGGER.add(sink=sys.stdout, level='DEBUG')   # Все логи от DEBUG и выше в stdout
MY_LOGGER.add(  # системные логи в файл
    sink=f'{BASE_DIR}/logs/sys_log.log',
    level='DEBUG',
    rotation='10 MB',
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True
)