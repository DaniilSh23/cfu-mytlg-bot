import os
import sys

import loguru
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('TOKEN', '5265303938:AAE1daGp-VJR0R15J9tHksR38hQlbCXMYdU')
BOT_USERNAME = os.environ.get('BOT_USERNAME', 'CourseTrainBot')
API_ID = os.environ.get('API_ID', '1234567890')
API_HASH = os.environ.get('API_HASH', 'какой-то там хэш')
BOT_MANAGER_ID = os.environ.get('BOT_MANAGER_ID', 1978587604)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'ключик от API OpenAI')

# Абсолютный путь к директории проекта
BASE_DIR = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]

# Константы для API Django проекта
BASE_HOST_URL = os.environ.get('BASE_HOST_URL', 'http://127.0.0.1:8000/')
WRITE_USR_URL = f'{BASE_HOST_URL}mytlg/write_usr/'
SET_ACC_RUN_FLAG_URL = f'{BASE_HOST_URL}mytlg/set_acc_run_flag/'
SET_ACC_FLAGS_URL = f'{BASE_HOST_URL}mytlg/set_acc_flags/'
GET_CHANNELS_URL = f'{BASE_HOST_URL}mytlg/get_channels/'
GET_SETTINGS_URL = f'{BASE_HOST_URL}mytlg/get_settings/'
GET_RELATED_NEWS = f'{BASE_HOST_URL}mytlg/related_news/'
WRITE_SUBSCRIPTION_RSLT = f'{BASE_HOST_URL}mytlg/write_subs_rslt/'
UPDATE_CHANNELS = f'{BASE_HOST_URL}mytlg/update_channels/'
GET_ACTIVE_ACCOUNTS = f'{BASE_HOST_URL}mytlg/get_active_accounts/'
ACCOUNT_ERR_URL = f'{BASE_HOST_URL}mytlg/account_error/'

# Ссылки на веб-страницы
START_SETTINGS_FORM = f'{BASE_HOST_URL}mytlg/start_settings/'
WRITE_INTERESTS_FORM = f'{BASE_HOST_URL}mytlg/write_interests/'
# TODO: закомментить, это тест
# START_SETTINGS_FORM = f'https://yandex.ru'
# WRITE_INTERESTS_FORM = f'https://yandex.ru'


# Настройки логгера
MY_LOGGER = loguru.logger
MY_LOGGER.remove()  # Удаляем все предыдущие обработчики логов
MY_LOGGER.add(sink=sys.stdout, level='DEBUG')   # Все логи от DEBUG и выше в stdout
MY_LOGGER.add(  # системные логи в файл
    sink=f'{BASE_DIR}/logs/sys_log.log',
    level='DEBUG',
    rotation='2 MB',
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True
)

# Словари для хранения чего-либо
#
# Словарь для запущенных клиентов
WORKING_CLIENTS = dict()
# Каналы для запущенных клиентов
# [{'pk': int, 'channel_id': str, 'channel_name': str, 'channel_link': str}, ...]
CLIENT_CHANNELS = dict()
# Состояния бота
STATES_DCT = dict()

# Разные константы
PAUSE_BETWEEN_JOIN_TO_CHANNELS = tuple(map(lambda x: int(x), os.environ.get("PAUSE_BETWEEN_JOIN_TO_CHANNELS").split()))
PAUSE_BETWEEN_FIVE_CHANNELS = tuple(map(lambda x: int(x), os.environ.get("PAUSE_BETWEEN_FIVE_CHANNELS").split()))
FLOOD_WAIT_LIMIT = int(os.environ.get("FLOOD_WAIT_LIMIT"))

SENTRY_DSN = os.environ.get("SENTRY_DSN")
