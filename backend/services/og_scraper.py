import httpx
import logging
from bs4 import BeautifulSoup
from database.enums import URLStatus
from database.models import URLRecord
from database.session import AsyncSessionLocal
from database.session import init_db
from database import crud
from settings import REDIS_CLIENT
from typing import Optional


REDIS_OG_PROCESS_EXPIRATION_SECONDS = 60 * 5

logger = logging.getLogger(__name__)

async def extract_og_image(url: str) -> Optional[str]:
    """
    Extract the OG image from the url
    Args:
        Input:
            url: input url
        Output:
            image_url
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            tag = soup.find("meta", property="og:image")
            image_url = tag["content"] if tag else None
            logging.info(f"Extract og tag from url: {url}, image_url: {image_url}")
            return image_url
    except Exception as e:
        logging.exception(f"Extract og tag from url: {url} error: {e}")
        return None


async def cache_save(url: str, image_url: str, ttl: int = REDIS_OG_PROCESS_EXPIRATION_SECONDS):
    """
    Save the url, image_url as key, value with TTL to the cache.
    """
    await REDIS_CLIENT.set(url, image_url, ex=ttl)


async def process_og_url_by_entry_id(id: int):
    """
    Process the og tag based on entry id and save the value to the cache
    Args:
        Input:
            id: input URLRecord id
    """
    await init_db()
    async with AsyncSessionLocal() as session:
        entry = await session.get(URLRecord, id)
        if entry:
            url = entry.url
            image_url = await extract_og_image(url)
            if image_url:
                status = URLStatus.SUCCESS.value if image_url else URLStatus.FAILED.value
                await cache_save(url, image_url)
                await crud.update_url_entry(id, image_url or "", status)
