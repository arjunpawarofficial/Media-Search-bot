from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional
import datetime

class Media(Document):
    file_id: str
    file_name: Optional[str]
    file_size: Optional[int]
    file_type: Optional[str]
    mime_type: Optional[str]
    caption: Optional[str]
    added_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Settings:
        name = "Telegram_files"

    @classmethod
    async def ensure_indexes(cls):
        await cls.create_index("file_name")
        await cls.create_index("file_id")
