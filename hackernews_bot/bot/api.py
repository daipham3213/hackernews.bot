import asyncio
import logging
from configparser import ConfigParser
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.utils import chat_action

from hackernews_bot.bot import middlewares
from hackernews_bot.consts import INVALIDCMD_MSG, START_MSG, STORY_TEMPLATE
from hackernews_bot.hackernews import client

LOG = logging.getLogger(__name__)
dispatch = Dispatcher()


@dispatch.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(START_MSG, disable_web_page_preview=True)


@dispatch.message(Command(
    types.BotCommand(command="top_stories", description="Get top stories")))
async def top_stories(message: types.Message, hn_client: client.HackerNews):
    await message.answer("Fetching top stories...",
                         disable_web_page_preview=True)

    stories = await hn_client.get_top_stories()
    if not stories:
        await message.answer("No top stories available at the moment.")
        return

    async def send_story(story_id: int):
        story = await hn_client.get_item(story_id)
        created_at = datetime.fromtimestamp(story["time"])
        render = STORY_TEMPLATE.format(
            url=story.get("url", "No URL available"),
            title=story.get("title", "No title available"),
            by=story.get("by", "Unknown"),
            score=story.get("score", 0),
            descendants=story.get("descendants", 0),
            time=created_at.strftime("%m/%d/%Y %I:%M %p"),
            text=story.get("text", "---"),
        )
        await message.answer(render)

    # Send the top stories in asynchronous tasks
    tasks = map(lambda story_id: send_story(story_id), stories)
    await asyncio.gather(*tasks)


@dispatch.message(Command(
    types.BotCommand(command="item", description="Get item by ID")))
async def item(message: types.Message, hn_client: client.HackerNews):
    try:
        item_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("Please provide a valid item ID.")
        return

    await message.answer(f"Fetching item with ID {item_id}...",
                         disable_web_page_preview=True)

    try:
        item = await hn_client.get_item(item_id)
    except Exception as e:
        LOG.error("Error fetching item %s: %s", item_id, e)
        await message.answer(f"Item with ID {item_id} not found.")
        return
    if item.get("type") != "story":
        await message.answer("The provided ID is not a story.")
        return

    created_at = datetime.fromtimestamp(item["time"])
    render = STORY_TEMPLATE.format(
        url=item.get("url", "No URL available"),
        title=item.get("title", "No title available"),
        by=item.get("by", "Unknown"),
        score=item.get("score", 0),
        descendants=item.get("descendants", 0),
        text=item.get("text", "---"),
        time=created_at,
    )
    await message.answer(render)


@dispatch.message()
async def echo(message: types.Message):
    await message.answer(INVALIDCMD_MSG, disable_web_page_preview=True)


async def start(config: ConfigParser, hn_client: client.HackerNews):
    """Starting the bot.
    This function initializes the bot with the given configuration and
    starts polling for messages.

    :param config: The configuration parser instance.
    :param hn_client: The HackerNews client instance.
    """
    LOG.info("Starting bot with token: %s", config.get("DEFAULT", "bot_token"))
    bot = Bot(token=config.get("DEFAULT", "bot_token"),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Register middlewares
    LOG.debug("Registering middlewares")
    dispatch.message.middleware(chat_action.ChatActionMiddleware())
    dispatch.message.middleware(middlewares.HackerNewsMiddleware(hn_client))

    LOG.debug("Registering handlers")
    await dispatch.start_polling(bot)
