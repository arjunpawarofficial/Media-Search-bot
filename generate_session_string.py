import logging
import logging.config
import asyncio
from pyrogram import Client
from info import API_ID, API_HASH

# Setup logging
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logging.getLogger().setLevel(logging.WARNING)

async def main():
    """Generate session string for user bot"""
    phone_number = input('Enter phone number with country code (e.g., +91xxxxxxxxxx): ')

    user_bot = Client(
        name="userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone_number,
        in_memory=True  # Ensures session is not saved to a file
    )

    async with user_bot:
        session_string = await user_bot.export_session_string()
        print(f"\n✅ Your Pyrogram session string:\n\n{session_string}\n")

if __name__ == "__main__":
    asyncio.run(main())
