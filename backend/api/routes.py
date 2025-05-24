import logging
from api.schemas import PaginatedURLInfo
from api.schemas import URLInfo
from api.schemas import URLSubmit
from database import crud
from fastapi import APIRouter
from settings import REDIS_CLIENT
from services.og_scraper import cache_save
from services.og_scraper import process_og_url_by_entry_id
from typing import Optional


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/submit", response_model=URLInfo)
async def submit_url(payload: URLSubmit):
    """
    Response image_url for given url by scraping the og tag image attribute.
    Args:
        input: URLSubmit
        output: URLInfo
    """
    url = payload.url
    cached_image_url = await REDIS_CLIENT.get(url)

    # CASE 1: Cache hit
    if cached_image_url:
        logging.info(f"API - Submit - cache hit - url: {url}, image_url: {cached_image_url}")
        return await crud.get_url_entry_by_url(url)

    # CASE 2: No cache — check if DB already has it
    db_entry = await crud.get_url_entry_by_url(url)
    if db_entry:
        if db_entry.image_url:
            logging.info(f"API - Submit - existing entry - no image_url - url: {url}, image_url: {db_entry.image_url}")
            await cache_save(url, db_entry.image_url)
            return db_entry
        else:
            # retry processing and cache the value
            logging.info(f"API - Submit - existing entry - has image_url - url: {url}, image_url: {db_entry.image_url}")
            await process_og_url_by_entry_id(db_entry.id)
            return await crud.get_url_entry_by_id(db_entry.id)

    # CASE 3: New URL — processing the url
    db_entry = await crud.create_url_entry(url)

    await process_og_url_by_entry_id(db_entry.id)
    entry = await crud.get_url_entry_by_id(db_entry.id)
    logging.info(f"API - Submit - create new entry - url: {url}, image_url: {entry.image_url}")
    return entry


@router.get("/history", response_model=PaginatedURLInfo)
async def get_history(limit: int = 10, cursor: Optional[str] = None):
    """
    Get all history records of the user url og tag queries
    Args:
        Input:
            limit: size per page
            cursor: id of the record as the cursor
        Output:
            PaginatedURLInfo
    """
    cursor = int(cursor) if cursor else None
    entries, next_cursor = await crud.get_all_entries(limit=limit, cursor=cursor, is_desc_order=True)
    return PaginatedURLInfo(
        results=[URLInfo.from_orm(entry) for entry in entries],
        next_cursor=next_cursor
    )
