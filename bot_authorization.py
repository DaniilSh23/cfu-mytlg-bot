import asyncio
import subprocess

from pyrogram import Client

from settings.config import TOKEN, API_ID, API_HASH

api_id = API_ID
api_hash = API_HASH
bot_token = TOKEN


# app = Client(
#     "test_bot",
#     api_id=api_id, api_hash=api_hash,
#     bot_token=bot_token
# )
#
# app.run()

async def main():
    async with Client("test_bot", api_id, api_hash, bot_token=bot_token) as app:
        rslt = await app.get_me()
        command = f"echo 'Запущен скрипт получения файла сессии для бота. Результат метода get_me():{rslt}'"
        process = subprocess.Popen(command, shell=True)
        process.wait()


asyncio.run(main())