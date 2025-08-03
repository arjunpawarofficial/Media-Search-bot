from pyrogram import Client, filters
from pyrogram.types import Message, Document, Audio, Video

from info import CHANNELS
from utils import save_file  # Your Beanie-based file save function

# Match only documents, videos, or audios
media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media_handler(client: Client, message: Message):
    """Handle media files from monitored channels"""

    media = None
    file_type = None

    if message.document:
        media = message.document
        file_type = "document"
    elif message.video:
        media = message.video
        file_type = "video"
    elif message.audio:
        media = message.audio
        file_type = "audio"

    if not media:
        return  # Shouldn't occur due to filter, but safe check

    # Inject required attributes before saving
    media.file_type = file_type
    media.caption = message.caption

    await save_file(media)
