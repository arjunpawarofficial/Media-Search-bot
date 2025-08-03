import logging
import logging.config

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from info import SESSION, API_ID, API_HASH, BOT_TOKEN
from utils.database import init_db, Media  

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

   class Bot(Client):
    async def start(self):
        await super().start()
        await init_db()  # initialize beanie here
        me = await self.get_me()
        self.username = '@' + me.username
        print(f"{me.first_name} running as Pyrogram v{__version__} (Layer {layer}) on {me.username}")


    async def stop(self, *args):
        await super().stop()
        print("Bot stopped. Bye.")


if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    logging.getLogger().setLevel(logging.WARNING)
    
    app = Bot()
    app.run()
