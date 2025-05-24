from database.models import URLRecord
from database.session import AsyncSessionLocal
from sqlalchemy import select
from typing import List
from typing import Optional
from typing import Tuple


async def create_url_entry(url: str) -> URLRecord:
    """
    Create url data record
    Args:
        url: input url
    """
    async with AsyncSessionLocal() as session:
        entry = URLRecord(url=url, status="pending")
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        return entry


async def update_url_entry(id: int, image_url: str, status: str):
    """
    Update url data record
    Args:
        id: URLRecord id
        image_url: image url
        status: processing status
    """
    async with AsyncSessionLocal() as session:
        entry = await session.get(URLRecord, id)
        if entry:
            entry.image_url = image_url
            entry.status = status
            await session.commit()


async def get_url_entry_by_url(url: str) -> Optional[URLRecord]:
    """
    Get url data record by url
    Args:
        url: input url
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(URLRecord).where(URLRecord.url == url))
        return result.scalar_one_or_none()


async def get_url_entry_by_id(id: int) -> Optional[URLRecord]:
    """
    Get url data record by id
    Args:
        url: URLRecord id
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(URLRecord).where(URLRecord.id == id))
        return result.scalar_one_or_none()


async def get_all_entries(
    limit: int = 10,
    cursor: Optional[int] = None,
    is_desc_order: bool = True,
) -> Tuple[List[URLRecord], Optional[int]]:
    """
    Get all entries
    Args:
    Inputs:
        limit: size per page
        cursor: URLRecord id.
            If invalid, get the first limit number of records, else, filter from cursor
            Note: the output will include this cursor's URLRecord
        is_desc_order: if False, sort in descending order, else, sort in ascending order
    Outputs:
        list of URLRecord
        next cursor
    """
    async with AsyncSessionLocal() as session:
        stmt = select(URLRecord)
        if cursor:
            if is_desc_order:
                stmt = stmt.where(URLRecord.id <= cursor)
            else:
                stmt = stmt.where(URLRecord.id >= cursor)

        stmt = stmt.order_by(URLRecord.id.desc() if is_desc_order else URLRecord.id.asc())
        stmt = stmt.limit(limit + 1) # fetch one extra to determine if next_cursor is available

        result = await session.execute(stmt)
        entries = result.scalars().all()

        # Check for next cursor
        has_more = len(entries) > limit
        if has_more:
            next_cursor = entries[-1].id
            entries = entries[:-1]  # Remove the extra one
        else:
            next_cursor = None
        return entries, next_cursor
