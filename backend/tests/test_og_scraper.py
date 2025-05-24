import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from services.og_scraper import extract_og_image, cache_save, process_og_url_by_entry_id
from database.enums import URLStatus

HTML_WITH_OG = '<html><head><meta property="og:image" content="https://example.com/image.jpg"></head></html>'
HTML_NO_OG = '<html><head><title>No OG</title></head></html>'

class TestOGProcessor(unittest.IsolatedAsyncioTestCase):
    @patch("services.og_scraper.httpx.AsyncClient.get")
    async def test_extract_og_image_success(self, mock_get):
        mock_get.return_value.text = HTML_WITH_OG
        result = await extract_og_image("https://example.com")
        print('testing...')
        self.assertEqual(result, "https://example.com/image.jpg")

    @patch("services.og_scraper.httpx.AsyncClient.get")
    async def test_extract_og_image_no_tag(self, mock_get):
        mock_get.return_value.text = HTML_NO_OG
        result = await extract_og_image("https://example.com")
        self.assertIsNone(result)

    @patch("services.og_scraper.httpx.AsyncClient.get", side_effect=Exception("Timeout"))
    async def test_extract_og_image_exception(self, mock_get):
        result = await extract_og_image("https://timeout.com")
        self.assertIsNone(result)

    @patch("services.og_scraper.REDIS_CLIENT.set", new_callable=AsyncMock)
    async def test_cache_save(self, mock_set):
        await cache_save("https://example.com", "https://example.com/image.jpg", ttl=60)
        mock_set.assert_awaited_once_with("https://example.com", "https://example.com/image.jpg", ex=60)

    @patch("services.og_scraper.init_db", new_callable=AsyncMock)
    @patch("services.og_scraper.AsyncSessionLocal")
    @patch("services.og_scraper.extract_og_image", return_value="https://example.com/image.jpg")
    @patch("services.og_scraper.cache_save", new_callable=AsyncMock)
    @patch("services.og_scraper.crud.update_url_entry", new_callable=AsyncMock)
    async def test_process_og_url_success(
        self, mock_update, mock_cache, mock_extract, mock_session_local, mock_init_db
    ):
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=MagicMock(id=1, url="https://example.com"))
        mock_session_local.return_value.__aenter__.return_value = mock_session

        await process_og_url_by_entry_id(1)

        mock_extract.assert_awaited_once_with("https://example.com")
        mock_cache.assert_awaited_once_with("https://example.com", "https://example.com/image.jpg")
        mock_update.assert_awaited_once_with(1, "https://example.com/image.jpg", URLStatus.SUCCESS.value)

    @patch("services.og_scraper.init_db", new_callable=AsyncMock)
    @patch("services.og_scraper.AsyncSessionLocal")
    async def test_process_og_url_entry_not_found(self, mock_session_local, mock_init_db):
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=None)
        mock_session_local.return_value.__aenter__.return_value = mock_session

        await process_og_url_by_entry_id(999)
        mock_session.get.assert_awaited_once()

if __name__ == "__main__":
    unittest.main()
