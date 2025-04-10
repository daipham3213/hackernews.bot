import configparser
import os

cwd = os.getcwd()

_common_paths = [
    os.path.join(cwd, "config.ini"),
    os.path.join(cwd, "etc", "hackernews_bot", "config.ini"),
    os.path.join("etc", "hackernews_bot", "config.ini"),
]

parser = configparser.ConfigParser(default_section="DEFAULT")

DEFAULT = """
[DEFAULT]
on_news = False

[logging]
level = INFO
"""


def load(path: str):
    """Load the configuration file.

    Args:
        path (str): The path to the configuration file.

    Returns:
        configparser.ConfigParser: The configuration parser object.
    """
    parser.read_string(DEFAULT)
    if path and os.path.exists(path):
        parser.read(path)
    else:
        for p in _common_paths:
            if os.path.exists(p):
                parser.read(p)
                path = p
                break

    return parser, path
