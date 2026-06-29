from playwright.sync_api import sync_playwright
from scrapers.base_scraper import BaseScraper
from utils.logger import get_logger
import time
import re
import json
import csv
import os

logger = get_logger("PlaywrightScraper")

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}

class PlaywrightScraper(BaseScraper):
    def __init__(self, config_path="config/config.yaml"):
        super().__init__(config_path)
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.scraper_config["headless"]
        )
        self.page = self.browser.new_page()
        self.page.set_extra_http_headers({
            "User-Agent": self.scraper_config["user_agent"]
        })
        logger.info("Playwright browser started")

    def fetch(self, url: str):
        self.page.goto(url, timeout=self.timeout * 1000)
        self.page.wait_for_load_state("networkidle")
        return self.page

    def clean_price(self, price: str) -> str:
        price = re.sub(r'[^\d.]', '', price.strip())
        return f"£{price}"

    def format_rating(self, rating: int) -> str:
        return "⭐" * rating if rating > 0 else "No rating"

    def get_book_urls(self, page_url: str) -> list:
        self.fetch(page_url)
        anchors = self.page.query_selector_all("div.image_container a")
        urls = []
        for a in anchors:
            href = a.get_attribute("href") or ""
            href = href.replace("../", "")
            full_url = f"https://books.toscrape.com/catalogue/{href.split('catalogue/')[-1]}"
            urls.append(full_url)
        return urls

    def get_all_book_urls(self) -> list:
        all_urls = []
        page = 1
        while True:
            page_url = self.base_url if page == 1 else f"https://books.toscrape.com/catalogue/page-{page}.html"
            logger.info(f"Scraping page {page}: {page_url}")
            try:
                urls = self.get_book_urls(page_url)
                if not urls:
                    break
                all_urls.extend(urls)
                logger.info(f"Found {len(urls)} books on page {page}")
                page += 1
                time.sleep(1)
            except Exception as e:
                logger.error(f"Stopped at page {page}: {e}")
                break
        logger.info(f"Total book URLs collected: {len(all_urls)}")
        return all_urls

    def scrape_book(self, url: str) -> dict:
        self.fetch(url)
        p = self.page

        # Title
        title = p.query_selector("div.product_main h1")
        title = title.inner_text().strip() if title else "N/A"

        # Price
        price = p.query_selector("p.price_color")
        price = self.clean_price(price.inner_text()) if price else "N/A"

        # Availability
        availability = p.query_selector("p.instock.availability")
        availability = " ".join(availability.inner_text().split()) if availability else "N/A"

        # Image URL
        image = p.query_selector("#product_gallery .active img")
        image_url = "N/A"
        if image:
            src = image.get_attribute("src") or ""
            src = src.replace("../../", "")
            image_url = f"https://books.toscrape.com/{src}"

        # Description
        description = p.query_selector("div#product_description + p")
        description = description.inner_text().strip() if description else "N/A"

        # Rating
        rating_tag = p.query_selector("p.star-rating")
        rating_num = 0
        if rating_tag:
            classes = rating_tag.get_attribute("class") or ""
            for word in classes.split():
                if word in RATING_MAP:
                    rating_num = RATING_MAP[word]

        # Product info table
        product_info = {}
        rows = p.query_selector_all("table.table-striped tr")
        for row in rows:
            th = row.query_selector("th")
            td = row.query_selector("td")
            if th and td:
                key = th.inner_text().strip()
                val = td.inner_text().strip()
                if "Price" in key or "Tax" in key:
                    val = self.clean_price(val)
                product_info[key] = val

        # Screenshot on each book
        os.makedirs("logs/screenshots", exist_ok=True)
        safe_title = re.sub(r'[^\w]', '_', title)[:50]
        p.screenshot(path=f"logs/screenshots/{safe_title}.png")

        return {
            "title": title,
            "price": price,
            "availability": availability,
            "rating": self.format_rating(rating_num),
            "description": description,
            "upc": product_info.get("UPC", "N/A"),
            "product_type": product_info.get("Product Type", "N/A"),
            "price_excl_tax": product_info.get("Price (excl. tax)", "N/A"),
            "price_incl_tax": product_info.get("Price (incl. tax)", "N/A"),
            "tax": product_info.get("Tax", "N/A"),
            "num_reviews": product_info.get("Number of reviews", "0"),
            "image_url": image_url,
            "url": url
        }

    def save_json(self, data: list, filename: str):
        os.makedirs("output", exist_ok=True)
        filepath = f"output/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"JSON saved to {filepath}")

    def save_csv(self, data: list, filename: str):
        os.makedirs("output", exist_ok=True)
        filepath = f"output/{filename}"
        if not data:
            return
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"CSV saved to {filepath}")

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        super().close()
