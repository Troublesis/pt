# https://pypi.org/project/loguru/
import sys

from loguru import logger

from config.config import settings


def my_filter(record):
    # Exclude log messages with level 'DEBUG'
    if record["level"].name == "ERROR":
        pass
    return record["level"].name != "DEBUG"


logger.remove()  # Remove the default logger


is_debug = settings.get("DEBUG", False)
if is_debug:
    filter = None
    log_level = "DEBUG"
else:
    filter = my_filter
    log_level = "INFO"

normal_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{level: <8}</level> [{file}:{line}] {message}"
error_format = "<red>{time:YYYY-MM-DD HH:mm:ss}</red> <level>{level: <8}</level> [{file}:{line}] {message}"

logger.add(
    sys.stderr,
    format=normal_format,
    level=log_level,
    filter=filter,
)
logger.add(
    "logs/access.log", rotation="100 MB", retention="7 days", format=normal_format
)
logger.add("logs/error.log", level="ERROR", rotation="100 MB", format=error_format)

if __name__ == "__main__":
    logger.info("Hello World!")
    logger.debug("This is a debug message")
    logger.warning(f"Warning: Something wrong")
    logger.error("Something went wrong.")
    logger.critical("Critical error!")
