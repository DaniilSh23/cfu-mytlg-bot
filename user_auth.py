from pyrogram import Client

from settings.config import API_ID, API_HASH

api_id = API_ID
api_hash = API_HASH

app = Client(
    "my_acc2",
    api_id=api_id, api_hash=api_hash,
)

app.run()
