class BotExceptions(Exception):
    """Base class for all exceptions raised by the bot."""
    pass


class ConfigError(BotExceptions):
    """Exception raised for errors in the configuration."""
    pass


class NetworkError(BotExceptions):
    """Exception raised for network-related errors."""
    pass


class DataError(BotExceptions):
    """Exception raised for errors in the data."""
    pass


class CallbackError(BotExceptions):
    """Exception raised for errors in the callback."""
    pass


class ItemNotFoundError(BotExceptions):
    """Exception raised when an item is not found."""
    pass
