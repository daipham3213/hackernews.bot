import typing as ty

from aiogram import BaseMiddleware, types


class HackerNewsMiddleware(BaseMiddleware):
    """Inject HackerNews client into the bot context."""

    def __init__(self, hn_client):
        super().__init__()
        self.hn_client = hn_client

    async def __call__(
        self,
        handler: ty.Callable[
            [types.Message, dict[str, ty.Any]], ty.Awaitable[ty.Any]],
        event: types.Message,
        data: dict[str, ty.Any]
    ):
        data["hn_client"] = self.hn_client
        return await handler(event, data)


