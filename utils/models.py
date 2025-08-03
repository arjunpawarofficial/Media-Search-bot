from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import Field
from typing import Optional
import datetime


class Media(Document):
    file_id: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    caption: Optional[str] = None
    added_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Settings:
        name = "Telegram_files"  # collection name

    class Config:
        arbitrary_types_allowed = True  # in case non-JSON types are added in future

    @classmethod
    async def ensure_indexes(cls):
        await cls.creat
