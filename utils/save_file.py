from utils.models import Media

async def save_file(media):
    await Media(
        file_id=media.file_id,
        file_name=media.file_name,
        file_size=media.file_size,
        file_type=media.file_type,
        mime_type=media.mime_type,
        caption=media.caption
    ).insert()
