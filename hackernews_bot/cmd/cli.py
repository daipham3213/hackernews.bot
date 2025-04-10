import argparse
import asyncio
import logging
from configparser import ConfigParser

from hackernews_bot import config, exceptions
from hackernews_bot.bot import api
from hackernews_bot.hackernews import client

LOG = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Hacker News Bot CLI")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the configuration file",
        default=None,
    )
    return parser.parse_args()


async def on_new_item(hackernews: client.HackerNews, item_id: int):
    """Callback function to handle new items.

    :param hackernews: The HackerNews client instance.
    :param item_id: The ID of the new item.
    """
    LOG.debug("An item received from Hacker News: item-id %s", item_id)
    try:
        item = await hackernews.get_item(item_id)
        LOG.debug("An item received from Hacker News: %s", item)
    except exceptions.ItemNotFoundError:
        LOG.error("An error occurred while fetching the item: %s", item_id)


async def entry(cfg: ConfigParser):
    """Run the main function.

    :param cfg: The configuration parser instance.
    """

    hn_client = client.HackerNews(ver="v0")
    LOG.info("Hacker News client initialized with version: %s", hn_client.ver)

    jobs = {
        "bot": api.start(config=cfg, hn_client=hn_client),
    }
    if cfg.getboolean("DEFAULT", "on_news", fallback=False):
        jobs["on_news"] = hn_client.on_news(
            lambda item_id: on_new_item(hn_client, item_id)
        )
    try:
        await asyncio.gather(*jobs.values())
    except asyncio.CancelledError:
        LOG.info("Hacker News Bot stopped.")
        raise


def main():
    args = parse_args()
    cfg, path = config.load(args.config)

    logging.basicConfig(level=cfg.get("logging", "level", fallback="INFO"))
    LOG.info("Starting Hacker News Bot with config located at: %s", path)

    token = cfg.get("DEFAULT", "bot_token", fallback=None)
    if not token:
        raise exceptions.ConfigError(
            "`bot_token` options is required in the configuration file."
        )
    asyncio.run(entry(cfg))
