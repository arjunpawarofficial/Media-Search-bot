import os
import logging

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from info import START_MSG, CHANNELS, ADMINS, INVITE_MSG
from utils.models import Media  # ← Make sure this import is correct

logger = logging.getLogger(__name__)


@Client.on_message(filters.command('start'))
async def start(bot: Client, message: Message):
    if len(message.command) > 1 and message.command[1] == 'subscribe':
        await message.reply(INVITE_MSG)
    else:
        buttons = [
            [
                InlineKeyboardButton('Search Here', switch_inline_query_current_chat=''),
                InlineKeyboardButton('Go Inline', switch_inline_query=''),
            ]
        ]
        await message.reply(START_MSG, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot: Client, message: Message):
    channels = CHANNELS if isinstance(CHANNELS, list) else [CHANNELS]

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        text += f'\n@{chat.username}' if chat.username else f'\n{chat.title or chat.first_name}'

    text += f'\n\n**Total:** {len(channels)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        with open('Indexed channels.txt', 'w') as f:
            f.write(text)
        await message.reply_document('Indexed channels.txt')
        os.remove('Indexed channels.txt')


@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot: Client, message: Message):
    msg = await message.reply("Processing...⏳", quote=True)
    try:
        total = await Media.find_all().count()
        await msg.edit(f'📁 Saved files: {total}')
    except Exception as e:
        logger.exception("Failed to check total files")
        await msg.edit(f'Error: {e}')


@Client.on_message(filters.command('logger') & filters.user(ADMINS))
async def log_file(bot: Client, message: Message):
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(f'Log file error: {e}')


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot: Client, message: Message):
    reply = message.reply_to_message
    if not (reply and reply.media):
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    msg = await message.reply("Processing...⏳", quote=True)

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media:
            media.file_type = file_type
            break
    else:
        await msg.edit('This is not a supported file format')
        return

    # Query in Beanie way
    result = await Media.find_one(
        Media.file_name == media.file_name,
        Media.file_size == media.file_size,
        Media.file_type == media.file_type,
        Media.mime_type == media.mime_type,
    )

    if result:
        await result.delete()
        await msg.edit('File is successfully deleted from database')
    else:
        await msg.edit('File not found in database')
