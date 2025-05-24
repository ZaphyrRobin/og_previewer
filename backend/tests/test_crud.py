import unittest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database.models import Base, URLRecord
from database import crud

class TestCRUDOperations(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Create in-memory SQLite DB
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

        # Override the actual session
        crud.AsyncSessionLocal = self.async_session

        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def asyncTearDown(self):
        await self.engine.dispose()

    async def test_create_and_get_url_entry(self):
        url = "https://example.com"
        entry = await crud.create_url_entry(url)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.url, url)
        self.assertEqual(entry.status, "pending")

        fetched = await crud.get_url_entry_by_url(url)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.id, entry.id)

        fetched_by_id = await crud.get_url_entry_by_id(entry.id)
        self.assertEqual(fetched_by_id.url, url)

    async def test_update_url_entry(self):
        entry = await crud.create_url_entry("https://test.com")
        await crud.update_url_entry(entry.id, "https://image.com/img.jpg", "success")

        updated = await crud.get_url_entry_by_id(entry.id)
        self.assertEqual(updated.image_url, "https://image.com/img.jpg")
        self.assertEqual(updated.status, "success")

    async def test_get_all_entries_pagination(self):
        # Insert 15 entries
        for i in range(15):
            await crud.create_url_entry(f"https://site{i}.com")

        entries, next_cursor = await crud.get_all_entries(limit=10)
        self.assertEqual(len(entries), 10)
        self.assertIsNotNone(next_cursor)

        # Fetch next page
        entries2, next_cursor2 = await crud.get_all_entries(limit=10, cursor=next_cursor)
        self.assertEqual(len(entries2), 5)
        self.assertIsNone(next_cursor2)

    async def test_get_all_entries_ascending(self):
        # Insert 3 entries
        urls = [f"https://asc{i}.com" for i in range(3)]
        for u in urls:
            await crud.create_url_entry(u)

        entries, _ = await crud.get_all_entries(limit=3, is_desc_order=False)
        self.assertEqual([e.url for e in entries], urls)

if __name__ == "__main__":
    unittest.main()
