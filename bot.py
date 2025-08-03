import logging
import logging.config
from pathlib import Path

from pyrogram import Client, __version__ as pyrogram_version
from pyrogram.raw.all import layer

# Local imports (update these if your structure is different)
from core.utils.media import Media  # Assuming Media is now in core/utils/media.py
from info import SESSION, API_ID, API_HASH, BOT_TOKEN


# Setup logging
def setup_logging():
    config_path = Path("logging.conf")
    if config_path.exists():
        logging.config.fileConfig(config_path)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    logging.getLogger().setLevel(logging.WARNING)


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
        self.username: str = ""

    async def start(self):
        await super().start()
        await Media.ensure_indexes()

        me = await self.get_me()
        self.username = f"@{me.username}"
        print(f"{me.first_name} running on Pyrogram v{pyrogram_version} (Layer {layer}) as {self.username}.")

    async def stop(self, *args):
        await super().stop()
        print("Bot stopped. Bye.")


if __name__ == "__main__":
    setup_logging()
    app = Bot()
    app.run()
