import re
import logging

from pymongo.errors import DuplicateKeyError
from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, USE_CAPTION_FILTER
from .helpers import unpack_new_file_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(DATABASE_URI)
database = client[DATABASE_NAME]

# Define the Media model here directly (instead of utils.models)
class Media(Document):
    file_id: str
    file_ref: Optional[str]
    file_name: str
    file_size: int
    file_type: Optional[str]
    mime_type: Optional[str]
    caption: Optional[str]

    class Settings:
        name = COLLECTION_NAME
        indexes = ["file_name"]

# Call once when app starts
async def init_db():
    await init_beanie(database=database, document_models=[Media])

# Save media file to DB
async def save_file(media):
    file_id, file_ref = unpack_new_file_id(media.file_id)

    try:
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=media.file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
        )
        await file.insert()
        logger.info(media.file_name + " saved in database")
    except DuplicateKeyError:
        logger.warning(media.file_name + " already exists in database")
    except Exception:
        logger.exception("Error while saving file")

# Search function
async def get_search_results(query, file_type=None, max_results=10, offset=0):
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_\(\)\[\]]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error:
        return [], ''

    search_filter = {
        "$or": [{"file_name": {"$regex": regex}}],
    }

    if USE_CAPTION_FILTER:
        search_filter["$or"].append({"caption": {"$regex": regex}})

    if file_type:
        search_filter["file_type"] = file_type

    # Mongo-style query for Beanie
    results = await Media.find(search_filter).skip(offset).limit(max_results).to_list()
    total = await Media.find(search_filter).count()

    next_offset = offset + max_results if offset + max_results < total else ''

    return results, next_offset
