from loguru import logger
import sys
import os

# Remove default logger
logger.remove()

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Console logger
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="INFO"
)

# File logger
logger.add(
    "logs/scraper_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} - {message}",
    level="DEBUG",
    rotation="1 day",
    retention="7 days"
)

def get_logger(name: str):
    return logger.bind(name=name)
