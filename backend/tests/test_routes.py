import unittest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app  # replace with the correct path to your FastAPI app
from types import SimpleNamespace
from database.enums import URLStatus
import unittest
from unittest.mock import patch, AsyncMock
from types import SimpleNamespace
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.routes import router  # adjust import to your actual router location


app = FastAPI()
app.include_router(router, prefix="/api")

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("api.routes.REDIS_CLIENT.get", new_callable=AsyncMock)
    @patch("database.crud.get_url_entry_by_url", new_callable=AsyncMock)
    def test_submit_url_cache_hit(self, mock_get_by_url, mock_redis_get):
        mock_redis_get.return_value = "https://cached.com/img.png"
        mock_get_by_url.return_value = SimpleNamespace(
            id=1, url="https://cached.com", image_url="https://cached.com/img.png", status=URLStatus.SUCCESS
        )
        response = self.client.post("/api/submit", json={"url": "https://cached.com"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["url"], "https://cached.com/")
        self.assertEqual(data["image_url"], "https://cached.com/img.png")

    @patch("api.routes.REDIS_CLIENT.get", new_callable=AsyncMock)
    @patch("database.crud.get_url_entry_by_url", new_callable=AsyncMock)
    @patch("services.og_scraper.cache_save", new_callable=AsyncMock)
    def test_submit_url_existing_entry_with_image(self, mock_cache_save, mock_get_by_url, mock_redis_get):
        mock_redis_get.return_value = None
        mock_get_by_url.return_value = SimpleNamespace(
            id=2, url="https://existing.com", image_url="https://existing.com/img.png", status=URLStatus.SUCCESS
        )
        response = self.client.post("/api/submit", json={"url": "https://existing.com"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["url"], "https://existing.com/")
        self.assertEqual(data["image_url"], "https://existing.com/img.png")

    @patch("database.crud.update_url_entry", new_callable=AsyncMock)
    @patch("services.og_scraper.REDIS_CLIENT.set", new_callable=AsyncMock)
    @patch("api.routes.REDIS_CLIENT.get", new_callable=AsyncMock)
    @patch("database.crud.get_url_entry_by_url", new_callable=AsyncMock)
    @patch("database.crud.create_url_entry", new_callable=AsyncMock)
    @patch("database.crud.get_url_entry_by_id", new_callable=AsyncMock)
    @patch("services.og_scraper.process_og_url_by_entry_id", new_callable=AsyncMock)
    def test_submit_url_new_entry(
        self, mock_process, mock_get_by_id, mock_create, mock_get_by_url, mock_redis_get, mock_redis_set, mock_update_url_entry
    ):
        mock_redis_get.return_value = None
        mock_get_by_url.return_value = None
        mock_create.return_value = SimpleNamespace(
            id=3, url="https://new.com", image_url=None, status=URLStatus.PENDING
        )
        mock_get_by_id.return_value = SimpleNamespace(
            id=3, url="https://new.com", image_url="https://new.com/img.png", status=URLStatus.SUCCESS
        )
        response = self.client.post("/api/submit", json={"url": "https://new.com"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["url"], "https://new.com/")
        self.assertIn("image_url", data)

    @patch("database.crud.get_all_entries", new_callable=AsyncMock)
    def test_get_history(self, mock_get_all):
        mock_get_all.return_value = (
            [
                SimpleNamespace(id=1, url="https://one.com", image_url="https://one.com/img.png", status=URLStatus.SUCCESS),
                SimpleNamespace(id=2, url="https://two.com", image_url=None, status=URLStatus.PENDING),
            ],
            None,
        )
        response = self.client.get("/api/history?limit=2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        self.assertIsNone(data["next_cursor"])
        self.assertEqual(data["results"][0]["url"], "https://one.com/")
        self.assertEqual(data["results"][1]["url"], "https://two.com/")


if __name__ == "__main__":
    unittest.main()
