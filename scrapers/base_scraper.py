import time
import yaml
from utils.logger import get_logger

logger = get_logger("BaseScraper")

class BaseScraper:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.scraper_config = self.config["scraper"]
        self.timeout = self.scraper_config["timeout"]
        self.retries = self.scraper_config["retries"]
        self.base_url = self.scraper_config["base_url"]
        logger.info(f"BaseScraper initialized with base_url: {self.base_url}")

    def fetch(self, url: str):
        raise NotImplementedError("Subclasses must implement fetch()")

    def retry(self, func, *args, **kwargs):
        for attempt in range(1, self.retries + 1):
            try:
                logger.info(f"Attempt {attempt} of {self.retries}")
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Attempt {attempt} failed: {e}")
                if attempt < self.retries:
                    time.sleep(2 ** attempt)
                else:
                    logger.error("All retries exhausted")
                    raise

    def save(self, data, filename: str):
        import json
        import os
        os.makedirs("output", exist_ok=True)
        filepath = f"output/{filename}"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Data saved to {filepath}")

    def close(self):
        logger.info("Scraper closed")
