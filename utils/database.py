import re
import logging
from typing import Optional, Tuple, List

from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from pydantic import BaseModel

from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, USE_CAPTION_FILTER

from .helpers import unpack_new_file_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global MongoDB client
client = AsyncIOMotorClient(DATABASE_URI)


# Pydantic-style Beanie document
class Media(Document):
    file_id: str
    file_ref: Optional[str] = None
    file_name: str
    file_size: int
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    caption: Optional[str] = None

    class Settings:
        name = COLLECTION_NAME
        indexes = ["file_name"]


# Call this once at app startup
async def init_db():
    await init_beanie(database=client[DATABASE_NAME], document_models=[Media])


# Save media to MongoDB
async def save_file(media):
    file_id, file_ref = unpack_new_file_id(media.file_id)

    file = Media(
        file_id=file_id,
        file_ref=file_ref,
        file_name=media.file_name,
        file_size=media.file_size,
        file_type=media.file_type,
        mime_type=media.mime_type,
        caption=media.caption.html if media.caption else None,
    )

    try:
        await file.insert()
        logger.info(f"{media.file_name} is saved in the database.")
    except DuplicateKeyError:
        logger.warning(f"{media.file_name} is already saved in the database.")


# Search and paginate results
async def get_search_results(query: str, file_type: Optional[str] = None, max_results: int = 10, offset: int = 0) -> Tuple[List[Media], str]:
    query = query.strip()
    if not query:
        raw_pattern = "."
    elif " " not in query:
        raw_pattern = r"(\b|[\.\+\-_])" + re.escape(query) + r"(\b|[\.\+\-_])"
    else:
        raw_pattern = re.escape(query).replace(r"\ ", r".*[\s\.\+\-_\(\)\[\]]")

    try:
        regex = re.compile(raw_pattern, re.IGNORECASE)
    except re.error:
        return [], ""

    filters = {}
    if USE_CAPTION_FILTER:
        filters = {
            "$or": [
                {"file_name": {"$regex": regex}},
                {"caption": {"$regex": regex}},
            ]
        }
    else:
        filters = {"file_name": {"$regex": regex}}

    if file_type:
        filters["file_type"] = file_type

    total_results = await Media.find(filters).count()
    next_offset = offset + max_results if offset + max_results < total_results else ""

    files = (
        await Media.find(filters)
        .sort("-_id")  # newest first
        .skip(offset)
        .limit(max_results)
        .to_list()
    )

    return files, str(next_offset)
