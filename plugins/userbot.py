import logging
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait

from info import USERBOT_STRING_SESSION, API_ID, API_HASH, ADMINS, id_pattern
from utils import save_file

logger = logging.getLogger(__name__)
lock = asyncio.Lock()


@Client.on_message(filters.command(['index', 'indexfiles']) & filters.user(ADMINS))
async def index_files_handler(bot, message):
    """Save channel or group files with the help of userbot"""

    if not USERBOT_STRING_SESSION:
        return await message.reply(
            'Set `USERBOT_STRING_SESSION` in info.py file or in environment variables.'
        )

    if len(message.command) == 1:
        return await message.reply(
            'Please specify channel username or ID in command.\n\nExample: `/index -10012345678`'
        )

    if lock.locked():
        return await message.reply('Wait until previous indexing process completes.')

    reply_msg = await message.reply('Processing... ⏳')
    raw_data = message.command[1:]
    chats = [int(chat) if id_pattern.search(chat) else chat for chat in raw_data]

    total_files = 0
    user_bot = Client("UserBot", api_id=API_ID, api_hash=API_HASH, session_string=USERBOT_STRING_SESSION)

    async with lock:
        try:
            async with user_bot:
                for chat in chats:
                    async for user_msg in user_bot.get_chat_history(chat):
                        try:
                            full_msg = await bot.get_messages(chat, user_msg.id)
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                            full_msg = await bot.get_messages(chat, user_msg.id)

                        for file_type in ("document", "video", "audio"):
                            media = getattr(full_msg, file_type, None)
                            if media is not None:
                                break
                        else:
                            continue

                        media.file_type = file_type
                        media.caption = full_msg.caption
                        await save_file(media)
                        total_files += 1

        except Exception as e:
            logger.exception(e)
            return await reply_msg.edit(f'Error occurred: `{e}`')

        await reply_msg.edit(f'Total **{total_files}** media files indexed ✅')
