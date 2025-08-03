from utils.models import Media

async def get_search_results(query, file_type=None, max_results=10, offset=0):
    filters = {}
    if query:
        filters["file_name"] = {"$regex": query, "$options": "i"}
    if file_type:
        filters["file_type"] = file_type

    cursor = Media.find(filters).skip(offset).limit(max_results)
    results = await cursor.to_list()
    next_offset = offset + len(results) if results else ""
    return results, next_offset
