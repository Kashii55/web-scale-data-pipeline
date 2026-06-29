import random
import time
import asyncio
from utils.logger import get_logger

logger = get_logger("AntiBot")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
]

PROXIES = [
    # Add your proxies here in format: "http://user:pass@host:port"
    # Left empty for now - add real proxies when needed
]

class AntiBot:
    def __init__(self, min_delay: float = 0.5, max_delay: float = 2.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.request_count = 0

    def get_random_user_agent(self) -> str:
        ua = random.choice(USER_AGENTS)
        logger.debug(f"Using User-Agent: {ua[:50]}...")
        return ua

    def get_random_proxy(self) -> str | None:
        if not PROXIES:
            return None
        proxy = random.choice(PROXIES)
        logger.debug(f"Using proxy: {proxy}")
        return proxy

    def get_random_delay(self) -> float:
        return random.uniform(self.min_delay, self.max_delay)

    def wait(self):
        delay = self.get_random_delay()
        self.request_count += 1
        if self.request_count % 50 == 0:
            # Extra pause every 50 requests
            delay += random.uniform(2.0, 5.0)
            logger.info(f"Extended pause after {self.request_count} requests: {delay:.2f}s")
        time.sleep(delay)

    async def async_wait(self):
        delay = self.get_random_delay()
        self.request_count += 1
        if self.request_count % 50 == 0:
            delay += random.uniform(2.0, 5.0)
            logger.info(f"Extended pause after {self.request_count} requests: {delay:.2f}s")
        await asyncio.sleep(delay)

    def get_headers(self) -> dict:
        return {
            "User-Agent": self.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
