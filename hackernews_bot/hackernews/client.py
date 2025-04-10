import asyncio
import json
import logging
import typing as ty

from aiohttp import ClientResponseError, ClientSession
from aiosseclient import aiosseclient

from hackernews_bot import exceptions

LOG = logging.getLogger(__name__)


class OnNewCallback(ty.Protocol):
    async def __call__(self, item_id: int) -> None:
        """Callback to be called with the news item ID."""
        pass


class HackerNews:
    _headers = {
        "User-Agent": "HackerNewsBot/1.0",
    }
    _supported_versions = {
        "v0": "https://hacker-news.firebaseio.com/",
    }

    def __init__(self, ver="v0"):
        self.ver = ver
        self.base_url = self._supported_versions.get(ver)
        if not self.base_url:
            raise ValueError(f"Unsupported version: {ver}")

    async def on_news(
        self,
        callback: OnNewCallback | ty.Callable[[int], ty.Awaitable[None]]
    ):
        """Subscribe to news updates.

        :param callback: A callable that will be called with the news item.
        """
        LOG.info("Subscribing to Hacker News updates...")

        path = f"{self.base_url}/{self.ver}/maxitem.json"
        async for event in aiosseclient(path, headers=self._headers):
            data = json.loads(event.data) or {}
            if item_id := data.get("data"):
                await callback(item_id=int(item_id))
            else:
                LOG.warning("Received empty data from Hacker News.")

    async def get_item(self,
                       item_id: int,
                       retries: int = 5,
                       interval: int = 3) -> dict:
        """Get a news item by its ID.

        :param item_id: The ID of the news item.
        :param retries: Number of retries if the request fails.
        :param interval: Interval between retries in seconds.

        :return: The news item data.
        """
        path = f"{self.base_url}/{self.ver}/item/{item_id}.json"
        async with ClientSession() as session:
            for _attempt in range(retries):
                try:
                    async with session.get(path) as response:
                        response.raise_for_status()
                        data = await response.json()
                        LOG.debug(
                            "Received item from Hacker News: %s", data
                        )
                        if not data:
                            LOG.warning(
                                "Received empty response from Hacker News."
                            )
                            raise ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status,
                                message="Empty response from Hacker News.",
                            )
                        return data
                except ClientResponseError as e:
                    msg = (
                        f"Error fetching item {item_id}: {e.message}, "
                        f"retrying in {interval} seconds."
                    )
                    LOG.debug(msg)
                    await asyncio.sleep(interval)
            msg = f"Failed to fetch item {item_id} after {retries} attempts."
            raise exceptions.ItemNotFoundError(msg)

    async def get_top_stories(self) -> list[int]:
        """Get the top stories from Hacker News."""
        path = f"{self.base_url}/{self.ver}/topstories.json"
        async with ClientSession() as session:
            async with session.get(path) as response:
                response.raise_for_status()
                story_ids = await response.json()
                LOG.debug(
                    "Received top stories from Hacker News: %s",
                    story_ids
                )
                if not story_ids:
                    LOG.warning("Received empty response from Hacker News.")
                return story_ids
